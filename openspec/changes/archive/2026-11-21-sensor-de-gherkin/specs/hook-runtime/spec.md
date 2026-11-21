## MODIFIED Requirements

### Requirement: Entrega dos hooks pelo APM
O pacote SHALL declarar os hooks em `.apm/hooks/` com os scripts no mesmo diretório, de modo que `apm install --target claude,copilot` registre `SessionStart`, `PreToolUse`, `PostToolUse` e `Stop` em `.claude/settings.json` e `.github/hooks/` e implante os scripts, sem cópia manual.

```gherkin
Cenário: Instalação num projeto vazio
  Dado um projeto vazio que depende do pacote
  Quando "apm install --target claude,copilot" roda
  Então SessionStart, PreToolUse, PostToolUse e Stop aparecem em .claude/settings.json
  E os scripts referenciados existem nos caminhos registrados
```

#### Scenario: Instalação num projeto vazio
- **WHEN** `apm install --target claude,copilot` roda num projeto que depende do pacote
- **THEN** os quatro eventos aparecem em `.claude/settings.json` e os scripts referenciados existem nos caminhos registrados

#### Scenario: Script entregue funciona
- **WHEN** o script implantado do hook de Stop roda com um payload válido num projeto sem configuração
- **THEN** ele sai com código 0

### Requirement: Hooks só com biblioteca padrão e sem stack
Os scripts de hook SHALL usar somente a biblioteca padrão do Python e os helpers `_common` e `_gherkin` do próprio diretório, e SHALL NOT citar linguagem, pasta ou comando de um projeto específico.

```gherkin
Cenário: Importações e termos
  Dado os scripts de .apm/hooks/
  Quando as importações e os termos de projeto são inspecionados
  Então só há importações da biblioteca padrão ou dos helpers do diretório
  E a busca por termos do projeto de origem não encontra nada
```

#### Scenario: Importações e termos
- **WHEN** os scripts de `.apm/hooks/` são inspecionados
- **THEN** todas as importações são da biblioteca padrão ou dos helpers do próprio diretório, e a busca por "cowboy", "cobol", "cobc" e "calculadora" não encontra nada
