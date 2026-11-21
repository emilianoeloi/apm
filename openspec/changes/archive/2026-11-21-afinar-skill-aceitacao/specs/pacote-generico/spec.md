## ADDED Requirements

### Requirement: Aviso de migração para o skill afinado
O `README.md` SHALL acrescentar à seção "Testes de aceitação" um aviso de migração para projetos na versão anterior, dizendo o que muda no coder, no planner e na decisão do humano levada ao reviewer.

```gherkin
Cenário: Leitor de projeto na versão anterior
  Dado alguém que usa a versão anterior do pacote
  Quando lê o README.md
  Então encontra, em Testes de aceitação, o aviso sobre o falso verde, o Extra:, a fixture por constante e a prova humana
```

#### Scenario: Leitor de projeto na versão anterior
- **WHEN** quem usa a versão anterior lê o `README.md`
- **THEN** encontra, na seção "Testes de aceitação", o aviso sobre falso verde, `Extra:`, fixture por constante, prova humana e a decisão do humano no brief do reviewer
