# SPDD Analysis: Skill acceptance-from-spec (F3 da V2.0)

## Original Business Requirement

Fonte: especificação APM_SETUP_V2.0 (Google Drive, arquivo `APM_SETUP_V2.0.md`). **Não li o arquivo** (sem conector do Drive nesta sessão); os trechos vêm do pedido da sessão principal. Se o texto original diferir, vale o original.

> H3. Como Emiliano, quero testes de aceitação gerados da spec, para provar que o código cumpre a intenção.
> (1) Dado um cenário aprovado, quando o sdlc-coder entra em "apply", então cria primeiro o teste de aceitação, que falha.
> (2) Dado o código pronto, quando rodo os sensores, então o teste passa.
> (3) Dado um projeto sem framework de teste definido, quando o skill roda, então ele propõe a ferramenta e espera a aprovação do Emiliano.
>
> Arquitetura: skill `acceptance-from-spec` não fixa framework e usa o `sensors_command` do projeto; ferramenta de teste por stack é "não informado". Só adições; sem framework novo de testes; fluxo SDLC único; stack-agnóstico. Objetivos: toda funcionalidade tem ao menos um teste de aceitação ligado à spec; o teste falha antes do código e passa depois. README: seção "Testes de aceitação" e aviso de migração.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Bloco Gherkin por requisito** (F1, `spec-gherkin-scenarios`) e **sensor** (F2, `gherkin-sensor`, `_gherkin.effective_requirements`): garantem que todo requisito tem `Cenário:` com título igual a um `#### Scenario:`.
- **`sdlc-coder`**: fase `apply`, canvas aprovado, ferramenta `Skill`, escreve só em `code_prefixes`, seção "Evidência de TDD" (relatar o vermelho com comando e contagem). Não tem `AskUserQuestion`.
- **Skills públicos** em `.apm/skills/<nome>/SKILL.md`, implantados em `.claude/skills/` e `.agents/skills/`.
- **Contrato dos agentes** (`tests/agents/test_contract.py`): `STACK_TERMS`, skills citadas existem, `SKILLS_BY_ROLE`, cópias idênticas.
- **`sensors_command`** do `harness.config.json`: roda no Stop e no pre-commit; vazio por padrão nos projetos-alvo.

### New Concepts Required
- **Teste de aceitação ligado**: teste de projeto que prova um `Cenário:` e carrega a linha `Spec: <capability> / <requisito> / <cenário>`.
- **Ciclo vermelho-código-verde com evidência**: comando e contagem de falhas antes e depois, motivo do vermelho, sem stubs.
- **Descoberta de framework e parada**: ordem de busca; sem ferramenta, proposta e parada.
- **Skill `acceptance-from-spec`** e a edição do coder que o invoca.

### Key Business Rules
- Teste antes do código; vermelho provado; verde pelos sensores.
- Nenhum framework fixado; "não informado" por stack; o Emiliano aprova a ferramenta.
- Só adições, stack-agnóstico, sem perfis.
- Ligação teste-cenário conferível por texto (a F4 usa).

## Strategic Approach

### Solution Direction
Skill de instruções (sem script), citado pelo coder antes das Operations que realizam requisitos com cenário. A convenção `Spec:` dá o elo conferível. A ausência de framework vira uma parada com proposta devolvida pela sessão principal, já que o coder não pergunta ao humano. Um teste estático protege o texto do skill, a citação pelo coder e as cópias implantadas.

### Key Design Decisions
- **Skill em `.apm/skills/`, público**, sem helper de script (o caminho implantado varia por host) → o skill lê o markdown da spec.
- **Marcador `Spec:` em uma linha** → busca de texto simples para a F4.
- **Vermelho com evidência no relatório**, vermelho por símbolo ausente aceito se declarado; sem stubs.
- **Conferir que o `sensors_command` roda a aceitação** → evita o "verde vazio".
- **Parada sem framework devolve a proposta à sessão principal** → o coder não tem `AskUserQuestion`.

### Alternatives Considered
- **Script gerador de testes**: rejeitado (exige conhecer a stack).
- **Executar o `.feature` com runner de BDD**: rejeitado (framework novo, fora do escopo).
- **Fixar um framework por stack no skill**: rejeitado (contraria o pedido; "não informado").
- **Modo `--list-scenarios` no sensor da F2**: rejeitado por ora (caminho implantado instável).
- **Planner também invoca o skill**: adiado (Q3).

## Risk & Gap Analysis

### Requirement Ambiguities
- **"Cenário aprovado"**: interpretado como `Cenário:` dos requisitos `ADDED`/`MODIFIED` da change cujo canvas foi aprovado.
- **"Falha" antes do código**: assertiva falha ou símbolo ausente; em stacks compiladas só existe o segundo sem stubs (Q5).
- **"Espera a aprovação"**: como o coder não pergunta, a espera é uma parada com relatório (Q6).
- **"Usa o `sensors_command`"**: o comando pode não rodar a aceitação; o skill confere e relata.
- **Fonte V2.0 não lida**.

### Edge Cases
- **Teste verde já no primeiro run**: relatar, não seguir em silêncio.
- **Fontes em conflito sobre o framework** (arquivo raiz x testes existentes): parar e reportar.
- **Cenário já coberto por teste existente**: ligar com a linha `Spec:` em vez de duplicar, ainda provando o vermelho quando a Operation muda comportamento.
- **Título de cenário com ` / `**: marcador ambíguo (Q1).
- **`sensors_command` vazio**: "sensores não configurados".
- **Operation sem comportamento observável** (documentação, configuração): sem cenário, sem teste de aceitação; o coder registra "sem cenário aplicável".

### Technical Risks
- **Comportamento do modelo não provável estaticamente** (confiança amarela): teste prova só o texto; prova real em projeto de prova (task 6.4).
- **Texto abstrato demais**: mitigado com passos concretos de relatório.
- **Escritas fora de `code_prefixes`**: README, cópias implantadas, `apm.lock.yaml`, `CLAUDE.md` ficam com a sessão principal.
- **Divergência entre cópias implantadas**: teste de cópias idênticas.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | Em apply, o coder cria primeiro o teste, que falha | Partial | Texto do skill e do coder protegido por teste; comportamento provado só em projeto real |
| 2 | Código pronto: sensores passam o teste | Partial | Depende de o `sensors_command` rodar a aceitação; o skill confere e relata a lacuna |
| 3 | Sem framework: propõe e espera aprovação | Partial | Parada com proposta devolvida à sessão principal; aprovação é humana |
| 4 | Ao menos um teste ligado por funcionalidade | Yes | Convenção `Spec:`; conferência automática na F4 |
| 5 | Só adições, sem framework novo, stack-agnóstico | Yes | `STACK_TERMS` e `grep` de neutralidade no skill e no coder |
| 6 | README: seção e aviso de migração | Yes | Task da sessão principal |
