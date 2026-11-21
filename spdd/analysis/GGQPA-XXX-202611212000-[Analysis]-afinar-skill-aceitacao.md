# SPDD Analysis: Afinar o skill acceptance-from-spec (F5, follow-up das provas)

## Original Business Requirement

Follow-up das provas da F3 e da revisão da F4, **fora da spec V2.0** (decisão do Emiliano). Não li a V2.0 no Drive e esta change não depende dela. Pedido (sessão principal): afinar o skill `acceptance-from-spec` fechando seis atritos observados; só adições e esclarecimentos; stack-agnóstico (o skill não nomeia ferramenta de teste; há testes de neutralidade em `tests/agents`).

Atritos: (1) vermelho por erro do ambiente (falso verde); (2) `#### Scenario:` extras sem anotação que evite `ORFAO`; (3) fixture com linha `Spec:` em string vira `ORFAO`; (4) cenário de comportamento do modelo que só prova humana cobre; (5) skill x tasks do planner divergentes; (6) cenário herdado em `MODIFIED`.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Skill `acceptance-from-spec`** (97 linhas, v1.0): passos 1 a 8, `Spec:` literal, vermelho/verde, ramo sem framework. Teste de proteção `tests/agents/test_acceptance_skill.py` (`REQUIRED`, `MAX_LINES = 150`, neutralidade, cópias idênticas, coder cita o skill).
- **`spec-trace.py`** (F4): reconhece só linha com `Spec:` e dois ou mais ` / `; herdado é informativo; `#### Scenario:` extra só entra em `extras: N`; varre o fonte dos testes.
- **`sdlc-coder`** (63 linhas) e **`sdlc-planner`** (93 linhas): limite do teste de contrato de 300 linhas por corpo; `STACK_TERMS` proíbe termos de stack.
- **Reviewer da F4**: trata `SEM_TESTE` como alta e `REPROVADO`; extras sem teste como baixa; órfão em fixture é descartado ao ler.
- **Prova humana**: precedente de dois `SEM_TESTE` conhecidos em `sdlc-agent-roles` (decisão do Elói na F4).

### New Concepts Required
- **Falso verde de aceitação**: teste que passa sem o programa porque o ambiente falhou de um jeito que o teste aceita (código de saída genérico).
- **Anotação `Extra:`**: rótulo, com a trinca, para o `#### Scenario:` extra que ganhou teste; nunca `Spec:`.
- **Fixture por constante**: a linha `Spec:` de exemplo é montada em tempo de execução.
- **Pendente de prova humana**: estado de relatório do cenário de comportamento do modelo (`SEM_TESTE` conhecido com decisão do humano).
- **Seção "Cenários só de prova humana"** em `design.md`, mais a task de prova.

### Key Business Rules
- Um teste por `Cenário:` do bloco; extra só com comportamento distinto, anotado `Extra:`.
- Só cenário novo ou alterado é exigido; herdado é informativo.
- O vermelho vem da asserção do `Então`, ou, em linguagem compilada, de símbolo de produção ausente declarado; erro do ambiente não conta.
- Não existe teste que finge cobrir comportamento do modelo.
- Só adições; sem nome de ferramenta; skill dentro de 150 linhas.

## Strategic Approach

### Solution Direction
O texto normativo mora no skill (fonte única). O coder só aponta; o planner recebe a regra das tasks e a seção de prova humana. Nenhum script, hook, reviewer ou configuração muda. O reviewer da F4 e o `spec-trace` já aceitam as convenções (ignoram `Extra:`; herdado informativo).

### Key Design Decisions
- **`Extra:` como rótulo irmão de `Spec:`** → zero código, zero `ORFAO`; custo: sem conferência mecânica.
- **Fixture por constante** → sem tocar no `spec-trace` (o teste atual já usa `TAG`).
- **Falso verde com duas defesas** (rodar antes de existir o programa; afirmar o conteúdo).
- **Prova humana** como pendente registrado, sem teste fingido; o reviewer não muda e a decisão vai no brief.
- **Manter `MAX_LINES = 150`**: ~116 linhas projetadas.
- **Testes em tabela, linha `Spec:` por método**, e dois testes de caracterização com o `spec-trace` real.

### Alternatives Considered
- **Só no skill**: rejeitada (o planner gera as tasks; sem ele o atrito 5 volta).
- **Ensinar o `spec-trace` a ler `Extra:` e ignorar fixtures**: rejeitada nesta change (mexe em script; change própria).
- **Subir o teto ou criar `references/`**: rejeitada (sem necessidade; implantação de `references/` não provada).
- **Teste "leve" para cobrir o cenário de comportamento do modelo**: rejeitada (finge cobertura; é o que o ajuste 4 proíbe).
- **Reviewer aceitar a decisão registrada em `design.md`**: adiada.

## Risk & Gap Analysis

### Requirement Ambiguities
- "Quanto cabe": teto do teste (150) vs conforto do skill; assumido manter o teto (Q7).
- Convenção do extra (Q2) e tratamento da prova humana pelo reviewer (Q4) não estão no pedido; assumidas as recomendações.
- Tipo de commit (Q9) e limite de PR (Q10) não informados.
- Fonte V2.0 não lida; irrelevante para esta change.

### Edge Cases
- **Extra sem comportamento distinto**: não ganha teste.
- **Cenário herdado cujo comportamento a Operation muda**: a spec o altera, vira exigido.
- **Linguagem compilada**: símbolo ausente declarado é vermelho válido; erro de sintaxe não.
- **Teste que passa antes do programa por motivo legítimo** (funcionalidade já existe): já coberto pelo skill; o falso verde cobre só o caso do ambiente.
- **`Extra:` esquecido**: o reviewer vê extra sem teste como baixa.
- **Fixture que o próprio projeto escaneia**: a linha literal vira `ORFAO`; por constante, não.

### Technical Risks
- **Comportamento do modelo** não se prova por teste estático (6.4).
- **Teste de README e de cópias dependem da sessão principal** (README, `apm install`): ficam vermelhos até lá; ordem das tasks trata isso.
- **Testes de caracterização sem vermelho natural**: declarados.
- **Skill mais longo**: ~116 linhas; teto 150 protege.
- **Termos de stack** em prosa nova (`pip`, `make`, `node`, `python`): `STACK_TERMS` pega.
- **PR empilhado sobre a F4** (#38 aberto): ordem de merge.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | Vermelho pela asserção, falso verde | Yes (texto) / Partial (modelo) | Texto testado; uso real na 6.4 |
| 2 | Convenção do extra sem `ORFAO` | Yes | Texto + `spec-trace` real (caracterização) |
| 3 | Fixture por constante | Yes | Texto + lint do próprio fonte do teste |
| 4 | Prova humana sem teste fingido | Yes (texto) / Partial (modelo) | 2 cenários `SEM_TESTE` conhecidos |
| 5 | Skill x tasks alinhados | Yes | Skill, planner e testes de contrato |
| 6 | Herdado informativo | Yes | Texto; alinha com o `spec-trace` |
| 7 | Neutralidade e teto | Yes | `STACK_TERMS`, `MAX_LINES`, grep de origem |
| 8 | Só adições | Yes | `REQUIRED` antigo continua verde |
