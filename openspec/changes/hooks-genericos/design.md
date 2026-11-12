# Design

## Context

Hoje o pacote tem três hooks em `.apm/scripts/hooks/` (`session-start.py`, `pre-tool-write-guard.py`, `pre-tool-bash-guard.py`), o `phase_cli.py` em `.apm/scripts/harness/` e um registro de hooks parado em `.apm/_pending/hooks/harness.json`. O `install-dev-harness` copia os scripts para `scripts/hooks/` do projeto e mescla `settings.hooks.json` em `.claude/settings.json`. O repositório aplicou esse caminho manual na Onda 0.

Levantamento do código (leitura dos quatro scripts):
- `_project_root`, `_load_config` e a leitura do payload se repetem em cada script.
- `json.load(sys.stdin)` não tem guarda; `config.get(...)` assume que o JSON é um objeto; `entry["pattern"]` e `re.search` quebram com entrada malformada.
- O teste de contenção usa `str(resolved).startswith(str(repo_root))`, que aceita `/tmp/proj-outro` para a raiz `/tmp/proj`; o `phase_cli.py` tem o mesmo teste.
- A decisão sai sempre como `{"permissionDecision": ...}` em stdout com código 0, que é o formato do Copilot. O Claude Code bloqueia por código 2 ou por `hookSpecificOutput`; o hook antigo do cowboy usava código 2.
- O `phase_cli.py show` quebra se o arquivo de estado está corrompido.

Teste descartável do APM 0.35.0 (repositório temporário, fonte local): um `.apm/hooks/*.json` com `${PLUGIN_ROOT}/.apm/hooks/scripts/x.py` foi registrado em `.claude/settings.json` como `${CLAUDE_PROJECT_DIR}/.claude/hooks/<pacote>/.apm/hooks/scripts/x.py` e em `.github/hooks/<pacote>-<nome>.json` como `.github/hooks/scripts/<pacote>/.apm/hooks/scripts/x.py`, e os scripts foram copiados para esses caminhos. O formato achatado (sem grupo aninhado) saiu certo para os dois hosts: aninhado para o Claude, achatado para o Copilot. A doc do APM diz que arquivos vizinhos do script (helpers) também são implantados. Isso resolve o risco 1 da spec.

## Goals / Non-Goals

**Goals:**
- Um hook de Stop que lê o comando de sensores do projeto e nunca trava sem ele.
- Hooks que não quebram com entrada inválida e que bloqueiam de verdade em cada host.
- Entrega pelo APM, sem cópia manual, e uma bateria de testes que vira o sensor do próprio repositório.

**Non-Goals:**
- Provar o comportamento no Copilot (não há Copilot aqui); fica declarado como não verificado.
- Os agentes `sdlc-*`, o pré-lançamento e o sensor anti-fantasma.
- Reescrever o `phase_cli.py`: só correções pontuais (prefixo e arquivo de estado corrompido).

## Decisions

1. **Scripts em `.apm/hooks/scripts/`, registro em `.apm/hooks/harness.json`.** É o único lugar que o APM entrega como bundle de hook. Alternativa descartada: manter `.apm/scripts/hooks/` e copiar pelo skill, que repete o problema de cópia e de deriva.
2. **Formato achatado no JSON de origem**, com `${PLUGIN_ROOT}` nos caminhos, para o APM renderizar o formato nativo de cada host (confirmado no teste). Eventos: `SessionStart`, `PreToolUse` (matchers `Write|Edit|NotebookEdit` e `Bash`) e `Stop`.
3. **Um helper comum, `_common.py`, no mesmo diretório.** Reúne raiz do projeto, leitura tolerante da configuração (devolve `{}` se não for objeto), leitura tolerante do payload, contenção de caminho e emissão da decisão por host. Acaba com a cópia repetida e concentra o fail-open num lugar. Alternativa descartada: cada script autocontido, que repete as correções quatro vezes. Risco: o helper não chegar ao projeto; a doc do APM e uma task de teste no consumidor cobrem isso.
4. **Fail-open só para o que depende de configuração ou de entrada.** Os bloqueios embutidos (credenciais, `git push`, `reset --hard`, `clean -f`, `branch -D`, `rm -rf`) valem mesmo sem configuração, como já documenta o script. A spec do H2 diz "permite e não trava" para configuração ausente ou corrompida; interpreto como: o erro de configuração nunca bloqueia nem derruba o hook, e as defesas embutidas seguem ativas. É decisão a confirmar na aprovação.
5. **Decisão por host pelo formato do payload.** `tool_name`/`tool_input` (Claude): código 2 e motivo em stderr. `toolName`/`toolArgs` (Copilot): JSON `permissionDecision` em stdout e código 0, como hoje. Payload irreconhecível: permite. Alternativa descartada: emitir os dois formatos juntos, porque o código 2 do Claude ignora o JSON e o Copilot pode tratar código diferente de 0 como falha do hook.
6. **Stop: `sensors_command` e `sensors_timeout_seconds` na configuração.** Roda com `shell=True`, na raiz do projeto, com o limite de tempo (50 s por padrão, abaixo do `timeout` de 60 s do registro). Falha, código diferente de 0 ou estouro de tempo bloqueiam com código 2 e o final da saída (3000 caracteres); `stop_hook_active` verdadeiro libera, para não entrar em laço. Falha ao iniciar o processo (erro do sistema) libera com aviso. A confiança é a mesma de qualquer hook: o comando vem do arquivo do próprio projeto e o consumidor aprova os executáveis com `apm approve`.
7. **Pre-commit genérico em `.apm/scripts/git-hooks/pre-commit`.** Script `sh` curto que lê o mesmo `sensors_command` com `python3` e o executa; sem comando, passa. Não é entregue pelo APM (só hooks são); o `install-dev-harness` o copia e explica `git config core.hooksPath`. Cumpre a promessa da F1.
8. **Dogfood.** O `harness.config.json` deste repositório recebe `sensors_command` apontando para `python3 -m unittest discover -s tests -t . -v`, e o `CLAUDE.md` troca "não informado" por esse quality gate. O repositório passa a testar o que entrega.
9. **O `.claude/settings.json` e o `scripts/hooks/` do próprio repositório saem**, porque o `apm install` regera o registro e os scripts. Evita registro duplicado dos mesmos hooks.

10. **Padrões de comando ancorados na posição de comando** (descoberto no apply). Com o hook ativo de verdade, o guarda bloqueou um comando que só citava `git push` num texto. O padrão passou a exigir início de texto ou `;`, `&`, `|`, quebra de linha ou `$(` antes do comando, com `(` e `sudo` opcionais. Crase ficou de fora dos separadores porque aparece em todo Markdown (mensagens de commit, corpo de PR). Limite aceito e documentado: `env X=1 git push`, `git -C dir push` e substituição por crases não são detectados; o harness é rede de segurança, não sandbox. Alternativa descartada: manter `\bgit\s+push\b`, que bloqueia qualquer menção.
11. **Padrão de branch só com `D` maiúsculo** (descoberto no apply). Com a busca sem diferenciar caixa, `-[A-Z]` casava `git branch -a` e `-vv`. O padrão usa `(?-i:D)` e os dois modelos, a configuração do repositório e o guarda ficam iguais, com um teste de deriva.
12. **`allowed_write_roots`, opt-in** (descoberto no apply). Ao bloquear de verdade no Claude Code, o guarda de escrita barrou a pasta temporária da própria sessão, que fica fora do projeto. Em vez de afrouxar o padrão, o campo lista diretórios absolutos permitidos (vazio por padrão, nunca libera credencial). O repositório lista `/tmp` e `/private/tmp`.
13. **Estouro de tempo mata o grupo de processos.** `subprocess.run(..., timeout=)` mata só o shell e deixa o sensor filho órfão; o hook usa `Popen` com `start_new_session` e `killpg`, com teste de processo órfão.

## Risks / Trade-offs

- [O Claude Code pode não honrar o formato esperado, ou o hook registrado pode não disparar] → **verificado no apply**: o guarda de Bash e o de escrita, entregues pelo APM, bloquearam comandos reais na sessão do Claude Code (código 2 e motivo em stderr). O Copilot continua não verificado.
- [O formato do Copilot (`.github/hooks/*.json`) e a decisão `deny` dele não podem ser provados aqui] → declarado como não verificado no README e no CHANGELOG; os testes cobrem só o formato da saída.
- [O helper pode não ser implantado, o que derrubaria os hooks] → teste que instala o pacote num projeto temporário e roda os scripts implantados; uma falha de importação sai com código 1, que o Claude Code trata como erro sem bloqueio.
- [`shell=True` executa texto do arquivo de configuração] → o arquivo é do próprio projeto, versionado e revisável; o consumidor aprova os executáveis; documentado no README.
- [Registro duplicado se sobrar o `.claude/settings.json` manual] → a task de entrega remove o arquivo manual antes do `apm install` e confere que cada evento aparece uma vez.
- [Ao mudar o caminho dos scripts, projetos da 0.3.x que copiaram os antigos ficam com cópia sem dono] → o aviso de migração do README cobre a troca; só vale para quem trocar de tag.

## Migration Plan

1. Mover e criar os scripts, o registro e os modelos; escrever os testes junto de cada script.
2. Remover o registro manual do próprio repositório e reimplantar com `apm install --target claude,copilot`.
3. Provar a entrega num projeto temporário (instalação e execução dos scripts implantados) e o bloqueio no Claude Code.
4. Atualizar skill, README, `CLAUDE.md` e CHANGELOG; abrir o PR `feat:`; mesclar e o PR de release seguem como atos do Elói.
5. Rollback: reverter o PR ou manter a dependência na tag da F1.
