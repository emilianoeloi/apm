# release-versioning Specification

## Purpose
Garante que o pacote seja publicado pelo release-please de modo que o MVP saia como pré-lançamento, os pré-lançamentos seguintes numerem sozinhos e a versão final dependa só de uma mudança de configuração e de um ato humano.

## Requirements

### Requirement: Versão final por mudança de configuração
Com `prerelease` falso, o release-please SHALL propor a versão final `1.0.0` a partir de qualquer `1.0.0-alpha.N`, sem outra alteração de configuração.

```gherkin
Cenário: Saída do pré-lançamento
  Dado a versão 1.0.0-alpha.3 e prerelease falso
  Quando a estratégia recebe um commit feat
  Então a próxima versão é 1.0.0
```

#### Scenario: Saída do pré-lançamento
- **WHEN** a estratégia recebe `1.0.0-alpha.3` com `prerelease` falso e um commit `feat`
- **THEN** a próxima versão é `1.0.0`

### Requirement: Publicar continua ato humano
O fluxo de release SHALL abrir ou atualizar apenas o PR de release; nenhuma etapa automática SHALL mesclá-lo, e a publicação da tag e do GitHub Release SHALL ocorrer só quando uma pessoa mesclar esse PR.

```gherkin
Cenário: Workflow
  Dado o arquivo .github/workflows/release-please.yml
  Quando ele é lido
  Então ele só roda a ação do release-please em push na main
  E nenhum passo ativa mesclagem automática
```

#### Scenario: Workflow
- **WHEN** `.github/workflows/release-please.yml` é lido
- **THEN** ele só roda a ação do release-please em push na `main` e nenhum passo ativa mesclagem automática

### Requirement: Versão no manifesto e no pacote em sincronia
O PR de release SHALL atualizar o manifesto `.release-please-manifest.json` e a linha `version:` do `apm.yml` para a mesma versão, e a configuração SHALL listar o `apm.yml` em `extra-files`.

```gherkin
Cenário: Configuração de arquivos
  Dado a configuração do release-please
  Quando ela é lida
  Então extra-files contém apm.yml e o manifesto tem a chave "."
```

#### Scenario: Configuração de arquivos
- **WHEN** a configuração é lida
- **THEN** `extra-files` contém `apm.yml` e o manifesto tem a chave `.`

### Requirement: README explica o pré-lançamento
O `README.md` SHALL explicar como consumir um pré-lançamento, que a `v0.3.1` continua sendo a última versão estável até a final e como a `1.0.0` sai.

```gherkin
Cenário: Leitor do README
  Dado quem consome o pacote
  Quando lê a seção de releases do README
  Então encontra a tag do pré-lançamento, a última versão estável e o caminho para a versão final
```

#### Scenario: Leitor do README
- **WHEN** quem consome o pacote lê a seção de releases
- **THEN** encontra a tag do pré-lançamento, a indicação da última versão estável e o caminho para a versão final

### Requirement: A configuração propõe a versão final 1.0.0
Depois da prova aprovada, o release-please SHALL propor `1.0.0` a partir de `1.0.0-alpha.1` com `prerelease` falso, mantendo a estratégia `prerelease` ativa até a tag `v1.0.0` existir, e a configuração SHALL NOT conter `release-as`.

```gherkin
Cenário: Versão proposta
  Dado a versão 1.0.0-alpha.1 e prerelease falso
  Quando a estratégia recebe commits de qualquer tipo, inclusive incompatíveis
  Então a próxima versão é 1.0.0
```

#### Scenario: Configuração da versão final
- **WHEN** a configuração é lida enquanto o manifesto está em `1.0.0-alpha.1`
- **THEN** `prerelease` é falso, `versioning` continua `prerelease` e não existe `release-as`

#### Scenario: Versão proposta
- **WHEN** a estratégia recebe `1.0.0-alpha.1` com `prerelease` falso e commits de qualquer tipo, inclusive incompatíveis
- **THEN** a próxima versão é `1.0.0`

#### Scenario: Versões depois da final
- **WHEN** a estratégia recebe `1.0.0` com um commit `feat`, depois um `fix` e depois um incompatível
- **THEN** as versões propostas são `1.1.0`, `1.0.1` e `2.0.0`

### Requirement: Estratégia de pré-lançamento mantida até a tag final
Enquanto a versão do manifesto for um pré-lançamento, a configuração SHALL manter `"versioning": "prerelease"`, porque a estratégia padrão proporia `2.0.0-alpha.1` ou `1.1.0-alpha.1` em vez da `1.0.0`.

```gherkin
Cenário: Manifesto em pré-lançamento
  Dado um manifesto com sufixo de pré-lançamento
  Quando a configuração é lida
  Então versioning é prerelease
```

#### Scenario: Manifesto em pré-lançamento
- **WHEN** a versão do manifesto contém um sufixo de pré-lançamento
- **THEN** `versioning` é `prerelease`

### Requirement: A versão final é provocada por um commit liberável com Release-As
O release-please SHALL abrir o PR de release da versão final apenas depois de um commit liberável (`fix` ou `feat`) desde a última tag, e esse commit SHALL levar o rodapé `Release-As: 1.0.0` na mensagem do commit de squash.

```gherkin
Cenário: Commit liberável com Release-As
  Dado um commit fix com o rodapé Release-As: 1.0.0 na main
  Quando o release-please roda
  Então o bot abre o PR de release propondo 1.0.0
```

#### Scenario: Só commits escondidos
- **WHEN** os commits desde a tag são só `docs`, `chore` e `ci`
- **THEN** o workflow termina com sucesso, informa que não há commits visíveis e nenhum PR de release é aberto

#### Scenario: Commit liberável com Release-As
- **WHEN** a `main` recebe um commit `fix` cuja mensagem termina com `Release-As: 1.0.0`
- **THEN** o bot abre o PR de release propondo `1.0.0`
