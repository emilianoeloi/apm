# Proposal

## Why

As três funcionalidades do MVP da Onda 1 (F1, F2 e F3) já estão na `main`, e o release-please abriu o PR de release #12 propondo a versão `1.0.0` final. A spec manda outra coisa: o MVP sai como pré-lançamento `1.0.0-alpha.1`, a prova da calculadora em Go roda sobre ele e a `1.0.0` só sai depois da prova aprovada. A configuração atual não sabe fazer isso: com commits incompatíveis ela calcula `1.0.0`, e mesclar o PR #12 hoje publicaria a versão estável sem prova nenhuma. A spec marca como "não informado" como configurar o release-please para pré-lançamento; esta change fecha esse ponto com base na documentação e no código do release-please, e é a última peça do MVP da Onda 1.

## What Changes

- Configurar o release-please para pré-lançamento no pacote `.` de `release-please-config.json`: `"versioning": "prerelease"`, `"prerelease": true` e `"prerelease-type": "alpha.1"`. O PR de release #12 passa de `1.0.0` para `1.0.0-alpha.1`, a tag será `v1.0.0-alpha.1` (sem nome de componente) e o GitHub Release sai marcado como pré-lançamento.
- Os pré-lançamentos seguintes incrementam o número sozinhos (`alpha.2`, `alpha.3`, …), sem uma configuração de versão fixa (`release-as`) que alguém precise lembrar de remover.
- A versão final fica a uma mudança de configuração (`"prerelease": false`): o próximo PR de release descarta o sufixo e propõe `1.0.0`.
- Teste do pacote (`tests/release/`) que guarda a configuração: chaves do pré-lançamento presentes, nenhum `release-as` pendente, manifesto coerente e workflow que continua sem mesclar nada sozinho.
- README: a seção de releases passa a explicar o pré-lançamento e como a versão final sai, e corrige a frase sobre a marcação `x-release-please-version`, que não existe no `apm.yml` (o bot atualiza a linha `version:` pelo `extra-files`).

Ficam fora desta change: mesclar o PR de release (ato do Elói), a publicação da tag, a troca do exemplo de consumo do README para `#v1.0.0-alpha.1` (só vale depois de a tag existir), o roteiro de teste manual e o fechamento da Onda 1, a `1.0.0` final e a calculadora em Go.

## Capabilities

### New Capabilities
- `release-versioning`: como o pacote é versionado e publicado pelo release-please, com a primeira publicação do `1.0.0` como pré-lançamento, a numeração dos pré-lançamentos seguintes e a saída da versão final por configuração.

### Modified Capabilities

Nenhuma. As specs principais existentes não mudam de comportamento.

## Impact

- **Arquivos alterados**: `release-please-config.json`, `README.md`, `CHANGELOG.md` e, só se necessário, o `CLAUDE.md`.
- **Arquivos novos**: `tests/release/test_release_config.py`.
- **Efeito no GitHub após o merge**: o bot atualiza o PR #12 para `1.0.0-alpha.1`, com o `apm.yml` e o manifesto na mesma versão; mesclar esse PR continua sendo ato humano do Elói e cria a tag `v1.0.0-alpha.1` e um GitHub Release de pré-lançamento.
- **Consumidores**: nenhum é afetado até a tag existir; quem quiser o pré-lançamento passa a apontar para `v1.0.0-alpha.1`, e a `v0.3.1` continua sendo a última versão estável.
- **Release**: a mensagem desta change é `ci(release):`, que não altera a versão calculada.
- **Risco**: `prerelease-type: "alpha.1"` usa o texto do tipo como o primeiro sufixo, comportamento que a documentação não descreve e que foi confirmado lendo o código da estratégia; a change o confirma de novo rodando a própria biblioteca antes de depender dele.
