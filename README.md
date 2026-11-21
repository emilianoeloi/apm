# apm

[![Release](https://img.shields.io/github/v/release/emilianoeloi/apm)](https://github.com/emilianoeloi/apm/releases)
[![Licença: MIT](https://img.shields.io/badge/licença-MIT-blue.svg)](LICENSE)

Pacote APM (Agent Package Manager) público e genérico, com Lean Inception, Harness e SDLC em skills, agentes e hooks, para qualquer stack (iOS, Rust, JavaScript, Go e outras). É instalado por versão e entregue para `claude` e `copilot`.

O SDLC do pacote é **verificável**: todo requisito da spec tem um cenário Gherkin conferido por sensor, todo cenário novo tem um teste de aceitação escrito antes do código, e o revisor confere o vínculo entre cenário e teste.

## Índice

- [Instalação](#instalação)
- [O que o pacote entrega](#o-que-o-pacote-entrega)
- [Fluxo de desenvolvimento](#fluxo-de-desenvolvimento-openspec--openspdd)
- [Agentes de SDLC](#agentes-de-sdlc)
- [Hooks](#hooks)
- [Testes de aceitação](#testes-de-aceitação)
- [Conferência de cenários na revisão](#conferência-de-cenários-na-revisão)
- [Sensor de Gherkin](#sensor-de-gherkin)
- [Migração](#migração)
- [Versões e releases](#versões-e-releases)
- [Contribuindo](#contribuindo) e [Licença](#licença)

## Instalação

Requisitos: o CLI `apm`, o `python3` (os hooks usam só a biblioteca padrão) e, para o fluxo de especificação, o CLI `openspec` 1 ou maior.

No `apm.yml` do projeto:

```yaml
dependencies:
  apm:
    - emilianoeloi/apm#v2.0.0
```

Depois rode `apm install --target claude,copilot` e commite `apm.yml`, `apm.lock.yaml` e os diretórios implantados. Hooks são código executável: revise os scripts antes de instalar.

## O que o pacote entrega

| Pasta em `.apm/` | Conteúdo |
|---|---|
| `skills/` | Lean Inception, harness, OpenSpec (`openspec-*`), OpenSPDD (`spdd-*`), `acceptance-from-spec`, `skill-retrospective`, `install-dev-harness` e outros |
| `agents/` | Os quatro agentes `sdlc-*` |
| `prompts/` | Os comandos `/opsx-*` |
| `hooks/` | O registro e os scripts de hook (inclui `gherkin-sensor.py` e `spec-trace.py`) |
| `scripts/` | `phase_cli.py` (gate de fase) e o pre-commit genérico |
| `templates/` | O modelo de `harness.config.json` e o do quadrante do harness |

## Fluxo de desenvolvimento (OpenSpec + OpenSPDD)

O pacote mantém **vendorizadas** as skills e prompts de OpenSpec e OpenSPDD, então `apm install` entrega o fluxo completo:

| Origem | Em `.apm/` | Comandos |
|---|---|---|
| OpenSpec | `skills/openspec-*` (6) e `prompts/opsx-*.prompt.md` | `/opsx-propose`, `/opsx-explore`, `/opsx-apply`, `/opsx-update`, `/opsx-sync`, `/opsx-archive` |
| OpenSPDD (original, `openspdd generate -t codex`) | `skills/spdd-*` (5) | `/spdd-analysis`, `/spdd-reasons-canvas`, `/spdd-generate`, `/spdd-sync`, `/spdd-prompt-update` |

Depois de cada feature, o skill `skill-retrospective` decide se skills existentes devem ser atualizados ou se um novo deve ser criado. Os skills autorais (`openspec-workflow`, `install-dev-harness`) integram o fluxo com o gate de fase; o OpenSPDD é mantido sem alterações. O estado por projeto (`openspec/`) é criado com `openspec init --tools none`.

Para atualizar o vendor (requer os CLIs `openspec` e `openspdd`):

```bash
python3 scripts/sync-vendor.py
git diff   # revise antes de publicar
```

As versões usadas ficam em [vendor.json](vendor.json). Não edite à mão os arquivos vendorizados: o próximo sync os sobrescreve; customizações vão nas skills autorais.

## Agentes de SDLC

Quatro agentes de papel único e fonte única (`.apm/agents/sdlc-*.agent.md`), entregues para `claude` (`.claude/agents/`) e `copilot` (`.github/agents/`). **A sessão principal dispara cada um; eles não se chamam entre si.**

| Agente | Fase | O que faz | Escreve |
|---|---|---|---|
| `sdlc-planner` | `proposal` | proposta OpenSpec validada, análise e REASONS Canvas | só `planning_write_prefixes` (por padrão `openspec/` e `spdd/`); nunca código |
| `sdlc-coder` | `apply` | código pelas Operations do canvas, com o teste de aceitação de cada cenário antes do código (skill `acceptance-from-spec`); roda os sensores antes de entregar; para se não houver canvas | só `code_prefixes` e os checkboxes do `tasks.md` |
| `sdlc-reviewer` | depois da implementação | confere código, Operations, tasks e o vínculo cenário-teste; roda `openspec validate --strict` e os sensores; entrega relatório com veredito | nada: somente leitura |
| `sdlc-auditor` | sob demanda | responde dúvidas e audita conformidade, arquitetura e segurança com evidências de arquivo e linha | nada: somente leitura |

**Ordem de disparo**

1. Pedido de funcionalidade: declare a fase (`python3 scripts/harness/phase_cli.py set proposal <change>`) e dispare o `sdlc-planner`.
2. O humano revisa e aprova a proposta, a análise e o canvas.
3. Declare `set apply <change>` e dispare o `sdlc-coder`.
4. Dispare o `sdlc-reviewer` e leia o relatório; o humano decide o merge. Depois, `/spdd-sync`, `openspec archive` e a retrospectiva de skills.

Um arquivo serve aos dois hosts: o frontmatter tem só `name`, `description` e `tools`. Nenhum agente cita linguagem, pasta ou comando de um projeto: as pastas e o comando de sensores vêm do `harness.config.json`, e as regras, do arquivo raiz do agente (`CLAUDE.md` ou `AGENTS.md`).

**Limites.** O somente leitura do reviewer e do auditor vem de ferramentas mínimas (sem `Write` e `Edit`) e do texto; o `Bash` que eles têm ainda poderia escrever, por isso o relatório confirma que o `git status --porcelain` final é igual ao inicial. O escopo do coder em `apply` não tem bloqueio mecânico: o reviewer o confere pelo diff. O carregamento dos quatro agentes no Copilot não foi verificado num Copilot real. Veja as provas em [docs/roteiro-de-teste.md](docs/roteiro-de-teste.md).

## Hooks

`apm install --target claude,copilot` copia os scripts (com o helper `_common.py`) e os registra em `.claude/settings.json` e `.github/hooks/`. Se o `apm.yml` do projeto declara um bloco `executables:`, aprove o pacote com `apm approve emilianoeloi/apm`.

| Evento | Script | O que faz |
|---|---|---|
| `SessionStart` | `session-start.py` | injeta fase, branch e guias no contexto da sessão |
| `PreToolUse` (escrita) | `pre-tool-write-guard.py` | bloqueia credenciais, escrita fora da raiz do projeto e código na fase `proposal` |
| `PreToolUse` (Bash) | `pre-tool-bash-guard.py` | bloqueia `git push`, `git reset --hard`, `git clean -f`, `git branch -D` e `rm -rf` (só quando são o comando) e, em `proposal`, os que mutam o repositório |
| `PostToolUse` (Bash) | `gherkin-sensor.py --on-validate` | depois de um `openspec validate`, falha com código 2 se algum requisito não tiver bloco Gherkin |
| `Stop` | `stop-sensors.py` | roda o comando de sensores do projeto e só deixa encerrar se ele passar |

Tudo é configurado pelo `harness.config.json` do projeto (modelo em `.apm/templates/`):

- `sensors_command`: o comando que o `Stop` roda. **Vazio por padrão: sem comando, nada bloqueia.** Saída diferente de 0 ou estouro de `sensors_timeout_seconds` (50 s) bloqueia o encerramento e mostra a saída. O comando roda em shell: revise-o como qualquer outro hook.
- `allowed_write_roots`: diretórios absolutos fora do projeto onde a escrita é permitida (por exemplo `/tmp`); vazio por padrão.
- Fase, prefixos de planejamento e de código, nomes de arquivo e padrões de comando bloqueados.

Configuração ou payload ausente, corrompido ou de tipo errado nunca derruba nem trava um hook: só desliga os checks que dependem dela. As defesas embutidas (credenciais, `git push` e demais comandos destrutivos) continuam valendo sem configuração. O harness é uma rede de segurança contra deslizes do agente, não um sandbox: formas como `env X=1 git push` não são detectadas. O pre-commit genérico (`.apm/scripts/git-hooks/pre-commit`) roda o mesmo `sensors_command`; veja o skill `install-dev-harness`.

O bloqueio foi comprovado no Claude Code (código de saída 2). O formato do Copilot (`.github/hooks/`) é gerado pelo APM e coberto por testes de saída, mas **não foi verificado num Copilot real**.

## Testes de aceitação

O skill `acceptance-from-spec` faz o `sdlc-coder`, na fase `apply`, escrever **primeiro** o teste de aceitação de cada `Cenário:` aprovado da change, provar que ele falha, implementar e provar que ele passa. O skill não fixa ferramenta de teste: descobre a do projeto.

1. **Ligação com a spec.** Cada teste leva uma linha literal, em comentário ou no nome do teste: `Spec: <capability> / <nome do requisito> / <título do cenário>`, com os três textos copiados da spec.
2. **Vermelho antes do código.** O coder relata o comando, a contagem de falhas e o motivo, sem stubs artificiais. O vermelho vem da asserção do `Então`, não de erro do ambiente: um programa ausente costuma sair com código de erro genérico e fazer passar um teste que só confere o código. Teste que passa sem o programa existir é **falso verde**; afirme o conteúdo, não só o código de saída.
3. **Verde depois.** O coder roda o teste e o `sensors_command` e confere que o comando **executa** a aceitação; se não executa ou está vazio, diz "sensores não configurados" em vez de afirmar que passou.
4. **Sem framework: propõe e espera.** O coder descobre a ferramenta (arquivo raiz do agente, `sensors_command`, testes existentes, manifesto de build). Se não houver, não escreve nem instala nada: devolve de uma a três opções com o relatório `BLOQUEADO` e para até a aprovação.

**Convenções.**
- **`#### Scenario:` extras.** Um extra com comportamento distinto leva a linha `Extra: <capability> / <requisito> / <título>`, nunca `Spec:`; o `spec-trace` ignora o rótulo `Extra:`.
- **Fixtures.** Monte a linha `Spec:` de exemplo por constante, em tempo de execução, para não criar `ORFAO` no próprio teste.
- **Cenário só de prova humana.** Um cenário que descreve o comportamento do modelo e só uma prova humana cobre fica como `SEM_TESTE` conhecido, com a decisão do humano registrada no `design.md`; não ligue um teste de texto que finja cobri-lo.
- **Tasks do planner.** O `sdlc-planner` gera as tasks de teste com um teste por `Cenário:` do bloco. Cenário idêntico ao da spec principal não exige teste novo.

**Migração.** Em projetos que ainda não usam o skill, atualize a dependência do apm e rode `apm install`: a partir daí o coder exige o teste antes do código, a primeira `apply` sem ferramenta de teste para e pede a sua escolha, e o `sensors_command` precisa rodar a aceitação. O skill 1.1 só acrescenta as convenções acima. Detalhes no [guia de migração](docs/migracao.md).

## Conferência de cenários na revisão

O `sdlc-reviewer` confere se cada `Cenário:` da change tem um teste ligado pela linha `Spec:`. Ele continua **somente leitura**: usa o script `spec-trace.py`, que só lê e não deixa rastro, e cita o resultado no relatório.

```bash
python3 -B <caminho>/spec-trace.py --root . --change <nome-da-change>
```

O reviewer usa a cópia implantada do host (`.claude/hooks/apm/.apm/hooks/scripts/` ou `.github/hooks/scripts/apm/.apm/hooks/scripts/`), nunca a de `apm_modules/`. Com `Glob` ele a acha por `**/spec-trace.py`; sem `Glob`, o plano B é `find . -name spec-trace.py -not -path "*/apm_modules/*"`. A saída tem uma linha por cenário, `spec-trace: ESTADO capability / requisito / cenário @ arquivo:linha`, e um resumo no fim.

| Estado | Significado | Efeito no veredito |
|---|---|---|
| `COBERTO` | há um teste com a linha `Spec:` do cenário | nenhum |
| `SEM_TESTE` | cenário novo ou alterado sem teste ligado | **reprova** |
| `HERDADO_SEM_TESTE` | cenário antigo de um requisito modificado, sem alteração | só informativo |
| `ORFAO` | linha `Spec:` sem cenário correspondente | achado de severidade média |
| `AMBIGUO` | a linha casa com mais de um cenário | achado de severidade média |

Só o cenário **novo ou alterado** da change é exigido: cenários antigos não são exigidos. O agente também reprova o **falso verde** (o teste que não afirma o `Então` ou que passaria sem o código), o que ele decide lendo o teste. A saída 2 do script não é o veredito: só `SEM_TESTE` reprova.

**Fim do título do marcador.** Depois do título do cenário só vale um fechamento de comentário conhecido (`*/`, `-->`, `--]]`, `--}}`, `%}`, `?>`, aspas, `)`, `]`, `}`, `#` ou `//`) ou nada, seguido de uma fronteira (fim da linha, espaço ou outro fechamento). Qualquer outro sufixo (`-`, `_`, `.`, `(`, letra ou dígito) deixa a linha sem casar e ela vira `ORFAO`. O casamento é no código-fonte dos testes, nunca na saída do executor. O arquivo de teste é aberto sem bloquear em FIFO ou dispositivo e, onde o sistema oferece `O_NOFOLLOW`, sem seguir link.

**Limites.** O script prova o vínculo, não a qualidade do teste: essa parte é leitura do agente. Fixtures com uma linha `Spec:` dentro de uma string aparecem como `ORFAO` (monte a linha por constante). O comportamento do modelo no reviewer foi exercitado em provas com um modelo e uma fixture, sem taxa de acerto. Dois cenários de comportamento do modelo (`sdlc-agent-roles`) ficam `SEM_TESTE` conhecidos.

**Migração.** Depois de atualizar o apm, o reviewer passa a reprovar cenário novo ou alterado sem teste ligado. Cenários antigos não são exigidos. Se um projeto usa um fechamento de comentário fora da lista, o cenário passa a sair `ORFAO`; o caminho durável é deixar o marcador sozinho no fim da linha. Veja o [guia de migração](docs/migracao.md).

## Sensor de Gherkin

Todo requisito das specs do OpenSpec traz um bloco ` ```gherkin ` com `Cenário:`, `Dado`, `Quando` e `Então`, antes do primeiro `#### Scenario:`. O sensor `gherkin-sensor.py` (só biblioteca padrão, ao lado dos outros hooks) confere isso e **falha com código 2 citando o requisito**; sem violação, sai 0 e fica mudo.

```text
gherkin: sensor-gate / Requirement: Exemplo [change minha-change]: esperado exatamente 1 bloco gherkin, achei 0
```

Ele lê as specs principais e aplica os deltas das changes ativas (`ADDED`, `MODIFIED`, `REMOVED` e `RENAMED`; `archive/` é ignorado). A raiz vem de `--root`, depois de `CLAUDE_PROJECT_DIR`, depois do `.git`; sem pasta `openspec/` ele sai 0 com um aviso.

- **Junto do `openspec validate`:** o hook `PostToolUse` roda o sensor depois de qualquer `openspec validate` no Bash. Funciona sem editar a configuração do projeto.
- **No Stop e no pre-commit:** componha no `sensors_command`, por exemplo `python3 -m unittest discover -s tests -t . && python3 <caminho>/gherkin-sensor.py`. Nos modelos entregues o comando segue vazio.
- **Limites:** o casamento do comando é por texto, então um comando que só cite `openspec validate` também roda o sensor (ruído, sem dano). O disparo do hook numa sessão real e no Copilot não foi verificado.

O `openspec validate --strict` segue como juiz da estrutura; o sensor só confere o bloco.

## Migração

Versões incompatíveis e o que fazer em cada uma estão no [guia de migração](docs/migracao.md):

- **1.x para 2.0:** specs sem bloco Gherkin passam a falhar no sensor, o coder exige o teste de aceitação antes do código e o reviewer reprova cenário novo sem teste.
- **0.3.x para 1.0:** a limpeza do projeto de origem (`cowboy`, uma calculadora em COBOL) removeu, de forma incompatível, os agentes, prompts, skills e hooks de COBOL. O conteúdo não foi movido: quem ainda precisa dele mantém a dependência na tag `v0.3.1`.

## Versões e releases

Os releases são automáticos, com o [release-please](https://github.com/googleapis/release-please-action) e **Conventional Commits** nos títulos dos PRs: `feat` gera MINOR, `fix` gera PATCH e `!` gera MAJOR. O bot mantém um PR de release com a versão e o [CHANGELOG](CHANGELOG.md); **mesclar esse PR é o ato humano** que cria a tag `vX.Y.Z` e o GitHub Release. Tags `v*` não se apagam nem se movem. A `v0.3.1` foi a última versão com o conteúdo do projeto de origem, e a `v1.0.0` foi a primeira estável genérica.

Detalhes (como forçar uma versão, cuidados antes de mesclar e o histórico): [docs/releases.md](docs/releases.md). O registro de desenvolvimento por onda está em [docs/historico.md](docs/historico.md).

## Contribuindo

Veja o [CONTRIBUTING.md](CONTRIBUTING.md). Os testes rodam com `python3 -B -m unittest discover -s tests -t .`.

## Licença

[MIT](LICENSE).
