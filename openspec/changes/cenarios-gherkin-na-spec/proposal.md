# Proposal

## Why

Hoje a intenção de cada requisito mora em `#### Scenario:` com `WHEN`/`THEN`, formato que o `openspec validate --strict` exige mas que ninguém consegue executar nem ler de forma mecânica. A história H1 da especificação APM_SETUP_V2.0 pede cenários Gherkin na spec, para a intenção ficar testável: "como Emiliano, quero cenários Gherkin na spec, para a intenção ficar testável". Esta change (F1) define o formato exato do bloco e o torna obrigatório no planejamento; o sensor que o lê (F2) e o skill `acceptance-from-spec` (F3) vêm depois e **não** fazem parte daqui.

## What Changes

- **Formato fixo** (spec nova `spec-gherkin-scenarios`): sob cada `### Requirement:`, logo depois do parágrafo normativo e antes do primeiro `#### Scenario:`, um bloco cercado ```` ```gherkin ```` com ao menos um `Cenário: <título>` e os passos `Dado`, `Quando`, `Então` (palavras-chave em português; `E`/`Mas` como continuação). O título repete o de um `#### Scenario:` do mesmo requisito.
- **Só adição**: os `#### Scenario:` com `WHEN`/`THEN` continuam, porque a validação estrita os exige. OpenSpec e OpenSPDD seguem como estão.
- **Planner e orientações**: o agente `sdlc-planner` (`.apm/agents/sdlc-planner.agent.md`), o skill `openspec-workflow` e as regras de specs de `openspec/config.yaml` passam a exigir o bloco em cada requisito novo ou modificado. As cópias implantadas (`.claude`, `.github`, `.agents`) são regeneradas por `apm install --target claude,copilot`.
- **Retrofit das 6 specs existentes**: 31 requisitos recebem o bloco por deltas `MODIFIED` (texto e cenários idênticos, só o bloco entra). Os 2 requisitos que a change `versao-final-1-0-0` remove ficam de fora; os 3 que ela adiciona ganharam o bloco no próprio delta dela.
- **Testes primeiro**: um teste estático (stdlib) confere o formato dos requisitos efetivos (specs principais mais deltas ativos) e o contrato dos agentes passa a exigir a instrução no planner e no skill.
- **Rotina de quem opera**: toda proposta do planner passa a trazer um bloco a mais por requisito, e quem revisa a spec lê duas formas de cenário (Gherkin e `WHEN`/`THEN`).

Ficam fora desta change: o sensor que valida o bloco em qualquer projeto (F2), o skill `acceptance-from-spec` (F3), perfis de SDLC, e qualquer framework ou executor de testes Gherkin. O bloco é só texto legível por máquina.

## Capabilities

### New Capabilities
- `spec-gherkin-scenarios`: formato, posição, cenário mínimo, convivência com `WHEN`/`THEN`, obrigação do planner e das orientações, conformidade das specs principais.

### Modified Capabilities
- `hook-runtime`, `pacote-generico`, `release-versioning`, `sdlc-agent-contract`, `sdlc-agent-roles`, `sensor-gate`: cada requisito listado ganha o bloco Gherkin; o comportamento especificado não muda.

## Impact

- **Arquivos (apply)**: `.apm/agents/sdlc-planner.agent.md`, `.apm/skills/openspec-workflow/SKILL.md`, `openspec/config.yaml`, `tests/specs/` (novo), `tests/agents/test_contract.py`, `CLAUDE.md` e as cópias implantadas por `apm install`.
- **Não tocado**: `.apm/skills/openspec-propose/SKILL.md` (gerado pelo CLI do OpenSpec, autor `openspec`; `openspec update` o sobrescreveria).
- **Ordem de arquivamento**: arquivar `versao-final-1-0-0` antes desta change; os deltas não se sobrepõem em nenhum requisito.
- **Release**: mensagem `feat(agents):` (provoca versão minor). Mesclar o PR de release e dar push são atos do Elói.
- **Risco principal**: o Gherkin pesar. Mitigação: um bloco por requisito, mínimo de um cenário, sem exigir mais que isso.
