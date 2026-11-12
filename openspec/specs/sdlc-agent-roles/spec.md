# sdlc-agent-roles Specification

## Purpose
Fixa o escopo, as entradas, as saídas e os limites de escrita de cada papel do SDLC por agentes, para que planejar, implementar, revisar e auditar rodem sem conflito e o humano decida o merge.

## Requirements

### Requirement: Planner planeja sem tocar em código
O `sdlc-planner` SHALL, na fase `proposal`, entregar a proposta OpenSpec validada, a análise SPDD e o REASONS Canvas usando os skills `openspec-explore`, `openspec-propose`, `spdd-analysis` e `spdd-reasons-canvas`, e SHALL escrever só nas pastas de planejamento do `harness.config.json`.

#### Scenario: Pedido de funcionalidade
- **WHEN** o planner recebe um pedido de funcionalidade
- **THEN** ele entrega a proposta, a análise e o canvas e `openspec validate --strict` passa

#### Scenario: Escrita de código na fase de proposta
- **WHEN** o planner tenta escrever fora das pastas de planejamento durante a fase `proposal`
- **THEN** o gate de fase bloqueia a escrita

#### Scenario: Fase incompatível
- **WHEN** o planner é disparado com a fase `apply` declarada
- **THEN** ele avisa e para sem alterar nada

### Requirement: Coder implementa pelo canvas
O `sdlc-coder` SHALL, na fase `apply` e com um canvas aprovado, gerar o código pelas Operations do canvas usando os skills `spdd-generate` e `openspec-apply-change`, escrever só nas pastas de código e de testes do `harness.config.json` e marcar as tasks, rodar o comando de sensores antes de entregar e parar com um aviso quando o canvas não existir.

#### Scenario: Canvas aprovado e fase apply
- **WHEN** o coder é disparado com o canvas aprovado e a fase `apply`
- **THEN** ele implementa as Operations, os sensores passam e as tasks ficam marcadas

#### Scenario: Canvas ausente
- **WHEN** o coder é disparado sem canvas
- **THEN** ele avisa a falta e para sem escrever código

#### Scenario: Escopo de escrita
- **WHEN** o coder termina
- **THEN** as únicas mudanças fora das pastas de código e de testes são os checkboxes do `tasks.md`

### Requirement: Reviewer só lê e decide pelo humano
O `sdlc-reviewer` SHALL conferir o código contra as Operations do canvas e as tasks, rodar `openspec validate --strict` e os sensores, e entregar um relatório com achados e veredito, sem alterar nenhum arquivo; cada achado SHALL citar arquivo, linha e a Operation do canvas.

#### Scenario: Relatório
- **WHEN** o reviewer é disparado sobre o código implementado
- **THEN** ele entrega um relatório com veredito e cada achado cita arquivo, linha e Operation

#### Scenario: Sem alteração
- **WHEN** o reviewer termina
- **THEN** o estado do repositório é idêntico ao anterior e `tools` não inclui `Write` nem `Edit`

#### Scenario: Escopo da implementação
- **WHEN** o reviewer encontra arquivos alterados fora das pastas de código e de testes e do `tasks.md`
- **THEN** ele registra um achado de escopo

### Requirement: Auditor responde com evidências
O `sdlc-auditor`, opcional, SHALL responder dúvidas e auditar conformidade, arquitetura e segurança citando evidências do repositório, sem alterar nenhum arquivo.

#### Scenario: Dúvida ou auditoria
- **WHEN** o auditor recebe uma dúvida ou um pedido de auditoria
- **THEN** ele responde com evidências (arquivo e linha) do repositório

#### Scenario: Sem alteração
- **WHEN** o auditor termina
- **THEN** o estado do repositório é idêntico ao anterior e `tools` não inclui `Write` nem `Edit`
