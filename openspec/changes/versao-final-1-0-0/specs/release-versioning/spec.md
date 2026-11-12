# Spec Delta

## ADDED Requirements

### Requirement: A configuração propõe a versão final 1.0.0
Depois da prova aprovada, o release-please SHALL propor `1.0.0` a partir de `1.0.0-alpha.1` com `prerelease` falso, mantendo a estratégia `prerelease` ativa até a tag `v1.0.0` existir, e a configuração SHALL NOT conter `release-as`.

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

#### Scenario: Manifesto em pré-lançamento
- **WHEN** a versão do manifesto contém um sufixo de pré-lançamento
- **THEN** `versioning` é `prerelease`

### Requirement: A versão final é provocada por um commit liberável com Release-As
O release-please SHALL abrir o PR de release da versão final apenas depois de um commit liberável (`fix` ou `feat`) desde a última tag, e esse commit SHALL levar o rodapé `Release-As: 1.0.0` na mensagem do commit de squash.

#### Scenario: Só commits escondidos
- **WHEN** os commits desde a tag são só `docs`, `chore` e `ci`
- **THEN** o workflow termina com sucesso, informa que não há commits visíveis e nenhum PR de release é aberto

#### Scenario: Commit liberável com Release-As
- **WHEN** a `main` recebe um commit `fix` cuja mensagem termina com `Release-As: 1.0.0`
- **THEN** o bot abre o PR de release propondo `1.0.0`

## REMOVED Requirements

### Requirement: Primeira publicação do 1.0.0 é um pré-lançamento
**Reason**: cumprido: a tag `v1.0.0-alpha.1` foi publicada com o GitHub Release marcado como pré-lançamento. A configuração deixa de ser de pré-lançamento.
**Migration**: a versão final é coberta pelo requisito "A configuração propõe a versão final 1.0.0".

### Requirement: Pré-lançamentos seguintes incrementam o número
**Reason**: o período de pré-lançamento terminou com a prova aprovada; não haverá `1.0.0-alpha.2`. Com `prerelease` falso a numeração dos alphas não se aplica.
**Migration**: a versão final é coberta pelo requisito "A configuração propõe a versão final 1.0.0".
