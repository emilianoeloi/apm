# Proposal

## Why

O pacote já entrega o fluxo de SDLC em skills (`openspec-*`, `spdd-*`) e em prompts (`/opsx-*`), mais o gate de fase e os hooks, mas não tem nenhum agente: a F1 removeu os agentes do cowboy e o `.apm/agents/` ficou vazio. Hoje o desenvolvedor que virou orquestrador de agentes ainda faz tudo na sessão principal, sem papéis separados, sem escopo de escrita por papel e sem um revisor que não pode alterar código. A spec pede quatro agentes genéricos, de fonte única, que a sessão principal dispara um a um: `sdlc-planner`, `sdlc-coder`, `sdlc-reviewer` e `sdlc-auditor`. Há também o risco 2 da spec: os agentes antigos usavam o formato do Copilot (`tools: ['read', 'search', 'execute']`, `handoffs`) e o APM copia o arquivo sem conversão para `.claude/agents/`, onde esses nomes de ferramenta não existem. As docs do Claude Code e do GitHub Copilot, lidas para esta proposta, mostram um formato único que serve aos dois. É a funcionalidade F3 da Onda 1 da spec APM_SETUP V1.2 e fecha a parte do pacote que a calculadora em Go vai exercitar.

## What Changes

- Quatro agentes novos em `.apm/agents/`, um arquivo por papel, entregues pelo `apm install` para `.claude/agents/` e `.github/agents/`:
  - `sdlc-planner`: fase `proposal`; gera proposta OpenSpec, análise e REASONS Canvas; escreve só nas pastas de planejamento; nunca escreve código.
  - `sdlc-coder`: fase `apply`; gera o código pelas Operations do canvas; escreve só nas pastas de código e de testes do `harness.config.json` (mais os checkboxes do `tasks.md`); roda os sensores antes de entregar; para se não houver canvas.
  - `sdlc-reviewer`: só leitura; confere o código contra as Operations e as tasks, roda `openspec validate --strict` e os sensores e entrega um relatório com achados (arquivo, linha e Operation) e veredito para o humano decidir.
  - `sdlc-auditor`: só leitura e opcional; responde dúvidas e audita conformidade, arquitetura e segurança com evidências do repositório.
- Formato único de frontmatter, válido nos dois hosts: `name` em minúsculas com hífen, `description`, `tools` como texto separado por vírgula com os nomes do Claude (o Copilot os aceita como alias), sem `model` e sem `handoffs`.
- Os agentes não se chamam entre si, não têm a ferramenta de subagente e dizem que a sessão principal os dispara.
- Nenhum agente cita linguagem, pasta ou comando de um projeto: o que é do projeto vem do arquivo raiz do agente e do `harness.config.json`.
- Primeiros testes de contrato dos agentes em `tests/agents/` (formato, ferramentas mínimas por papel, neutralidade de stack, skills citadas existem, implantação idêntica à fonte).
- README com a lista de agentes e a ordem de disparo; skill `install-dev-harness` e modelo de `CLAUDE.md` com o fluxo por agentes.

Ficam fora desta change: o skill `sdlc-orchestrator` e a regra de disparo sem cadeia (F4, Onda 2), os agentes `harness-*` (F5), o sensor anti-fantasma (F8), a configuração de pré-lançamento do release-please e a prova com a calculadora em Go.

## Capabilities

### New Capabilities
- `sdlc-agent-contract`: o formato, a neutralidade de stack e a orquestração sem cadeia que valem para todos os agentes de SDLC do pacote.
- `sdlc-agent-roles`: o escopo, as entradas, as saídas e os limites de escrita de cada um dos quatro papéis (planejar, implementar, revisar, auditar).

### Modified Capabilities

Nenhuma. As specs principais existentes (`pacote-generico`, `hook-runtime`, `sensor-gate`) não mudam de comportamento.

## Impact

- **Arquivos novos**: `.apm/agents/sdlc-{planner,coder,reviewer,auditor}.agent.md`, `tests/agents/*`, e as cópias implantadas em `.claude/agents/` e `.github/agents/`.
- **Arquivos alterados**: `README.md`, `CHANGELOG.md`, `CLAUDE.md`, skill `install-dev-harness`, `.claude/`, `.agents/`, `.github/` e `apm.lock.yaml` (reimplantação).
- **Consumidores**: quem instalar a nova versão passa a receber os quatro agentes nos dois hosts. A pasta de agentes que a F1 deixou vazia volta a existir.
- **Release**: a mensagem é `feat:` sem `!`. O PR de release `1.0.0` do release-please continua aberto e não deve ser mesclado antes da change de pré-lançamento.
- **Risco**: o comportamento real de cada agente só se prova rodando-o. Esta change verifica o formato de forma mecânica (inclusive `claude plugin validate` quando disponível) e tenta um teste de fumaça de leitura apenas; a prova completa é a calculadora em Go. O Copilot continua sem verificação num host real.
