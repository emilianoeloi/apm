# pacote-generico Specification

## Purpose
Garante que o pacote APM entregue aos projetos consumidores seja genérico: sem o projeto de origem (cowboy), sem COBOL e sem metadados que prendam o pacote a uma stack.

## Requirements

### Requirement: Fonte do pacote sem referências ao cowboy
A fonte do pacote em `.apm/` SHALL NOT conter os termos "cowboy", "cobol", "cobc" ou "calculadora", sem diferenciar maiúsculas de minúsculas, nem em nomes de arquivo nem em conteúdo.

```gherkin
Cenário: Busca vazia na fonte
  Dado a fonte do pacote em .apm/
  Quando a busca pelos quatro termos proibidos roda em nomes e em conteúdo
  Então a busca não retorna nenhum resultado
```

#### Scenario: Busca vazia na fonte
- **WHEN** a busca por "cowboy", "cobol", "cobc" e "calculadora" roda em `.apm/`, em nomes e em conteúdo
- **THEN** a busca não retorna nenhum resultado

### Requirement: Conteúdo exclusivo do cowboy removido
O pacote SHALL NOT incluir os agentes `cobol-*` e `readme-writer`, os sete prompts do cowboy, as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`, nenhum hook que execute `make fitness` e nenhum script que compile COBOL.

```gherkin
Cenário: Agentes e prompts
  Dado as pastas .apm/agents e .apm/prompts
  Quando elas são listadas
  Então não há arquivo cobol-* nem readme-writer
  E os prompts restantes são apenas os opsx-*
```

#### Scenario: Agentes e prompts
- **WHEN** `.apm/agents` e `.apm/prompts` são listados
- **THEN** não há arquivo `cobol-*` nem `readme-writer`, e os prompts restantes são apenas os `opsx-*`

#### Scenario: Hooks e scripts
- **WHEN** `.apm/hooks` e `.apm/scripts` são listados
- **THEN** não existe `cowboy.json` nem `pre-commit` que invoque `cobc`

### Requirement: Metadados e README neutros
O `apm.yml` e o `README.md` SHALL descrever o pacote como público e genérico, sem citar o cowboy como origem, exceto o aviso de migração do README.

```gherkin
Cenário: Nome e descrição
  Dado o apm.yml do pacote
  Quando nome e descrição são lidos
  Então eles não citam o cowboy
```

#### Scenario: Nome e descrição
- **WHEN** nome e descrição são lidos no `apm.yml`
- **THEN** eles não citam o cowboy

#### Scenario: Visibilidade
- **WHEN** a introdução do `README.md` é lida
- **THEN** ela não chama o pacote de privado nem de extraído de outro projeto

### Requirement: Modelo de quadrante sem dados de projeto
O arquivo `.apm/templates/HARNESS_QUADRANTE.md` SHALL ser um modelo com campos a preencher, sem notas, evidências ou arquivos de nenhum projeto real.

```gherkin
Cenário: Abrir o modelo
  Dado o arquivo .apm/templates/HARNESS_QUADRANTE.md
  Quando ele é aberto
  Então ele traz campos para preencher e nenhuma pontuação nem caminho de projeto específico
```

#### Scenario: Abrir o modelo
- **WHEN** o arquivo é aberto
- **THEN** ele traz campos marcados para preencher e nenhuma pontuação nem caminho de um projeto específico

### Requirement: Aviso de migração para a 0.3.x
O `README.md` SHALL trazer um aviso de migração para quem usava a versão 0.3.x, listando o que foi removido e como obter o conteúdo antigo.

```gherkin
Cenário: Leitor da 0.3.x
  Dado alguém que usava a 0.3.x
  Quando lê o README.md
  Então encontra a lista do que foi removido e a tag v0.3.1
```

#### Scenario: Leitor da 0.3.x
- **WHEN** quem usava a 0.3.x lê o `README.md`
- **THEN** encontra a lista do que foi removido e a indicação da tag `v0.3.1`, que guarda o estado antigo

### Requirement: Implantação reflete a fonte
Depois de `apm install --target claude,copilot`, os diretórios implantados e o `apm.lock.yaml` SHALL NOT conter o conteúdo removido da fonte.

```gherkin
Cenário: Diretórios implantados
  Dado o pacote instalado com "apm install --target claude,copilot"
  Quando a busca pelos quatro termos roda nos diretórios implantados
  Então a busca não retorna nenhum resultado
```

#### Scenario: Diretórios implantados
- **WHEN** a busca pelos quatro termos roda em `.claude/`, `.agents/`, `.github/agents` e `.github/prompts`
- **THEN** a busca não retorna nenhum resultado

#### Scenario: Lockfile
- **WHEN** o `apm.lock.yaml` é lido
- **THEN** ele não lista nenhum arquivo implantado do cowboy

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
