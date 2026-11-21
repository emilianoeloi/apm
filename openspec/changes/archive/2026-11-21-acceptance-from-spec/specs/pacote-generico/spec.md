## ADDED Requirements

### Requirement: Aviso de migração para os testes de aceitação
O `README.md` SHALL trazer a seção "Testes de aceitação" e um aviso de migração para projetos na versão anterior, dizendo que depois de atualizar o pacote o coder cria o teste de aceitação antes do código, que projetos sem ferramenta de teste recebem uma proposta e esperam a aprovação do humano, e que o `sensors_command` precisa rodar esses testes.

```gherkin
Cenário: Leitor de projeto na versão anterior
  Dado alguém que usa a versão anterior do pacote
  Quando lê o README.md
  Então encontra a seção Testes de aceitação e o aviso de migração
```

#### Scenario: Leitor de projeto na versão anterior
- **WHEN** quem usa a versão anterior do pacote lê o `README.md`
- **THEN** encontra a seção "Testes de aceitação" e o aviso sobre a proposta de ferramenta e o `sensors_command`
