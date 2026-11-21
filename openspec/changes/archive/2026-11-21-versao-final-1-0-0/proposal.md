# Proposal

## Why

A prova da calculadora em Go foi concluída e o Elói a aprovou: o pacote, na versão `v1.0.0-alpha.1`, criou do zero um projeto real (duas funcionalidades pelo fluxo planner, coder e reviewer, uma delas fechada num pull request mesclado), com os testes passando na `main` publicada. A spec manda publicar a `1.0.0` final só depois dessa aprovação, e a configuração do release-please ainda está no modo de pré-lançamento (`"prerelease": true`), então o próximo PR de release proporia `1.0.0-alpha.2`. Esta change faz a configuração propor a `1.0.0`, sem publicar nada: mesclar o PR e o PR de release continua sendo ato do Elói.

## What Changes

- `release-please-config.json`: `"prerelease"` passa de `true` para `false`. As chaves `"versioning": "prerelease"` e `"prerelease-type": "alpha.1"` **ficam** até a tag `v1.0.0` existir: a simulação com a biblioteca do release-please mostrou que, sem a estratégia de pré-lançamento, o bot proporia `2.0.0-alpha.1` ou `1.1.0-alpha.1` a partir de `1.0.0-alpha.1`.
- O teste de configuração (`tests/release/`) passa a guardar a versão final: `prerelease` falso, `versioning` mantido enquanto o manifesto for um pré-lançamento, nenhum `release-as`.
- README e `CLAUDE.md`: o texto de pré-lançamento passa a dizer que a configuração já está na versão final e que a limpeza das chaves de pré-lançamento vem depois da tag.
- CHANGELOG: registra a preparação da `1.0.0`.
- Retira da spec principal os dois requisitos que só valem durante o pré-lançamento (primeira publicação como alpha e numeração dos alphas, já cumpridos pela tag `v1.0.0-alpha.1`) e acrescenta o requisito da versão final.

Ficam fora desta change: mesclar o PR de release e publicar a tag `v1.0.0` (atos do Elói), trocar o exemplo de consumo do README e a dependência do `calculadora_go` para a `v1.0.0` (só depois de a tag existir), e a limpeza final das chaves `versioning` e `prerelease-type`.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities
- `release-versioning`: a versão final `1.0.0` sai por configuração; os requisitos exclusivos do período de pré-lançamento são removidos.

## Impact

- **Arquivos alterados**: `release-please-config.json`, `tests/release/test_release_config.py`, `README.md`, `CLAUDE.md`, `CHANGELOG.md` e a spec `release-versioning` (via arquivamento).
- **Efeito no GitHub após o merge**: o bot abre um PR de release propondo `1.0.0`, com o `apm.yml` e o manifesto na mesma versão; ao mesclá-lo, o Elói cria a tag `v1.0.0` e um GitHub Release publicado (não marcado como pré-lançamento).
- **Consumidores**: nenhum é afetado até a tag existir; a `v1.0.0-alpha.1` continua disponível.
- **Release**: a mensagem desta change é `ci(release):`, que não altera a versão calculada.
- **Risco**: tags `v*` não se apagam nem se movem, então o PR de release deve ser conferido (título, `apm.yml`, manifesto e CHANGELOG) antes de ser mesclado.
