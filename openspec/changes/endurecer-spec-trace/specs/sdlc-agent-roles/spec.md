## MODIFIED Requirements

### Requirement: Reviewer confere cada cenário contra um teste
O `sdlc-reviewer` SHALL conferir que cada `Cenário:` novo ou alterado pela change tem teste ligado pela linha `Spec:`, usando o `spec-trace.py` achado por `Glob` (ou, sem a ferramenta `Glob`, por `find` que exclua `apm_modules`) ou, sem o script, `grep -F` da trinca no fonte dos testes, SHALL usar a cópia implantada do host (`.claude/hooks/apm/.apm/hooks/scripts/` ou `.github/hooks/scripts/apm/.apm/hooks/scripts/`) e nunca a de `apm_modules/`, SHALL ler cada teste ligado para confirmar que afirma o `Então`, SHALL tratar o cenário herdado sem teste como informativo e SHALL entregar a seção "Cenários x testes" sem alterar arquivo nem as `tools`.

```gherkin
Cenário: Revisão de change com cenários
  Dado uma change com cenários novos, testes ligados por Spec: e o script spec-trace.py implantado
  Quando o reviewer é disparado
  Então o relatório traz a seção Cenários x testes com o estado e o arquivo:linha de cada cenário
  E o git status --porcelain final é igual ao inicial

Cenário: Cópia certa do script
  Dado o texto do agente reviewer
  Quando ele é lido
  Então diz que a cópia certa é a implantada do host, fora de apm_modules
  E diz que find, excluindo apm_modules, é o plano B quando não há Glob
```

#### Scenario: Revisão de change com cenários
- **WHEN** o reviewer é disparado sobre uma change com cenários novos e testes ligados
- **THEN** o relatório traz a seção "Cenários x testes" com estado e `arquivo:linha` por cenário e o `git status --porcelain` final é igual ao inicial

#### Scenario: Script não encontrado
- **WHEN** o `Glob` não acha `spec-trace.py` ou `python3` falta
- **THEN** o reviewer confere com `grep -F` por cenário no fonte e diz no relatório que usou a reserva

#### Scenario: Cenário herdado
- **WHEN** um cenário de requisito `MODIFIED` é igual ao da spec principal e não tem teste
- **THEN** ele aparece como informativo na seção e não vira achado nem muda o veredito

#### Scenario: Ferramentas inalteradas
- **WHEN** o frontmatter do reviewer é lido
- **THEN** `tools` continua `Read, Grep, Glob, Bash`

#### Scenario: Cópia certa do script
- **WHEN** o texto do reviewer é lido
- **THEN** ele manda usar a cópia implantada do host, fora de `apm_modules/`, e cita `find` (sem `apm_modules`) como plano B sem `Glob`
