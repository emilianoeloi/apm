## MODIFIED Requirements

### Requirement: Versão final por mudança de configuração
Com `prerelease` falso, o release-please SHALL propor a versão final `1.0.0` a partir de qualquer `1.0.0-alpha.N`, sem outra alteração de configuração.

```gherkin
Cenário: Saída do pré-lançamento
  Dado a versão 1.0.0-alpha.3 e prerelease falso
  Quando a estratégia recebe um commit feat
  Então a próxima versão é 1.0.0
```

#### Scenario: Saída do pré-lançamento
- **WHEN** a estratégia recebe `1.0.0-alpha.3` com `prerelease` falso e um commit `feat`
- **THEN** a próxima versão é `1.0.0`

### Requirement: Publicar continua ato humano
O fluxo de release SHALL abrir ou atualizar apenas o PR de release; nenhuma etapa automática SHALL mesclá-lo, e a publicação da tag e do GitHub Release SHALL ocorrer só quando uma pessoa mesclar esse PR.

```gherkin
Cenário: Workflow
  Dado o arquivo .github/workflows/release-please.yml
  Quando ele é lido
  Então ele só roda a ação do release-please em push na main
  E nenhum passo ativa mesclagem automática
```

#### Scenario: Workflow
- **WHEN** `.github/workflows/release-please.yml` é lido
- **THEN** ele só roda a ação do release-please em push na `main` e nenhum passo ativa mesclagem automática

### Requirement: Versão no manifesto e no pacote em sincronia
O PR de release SHALL atualizar o manifesto `.release-please-manifest.json` e a linha `version:` do `apm.yml` para a mesma versão, e a configuração SHALL listar o `apm.yml` em `extra-files`.

```gherkin
Cenário: Configuração de arquivos
  Dado a configuração do release-please
  Quando ela é lida
  Então extra-files contém apm.yml e o manifesto tem a chave "."
```

#### Scenario: Configuração de arquivos
- **WHEN** a configuração é lida
- **THEN** `extra-files` contém `apm.yml` e o manifesto tem a chave `.`

### Requirement: README explica o pré-lançamento
O `README.md` SHALL explicar como consumir um pré-lançamento, que a `v0.3.1` continua sendo a última versão estável até a final e como a `1.0.0` sai.

```gherkin
Cenário: Leitor do README
  Dado quem consome o pacote
  Quando lê a seção de releases do README
  Então encontra a tag do pré-lançamento, a última versão estável e o caminho para a versão final
```

#### Scenario: Leitor do README
- **WHEN** quem consome o pacote lê a seção de releases
- **THEN** encontra a tag do pré-lançamento, a indicação da última versão estável e o caminho para a versão final
