# Changelog

## Onda 1 — F2: hooks genéricos (2026-11-12)

Change `hooks-genericos`. Ainda sem tag e sem push; a F3 e o pré-lançamento `1.0.0-alpha.1` vêm depois.

### Novidades

* Hook de Stop `stop-sensors`: roda o `sensors_command` do `harness.config.json` (vazio por padrão). Sem comando, sem arquivo ou sem Makefile, o encerramento é permitido; sensor que falha ou estoura `sensors_timeout_seconds` bloqueia com código 2 e mostra a saída. Estouro de tempo mata o grupo de processos, sem sensor órfão.
* Entrega pelo APM: hooks e scripts em `.apm/hooks/`; `apm install --target claude,copilot` registra `SessionStart`, `PreToolUse` e `Stop` em `.claude/settings.json` e `.github/hooks/` e implanta os scripts, sem cópia manual. O risco 1 da spec está resolvido.
* Pre-commit genérico em `.apm/scripts/git-hooks/pre-commit`, que roda o mesmo `sensors_command`.
* `allowed_write_roots` (opt-in, vazio por padrão) para escrita fora do projeto, como `/tmp`.
* Primeira bateria de testes do pacote (`tests/`, `unittest`, 81 testes), usada como `sensors_command` do próprio repositório.

### Correções

* Hooks não quebram mais com configuração ou payload ausente, corrompido ou de tipo errado; as defesas embutidas seguem valendo sem configuração.
* Contenção de caminho exata (`/tmp/proj-outro` deixou de passar como se fosse `/tmp/proj`), nos guardas e no `phase_cli.py`; `phase_cli.py show` aguenta estado corrompido.
* Bloqueio no formato de cada host: código 2 e motivo em stderr no Claude Code; JSON `deny` no Copilot. Antes só existia o JSON, que o Claude Code não usa para bloquear.
* Padrões de comando ancorados na posição de comando: `git push` citado em texto (mensagem de commit, corpo de PR) não bloqueia mais.
* Padrão de `git branch` só bloqueia `-D`; `git branch -a` e `-vv` passam.
* O skill `install-dev-harness` deixou de copiar scripts e de mesclar `settings.json`; o modelo de `harness.config.json` perdeu a entrada de pre-commit inexistente.

### Mudanças de quem usa o pacote

* Projetos que copiaram `scripts/hooks/` (0.3.x) devem apagar a cópia e deixar o `apm install` registrar os hooks, para não duplicar. Os padrões de comando nos `harness.config.json` existentes não mudam sozinhos: copie os novos do modelo.
* O `.claude/hooks/<pacote>/` e `.github/hooks/scripts/<pacote>/` passam a existir no projeto; o caminho usa o nome do pacote (`apm`).

### Verificação

* `python3 -m unittest discover -s tests -t .`: 81 testes ok. Busca por "cowboy", "cobol", "cobc" e "calculadora" em `.apm/`, `.claude/`, `.agents/`, `.github/` e `apm.lock.yaml`: vazia.
* Projeto consumidor temporário que depende do pacote: instalação ok e 8/8 verificações dos scripts implantados (Stop sem configuração sai 0; Stop com sensor que falha sai 2 com a saída; Bash bloqueado; escrita em `.env` bloqueada; configuração corrompida não trava; Copilot devolve JSON `deny`).
* **Claude Code real:** com os hooks entregues pelo APM ativos na sessão, o guarda de Bash e o de escrita bloquearam comandos reais (código 2, motivo em stderr). Foi assim que apareceram a menção em texto e a pasta temporária fora do projeto.
* **Não verificado:** o formato do Copilot (`.github/hooks/`) e a decisão `agentStop` dele num Copilot real; só há testes de saída. O comportamento de `apm approve` para pacotes remotos também não foi exercitado (a dependência local foi aceita sem aprovação).

### Observações

* O aviso do APM "Skill 'harness' replaced overlapping files" segue aparecendo a partir da segunda rodada do `apm install` (registrado na F1).
* Meus testes numa cópia temporária deixaram recibos em `~/.apm/deployment-receipts` (sem efeito neste repositório; não removidos).
* Sem hooks ativos no repositório, `git push` e demais comandos destrutivos passam a ser bloqueados nas sessões do Claude Code: o push precisa ser feito pelo desenvolvedor.

### Retrospectiva de skills

* `install-dev-harness`: atualizado nesta change (hooks pelo APM, `sensors_command`, pre-commit opcional, `allowed_write_roots`); os furos da Onda 0 foram fechados. Falta publicar o skill; nada foi publicado sem o "ok".
* `dev-harness-architect` e `harness-quadrant-process`: devem pedir um teste de fumaça de que o hook dispara no host (aqui o formato errado passou despercebido porque o bloqueio nunca era exercitado). Proposta de atualização, skill público.
* `openspec-workflow`: continua com os pontos da F1 (criação manual do `.openspec.yaml`, fases das tasks); candidato a receber também a orientação de adaptar o canvas a mudanças que não são de backend.
* Skill novo: nenhum necessário.

## Onda 1 — F1: limpeza do cowboy (2026-11-12)

Change `limpeza-do-cowboy`. Ainda sem tag e sem push; a F2, a F3 e o pré-lançamento `1.0.0-alpha.1` vêm depois.

### ⚠ BREAKING

* Removidos os agentes `cobol-vibecoder`, `cobol-planner`, `cobol-coder`, `cobol-reviewer` e `readme-writer`.
* Removidos os prompts `criar-programa`, `implementar-soma`, `implementar-subtracao`, `implementar-log`, `testar-programa`, `atualizar-readme` e `manutencao-repositorio`.
* Removidas as skills `cobol-calculadora`, `vibe-coding-fundamentals` e `readme-manutencao`.
* Removidos o pre-commit que compilava COBOL e o guia `cowboy.instructions.md`. O hook `cowboy.json` já saíra na Onda 0.
* Quem depende da 0.3.x deve manter a tag `v0.3.1` (aviso de migração no README).

### Mudanças

* `openspec-workflow` sem exemplos COBOL; `HARNESS_QUADRANTE.md` virou modelo com campos a preencher.
* `apm.yml`: nome `apm` e descrição genérica (a versão segue com o release-please). README público, sem "extraído do cowboy", com aviso de migração.
* `.harness/` no `.gitignore`.
* Pacote reimplantado com `apm install --target claude,copilot`: 36 arquivos antigos limpos de `.claude/`, `.agents/` e `.github/`.

### Verificação

* Busca por "cowboy", "cobol", "cobc" e "calculadora" em `.apm/`, `.claude/`, `.agents/`, `.github/agents`, `.github/prompts` e `apm.lock.yaml`: vazia.
* `session-start.py`, `openspec list`, `phase_cli.py show` e `openspec validate limpeza-do-cowboy --strict`: ok.
* `.apm/agents/` ficou sem arquivos e a pasta deixou de existir no git (o APM avisa sobre `.gitkeep` em pasta de agentes); a F3 a recria com os agentes `sdlc-*`.

### Observações

* O `apm install` (0.35.0) mostra, a partir da segunda rodada, o aviso "Skill 'harness' replaced overlapping files from another package". Os arquivos implantados estão corretos e o lockfile só lista o pacote local; causa não identificada, vale reportar ao projeto do APM se persistir.
* Testes numa cópia temporária deixaram 6 recibos de implantação em `~/.apm/deployment-receipts` (arquivos sem efeito neste repositório); não foram removidos.

### Retrospectiva de skills

* `openspec-workflow` (autoral): manda criar `.openspec.yaml` e as pastas à mão, mas o `openspec new change` já faz isso; e a lista de fases das tasks (Propose, Analysis, Canvas, Generate, Review) não bate com os grupos que o schema `spec-driven` pede (cada grupo com seus testes e documentação). Proposta: atualizar o skill (público). Nada publicado.
* `spdd-reasons-canvas` e `spdd-generate` (vendorizados): os modelos são de backend Java (controller, service, anotações) e servem mal a mudanças de empacotamento ou documentação; adaptei as seções à mão. Como são vendorizados, a orientação para esses casos deve ir no `openspec-workflow` (público), não nos arquivos do vendor.
* `install-dev-harness`: os furos da Onda 0 seguem abertos (guia de pre-commit no template, fonte local no passo 3, chave `_comment` do `settings.hooks.json`). Skill novo: nenhum necessário.

## Onda 0 — preparo do repositório (2026-11-12)

Spec: APM_SETUP V1.2. Nenhuma tag e nenhum push; a Onda 1 (1.0.0-alpha.1) ainda não começou.

### Feito

* Removido `.apm/hooks/cowboy.json` (hook de Stop do cowboy que exigia `make fitness`).
* Harness instalado no próprio repositório pela **fonte local** (`apm install --target claude,copilot`, sem instalar a tag v0.3.1): `apm.lock.yaml`, `.claude/`, `.agents/`, `.github/agents/` e `.github/prompts/`.
* Estado do OpenSpec criado com `openspec init --tools none --language português` (`openspec/`); pastas `spdd/analysis/` e `spdd/prompt/`.
* Gate de fase: `harness.config.json` (planejamento em `openspec/`, `spdd/`, `.harness/`; código em `.apm/`, `scripts/`, `tests/`), `scripts/hooks/*.py`, `scripts/harness/phase_cli.py`, `.claude/settings.json` e `CLAUDE.md` (quality gates: não informado).

### Verificação

* `session-start.py` imprime JSON com `additionalContext`: ok.
* `openspec list` roda sem erro: ok.
* `phase_cli.py show` mostra a fase (não declarada): ok.
* `spdd-*/SKILL.md` e `opsx-*.prompt.md` existem em `.claude/skills/` e `.github/prompts/`: ok.
* `.apm/hooks/cowboy.json` não existe mais: ok.

### Observações

* O APM aceitou a fonte local do próprio repositório (risco 3 da spec não se confirmou).
* `apm install` ainda implanta agentes, prompts e skills COBOL em `.claude/`, `.agents/` e `.github/`, e avisa de frontmatter não suportado nos prompts do cowboy. Saem na Onda 1 (F1).
* Os hooks de segurança ainda não são entregues pelo APM (`.apm/_pending/hooks/harness.json`); por isso os scripts foram copiados para `scripts/` e registrados em `.claude/settings.json`.

### Retrospectiva de skills

* `install-dev-harness`: o template `harness.config.json.template` lista `.pre-commit-config.yaml` em `guide_files` mesmo sem o arquivo existir, gerando um "MISSING" falso (removido à mão aqui). O passo 3 só cobre `apm install <repo>#<tag>`, não a fonte local. `settings.hooks.json` traz uma chave `_comment` que precisou ser tirada ao criar `.claude/settings.json`. Proposta: atualizar o skill (público, serve a qualquer projeto). Nada publicado.
* Skill novo: nenhum necessário nesta onda.

## [0.3.1](https://github.com/emilianoeloi/apm/compare/v0.3.0...v0.3.1) (2026-11-11)


### Bug Fixes

* **release:** tag sem o nome do componente (vX.Y.Z) ([#8](https://github.com/emilianoeloi/apm/issues/8)) ([70812ed](https://github.com/emilianoeloi/apm/commit/70812ed29b8774245a9354753228c4cd4124fb6a))

## [0.3.0](https://github.com/emilianoeloi/apm/compare/harness-v0.2.0...harness-v0.3.0) (2026-11-11)


### Features

* pacote APM com o harness extraido do cowboy ([789c49e](https://github.com/emilianoeloi/apm/commit/789c49e155b64916185a57fe86315feca5293ad7))
* **skills:** install-dev-harness com fluxo APM + OpenSpec + OpenSPDD ([#3](https://github.com/emilianoeloi/apm/issues/3)) ([76f66a7](https://github.com/emilianoeloi/apm/commit/76f66a78e0c8a7b7dc4372ab6655844754dd097c))
* **skills:** skill-retrospective e passo de retrospectiva no fluxo ([#5](https://github.com/emilianoeloi/apm/issues/5)) ([368a0e8](https://github.com/emilianoeloi/apm/commit/368a0e8c56969231e75ef1618341cf43c50491fa))
* vendoriza OpenSpec e OpenSPDD (original) no pacote APM ([#4](https://github.com/emilianoeloi/apm/issues/4)) ([c29d3a7](https://github.com/emilianoeloi/apm/commit/c29d3a7d1a9819fe1802076cb8427858d973f231))


### Bug Fixes

* **hooks:** regex de bloqueio so casa no inicio do comando ([#2](https://github.com/emilianoeloi/apm/issues/2)) ([335a22e](https://github.com/emilianoeloi/apm/commit/335a22e9d7c6fda64f1c1adba302a4491c8bdb92))
