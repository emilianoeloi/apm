# Tasks

## 1. Testes primeiro (vermelhos)

- [x] 1.1 Criar `tests/hooks/test_gherkin_sensor.py` (em tabela, projetos temporários com `openspec/specs` e `openspec/changes`): requisito sem bloco reprova com código 2 citando capability, nome e motivo; todas as violações listadas; projeto conforme sai 0 sem stderr; delta `ADDED` sem bloco cita a change; `REMOVED` não conta; `RENAMED` não duplica; `archive/` ignorado; sem `openspec/` sai 0 com aviso; `--root` e `CLAUDE_PROJECT_DIR`; spec com bytes inválidos sai 2 sem traceback; modo `--on-validate` com `openspec validate --strict` sai 2, com `git status` sai 0 mudo, com payload inválido sai 0, com formato Copilot (`toolName`/`toolArgs`) dispara; verificar que falham porque o script não existe
- [x] 1.2 Ajustar `tests/hooks/test_package.py`: eventos `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`; matcher `Bash` do `PostToolUse` apontando para `gherkin-sensor.py`; importações permitidas incluem `_gherkin`; verificar que falham
- [x] 1.3 Ajustar `tests/specs/test_gherkin_blocks.py` para importar `validate`, `effective_requirements` e o leitor de `_gherkin` (sem defini-los) e conferir que o repo passa; verificar que falha com `ImportError` antes da biblioteca existir
- [x] 1.4 Acrescentar teste de que os modelos `harness.config.json` seguem com `sensors_command` vazio (já coberto em `test_package.py`; confirmar que continua verde)

## 2. Biblioteca e sensor

- [x] 2.1 Criar `.apm/hooks/scripts/_gherkin.py` movendo `parse_requirements`, `parse_delta`, `effective_requirements` e `validate` do teste da F1, com parâmetro `root`, campo `origin` e `RENAMED`; verificar que 1.3 e os casos da biblioteca em 1.1 passam
- [x] 2.2 Criar `.apm/hooks/scripts/gherkin-sensor.py` (CLI com `--root`, saída `gherkin: <capability> / Requirement: <nome> [change X]: <motivo>`, códigos 0 e 2); verificar que os casos de 1.1 sem hook passam
- [x] 2.3 Acrescentar o modo `--on-validate` (lê o payload, casa `openspec validate`, fail-open do `_common.run`); verificar que os casos de hook de 1.1 passam
- [x] 2.4 Registrar o `PostToolUse` (matcher `Bash`, `${PLUGIN_ROOT}`, timeout 10) em `.apm/hooks/harness.json`; verificar que 1.2 passa

## 3. Documentação e configuração

- [x] 3.1 Acrescentar ao `.apm/skills/install-dev-harness/SKILL.md` uma nota sobre o sensor de Gherkin e como compô-lo ao `sensors_command`; verificar a neutralidade com `grep`
- [x] 3.2 (sessão principal, fora do `code_prefixes`) README: seção "Sensor de Gherkin" com o que faz, como roda junto do `openspec validate`, como compor no `sensors_command` de um projeto-alvo, saída de exemplo e o aviso de que o `PostToolUse` no Copilot não foi verificado; linha na tabela de hooks
- [x] 3.3 (sessão principal) `harness.config.json`: acrescentar o sensor ao `sensors_command` deste repo; `CLAUDE.md`: citar o sensor nos quality gates
- [x] 3.4 (sessão principal, opcional, Q6) citar o sensor em `rules.specs` de `openspec/config.yaml` (não aplicada: Q6 decidida como "não por ora")

## 4. Implantação

- [x] 4.1 Rodar `apm install --target claude,copilot` e verificar que `PostToolUse` aparece em `.claude/apm-hooks.json` e `.github/hooks/`, e que os scripts implantados são idênticos à fonte (`diff`)
- [x] 4.2 Rodar `claude plugin validate .claude/agents`

## 5. Integração

- [x] 5.1 Rodar `python3 -m unittest discover -s tests -t . -v` e verificar que tudo passa
- [x] 5.2 Rodar `python3 .apm/hooks/scripts/gherkin-sensor.py` neste repo (deve sair 0) e, num projeto temporário com um requisito sem bloco, verificar código 2 e a citação do requisito
- [x] 5.3 Rodar `openspec validate sensor-de-gherkin --strict` e `openspec validate --specs --strict`
- [x] 5.4 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` e verificar que volta vazia
- [ ] 5.5 Rodar `openspec validate sensor-de-gherkin --strict` numa sessão com o hook instalado e verificar que o sensor dispara (registrar no PR; no Copilot, registrar como não verificado)

## Workflow follow-up

- Abrir o PR com título `feat(hooks): …`; push e mesclagem são do Elói.
- Depois do merge, `openspec archive sensor-de-gherkin`, trocar o `## Purpose` provisório de `gherkin-sensor` por uma frase real e rodar `openspec validate --specs --strict`.
