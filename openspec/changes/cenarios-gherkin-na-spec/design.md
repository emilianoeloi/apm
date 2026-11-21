# Design

## Context

As 6 specs principais têm 33 requisitos, todos com `#### Scenario:` em `WHEN`/`THEN`. O `openspec validate --strict` exige esses cenários e avisa quando o texto de um requisito passa de 500 caracteres. O planner (`.apm/agents/sdlc-planner.agent.md`) delega a proposta ao skill `openspec-propose` (gerado pelo CLI, autor `openspec`) e já consulta `openspec/config.yaml`. Os testes de contrato estão em `tests/agents/test_contract.py` (estáticos, stdlib). A fonte é `.apm/`; `.claude/`, `.github/` e `.agents/` são cópias de `apm install`.

Não li a especificação APM_SETUP_V2.0 no Drive; usei só a história H1, os critérios de aceite e as restrições do pedido. Se o texto original diferir, vale o texto original.

Verificado com o CLI (`openspec` local): um bloco cercado **entre o parágrafo normativo e o primeiro `#### Scenario:`** passa em `--strict`, não entra no texto do requisito (não conta para o limite de 500 caracteres) e não vira cenário. Um bloco **depois** de um `#### Scenario:` é absorvido pelo `rawText` desse cenário. Por isso a posição é antes do primeiro cenário.

## Goals / Non-Goals

**Goals:**
- Formato único, exato e legível por máquina, para o sensor F2 ler sem adivinhar.
- Todo requisito novo ou modificado nasce com o bloco, e os existentes são migrados.

**Non-Goals:**
- O sensor (F2) e o skill `acceptance-from-spec` (F3).
- Perfis de SDLC, executor de Gherkin, framework de testes, troca de OpenSpec/OpenSPDD.
- Mexer no comportamento que as specs existentes descrevem.

## Decisions

1. **Formato exato.** Dentro de um requisito, na ordem: parágrafo normativo (SHALL/MUST), uma linha em branco, o bloco, uma linha em branco, os `#### Scenario:`.

   ````
   ```gherkin
   Cenário: <título igual ao de um #### Scenario: do requisito>
     Dado <contexto>
     E <contexto adicional, opcional>
     Quando <ação>
     Então <resultado observável>
     E <resultado adicional, opcional>
   ```
   ````

   Regras para o leitor de máquina: a linha de abertura é exatamente ```` ```gherkin ```` no início da linha; o fechamento é ```` ``` ```` sozinho; dentro do bloco cada linha, sem o recuo, começa com `Cenário:`, `Dado`, `Quando`, `Então`, `E` ou `Mas`, ou é vazia ou começa com `#` (comentário); `Cenário:` e `Então` levam acento; um bloco pode ter mais de um `Cenário:`, e cada um precisa de `Dado`, `Quando` e `Então`, nessa ordem. Mínimo exigido: um cenário por requisito.
2. **Aditivo.** Os `#### Scenario:` ficam, porque o validador os exige e porque dão o detalhe por caso. O Gherkin é o cenário representativo que a máquina lê. A repetição do título amarra os dois e permite ao F2 detectar divergência.
3. **Onde entra a obrigação.** Em três pontos que o pacote controla: (a) o texto do `sdlc-planner`, que é o que o aceite exige; (b) o skill `openspec-workflow`, que o planner e o coder consultam e que viaja com o pacote; (c) `rules.specs` em `openspec/config.yaml`, que o `openspec instructions` injeta ao gerar a spec neste repositório. `openspec-propose` não é editado: é gerado pelo CLI e seria sobrescrito por `openspec update`.
4. **Retrofit nesta change.** As 6 specs ganham o bloco por deltas `MODIFIED` (31 requisitos). Texto e cenários são copiados sem alteração, só o bloco entra, então o comportamento especificado não muda. Os 2 requisitos de pré-lançamento de `release-versioning` ficam de fora porque a change `versao-final-1-0-0` os remove; os 3 que ela adiciona receberam o bloco no próprio delta dela.
5. **Teste estático dos requisitos efetivos.** `tests/specs/test_gherkin_blocks.py` calcula os requisitos efetivos (specs principais, trocando pelos `MODIFIED`/`ADDED` dos deltas ativos e tirando os `REMOVED`) e confere a regra do item 1. Usar os efetivos, e não só as principais, mantém o sensor de Stop verde durante o `apply`, antes do arquivamento. O F2 pode reaproveitar esse leitor; não é um sensor genérico do pacote.
6. **Tamanho do bloco.** Um `Cenário:` por requisito basta; o objetivo é a intenção testável, não cobertura. Os casos de borda continuam nos `#### Scenario:`.

## Decisões em aberto (do humano)

- **Q1. Retrofit das 6 specs nesta change ou numa seguinte?** Recomendação: nesta change (o pedido diz "todo requisito do apm"; sem o retrofit o F2 nasceria com 31 violações). Custo: os deltas repetem ~400 linhas de spec e a revisão fica mais longa, embora mecânica. Risco: erro de cópia num `MODIFIED` troca texto sem aviso; mitigado por o bloco ser a única diferença (conferível por diff) e pelo arquivamento falhar se o nome do requisito não casar. Alternativa: só planner e skill agora, retrofit depois, com o F2 tolerando specs antigas.
- **Q2. Posição do bloco: antes do primeiro `#### Scenario:` (recomendado) ou depois do último?** Antes não conta para o limite de 500 caracteres e não é absorvido por um cenário; depois seria engolido pelo último `#### Scenario:` no parse do CLI. Custo: nenhum. Risco: um dia o CLI mudar o parser; o teste do item 5 pegaria pela validação estrita.
- **Q3. O título do `Cenário:` precisa ser igual ao de um `#### Scenario:`?** Recomendação: sim (rastro e detecção de divergência). Custo: renomear nos dois lugares ao mudar um. Risco: atrito de escrita; é fácil de relaxar depois porque só o F2 usará a regra.
- **Q4. Teste de formato nesta change ou esperar o F2?** Recomendação: incluir o teste pequeno aqui, porque a ordem é teste-primeiro e o retrofit precisa de uma prova. Custo: ~110 linhas de teste que o F2 pode absorver. Risco: sobreposição com o F2; mitigada por o leitor ser reaproveitável.
- **Q5. `Então` com acento obrigatório?** Recomendação: sim, forma única para o F2 (`Entao` sem acento reprova). Custo: digitação. Risco: falso negativo se alguém escrever sem acento; o teste dá a mensagem.
- **Q6. Edição do delta de outra change.** Já feita: acrescentei 3 blocos Gherkin em `openspec/changes/versao-final-1-0-0/specs/release-versioning/spec.md` (nenhuma outra linha mudou; `openspec validate versao-final-1-0-0 --strict` passa). Sem isso, depois do arquivamento dela as specs principais teriam 3 requisitos fora do formato. Confirme ou peça para desfazer.

A seção "Decisões do humano" fica vazia até a aprovação.

### Ações do humano fora do código
- Arquivar `versao-final-1-0-0` (depois da tag `v1.0.0`, como já planejado) antes de arquivar esta change.
- Push, PR e mesclagem; o PR de release só é mesclado depois de conferir a versão proposta.

## Risks / Trade-offs

- [Gherkin pesar e virar burocracia] → um bloco, mínimo de um cenário por requisito; sem exigência de cobertura.
- [Duplicação entre Gherkin e `WHEN`/`THEN` divergir] → título igual e verificação de rastro pelo F2; o teste desta change só confere a presença do título.
- [Cópia imperfeita nos `MODIFIED`] → diff mecânico (só o bloco entra) e falha de arquivamento se o nome não casar.
- [Parser do CLI mudar a posição] → coberto por `openspec validate --strict` e pelo teste.
- [Planner ignorar a instrução] → a instrução está em três pontos e o contrato de agentes a testa; a prova real é o planner gerar uma proposta, o que o F2 fiscalizará.
- [Conflito de arquivamento com `versao-final-1-0-0`] → não há requisito em comum nos deltas; arquivar a outra primeiro.

## Migration Plan

1. Testes vermelhos (formato e contrato), depois as instruções, depois as cópias implantadas.
2. `openspec validate cenarios-gherkin-na-spec --strict` e a suíte completa.
3. No arquivamento, os deltas atualizam as 6 specs principais e a nova spec ganha o `Purpose` real (o texto provisório do arquivamento é trocado à mão).
4. Rollback: reverter o commit; nada é publicado enquanto o PR de release não for mesclado.

## Estimativa de tamanho

- Instruções (prosa): planner ~15 linhas, `openspec-workflow` ~35, `config.yaml` ~8, `CLAUDE.md` ~3: ~60 linhas; cópias implantadas são geradas.
- Testes: leitor e conformidade em tabela (~110 linhas, ~1,4 vez a lógica de ~80) mais ~30 no contrato dos agentes: ~140 linhas, estimadas à parte do código.
- Deltas de spec (já escritos): ~600 linhas de Markdown, não contam como código.
- Limite de PR: não informado; ~200 linhas de código e teste somados devem caber folgadamente.
