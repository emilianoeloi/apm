# acceptance-from-spec Specification

## Purpose
Fixa o skill `acceptance-from-spec`: na fase `apply`, o `sdlc-coder` escreve primeiro o teste de aceitação de cada cenário aprovado, ligado à spec pela linha `Spec:`, prova o vermelho e depois o verde pelo `sensors_command`, e, sem ferramenta de teste definida, propõe opções e para até a aprovação do humano.

## Requirements

### Requirement: Skill público de aceitação a partir da spec
O pacote SHALL entregar o skill `acceptance-from-spec` em `.apm/skills/acceptance-from-spec/SKILL.md`, com frontmatter válido (`name` igual ao nome da pasta e `description`), sem fixar framework de teste e sem citar linguagem, ferramenta ou comando de uma stack específica.

```gherkin
Cenário: Skill presente e neutro
  Dado a fonte do pacote em .apm/skills/
  Quando o arquivo do skill e a busca de termos de stack são inspecionados
  Então existe acceptance-from-spec/SKILL.md com frontmatter válido
  E nenhum termo de stack nem do projeto de origem aparece nele
```

#### Scenario: Skill presente e neutro
- **WHEN** o arquivo `.apm/skills/acceptance-from-spec/SKILL.md` e a busca de termos de stack são inspecionados
- **THEN** o arquivo existe com `name` igual à pasta e `description` preenchida, e nenhum termo de stack nem do projeto de origem aparece nele

#### Scenario: Cópias implantadas
- **WHEN** `apm install --target claude,copilot` roda
- **THEN** as cópias em `.claude/skills/acceptance-from-spec/` e `.agents/skills/acceptance-from-spec/` são idênticas à fonte

### Requirement: Teste de aceitação escrito antes do código e vermelho
O skill SHALL instruir o coder, para cada `Cenário:` dos requisitos `ADDED` e `MODIFIED` da change, a escrever o teste de aceitação antes da implementação, a rodá-lo e a relatar o comando e a contagem de falhas (vermelho) antes de escrever o código, sem criar implementações falsas ou stubs artificiais só para o teste compilar ou falhar. O coder SHALL registrar o motivo do vermelho (asserção que falha ou símbolo de produção ainda inexistente) e, se pular o vermelho, SHALL dizê-lo no relatório.

```gherkin
Cenário: Cenário aprovado entra em apply
  Dado um cenário aprovado numa spec da change e a fase apply
  Quando o sdlc-coder inicia a Operation que o realiza
  Então ele escreve primeiro o teste de aceitação
  E o relatório traz o comando e a contagem de falhas do teste vermelho
```

#### Scenario: Cenário aprovado entra em apply
- **WHEN** o coder inicia a Operation que realiza um requisito com cenário aprovado, na fase `apply`
- **THEN** o teste de aceitação é escrito primeiro e o relatório traz o comando e a contagem de falhas da execução vermelha, antes de qualquer código de produção

#### Scenario: Vermelho pelo motivo certo
- **WHEN** o teste vermelho falha
- **THEN** o relatório diz se a falha é de asserção ou de símbolo de produção ainda inexistente, e nenhum stub é criado para forçar o resultado

#### Scenario: Vermelho pulado
- **WHEN** o coder não consegue observar o vermelho de um cenário
- **THEN** o relatório diz explicitamente que pulou o vermelho e por quê

### Requirement: Teste verde pelos sensores depois do código
O skill SHALL exigir que, com o código pronto, o coder rode o `sensors_command` do projeto e relate o resultado, confirmando que o comando executa os testes de aceitação criados; se o `sensors_command` estiver vazio ou não os executar, o coder SHALL dizer "sensores não configurados" ou apontar a lacuna e SHALL NOT afirmar que a aceitação passou pelos sensores.

```gherkin
Cenário: Código pronto e sensores rodando
  Dado o código implementado e o teste de aceitação criado
  Quando o sdlc-coder roda o sensors_command
  Então o teste de aceitação passa
  E o relatório traz a contagem de falhas zerada
```

#### Scenario: Código pronto e sensores rodando
- **WHEN** o coder roda o `sensors_command` com o código implementado
- **THEN** o teste de aceitação passa e o relatório registra a execução verde, separada da vermelha

#### Scenario: Sensores que não rodam a aceitação
- **WHEN** o `sensors_command` está vazio ou não executa os testes de aceitação
- **THEN** o relatório aponta a lacuna e não afirma que a aceitação passou pelos sensores

### Requirement: Ligação entre o teste e o cenário
Todo teste de aceitação SHALL trazer, em comentário, nome ou rótulo do teste, a linha literal `Spec: <capability> / <nome do requisito> / <título do cenário>`, com os três textos idênticos aos da spec, para que a ligação possa ser conferida por busca de texto.

```gherkin
Cenário: Teste ligado ao cenário
  Dado um teste de aceitação criado pelo coder
  Quando o texto do teste é procurado pela linha Spec:
  Então a capability, o requisito e o título do cenário aparecem idênticos aos da spec
```

#### Scenario: Teste ligado ao cenário
- **WHEN** o texto de um teste de aceitação é procurado pela linha `Spec:`
- **THEN** a capability, o nome do requisito e o título do cenário aparecem idênticos aos da spec

#### Scenario: Cenário sem teste
- **WHEN** um `Cenário:` aprovado da change não tem nenhum teste com a sua linha `Spec:`
- **THEN** o coder lista o cenário como pendente no relatório em vez de declarar a Operation concluída

### Requirement: Framework descoberto, nunca imposto
O skill SHALL mandar o coder descobrir o framework de teste do projeto, nesta ordem: o arquivo raiz do agente, o `sensors_command` do `harness.config.json`, a pasta e os arquivos de teste existentes; o skill SHALL NOT fixar um framework, e a ferramenta de teste por stack SHALL permanecer "não informado" no pacote.

```gherkin
Cenário: Projeto com testes existentes
  Dado um projeto que já tem testes e um sensors_command que os roda
  Quando o skill roda
  Então o teste de aceitação usa o mesmo framework e a mesma pasta
  E nenhuma ferramenta nova é proposta
```

#### Scenario: Projeto com testes existentes
- **WHEN** o skill roda num projeto que já tem testes e um `sensors_command` que os executa
- **THEN** o teste de aceitação usa o framework e a pasta existentes e nenhuma ferramenta nova é proposta

### Requirement: Sem ferramenta definida, propor e parar
Quando o projeto não tem framework de teste definido, o skill SHALL mandar o coder propor a ferramenta (com motivo, custo, onde os testes ficariam e como entraria no `sensors_command`), preferir a que acompanha a toolchain do projeto, parar sem escrever teste algum e sem instalar nada, e devolver a proposta à sessão principal para a aprovação do Emiliano; o coder SHALL só prosseguir quando o brief trouxer a ferramenta aprovada.

```gherkin
Cenário: Projeto sem framework de teste
  Dado um projeto sem framework de teste definido
  Quando o skill roda
  Então ele propõe a ferramenta e espera a aprovação do Emiliano
  E não instala nada nem escreve nenhum teste
```

#### Scenario: Projeto sem framework de teste
- **WHEN** o skill roda num projeto sem framework de teste definido
- **THEN** o coder devolve uma proposta de ferramenta à sessão principal, para sem instalar nada nem escrever teste, e aguarda a aprovação do Emiliano

#### Scenario: Ferramenta aprovada no brief
- **WHEN** o coder é redisparado com a ferramenta aprovada no brief
- **THEN** ele escreve os testes de aceitação com essa ferramenta e segue o fluxo teste-primeiro

#### Scenario: Escopo do coder na aprovação
- **WHEN** a escolha da ferramenta precisa ser registrada no `CLAUDE.md` ou no `harness.config.json`
- **THEN** o coder lista a edição como pendente para a sessão principal, porque esses arquivos estão fora de `code_prefixes`

### Requirement: Vermelho vem da asserção do cenário
O skill SHALL exigir que o vermelho de cada teste de aceitação venha da asserção do `Então` do cenário e SHALL NOT aceitar como vermelho o erro do ambiente; o teste que passa sem o programa existir SHALL ser tratado como falso verde e reforçado, afirmando o conteúdo e não só o código de saída.

```gherkin
Cenário: Teste que passa sem o programa
  Dado um teste de aceitação que passa antes de o programa existir
  Quando o coder segue o skill
  Então o coder relata falso verde e reforça o teste afirmando o conteúdo
  E o vermelho relatado vem da asserção do cenário
```

#### Scenario: Teste que passa sem o programa
- **WHEN** um teste de aceitação passa antes de o programa existir
- **THEN** o skill manda relatar falso verde e reforçar o teste afirmando o conteúdo, não só o código de saída

#### Scenario: Vermelho por erro do ambiente
- **WHEN** a falha do teste vem do ambiente (arquivo, módulo ou comando ausente, código de saída genérico)
- **THEN** o skill não a aceita como vermelho e manda relatar a asserção do cenário que falhou, ou, em linguagem compilada, o símbolo de produção ausente declarado

### Requirement: Cenário extra anotado sem virar órfão
O skill SHALL mandar anotar o `#### Scenario:` extra (sem `Cenário:` correspondente no bloco `gherkin`) que ganhar teste com a linha `Extra: <capability> / <requisito> / <título do #### Scenario>` e SHALL proibir a linha `Spec:` nesse caso, para o `spec-trace` não apontar `ORFAO`; o extra sem comportamento observável distinto SHALL NOT ganhar teste.

```gherkin
Cenário: Extra com comportamento distinto
  Dado um #### Scenario: extra que descreve comportamento observável distinto
  Quando o coder escreve o teste dele
  Então o teste traz a linha Extra: com a trinca
  E não traz a linha Spec:
```

#### Scenario: Extra com comportamento distinto
- **WHEN** o coder escreve o teste de um `#### Scenario:` extra com comportamento observável distinto
- **THEN** o teste traz a linha `Extra: <capability> / <requisito> / <título>` e nunca a linha `Spec:`

#### Scenario: Extra anotado não vira órfão
- **WHEN** o `spec-trace.py` roda sobre um teste com a linha `Extra:` e a trinca de um extra
- **THEN** a linha não sai `ORFAO` e a saída continua 0

### Requirement: Fixture com linha Spec montada por constante
O skill SHALL mandar montar por constante, em tempo de execução, a linha `Spec:` que aparecer dentro de fixture ou exemplo de teste, para que a linha literal não exista no fonte e o `spec-trace` não a aponte como `ORFAO`.

```gherkin
Cenário: Fixture montada por constante
  Dado um teste cuja fixture precisa de uma linha Spec: com três campos
  Quando o coder monta a fixture seguindo o skill
  Então a linha é montada por constante e não aparece literal no fonte
  E o spec-trace não aponta ORFAO para ela
```

#### Scenario: Fixture montada por constante
- **WHEN** uma fixture de teste precisa de uma linha `Spec:` com três campos
- **THEN** o skill manda montá-la por constante, e o `spec-trace.py` não aponta `ORFAO` para o fonte do teste, ao contrário da linha literal

### Requirement: Cenário de comportamento do modelo é prova humana
O skill SHALL mandar registrar como pendente de prova humana, com a decisão do humano, o `Cenário:` cujo comportamento só uma prova humana cobre (comportamento do modelo), e SHALL NOT permitir criar teste que finja cobri-lo sem provar o comportamento; o relatório SHALL listar esses cenários à parte dos cenários sem teste.

```gherkin
Cenário: Cenário que só a prova humana cobre
  Dado um Cenário: que descreve o comportamento do modelo
  Quando o coder o encontra na lista de cenários
  Então o relatório o lista como pendente de prova humana, com a decisão do humano
  E nenhum teste é criado para fingir cobertura
```

#### Scenario: Cenário que só a prova humana cobre
- **WHEN** o coder encontra um `Cenário:` que descreve o comportamento do modelo
- **THEN** o relatório o lista como pendente de prova humana (`SEM_TESTE` conhecido) com a decisão do humano

#### Scenario: Teste que não prova o comportamento
- **WHEN** só existe um teste que não prova o comportamento do cenário
- **THEN** o skill proíbe ligá-lo ao cenário pela linha `Spec:` e manda manter o cenário pendente

### Requirement: Cenário herdado em requisito modificado
O skill SHALL tratar como herdado o `Cenário:` de requisito `MODIFIED` idêntico (título e passos) ao da spec principal, SHALL NOT exigir teste novo para ele e SHALL exigir teste para o cenário novo ou de passos alterados, em acordo com o `spec-trace`, que mostra o herdado sem teste como informativo.

```gherkin
Cenário: Herdado não exige teste novo
  Dado um requisito MODIFIED com um cenário igual ao da spec principal e um cenário novo
  Quando o coder lista os cenários a testar
  Então só o cenário novo ganha teste ligado por Spec:
  E o herdado é relatado como informativo
```

#### Scenario: Herdado não exige teste novo
- **WHEN** o coder lista os cenários de um requisito `MODIFIED` com um cenário igual ao da spec principal e um novo
- **THEN** só o novo ganha teste ligado por `Spec:` e o herdado é relatado como informativo

### Requirement: Afinação só por adição e dentro do teto
O skill afinado SHALL manter todos os trechos obrigatórios do skill anterior, SHALL ter versão `1.1`, SHALL continuar dentro do teto de tamanho do teste (150 linhas) e sem termo de stack ou de origem, e as cópias implantadas SHALL ser idênticas à fonte depois de `apm install`.

```gherkin
Cenário: Skill afinado cabe no teto
  Dado o skill afinado com as adições desta change
  Quando o teste de tamanho e de trechos obrigatórios roda
  Então todos os trechos antigos continuam presentes
  E o skill não passa de 150 linhas nem cita termo de stack
```

#### Scenario: Skill afinado cabe no teto
- **WHEN** o teste de tamanho e de trechos obrigatórios roda sobre o skill afinado
- **THEN** todos os trechos do skill anterior continuam presentes, a versão é `1.1` e o arquivo não passa de 150 linhas nem cita termo de stack

#### Scenario: Cópias do skill idênticas à fonte
- **WHEN** `apm install --target claude,copilot` roda depois da edição
- **THEN** as cópias em `.claude/skills/acceptance-from-spec/` e `.agents/skills/acceptance-from-spec/` são idênticas à fonte
