# SPDD Analysis: Pré-lançamento 1.0.0-alpha.1 no release-please

## Original Business Requirement

Fonte: `APM_SETUP_V1.2.md` (Google Drive), seção "Pré-lançamento 1.0.0-alpha.1" e o sequenciador da Onda 1, mais a change `openspec/changes/prelancamento-alpha/`. Trechos da spec, sem alteração:

> A calculadora roda sobre o pré-lançamento 1.0.0-alpha.1, e não sobre a 1.0.0 final. Motivo: a prova acontece antes de fechar a versão estável. A Onda 1 passa a publicar a 1.0.0-alpha.1, e a 1.0.0 sai depois da prova.
>
> Pré-lançamento 1.0.0-alpha.1: Os releases do apm saem pelo release-please, no GitHub Actions. A Onda 1 precisa gerar a tag v1.0.0-alpha.1, e não a v1.0.0. Como configurar o release-please para pré-lançamento: não informado. O Claude Code confere na documentação do release-please e propõe a mudança. Mesclar o PR de release continua sendo ato humano, do Elói. A 1.0.0 final só é publicada depois da prova da calculadora aprovada.
>
> Sequenciador: Onda 1 (MVP): F1, F2 e F3, publicadas como 1.0.0-alpha.1. A prova da calculadora em Go roda sobre a 1.0.0-alpha.1. A 1.0.0 final sai depois da prova aprovada. Toda onda fecha com CHANGELOG, README, roteiro de teste e retrospectiva de skills.
>
> Documentação: CHANGELOG do apm: é gerado pelo release-please; a seção 1.0.0 lista a remoção como incompatível.
>
> Cuidados: Nunca dar push sem o "ok" explícito do Elói.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Fluxo de release**: workflow `release-please.yml` (ação v5.0.0, que usa `release-please` `^17.6.0`) roda em todo push na `main` e abre ou atualiza um PR de release; mesclar esse PR cria a tag e o GitHub Release.
- **Configuração do release-please**: `release-please-config.json` (pacote `.`, tipo `simple`, `package-name: harness`, tag com `v` e sem componente, `extra-files: apm.yml`) e `.release-please-manifest.json` (`0.3.1`).
- **PR de release #12**: aberto, propõe `1.0.0` (por causa do commit incompatível da F1), com o `apm.yml` indo de `0.3.1` para `1.0.0`.
- **Convenção de commits**: títulos de PR em Conventional Commits, conferidos pelo workflow `pr-title`.
- **Tags `v*`**: protegidas contra apagar e mover.
- **Versão estável vigente**: `v0.3.1`.

### New Concepts Required
- **Pré-lançamento**: versão `1.0.0-alpha.N`, publicada como GitHub Release de pré-lançamento, que o consumidor só recebe apontando para a tag.
- **Saída do pré-lançamento**: a passagem de `1.0.0-alpha.N` para `1.0.0` por mudança de configuração, depois da prova.
- **Guarda da configuração de release**: teste do repositório que impede um `release-as` esquecido e confere as chaves do pré-lançamento.

### Key Business Rules
- **A tag publicada é `v1.0.0-alpha.1`, nunca `v1.0.0`, na Onda 1.**
- **A `1.0.0` final só depois da calculadora aprovada.**
- **Publicar é ato humano do Elói**: o bot só prepara o PR de release.
- **Tags não se apagam nem se movem**: um erro de versão seria definitivo, então a conferência vem antes de mesclar.
- **Sem push sem o "ok" do Elói.**
- **A versão no `apm.yml` e no manifesto andam juntas**, atualizadas pelo bot.

## Strategic Approach

### Solution Direction
Mudar só a configuração do release-please para a estratégia de versionamento `prerelease`, escolher o tipo de modo que o primeiro cálculo dê exatamente `1.0.0-alpha.1`, provar o cálculo com a própria biblioteca antes de depender dele, guardar a configuração com um teste e documentar o fluxo no README. Fluxo depois do merge: push na `main` → bot atualiza o PR #12 para `1.0.0-alpha.1` → conferência do título, do `apm.yml`, do manifesto e do CHANGELOG → o Elói mescla → tag `v1.0.0-alpha.1` e GitHub Release de pré-lançamento → fechamento da Onda 1.

### Key Design Decisions
- **`prerelease-type: "alpha.1"` em vez de `release-as`**: o tipo vira o primeiro sufixo (`1.0.0-alpha.1`) e os bumps seguintes incrementam o número; `release-as` trava a versão se ninguém o remover → adotar o tipo, e provar com a biblioteca.
- **Versão final por `prerelease: false`**: o código descarta o sufixo sozinho → uma linha de configuração, sem versão fixa.
- **Manter `package-name: harness`**: mudar renomearia a branch do bot e deixaria o #12 órfão → manter.
- **Teste de configuração no pacote**: guarda contra `release-as` pendente e contra a volta da versão estável → adotar.
- **Exemplo de consumo do README só muda depois da tag**: documentar uma tag inexistente induziria erro → adiar.

### Alternatives Considered
- **`prerelease-type: "alpha"`**: dá `1.0.0-alpha` na primeira vez, sem o `.1` da spec → rejeitada.
- **`release-as: "1.0.0-alpha.1"`**: documentada, mas exige remoção depois do release, senão toda proposta repete a versão → rejeitada.
- **Criar a tag à mão com `git tag`**: contorna o release-please, não gera o GitHub Release nem o CHANGELOG, e contraria o fluxo da spec → rejeitada.
- **Mesclar o PR #12 como está (`1.0.0`)**: publicaria a versão estável sem prova → rejeitada.

## Risk & Gap Analysis

### Requirement Ambiguities
- **Formato do número do pré-lançamento**: a spec fixa `1.0.0-alpha.1`; a numeração dos seguintes (`alpha.2`…) é decisão desta change.
- **Quando limpar `versioning` e `prerelease-type`**: depois da versão final; não bloqueia nada agora.
- **Quem conserta o README depois da tag**: a spec manda o fechamento da onda registrar README e CHANGELOG; ficou como passo posterior.

### Edge Cases
- **PR #12 mesclado antes desta change**: publicaria `1.0.0`; mitigado pela ordem e pelo aviso reiterado.
- **Commit `ci` ou `chore` do próprio PR**: não altera a versão calculada, pois os commits incompatíveis anteriores já fixam o bump.
- **Mais commits entre o merge desta change e o do PR de release**: o número do pré-lançamento só sobe depois de existir uma tag `alpha`; antes dela, continua `alpha.1`.
- **`apm.yml` com sufixo de pré-lançamento**: a atualização da linha `version:` pelo `extra-files` não foi vista com sufixo; conferir no diff do PR de release.
- **Consumidor sem tag explícita**: pode receber o pré-lançamento se usar a `main`; o README avisa.

### Technical Risks
- **Comportamento do `alpha.1` como tipo, não documentado**: confirmado no código; a task de verificação o executa com a biblioteca.
- **Versão da biblioteca na ação (`^17.6.0`) difere da testada**: verificar o piso e a mais recente.
- **Erro de versão em tag protegida é irreversível**: conferir o PR de release antes do merge.
- **O bot não recalcular o #12**: o log do workflow mostra; nada é publicado sem o merge humano.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | A Onda 1 gera a tag `v1.0.0-alpha.1` e não a `v1.0.0` | Yes | Configuração mais prova com a biblioteca; a tag só nasce no merge humano do PR de release |
| 2 | Como configurar o release-please para pré-lançamento (era "não informado") | Yes | Documentação e código do release-please lidos; decisão registrada no design |
| 3 | Mesclar o PR de release é ato humano | Yes | O workflow não muda; teste confere que não há mesclagem automática |
| 4 | A `1.0.0` final só depois da prova aprovada | Yes | `prerelease: false` fica para depois; o teste guarda o estado atual |
| 5 | CHANGELOG com a seção 1.0.0 listando a remoção como incompatível | Partial | Gerado pelo release-please no PR de release; conferido antes do merge |
| 6 | Onda fecha com CHANGELOG, README, roteiro e retrospectiva | Partial | Depende da tag; fica como passo posterior documentado |
