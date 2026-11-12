# Design

## Context

O pacote tem a fonte em `.apm/` e é entregue pelo APM aos hosts `claude` e `copilot`. O próprio repositório consome a fonte local (`apm install --target claude,copilot`, feito na Onda 0), então `.claude/`, `.agents/`, `.github/agents`, `.github/prompts` e `apm.lock.yaml` são cópias derivadas da fonte e hoje carregam o cowboy. Levantamento da fonte (322 ocorrências em 19 arquivos): 5 agentes, 7 prompts, 3 skills, `scripts/git-hooks/pre-commit`, `_pending/instructions/cowboy.instructions.md`, `templates/HARNESS_QUADRANTE.md` e 4 linhas da skill `openspec-workflow`. As skills `harness`, `install-dev-harness`, `dev-harness-architect`, `harness-quadrant-process`, `architecture-fitness-functions` e `skill-retrospective`, os hooks Python e o `phase_cli.py` não citam o cowboy. A skill `harness-quadrant-process` já traz um modelo neutro em `references/quadrant-doc-template.md`.

## Goals / Non-Goals

**Goals:**
- Fonte e implantação sem nenhum dos quatro termos (cowboy, cobol, cobc, calculadora), verificável por uma busca.
- Remoção em uma change só, para o histórico mostrar o antes e o depois.

**Non-Goals:**
- Criar o hook genérico de Stop, o pre-commit genérico ou os agentes `sdlc-*`: são F2 e F3.
- Mudar a versão ou o release-please: a versão é do bot, e o pré-lançamento tem change própria.
- Criar um teste automático permanente contra os termos: o sensor anti-fantasma é da Onda 2.

## Decisions

1. **Apagar, não mover.** O conteúdo sai sem cópia em outro lugar. A tag `v0.3.1` guarda o estado antigo, e o aviso de migração aponta para ela. Alternativa descartada: mover para uma pasta `legacy/` ou um repositório do cowboy, porque manteria os termos no pacote e contraria a Decisão 1 da spec.
2. **Apagar também o pre-commit.** Ele só roda `tests/fitness` e `cobc`, que não existem aqui. O substituto genérico, que lê o `harness.config.json`, chega na F2. Alternativa descartada: reescrever o script agora, que anteciparia a F2 e misturaria duas funcionalidades.
3. **`HARNESS_QUADRANTE.md` vira cópia do modelo neutro da skill.** O conteúdo passa a ser o de `harness-quadrant-process/references/quadrant-doc-template.md`. A duplicação é aceita porque o arquivo em `templates/` é o que o consumidor recebe. Alternativa descartada: apagar o arquivo, que quebraria a spec e o layout documentado no README.
4. **`openspec-workflow` ganha exemplos sem stack.** Trocar "variáveis COBOL em Working-Storage" por uma frase genérica, "Fase 4 - Generate (Implementação)", e as tasks 4.1 a 4.3 por tasks que citam "o comando de sensores do projeto". Nenhum comando de um projeto específico entra no texto.
5. **`apm.yml`: nome `apm`, descrição genérica, versão intocada.** O nome `harness` não descreve mais o pacote (Lean Inception, Harness e SDLC). A linha `version` e a marcação do release-please não mudam. Alternativa descartada: manter `harness`, que deixaria o nome menor que o escopo.
6. **Reimplantar depois de apagar.** Rodar `apm install --target claude,copilot` e conferir se o APM remove as cópias órfãs e limpa o lockfile. Se não remover, usar `apm prune` e, em último caso, apagar à mão só os arquivos listados no lockfile.
7. **`.harness/` no `.gitignore`.** O estado de fase (`change-phase.json`) é de cada sessão e não deve ir para o git.

## Risks / Trade-offs

- [Consumidores da 0.3.x perdem agentes e prompts ao trocar de tag] → o aviso de migração no README e a tag `v0.3.1` preservada; a change fica marcada como **BREAKING**.
- [O release-please propõe `1.0.0` ao mesclar esta change antes da configuração de pré-lançamento] → não mesclar o PR de release até a change do pré-lançamento entrar; o PR de release é recalculado a cada push na `main`.
- [Sem pre-commit e sem hook de Stop até a F2, o repositório fica sem sensor de encerramento] → aceitável: não há versão publicada sem o cowboy ainda, e o `harness.config.json` sem comando de sensores já permite o encerramento.
- [A busca pelos termos pode pegar palavras legítimas, como "calculadora" em exemplos futuros] → a busca é o critério da spec; exemplos futuros devem evitar esses termos no pacote.
- [`apm install` pode deixar órfãos em `.claude/` ou `.agents/`] → a verificação final busca nos diretórios implantados, e não só na fonte.

## Migration Plan

1. Remover e neutralizar na fonte (`.apm/`, `apm.yml`, `README.md`).
2. Reimplantar e conferir `.claude/`, `.agents/`, `.github/` e o lockfile.
3. Abrir um PR com título `feat!: …`; a mesclagem e o PR de release continuam sendo atos do Elói.
4. Rollback: reverter o PR ou apontar o consumidor para `v0.3.1`.
