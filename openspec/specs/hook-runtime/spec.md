# hook-runtime Specification

## Purpose
Garante que os hooks do pacote funcionem em qualquer stack e em qualquer host: não travam com entrada inválida, decidem no formato que cada host entende e chegam ao projeto pelo APM, sem cópia manual.

## Requirements

### Requirement: Configuração e payload inválidos nunca travam os hooks
Cada hook do pacote SHALL permitir a ação, sem traceback, quando o `harness.config.json` está ausente, corrompido, não é um objeto ou tem entradas de tipo errado, e quando o payload recebido não é um JSON válido.

#### Scenario: Configuração corrompida
- **WHEN** o `harness.config.json` contém texto que não é JSON e qualquer hook roda com um comando inofensivo
- **THEN** o hook sai com código 0 e não escreve traceback

#### Scenario: Configuração que não é objeto
- **WHEN** o `harness.config.json` contém uma lista JSON
- **THEN** o hook trata como configuração vazia e permite

#### Scenario: Payload inválido
- **WHEN** o hook recebe texto que não é JSON na entrada padrão
- **THEN** o hook sai com código 0 e não escreve traceback

### Requirement: Bloqueios de segurança embutidos valem sem configuração
Os hooks de escrita e de Bash SHALL bloquear, mesmo sem `harness.config.json`, a escrita em arquivos de credencial conhecidos e os comandos `git push`, `git reset --hard`, `git clean -f`, `git branch -D` e `rm -rf`.

#### Scenario: Push sem configuração
- **WHEN** o hook de Bash recebe `git push origin main` e não há `harness.config.json`
- **THEN** a ação é bloqueada

#### Scenario: Credencial sem configuração
- **WHEN** o hook de escrita recebe um caminho terminado em `.env` e não há `harness.config.json`
- **THEN** a ação é bloqueada

#### Scenario: Menção em texto não bloqueia
- **WHEN** o hook de Bash recebe um comando que só cita `git push` em texto, como numa mensagem de commit ou num `echo`
- **THEN** a ação é permitida

#### Scenario: Comando em qualquer posição de comando
- **WHEN** o hook de Bash recebe `git push` depois de `&&`, `;`, `|`, `$(` ou numa nova linha
- **THEN** a ação é bloqueada

#### Scenario: Listagem de branches
- **WHEN** o hook de Bash recebe `git branch -a` ou `git branch -vv`
- **THEN** a ação é permitida, e só `git branch -D` é bloqueado

### Requirement: Escrita fora da raiz só por opt-in
O hook de escrita SHALL permitir a escrita fora da raiz do projeto apenas em diretórios absolutos listados em `allowed_write_roots` (vazio por padrão), nunca para arquivos de credencial, e SHALL ignorar entradas relativas ou de tipo errado.

#### Scenario: Raiz extra listada
- **WHEN** `allowed_write_roots` contém `/tmp/liberada` e o caminho está dentro dela
- **THEN** a escrita é permitida, e um caminho em outra pasta fora da raiz continua bloqueado

#### Scenario: Credencial na raiz extra
- **WHEN** o caminho é `.env` dentro de uma raiz extra permitida
- **THEN** a escrita é bloqueada

### Requirement: Contenção de caminho exata
O hook de escrita SHALL tratar como fora do repositório qualquer caminho que não esteja dentro da raiz como diretório, inclusive uma pasta irmã cujo nome começa com o nome da raiz.

#### Scenario: Pasta irmã de nome parecido
- **WHEN** a raiz é `/tmp/proj` e o caminho é `/tmp/proj-outro/arquivo.txt`
- **THEN** a escrita é bloqueada como fora da raiz

### Requirement: Decisão no formato de cada host
Os hooks de escrita e de Bash SHALL bloquear no Claude Code com código de saída 2 e o motivo em stderr, e no Copilot com o JSON de decisão `deny` na saída padrão e código 0; o host é identificado pelo formato do payload.

#### Scenario: Bloqueio no Claude Code
- **WHEN** o payload tem `tool_name` e `tool_input` e o comando é bloqueado
- **THEN** o hook sai com código 2 e o motivo aparece em stderr

#### Scenario: Bloqueio no Copilot
- **WHEN** o payload tem `toolName` e `toolArgs` e o comando é bloqueado
- **THEN** o hook sai com código 0 e imprime JSON com `permissionDecision` igual a `deny`

### Requirement: Entrega dos hooks pelo APM
O pacote SHALL declarar os hooks em `.apm/hooks/` com os scripts no mesmo diretório, de modo que `apm install --target claude,copilot` registre `SessionStart`, `PreToolUse` e `Stop` em `.claude/settings.json` e `.github/hooks/` e implante os scripts, sem cópia manual.

#### Scenario: Instalação num projeto vazio
- **WHEN** `apm install --target claude,copilot` roda num projeto que depende do pacote
- **THEN** os três eventos aparecem em `.claude/settings.json` e os scripts referenciados existem nos caminhos registrados

#### Scenario: Script entregue funciona
- **WHEN** o script implantado do hook de Stop roda com um payload válido num projeto sem configuração
- **THEN** ele sai com código 0

### Requirement: Hooks só com biblioteca padrão e sem stack
Os scripts de hook SHALL usar somente a biblioteca padrão do Python e SHALL NOT citar linguagem, pasta ou comando de um projeto específico.

#### Scenario: Importações e termos
- **WHEN** os scripts de `.apm/hooks/` são inspecionados
- **THEN** todas as importações são da biblioteca padrão ou do helper do próprio diretório, e a busca por "cowboy", "cobol", "cobc" e "calculadora" não encontra nada
