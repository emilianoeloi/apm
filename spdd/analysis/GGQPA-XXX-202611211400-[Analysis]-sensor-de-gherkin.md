# SPDD Analysis: Sensor de Gherkin (F2 da V2.0)

## Original Business Requirement

Fonte: especificação APM_SETUP_V2.0 (Google Drive), funcionalidade F2. **Não li o arquivo do Drive**; os trechos vêm do pedido da sessão principal. Se o texto original diferir, vale o original.

> H2. Como Emiliano, quero um sensor de Gherkin, para saber quando falta cenário.
> Dado um requisito sem cenário, quando o sensor de Gherkin roda, então ele falha e cita o requisito.
> Dado todos os requisitos com cenário, quando o sensor roda, então ele passa.
> Dado o `openspec validate --strict`, quando ele roda, então o sensor de Gherkin roda junto.
>
> Arquitetura: script Python, só biblioteca padrão, ao lado dos hooks atuais (`.apm/hooks/scripts/`), junto do `openspec validate --strict`. Restrições: só adições; sem framework novo; stack-agnóstico; saída 0 ou 2 como os outros sensores, citando capability e nome do requisito; sem push.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Formato do bloco** (F1, spec `spec-gherkin-scenarios`): fence `gherkin` depois do parágrafo normativo e antes do primeiro `#### Scenario:`, `Cenário:`/`Dado`/`Quando`/`Então`, título igual ao de um `#### Scenario:`.
- **Leitor e validador da F1**: `parse_requirements`, `parse_delta`, `effective_requirements`, `validate` em `tests/specs/test_gherkin_blocks.py`, presos a constantes do repo.
- **Hooks do pacote**: scripts stdlib em `.apm/hooks/scripts/`, helper `_common.py` (`project_root`, `load_config`, `run` fail-open), registro em `.apm/hooks/harness.json` com `${PLUGIN_ROOT}`; teste de contrato em `tests/hooks/test_package.py` (eventos, importações, neutralidade).
- **`sensors_command`**: comando do projeto que o Stop (e o pre-commit) rodam; vazio por padrão nos modelos; aqui roda `unittest discover`.
- **Caminho implantado dos scripts**: varia por host (`.claude/hooks/apm/.apm/hooks/scripts/` no Claude Code), então só o manifesto o resolve (`${PLUGIN_ROOT}`).
- **Agentes coder/reviewer**: já rodam `sensors_command` e `openspec validate`.

### New Concepts Required
- **`_gherkin.py`**: biblioteca com a regra de formato e os requisitos efetivos, parametrizada por raiz.
- **`gherkin-sensor.py`**: CLI (`--root`) e modo `--on-validate` para hook.
- **Hook `PostToolUse` em `Bash`**: dispara o sensor quando o comando executado contém `openspec validate`.
- **Violação**: capability, nome do requisito, change de origem (se delta) e motivo.

### Key Business Rules
- Falta de cenário reprova (2) e cita capability + requisito; tudo conforme passa (0).
- O sensor roda quando o `openspec validate` roda, em qualquer projeto que instale o pacote.
- Só stdlib; nada de stack; só adições; sem push.
- Uma única implementação da regra (o teste da F1 passa a importá-la).

## Strategic Approach

### Solution Direction
Mover a lógica do teste da F1 para `_gherkin.py` (com `root`, `origin` e `RENAMED`), expor um CLI fino e registrar um `PostToolUse` no manifesto, que é o único ponto portável de "junto do validate". Neste repo o `sensors_command` também ganha o sensor, cobrindo Stop e pre-commit.

### Key Design Decisions
- **Hook em vez de wrapper ou só `sensors_command`** → o caminho implantado varia por host e um wrapper exigiria mudar o comando de todos (Q1).
- **Biblioteca com nome de módulo** → o script com hífen não é importável; teste e CLI compartilham a regra.
- **Raiz por `--root`, `CLAUDE_PROJECT_DIR`, `.git`** → reusa `project_root`; sem `openspec/` sai 0 com aviso.
- **Falha de execução no CLI = 2; no hook = fail-open** (Q3).
- **Nenhum agente editado** → coder/reviewer herdam via `sensors_command` e hook.

### Alternatives Considered
- **Wrapper `openspec-validate.py`**: rejeitado, depende de todos trocarem o comando.
- **Só `sensors_command`**: rejeitado como único mecanismo; não roda "junto" do validate e o caminho varia.
- **Chamar o sensor dentro do `openspec validate`**: o CLI é de terceiros; não é editável.
- **Duplicar a lógica do teste no script**: rejeitado (dois lugares divergem).

## Risk & Gap Analysis

### Requirement Ambiguities
- **"Roda junto"**: interpretado como disparado pelo evento de o `validate` rodar (hook), não como um comando único. Confirmar (Q1).
- **"Cita o requisito"**: capability + nome do requisito (pedido), mais a change quando vier de delta.
- **Projeto sem `openspec/`**: não especificado; escolhido aprovar com aviso.
- **Fonte V2.0 não lida**.

### Edge Cases
- **`RENAMED`**: o leitor da F1 ignora; sem tratamento o requisito apareceria com o nome antigo.
- **Delta de capability nova**: entra como está.
- **`archive/`**: ignorado.
- **Arquivo não UTF-8**: vira violação citada, sem traceback.
- **Comando composto** (`cd x && openspec validate`): o casamento por `\bopenspec\s+validate\b` pega; um falso positivo em texto (`echo "openspec validate"`) só roda um sensor barato.
- **Payload Copilot** (`toolArgs` em JSON texto): tratado.

### Technical Risks
- **`PostToolUse` no Copilot não verificado**: Stop e pre-commit cobrem; documentar.
- **Edição de config e docs fora do coder**: `harness.config.json`, README, `CLAUDE.md`, `config.yaml` vão para a sessão principal.
- **Parser próprio divergir do CLI do OpenSpec**: `--strict` segue como juiz da estrutura.
- **Sensor bloquear o Stop por bug**: aceito no CLI (Q3).

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | Requisito sem cenário: sensor falha e cita o requisito | Yes | Código 2, capability + nome + motivo |
| 2 | Todos com cenário: sensor passa | Yes | Código 0, stderr vazio |
| 3 | `openspec validate --strict` roda: sensor roda junto | Partial | Hook `PostToolUse`; Claude Code testável por payload, Copilot não verificado |
| 4 | Stdlib, ao lado dos hooks, 0 ou 2, stack-agnóstico | Yes | Teste de contrato do pacote e `grep` de neutralidade |
| 5 | Só adições, sem push | Yes | Nenhum hook ou agente alterado |
