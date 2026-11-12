# Spec Delta

## Purpose

Garante que o pacote APM entregue aos projetos consumidores seja genérico: sem o projeto de origem (cowboy), sem COBOL e sem metadados que prendam o pacote a uma stack.

## ADDED Requirements

### Requirement: Fonte do pacote sem referências ao cowboy
A fonte do pacote em `.apm/` SHALL NOT conter os termos "cowboy", "cobol", "cobc" ou "calculadora", sem diferenciar maiúsculas de minúsculas, nem em nomes de arquivo nem em conteúdo.

#### Scenario: Busca vazia na fonte
- **WHEN** a busca por "cowboy", "cobol", "cobc" e "calculadora" roda em `.apm/`, em nomes e em conteúdo
- **THEN** a busca não retorna nenhum resultado

### Requirement: Conteúdo exclusivo do cowboy removido
O pacote SHALL NOT incluir os agentes `cobol-*` e `readme-writer`, os sete prompts do cowboy, as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`, nenhum hook que execute `make fitness` e nenhum script que compile COBOL.

#### Scenario: Agentes e prompts
- **WHEN** `.apm/agents` e `.apm/prompts` são listados
- **THEN** não há arquivo `cobol-*` nem `readme-writer`, e os prompts restantes são apenas os `opsx-*`

#### Scenario: Hooks e scripts
- **WHEN** `.apm/hooks` e `.apm/scripts` são listados
- **THEN** não existe `cowboy.json` nem `pre-commit` que invoque `cobc`

### Requirement: Metadados e README neutros
O `apm.yml` e o `README.md` SHALL descrever o pacote como público e genérico, sem citar o cowboy como origem, exceto o aviso de migração do README.

#### Scenario: Nome e descrição
- **WHEN** nome e descrição são lidos no `apm.yml`
- **THEN** eles não citam o cowboy

#### Scenario: Visibilidade
- **WHEN** a introdução do `README.md` é lida
- **THEN** ela não chama o pacote de privado nem de extraído de outro projeto

### Requirement: Modelo de quadrante sem dados de projeto
O arquivo `.apm/templates/HARNESS_QUADRANTE.md` SHALL ser um modelo com campos a preencher, sem notas, evidências ou arquivos de nenhum projeto real.

#### Scenario: Abrir o modelo
- **WHEN** o arquivo é aberto
- **THEN** ele traz campos marcados para preencher e nenhuma pontuação nem caminho de um projeto específico

### Requirement: Aviso de migração para a 0.3.x
O `README.md` SHALL trazer um aviso de migração para quem usava a versão 0.3.x, listando o que foi removido e como obter o conteúdo antigo.

#### Scenario: Leitor da 0.3.x
- **WHEN** quem usava a 0.3.x lê o `README.md`
- **THEN** encontra a lista do que foi removido e a indicação da tag `v0.3.1`, que guarda o estado antigo

### Requirement: Implantação reflete a fonte
Depois de `apm install --target claude,copilot`, os diretórios implantados e o `apm.lock.yaml` SHALL NOT conter o conteúdo removido da fonte.

#### Scenario: Diretórios implantados
- **WHEN** a busca pelos quatro termos roda em `.claude/`, `.agents/`, `.github/agents` e `.github/prompts`
- **THEN** a busca não retorna nenhum resultado

#### Scenario: Lockfile
- **WHEN** o `apm.lock.yaml` é lido
- **THEN** ele não lista nenhum arquivo implantado do cowboy
