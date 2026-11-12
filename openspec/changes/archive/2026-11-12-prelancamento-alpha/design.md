# Design

## Context

O release-please roda por `.github/workflows/release-please.yml` (ação `googleapis/release-please-action` v5.0.0, que usa o pacote `release-please` `^17.6.0`) em todo push na `main`, com `release-please-config.json` e `.release-please-manifest.json`. O pacote é `release-type: simple`, `include-v-in-tag: true`, `include-component-in-tag: false` e `extra-files: ["apm.yml"]`. O manifesto está em `0.3.1`. O PR de release #12 já propõe `1.0.0`, porque F1 trouxe um commit incompatível.

Pesquisa feita para esta change (documentação e código do release-please):
- A estratégia de versionamento `prerelease` só gera sufixo quando `"prerelease": true`; o tipo vem de `"prerelease-type"`. Com `false`, ela calcula o bump e **descarta o sufixo**.
- Código da estratégia (`src/versioning-strategies/prerelease.ts`): partindo de uma versão estável, um commit incompatível dá `major + 1` com o texto de `prerelease-type` como sufixo, ou seja, `0.3.1` + `alpha` resulta em `1.0.0-alpha` (sem `.1`); partindo de uma versão que já tem sufixo, o último grupo de dígitos do sufixo é incrementado (`alpha.1` vira `alpha.2`; `alpha` sem número vira `alpha.1`). Para versões `x.0.0-…`, qualquer tipo de commit incrementa o sufixo.
- `release-as` fixa a versão, mas a documentação avisa que deve ser removido ou atualizado depois do release, senão toda proposta seguinte repete a mesma versão.
- `"prerelease": true` também marca o GitHub Release como pré-lançamento (e os de versão menor que `1.0.0`).
- O schema oficial (`schemas/config.json`) tem as chaves `versioning`, `prerelease`, `prerelease-type` e `release-as`.
- O `apm.yml` não tem marcador `x-release-please-version`, mas o PR #12 mostra que o bot atualiza a linha `version:` pelo `extra-files`; a frase do README sobre o marcador está errada.

## Goals / Non-Goals

**Goals:**
- A primeira publicação do `1.0.0` sai como `1.0.0-alpha.1`, com tag `v1.0.0-alpha.1` e GitHub Release de pré-lançamento.
- Os pré-lançamentos seguintes numeram sozinhos, sem configuração temporária que dependa de memória.
- A versão final sai por uma mudança de configuração, depois da prova.

**Non-Goals:**
- Mesclar o PR de release ou publicar a tag: atos do Elói.
- Renomear `package-name` (`harness`): mudaria o nome da branch do bot e criaria um PR de release novo, deixando o #12 órfão.
- Trocar o workflow, a ação ou a política de proteção das tags `v*`.
- Atualizar o exemplo de consumo do README para a nova tag antes de ela existir.

## Decisions

1. **`versioning: "prerelease"`, `prerelease: true` e `prerelease-type: "alpha.1"`, sem `release-as`.** Como o tipo vira o primeiro sufixo, o primeiro cálculo dá `1.0.0-alpha.1`, e os seguintes incrementam o número. Alternativas descartadas: `prerelease-type: "alpha"`, que daria `1.0.0-alpha` (sem número) na primeira vez e não casa com a tag da spec; e `release-as: "1.0.0-alpha.1"`, que é documentada, mas trava a versão se ninguém a remover depois do release.
2. **Versão final por `"prerelease": false`.** O próprio código descarta o sufixo e propõe `1.0.0`. Depois disso, `versioning` e `prerelease-type` podem sair numa limpeza. Alternativa descartada: `release-as: "1.0.0"`, que tem o mesmo problema de ficar preso.
3. **Manter `package-name: harness`.** O nome só aparece na branch do bot e no título; mudá-lo abriria outro PR de release e deixaria o #12 aberto sem dono.
4. **Teste da configuração em `tests/release/`** (só `unittest`): chaves do pré-lançamento com os valores esperados, ausência de `release-as`, manifesto com a chave `.`, `apm.yml` em `extra-files`, tag sem componente e workflow sem mesclagem automática. É o que impede que alguém reintroduza um `release-as` esquecido.
5. **Verificação com a própria biblioteca, fora do repositório.** Numa pasta temporária, instalar `release-please` nas versões `17.6.0` (piso da ação) e a mais recente `17.x` e calcular, com os valores desta configuração, as versões de `0.3.1` com commit incompatível, `alpha.1` com `feat`, `alpha.2` com `fix` e `alpha.3` com `prerelease` falso. Isso confirma o comportamento que a documentação não descreve, sem tocar no GitHub.
   - **Resultado no apply:** os 8 cenários passaram nas duas versões (`17.6.0` e `17.11.2`): `0.3.1` com os commits reais desde a `v0.3.1` resulta em `1.0.0-alpha.1`; `feat`, `fix`, só `chore`/`ci` e um incompatível sobem o número (`alpha.2` a `alpha.5`); com `prerelease` falso, `1.0.0-alpha.3` resulta em `1.0.0` para `feat`, `fix` e incompatível. Contraste: `prerelease-type: "alpha"` daria `1.0.0-alpha`. A configuração valida contra o schema oficial com `jsonschema`.
6. **Efeito real conferido depois do merge:** o bot atualiza o PR #12 sozinho no push na `main`; a conferência é ler o título, a versão no `apm.yml` e no manifesto e o CHANGELOG do PR, antes de o Elói mesclá-lo.
7. **README:** a seção de releases explica o pré-lançamento, a `v0.3.1` como última estável, a saída da final e corrige a frase do marcador; o exemplo de consumo continua em `v0.3.1` até a tag existir.

## Risks / Trade-offs

- [`prerelease-type: "alpha.1"` depende de um comportamento que a documentação não cita] → confirmado na leitura do código, na execução da biblioteca (decisão 5) e pelo teste de configuração; se uma versão futura mudar, o PR de release mostra a versão errada antes de qualquer publicação.
- [Mesclar o PR #12 antes desta change publicaria a `1.0.0` final] → a change entra antes; o PR #12 não deve ser mesclado até estar em `1.0.0-alpha.1`, e mesclar é ato humano.
- [O bot pode não atualizar o PR #12 de imediato] → o push na `main` dispara o workflow; se não atualizar, o log da execução mostra o motivo e nada é publicado.
- [A linha `version:` do `apm.yml` pode ficar errada com sufixo] → conferida no diff do PR de release antes do merge.
- [A tag `v1.0.0-alpha.1` não pode ser apagada nem movida (tags `v*` protegidas)] → o erro seria definitivo; por isso a conferência do PR de release vem antes de o Elói mesclar.
- [Consumidor que apontar para `main` ou usar "mais recente" pode receber o pré-lançamento] → o README diz que a `v0.3.1` é a última estável e que o pré-lançamento exige a tag explícita.

## Migration Plan

1. Escrever o teste de configuração (falhando), alterar `release-please-config.json` e fazer o teste passar.
2. Rodar a verificação com a biblioteca numa pasta temporária e registrar o resultado.
3. Atualizar README e CHANGELOG; abrir o PR `ci(release):`; mesclar é ato do Elói.
4. Depois do merge: conferir o PR #12 atualizado; o Elói mescla o PR de release e a tag `v1.0.0-alpha.1` nasce.
5. Fechar a Onda 1: README com o consumo da tag nova, CHANGELOG, roteiro de teste e retrospectiva.
6. Rollback: reverter o commit da configuração; o bot volta a propor `1.0.0`; nada foi publicado enquanto o PR de release não for mesclado.
