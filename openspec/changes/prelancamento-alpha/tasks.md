# Tasks

## 1. Configuração do pré-lançamento com teste

- [x] 1.1 Escrever `tests/release/test_release_config.py` (`unittest`) cobrindo os cenários de `release-versioning` que dependem só de arquivos (valores do pré-lançamento, ausência de `release-as`, tag sem componente, `extra-files`, manifesto, workflow sem mesclagem automática) e verificar com `python3 -m unittest tests.release.test_release_config -v` que os testes do pré-lançamento falham com a configuração atual
- [x] 1.2 Alterar o pacote `.` de `release-please-config.json` (`versioning: prerelease`, `prerelease: true`, `prerelease-type: alpha.1`, sem `release-as`) e verificar que o JSON é válido e que `python3 -m unittest tests.release.test_release_config -v` passa

## 2. Verificação do cálculo de versões

- [x] 2.1 Numa pasta temporária fora do repositório, instalar `release-please@17.6.0` e a versão `17.x` mais recente e calcular, com os valores da configuração, `0.3.1` + commit incompatível, `1.0.0-alpha.1` + `feat`, `1.0.0-alpha.2` + `fix` e `1.0.0-alpha.3` com `prerelease` falso; verificar que os resultados são `1.0.0-alpha.1`, `1.0.0-alpha.2`, `1.0.0-alpha.3` e `1.0.0`, e registrar a saída
- [x] 2.2 Conferir a configuração contra o schema oficial do release-please (`schemas/config.json`) e verificar que as quatro chaves usadas existem com os tipos esperados

## 3. Documentação

- [x] 3.1 Atualizar a seção "Releases" do `README.md` (pré-lançamento, `v0.3.1` como última estável, como consumir a tag do pré-lançamento, saída da `1.0.0` por `prerelease: false`, correção da frase do marcador) e verificar relendo que cobre os cenários da spec
- [x] 3.2 Acrescentar ao `CLAUDE.md` do repositório o cuidado de não reintroduzir `release-as` e de não mesclar o PR de release sem conferir a versão, e verificar que o texto está no arquivo

## 4. Integração

- [x] 4.1 Rodar `python3 -m unittest discover -s tests -t . -v` e `openspec validate prelancamento-alpha --strict` e verificar que passam
- [x] 4.2 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm .claude .agents .github` e verificar que volta vazia
- [x] 4.3 Registrar a change na seção da Onda 1 do `CHANGELOG.md` (resultado da verificação, o que fica para depois do merge e retrospectiva de skills) e verificar que o texto lista o que foi entregue

## Workflow follow-up

- Abrir o PR com título `ci(release): …` e esperar o "ok" do Elói para o push e a mesclagem.
- Depois do merge: conferir que o bot atualizou o PR #12 para `1.0.0-alpha.1` (título, `apm.yml`, manifesto e CHANGELOG); o Elói mescla o PR de release.
- Depois da tag: fechar a Onda 1 (README com o consumo da nova tag, CHANGELOG, roteiro de teste e retrospectiva), arquivar a change e fazer a retrospectiva de skills.
- Não publicar a `1.0.0` final antes da prova da calculadora em Go aprovada.
