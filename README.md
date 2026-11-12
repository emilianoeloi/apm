# apm

Pacote APM público e genérico, com Lean Inception, Harness e SDLC em skills, agentes e hooks, para qualquer stack (iOS, Rust, JavaScript, Go e outras). É instalado por versão e entregue para `claude` e `copilot`.

Consumo (no projeto):

```yaml
dependencies:
  apm:
    - emilianoeloi/apm#v0.3.1
```

Layout: `.apm/skills/*`, `.apm/prompts/*`, `.apm/agents/*`, `.apm/hooks/*` (registro e scripts de hook), `.apm/scripts/*` (`phase_cli.py` e pre-commit genérico) e `.apm/templates/*` (`harness.config.json` e modelo do quadrante).

## Migração da 0.3.x

A limpeza do projeto de origem (`cowboy`, uma calculadora em COBOL) removeu, de forma **incompatível**:

- os agentes `cobol-vibecoder`, `cobol-planner`, `cobol-coder`, `cobol-reviewer` e `readme-writer`;
- os prompts `criar-programa`, `implementar-soma`, `implementar-subtracao`, `implementar-log`, `testar-programa`, `atualizar-readme` e `manutencao-repositorio`;
- as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`;
- o hook de encerramento `cowboy.json` (rodava `make fitness`) e o script de pre-commit que compilava COBOL.

O conteúdo não foi movido: quem ainda precisa dele deve manter a dependência na tag `v0.3.1`, que guarda o estado antigo. O hook de encerramento que o substitui é genérico (veja "Hooks" abaixo); os agentes de SDLC chegam nas próximas versões.

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

## Hooks

O pacote entrega os hooks pelo APM: `apm install --target claude,copilot` copia os scripts (com o helper `_common.py`) e os registra em `.claude/settings.json` e `.github/hooks/`, sem cópia manual. Hooks são código executável: revise os scripts e, se o APM pedir, rode `apm approve`.

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

A versão do `apm.yml` é atualizada pelo bot (linha marcada com `x-release-please-version`); não edite a versão à mão. Tags `v*` são protegidas contra apagar e mover.
