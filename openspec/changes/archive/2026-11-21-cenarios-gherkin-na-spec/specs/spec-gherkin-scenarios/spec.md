# spec-gherkin-scenarios Specification

## Purpose
Fixa o formato do cenário Gherkin que acompanha cada requisito das specs do OpenSpec, para a intenção ficar testável e legível por máquina, e obriga o planner e as orientações do pacote a gerá-lo.

## ADDED Requirements

### Requirement: Bloco Gherkin cercado sob cada requisito
Cada `### Requirement:` de uma spec do OpenSpec (principal ou delta `ADDED`/`MODIFIED`) SHALL conter um bloco cercado com a linguagem `gherkin` (abertura ```` ```gherkin ````), logo depois do parágrafo normativo e antes do primeiro `#### Scenario:`.

```gherkin
Cenário: Bloco depois do parágrafo normativo
  Dado um requisito com parágrafo normativo e cenários WHEN/THEN
  Quando o bloco gherkin cercado é inserido
  Então ele fica depois do parágrafo e antes do primeiro "#### Scenario:"
```

#### Scenario: Bloco depois do parágrafo normativo
- **WHEN** um requisito de qualquer spec é lido
- **THEN** o bloco ```` ```gherkin ```` aparece depois do parágrafo com SHALL ou MUST e antes do primeiro `#### Scenario:`

#### Scenario: Um bloco por requisito
- **WHEN** a spec é inspecionada requisito a requisito
- **THEN** cada requisito tem exatamente um bloco `gherkin`, que pode reunir mais de um `Cenário:`

### Requirement: Cenário mínimo em português
Cada bloco SHALL conter ao menos um `Cenário: <título>` com ao menos um passo `Dado`, um `Quando` e um `Então`, nessa ordem, cada passo em linha própria e em português; `E` e `Mas` SHALL ser aceitos como continuação, e o título SHALL repetir o de um `#### Scenario:` do mesmo requisito.

```gherkin
Cenário: Cenário mínimo completo
  Dado um bloco gherkin com um Cenário
  Quando o bloco é lido linha a linha
  Então existem os passos Dado, Quando e Então, nessa ordem
```

#### Scenario: Cenário mínimo completo
- **WHEN** o bloco de um requisito é lido linha a linha
- **THEN** há um `Cenário:` seguido de `Dado`, `Quando` e `Então`, nessa ordem, com as palavras-chave em português e `Então` com acento

#### Scenario: Rastro até o cenário WHEN/THEN
- **WHEN** o título de um `Cenário:` é comparado com os `#### Scenario:` do mesmo requisito
- **THEN** ele é igual ao título de um deles

### Requirement: Bloco convive com os cenários WHEN/THEN
O bloco Gherkin SHALL ser acréscimo: os `#### Scenario:` com `WHEN`/`THEN`, exigidos por `openspec validate --strict`, SHALL permanecer em todo requisito, e a validação estrita SHALL passar com os dois presentes.

```gherkin
Cenário: Validação estrita com os dois formatos
  Dado uma spec com o bloco gherkin e os "#### Scenario:" WHEN/THEN
  Quando "openspec validate --strict" roda
  Então a validação passa sem avisos
```

#### Scenario: Validação estrita com os dois formatos
- **WHEN** `openspec validate --strict` roda sobre specs com o bloco e com os `#### Scenario:`
- **THEN** a validação passa sem erros nem avisos

### Requirement: Planner e orientações exigem o bloco
O agente `sdlc-planner`, o skill `openspec-workflow` e as regras de specs em `openspec/config.yaml` SHALL exigir o bloco Gherkin em cada requisito novo ou modificado, com o formato desta spec, e as cópias implantadas SHALL ser idênticas à fonte em `.apm/`.

```gherkin
Cenário: Planner gera o bloco em cada requisito
  Dado o sdlc-planner com a instrução do bloco Gherkin
  Quando ele gera a proposta com requisitos
  Então cada requisito tem ao menos um cenário Dado, Quando e Então em bloco cercado
```

#### Scenario: Planner gera o bloco em cada requisito
- **WHEN** o planner gera uma proposta com requisitos
- **THEN** cada requisito tem ao menos um cenário Dado/Quando/Então num bloco `gherkin` cercado

#### Scenario: Instrução presente na fonte e nas cópias
- **WHEN** `.apm/agents/sdlc-planner.agent.md` e `.apm/skills/openspec-workflow/SKILL.md` são lidos junto com as cópias implantadas
- **THEN** todos citam o bloco `gherkin`, e as cópias são idênticas à fonte

### Requirement: Specs principais em conformidade
Depois do arquivamento desta change, todo `### Requirement:` das specs principais em `openspec/specs/` SHALL ter o bloco Gherkin no formato desta spec.

```gherkin
Cenário: Specs principais com bloco em todo requisito
  Dado as specs principais depois do arquivamento da change
  Quando cada requisito é verificado
  Então todos têm o bloco gherkin com Dado, Quando e Então
```

#### Scenario: Specs principais com bloco em todo requisito
- **WHEN** cada `### Requirement:` de `openspec/specs/*/spec.md` é verificado
- **THEN** todos têm o bloco `gherkin` com `Cenário:`, `Dado`, `Quando` e `Então`
