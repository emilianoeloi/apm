---
name: install-dev-harness
description: >
  Prepara o workflow de SDLC de um projeto (Spec-Driven Development) com
  OpenSpec + OpenSPDD, protegido por um gate de fase (proposal vs. apply)
  mecânico via hooks. Funciona para Claude Code e GitHub Copilot, entregue
  via APM. Stack-agnóstico. Use quando o usuário quiser "trazer o harness
  para este projeto", instalar o fluxo propose → analysis → canvas →
  generate → archive, proteger o planejamento contra escrita prematura de
  código, ou bloquear comandos destrutivos de git/shell.
allowed-tools: Read, Write, Edit, Bash, Glob
license: MIT
metadata:
  author: exported-from-uimaker-adk
  version: "2.0"
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
| **APM** (`apm.yml`) | distribuição | entrega skills, agents, prompts e hooks para `claude` e `copilot` com um único `apm install` |
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
   - Hosts em uso: `.claude/` → Claude Code; `.github/` → Copilot. Se ambos
     ou nenhum, instale para os dois.
   - Já existe `apm.yml`, `openspec/`, `AGENTS.md`/`CLAUDE.md`,
     `.claude/settings.json`? Faça merge, nunca sobrescreva.

2. **Pergunte o que falta** (AskUserQuestion, só se mudar o resultado):
   - Hosts alvo (`claude`, `copilot`, ambos).
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
   apm install emilianoeloi/apm#<tag>     # ou adicione em apm.yml → dependencies.apm
   apm install --target claude,copilot    # reaplica para os hosts escolhidos
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
   “Fase da change” (com o mapeamento do passo 8). Não crie
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

Isso não substitui revisão humana para `git push` — o hook bloqueia a
execução automática; o agente ainda deve pedir confirmação explícita ao
usuário antes de rodar o comando manualmente fora do hook.
