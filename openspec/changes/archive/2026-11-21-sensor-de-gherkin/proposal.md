# Proposal

## Why

A F1 fixou o formato do bloco Gherkin em cada requisito (spec `spec-gherkin-scenarios`) e deixou um teste estático em `tests/specs/test_gherkin_blocks.py` que só vale para este repositório. A história H2 da especificação APM_SETUP_V2.0 pede o passo seguinte: "como Emiliano, quero um sensor de Gherkin, para saber quando falta cenário". O pacote é usado em outros projetos, então o sensor precisa viajar com ele, sem framework novo e sem depender de stack.

Não li a especificação no Drive; os critérios abaixo vêm do pedido da sessão principal.

## What Changes

- **Sensor `gherkin-sensor.py`** (`.apm/hooks/scripts/`, só biblioteca padrão): lê os requisitos efetivos de um projeto (specs principais mais deltas de changes ativas) e sai com 0 se todos têm o bloco Gherkin no formato da F1, ou com 2 listando cada violação como `capability / Requirement: nome / motivo`.
- **Biblioteca `_gherkin.py`** (mesmo diretório, ao lado de `_common.py`): recebe a lógica de leitura e validação que hoje vive no teste da F1. O teste da F1 passa a importá-la, sem duplicar nada.
- **Roda junto do `openspec validate`**: um hook `PostToolUse` (matcher `Bash`), registrado em `.apm/hooks/harness.json`, dispara o sensor sempre que o comando executado contém `openspec validate`. Entregue pelo APM, funciona em qualquer projeto que instale o pacote, sem caminho fixo.
- **Também na rede do Stop**: neste repositório o `sensors_command` ganha o sensor (`python3 -m unittest discover -s tests -t . && python3 .apm/hooks/scripts/gherkin-sensor.py`). Em projetos-alvo o `sensors_command` continua vazio por padrão; o README mostra como compor.
- **Raiz do projeto**: `--root` > `CLAUDE_PROJECT_DIR` > pasta com `.git` acima do diretório atual (a regra de `_common.project_root`). Sem `openspec/` na raiz o sensor sai com 0 e avisa que não há o que verificar.
- **Documentação**: seção "Sensor de Gherkin" no README e uma linha no skill `install-dev-harness`.

Só adições: nenhum hook, spec ou comportamento existente é removido.

**Rotina de quem opera**: depois de rodar `openspec validate`, a sessão passa a ver a saída do sensor (stderr, código 2) quando falta Gherkin; é um aviso a mais, não um passo manual. Quem quiser o sensor também no Stop de um projeto-alvo precisa editar o `sensors_command` (ação do humano).

Fora desta change: o skill `acceptance-from-spec` (F3), executor de Gherkin, perfis de SDLC, qualquer verificação da qualidade do texto dos passos (o sensor confere forma, não sentido).

## Capabilities

### New Capabilities
- `gherkin-sensor`: detecção de requisito sem cenário, requisitos efetivos, localização do `openspec/`, contrato de saída, disparo junto do `openspec validate`, biblioteca única.

### Modified Capabilities
- `hook-runtime`: a entrega pelo APM passa a registrar também `PostToolUse`; o helper permitido dos scripts inclui `_gherkin`.

## Impact

- **Arquivos (apply)**: `.apm/hooks/scripts/_gherkin.py` e `gherkin-sensor.py` (novos), `.apm/hooks/harness.json`, `tests/hooks/test_gherkin_sensor.py` (novo), `tests/hooks/test_package.py`, `tests/specs/test_gherkin_blocks.py`, `.apm/skills/install-dev-harness/SKILL.md` e as cópias implantadas por `apm install`.
- **Fora do escopo de escrita do coder** (`code_prefixes`: `.apm/`, `scripts/`, `tests/`): `harness.config.json` (`sensors_command` deste repo), `README.md`, `CLAUDE.md` e, se aceito, `openspec/config.yaml`. Ficam para a sessão principal.
- **Release**: `feat(hooks):` (minor). Push, PR e mesclagem são do Elói.
- **Risco principal**: o `PostToolUse` no Copilot não foi verificado num host real (ver design, Q2).
