## ADDED Requirements

### Requirement: Script confere o vínculo cenário-teste
O script `.apm/hooks/scripts/spec-trace.py` SHALL, para cada `Cenário:` exigido da change, procurar nos arquivos de teste a linha literal `Spec: <capability> / <requisito> / <cenário>`, SHALL imprimir uma linha por cenário com o estado `COBERTO` (com `arquivo:linha`) ou `SEM_TESTE`, e SHALL sair com 0 quando nenhum cenário exigido estiver sem teste e não houver `ORFAO` nem `AMBIGUO`, e com 2 nos demais casos.

```gherkin
Cenário: Cenário exigido com e sem teste
  Dado uma change que acrescenta dois cenários e um teste com a linha Spec: de apenas um deles
  Quando o script roda sobre o projeto
  Então o cenário ligado sai COBERTO com arquivo e linha
  E o outro sai SEM_TESTE
  E a saída é 2
```

#### Scenario: Cenário exigido com e sem teste
- **WHEN** o script roda sobre uma change com dois cenários acrescentados e um teste que traz a linha `Spec:` de só um deles
- **THEN** o cenário ligado sai `COBERTO` com `arquivo:linha`, o outro sai `SEM_TESTE` e a saída é 2

#### Scenario: Todos cobertos
- **WHEN** todo cenário exigido tem a sua linha `Spec:` num teste
- **THEN** nenhuma linha `SEM_TESTE` aparece e a saída é 0

#### Scenario: Prefixo mais longo
- **WHEN** a spec tem os cenários `Caso` e `Caso feliz` no mesmo requisito e o teste traz só a linha de `Caso feliz`
- **THEN** `Caso feliz` sai `COBERTO` e `Caso` sai `SEM_TESTE`

### Requirement: Só cenário novo ou alterado é exigido
O script SHALL exigir teste para todo `Cenário:` de requisito `ADDED` e para o de requisito `MODIFIED` com título novo ou passos diferentes dos da spec principal, SHALL marcar o cenário idêntico e sem teste como `HERDADO_SEM_TESTE`, sem pesar na saída, e SHALL restringir o exigido aos deltas de `--change <nome>` quando dada.

```gherkin
Cenário: Cenário herdado de requisito modificado
  Dado um requisito MODIFIED com um cenário igual ao da spec principal e um cenário novo, ambos sem teste
  Quando o script roda sobre a change
  Então o cenário igual sai HERDADO_SEM_TESTE e não pesa na saída
  E o cenário novo sai SEM_TESTE
```

#### Scenario: Cenário herdado de requisito modificado
- **WHEN** o script roda sobre uma change com requisito `MODIFIED` que mantém um cenário da spec principal e acrescenta outro, ambos sem teste
- **THEN** o cenário mantido sai `HERDADO_SEM_TESTE` sem pesar na saída e o novo sai `SEM_TESTE`

#### Scenario: Passos alterados
- **WHEN** um cenário `MODIFIED` mantém o título e muda os passos
- **THEN** ele é exigido e sai `SEM_TESTE` sem teste

#### Scenario: Filtro por change
- **WHEN** há duas changes ativas e o script roda com `--change` de uma delas
- **THEN** só os cenários dos deltas dessa change são exigidos

### Requirement: Marcador órfão e marcador ambíguo são apontados
O script SHALL apontar como `ORFAO` toda linha de teste com `Spec:` e ao menos dois separadores ` / ` que não case, por prefixo, com nenhum cenário efetivo, e SHALL apontar como `AMBIGUO` os cenários de capability e requisito distintos cujo literal da trinca seja idêntico; a linha com `Spec:` e menos de dois separadores SHALL ser ignorada.

```gherkin
Cenário: Título digitado errado
  Dado um teste com a linha Spec: cujo título de cenário não existe na spec
  Quando o script roda
  Então a linha sai ORFAO com arquivo e linha
  E a saída é 2
```

#### Scenario: Título digitado errado
- **WHEN** um teste traz uma linha `Spec:` com título de cenário inexistente
- **THEN** a linha sai `ORFAO` com `arquivo:linha` e a saída é 2

#### Scenario: Literal em colisão
- **WHEN** dois cenários de requisitos distintos formam o mesmo literal por causa de ` / ` nos nomes
- **THEN** ambos saem `AMBIGUO` e a saída é 2

#### Scenario: Prosa com Spec:
- **WHEN** um arquivo traz `Spec: alguma coisa` com menos de dois separadores
- **THEN** a linha é ignorada

### Requirement: Busca em arquivos de teste com exclusões
O script SHALL pesquisar, por padrão, os arquivos de texto da raiz do projeto, exceto as pastas de controle e de dependências (`.git`, `openspec`, `spdd`, `.harness`, `.claude`, `.github`, `.agents`, `.apm`, `apm_modules`, `node_modules`, `vendor`, `target`, `build`, `dist`, `__pycache__`, `.venv`, `venv`), os arquivos `.md`, os binários (com byte NUL) e os maiores que 1 MiB; a opção `--tests <caminho>`, repetível, SHALL restringir a busca aos caminhos dados.

```gherkin
Cenário: Marcador só em documentação
  Dado a linha Spec: de um cenário aparece apenas num arquivo .md e numa pasta excluída
  Quando o script roda
  Então o cenário sai SEM_TESTE
```

#### Scenario: Marcador só em documentação
- **WHEN** a linha `Spec:` de um cenário aparece só num `.md` e numa pasta excluída
- **THEN** o cenário sai `SEM_TESTE`

#### Scenario: Busca restrita
- **WHEN** o script roda com `--tests` apontando uma pasta
- **THEN** só os arquivos dessa pasta são lidos

#### Scenario: Arquivo que não é texto
- **WHEN** há um binário e um arquivo ilegível na raiz
- **THEN** eles são ignorados e o script termina sem erro

### Requirement: Script só lê e não deixa rastro
O script SHALL ser somente leitura: SHALL NOT criar, alterar nem apagar arquivo, SHALL definir `sys.dont_write_bytecode` antes de importar `_gherkin` para não criar `__pycache__`, SHALL NOT chamar `git` e SHALL usar só a biblioteca padrão e os módulos locais `_gherkin` e `_common`; a leitura das specs SHALL reutilizar `_gherkin`, acrescida de `parse_scenarios(body)`, que devolve `(título, passos)` de cada `Cenário:` do bloco sem alterar `validate` nem `effective_requirements`.

```gherkin
Cenário: Execução sem rastro
  Dado um projeto com specs e testes
  Quando o script roda
  Então nenhum arquivo é criado nem alterado, inclusive __pycache__
  E o git status --porcelain fica igual
```

#### Scenario: Execução sem rastro
- **WHEN** o script roda sobre um projeto com specs e testes
- **THEN** nenhum arquivo é criado ou alterado, nem `__pycache__` na pasta dos scripts, e o `git status --porcelain` fica igual

#### Scenario: Leitura dos cenários do bloco
- **WHEN** `parse_scenarios` recebe o corpo de um requisito com bloco `gherkin`
- **THEN** devolve o título e os passos de cada `Cenário:` na ordem, e `[]` sem bloco

### Requirement: Saída e robustez
O script SHALL imprimir em stdout uma linha por item no formato `spec-trace: <ESTADO> <capability> / <requisito> / <cenário>` mais um resumo com as contagens e `extras: N` (`#### Scenario:` sem `Cenário:` no bloco, não exigidos), SHALL sair somente com 0 ou 2, SHALL sair 0 avisando em stderr quando a raiz não tiver `openspec/` ou não houver change ativa, e SHALL tratar erro inesperado como saída 2.

```gherkin
Cenário: Projeto sem openspec
  Dado uma raiz sem a pasta openspec
  Quando o script roda
  Então ele avisa em stderr que não há specs e sai 0
```

#### Scenario: Projeto sem openspec
- **WHEN** o script roda numa raiz sem `openspec/`
- **THEN** ele avisa em stderr e sai 0

#### Scenario: Resumo
- **WHEN** o script termina uma conferência
- **THEN** a última linha traz as contagens e `extras: N`

### Requirement: Implantação junto dos scripts do pacote
O `spec-trace.py` SHALL ficar em `.apm/hooks/scripts/` ao lado de `_gherkin.py`, SHALL ser copiado por `apm install --target claude,copilot` para os diretórios de scripts dos dois hosts, idêntico à fonte, e SHALL NOT constar do `harness.json` nem do `sensors_command` deste repositório.

```gherkin
Cenário: Script implantado
  Dado o pacote instalado com apm install --target claude,copilot
  Quando as cópias são comparadas com a fonte
  Então os dois hosts têm spec-trace.py e _gherkin.py idênticos à fonte
```

#### Scenario: Script implantado
- **WHEN** as cópias em `.claude/hooks/apm/.apm/hooks/scripts/` e `.github/hooks/scripts/apm/.apm/hooks/scripts/` são comparadas com a fonte
- **THEN** `spec-trace.py` e `_gherkin.py` são idênticos à fonte

#### Scenario: Fora do hook e do sensor
- **WHEN** o `harness.json` e o `sensors_command` são lidos
- **THEN** nenhum cita `spec-trace`
