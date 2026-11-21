# SPDD Analysis: Cenários Gherkin na spec (F1 da V2.0)

## Original Business Requirement

Fonte: especificação APM_SETUP_V2.0 (Google Drive), funcionalidade F1. **Não li o arquivo do Drive**; os trechos abaixo vêm do pedido da sessão principal, transcritos sem alteração. Se o texto original diferir, vale o original.

> H1. Como Emiliano, quero cenários Gherkin na spec, para a intenção ficar testável.
> Dado o sdlc-planner, quando ele gera a proposta, então cada requisito tem ao menos um cenário Dado/Quando/Então.
> Dado um cenário na spec, quando eu o leio, então ele está num bloco cercado (fenced), dentro da spec do OpenSpec.
>
> Restrições: só adições (o pacote evolui, sem trocar OpenSpec/OpenSPDD); um cenário mínimo por requisito (risco: Gherkin pesar); sem perfis de SDLC; não é framework de testes. O sensor (F2) e o skill `acceptance-from-spec` (F3) não fazem parte desta change; só deixar o formato do bloco pronto para o sensor ler.

Formato decidido (pedido): fence ```` ```gherkin ````, palavras-chave em português (Dado/Quando/Então), posição sob cada `### Requirement:`.

## Domain Concept Identification

### Existing Concepts (from codebase)
- **Spec OpenSpec**: `openspec/specs/<capability>/spec.md`, com `### Requirement:` (parágrafo com SHALL/MUST) e `#### Scenario:` em `WHEN`/`THEN`, exigidos por `openspec validate --strict`. 6 specs, 33 requisitos.
- **Delta de change**: `ADDED`/`MODIFIED`/`REMOVED Requirements`; `MODIFIED` repete o requisito inteiro e é aplicado no arquivamento.
- **Planner**: `.apm/agents/sdlc-planner.agent.md`, que delega a proposta ao skill `openspec-propose` (gerado pelo CLI, autor `openspec`) e já respeita `openspec/config.yaml`.
- **Skill `openspec-workflow`**: autoral, viaja com o pacote, tem regras sobre requisitos curtos (< 500 caracteres).
- **Testes de contrato**: `tests/agents/test_contract.py`, estáticos e só com stdlib; neutralidade de stack e identidade das cópias implantadas.
- **Implantação**: `.apm/` é a fonte; `.claude/`, `.github/` e `.agents/` vêm de `apm install --target claude,copilot`.
- **Change `versao-final-1-0-0`**: concluída, ainda não arquivada; remove 2 e adiciona 3 requisitos em `release-versioning`.

### New Concepts Required
- **Bloco Gherkin do requisito**: um fence `gherkin` por requisito, depois do parágrafo normativo e antes do primeiro `#### Scenario:`, com `Cenário:` e os passos `Dado`/`Quando`/`Então` em português.
- **Rastro de título**: o título do `Cenário:` repete o de um `#### Scenario:` do mesmo requisito, para o F2 detectar divergência.
- **Requisitos efetivos**: specs principais mais os deltas ativos; é a visão que o teste (e depois o sensor) lê.

### Key Business Rules
- O Gherkin é **acréscimo**: `WHEN`/`THEN` continuam, porque a validação estrita os exige.
- Mínimo de **um** cenário por requisito; o Gherkin não pode virar peso.
- O bloco não é executável nem framework de testes; é texto legível por máquina.
- Sem perfis de SDLC; sem F2 nem F3 nesta change.
- Push, PR e mesclagem são do Elói.

## Strategic Approach

### Solution Direction
Definir o formato exato numa spec nova, torná-lo obrigatório nos três pontos que o pacote controla (planner, `openspec-workflow`, `rules.specs` do `config.yaml`), migrar as 6 specs por deltas `MODIFIED` e guardar tudo com um teste estático escrito antes. Verificado com o CLI: o bloco entre o parágrafo e o primeiro `#### Scenario:` passa em `--strict`, não conta para o limite de 500 caracteres e não vira cenário; depois de um cenário, seria absorvido por ele.

### Key Design Decisions
- **Posição antes do primeiro cenário** → única que o parser do CLI trata como fora do cenário e do texto do requisito.
- **Aditivo, não substitutivo** → o validador exige `WHEN`/`THEN`; trocar quebraria `--strict`.
- **Não editar `openspec-propose`** → é gerado pelo CLI e seria sobrescrito; a exigência entra no planner, no `openspec-workflow` e no `config.yaml`.
- **Retrofit nesta change** → o pedido fala em "todo requisito do apm"; sem ele o F2 nasceria com 31 violações.
- **Teste sobre requisitos efetivos** → mantém o sensor de Stop verde durante o `apply`, antes do arquivamento.
- **Acento obrigatório em `Cenário:` e `Então`** → forma única para o leitor de máquina.

### Alternatives Considered
- **Só planner e templates agora, retrofit depois**: menor, mas deixa as specs atuais fora do formato e o F2 sem base uniforme → recomendação é migrar já (Q1 em aberto).
- **Gherkin dentro do `#### Scenario:`**: o CLI o trataria como texto do cenário e o F2 teria de achá-lo dentro de um bullet → rejeitado.
- **Arquivo `.feature` separado por capability**: duplica a fonte e foge de "dentro da spec do OpenSpec" → rejeitado.
- **Trocar `WHEN`/`THEN` por Gherkin**: reprova `--strict` → rejeitado.
- **Editar `openspec-propose`**: sobrescrito por `openspec update` → rejeitado.

## Risk & Gap Analysis

### Requirement Ambiguities
- **"Cada requisito tem ao menos um cenário" vs. cenários que já existem em `WHEN`/`THEN`**: tratado como o bloco Gherkin ser exigido além deles (aditivo). Confirmar (Q1/Q2).
- **Idioma das palavras-chave**: pedido diz Dado/Quando/Então; `E` e `Mas` como continuação é decisão desta change; `Cenário:` também (o pedido não o nomeia).
- **O que vale como "um cenário" para um requisito com vários `#### Scenario:`**: um representativo basta; os demais ficam em `WHEN`/`THEN`.
- **Fonte da V2.0 não lida**: critérios transcritos do pedido.

### Edge Cases
- **Requisito `REMOVED`**: não leva bloco (sem corpo).
- **Requisito com menção de ```` ```gherkin ```` no meio da linha** (a própria spec nova): o leitor só reconhece o fence no início da linha.
- **`MODIFIED` com nome que não casa**: o arquivamento falha; o nome vem copiado da spec principal.
- **Overlap com `versao-final-1-0-0`**: 2 requisitos removidos ficam de fora; 3 adicionados ganharam o bloco no delta dela (edição de outra change, a confirmar, Q6).
- **Change arquivada antes da outra**: sem requisito em comum, qualquer ordem arquiva; a ordem recomendada é a `versao-final` primeiro.
- **Requisito de mais de 500 caracteres**: o bloco não conta para o limite.

### Technical Risks
- **Gherkin pesar** (risco declarado no pedido): mínimo de um cenário e um bloco por requisito.
- **Duplicação entre Gherkin e `WHEN`/`THEN` divergir**: título igual e F2.
- **Cópia imperfeita nos `MODIFIED`**: o único diferencial é o bloco; o diff é conferível.
- **Parser do CLI mudar**: `--strict` e o teste pegam.
- **Planner ignorar a instrução**: nenhum teste estático prova o comportamento do modelo; a prova real é uma proposta gerada, fiscalizada depois pelo F2.
- **`config.yaml` fora do escopo de escrita do coder**: a regra de specs é aplicada pela sessão principal ou pelo humano.

### Acceptance Criteria Coverage
| AC# | Description | Addressable? | Gaps/Notes |
|-----|-------------|--------------|------------|
| 1 | O planner, ao gerar a proposta, produz ao menos um cenário Dado/Quando/Então por requisito | Partial | Instrução em três pontos e teste estático; o comportamento do modelo só se prova numa proposta real (F2 fiscaliza) |
| 2 | O cenário está num bloco cercado dentro da spec do OpenSpec | Yes | Formato e posição fixados e testados; `--strict` passa |
| 3 | Só adições, sem trocar OpenSpec/OpenSPDD | Yes | `WHEN`/`THEN` e skills de terceiros intactos |
| 4 | Um cenário mínimo por requisito | Yes | Regra e teste |
| 5 | Formato pronto para o sensor ler (F2) | Yes | Gramática linha a linha no design; leitor reaproveitável |
| 6 | Sem perfis, sem framework de testes, sem F2/F3 | Yes | Fora de escopo declarado |
