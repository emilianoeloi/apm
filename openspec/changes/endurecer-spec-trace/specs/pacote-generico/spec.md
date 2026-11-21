## MODIFIED Requirements

### Requirement: Aviso de migração para a conferência de cenários
O `README.md` SHALL trazer a seção "Conferência de cenários na revisão" e um aviso de migração para projetos na versão anterior, dizendo que depois de atualizar o pacote o reviewer reprova a change com cenário novo ou alterado sem teste ligado por `Spec:`, que cenários antigos não são exigidos, que o script `spec-trace.py` prova o vínculo e não a qualidade do teste, que fixtures com `Spec:` podem aparecer como órfãs e que depois do título só valem o fim da linha ou um fechamento de comentário conhecido, sob pena de `ORFAO`.

```gherkin
Cenário: Leitor de projeto na versão anterior
  Dado alguém que usa a versão anterior do pacote
  Quando lê o README.md
  Então encontra a seção e o aviso sobre o reviewer reprovar cenário sem teste
  E encontra a regra do fim do título do marcador
```

#### Scenario: Leitor de projeto na versão anterior
- **WHEN** quem usa a versão anterior lê o `README.md`
- **THEN** encontra a seção "Conferência de cenários na revisão", o aviso de migração e a regra do fim do título do marcador
