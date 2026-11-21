# Skill acceptance-from-spec (F3 da V2.0)

## Requirements

Entregar o skill público `acceptance-from-spec`, que faz o `sdlc-coder`, na fase `apply`, escrever primeiro um teste de aceitação para cada `Cenário:` aprovado da change, provar o vermelho (comando e contagem de falhas, sem stubs), implementar e provar o verde pelo `sensors_command`; ligar cada teste ao cenário pela linha `Spec: <capability> / <requisito> / <cenário>`; descobrir o framework do projeto e, sem ele, propor a ferramenta e parar esperando a aprovação do Emiliano, sem instalar nada. Inclui o teste do skill e a edição do coder. Fora: conferência cenário-teste (F4), executor de Gherkin, perfis de SDLC, framework novo, script gerador de testes.

## Entities

```mermaid
classDiagram
direction TB

class Cenario {
    +String capability
    +String requisito
    +String titulo
    +fonte: bloco gherkin do delta da change
}

class TesteDeAceitacao {
    +linha "Spec: capability / requisito / titulo"
    +arquivo na pasta de testes do projeto
}

class EvidenciaTDD {
    +comando
    +contagemDeFalhas
    +motivo: assercao ou simbolo ausente
    +fase: vermelho ou verde
}

class SkillAcceptance {
    +listarCenarios()
    +descobrirFramework()
    +escreverTesteLigado()
    +provarVermelho()
    +provarVerde()
    +propor e parar sem framework
}

class SdlcCoder {
    +usa o skill antes das Operations
    +relata por cenario
}

class SensorsCommand {
    +harness.config.json
}

class SessaoPrincipal {
    +aprova ferramenta com o humano
    +edita CLAUDE.md e config
}

SkillAcceptance ..> Cenario : le
SkillAcceptance --> TesteDeAceitacao : orienta
TesteDeAceitacao ..> Cenario : Spec:
SkillAcceptance --> EvidenciaTDD : exige
SdlcCoder --> SkillAcceptance : Skill
SkillAcceptance --> SensorsCommand : verde e confere
SkillAcceptance ..> SessaoPrincipal : devolve proposta
```

Conservador: só adições; nenhum hook, `_gherkin.py`, spec existente ou outro agente muda.

## Approach

1. Testes vermelhos: `tests/agents/test_acceptance_skill.py` e ajustes em `test_contract.py`.
2. Escrever o skill: listar cenários, descobrir framework (arquivo raiz do agente, `sensors_command`, testes existentes), teste ligado, vermelho, código, verde, relatório; ramo sem framework (propor e parar).
3. Editar o coder: citar o skill antes das Operations e exigir teste, vermelho e verde por cenário no entregável.
4. Sessão principal: README (seção e aviso de migração), `apm install`, conferência das cópias.
5. Prova de comportamento num projeto de prova (humano).

## Structure

### Inheritance Relationships
1. Sem herança. Documentos e testes.

### Dependencies
1. O coder depende do skill pelo nome (`acceptance-from-spec`); o `test_contract.py` confere que o skill existe.
2. O skill depende de `harness.config.json` (`sensors_command`, `code_prefixes`) e do arquivo raiz do agente, não de scripts do pacote.
3. A F4 dependerá da convenção `Spec:` e do bloco Gherkin da F1.
4. As cópias implantadas dependem de `apm install`.

### Layered Architecture
1. Instrução: `SKILL.md`.
2. Agente: `sdlc-coder.agent.md`.
3. Prova estática: `tests/agents/`.
4. Documentação e implantação: README, `apm install` (sessão principal).

## Operations

### Create Tests - tests/agents/test_acceptance_skill.py (primeiro, vermelho)
1. Responsibility: proteger o texto do skill. Em tabela: frontmatter; trechos obrigatórios (`Spec:`, `Cenário:`, `vermelho`, `verde`, `contagem de falhas`, `sensors_command`, `harness.config.json`, `Pare`, `aprovação`, `não instal`, `code_prefixes`); `STACK_TERMS` e os quatro termos ausentes; tamanho; exemplo do marcador casa com o regex canônico; cópias idênticas em `.claude/skills/` e `.agents/skills/`.
2. Verificar vermelho (skill inexistente) e registrar comando e contagem. Estimativa: ~120 linhas.
3. Implementado além do previsto, após a revisão: casos negativos do marcador `Spec:` (dois campos, um campo, campos vazios, título vazio) e um positivo; trechos obrigatórios `BLOQUEADO`, `pendente`, `pulou`, `sem stubs`, `não se aplica`, `seguem normalmente` e `nada escrito`; lista `CODER_REQUIRED` para o coder; teste que impede "pára" no frontmatter. Tamanho real do skill: 97 linhas.

### Update Tests - tests/agents/test_contract.py
1. Responsibility: o coder cita o skill. `SKILLS_BY_ROLE["sdlc-coder"]` ganha `acceptance-from-spec`; regex de skills citadas cobre o nome; ordem (skill citado antes do item das Operations).
2. Verificar vermelho. Estimativa: ~8 linhas.

### Create Skill - .apm/skills/acceptance-from-spec/SKILL.md
1. Responsibility: instrução do ciclo teste-primeiro. Frontmatter `name`, `description`, `license: MIT`, `metadata`.
2. Passos: (1) cenários da change (`ADDED`/`MODIFIED`, bloco gherkin); (2) descobrir framework em ordem, parar no primeiro achado, conflito = parar; (3) sem framework: propor 1 a 3 opções (motivo, custo, pasta, comando, composição no `sensors_command`), Pare, não instale, não escreva, devolva à sessão principal para a aprovação do Emiliano; (4) escrever o teste com a linha `Spec:`; (5) vermelho: comando mais estreito, contagem de falhas, motivo, sem stubs; teste verde de primeira = relatar; (6) implementar; (7) verde: teste estreito e `sensors_command`, conferir que a aceitação roda, senão "sensores não configurados"; (8) relatório por cenário; pendências fora de `code_prefixes`.
3. Sem nomes de ferramenta, linguagem ou comando de stack. Estimativa: ~110 linhas.
4. Acrescentado após a revisão: change sem nenhum `Cenário:` faz o skill não se aplicar (sem inventar teste, registrado no relatório); no ramo "sem framework" o relatório é `BLOQUEADO: ferramenta de teste não definida: nada escrito, aguardando ferramenta`, e as Operations sem cenário seguem normalmente como pendente.

### Update Agent - .apm/agents/sdlc-coder.agent.md
1. Responsibility: invocar o skill. Item em "O que você faz" antes das Operations; linha em "Entregável". Nada mais muda (ferramentas, escrita, limites). Implementado também: o Entregável traz o formato BLOQUEADO e o item "corrija até os sensores passarem" diz que a falta de ferramenta de teste não conta como falha de sensor; o item novo é o nº 1 de "O que você faz" e os demais foram renumerados.
2. Verificar `tests/agents` verde. Estimativa: ~14 linhas.

### Update Docs (sessão principal, fora do coder)
1. `README.md`: seção "Testes de aceitação", linha na tabela, aviso de migração. `CLAUDE.md` opcional.

### Deploy (sessão principal)
1. `apm install --target claude,copilot`; `diff` das cópias; `claude plugin validate .claude/agents`.

### Verify
1. `python3 -B -m unittest discover -s tests -t .`; `openspec validate acceptance-from-spec --strict`; `python3 -B .apm/hooks/scripts/gherkin-sensor.py`; `grep -rniE "cowboy|cobol|cobc|calculadora" .apm` vazia; prova de comportamento no projeto de prova.

## Norms

1. Artefatos em português; cabeçalhos do OpenSpec e SHALL/MUST em inglês.
2. Skill e coder sem termos de stack nem do projeto de origem; só descrever, nunca nomear ferramenta.
3. Teste primeiro: cada task só vira `[x]` depois de a verificação passar; relatar o vermelho da suíte de contrato com comando e contagem.
4. Conventional Commits (`feat(agents):`), sem atribuição ao Claude.
5. Testes em `unittest`, estáticos, em tabela.

## Safeguards

1. Functional Constraints: `openspec validate --strict` e o sensor de Gherkin passam; o skill nunca manda instalar nada.
2. Scope Constraints: sem F4, sem executor de Gherkin, sem perfis, sem framework novo, sem script; ferramentas e limites de escrita do coder inalterados.
3. Neutrality Constraints: `grep` de neutralidade vazia; `STACK_TERMS` não casa no skill nem no coder; a ferramenta por stack permanece "não informado".
4. Honesty Constraints: o coder nunca afirma que a aceitação passou pelos sensores se o `sensors_command` não a roda; vermelho pulado é dito; comportamento do modelo "não verificado" até a prova no projeto real.
5. Stop Constraints: sem framework definido, nenhum teste é escrito e nada é instalado até a aprovação do Emiliano.
6. Release Constraints: sem push, tag ou merge sem o "ok" do Elói; PR `feat(agents):`.

<!-- Sync pós-implementação. Task 6.4 (comportamento do modelo num projeto de prova, não informado) segue aberta; os testes provam o texto, não o modelo. -->
