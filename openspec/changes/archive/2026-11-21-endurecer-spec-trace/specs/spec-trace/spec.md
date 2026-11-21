## MODIFIED Requirements

### Requirement: Marcador órfão e marcador ambíguo são apontados
O script SHALL apontar como `ORFAO` toda linha de teste com `Spec:` e ao menos dois separadores ` / ` que não case, por prefixo seguido de um fim de título válido (requisito "Fim do título do marcador"), com nenhum cenário efetivo, e SHALL apontar como `AMBIGUO` os cenários de capability e requisito distintos cujo literal da trinca seja idêntico; a linha com `Spec:` e menos de dois separadores SHALL ser ignorada.

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
O script SHALL pesquisar, por padrão, os arquivos de texto da raiz do projeto, exceto as pastas de controle e de dependências (`.git`, `openspec`, `spdd`, `.harness`, `.claude`, `.github`, `.agents`, `.apm`, `apm_modules`, `node_modules`, `vendor`, `target`, `build`, `dist`, `__pycache__`, `.venv`, `venv`), os arquivos `.md`, os binários (com byte NUL) e os maiores que 1 MiB; a opção `--tests <caminho>`, repetível, SHALL restringir a busca aos caminhos dados; o script SHALL abrir cada arquivo sem seguir link simbólico e sem bloquear (`O_NOFOLLOW` e `O_NONBLOCK`, cada um onde o sistema o oferece) e SHALL conferir que é arquivo regular no descritor já aberto, ignorando FIFO, dispositivo e link, inclusive o arquivo trocado por um deles depois da listagem.

```gherkin
Cenário: Marcador só em documentação
  Dado a linha Spec: de um cenário aparece apenas num arquivo .md e numa pasta excluída
  Quando o script roda
  Então o cenário sai SEM_TESTE

Cenário: Arquivo trocado por FIFO depois da listagem
  Dado um arquivo comum de texto que é trocado por um FIFO logo antes de ser aberto
  Quando o script lê o arquivo
  Então a abertura usa as opções que não seguem link e não bloqueiam
  E o arquivo é ignorado sem travar o script
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

#### Scenario: Arquivo trocado por FIFO depois da listagem
- **WHEN** um arquivo comum vira FIFO entre a listagem e a abertura
- **THEN** a abertura usa `O_NOFOLLOW` e `O_NONBLOCK`, o arquivo é ignorado e o script termina sem travar

#### Scenario: Link, FIFO e dispositivo
- **WHEN** a busca encontra um link simbólico (para arquivo comum ou para dispositivo) ou um FIFO
- **THEN** eles são ignorados e o script termina sem travar

## ADDED Requirements

### Requirement: Fim do título do marcador
O script SHALL aceitar, depois do título do cenário na linha `Spec:`, somente o fim da linha ou um fechamento de comentário conhecido (`*/`, `-->`, `--]]`, `--}}`, `%}`, `?>`, `"`, `'`, `` ` ``, `)`, `]`, `}`, `#`, `//`), precedido ou não de espaço, tab ou espaço não separável (NBSP); SHALL tratar qualquer outro resto da linha como não casado, de modo que a linha com dois ou mais ` / ` saia `ORFAO` e o cenário saia `SEM_TESTE`; e a lista de fechamentos SHALL ser uma constante única do script.

```gherkin
Cenário: Fechamento conhecido depois do título
  Dado um cenário Um e uma linha Spec: do cenário seguida de um fechamento de comentário conhecido, com espaço, tab ou NBSP antes dele
  Quando o script roda
  Então o cenário sai COBERTO com arquivo e linha

Cenário: Sufixo que não é fechamento
  Dado um cenário Caso e uma linha Spec: cujo título é seguido de um sufixo que não é fechamento, como " - feliz", "_2", "." ou " (extra)"
  Quando o script roda
  Então a linha sai ORFAO com arquivo e linha
  E o cenário Caso sai SEM_TESTE
  E a saída é 2
```

#### Scenario: Fechamento conhecido depois do título
- **WHEN** a linha `Spec:` de um cenário termina em fechamento conhecido, com espaço, tab ou NBSP antes dele
- **THEN** o cenário sai `COBERTO` com `arquivo:linha`

#### Scenario: Sufixo que não é fechamento
- **WHEN** o título da linha `Spec:` é seguido de `-`, `_`, `.` ou `(` com texto, ou de letra ou dígito
- **THEN** a linha sai `ORFAO`, o cenário sai `SEM_TESTE` e a saída é 2

#### Scenario: Marcador sozinho na linha
- **WHEN** a linha `Spec:` termina no título, sem nada depois
- **THEN** o cenário sai `COBERTO`
