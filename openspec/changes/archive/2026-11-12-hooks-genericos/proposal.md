# Proposal

## Why

Depois da F1, o pacote não tem mais nenhum hook de encerramento: o `cowboy.json` exigia `make fitness` e travava projetos sem Makefile, então saiu. Falta o substituto genérico, que leia o comando de sensores do próprio projeto. Além disso, os hooks de segurança que sobraram têm problemas que a F2 resolve: quebram com configuração ou payload mal formados (`json.load` sem guarda, `config` que não é objeto, entradas sem `pattern`), usam um teste de prefixo (`startswith`) que deixa passar uma pasta irmã de nome parecido, só respondem no formato do Copilot (o Claude Code lê o código de saída 2 ou o JSON de `hookSpecificOutput`, então o bloqueio provavelmente não vale nele) e ainda dependem de cópia manual de scripts, porque o README marca a entrega pelo APM como pendente. Um teste descartável mostrou que o APM entrega hooks e scripts sozinho: este é o momento de usar isso. É a funcionalidade F2 da Onda 1 da spec APM_SETUP V1.2.

## What Changes

- Novo hook de Stop, `stop-sensors`, que roda o comando de sensores definido em `harness.config.json` (campo novo `sensors_command`, vazio por padrão). Sem comando, sem arquivo de configuração ou sem Makefile, o encerramento é permitido; com comando que falha, bloqueia e mostra a saída.
- Hooks `SessionStart`, escrita e Bash passam a tolerar configuração ou payload ausente, corrompido ou de tipo errado, sem travar e sem traceback. Os bloqueios embutidos (credenciais, `git push`, `reset --hard`, `clean -f`, `branch -D`, `rm -rf`) continuam valendo sem configuração.
- Teste de "caminho dentro do repositório" corrigido para comparar caminhos de verdade, e não prefixos de texto.
- O bloqueio responde no formato de cada host: no Claude Code, código de saída 2 com o motivo em stderr; no Copilot, o JSON de decisão de hoje.
- Hooks e scripts passam a ser entregues pelo APM (`.apm/hooks/*.json` mais o bundle de scripts), registrados em `.claude/settings.json` e `.github/hooks/`. Sai a cópia manual de scripts e o registro à mão.
- Primeira bateria de testes do pacote (`tests/hooks/`, só `unittest`), que também vira o comando de sensores do próprio repositório.
- Pre-commit genérico, que roda o mesmo `sensors_command` (prometido na F1 no lugar do pre-commit do COBOL).
- Atualizações de skill e documentação: `install-dev-harness` deixa de copiar scripts de hook, o template de `guide_files` perde a entrada de pre-commit inexistente, e o README perde a nota pendente.

Ficam fora desta change: os agentes `sdlc-*` (F3), a configuração do release-please para pré-lançamento, os agentes de harness e o sensor anti-fantasma (Onda 2).

## Capabilities

### New Capabilities
- `sensor-gate`: o encerramento da sessão só é bloqueado quando o comando de sensores configurado pelo projeto falha; sem comando, nada bloqueia.
- `hook-runtime`: os hooks do pacote funcionam em qualquer stack sem travar com entrada inválida, decidem no formato de cada host e chegam ao projeto pelo APM.

### Modified Capabilities

Nenhuma. A única spec principal existente, `pacote-generico`, não muda de comportamento.

## Impact

- **Arquivos movidos**: `.apm/scripts/hooks/*.py` para `.apm/hooks/scripts/` (o APM só entrega bundle de hook que fique no diretório de hooks).
- **Arquivos novos**: `.apm/hooks/harness.json`, `.apm/hooks/scripts/stop-sensors.py` e um helper comum, `.apm/scripts/git-hooks/pre-commit`, `tests/hooks/*`.
- **Arquivos removidos**: `.apm/_pending/hooks/harness.json`, `scripts/hooks/*` e `.claude/settings.json` do próprio repositório (o APM os regera), e as cópias dos scripts em `install-dev-harness/templates/hooks/` e `settings.hooks.json`.
- **Arquivos alterados**: `harness.config.json` (e os dois modelos), `.apm/scripts/harness/phase_cli.py`, skill `install-dev-harness`, `CLAUDE.md` (quality gates passam de "não informado" a definidos), `README.md`, `CHANGELOG.md`.
- **Consumidores**: quem usa a 0.3.x continua com a tag antiga. Na nova versão, o projeto passa a receber os hooks pelo `apm install` e precisa aprovar os executáveis (`apm approve`).
- **Release**: a mensagem é `feat:` sem `!` (a quebra já está na F1). O PR de release `1.0.0` aberto pelo release-please continua sem ser mesclado até a change de pré-lançamento.
- **Risco**: o comportamento real no Claude Code e no Copilot só se confirma rodando cada host; o plano prevê um teste no Claude Code e deixa o Copilot declarado como não verificado.
