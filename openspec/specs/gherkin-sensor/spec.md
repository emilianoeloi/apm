# gherkin-sensor Specification

## Purpose
Fixa o sensor de Gherkin: um script só de biblioteca padrão que confere o bloco `gherkin` de cada requisito das specs do OpenSpec, aplicando os deltas das changes ativas, e falha com código 2 citando o requisito, tanto no Stop e no pre-commit quanto logo depois de um `openspec validate`.

## Requirements

### Requirement: Requisito sem cenário reprova e é citado
O sensor de Gherkin SHALL sair com código 2 quando algum requisito efetivo não tem bloco Gherkin conforme ao formato de `spec-gherkin-scenarios`, e SHALL citar em stderr cada requisito com falha pela capability, pelo nome do requisito e pelo motivo.

```gherkin
Cenário: Requisito sem bloco
  Dado um projeto com um requisito sem bloco gherkin
  Quando o sensor de Gherkin roda
  Então ele sai com código 2
  E stderr cita a capability e o nome do requisito
```

#### Scenario: Requisito sem bloco
- **WHEN** o sensor roda num projeto cuja spec tem um requisito sem bloco `gherkin`
- **THEN** ele sai com código 2 e stderr traz a capability, o nome do requisito e o motivo

#### Scenario: Todas as violações de uma vez
- **WHEN** dois requisitos violam o formato por motivos diferentes (sem `Então`, título sem correspondência)
- **THEN** stderr lista os dois, cada um com seu motivo, e o sensor sai com código 2

### Requirement: Requisitos conformes passam
O sensor SHALL sair com código 0 e não escrever em stderr quando todo requisito efetivo tem o bloco Gherkin conforme.

```gherkin
Cenário: Todos os requisitos com cenário
  Dado um projeto em que todo requisito tem o bloco gherkin conforme
  Quando o sensor de Gherkin roda
  Então ele sai com código 0
```

#### Scenario: Todos os requisitos com cenário
- **WHEN** o sensor roda num projeto em que todo requisito tem o bloco conforme
- **THEN** ele sai com código 0 e stderr fica vazio

### Requirement: Requisitos efetivos incluem os deltas ativos
O sensor SHALL verificar os requisitos efetivos: as specs principais com os requisitos trocados pelos `ADDED` e `MODIFIED` dos deltas de changes ativas, sem os `REMOVED`, com os `RENAMED` aplicados, e SHALL ignorar tudo em `changes/archive/`; um requisito de delta com falha SHALL ser citado com o nome da change.

```gherkin
Cenário: Delta ativo sem bloco
  Dado uma spec principal conforme e um delta ativo com um requisito ADDED sem bloco
  Quando o sensor de Gherkin roda
  Então ele sai com código 2
  E stderr cita a capability, o requisito e o nome da change
```

#### Scenario: Delta ativo sem bloco
- **WHEN** um delta ativo traz um requisito `ADDED` sem bloco
- **THEN** o sensor sai com código 2 e cita a capability, o requisito e a change

#### Scenario: Requisito removido não conta
- **WHEN** uma spec principal tem um requisito sem bloco e um delta ativo o remove com `REMOVED`
- **THEN** o sensor sai com código 0

#### Scenario: Arquivo arquivado é ignorado
- **WHEN** um delta em `changes/archive/` tem um requisito sem bloco
- **THEN** o sensor não o cita

### Requirement: Localização do diretório openspec
O sensor SHALL procurar `openspec/` na raiz do projeto, resolvida por `--root`, depois por `CLAUDE_PROJECT_DIR`, depois pela pasta com `.git` acima do diretório atual, e SHALL sair com código 0 avisando em stderr que não há o que verificar quando a raiz não tem `openspec/`.

```gherkin
Cenário: Projeto sem openspec
  Dado um projeto sem o diretório openspec
  Quando o sensor de Gherkin roda
  Então ele sai com código 0
  E avisa que não há specs para verificar
```

#### Scenario: Projeto sem openspec
- **WHEN** o sensor roda numa raiz sem `openspec/`
- **THEN** ele sai com código 0 e stderr avisa que não há specs para verificar

#### Scenario: Raiz por parâmetro
- **WHEN** o sensor roda com `--root` apontando para outro projeto
- **THEN** ele verifica o `openspec/` desse projeto, independente do diretório atual

### Requirement: Contrato de saída e robustez
O sensor SHALL usar só a biblioteca padrão e o helper `_common.py`/`_gherkin.py` do próprio diretório, SHALL sair somente com código 0 ou 2, e SHALL tratar arquivo ilegível ou spec malformada como requisito com falha citado, sem traceback.

```gherkin
Cenário: Spec ilegível
  Dado uma spec que não pode ser lida como texto
  Quando o sensor de Gherkin roda
  Então ele sai com código 2 sem traceback
  E cita o arquivo ilegível
```

#### Scenario: Spec ilegível
- **WHEN** uma `spec.md` tem bytes que não decodificam como UTF-8
- **THEN** o sensor sai com código 2, cita o arquivo e não escreve traceback

#### Scenario: Importações e termos
- **WHEN** `gherkin-sensor.py` e `_gherkin.py` são inspecionados
- **THEN** só importam a biblioteca padrão ou o helper do diretório, e a busca por "cowboy", "cobol", "cobc" e "calculadora" não encontra nada

### Requirement: Sensor roda junto do openspec validate
O pacote SHALL registrar em `.apm/hooks/harness.json` um hook `PostToolUse` com matcher `Bash` que executa o sensor quando o comando do payload contém `openspec validate`, SHALL propagar o código 2 e o stderr do sensor, e SHALL sair com código 0 sem saída para qualquer outro comando.

```gherkin
Cenário: Validate dispara o sensor
  Dado um projeto com um requisito sem bloco gherkin
  Quando o hook PostToolUse recebe o comando "openspec validate --strict"
  Então ele sai com código 2
  E stderr cita o requisito
```

#### Scenario: Validate dispara o sensor
- **WHEN** o hook recebe um payload `Bash` com `openspec validate minha-change --strict` num projeto com requisito sem bloco
- **THEN** o hook sai com código 2 e stderr cita o requisito

#### Scenario: Outro comando não dispara
- **WHEN** o hook recebe um payload `Bash` com `git status`
- **THEN** o hook sai com código 0 sem escrever nada

#### Scenario: Payload inválido não trava
- **WHEN** o hook recebe texto que não é JSON ou uma configuração corrompida
- **THEN** o hook sai com código 0 e não escreve traceback

### Requirement: Uma única implementação da regra de formato
A leitura dos requisitos efetivos e a validação do bloco SHALL viver em `_gherkin.py`, e o teste `tests/specs/test_gherkin_blocks.py` SHALL importá-las dali, sem manter cópia da lógica.

```gherkin
Cenário: Teste da F1 usa a biblioteca
  Dado o teste tests/specs/test_gherkin_blocks.py
  Quando suas importações são inspecionadas
  Então ele importa a leitura e a validação de _gherkin
  E não define essas funções
```

#### Scenario: Teste da F1 usa a biblioteca
- **WHEN** `tests/specs/test_gherkin_blocks.py` é inspecionado
- **THEN** ele importa de `_gherkin` e não define `validate` nem `effective_requirements`

### Requirement: Sensor no sensors_command deste repositório
O `harness.config.json` deste repositório SHALL incluir a execução do sensor de Gherkin no `sensors_command`, de modo que o hook de Stop bloqueie o encerramento quando falta Gherkin, e os modelos de configuração entregues SHALL manter `sensors_command` vazio.

```gherkin
Cenário: Stop bloqueia por falta de cenário
  Dado o sensors_command deste repositório com o sensor de Gherkin
  Quando a sessão encerra com um requisito sem bloco
  Então o hook de Stop sai com código 2
```

#### Scenario: Stop bloqueia por falta de cenário
- **WHEN** o `sensors_command` do repositório roda com um requisito sem bloco
- **THEN** ele sai com código diferente de 0 e o Stop bloqueia

#### Scenario: Modelos continuam vazios
- **WHEN** os modelos `harness.config.json` do pacote são lidos
- **THEN** `sensors_command` é vazio em ambos
