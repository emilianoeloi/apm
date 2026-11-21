# SPDD Analysis: Reviewer confere cenário contra teste (F4 da V2.0)

## Original Business Requirement

Fonte: especificação APM_SETUP_V2.0 (Google Drive). **Não li o arquivo** (sem conector do Drive nesta sessão); os trechos vêm do pedido da sessão principal. Se o texto original diferir, vale o original.

> "Dado o sdlc-reviewer, quando revisa, então confere que cada cenário tem teste." Jornada, passo 5: "O sdlc-reviewer confere que cada cenário tem teste."
>
> Restrições: só adições; sem perfis de SDLC; sem revisão cruzada entre modelos; stack-agnóstico (sem nomear ferramenta de teste); o reviewer é SOMENTE LEITURA (tools Read, Grep, Glob, Bash; não escreve arquivos). Onda 2; esforço P, valor $$, confiança verde.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Bloco Gherkin por requisito** (F1) e **`_gherkin.py`** (F2): `effective_requirements`, `parse_delta`, `parse_requirements`, `validate`. O sensor confere só o formato; **não lê testes**.
- **Convenção `Spec:`** (F3, skill `acceptance-from-spec`): linha literal `Spec: <capability> / <requisito> / <cenário>` em comentário, nome ou rótulo do teste; um teste por `Cenário:` do bloco.
- **`sdlc-reviewer`**: só lê; roda `openspec validate`, sensores, confere escopo; relatório com veredito e achados (arquivo, linha, Operation); `git status --porcelain` igual ao final.
- **Implantação por host**: scripts de `.apm/hooks/scripts/` copiados para `.claude/hooks/apm/.apm/hooks/scripts/` e `.github/hooks/scripts/apm/.apm/hooks/scripts/`.
- **Achados das provas** (`docs/roteiro-de-teste.md`): cenário herdado de requisito modificado ficou sem `Spec:`; skill (um teste por `Cenário:`) e planner (todos os `#### Scenario:`) divergem; subteste de Go troca espaço por `_`; teste passou de primeira por erro do ambiente; sensor sai 0 sem `Spec:`.

### New Concepts Required
- **Vínculo cenário-teste conferido**: estados `COBERTO`, `SEM_TESTE`, `HERDADO_SEM_TESTE`, `ORFAO`, `AMBIGUO`.
- **Cenário exigido**: novo ou alterado pela change (vs herdado, idêntico à spec principal).
- **Script `spec-trace.py`** só-leitura e `_gherkin.parse_scenarios`.
- **Falso verde**: teste ligado que não afirma o `Então` ou passaria sem o código.
- Seção do relatório **"Cenários x testes"** e regras de severidade e veredito.

### Key Business Rules
- Cada cenário novo/alterado precisa de teste ligado por `Spec:`; sem ele, severidade alta e `REPROVADO`.
- Herdado sem teste é informativo.
- O reviewer nunca escreve (nem `__pycache__`); stack-agnóstico; só adições.
- O vínculo textual prova a ligação, não a qualidade do teste: a qualidade é conferida por leitura.

## Strategic Approach

### Solution Direction
Dois níveis. O **mecânico** (listar cenários exigidos, comparar com a spec principal, casar a trinca com linhas de teste) vira script determinístico reaproveitando `_gherkin`, achado por `Glob` em qualquer host. O **julgamento** (o teste afirma o `Então`? cobre sem marcador?) fica no agente, por leitura. Sem o script, o agente repete o mecânico com `grep -F`. O script não é hook nem sensor: roda só na revisão.

### Key Design Decisions
- **Script + reserva em prosa** → determinismo para a parte que exige comparar spec principal e delta, sem prender o agente a um caminho de host.
- **Exigir só novo/alterado** → evita o atrito da prova; herdado visível como informativo.
- **Um teste por `Cenário:` do bloco**; `#### Scenario:` extras não exigidos (só contados).
- **Prefixo mais longo** casa a trinca, tolerando fechamento de comentário; colisão exata = `AMBIGUO`; linha com `Spec:` sem casamento = `ORFAO`.
- **`dont_write_bytecode` antes do import** → o reviewer mantém o `git status` igual.
- **grep no fonte**, nunca na saída verbosa do executor (subteste de Go).
- **Fora do `harness.json` e do `sensors_command`** → não quebra o Stop em `proposal` nem pune cenário antigo.

### Alternatives Considered
- **Só prosa**: rejeitada como única via (muitos `grep`, erro na lista de herdados/alterados); mantida como reserva.
- **Script como sensor do Stop/pre-commit**: rejeitado (roda em `proposal`, sem testes ainda).
- **Exigir todo cenário do requisito tocado**: rejeitado (obriga ligar testes antigos; atrito da prova).
- **Mutação para provar teste fraco**: rejeitada (o reviewer não escreve).
- **Modo `--all`**: adiado (retrofit de projetos antigos, change própria).
- **Pasta `.apm/scripts/` nova**: rejeitada (implantação não provada).

## Risk & Gap Analysis

### Requirement Ambiguities
- "Cada cenário": interpretado como `Cenário:` de requisito `ADDED`/`MODIFIED` novo ou alterado da change em revisão (Q2).
- "Tem teste": linha `Spec:` num arquivo de teste mais leitura que confirma a afirmação do `Então` (Q8).
- Severidade e efeito no veredito não estão no texto V2.0 (Q4).
- Fonte V2.0 não lida (Q9).

### Edge Cases
- **Título que é prefixo de outro** no mesmo requisito: prefixo mais longo.
- **Nome com ` / `**: colisão de literal = `AMBIGUO`; sem colisão, o prefixo resolve.
- **Cenário renomeado/removido com teste antigo**: `ORFAO`.
- **`RENAMED`+`MODIFIED`**: base buscada pelo nome antigo.
- **Requisito `MODIFIED` sem base na principal**: tudo exigido.
- **Change sem `Cenário:`**: nada exigido; relata "nada a conferir".
- **`Spec:` em `.md` ou pasta excluída**: não conta.
- **Teste que cobre sem marcador**: média, com o arquivo.
- **Fixtures de teste com `Spec:`** (neste repositório): aparecem como `ORFAO`; o agente descarta ao ler.
- **`python3` ausente**: reserva em prosa.
- **Mais de uma change ativa**: sem `--change`, todas; com a opção, só uma.

### Technical Risks
- **Comportamento do modelo** não se prova por teste estático (prova real em projeto, task 6.4).
- **Casamento do script diverge da prosa**: teste compara os dois num caso.
- **Busca lenta em monorepo grande**: limite de 1 MiB e pastas excluídas.
- **`Spec:` em código de produção conta como ligação**: o agente confirma lendo.
- **Escritas fora de `code_prefixes`**: README, cópias implantadas, `apm.lock.yaml`, `CLAUDE.md` (sessão principal).
- **PR empilhado sobre a F3** (#33 a #36 abertos): ordem de merge.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | O reviewer confere que cada cenário tem teste | Yes (script) / Partial (agente) | Script determinístico prova o vínculo; o uso pelo modelo só em projeto real |
| 2 | Reviewer continua somente leitura | Yes | `tools` inalteradas, script sem escrita nem bytecode, teste de árvore intacta |
| 3 | Stack-agnóstico | Yes | `STACK_TERMS` e `grep` de neutralidade; vínculo é texto |
| 4 | Só adições, sem perfis, sem revisão cruzada | Yes | Nenhum hook/spec/agente removido |
| 5 | Cenário herdado tratado | Yes | Informativo, regra e teste |
| 6 | README: seção e aviso | Yes | Task da sessão principal |
