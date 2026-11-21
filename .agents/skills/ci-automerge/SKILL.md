---
name: ci-automerge
description: >-
  Configura e mantém automação de CI para versionamento, PR de release, tag e GitHub Release
  com GitHub Actions (Conventional Commits no título do PR + release-please), protegendo
  tags v* e separando o que o bot automatiza do ato humano de mesclar o release. Use quando
  precisar configurar, ajustar ou auditar pipelines de release automático em repositórios de
  pacotes ou aplicações, migrar de pré-lançamento para versão final ou criar testes de guarda
  para a configuração de release.
license: MIT
metadata:
  author: Emiliano Barbosa
  version: "1.0"
---

# Skill — Automação de CI e release (`pr-title` + `release-please`)

Automatizar versionamento, `CHANGELOG.md`, tags e GitHub Releases elimina trabalho manual
repetitivo, mas exige guardrails claros: tags `v*` protegidas não podem ser apagadas nem
movidas, e um erro de configuração no bot gera versões erradas ou trava os releases seguintes.

Este skill captura o padrão validado em repositórios de pacotes com GitHub Actions, deixando
explícita a fronteira entre **o que o CI automatiza** e **o que continua sendo decisão humana**.

## 1. Arquitetura mínima (2 workflows)

### a) Validação de título do PR (`pr-title.yml`)

O título do PR vira a mensagem do commit de *squash* na `main` e alimenta o cálculo da versão.

- Dispare em `pull_request` (`types: [opened, edited, synchronize, reopened]`).
- Permissão mínima: `contents: read`.
- Valide **Conventional Commits**:
  `^(feat|fix|docs|chore|refactor|test|ci|build|perf|revert|style)(\([a-z0-9._/-]+\))?!?: .+`
- Mapeamento SemVer:
  - `fix:` → `PATCH`
  - `feat:` → `MINOR`
  - `!` ou `BREAKING CHANGE` → `MAJOR`

### b) Bot de release (`release-please.yml`)

- Dispare em `push` na `main`.
- Permissões mínimas: `contents: write` e `pull-requests: write`.
- Use `concurrency` com `group: release-please` e `cancel-in-progress: false` para que dois
  merges próximos na `main` não cancelem a atualização do PR de release no meio.
- Fixe a action por **SHA de commit** (com comentário da tag, ex.: `# v5.0.0`), não por tag
  mutável.
- Passe `config-file: release-please-config.json` e
  `manifest-file: .release-please-manifest.json`.

## 2. Configuração do manifesto e das tags

Em `release-please-config.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    ".": {
      "release-type": "simple",
      "package-name": "<nome-do-pacote>",
      "include-v-in-tag": true,
      "include-component-in-tag": false,
      "changelog-path": "CHANGELOG.md",
      "extra-files": [
        "apm.yml"
      ]
    }
  }
}
```

- **`include-v-in-tag: true` + `include-component-in-tag: false`:** gera tags limpas `vX.Y.Z`.
  Sem `include-component-in-tag: false`, o bot prefixa o nome do pacote (`<pacote>-vX.Y.Z`),
  quebrando consumidores que esperam `#vX.Y.Z`.
- **`extra-files`:** liste arquivos de manifesto que carregam a versão (ex.: `apm.yml`,
  `package.json`, `pyproject.toml`) usando a anotação esperada pelo `release-please`
  (`x-release-please-version` quando aplicável). **Nunca edite a versão desses arquivos à mão**;
  mantenha-os sincronizados com `.release-please-manifest.json` pelo bot.

## 3. Fronteira de automação: publicar é ato humano

O CI automatiza:
- validar o título do PR;
- calcular o próximo SemVer e atualizar `CHANGELOG.md`, manifesto e `extra-files`;
- abrir e manter o PR de release atualizado a cada merge na `main`;
- criar a tag `vX.Y.Z` e o GitHub Release **depois** que o PR de release é mesclado.

O CI **não** deve fazer:
- **auto-merge do PR de release** (não use `auto-merge`, `automerge`, `gh pr merge --auto` ou
  `enablePullRequestAutoMerge` no workflow de release).
- Motivo: tags `v*` devem ser protegidas contra exclusão e movimentação. Revisar a versão
  proposta e clicar em *Merge* no PR de release é o gate humano que evita publicar uma tag
  errada de forma irreversível.

## 4. Regras que evitam surpresas em produção

- **Apenas commits liberáveis abrem PR de release:** `docs:`, `chore:` e `ci:` ficam ocultos
  do `CHANGELOG.md` e **não** provocam a abertura do PR de release. Só `feat:`, `fix:` ou
  mudanças incompatíveis (`!` / `BREAKING CHANGE`) acionam o bot.
- **Nunca use `release-as` em `release-please-config.json`:** se esquecido na configuração, o
  bot repetirá a mesma versão em toda proposta seguinte. Quando precisar forçar uma versão
  pontualmente, use um commit `fix` com o rodapé `Release-As: <versão>` na mensagem do commit
  de *squash*.
- **Graduação de pré-lançamento (`1.0.0-alpha.1` → `1.0.0`):**
  1. Para publicar o pré-lançamento, configure `"versioning": "prerelease"`, `"prerelease": true`
     e `"prerelease-type": "alpha.1"`.
  2. Para graduar para a versão final `1.0.0`, mude apenas `"prerelease": false` e **mantenha**
     `"versioning": "prerelease"` até a tag `v1.0.0` existir. Sem essa estratégia, o bot parte
     do sufixo alpha e propõe `2.0.0-alpha.1` ou `1.1.0-alpha.1` em vez de `1.0.0`.
  3. Depois que `v1.0.0` for criada, remova `versioning` e `prerelease-type`.

## 5. Testes de guarda da configuração de release

Adicione uma suíte unitária rápida (ex.: `tests/release/test_release_config.py`) que rode no
CI e proteja os invariantes da configuração:

1. `release-please-config.json` é JSON válido com `$schema` e chave `.` em `packages`.
2. `include-v-in-tag` é `true` e `include-component-in-tag` é `false`.
3. `extra-files` contém o arquivo de manifesto do pacote e a versão nele bate exatamente com
   `.release-please-manifest.json`.
4. `release-as` **não** aparece em `release-please-config.json`.
5. Se a versão atual no manifesto contém `-` (pré-lançamento), `versioning` continua igual a
   `"prerelease"`.
6. `release-please.yml` dispara em `push` na `main`, usa `googleapis/release-please-action` e
   **não** contém termos de mesclagem automática (`auto-merge`, `automerge`, `gh pr merge`,
   `--auto`, `enablePullRequestAutoMerge`).

## Armadilhas

- Esquecer `"include-component-in-tag": false` e só descobrir depois que uma tag com prefixo
  indesejado já foi criada e protegida.
- Abrir PR com `docs:` ou `chore:` esperando que o `release-please` abra o PR de release.
- Remover `"versioning": "prerelease"` antes da tag final `v1.0.0` existir, fazendo o bot
  propor `2.0.0-alpha.1` em vez de `1.0.0`.
- Deixar `"release-as"` em `release-please-config.json` em vez de usar o rodapé
  `Release-As:` no commit de *squash*.
- Habilitar auto-merge no PR de release ou editar a versão do manifesto à mão, quebrando a
  sincronia com `.release-please-manifest.json`.
