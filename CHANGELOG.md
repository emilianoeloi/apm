# Changelog

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
