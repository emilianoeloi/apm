# Spec Delta

## Purpose

Faz o encerramento da sessão respeitar os sensores do próprio projeto: o comando vem da configuração, nunca de um Makefile ou de uma stack fixa, e na ausência dele nada bloqueia.

## ADDED Requirements

### Requirement: Encerramento sem sensores configurados é permitido
O hook de Stop SHALL permitir o encerramento, sem saída de erro, quando o `harness.config.json` não existe, não tem `sensors_command`, ou o campo está vazio ou não é texto.

#### Scenario: Projeto sem configuração nem Makefile
- **WHEN** a sessão encerra numa pasta sem `harness.config.json` e sem Makefile
- **THEN** o hook sai com código 0 e não escreve em stderr

#### Scenario: Comando vazio
- **WHEN** o `harness.config.json` traz `"sensors_command": ""`
- **THEN** o hook sai com código 0

### Requirement: Sensores configurados rodam na raiz do projeto
O hook de Stop SHALL executar o `sensors_command` com a raiz do projeto como diretório de trabalho e permitir o encerramento quando o comando sai com código 0.

#### Scenario: Sensor que passa
- **WHEN** `sensors_command` é um comando que sai com 0
- **THEN** o hook sai com código 0

#### Scenario: Diretório de trabalho
- **WHEN** `sensors_command` imprime o diretório atual
- **THEN** o diretório impresso é a raiz do projeto

### Requirement: Sensores com falha bloqueiam o encerramento
O hook de Stop SHALL bloquear o encerramento com código 2 quando o `sensors_command` falha ou excede o tempo limite, e SHALL mostrar em stderr o código de saída e o final da saída do comando.

#### Scenario: Sensor que falha
- **WHEN** `sensors_command` sai com código diferente de 0 e imprime uma mensagem
- **THEN** o hook sai com código 2 e a mensagem aparece em stderr

#### Scenario: Sensor que excede o tempo
- **WHEN** o comando passa de `sensors_timeout_seconds`
- **THEN** o hook sai com código 2 e stderr informa o estouro do tempo

### Requirement: Encerramento já forçado não entra em laço
O hook de Stop SHALL permitir o encerramento, sem rodar o comando, quando o payload traz `stop_hook_active` verdadeiro.

#### Scenario: Segunda tentativa de encerrar
- **WHEN** o payload tem `"stop_hook_active": true` e o `sensors_command` falharia
- **THEN** o hook sai com código 0 sem executar o comando

### Requirement: Campos de sensor documentados nos modelos
Os dois modelos de `harness.config.json` SHALL declarar `sensors_command` (vazio por padrão) e `sensors_timeout_seconds` (50 por padrão), com a descrição do comportamento.

#### Scenario: Modelo novo
- **WHEN** um projeto cria o `harness.config.json` a partir do modelo
- **THEN** o campo `sensors_command` existe e vale texto vazio
