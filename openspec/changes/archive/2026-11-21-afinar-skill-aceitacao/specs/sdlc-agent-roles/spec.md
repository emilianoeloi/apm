## ADDED Requirements

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
