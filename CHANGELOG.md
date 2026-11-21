# Changelog

## [2.0.0](https://github.com/emilianoeloi/apm/compare/v1.5.0...v2.0.0) (2026-11-21)


### ⚠ BREAKING CHANGES

* **agents:** lanca a 2.0 com cenarios Gherkin verificaveis e teste de aceitacao antes do codigo ([#42](https://github.com/emilianoeloi/apm/issues/42))

### Features

* **agents:** afina o skill de aceitacao e endurece o spec-trace ([#40](https://github.com/emilianoeloi/apm/issues/40)) ([a5786eb](https://github.com/emilianoeloi/apm/commit/a5786eb9688886fa13ba2d0e7258b776f9349a9f))
* **agents:** cenarios Gherkin na spec, sensor, teste de aceitacao e conferencia pelo reviewer ([#38](https://github.com/emilianoeloi/apm/issues/38)) ([063b541](https://github.com/emilianoeloi/apm/commit/063b5410a1197eebd1beaeb8e8a822badcc6e41e))
* **agents:** lanca a 2.0 com cenarios Gherkin verificaveis e teste de aceitacao antes do codigo ([#42](https://github.com/emilianoeloi/apm/issues/42)) ([6a858da](https://github.com/emilianoeloi/apm/commit/6a858dabc5db53c9f48f5f7a065d5f4067b4fc97))

## [1.5.0](https://github.com/emilianoeloi/apm/compare/v1.4.0...v1.5.0) (2026-11-21)


### Features

* **skills:** adiciona skill ci-automerge com padrões de CI e release-please ([#31](https://github.com/emilianoeloi/apm/issues/31)) ([43ee09c](https://github.com/emilianoeloi/apm/commit/43ee09cf2734a195aeace76d42690c8a966b10e6))

## [1.4.0](https://github.com/emilianoeloi/apm/compare/v1.3.0...v1.4.0) (2026-11-21)


### Features

* **skills:** atualiza drive-status, install-dev-harness e harness com aprendizados de multi-agente e Cloud Run ([#28](https://github.com/emilianoeloi/apm/issues/28)) ([c20dd14](https://github.com/emilianoeloi/apm/commit/c20dd14a832136e2293e7057cc8ccfbd19bb991a))

## [1.3.0](https://github.com/emilianoeloi/apm/compare/v1.2.0...v1.3.0) (2026-11-20)


### Features

* licoes de uma feature real com Firestore e dois agentes em sdlc-coder, sdlc-reviewer, sdlc-planner, install-dev-harness, openspec-workflow, drive-status e drive-reader-browser ([#26](https://github.com/emilianoeloi/apm/issues/26)) ([02db130](https://github.com/emilianoeloi/apm/commit/02db130f8607dcdd763663e75e26e84720326654))

## [1.2.0](https://github.com/emilianoeloi/apm/compare/v1.1.0...v1.2.0) (2026-11-20)


### Features

* skills de leitura do Drive no navegador e status, mais licoes de uma retrospectiva real ([#24](https://github.com/emilianoeloi/apm/issues/24)) ([ff27ced](https://github.com/emilianoeloi/apm/commit/ff27ced75308e129b19fb14ca4e73ca913eef73e))

## [1.1.0](https://github.com/emilianoeloi/apm/compare/v1.0.0...v1.1.0) (2026-11-20)


### Features

* **skills:** adiciona suporte ao Google Antigravity e guardrails de revisão SDLC ([#21](https://github.com/emilianoeloi/apm/issues/21)) ([362a95e](https://github.com/emilianoeloi/apm/commit/362a95eb80c949d3aa2a043169c9111bee15fd2a))

## [1.0.0](https://github.com/emilianoeloi/apm/compare/v1.0.0-alpha.1...v1.0.0) (2026-11-12)


### Bug Fixes

* **release:** documenta que o PR de release exige commit liberavel e propoe a 1.0.0 ([#19](https://github.com/emilianoeloi/apm/issues/19)) ([d3f0678](https://github.com/emilianoeloi/apm/commit/d3f067833435df691d47d718a2663a1d4b682f71))

## [1.0.0-alpha.1](https://github.com/emilianoeloi/apm/compare/v0.3.1...v1.0.0-alpha.1) (2026-11-12)


### ⚠ BREAKING CHANGES

* agentes, prompts e skills do cowboy deixam de existir; quem depende deles deve manter a tag v0.3.1.

### Features

* agentes de SDLC genéricos sdlc-planner, coder, reviewer e auditor (F3) ([#14](https://github.com/emilianoeloi/apm/issues/14)) ([ff3afa6](https://github.com/emilianoeloi/apm/commit/ff3afa62fd13d61f98868b6722f8e7938791356a))
* hooks genéricos com sensores configuráveis e entrega pelo APM (F2) ([#13](https://github.com/emilianoeloi/apm/issues/13)) ([db5389e](https://github.com/emilianoeloi/apm/commit/db5389efa36b29f3808c578638d75781d91b7cf0))
* remove o conteúdo do cowboy e neutraliza o pacote (F1) ([#11](https://github.com/emilianoeloi/apm/issues/11)) ([021fc8c](https://github.com/emilianoeloi/apm/commit/021fc8c123a121023a7da923cbf8b92777b0a43d))

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
