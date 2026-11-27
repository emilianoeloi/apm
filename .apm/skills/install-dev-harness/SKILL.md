---
name: install-dev-harness
description: >
  Prepara o workflow de SDLC de um projeto (Spec-Driven Development) com
  OpenSpec + OpenSPDD, protegido por um gate de fase (proposal vs. apply)
  mecânico via hooks. Funciona para Claude Code, GitHub Copilot e Google
  Antigravity, entregue via APM. Stack-agnóstico. Use quando o usuário quiser
  "trazer o harness para este projeto", instalar o fluxo propose → analysis →
  canvas → generate → archive, proteger o planejamento contra escrita prematura
  de código, ou bloquear comandos destrutivos de git/shell.
allowed-tools: Read, Write, Edit, Bash, Glob
license: MIT
metadata:
  author: exported-from-uimaker-adk
  version: "2.2"
---

# Skill — Install Dev Harness (APM + OpenSpec + OpenSPDD)

O que este skill instala é, antes de tudo, o **workflow de uma
implementação**:

```
 fase "proposal" (escrita em código bloqueada)          fase "apply"
┌───────────────────────────────────────────────┐   ┌──────────────────────────────┐
│ OpenSpec      OpenSPDD            OpenSPDD    │   │ OpenSPDD       OpenSpec      │
│ /opsx-propose → /spdd-analysis → /spdd-       │ → │ /spdd-generate → /opsx-apply │ → /opsx-archive
│ (proposal,      (contexto,        reasons-    │   │ (código a      (marca tasks, │   (fase limpa)
│  design, tasks)  riscos)          canvas)     │   │  partir do     validate)     │
│                                   (contrato)  │   │  canvas)                     │
└───────────────────────────────────────────────┘   └──────────────────────────────┘
                 ▲ phase_cli.py set proposal <change>        ▲ phase_cli.py set apply <change>
```

Quatro peças, cada uma com um dono:

| Peça | Dono | O que fornece |
|---|---|---|
| **APM** (`apm.yml`) | distribuição | entrega skills, agents, prompts e hooks para `claude`, `copilot` e `antigravity` com um único `apm install` |
| **OpenSpec** | especificação | skills `openspec-*` e prompts `/opsx-*` **vendorizados neste repo**; o CLI `openspec` cria `openspec/` e roda `validate`/`archive` |
| **OpenSPDD** | prompt estruturado | skills originais `spdd-analysis`, `spdd-reasons-canvas`, `spdd-generate`, `spdd-sync`, `spdd-prompt-update` **vendorizadas neste repo**, sem alterações; não exige o CLI `openspdd` no projeto consumidor |
| **Harness gate** (hooks + `phase_cli.py`) | enforcement | bloqueia código em `proposal`, bloqueia `git push`/`rm -rf`/credenciais sempre |

Via APM os comandos têm o mesmo nome nos dois hosts: `/opsx-*` e `/spdd-*`
(o `/opsx:*` com dois-pontos é do `openspec init` nativo do Claude).

Os hooks são scripts Python stdlib-only (só `python3` é requisito) e rodam
como processo externo — funcionam para qualquer stack do projeto alvo. **O APM
entrega os hooks**: o pacote os declara em `.apm/hooks/harness.json` e o
`apm install` copia os scripts e os registra em `.claude/settings.json` e
`.github/hooks/`. Nada de copiar scripts nem editar o `settings.json` à mão.

> **Não rode `openspec init --tools claude,...` nem `openspdd generate` no
> projeto consumidor** — o APM já entrega esses arquivos e uma segunda cópia
> duplica comandos. Os arquivos em `templates/` são só o que o projeto precisa
> ter por conta própria: `harness.config.json`, `CLAUDE.md` e o `phase_cli.py`.

## Mantendo o vendor (mantenedores deste repo)

As skills/prompts de OpenSpec e OpenSPDD são cópias controladas, geradas
por `python3 scripts/sync-vendor.py` (exige os CLIs `openspec` e `openspdd`
instalados). O script roda os geradores num repo temporário, copia o
resultado para `.apm/skills/openspec-*`, `.apm/prompts/opsx-*.prompt.md` e
`.apm/skills/spdd-*` (OpenSPDD no formato original de skills, sem edição) e
registra as versões em `vendor.json`. Faça isso ao atualizar os CLIs, revise
o diff e só então publique. Customizações locais devem ir para as skills
autorais (`openspec-workflow`), nunca para os arquivos
vendorizados — o próximo sync os sobrescreve.

## Quando usar isto vs. quando não

Use quando o projeto quer **gate de fase real** + fluxo SDD. Se o objetivo é
só documentar convenções, um `AGENTS.md`/`CLAUDE.md` basta — não instale
hooks que o time não vai entender por que estão bloqueando.

Já tem OpenSpec/OpenSPDD instalados de forma legada (pré-APM), com
`.claude/commands/opsx/`, `.claude/commands/spdd-*.md` ou
`.github/copilot-prompts/`? Avise o usuário que o `apm install` vai entregar
`/opsx-*` e `/spdd-*` e que os arquivos legados ficam duplicados — proponha
removê-los, mas só depois de confirmar.

## Pré-requisitos

```bash
apm --version        # Agent Package Manager
openspec --version   # >= 1.x (init, validate, archive)
python3 --version
```

`openspdd` não é necessário no projeto consumidor. Se algum pré-requisito
faltar, informe ao usuário e pare — não instale ferramentas globais sem pedir.

## Passos

1. **Detecte o ambiente** do projeto alvo:
   - Stack (`pyproject.toml`, `package.json`, `Package.swift`/`*.xcodeproj`,
     `build.gradle(.kts)`) → sugere `code_prefixes` (`src/`, `tests/`, …).
   - Hosts em uso: `.claude/` → Claude Code; `.github/` → Copilot; `.agents/` → Antigravity / Codex. Se múltiplos ou nenhum, instale para os hosts aplicáveis.
   - Já existe `apm.yml`, `openspec/`, `AGENTS.md`/`CLAUDE.md`,
     `.claude/settings.json`? Faça merge, nunca sobrescreva.

2. **Pergunte o que falta** (AskUserQuestion, só se mudar o resultado):
   - Hosts alvo (`claude`, `copilot`, `antigravity`, ou combinação).
   - Arquivo raiz do agente (`AGENTS.md` lido por Copilot/Codex, `CLAUDE.md`
     para Claude; veja `dev-harness-architect/reference/harness-model.md#hierarquia-de-instrucoes`).
     Nunca crie `.github/copilot-instructions.md` junto de `AGENTS.md`.
   - Diretórios reais de código e testes (`code_prefixes`).
   - Idioma dos artefatos OpenSpec (`--language`), se não for o padrão.
   - Comando de sensores do projeto (`sensors_command`: testes, lint, build —
     o que deve passar antes de encerrar a sessão). Se o usuário não souber,
     deixe vazio e escreva "não informado" nos quality gates: vazio nunca
     bloqueia o encerramento.
   - Quer só os hooks de segurança sem gate de fase? Então deixe
     `planning_write_prefixes`/`code_prefixes` como `[]` e pule os passos 4–5.

3. **Instale o harness via APM** — entrega as skills `openspec-*`, os prompts
   `/opsx-*` e `/spdd-*`, agents e hooks para os hosts escolhidos:
   ```bash
   apm install emilianoeloi/apm#<tag>                  # ou adicione em apm.yml → dependencies.apm
   apm install --target claude,copilot,antigravity     # reaplica para os hosts escolhidos
   ```
   Resultado: `.claude/commands/opsx-*.md`, `.claude/skills/{openspec,spdd}-*`,
   `.github/prompts/opsx-*.prompt.md` e os hooks (`SessionStart`, `PreToolUse`
   para escrita e Bash, `Stop`) registrados em `.claude/settings.json` e
   `.github/hooks/`, com os scripts em `.claude/hooks/<pacote>/` e
   `.github/hooks/scripts/<pacote>/`.
   Hooks são código executável: se o APM pedir, use `apm approve` depois de
   revisar os scripts. Use `apm install --dry-run` antes quando o projeto já
   tiver arquivos locais, e confira que cada evento aparece uma vez no
   `.claude/settings.json` (se o projeto já registrava hooks parecidos à mão,
   remova o registro antigo para não duplicar).
   Se um pacote privado falhar com HTTP 401 mesmo com `gh auth status` válido,
   confira se há um `GITHUB_TOKEN` expirado no ambiente — rodar com
   `unset GITHUB_TOKEN` faz o APM usar a credencial ativa do `gh`.
   Ao montar o `.gitignore` de artefatos implantados pelo APM, inclua também
   `.claude/apm-hooks.json` e `.github/hooks/apm-harness.json` além das pastas
   implantadas (mantendo `.claude/settings.json` versionado no git).

4. **Crie o estado do OpenSpec** (só `openspec/`; os comandos já vieram do APM):
   ```bash
   openspec init --tools none --no-animation --no-copilot-cloud
   ```
   Gera `openspec/{config.yaml,specs/,changes/archive/}`. Depois, registre em
   `openspec/config.yaml` (`context:`/`rules:`) apenas o que o agente não
   infere do código — por exemplo, “propostas devem listar quality gates”.

5. **Crie as pastas de artefatos do SPDD**: `spdd/analysis/` e `spdd/prompt/`
   (com `.gitkeep`). Elas precisam estar em `planning_write_prefixes` para a
   fase `proposal` permitir escrita nelas.

6. **Instale o gate de fase** copiando `templates/` para o projeto (os hooks
   já vieram do APM no passo 3; o que sobra é a configuração e o CLI de fase):

   | Template | Destino | Placeholders |
   |---|---|---|
   | `templates/harness.config.json.template` | `harness.config.json` | `{{RULEBOOK_FILE}}`; `{{PLANNING_PREFIXES}}` = `["openspec/", "spdd/", ".harness/"]`; `{{CODE_PREFIXES}}` = ex. `["src/", "tests/"]`; depois preencha `sensors_command` |
   | `templates/CLAUDE.md.template` | `CLAUDE.md` (só se não existir) | `{{RULEBOOK_FILE}}`, `{{QUALITY_GATES}}`, `{{CODE_PREFIXES_HUMAN}}` |
   | `templates/phase_cli.py` | `scripts/harness/phase_cli.py` | — |

   Se `CLAUDE.md`/`AGENTS.md` já existir, apenas acrescente a seção
   “Fase da change” (com o mapeamento do passo 8). Quando usar Codex, Copilot
   ou Google Antigravity e `AGENTS.md` ainda não existir na raiz, crie um
   `AGENTS.md` enxuto apontando explicitamente para `CLAUDE.md` e
   `harness.config.json` (ponte canônica, sem duplicar texto longo). Não crie
   `scripts/hooks/` nem edite `.claude/settings.json` para registrar hooks: é
   o APM que faz isso.

   Opcional: o pre-commit genérico do pacote roda o mesmo `sensors_command`
   antes de cada commit (e nunca trava sem ele). Copie
   `.apm/scripts/git-hooks/pre-commit` do pacote para `.githooks/pre-commit` e
   rode `git config core.hooksPath .githooks`.

7. **Verifique**:
   ```bash
   echo '{"source":"new"}' | python3 .claude/hooks/*/.apm/hooks/scripts/session-start.py
   echo '{"hook_event_name":"Stop"}' | python3 .claude/hooks/*/.apm/hooks/scripts/stop-sensors.py; echo "exit=$?"
   openspec list
   python3 scripts/harness/phase_cli.py show
   ls .claude/skills/spdd-*/SKILL.md .github/prompts/opsx-*.prompt.md
   ```
   O primeiro comando deve imprimir JSON com `additionalContext` (fase não
   declarada + checklist de guias). O segundo deve sair com 0 (sem
   `sensors_command` ou com sensores passando) e com 2 mostrando a saída do
   sensor se ele falhar. O `ls` confirma que o APM entregou os prompts nos
   dois hosts.

8. **Ensine o mapeamento fluxo ↔ fase** (inclua no `AGENTS.md`/`CLAUDE.md`):

   | Etapa do fluxo | Comando | Fase do harness |
   |---|---|---|
   | Propor | `/opsx-propose` | `phase_cli.py set proposal <change>` **antes** |
   | Validar spec | `openspec validate <change> --strict` | `proposal` |
   | Analisar | `/spdd-analysis openspec/changes/<change>` → `spdd/analysis/` | `proposal` |
   | Canvas | `/spdd-reasons-canvas spdd/analysis/<arquivo>` → `spdd/prompt/` | `proposal` |
   | Gerar | `/spdd-generate spdd/prompt/<canvas>` | `phase_cli.py set apply <change>` **antes** |
   | Aplicar/fechar tasks | `/opsx-apply` + `openspec validate <change> --strict` | `apply` |
   | Reconciliar | `/spdd-sync` (código → canvas) | `apply` |
   | Arquivar | `openspec archive <change>` | `phase_cli.py set done <change>` (qualquer fase ≠ `proposal` libera) |

   Em `proposal`, os hooks bloqueiam toda escrita fora de
   `planning_write_prefixes` (`openspec/`, `spdd/`, `.harness/`) — inclusive
   `code_prefixes` — e `git commit/add/merge/rebase`. Fora de `proposal` (ou
   sem fase) tudo é liberado — o gate só existe durante planejamento. Por
   isso rode os passos 3–6 **antes** de declarar a primeira fase.

   **Agentes (opcional).** O `apm install` também entrega `sdlc-planner`,
   `sdlc-coder`, `sdlc-reviewer` e `sdlc-auditor` para `claude` e `copilot`. Eles
   seguem o fluxo acima: a sessão principal declara a fase e dispara um por vez
   (planner em `proposal`; depois da aprovação do humano e de `set apply`, o
   coder; em seguida o reviewer; o auditor sob demanda). O modelo de
   `CLAUDE.md` já traz esse roteiro. Os agentes leem as pastas e o comando de
   sensores do `harness.config.json`: preencha `code_prefixes` e
   `sensors_command` antes de usá-los. No Google Antigravity, como os arquivos de
   `.claude/agents/` não são carregados automaticamente, defina `sdlc-*` na
   sessão com as mesmas regras de ferramentas e faça a sessão principal rodar
   `sensors_command` + `openspec validate --strict` se o subagente reviewer não
   tiver shell.

9. **Relate** os arquivos criados/modificados, os comandos de verificação
   executados e o próximo passo natural: `architecture-fitness-functions`
   (transformar as regras do arquivo raiz em testes, que viram os quality
   gates do `/spdd-generate`).

## Contrato entre hook e CLI — não quebre isto

Os hooks (scripts do pacote, entregues pelo APM) e o CLI (`scripts/harness/phase_cli.py`) leem o
mesmo arquivo (`harness.config.json` → `phase_state_path`, default
`.harness/change-phase.json`) sem compartilhar código — o hook roda num
interpretador isolado e não pode importar nada do projeto. A única garantia
de sincronia é a **igualdade literal** do caminho relativo entre os dois
scripts. Ambos já leem do config, então continuam sincronizados — mas se
algum dia hardcodear o caminho de novo em qualquer um dos dois, quebra o
contrato silenciosamente. Não faça isso.

## Segurança dos hooks — o que eles cobrem por padrão

Independente de fase, os hooks sempre bloqueiam (configurável em
`harness.config.json`):
- Escrita em nomes de arquivo de credencial conhecidos (`.env`,
  `service_account.json`, chaves privadas).
- Escrita que resolve para fora da raiz do repositório (path traversal).
- `git push`, `git reset --hard`, `git clean -f`, `git branch -D`, `rm -rf`
  (só quando são o comando em si; citados em texto, como numa mensagem de
  commit, não bloqueiam).
- Escrita direta em `.env` via redirecionamento de shell (`> .env`,
  `tee .env`).

Fora da raiz do projeto, a escrita só passa pelas pastas listadas em
`allowed_write_roots` do `harness.config.json` (vazio por padrão; use para
pastas temporárias, como `/tmp`).

No encerramento da sessão, o hook de Stop roda o `sensors_command` do projeto:
saída diferente de 0 ou estouro do tempo bloqueia o encerramento e mostra a
saída; vazio nunca bloqueia. Configuração ausente, corrompida ou de tipo errado
nunca derruba um hook — só desliga os checks que dependem dela; as defesas
acima continuam valendo.

Sensor de Gherkin: o pacote entrega `gherkin-sensor.py` (e a biblioteca
`_gherkin.py`) ao lado dos hooks. Um hook `PostToolUse` (matcher `Bash`) o roda
sozinho quando o comando contém `openspec validate`, saindo com 2 e citando
capability e requisito quando falta o bloco Gherkin. Ele não entra no
`sensors_command`, que segue vazio nos modelos. Para ter o sensor também no
Stop, componha-o ao `sensors_command` do projeto com o caminho onde o host
implantou os scripts (varia por host), por exemplo
`<comando de testes> && python3 <caminho-implantado>/gherkin-sensor.py`.
No Copilot, o `PostToolUse` não foi verificado.

Isso não substitui revisão humana para `git push` — o hook bloqueia a
execução automática; o agente ainda deve pedir confirmação explícita ao
usuário antes de rodar o comando manualmente fora do hook.

## Armadilhas observadas em projetos consumidores

Aprendido ao instalar este harness num projeto consumidor real (app estático sem backend, com Firebase Auth e leitura do Google Drive; apm v1.0.0):

- **Este skill não entrega workflow de CI.** Se o projeto pedir "CI pronto desde o início",
  crie o `.github/workflows/ci.yml` à mão (checagem de sintaxe + `npm test` ou equivalente);
  o `install-dev-harness` só entrega os hooks e o gate de fase.
- **O hook `pre-tool-bash-guard.py` lê o comando inteiro antes de executar.** Um comando
  composto como `phase_cli.py set apply <change> && git commit ...` é bloqueado inteiro na
  fase `proposal`, mesmo que só a segunda metade seja o commit. Declare a fase num comando
  e faça o `git commit` em outro, depois de confirmar `phase_cli.py show`.
- **O hook de escrita bloqueia qualquer caminho fora da raiz do repositório**, inclusive
  arquivos de configuração do usuário (`~/.claude/CLAUDE.md`, por exemplo). Para editar algo
  fora do repo, peça ao humano para colar o trecho, ou declare o caminho em
  `allowed_write_roots` só se for intencional e temporário.
- **O `sdlc-coder` escreve só em `code_prefixes`.** Arquivos de configuração, documentação,
  CI e manifestos de pacote (`package.json`, `harness.config.json`, `apm.yml`, `CHANGELOG.md`,
  `README.md`, `docs/`) ficam por conta da sessão principal, mesmo quando a mudança deles é
  parte da mesma funcionalidade.
- **`sed -i` no macOS (BSD) exige o argumento de extensão do backup** (`sed -i '' ...` ou
  `sed -i.bak ...`); sem ele, o comando falha ou deixa um arquivo de backup solto no repo.
  Prefira editar com a ferramenta de edição do agente, não com `sed -i` em scripts de uma linha.
- **Só comite depois de ver os sensores passarem.** Um commit saiu com um teste quebrado,
  por um `import` esquecido num arquivo de teste; o problema só apareceu ao rodar os testes
  de novo depois. Rode `sensors_command` (ou o comando de teste do projeto) uma última vez
  antes de cada commit, não só antes do primeiro.

- **PRs empilhadas: mesclar uma PR cuja base é outra branch a leva só para essa branch.**
  Com `main ← A ← B ← C`, mesclar B e C depois de A deixa B e C dentro das branches de baixo e
  fora da `main`. Aponte a base de cada PR para a `main` depois de mesclar a anterior (ou
  mescle de cima para baixo), e confira na `origin/main` que o conteúdo entrou. Prefira uma
  funcionalidade por branch, cada uma a partir da `main` atual, quando não houver dependência.
- **Brief ao `sdlc-coder`: copie do canvas a lista completa de funções e arquivos da
  Operation**, em vez de resumir de memória; uma função esquecida no brief só reaparece quando
  o coder avisa. Peça sempre o vermelho com a contagem de falhas antes do código.
- **O limite de uso pode interromper um subagente no meio do trabalho.** Os testes vermelhos
  já escritos ficam como ponto de retomada: retome o mesmo agente depois do reinício em vez de
  começar outro.
- **Mudança que altera a rotina de quem opera o sistema** (um login que passa a pedir menos
  escopo, uma sincronização que deixa de rodar sozinha) precisa estar no README e no changelog
  e ser dita antes de publicar.
- **Arquivos de container e documentação raiz na fase `apply`:** O `sdlc-coder` valida se cada arquivo tocado pertence a `code_prefixes`. Quando uma change inclui containerização (`Dockerfile`, `.dockerignore`) ou documentação operacional na raiz (`README.md`, `CHANGELOG.md`), inclua `Dockerfile` em `code_prefixes` quando o coder for implementá-lo e deixe os arquivos fora de `code_prefixes` (`.dockerignore`, `README.md`, `CHANGELOG.md`) explicitamente atribuídos à sessão principal, evitando falso positivo de desvio de escopo no `sdlc-reviewer`.
- **Ambientes virtuais (`.venv`) com symlinks externos em subagentes com sandbox:** Quando `.venv/bin/python` aponta para um interpretador fora do workspace (ex.: `~/.local/share/uv/python/...`), subagentes restritos ao sandbox do diretório do projeto podem receber `Operation not permitted`. Rode a suíte padrão com o `python3` do sistema dentro do subagente (usando `pytest.importorskip` para extras opcionais) e execute a suíte completa de `.venv/bin/python` na sessão principal.

Aprendido ao instalar o harness num segundo projeto consumidor (app web estático, repositório novo e vazio no GitHub, apm v2.1.0):

- **Os agentes `sdlc-*` só carregam ao reiniciar a sessão.** O `apm install` grava `.claude/agents/`, mas a sessão que rodou o install não os enxerga ("agent type not found"). Depois do install, reinicie a sessão do Claude Code antes de disparar o `sdlc-planner`; sem os agentes o fluxo para.
- **`GITHUB_TOKEN` inválido vale para `gh` e `git push`, não só para o apm.** `env -u GITHUB_TOKEN gh ...` e `env -u GITHUB_TOKEN git push ...` usam o login do keyring. Esse prefixo `env` fica fora da detecção do `pre-tool-bash-guard.py` (limite documentado no próprio guard); por isso a confirmação explícita do humano antes de qualquer push segue sendo a regra, mesmo quando o hook não barra.
- **Remoto novo e vazio: o primeiro PR precisa de uma base.** Sem `main` no remoto não há contra o que abrir PR. Com o ok do humano, publique a `main` (o preparo) antes e depois a branch da funcionalidade.
- **`sensors_command` como `npm test` (ou `node --test tests/`) falha enquanto `tests/` não existir**, e o hook de Stop bloqueia o encerramento. Deixe o comando vazio até existir o primeiro teste, ou crie o primeiro teste antes de preenchê-lo.
- **`code_prefixes` "não informado" deixa o `sdlc-coder` sem onde escrever.** Defina as pastas de código e de testes com o humano antes da primeira funcionalidade; o Preparo pode deixá-las vazias, a primeira Onda não.

## Armadilhas de Windows e do apm install

- **CRLF:** com `core.autocrlf=true`, a cópia de trabalho sai em CRLF e testes que cortam código por quebra de linha falham só nessa máquina. No preparo, crie `.gitattributes` com `* text=auto eol=lf`.
- **Hooks duplicados:** depois do `apm install`, o `.claude/settings.json` pode receber grupos de hook idênticos (mesmo matcher e mesmo comando). Avise e pare. Só com o ok do humano, remova as duplicatas e confira o diff.
- **Arquivos implantados e troca de branch:** trocar de branch pode apagar do disco arquivos implantados que a outra branch ainda versiona. Depois, rode `apm install` e confira os hooks.
- **Fase proposal:** o hook de fase bloqueia `git merge` (inclusive `merge-tree` e `merge-base`). Traga a main com a fase em `apply` ou `done`, ou numa worktree.
