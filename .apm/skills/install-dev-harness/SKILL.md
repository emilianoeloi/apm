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
│ /opsx:propose → /spdd-analysis → /spdd-       │ → │ /spdd-generate → /opsx:apply │ → /opsx:archive
│ (proposal,      (contexto,        reasons-    │   │ (código a      (marca tasks, │   (fase limpa)
│  design, tasks)  riscos)          canvas)     │   │  partir do     validate)     │
│                                   (contrato)  │   │  canvas)                     │
└───────────────────────────────────────────────┘   └──────────────────────────────┘
                 ▲ phase_cli.py set proposal <change>        ▲ phase_cli.py set apply <change>
```

Quatro peças, cada uma com um dono:

| Peça | Dono | O que fornece |
|---|---|---|
| **APM** (`apm.yml`) | distribuição | skills, agents, prompts e hooks do harness para `claude` e `copilot` (`targets`) |
| **OpenSpec** (`openspec` CLI) | especificação | `openspec/`, comandos `/opsx:*` (Claude) e `/opsx-*` (Copilot), `validate`/`archive` |
| **OpenSPDD** (`openspdd` CLI) | prompt estruturado | comandos `/spdd-analysis`, `/spdd-reasons-canvas`, `/spdd-generate`, `/spdd-sync`, `/spdd-prompt-update` |
| **Harness gate** (hooks + `phase_cli.py`) | enforcement | bloqueia código em `proposal`, bloqueia `git push`/`rm -rf`/credenciais sempre |

Os hooks são scripts Python stdlib-only (só `python3` é requisito) e rodam
como processo externo — funcionam para qualquer stack do projeto alvo.

> **Não instale o harness “à mão” se o APM já o entrega.** Os arquivos em
> `templates/` são o fallback para projetos que não usam APM ou para o
> passo 5 (scripts de hook), que o APM ainda não materializa sozinho.

## Quando usar isto vs. quando não

Use quando o projeto quer **gate de fase real** + fluxo SDD. Se o objetivo é
só documentar convenções, um `AGENTS.md`/`CLAUDE.md` basta — não instale
hooks que o time não vai entender por que estão bloqueando.

Já tem OpenSpec/OpenSPDD instalados de forma legada (pré-APM)? Rode os
passos 2–3 mesmo assim: `openspec init` detecta e migra arquivos legados, e
`openspdd generate -f` atualiza os templates.

## Pré-requisitos

```bash
apm --version        # Agent Package Manager
openspec --version   # >= 1.x
openspdd --version
python3 --version
```

Se algum faltar, informe ao usuário e pare — não instale ferramentas globais
sem pedir.

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
   - Quer só os hooks de segurança sem gate de fase? Então deixe
     `planning_write_prefixes`/`code_prefixes` como `[]` e pule o SPDD.

3. **Instale o harness via APM** (skills, agents, prompts, hooks):
   ```bash
   apm install emilianoeloi/apm#<tag>     # ou adicione em apm.yml → dependencies.apm
   apm install --target claude,copilot    # reaplica para os hosts escolhidos
   ```
   Hooks são código executável: se o APM pedir, use `apm approve` depois de
   revisar. Use `apm install --dry-run` antes quando o projeto já tiver
   arquivos locais.

4. **Inicialize o OpenSpec** para os hosts escolhidos:
   ```bash
   openspec init --tools claude,github-copilot --no-animation --no-copilot-cloud
   ```
   Cria `openspec/{config.yaml,specs/,changes/archive/}`, skills
   `openspec-*` e os comandos `/opsx:*` (Claude, em `.claude/commands/opsx/`)
   e `/opsx-*` (Copilot, em `.github/prompts/`). Use `--tools all|none` ou
   outra lista conforme o passo 2. Depois, registre em
   `openspec/config.yaml` (`context:`/`rules:`) apenas o que o agente não
   infere do código — por exemplo, “propostas devem listar quality gates”.

5. **Inicialize o OpenSPDD** (um `generate` por host — `--all` exige `-t`):
   ```bash
   openspdd generate --all -f -t claude-code      # → .claude/commands/spdd-*.md
   openspdd generate --all -f -t github-copilot   # → .github/copilot-prompts/spdd-*.md
   ```
   Crie também as pastas de artefatos (`spdd/analysis/`, `spdd/prompt/`) —
   elas precisam estar em `planning_write_prefixes` para a fase `proposal`
   permitir escrita nelas.
   *Nota Copilot:* `openspdd` grava em `.github/copilot-prompts/`, mas o VS
   Code só descobre prompts em `.github/prompts/*.prompt.md`. Se o usuário
   quiser `/spdd-*` no chat do Copilot, copie/renomeie os arquivos para
   `.github/prompts/<nome>.prompt.md` e confirme.

6. **Instale o gate de fase** copiando `templates/` para o projeto:

   | Template | Destino | Placeholders |
   |---|---|---|
   | `templates/harness.config.json.template` | `harness.config.json` | `{{RULEBOOK_FILE}}`; `{{PLANNING_PREFIXES}}` = `["openspec/", "spdd/", ".harness/"]`; `{{CODE_PREFIXES}}` = ex. `["src/", "tests/"]` |
   | `templates/CLAUDE.md.template` | `CLAUDE.md` (só se não existir) | `{{RULEBOOK_FILE}}`, `{{QUALITY_GATES}}`, `{{CODE_PREFIXES_HUMAN}}` |
   | `templates/hooks/pre-tool-write-guard.py` | `scripts/hooks/` | — |
   | `templates/hooks/pre-tool-bash-guard.py` | `scripts/hooks/` | — |
   | `templates/hooks/session-start.py` | `scripts/hooks/` | — |
   | `templates/phase_cli.py` | `scripts/harness/phase_cli.py` | — |

   Se `CLAUDE.md`/`AGENTS.md` já existir, apenas acrescente a seção
   “Fase da change” (com o mapeamento do passo 8). Registre os hooks em
   `.claude/settings.json` fazendo **merge** com `templates/settings.hooks.json`
   (nunca sobrescreva). Se o APM já entrega os hooks via `.apm/hooks/*.json`,
   não duplique o registro — copie só os scripts.

7. **Verifique**:
   ```bash
   echo '{"source":"new"}' | python3 scripts/hooks/session-start.py
   openspec validate --all 2>&1 | tail -3   # sem changes ainda: ok/vazio
   openspec list
   openspdd list
   python3 scripts/harness/phase_cli.py show
   ```
   O primeiro comando deve imprimir JSON com `additionalContext` (fase não
   declarada + checklist de guias).

8. **Ensine o mapeamento fluxo ↔ fase** (inclua no `AGENTS.md`/`CLAUDE.md`):

   | Etapa do fluxo | Comando | Fase do harness |
   |---|---|---|
   | Propor | `/opsx:propose` (Claude) · `/opsx-propose` (Copilot) | `phase_cli.py set proposal <change>` **antes** |
   | Validar spec | `openspec validate <change> --strict` | `proposal` |
   | Analisar | `/spdd-analysis openspec/changes/<change>` → `spdd/analysis/` | `proposal` |
   | Canvas | `/spdd-reasons-canvas spdd/analysis/<arquivo>` → `spdd/prompt/` | `proposal` |
   | Gerar | `/spdd-generate spdd/prompt/<canvas>` | `phase_cli.py set apply <change>` **antes** |
   | Aplicar/fechar tasks | `/opsx:apply` · `/opsx-apply` + `openspec validate <change> --strict` | `apply` |
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

O hook (`scripts/hooks/*.py`) e o CLI (`scripts/harness/phase_cli.py`) leem o
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
- `git push`, `git reset --hard`, `git clean -f`, `git branch -D`, `rm -rf`.
- Escrita direta em `.env` via redirecionamento de shell (`> .env`,
  `tee .env`).

Isso não substitui revisão humana para `git push` — o hook bloqueia a
execução automática; o agente ainda deve pedir confirmação explícita ao
usuário antes de rodar o comando manualmente fora do hook.
