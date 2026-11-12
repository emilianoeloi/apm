# apm

Pacote APM público e genérico, com Lean Inception, Harness e SDLC em skills, agentes e hooks, para qualquer stack (iOS, Rust, JavaScript, Go e outras). É instalado por versão e entregue para `claude` e `copilot`.

Consumo (no projeto), pelo pré-lançamento da `1.0.0`, que é a versão com os hooks genéricos e os agentes de SDLC:

```yaml
dependencies:
  apm:
    - emilianoeloi/apm#v1.0.0-alpha.1
```

Depois rode `apm install --target claude,copilot` e commite `apm.yml`, `apm.lock.yaml` e os diretórios implantados. A `v0.3.1` continua sendo a última versão **estável** (com o conteúdo do cowboy) até a `1.0.0` sair; veja "Pré-lançamento da 1.0.0" abaixo.

Layout: `.apm/skills/*`, `.apm/prompts/*`, `.apm/agents/*`, `.apm/hooks/*` (registro e scripts de hook), `.apm/scripts/*` (`phase_cli.py` e pre-commit genérico) e `.apm/templates/*` (`harness.config.json` e modelo do quadrante).

## Migração da 0.3.x

A limpeza do projeto de origem (`cowboy`, uma calculadora em COBOL) removeu, de forma **incompatível**:

- os agentes `cobol-vibecoder`, `cobol-planner`, `cobol-coder`, `cobol-reviewer` e `readme-writer`;
- os prompts `criar-programa`, `implementar-soma`, `implementar-subtracao`, `implementar-log`, `testar-programa`, `atualizar-readme` e `manutencao-repositorio`;
- as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`;
- o hook de encerramento `cowboy.json` (rodava `make fitness`) e o script de pre-commit que compilava COBOL.

O conteúdo não foi movido: quem ainda precisa dele deve manter a dependência na tag `v0.3.1`, que guarda o estado antigo. O hook de encerramento que o substitui é genérico (veja "Hooks" abaixo), e os agentes de SDLC são os `sdlc-*` descritos em "Agentes de SDLC". Os agentes da 0.3.x não têm equivalente direto.

## Workflow SDD (OpenSpec + OpenSPDD)

O pacote mantém **vendorizadas** as skills e prompts de OpenSpec e OpenSPDD, então `apm install` entrega o fluxo completo para `claude` e `copilot`:

| Origem | Em `.apm/` | Comandos |
|---|---|---|
| OpenSpec | `skills/openspec-*` (6) e `prompts/opsx-*.prompt.md` | `/opsx-propose`, `/opsx-explore`, `/opsx-apply`, `/opsx-update`, `/opsx-sync`, `/opsx-archive` |
| OpenSPDD (original, `openspdd generate -t codex`) | `skills/spdd-*` (5) | `/spdd-analysis`, `/spdd-reasons-canvas`, `/spdd-generate`, `/spdd-sync`, `/spdd-prompt-update` |

Depois de cada feature, o skill `skill-retrospective` fecha o ciclo: decide se skills existentes devem ser atualizados ou se um novo deve ser criado.

Skills autorais (`openspec-workflow`, `install-dev-harness`) integram o fluxo com o gate de fase do harness; o OpenSPDD é mantido sem alterações. O estado por projeto (`openspec/`) é criado com `openspec init --tools none`.

### Atualizando o vendor

```bash
python3 scripts/sync-vendor.py   # requer os CLIs openspec e openspdd
git diff                         # revise antes de publicar
```

As versões usadas ficam em [vendor.json](vendor.json). Não edite à mão os arquivos vendorizados — o próximo sync os sobrescreve; customizações vão nas skills autorais.

## Agentes de SDLC

Quatro agentes de papel único e fonte única (`.apm/agents/sdlc-*.agent.md`), que o `apm install` entrega para `claude` (`.claude/agents/`) e `copilot` (`.github/agents/`). **A sessão principal dispara cada um; eles não se chamam entre si** (cada um devolve o resultado a ela).

| Agente | Fase | O que faz | Escreve | Ferramentas |
|---|---|---|---|---|
| `sdlc-planner` | `proposal` | proposta OpenSpec validada, análise e REASONS Canvas (skills `openspec-explore`, `openspec-propose`, `spdd-analysis`, `spdd-reasons-canvas`) | só `planning_write_prefixes` (por padrão `openspec/` e `spdd/`); nunca código | `Read, Grep, Glob, Write, Edit, Bash, Skill` |
| `sdlc-coder` | `apply` | código pelas Operations do canvas (skills `spdd-generate` e `openspec-apply-change`), tasks marcadas e sensores antes de entregar; para e avisa se não houver canvas | só `code_prefixes` e os checkboxes do `tasks.md` | `Read, Grep, Glob, Write, Edit, Bash, Skill` |
| `sdlc-reviewer` | depois da implementação | confere código, Operations e tasks, roda `openspec validate --strict` e os sensores e entrega um relatório com veredito e achados (arquivo, linha e Operation) | nada: somente leitura | `Read, Grep, Glob, Bash` |
| `sdlc-auditor` | sob demanda (opcional) | responde dúvidas e audita conformidade, arquitetura e segurança com evidências de arquivo e linha | nada: somente leitura | `Read, Grep, Glob, Bash` |

**Ordem de disparo**, sempre pela sessão principal:

1. Pedido de funcionalidade: declare a fase (`python3 scripts/harness/phase_cli.py set proposal <change>`; o planner declara sozinho se não houver fase) e dispare o `sdlc-planner`.
2. O humano revisa e aprova a proposta, a análise e o canvas.
3. Declare `python3 scripts/harness/phase_cli.py set apply <change>` e dispare o `sdlc-coder`.
4. Dispare o `sdlc-reviewer` e leia o relatório; o humano decide o merge. Depois, a sessão principal reconcilia com `/spdd-sync`, arquiva (`openspec archive`) e faz a retrospectiva de skills.
5. Dispare o `sdlc-auditor` quando quiser tirar uma dúvida ou auditar.

**Formato.** Um arquivo serve aos dois hosts: o frontmatter tem só `name`, `description` e `tools`, com nomes de ferramenta do Claude Code (o Copilot os aceita como alias), sem `model` e sem `handoffs`. Nenhum agente cita linguagem, pasta ou comando de um projeto: as pastas e o comando de sensores vêm do `harness.config.json`, e as regras, do arquivo raiz do agente (`CLAUDE.md` ou `AGENTS.md`).

**Limites e verificação.**

- O somente leitura do reviewer e do auditor vem de ferramentas mínimas (sem `Write` e `Edit`) e do texto; o `Bash` que eles têm ainda poderia escrever arquivos, por isso o relatório confirma que o `git status --porcelain` final é igual ao inicial. A imposição mecânica está prevista para a Onda 2.
- O escopo do coder em `apply` não tem bloqueio mecânico; o reviewer o confere pelo diff e registra um achado de escopo.
- Comprovado: o contrato (testes em `tests/agents/`), a validação do Claude Code (`claude plugin validate .claude/agents`) e um teste de fumaça do reviewer e do auditor no Claude Code, sem nenhuma alteração no repositório. **Não comprovado:** o comportamento do `sdlc-planner` e do `sdlc-coder` (que escrevem) fora de um projeto real, que é o que o projeto de prova vai exercitar, e o carregamento dos quatro no Copilot.

## Hooks

O pacote entrega os hooks pelo APM: `apm install --target claude,copilot` copia os scripts (com o helper `_common.py`) e os registra em `.claude/settings.json` e `.github/hooks/`, sem cópia manual. Hooks são código executável: revise os scripts antes de instalar. Por padrão o APM não exige aprovação (o `apm install` da tag `v1.0.0-alpha.1` instalou os hooks direto); se o `apm.yml` do projeto declara um bloco `executables:`, aprove o pacote com `apm approve emilianoeloi/apm`.

| Evento | Script | O que faz |
|---|---|---|
| `SessionStart` | `session-start.py` | injeta fase, branch e guias no contexto da sessão |
| `PreToolUse` (escrita) | `pre-tool-write-guard.py` | bloqueia credenciais, escrita fora da raiz do projeto e código na fase `proposal` |
| `PreToolUse` (Bash) | `pre-tool-bash-guard.py` | bloqueia `git push`, `git reset --hard`, `git clean -f`, `git branch -D` e `rm -rf` (só quando são o comando, não quando aparecem em texto) e, em `proposal`, os que mutam o repositório |
| `Stop` | `stop-sensors.py` | roda o comando de sensores do projeto e só deixa encerrar se ele passar |

Tudo é configurado pelo `harness.config.json` do projeto (modelo em `.apm/templates/`):

- `sensors_command`: o comando que o `Stop` roda (raiz do projeto como diretório de trabalho). **Vazio por padrão: sem comando, nada bloqueia**, e o hook não depende de Makefile nem de stack. Saída diferente de 0 ou estouro de `sensors_timeout_seconds` (50 s) bloqueia o encerramento e mostra a saída. O comando vem do arquivo do próprio projeto e roda em shell: revise-o como qualquer outro hook.
- `allowed_write_roots`: diretórios absolutos fora do projeto onde a escrita é permitida (por exemplo `/tmp`); vazio por padrão.
- Fase, prefixos de planejamento e de código, nomes de arquivo e padrões de comando bloqueados.

Configuração ou payload ausente, corrompido ou de tipo errado nunca derruba nem trava um hook: só desliga os checks que dependem dela. As defesas embutidas (credenciais, `git push` e demais comandos destrutivos) continuam valendo sem configuração. O harness é uma rede de segurança contra deslizes do agente, não um sandbox: formas como `env X=1 git push` não são detectadas.

O pre-commit genérico (`.apm/scripts/git-hooks/pre-commit`) roda o mesmo `sensors_command` antes de cada commit; veja o skill `install-dev-harness` para instalar.

**Verificação.** O bloqueio foi comprovado no Claude Code (Bash e escrita, pelo código de saída 2). O formato do Copilot (`.github/hooks/`, decisão `deny` por JSON) é gerado pelo APM e coberto por testes de saída, mas **não foi verificado num Copilot real**.

## Releases (automáticos)

Os releases saem do GitHub Actions com o [release-please](https://github.com/googleapis/release-please-action):

1. Use **Conventional Commits** nos títulos dos PRs (`feat:`, `fix:`, `docs:`, `chore:`…). O workflow `pr-title` confere.
2. Ao mesclar na `main`, o bot abre ou atualiza um **PR de release** com a versão nova (`feat` → MINOR, `fix` → PATCH, `!` → MAJOR) e o `CHANGELOG.md`.
3. **Revisar e mesclar o PR de release** é o ato humano. Ao mesclar, o bot cria a tag `vX.Y.Z` e o GitHub Release.
4. No consumidor, atualize o `ref` no `apm.yml`, rode `apm install` e commite `apm.yml`, `apm.lock.yaml` e os diretórios implantados.

A linha `version:` do `apm.yml` é atualizada pelo bot (pelo `extra-files` do `release-please-config.json`, sem marcador no arquivo); não edite a versão à mão. Tags `v*` são protegidas contra apagar e mover.

### Pré-lançamento da 1.0.0

A `1.0.0-alpha.1` foi o pré-lançamento da `1.0.0`. A prova em um projeto real (a calculadora em Go) foi aprovada, e a configuração do release-please já propõe a `1.0.0` final.

- **Última versão estável:** a `v0.3.1`, até a `1.0.0` sair. O GitHub Release do pré-lançamento é marcado como "pre-release"; a tag `v1.0.0-alpha.1` já está publicada e quem quiser testá-lo aponta para ela de forma explícita (`emilianoeloi/apm#v1.0.0-alpha.1`). Quem não fixa a tag não deve esperar receber um pré-lançamento.
- **Estado:** a configuração está na versão final (`prerelease: false`): o próximo PR de release propõe a `1.0.0`. Ao mesclá-lo, o Elói publica a tag `v1.0.0` e um GitHub Release completo, sem a marca de pré-lançamento. Não haverá `1.0.0-alpha.2`.
- **Configuração:** `versioning: "prerelease"` e `prerelease-type: "alpha.1"` continuam em `release-please-config.json` até a tag `v1.0.0` existir: sem a estratégia de pré-lançamento, o bot proporia `2.0.0-alpha.1` ou `1.1.0-alpha.1` a partir de um alpha. Depois da tag, as duas chaves saem. Um teste (`tests/release/`) guarda isso.
- **Não use `release-as`:** ele fixa a versão e, se ninguém o remover depois do release, todo PR de release repete a mesma versão. Um teste (`tests/release/`) impede que ele entre na configuração.
- **Antes de mesclar o PR de release,** confira o título, a versão no `apm.yml` e no `.release-please-manifest.json` e o CHANGELOG: uma tag publicada não se apaga nem se move. Mesclar continua sendo ato humano; nenhuma etapa automática faz isso.
