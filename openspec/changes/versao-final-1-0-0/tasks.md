# Tasks

## 1. Configuração da versão final com teste

- [x] 1.1 Atualizar `tests/release/test_release_config.py` para a versão final (`prerelease` falso, `versioning` igual a `prerelease` enquanto o manifesto tiver sufixo de pré-lançamento, nenhum `release-as`) e verificar com `python3 -m unittest tests.release.test_release_config -v` que o teste de `prerelease` falha com a configuração atual
- [x] 1.2 Trocar `"prerelease"` para `false` no pacote `.` de `release-please-config.json`, mantendo `versioning` e `prerelease-type`, e verificar que o JSON é válido e que `python3 -m unittest tests.release.test_release_config -v` passa

## 2. Verificação do cálculo de versões

- [x] 2.1 Rodar, numa pasta temporária fora do repositório, a simulação com `release-please@17.6.0` e `17.11.2` e verificar que `1.0.0-alpha.1` resulta em `1.0.0` (commits só de documentação, com `feat` e com incompatível) e que depois da `1.0.0` os bumps são `1.1.0`, `1.0.1` e `2.0.0`; registrar a saída e a armadilha da estratégia padrão

## 3. Documentação

- [x] 3.1 Atualizar a seção de pré-lançamento do `README.md` (a configuração já está na versão final, mesclar o PR de release publica a `1.0.0`, as chaves de pré-lançamento saem depois da tag, o consumo da tag nova só depois de ela existir) e verificar relendo que cobre os cenários da spec
- [x] 3.2 Atualizar "Cuidados de release" do `CLAUDE.md` com a regra de manter `versioning: prerelease` até a tag `v1.0.0` e verificar que o texto está no arquivo
- [x] 3.3 Registrar a preparação da `1.0.0` no `CHANGELOG.md` (o que muda, a simulação, o que fica para depois do merge e a retrospectiva) e verificar que o texto lista o que foi entregue

## 4. Integração

- [x] 4.1 Rodar `python3 -m unittest discover -s tests -t . -v` e `openspec validate versao-final-1-0-0 --strict` e verificar que passam
- [x] 4.2 Rodar `grep -rniE "cowboy|cobol|cobc|calculadora" .apm .claude .agents .github` e verificar que volta vazia

## Workflow follow-up

- Abrir o PR com título `ci(release): …` e esperar o "ok" do Elói para o push e a mesclagem.
- Depois do merge: conferir que o bot atualizou o PR de release para `1.0.0` (título, `apm.yml`, manifesto e CHANGELOG); o Elói mescla o PR de release.
- Depois da tag `v1.0.0`: trocar o consumo do README, apontar o `calculadora_go` para a `v1.0.0`, remover `versioning` e `prerelease-type` e arquivar a change.
