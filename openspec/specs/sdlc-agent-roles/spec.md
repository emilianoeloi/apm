# sdlc-agent-roles Specification

## Purpose
Fixa o escopo, as entradas, as saídas e os limites de escrita de cada papel do SDLC por agentes, para que planejar, implementar, revisar e auditar rodem sem conflito e o humano decida o merge.

## Requirements

### Requirement: Planner planeja sem tocar em código
O `sdlc-planner` SHALL, na fase `proposal`, entregar a proposta OpenSpec validada, a análise SPDD e o REASONS Canvas usando os skills `openspec-explore`, `openspec-propose`, `spdd-analysis` e `spdd-reasons-canvas`, e SHALL escrever só nas pastas de planejamento do `harness.config.json`.

```gherkin
Cenário: Pedido de funcionalidade
  Dado um pedido de funcionalidade e a fase proposal
  Quando o planner é disparado
  Então ele entrega a proposta, a análise e o canvas
  E openspec validate --strict passa
```

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

```gherkin
Cenário: Canvas aprovado e fase apply
  Dado um canvas aprovado e a fase apply
  Quando o coder é disparado
  Então ele implementa as Operations e os sensores passam
  E as tasks ficam marcadas
```

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

```gherkin
Cenário: Relatório
  Dado o código implementado
  Quando o reviewer é disparado
  Então ele entrega um relatório com veredito
  E cada achado cita arquivo, linha e Operation
```

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

```gherkin
Cenário: Dúvida ou auditoria
  Dado uma dúvida ou um pedido de auditoria
  Quando o auditor responde
  Então a resposta traz evidências do repositório com arquivo e linha
```

#### Scenario: Dúvida ou auditoria
- **WHEN** o auditor recebe uma dúvida ou um pedido de auditoria
- **THEN** ele responde com evidências (arquivo e linha) do repositório

#### Scenario: Sem alteração
- **WHEN** o auditor termina
- **THEN** o estado do repositório é idêntico ao anterior e `tools` não inclui `Write` nem `Edit`

### Requirement: Coder abre a implementação pelo teste de aceitação
O `sdlc-coder` SHALL, na fase `apply`, usar o skill `acceptance-from-spec` antes de implementar cada Operation que realiza um requisito com cenário aprovado, e SHALL incluir no relatório, por cenário, o teste ligado, a execução vermelha e a execução verde.

```gherkin
Cenário: Coder com cenário aprovado
  Dado um canvas aprovado, a fase apply e requisitos com cenário na change
  Quando o coder é disparado
  Então ele usa o skill acceptance-from-spec antes de implementar
  E o relatório traz, por cenário, o teste, o vermelho e o verde
```

#### Scenario: Coder com cenário aprovado
- **WHEN** o coder é disparado com canvas aprovado, fase `apply` e requisitos com cenário na change
- **THEN** ele usa o skill `acceptance-from-spec` antes de implementar e o relatório traz, por cenário, o teste, o vermelho e o verde

#### Scenario: Limites de escrita preservados
- **WHEN** o coder termina
- **THEN** as ferramentas e os limites de escrita do agente continuam os mesmos e o teste de contrato dos agentes passa

#### Scenario: Texto sem termos de stack
- **WHEN** o corpo do coder é conferido contra os termos de stack e do projeto de origem
- **THEN** a busca não encontra nenhum

### Requirement: Reviewer confere cada cenário contra um teste
O `sdlc-reviewer` SHALL conferir que cada `Cenário:` novo ou alterado pela change tem teste ligado pela linha `Spec:`, usando o `spec-trace.py` achado por `Glob` ou, sem ele, `grep -F` da trinca no fonte dos testes, SHALL ler cada teste ligado para confirmar que afirma o `Então`, SHALL tratar o cenário herdado sem teste como informativo e SHALL entregar a seção "Cenários x testes" sem alterar arquivo nem as `tools`.

```gherkin
Cenário: Revisão de change com cenários
  Dado uma change com cenários novos, testes ligados por Spec: e o script spec-trace.py implantado
  Quando o reviewer é disparado
  Então o relatório traz a seção Cenários x testes com o estado e o arquivo:linha de cada cenário
  E o git status --porcelain final é igual ao inicial
```

#### Scenario: Revisão de change com cenários
- **WHEN** o reviewer é disparado sobre uma change com cenários novos e testes ligados
- **THEN** o relatório traz a seção "Cenários x testes" com estado e `arquivo:linha` por cenário e o `git status --porcelain` final é igual ao inicial

#### Scenario: Script não encontrado
- **WHEN** o `Glob` não acha `spec-trace.py` ou `python3` falta
- **THEN** o reviewer confere com `grep -F` por cenário no fonte e diz no relatório que usou a reserva

#### Scenario: Cenário herdado
- **WHEN** um cenário de requisito `MODIFIED` é igual ao da spec principal e não tem teste
- **THEN** ele aparece como informativo na seção e não vira achado nem muda o veredito

#### Scenario: Ferramentas inalteradas
- **WHEN** o frontmatter do reviewer é lido
- **THEN** `tools` continua `Read, Grep, Glob, Bash`

### Requirement: Achados de cenário e veredito
O `sdlc-reviewer` SHALL classificar como alta, com veredito `REPROVADO`, o cenário novo ou alterado sem teste e o teste ligado que não afirma o `Então` (falso verde), e como média a linha `Spec:` órfã, o marcador ambíguo e a cobertura sem a linha `Spec:`; cada achado SHALL citar arquivo, linha e Operation, e sem o relatório do coder o reviewer SHALL dizer "vermelho não verificado".

```gherkin
Cenário: Cenário novo sem teste
  Dado uma change com um cenário novo sem teste ligado
  Quando o reviewer entrega o relatório
  Então há um achado de severidade alta para o cenário
  E o veredito é REPROVADO
```

#### Scenario: Cenário novo sem teste
- **WHEN** uma change tem um cenário novo sem teste ligado
- **THEN** o relatório traz um achado de severidade alta para o cenário e o veredito é `REPROVADO`

#### Scenario: Falso verde
- **WHEN** o teste ligado a um cenário só verifica que o ambiente executou, sem afirmar o `Então`
- **THEN** o relatório traz um achado de severidade alta de teste fraco

#### Scenario: Marcador órfão
- **WHEN** um teste traz uma linha `Spec:` sem cenário correspondente
- **THEN** o relatório traz um achado de severidade média e o veredito pode ser `APROVADO COM RESSALVAS`

#### Scenario: Cobertura sem marcador
- **WHEN** o reviewer acha por leitura um teste que cobre o cenário sem a linha `Spec:`
- **THEN** o achado cai para média e cita o arquivo do teste

### Requirement: Coder aplica as convenções afinadas do skill
O `sdlc-coder` SHALL apontar, em seu texto, as convenções afinadas do skill `acceptance-from-spec` (vermelho pela asserção e falso verde, anotação `Extra:` do cenário extra, herdado informativo e prova humana como pendente) sem duplicar o texto do skill, e SHALL relatá-las por cenário no Entregável, sem mudar `tools` nem os limites de escrita.

```gherkin
Cenário: Texto do coder cita as convenções
  Dado o texto do sdlc-coder
  Quando ele é lido
  Então cita o vermelho pela asserção, o Extra:, o herdado informativo e a prova humana
  E as tools continuam as mesmas

Cenário: Coder real aplica as convenções
  Dado uma change com um cenário só de prova humana e um extra com comportamento distinto
  Quando o sdlc-coder real é disparado em apply
  Então o relatório traz o cenário de prova humana como pendente e o extra anotado com Extra:
```

#### Scenario: Texto do coder cita as convenções
- **WHEN** o texto do `sdlc-coder` é lido
- **THEN** cita o vermelho pela asserção, a anotação `Extra:`, o cenário herdado como informativo e a prova humana como pendente, e `tools` continua `Read, Grep, Glob, Write, Edit, Bash, Skill`

#### Scenario: Coder real aplica as convenções
- **WHEN** o `sdlc-coder` real é disparado sobre uma change com um cenário só de prova humana e um extra com comportamento distinto
- **THEN** o relatório traz o cenário de prova humana como pendente e o extra anotado com `Extra:`

### Requirement: Planner gera tasks coerentes com o skill
O `sdlc-planner` SHALL gerar as tasks de teste com um teste por `Cenário:` do bloco `gherkin` (nunca por `#### Scenario:` sem `Cenário:`), SHALL anotar com `Extra:` o extra que mereça teste e SHALL registrar em `design.md`, na seção "Cenários só de prova humana", o `Cenário:` que só a prova humana cobre, com a task de prova correspondente.

```gherkin
Cenário: Texto do planner cita a regra das tasks
  Dado o texto do sdlc-planner
  Quando ele é lido
  Então manda um teste por Cenário: do bloco
  E cita o Extra: e a seção Cenários só de prova humana

Cenário: Planner real gera tasks coerentes
  Dado um pedido com um requisito que tem um cenário e um extra
  Quando o sdlc-planner real é disparado
  Então as tasks de teste listam um teste por Cenário: do bloco
  E o extra e a prova humana seguem a convenção
```

#### Scenario: Texto do planner cita a regra das tasks
- **WHEN** o texto do `sdlc-planner` é lido
- **THEN** manda um teste por `Cenário:` do bloco, cita a anotação `Extra:` e a seção "Cenários só de prova humana", e `tools` continua `Read, Grep, Glob, Write, Edit, Bash, Skill`

#### Scenario: Planner real gera tasks coerentes
- **WHEN** o `sdlc-planner` real é disparado sobre um pedido com um cenário e um extra
- **THEN** as tasks de teste listam um teste por `Cenário:` do bloco e o extra e a prova humana seguem a convenção
