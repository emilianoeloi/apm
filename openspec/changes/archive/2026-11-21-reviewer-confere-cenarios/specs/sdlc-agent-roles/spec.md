## ADDED Requirements

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
