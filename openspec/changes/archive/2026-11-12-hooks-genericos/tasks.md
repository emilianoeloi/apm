# Tasks

## 1. Estrutura, helper e modelos de configuração

- [x] 1.1 Mover `.apm/scripts/hooks/*.py` para `.apm/hooks/scripts/` (com `git mv`) e verificar que `.apm/scripts/hooks/` não existe mais
- [x] 1.2 Criar `.apm/hooks/scripts/_common.py` (raiz do projeto, configuração e payload tolerantes, contenção de caminho, decisão por host) e verificar com `python3 -c "import ast,sys;ast.parse(open('.apm/hooks/scripts/_common.py').read())"` que a sintaxe é válida e que só importa biblioteca padrão
- [x] 1.3 Criar `.apm/hooks/harness.json` no formato achatado (SessionStart, PreToolUse para `Write|Edit|NotebookEdit` e `Bash`, Stop) e apagar `.apm/_pending/hooks/harness.json`; verificar com `python3 -m json.tool .apm/hooks/harness.json`
- [x] 1.4 Acrescentar `sensors_command` (vazio) e `sensors_timeout_seconds` (50) aos dois modelos de `harness.config.json`, tirar a entrada `.pre-commit-config.yaml` do `guide_files` do modelo do skill, e verificar que os dois arquivos continuam sendo JSON válido (`python3 -m json.tool`) quando os marcadores `{{...}}` são substituídos

## 2. Hook de Stop com testes

- [x] 2.1 Escrever `tests/hooks/test_stop_sensors.py` (unittest, scripts chamados por `subprocess` com `CLAUDE_PROJECT_DIR` temporário) cobrindo os cenários de `sensor-gate` e verificar que os testes falham antes do script existir
- [x] 2.2 Implementar `.apm/hooks/scripts/stop-sensors.py` e verificar com `python3 -m unittest tests.hooks.test_stop_sensors -v` que todos os cenários passam (sem configuração, comando vazio, sensor que passa, que falha, que estoura o tempo, `stop_hook_active`, raiz como diretório de trabalho)

## 3. Guardas robustos e corrigidos, com testes

- [x] 3.1 Escrever `tests/hooks/test_guards.py` cobrindo os cenários de `hook-runtime` (configuração corrompida e que não é objeto, payload inválido, bloqueios embutidos sem configuração, pasta irmã, formato Claude e Copilot, fase `proposal`) e verificar que falham no código atual
- [x] 3.2 Refatorar `pre-tool-write-guard.py`, `pre-tool-bash-guard.py` e `session-start.py` para usar `_common.py` e verificar com `python3 -m unittest tests.hooks.test_guards -v` que os testes passam
- [x] 3.3 Corrigir o `phase_cli.py` (contenção de caminho exata e `show` com estado corrompido), com teste em `tests/hooks/test_phase_cli.py`, e verificar com `python3 -m unittest tests.hooks.test_phase_cli -v`
- [x] 3.4 Ancorar os padrões de comando bloqueados na posição de comando e restringir o padrão de branch ao `D` maiúsculo, alinhando os dois modelos e o `harness.config.json`, e verificar com `tests.hooks.test_guards` e `tests.hooks.test_package` (inclui o teste de deriva entre guarda e modelos)
- [x] 3.5 Acrescentar `allowed_write_roots` (opt-in, vazio por padrão) ao guarda de escrita e aos modelos, e verificar com os testes de raiz extra em `tests.hooks.test_guards`

## 4. Entrega pelo APM

- [x] 4.1 Apagar `scripts/hooks/` e `.claude/settings.json` do repositório, rodar `apm install --target claude,copilot` e verificar que `.claude/settings.json` traz `SessionStart`, `PreToolUse` (dois matchers) e `Stop`, cada um uma vez, e que `.github/hooks/` tem o registro do pacote
- [x] 4.2 Provar a entrega num projeto temporário que depende do pacote local: instalar, rodar os scripts implantados com payloads de exemplo e verificar saída 0 para o Stop sem configuração e bloqueio para `git push`
- [x] 4.3 Rodar o bloqueio no Claude Code real (projeto temporário, execução sem interface, quando disponível) e registrar o resultado; se não for possível, registrar "não verificado" no CHANGELOG
- [x] 4.4 Criar `.apm/scripts/git-hooks/pre-commit` genérico e verificar num repositório temporário que passa sem `sensors_command` e bloqueia o commit quando o comando falha

## 5. Skill, documentação e dogfood

- [x] 5.1 Atualizar o skill `install-dev-harness`: o passo 3 e o passo 6 deixam de copiar scripts de hook e de mesclar `settings.hooks.json` (o APM entrega e registra), mencionam `apm approve` e o pre-commit genérico; apagar `templates/hooks/` e `templates/settings.hooks.json`; verificar com `grep -n "scripts/hooks\|settings.hooks" .apm/skills/install-dev-harness/SKILL.md`, que deve voltar vazio
- [x] 5.2 Apontar o `sensors_command` do `harness.config.json` do repositório para `python3 -m unittest discover -s tests -t . -v`, trocar "não informado" por esse gate no `CLAUDE.md` e verificar que `echo '{}' | python3 .apm/hooks/scripts/stop-sensors.py` sai com 0
- [x] 5.3 Atualizar o `README.md` (seção de hooks: o que o pacote entrega, `apm approve`, `sensors_command`; remover a nota pendente; declarar o Copilot como não verificado) e verificar relendo que cobre os cenários de entrega
- [x] 5.4 Atualizar a skill `openspec-workflow` e o `session-start.py` para não citar `scripts/hooks/`, e verificar com `grep -rn "scripts/hooks" .apm README.md CLAUDE.md`

## 6. Integração

- [x] 6.1 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` e a mesma busca em `.claude`, `.agents` e `.github`, e verificar que ambas voltam vazias
- [x] 6.2 Rodar `python3 -m unittest discover -s tests -t . -v` e `openspec validate hooks-genericos --strict` e verificar que passam
- [x] 6.3 Registrar a F2 na seção da Onda 1 do `CHANGELOG.md` (resultado, itens não verificados e retrospectiva de skills) e verificar que o texto lista o que foi entregue

## Workflow follow-up

- Abrir o PR com título `feat: …` e esperar o "ok" do Elói para o push e a mesclagem.
- Não mesclar o PR de release do release-please antes da change de pré-lançamento.
- Reconciliar o código com o canvas (`/spdd-sync`), arquivar a change depois do merge e fazer a retrospectiva de skills.
