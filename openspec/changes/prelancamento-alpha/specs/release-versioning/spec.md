# Spec Delta

## Purpose

Garante que o pacote seja publicado pelo release-please de modo que o MVP saia como pré-lançamento, os pré-lançamentos seguintes numerem sozinhos e a versão final dependa só de uma mudança de configuração e de um ato humano.

## ADDED Requirements

### Requirement: Primeira publicação do 1.0.0 é um pré-lançamento
O release-please SHALL calcular `1.0.0-alpha.1` como próxima versão a partir de `0.3.1` quando houver commits incompatíveis, publicar a tag `v1.0.0-alpha.1` sem nome de componente e marcar o GitHub Release como pré-lançamento.

#### Scenario: Versão calculada
- **WHEN** a estratégia de versionamento recebe a versão `0.3.1` e commits que incluem uma mudança incompatível
- **THEN** a próxima versão é `1.0.0-alpha.1`

#### Scenario: Tag e tipo de release
- **WHEN** a configuração é lida
- **THEN** `include-v-in-tag` é verdadeiro, `include-component-in-tag` é falso e `prerelease` é verdadeiro

### Requirement: Pré-lançamentos seguintes incrementam o número
Estando na versão `1.0.0-alpha.N`, o release-please SHALL propor `1.0.0-alpha.N+1` para qualquer tipo de commit (incompatível, `feat` ou `fix`), sem depender de uma versão fixa na configuração.

#### Scenario: Sequência de pré-lançamentos
- **WHEN** a estratégia recebe `1.0.0-alpha.1` com um commit `feat`, depois `1.0.0-alpha.2` com um `fix`
- **THEN** as versões propostas são `1.0.0-alpha.2` e `1.0.0-alpha.3`

#### Scenario: Sem versão fixa pendente
- **WHEN** a configuração é lida
- **THEN** não existe a chave `release-as`

### Requirement: Versão final por mudança de configuração
Com `prerelease` falso, o release-please SHALL propor a versão final `1.0.0` a partir de qualquer `1.0.0-alpha.N`, sem outra alteração de configuração.

#### Scenario: Saída do pré-lançamento
- **WHEN** a estratégia recebe `1.0.0-alpha.3` com `prerelease` falso e um commit `feat`
- **THEN** a próxima versão é `1.0.0`

### Requirement: Publicar continua ato humano
O fluxo de release SHALL abrir ou atualizar apenas o PR de release; nenhuma etapa automática SHALL mesclá-lo, e a publicação da tag e do GitHub Release SHALL ocorrer só quando uma pessoa mesclar esse PR.

#### Scenario: Workflow
- **WHEN** `.github/workflows/release-please.yml` é lido
- **THEN** ele só roda a ação do release-please em push na `main` e nenhum passo ativa mesclagem automática

### Requirement: Versão no manifesto e no pacote em sincronia
O PR de release SHALL atualizar o manifesto `.release-please-manifest.json` e a linha `version:` do `apm.yml` para a mesma versão, e a configuração SHALL listar o `apm.yml` em `extra-files`.

#### Scenario: Configuração de arquivos
- **WHEN** a configuração é lida
- **THEN** `extra-files` contém `apm.yml` e o manifesto tem a chave `.`

### Requirement: README explica o pré-lançamento
O `README.md` SHALL explicar como consumir um pré-lançamento, que a `v0.3.1` continua sendo a última versão estável até a final e como a `1.0.0` sai.

#### Scenario: Leitor do README
- **WHEN** quem consome o pacote lê a seção de releases
- **THEN** encontra a tag do pré-lançamento, a indicação da última versão estável e o caminho para a versão final
