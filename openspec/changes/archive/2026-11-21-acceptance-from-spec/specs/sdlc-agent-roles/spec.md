## ADDED Requirements

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
