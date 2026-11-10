# apm — harness package

Pacote APM privado com o harness extraído do `cowboy`.

Consumo (no projeto):

```yaml
dependencies:
  apm:
    - emilianoeloi/apm#v0.2.0
```

Layout: `.apm/skills/*`, `.apm/prompts/*`, `.apm/agents/*`, `.apm/hooks/*.json`, `.apm/scripts/*` (hooks, phase_cli, pre-commit), `.apm/templates/*` (harness.config.json, quadrante).

## Workflow SDD (OpenSpec + OpenSPDD)

O pacote mantém **vendorizadas** as skills e prompts de OpenSpec e OpenSPDD, então `apm install` entrega o fluxo completo para `claude` e `copilot`:

| Origem | Em `.apm/` | Comandos |
|---|---|---|
| OpenSpec | `skills/openspec-*` (6) e `prompts/opsx-*.prompt.md` | `/opsx-propose`, `/opsx-explore`, `/opsx-apply`, `/opsx-update`, `/opsx-sync`, `/opsx-archive` |
| OpenSPDD (original, `openspdd generate -t codex`) | `skills/spdd-*` (5) | `/spdd-analysis`, `/spdd-reasons-canvas`, `/spdd-generate`, `/spdd-sync`, `/spdd-prompt-update` |

Skills autorais (`openspec-workflow`, `install-dev-harness`) integram o fluxo com o gate de fase do harness; o OpenSPDD é mantido sem alterações. O estado por projeto (`openspec/`) é criado com `openspec init --tools none`.

### Atualizando o vendor

```bash
python3 scripts/sync-vendor.py   # requer os CLIs openspec e openspdd
git diff                         # revise antes de publicar
```

As versões usadas ficam em [vendor.json](vendor.json). Não edite à mão os arquivos vendorizados — o próximo sync os sobrescreve; customizações vão nas skills autorais.

Pendente: confirmar como o APM entrega scripts de hook (ver perguntas na sessão).
