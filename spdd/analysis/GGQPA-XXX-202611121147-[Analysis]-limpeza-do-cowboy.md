# SPDD Analysis: Limpeza do cowboy no pacote APM

## Original Business Requirement

Fonte: `APM_SETUP_V1.2.md` (Google Drive), funcionalidade F1 da Onda 1, mais a change `openspec/changes/limpeza-do-cowboy/`. Trechos da spec, sem alteração:

> Ideia em uma frase: tirar o cowboy do emilianoeloi/apm e deixar um pacote genérico com Lean Inception, Harness e SDLC, em skills e agentes, para qualquer stack.
>
> Decisão 1: o conteúdo COBOL é apagado, sem mover para o cowboy. Motivo: o cowboy é um experimento, e a tag v0.3.1 guarda o estado antigo.
> Decisão 2: ninguém usa os agentes COBOL, então a remoção é livre.
>
> F1. Limpeza do cowboy. Esforço P, valor $$$, confiança verde.
>
> H1. Como Elói, quero o pacote sem cowboy, para instalar em qualquer projeto.
> Dado o pacote 1.0.0-alpha.1, quando busco "cowboy", "cobol", "cobc" e "calculadora" em .apm/, então a busca volta vazia.
> Dado o pacote 1.0.0-alpha.1, quando listo .apm/agents e .apm/prompts, então não há arquivo cobol-*, readme-writer nem prompt da calculadora.
> Dado o apm.yml, quando leio nome e descrição, então eles não citam o cowboy.
> Dado o HARNESS_QUADRANTE.md, quando abro o arquivo, então ele é um modelo com campos a preencher.
>
> Diagnóstico (v0.3.1): os cinco agentes são do cowboy (cobol-vibecoder, cobol-planner, cobol-coder, cobol-reviewer e readme-writer). Sete prompts são do cowboy (criar-programa, implementar-soma, implementar-subtracao, implementar-log, testar-programa, atualizar-readme e manutencao-repositorio). Três skills são do cowboy (cobol-calculadora, vibe-coding-fundamentals e readme-manutencao). O .apm/scripts/git-hooks/pre-commit compila src/CALCULADORA.cbl com cobc. O .apm/templates/HARNESS_QUADRANTE.md é a análise preenchida do cowboy, não um modelo. O skill openspec-workflow usa exemplos COBOL nas linhas 69, 76, 95 e 96. O .apm/_pending/instructions/cowboy.instructions.md é um guia de COBOL. O apm.yml se chama "harness" e diz "extraído do projeto cowboy". O README chama o pacote de privado, mas ele é público.
>
> Documentação: README do apm: remover "privado" e "extraído do cowboy", e a nota pendente sobre hooks, se resolvida. README do apm: aviso de migração para quem usava a 0.3.x.
>
> Decisão 3: o hook cowboy.json também é apagado, já na Onda 0 (feito, PR #10).

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Fonte do pacote (`.apm/`)**: o conteúdo que o APM entrega aos consumidores — skills, agentes, prompts, scripts, templates. Hoje mistura conteúdo genérico (harness, OpenSpec, OpenSPDD) com conteúdo do cowboy.
- **Implantação local**: cópias derivadas da fonte em `.claude/`, `.agents/`, `.github/agents`, `.github/prompts`, mais o `apm.lock.yaml` que registra cada arquivo implantado. A Onda 0 criou isso a partir da fonte local.
- **Manifesto do pacote (`apm.yml`) e README**: a identidade pública do pacote (nome, descrição, modo de consumo).
- **Modelo do quadrante**: `templates/HARNESS_QUADRANTE.md`, hoje uma análise preenchida; a skill `harness-quadrant-process` já tem o modelo neutro em `references/quadrant-doc-template.md`.
- **Gate de fase do harness**: `harness.config.json`, hooks e `phase_cli.py`, que já são genéricos e não mudam.
- **Release automático**: release-please, que calcula a versão pelas mensagens de commit; um `!` vira alteração de versão maior.

### New Concepts Required
- **Aviso de migração**: seção do README que diz a quem usava a 0.3.x o que saiu e onde está o estado antigo (tag `v0.3.1`).
- **Critério de neutralidade**: a busca vazia pelos quatro termos, como definição verificável de "pacote sem cowboy" na fonte e na implantação.

### Key Business Rules
- **Apagar, não mover** (Decisão 1): nenhuma cópia do conteúdo removido fica no pacote; governa fonte e implantação.
- **Remoção livre** (Decisão 2): não há consumidores dos agentes COBOL, então não há período de depreciação.
- **Genérico mantido intacto**: as skills `harness`, `install-dev-harness`, `dev-harness-architect`, `harness-quadrant-process`, `architecture-fitness-functions`, `skill-retrospective`, os seis `openspec-*`, os cinco `spdd-*`, os seis `opsx-*`, os hooks Python e o `phase_cli.py` não podem ser alterados além do necessário (vendorizados nunca são editados à mão).
- **Versão é do bot**: nenhuma edição manual da versão no `apm.yml` nem no manifesto do release-please.
- **Sem push e sem publicação sem o "ok" do Elói.**

## Strategic Approach

### Solution Direction
Uma change só, em quatro movimentos: (1) remover da fonte o que é exclusivo do cowboy; (2) neutralizar o que fica (exemplos da skill de workflow, modelo do quadrante, manifesto e README, com aviso de migração); (3) reimplantar pelo `apm install` local e conferir que o deploy e o lockfile acompanham a fonte; (4) provar a neutralidade pela busca pelos quatro termos na fonte e nos diretórios implantados. Fluxo de dados: fonte `.apm/` → `apm install` → `.claude/`, `.agents/`, `.github/`, `apm.lock.yaml`.

### Key Design Decisions
- **Apagar o pre-commit também**: ele depende de `tests/fitness` e `cobc`; reescrevê-lo agora anteciparia a F2 → apagar e deixar o substituto para a F2.
- **Modelo do quadrante como cópia do modelo da skill**: duplica 94 linhas, mas o consumidor recebe o arquivo de `templates/` → copiar, em vez de apagar, porque a spec exige o arquivo como modelo.
- **Nome `apm` no manifesto**: `harness` ficou menor que o escopo (Lean Inception, Harness, SDLC) → renomear; a versão não é tocada.
- **Reimplantar na própria change**: sem isso, o repositório continua distribuindo COBOL em `.claude/` mesmo com a fonte limpa → incluir a reimplantação e a verificação nos diretórios implantados.
- **`.harness/` ignorado no git**: o estado de fase é por sessão → ignorar.

### Alternatives Considered
- **Mover o conteúdo para `legacy/` ou para o repositório do cowboy**: mantém os termos no pacote ou cria trabalho fora do escopo; contraria a Decisão 1.
- **Uma change por tipo de arquivo (agentes, prompts, skills)**: o gate de fase aceita uma change por vez e o resultado só faz sentido junto → rejeitada.
- **Teste automático permanente contra os termos**: valioso, mas é o sensor anti-fantasma da Onda 2 → fica fora.

## Risk & Gap Analysis

### Requirement Ambiguities
- **O aviso de migração fala do cowboy**: a busca da spec cobre só `.apm/`, então o README pode citar os itens removidos; a spec da change deixa isso explícito (exceção do aviso).
- **Nome do pacote**: a spec exige só que nome e descrição não citem o cowboy; o novo nome `apm` é decisão desta change e precisa do aceite do Elói na aprovação da proposta.
- **Versão da linha de consumo no README**: o exemplo usa `#v0.3.0`; o certo é a tag mais nova publicada. Usar a última tag existente (`v0.3.1`) e trocar na Onda 1 pela alpha.

### Edge Cases
- **Órfãos na implantação**: o `apm install` pode não apagar arquivos implantados cuja fonte sumiu; por isso a task de conferir `.claude/`, `.agents/` e `.github/`, com `apm prune` como recurso.
- **Palavra "calculadora" em texto legítimo futuro**: a busca vai acusar; vale como alarme, não como erro de design.
- **Skill vendorizada com a palavra**: nenhuma hoje; um novo `sync-vendor.py` poderia trazer algo e a busca pegaria.
- **Pasta `.apm/hooks/` já não existe**: o README ainda cita `.apm/hooks/*.json`; corrigir na task 2.4.

### Technical Risks
- **Release-please propõe 1.0.0 final**: a mensagem incompatível leva a versão maior. Mitigação: o PR de release só é mesclado depois da change de pré-lançamento; mesclar é ato humano.
- **Sem sensor de encerramento até a F2**: o repositório fica sem pre-commit e sem hook de Stop temporariamente; sem impacto para consumidores, pois não há versão publicada sem o cowboy.
- **Avisos do APM sobre frontmatter dos prompts** somem com a remoção; se continuarem, há outro arquivo problemático.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | Busca por cowboy, cobol, cobc, calculadora em `.apm/` volta vazia | Yes | Verificada na task 4.1; também nos diretórios implantados (3.2) |
| 2 | `.apm/agents` e `.apm/prompts` sem `cobol-*`, `readme-writer` e prompt da calculadora | Yes | `.apm/agents` fica vazio até a F3; esperado |
| 3 | `apm.yml` não cita o cowboy em nome e descrição | Yes | Nome novo `apm` precisa de aceite |
| 4 | `HARNESS_QUADRANTE.md` é modelo com campos a preencher | Yes | Cópia do modelo da skill |
| 5 | README sem "privado" e "extraído do cowboy" e com aviso de migração | Yes | Nota sobre hooks segue pendente até a F2 |
