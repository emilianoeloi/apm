## ADDED Requirements

### Requirement: Vermelho vem da asserção do cenário
O skill SHALL exigir que o vermelho de cada teste de aceitação venha da asserção do `Então` do cenário e SHALL NOT aceitar como vermelho o erro do ambiente; o teste que passa sem o programa existir SHALL ser tratado como falso verde e reforçado, afirmando o conteúdo e não só o código de saída.

```gherkin
Cenário: Teste que passa sem o programa
  Dado um teste de aceitação que passa antes de o programa existir
  Quando o coder segue o skill
  Então o coder relata falso verde e reforça o teste afirmando o conteúdo
  E o vermelho relatado vem da asserção do cenário
```

#### Scenario: Teste que passa sem o programa
- **WHEN** um teste de aceitação passa antes de o programa existir
- **THEN** o skill manda relatar falso verde e reforçar o teste afirmando o conteúdo, não só o código de saída

#### Scenario: Vermelho por erro do ambiente
- **WHEN** a falha do teste vem do ambiente (arquivo, módulo ou comando ausente, código de saída genérico)
- **THEN** o skill não a aceita como vermelho e manda relatar a asserção do cenário que falhou, ou, em linguagem compilada, o símbolo de produção ausente declarado

### Requirement: Cenário extra anotado sem virar órfão
O skill SHALL mandar anotar o `#### Scenario:` extra (sem `Cenário:` correspondente no bloco `gherkin`) que ganhar teste com a linha `Extra: <capability> / <requisito> / <título do #### Scenario>` e SHALL proibir a linha `Spec:` nesse caso, para o `spec-trace` não apontar `ORFAO`; o extra sem comportamento observável distinto SHALL NOT ganhar teste.

```gherkin
Cenário: Extra com comportamento distinto
  Dado um #### Scenario: extra que descreve comportamento observável distinto
  Quando o coder escreve o teste dele
  Então o teste traz a linha Extra: com a trinca
  E não traz a linha Spec:
```

#### Scenario: Extra com comportamento distinto
- **WHEN** o coder escreve o teste de um `#### Scenario:` extra com comportamento observável distinto
- **THEN** o teste traz a linha `Extra: <capability> / <requisito> / <título>` e nunca a linha `Spec:`

#### Scenario: Extra anotado não vira órfão
- **WHEN** o `spec-trace.py` roda sobre um teste com a linha `Extra:` e a trinca de um extra
- **THEN** a linha não sai `ORFAO` e a saída continua 0

### Requirement: Fixture com linha Spec montada por constante
O skill SHALL mandar montar por constante, em tempo de execução, a linha `Spec:` que aparecer dentro de fixture ou exemplo de teste, para que a linha literal não exista no fonte e o `spec-trace` não a aponte como `ORFAO`.

```gherkin
Cenário: Fixture montada por constante
  Dado um teste cuja fixture precisa de uma linha Spec: com três campos
  Quando o coder monta a fixture seguindo o skill
  Então a linha é montada por constante e não aparece literal no fonte
  E o spec-trace não aponta ORFAO para ela
```

#### Scenario: Fixture montada por constante
- **WHEN** uma fixture de teste precisa de uma linha `Spec:` com três campos
- **THEN** o skill manda montá-la por constante, e o `spec-trace.py` não aponta `ORFAO` para o fonte do teste, ao contrário da linha literal

### Requirement: Cenário de comportamento do modelo é prova humana
O skill SHALL mandar registrar como pendente de prova humana, com a decisão do humano, o `Cenário:` cujo comportamento só uma prova humana cobre (comportamento do modelo), e SHALL NOT permitir criar teste que finja cobri-lo sem provar o comportamento; o relatório SHALL listar esses cenários à parte dos cenários sem teste.

```gherkin
Cenário: Cenário que só a prova humana cobre
  Dado um Cenário: que descreve o comportamento do modelo
  Quando o coder o encontra na lista de cenários
  Então o relatório o lista como pendente de prova humana, com a decisão do humano
  E nenhum teste é criado para fingir cobertura
```

#### Scenario: Cenário que só a prova humana cobre
- **WHEN** o coder encontra um `Cenário:` que descreve o comportamento do modelo
- **THEN** o relatório o lista como pendente de prova humana (`SEM_TESTE` conhecido) com a decisão do humano

#### Scenario: Teste que não prova o comportamento
- **WHEN** só existe um teste que não prova o comportamento do cenário
- **THEN** o skill proíbe ligá-lo ao cenário pela linha `Spec:` e manda manter o cenário pendente

### Requirement: Cenário herdado em requisito modificado
O skill SHALL tratar como herdado o `Cenário:` de requisito `MODIFIED` idêntico (título e passos) ao da spec principal, SHALL NOT exigir teste novo para ele e SHALL exigir teste para o cenário novo ou de passos alterados, em acordo com o `spec-trace`, que mostra o herdado sem teste como informativo.

```gherkin
Cenário: Herdado não exige teste novo
  Dado um requisito MODIFIED com um cenário igual ao da spec principal e um cenário novo
  Quando o coder lista os cenários a testar
  Então só o cenário novo ganha teste ligado por Spec:
  E o herdado é relatado como informativo
```

#### Scenario: Herdado não exige teste novo
- **WHEN** o coder lista os cenários de um requisito `MODIFIED` com um cenário igual ao da spec principal e um novo
- **THEN** só o novo ganha teste ligado por `Spec:` e o herdado é relatado como informativo

### Requirement: Afinação só por adição e dentro do teto
O skill afinado SHALL manter todos os trechos obrigatórios do skill anterior, SHALL ter versão `1.1`, SHALL continuar dentro do teto de tamanho do teste (150 linhas) e sem termo de stack ou de origem, e as cópias implantadas SHALL ser idênticas à fonte depois de `apm install`.

```gherkin
Cenário: Skill afinado cabe no teto
  Dado o skill afinado com as adições desta change
  Quando o teste de tamanho e de trechos obrigatórios roda
  Então todos os trechos antigos continuam presentes
  E o skill não passa de 150 linhas nem cita termo de stack
```

#### Scenario: Skill afinado cabe no teto
- **WHEN** o teste de tamanho e de trechos obrigatórios roda sobre o skill afinado
- **THEN** todos os trechos do skill anterior continuam presentes, a versão é `1.1` e o arquivo não passa de 150 linhas nem cita termo de stack

#### Scenario: Cópias do skill idênticas à fonte
- **WHEN** `apm install --target claude,copilot` roda depois da edição
- **THEN** as cópias em `.claude/skills/acceptance-from-spec/` e `.agents/skills/acceptance-from-spec/` são idênticas à fonte
