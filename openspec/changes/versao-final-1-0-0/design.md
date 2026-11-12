# Design

## Context

O manifesto está em `1.0.0-alpha.1` e a configuração do pacote `.` tem `versioning: "prerelease"`, `prerelease: true` e `prerelease-type: "alpha.1"` (change `prelancamento-alpha`). A prova da calculadora em Go foi aprovada pelo Elói. A estratégia `prerelease` do release-please (código em `src/versioning-strategies/prerelease.ts`) calcula o bump e, quando `prerelease` é falso, descarta o sufixo; a biblioteca foi executada nas versões `17.6.0` (piso da ação) e `17.11.2`.

Resultados da simulação com a configuração candidata (`prerelease: false`, estratégia mantida):
- `1.0.0-alpha.1` com commits só de `docs`, `ci` e `chore` (os reais desde a tag), com um `feat` ou com um incompatível: `1.0.0`.
- Depois da `1.0.0`: `feat` resulta em `1.1.0`, `fix` em `1.0.1` e incompatível em `2.0.0`.
- Armadilha: com a estratégia padrão (sem `versioning`) a partir de `1.0.0-alpha.1`, um incompatível dá `2.0.0-alpha.1` e um `feat` dá `1.1.0-alpha.1`.

## Goals / Non-Goals

**Goals:**
- O próximo PR de release propõe `1.0.0`, e só isso.
- A configuração fica guardada por teste contra as duas armadilhas conhecidas: `release-as` esquecido e saída precoce da estratégia de pré-lançamento.

**Non-Goals:**
- Mesclar o PR de release ou publicar a tag: atos do Elói.
- Limpar `versioning` e `prerelease-type`: só depois de a `v1.0.0` existir.
- Atualizar o exemplo de consumo do README e a dependência do `calculadora_go`: só depois da tag.

## Decisions

1. **Só `prerelease` muda, para `false`.** `versioning` e `prerelease-type` ficam, porque sem a estratégia de pré-lançamento o bot propõe versões erradas a partir de um alpha (simulação acima). Alternativa descartada: remover as três chaves de uma vez, que parece uma limpeza e produz `2.0.0-alpha.1`.
2. **`release-as` continua proibido.** Para a `1.0.0`, `release-as: "1.0.0"` também funcionaria, mas fixaria a versão e repetiria a proposta depois da tag; a mudança de estado da configuração é suficiente.
3. **Teste novo da armadilha.** O teste passa a exigir que, enquanto o manifesto tiver um sufixo de pré-lançamento, `versioning` seja `prerelease`; e `prerelease` seja falso. Depois da tag, a limpeza das chaves atualiza o teste.
4. **Spec:** os dois requisitos do período de pré-lançamento saem (cumpridos) e entra o requisito da versão final. Sem análise SPDD nem canvas: a mudança é de configuração e tem dois cenários de código, e o planejamento pelo OpenSpec cobre o que há para decidir. É uma escolha desta change; as anteriores usaram o canvas completo.
5. **Documentação:** README e `CLAUDE.md` passam a dizer que a configuração já está na versão final, que mesclar o PR de release publica a `1.0.0` e que a limpeza vem depois da tag.

## Risks / Trade-offs

- [Mesclar o PR de release sem conferir publicaria uma versão errada, e tags `v*` não se apagam] → conferir título, `apm.yml`, manifesto e CHANGELOG do PR antes de mesclar; a simulação e o teste já fixam `1.0.0`.
- [Alguém limpar `versioning` antes da tag e fazer o bot propor `2.0.0-alpha.1`] → o teste novo falha enquanto o manifesto for um pré-lançamento; o README e o `CLAUDE.md` avisam.
- [O bot não recalcular o PR de release de imediato] → o push na `main` dispara o workflow; o log mostra o motivo, e nada é publicado sem o merge humano.
- [Consumidores que apontam para a `main` passam a receber a `1.0.0` quando ela sair] → é o comportamento esperado de uma versão final; os pré-lançamentos continuam disponíveis pela tag.

## Migration Plan

1. Atualizar o teste (falhando), mudar `prerelease` para `false` e fazer o teste passar.
2. Atualizar README, `CLAUDE.md` e CHANGELOG; abrir o PR `ci(release):`; mesclar é ato do Elói.
3. Depois do merge: conferir o PR de release atualizado para `1.0.0`; o Elói o mescla e a tag `v1.0.0` nasce.
4. Depois da tag: trocar o exemplo de consumo do README para `#v1.0.0`, apontar o `calculadora_go` para a `v1.0.0` e remover `versioning` e `prerelease-type` (com o teste ajustado).
5. Rollback: reverter o commit; o bot volta a propor `1.0.0-alpha.2`; nada foi publicado enquanto o PR de release não for mesclado.
