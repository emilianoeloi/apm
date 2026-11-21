## MODIFIED Requirements

### Requirement: Quatro agentes de SDLC de fonte única
O pacote SHALL entregar exatamente os agentes `sdlc-planner`, `sdlc-coder`, `sdlc-reviewer` e `sdlc-auditor`, um arquivo `.apm/agents/<nome>.agent.md` cada, sem nenhum outro agente na pasta.

```gherkin
Cenário: Listagem da pasta
  Dado a pasta .apm/agents
  Quando ela é listada
  Então só existem os quatro arquivos sdlc-*.agent.md
```

#### Scenario: Listagem da pasta
- **WHEN** `.apm/agents` é listado
- **THEN** só existem os quatro arquivos `sdlc-*.agent.md`

#### Scenario: Implantação nos dois hosts
- **WHEN** `apm install --target claude,copilot` roda
- **THEN** existem `.claude/agents/sdlc-*.md` e `.github/agents/sdlc-*.agent.md`, idênticos à fonte

### Requirement: Frontmatter válido nos dois hosts
Cada agente SHALL declarar `name` igual ao nome do arquivo (minúsculas e hífen), `description` com a hora de usar, e `tools` como texto separado por vírgula só com nomes de ferramenta do Claude Code que o Copilot aceita como alias; SHALL NOT declarar `model` nem `handoffs`.

```gherkin
Cenário: Campos obrigatórios
  Dado o frontmatter de cada agente
  Quando ele é lido
  Então name, description e tools existem e name casa com o arquivo
  E model e handoffs não existem
```

#### Scenario: Campos obrigatórios
- **WHEN** o frontmatter de cada agente é lido
- **THEN** `name`, `description` e `tools` existem, `name` casa com o arquivo e `model` e `handoffs` não existem

#### Scenario: Nomes de ferramenta
- **WHEN** a lista `tools` de cada agente é lida
- **THEN** cada nome é um de `Read`, `Grep`, `Glob`, `Write`, `Edit`, `Bash` ou `Skill`

#### Scenario: Validação pelo Claude Code
- **WHEN** `claude plugin validate .claude/agents` roda, na versão que o oferece
- **THEN** nenhum agente é reportado com frontmatter inválido

### Requirement: Nenhuma ligação com uma stack
Os agentes SHALL NOT citar linguagem, ferramenta de build, pasta ou comando de um projeto específico; SHALL obter pastas de código, pastas de planejamento e comando de sensores do `harness.config.json` e as regras do projeto do arquivo raiz do agente.

```gherkin
Cenário: Busca de termos
  Dado os textos dos agentes
  Quando a busca por termos de projeto, linguagem e build roda
  Então a busca não encontra nada
```

#### Scenario: Busca de termos
- **WHEN** a busca por "cowboy", "cobol", "cobc", "calculadora", `Makefile`, `src/` e nomes de linguagens e ferramentas de build roda nos agentes
- **THEN** a busca não encontra nada

#### Scenario: Origem das informações do projeto
- **WHEN** o texto de cada agente é lido
- **THEN** ele manda ler o `harness.config.json` e o arquivo raiz do agente para pastas, sensores e regras

### Requirement: Orquestração sem cadeia
Nenhum agente SHALL ter a ferramenta de subagente nem instruir a chamar outro agente; cada agente SHALL declarar que a sessão principal o dispara e que ele devolve o resultado a ela.

```gherkin
Cenário: Ferramentas e instruções
  Dado o tools e o corpo de cada agente
  Quando eles são inspecionados
  Então não há Agent nem Task em tools
  E o texto não manda disparar outro agente
```

#### Scenario: Ferramentas e instruções
- **WHEN** `tools` e o corpo de cada agente são inspecionados
- **THEN** não há `Agent` nem `Task` em `tools` e o texto não manda disparar outro agente

### Requirement: Skills citadas existem
Todo skill que um agente cita pelo nome SHALL existir em `.apm/skills/`.

```gherkin
Cenário: Skill inexistente
  Dado os nomes de skill citados por um agente
  Quando eles são conferidos contra .apm/skills/
  Então cada nome corresponde a uma pasta com SKILL.md
```

#### Scenario: Skill inexistente
- **WHEN** os nomes de skill citados por um agente são conferidos contra `.apm/skills/`
- **THEN** cada nome corresponde a uma pasta com `SKILL.md`
