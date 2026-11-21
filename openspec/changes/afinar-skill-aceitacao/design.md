# Design

## Context

O skill `acceptance-from-spec` (97 linhas; teto do teste `MAX_LINES = 150`) e o `sdlc-coder` entregam o ciclo teste-primeiro por `Cenário:`. O `spec-trace.py` (F4) confere o vínculo e já trata o cenário herdado como informativo e o `#### Scenario:` extra como "não exigido" (só conta em `extras: N`). Seis atritos vieram das provas e da F4 (ver `proposal.md`). Todos se resolvem com texto: nenhum exige mudar script, hook, `harness.config.json` ou o reviewer.

Dois fatos do código moldam o desenho:

- O `spec-trace` só reconhece linha com `Spec:` e ao menos dois ` / `. Uma linha que comece por outro rótulo (`Extra:`) nunca vira `ORFAO`; é por isso que o extra pode ser anotado sem tocar no script.
- O `spec-trace` varre o fonte dos testes: uma fixture com a linha `Spec:` literal numa string é lida como marcador. Montar a linha por constante tira a linha literal do fonte (o teste atual já usa `TAG = "Spec"`).

Não li a V2.0 no Drive; esta change é follow-up das provas e não depende dela.

## Goals / Non-Goals

**Goals:**
- Fechar os seis atritos com texto, só por adição ou esclarecimento.
- Manter o skill dentro do teto do teste, sem termo de stack nem de origem.
- Alinhar skill, coder e planner numa regra só: um teste por `Cenário:` do bloco.

**Non-Goals:**
- Mudar `spec-trace.py`, reviewer, hooks, `harness.config.json` ou specs já arquivadas.
- Provar o comportamento do modelo por teste; criar `references/` no skill; fixar framework.

## Decisions

1. **Onde cada ajuste entra (Q1).** O texto normativo mora no **skill** (fonte única): ajustes 1 a 4 e 6. O **coder** só aponta (um parágrafo no Entregável, sem copiar o skill). O **planner** recebe só o que lhe cabe, a regra das tasks (ajuste 5) e a seção "Cenários só de prova humana" (ajuste 4 visto do planejamento). O reviewer não muda.
2. **Texto-alvo no skill (aditivo; as frases entre aspas são os trechos que os testes procuram):**
   - **Passo 1** (+~5 linhas): em requisito `MODIFIED`, o cenário idêntico ao da spec principal é *herdado*: "não precisa de teste novo" e vai no relatório como "informativo"; novo ou de passos alterados é exigido. O `#### Scenario:` extra que ganhar teste leva `Extra: <capability> / <requisito> / <título do #### Scenario>`, "nunca `Spec:`" (senão o `spec-trace` aponta `ORFAO`).
   - **Passo 4** (+~3 linhas): fixture ou exemplo de teste que precise de uma linha `Spec:` com três campos: monte "por constante" (rótulo concatenado em tempo de execução); a linha literal no fonte aparece como `ORFAO`.
   - **Passo 5** (+~5 linhas): o vermelho vem da asserção do `Então` (conteúdo da saída ou efeito observável); "erro do ambiente" (arquivo, módulo ou comando ausente, "código de saída" genérico) não é vermelho. Teste que passa com o programa ausente é "falso verde": rode-o antes de o programa existir ou afirme o "conteúdo", não só o código de saída. Em linguagem compilada, símbolo de produção ausente declarado vale.
   - **Passo 8** (+~6 linhas): cenário cujo comportamento é do modelo e só "prova humana" cobre: relate pendente "prova humana" (`SEM_TESTE` conhecido) com a "decisão do humano"; não crie teste que finja cobri-lo nem o ligue por `Spec:`. O relatório lista à parte: extras anotados, herdados e provas humanas.
   - Frontmatter: `version: "1.1"`. Total estimado: 97 + ~19 = ~116 linhas (teto 150; sobram ~34).
3. **Convenção do extra (Q2): `Extra:`.** Mesma forma da trinca, rótulo diferente, comentário, nome ou rótulo do teste. Mecanicamente inofensiva (o `spec-trace` ignora), sem custo de código. Não é conferida por script: se o coder esquecer, o reviewer só vê o extra sem teste como baixa (regra da F4).
4. **Regra única skill x tasks (Q5).** "Um teste por `Cenário:` do bloco" é a regra; o `#### Scenario:` extra só ganha teste se descrever comportamento observável distinto, e então com `Extra:`. O planner gera as tasks de teste assim; a F1 já obriga o título do bloco a igualar um `#### Scenario:`, então a divergência vinha só das tasks.
5. **Prova humana (Q4).** O cenário de comportamento do modelo continua `SEM_TESTE` para o `spec-trace` e, portanto, `REPROVADO` mecânico para o reviewer. A convenção tira a ambiguidade do coder (não finge teste) e dá ao planner um lugar para a decisão (`design.md`, seção "Cenários só de prova humana", com a task de prova). A decisão do humano precisa ir no brief da revisão; o reviewer não é alterado nesta change (ver Q4).
6. **Falso verde (Q3).** Duas defesas complementares no passo 5: conferir antes (rodar sem o programa) e afirmar o conteúdo. A segunda é a que sobrevive no teste para sempre; a primeira só prova no momento. O relatório já carrega o motivo do vermelho (F3), então o reviewer da F4 compara.
7. **Testes (teste primeiro, vermelho natural).** `tests/agents/test_acceptance_skill.py` ganha uma classe `AfinacaoDoSkillTest` (um método curto por cenário, com a linha `Spec:` em comentário e um auxiliar que confere uma tabela de trechos), testes de coder, de planner e de README. `tests/agents/test_contract.py` ganha tabelas de trechos do coder e do planner e a ligação `Spec:` dos testes de texto. Vermelho natural: os trechos novos não existem. Os testes dos extras que usam o `spec-trace.py` real (processo, projeto temporário, linha `Spec:` montada por constante) já passam antes da edição porque o script já ignora `Extra:`; são **caracterização**: o relatório do coder deve dizer isso em vez de fingir vermelho (a parte de texto do mesmo teste é que fica vermelha).
8. **Cópias.** Depois de editar a fonte, `apm install --target claude,copilot` (sessão principal) refaz as cópias do skill e dos agentes; até lá, os testes de cópia idêntica ficam vermelhos.

## Decisões em aberto (do humano)

Assumidas as recomendações nos artefatos; "Decisões do humano" fica vazia até a aprovação.

**Decisões do humano (Emiliano):** plano aprovado com Q1 a Q11 como recomendadas. Os dois cenários de `sdlc-agent-roles` que só prova humana cobre ("Coder real aplica as convenções" e "Planner real gera tasks coerentes") ficam `SEM_TESTE` conhecidos, cobertos pela task 6.4; o `spec-trace` sai 2 nesta change por isso, e o PR deve citar a decisão.

- **Q1. Onde entra cada ajuste.** Recomendação: skill como fonte do texto; coder aponta; planner recebe a regra das tasks. Custo: ~19 linhas no skill, ~4 no coder, ~7 no planner. Risco: texto duplicado entre skill e agentes divergir (mitigado: o agente cita, não copia). Alternativa: só no skill (o planner continuaria gerando tasks por `#### Scenario:`, o atrito 5 voltaria).
- **Q2. Convenção do extra.** Recomendação: `Extra: <capability> / <requisito> / <título do #### Scenario>`. Custo: nenhum no script. Risco: o vínculo do extra não é conferido mecanicamente. Alternativa: ensinar o `spec-trace` a conferir `Extra:` (script + testes, change própria) ou nenhum marcador no extra (o extra com teste fica invisível ao reviewer).
- **Q3. Falso verde.** Recomendação: exigir o vermelho pela asserção, tratar o teste que passa sem o programa como falso verde e reforçar afirmando o conteúdo. Custo: ~5 linhas. Risco: o coder pode dizer que conferiu sem conferir (só a prova real mostra). Alternativa: só "afirme o conteúdo" (mais curto, menos prova no ato).
- **Q4. Prova humana e o reviewer.** Recomendação: o skill registra `SEM_TESTE` conhecido com a decisão do humano; o reviewer **não muda**, e a sessão principal leva a decisão no brief. Risco: sem o brief o reviewer reprova (comportamento da F4, já aceito com os 2 `SEM_TESTE` de `sdlc-agent-roles`). Alternativa: uma linha no reviewer para aceitar a decisão registrada em `design.md` (fora do pedido; change própria).
- **Q5. Regra skill x tasks.** Recomendação: um teste por `Cenário:` do bloco; extras só se distintos. Alternativa: cobrir todos os `#### Scenario:` (mais testes, ruído, contra a F4).
- **Q6. Herdado.** Recomendação: sem teste novo; se a Operation mudar o comportamento do herdado, a spec já o altera e ele passa a exigido. Risco: herdado nunca testado continua assim (visível como informativo; retrofit é change própria).
- **Q7. Tamanho.** Recomendação: manter `MAX_LINES = 150`; o skill chega a ~116. Alternativa: subir o teto para 180 ou mover detalhes para uma pasta `references/` (não provada como implantada pelo `apm install`; risco). O teto só sobe com decisão sua.
- **Q8. Versão do skill.** Recomendação: `version: "1.1"` (só adição). Alternativa: manter `1.0`. Sem custo.
- **Q9. Tipo de commit.** Recomendação: `feat(agents):` (minor, muda a rotina do coder e do planner). Alternativa: `fix(agents):` (patch). A decisão é sua porque o PR de release escolhe a versão.
- **Q10. Tamanho do PR.** Texto ~31 linhas, testes ~150. Limite de PR não informado; um PR só é razoável (~180 linhas). Se o limite for ~200 linhas, cabe; se menor, dividir em (1) skill + testes do skill, (2) coder e planner + testes de contrato.
- **Q11. Prova humana desta change.** Recomendação: repetir a prova do ramo sem framework com o coder real (um cenário só de prova humana e um extra) e uma disparo do planner real; registrar no roteiro. O que não for executado, "não verificado".

### Cenários só de prova humana

Estes dois cenários descrevem o comportamento do modelo real e ficam `SEM_TESTE` conhecidos (decisão a confirmar pelo Emiliano, Q4); cobre-os a task de prova humana (6.4):

- `sdlc-agent-roles / Coder aplica as convenções afinadas do skill / Coder real aplica as convenções`
- `sdlc-agent-roles / Planner gera tasks coerentes com o skill / Planner real gera tasks coerentes`

Por isso o `spec-trace` sai 2 nesta change até a decisão ser registrada; o texto dos agentes é coberto pelos outros dois cenários desses requisitos.

### Ações do humano fora do código

- Depois do apply: `apm install --target claude,copilot` e `claude plugin validate .claude/agents` (sessão principal), conferir `diff` das cópias.
- README, CHANGELOG, `docs/roteiro-de-teste.md`: escritos pela sessão principal (fora de `code_prefixes`).
- Disparar o coder e o planner reais para a prova (6.4); push, PR (depois do #38) e mesclagem são do Elói; arquivar e retrospectiva depois do merge.

## Risks / Trade-offs

- [Comportamento do modelo só se prova num projeto] → testes provam o texto e a implantação; 6.4 é a prova real, registrada como "não verificado" se não rodar.
- [O README é exigido por teste e mora fora de `code_prefixes`] → o teste do README só fica verde depois da task 4.1 (sessão principal); o coder o relata como pendente, não o contorna.
- [Cópias idênticas ficam vermelhas até o `apm install`] → ordem das tasks: 4 e 5 antes da integração 6.
- [Testes de caracterização não têm vermelho natural] → declarados como tais no relatório.
- [Texto novo estoura o teto ou introduz termo de stack] → o teste de tamanho (150) e `STACK_TERMS` já existem e rodam em `unittest discover`; cuidado com palavras como "pip", "make" e "node" no texto.
- [Skill mais longo dilui o que já funciona] → só ~19 linhas; os trechos antigos são conferidos por teste (`REQUIRED` antigo continua verde).

## Migration Plan

1. Testes vermelhos (task 1).
2. Skill, coder, planner (tasks 2 e 3).
3. Sessão principal: README, `apm install`, cópias (tasks 4 e 5).
4. Integração e prova humana (task 6).
