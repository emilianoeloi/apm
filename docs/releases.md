# Releases

Os releases saem do GitHub Actions com o [release-please](https://github.com/googleapis/release-please-action). O `CHANGELOG.md` é gerado por ele; as notas manuais de desenvolvimento ficam em [historico.md](historico.md).

## Como uma versão sai

1. Use **Conventional Commits** nos títulos dos PRs (`feat:`, `fix:`, `docs:`, `chore:`...). O workflow `pr-title` confere.
2. Ao mesclar na `main`, o bot abre ou atualiza um **PR de release** com a versão nova (`feat` → MINOR, `fix` → PATCH, `!` ou `BREAKING CHANGE` → MAJOR) e o `CHANGELOG.md`.
3. **Revisar e mesclar o PR de release** é o ato humano. Ao mesclar, o bot cria a tag `vX.Y.Z` e o GitHub Release.
4. No consumidor, atualize o `ref` no `apm.yml`, rode `apm install` e commite `apm.yml`, `apm.lock.yaml` e os diretórios implantados.

A linha `version:` do `apm.yml` é atualizada pelo bot (pelo `extra-files` do `release-please-config.json`, sem marcador no arquivo); não edite a versão à mão. Tags `v*` são protegidas contra apagar e mover.

## Regras e cuidados

- **Commit liberável.** O bot só abre o PR de release quando há ao menos um commit liberável (`feat`, `fix` ou mudança incompatível) desde a última tag. `docs`, `chore` e `ci` ficam escondidos do CHANGELOG e não o provocam (o log do workflow diz "No user facing commits found").
- **Forçar uma versão.** Use um commit `fix` ou `feat` com o rodapé `Release-As: <versão>` na mensagem do commit de squash. No GitHub, a mensagem de squash deste repositório lista as mensagens dos commits da branch: confira que o rodapé aparece antes de confirmar o merge.
- **Não use `release-as` na configuração.** Ele fixa a versão e, se ninguém o remover depois do release, todo PR de release repete a mesma versão. Um teste (`tests/release/`) impede que ele entre.
- **Antes de mesclar o PR de release,** confira o título, a versão no `apm.yml` e no `.release-please-manifest.json` e o CHANGELOG. Uma tag publicada não se apaga nem se move. Mesclar continua sendo ato humano; nenhuma etapa automática faz isso.

## Histórico de versões

- **0.3.1:** a última versão com o conteúdo do projeto de origem (`cowboy`).
- **1.0.0-alpha.1:** o pré-lançamento da 1.0.0, com os hooks genéricos e os agentes de SDLC. Para consumir um pré-lançamento, aponte a tag de forma explícita (`emilianoeloi/apm#v1.0.0-alpha.1`); quem não fixa a tag não recebe pré-lançamentos. A prova em um projeto real (uma calculadora em Go) foi aprovada.
- **1.0.0:** a primeira versão estável genérica. Chegou com um commit `fix` com o rodapé `Release-As: 1.0.0`, porque os commits `docs`, `chore` e `ci` desde o alpha não provocavam o PR de release.
- **2.0.0:** o SDLC verificável (Gherkin, sensor, teste de aceitação antes do código e conferência na revisão). Veja o [guia de migração](migracao.md).

A configuração do release-please ainda traz `versioning: "prerelease"` e `prerelease-type: "alpha.1"`: a primeira foi mantida até a tag `v1.0.0` existir, porque sem ela o bot proporia versões alpha a partir de um alpha. Depois da tag, as duas chaves podem sair, com o teste de `tests/release/` ajustado.
