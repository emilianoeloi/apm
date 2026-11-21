# Proposal

## Why

Hoje o `sdlc-coder` segue o canvas e roda os sensores, mas nada obriga que cada cenário da spec vire um teste que falha antes do código e passa depois. A F1 pôs o bloco Gherkin em cada requisito e a F2 o confere; falta o elo que transforma o cenário aprovado em prova executável. A história H3 da especificação APM_SETUP_V2.0 diz: "como Emiliano, quero testes de aceitação gerados da spec, para provar que o código cumpre a intenção".

Não li a especificação no Drive (não há conector do Drive nesta sessão); os critérios abaixo vêm do pedido da sessão principal. Se o texto original diferir, vale o original.

## What Changes

- **Skill público `acceptance-from-spec`** (`.apm/skills/acceptance-from-spec/SKILL.md`): ensina o coder a, para cada `Cenário:` aprovado dos requisitos `ADDED`/`MODIFIED` da change, escrever primeiro um teste de aceitação, provar que ele falha (vermelho, com comando e contagem de falhas) e só então implementar. Não fixa framework: descobre o que o projeto já usa (arquivo raiz do agente, `sensors_command`, testes existentes) e, se não houver nada, propõe uma ferramenta e **para** esperando a aprovação do Emiliano, sem instalar nem escrever nada.
- **Convenção de ligação teste-cenário**: cada teste de aceitação leva, num comentário, no nome ou no rótulo do teste, a linha literal `Spec: <capability> / <nome do requisito> / <título do cenário>`, com os três textos exatamente como estão na spec. A F4 poderá conferir a ligação por busca de texto.
- **Edição do `sdlc-coder`** (`.apm/agents/sdlc-coder.agent.md`): em `apply`, antes de implementar cada Operation que realiza requisito da spec, usa o skill `acceptance-from-spec`; a evidência de vermelho e de verde entra no relatório. Só adição de texto; ferramentas e limites de escrita do coder não mudam.
- **Teste do skill** (`tests/agents/test_acceptance_skill.py`) e ajustes no `test_contract.py`: frontmatter, trechos obrigatórios, neutralidade de stack, citação pelo coder e cópias implantadas idênticas à fonte.
- **README (sessão principal)**: seção "Testes de aceitação" e aviso de migração.

Só adições: nenhum hook, spec ou skill existente é removido; nenhum framework de teste novo entra no pacote; o fluxo SDLC continua único (sem perfis).

**Rotina de quem opera**: na primeira `apply` de um projeto sem ferramenta de teste definida, o coder passa a parar e devolver uma proposta de ferramenta; o Emiliano precisa aprová-la (a sessão principal registra a escolha no arquivo raiz do agente e, se quiser, no `sensors_command`) antes de o coder seguir. É um passo a mais que antes não existia. Em projetos que já têm testes, o coder passa a escrever os testes de aceitação primeiro, sem passo manual novo.

**Aviso de migração** (projetos na versão anterior do pacote): depois de `apm update` e `apm install --target claude,copilot`, o coder passa a exigir o teste de aceitação antes do código. Nada quebra; projetos sem `sensors_command` ou sem testes recebem a proposta de ferramenta na primeira `apply`; projetos cujo `sensors_command` não roda os testes de aceitação serão avisados de que o "verde pelos sensores" não prova nada até comporem o comando. O texto vai para o README.

Fora desta change: a conferência cenário-contra-teste pelo reviewer (F4), executor de Gherkin (os testes são escritos na linguagem do projeto, não executam o `.feature`), geração automática de código de teste por script, perfis de SDLC, instalação de qualquer ferramenta.

## Capabilities

### New Capabilities
- `acceptance-from-spec`: o skill, a ordem teste-primeiro com evidência de vermelho e verde, a convenção de ligação, a descoberta do framework e a parada sem ferramenta aprovada, a neutralidade de stack e a implantação.

### Modified Capabilities
- `sdlc-agent-roles`: o coder passa a abrir a implementação pelo teste de aceitação (requisito acrescentado).
- `pacote-generico`: o README passa a trazer o aviso de migração desta versão (requisito acrescentado).

## Impact

- **Arquivos (apply, dentro de `code_prefixes`)**: `.apm/skills/acceptance-from-spec/SKILL.md` (novo), `.apm/agents/sdlc-coder.agent.md`, `tests/agents/test_acceptance_skill.py` (novo), `tests/agents/test_contract.py`.
- **Fora do escopo de escrita do coder** (`code_prefixes`: `.apm/`, `scripts/`, `tests/`): `README.md` (seção e aviso de migração), as cópias implantadas por `apm install` (`.claude/skills/`, `.agents/skills/`, `.claude/agents/`, `.github/agents/`) e `apm.lock.yaml`, e, se aceito, `CLAUDE.md` deste repo. Ficam para a sessão principal.
- **Release**: `feat(agents):` (minor). Push, PR e mesclagem são do Elói.
- **Risco principal**: o comportamento do coder só se prova num projeto real; o teste do repositório prova o texto, não o modelo (ver design, riscos).
