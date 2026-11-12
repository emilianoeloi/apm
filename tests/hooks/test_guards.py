"""Cenários da spec hook-runtime para os guardas de Bash e de escrita e para o session-start."""

import json

from tests.hooks._util import ProjectCase

BASH = "pre-tool-bash-guard.py"
WRITE = "pre-tool-write-guard.py"
SESSION = "session-start.py"


def claude_bash(command: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def copilot_bash(command: str) -> dict:
    return {"toolName": "bash", "toolArgs": {"command": command}}


def claude_write(path: str) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": path}}


def copilot_write(path: str) -> dict:
    return {"toolName": "create", "toolArgs": {"path": path}}


class BashGuardTest(ProjectCase):
    def assertBlockedClaude(self, command: str):
        result = self.run_hook(BASH, claude_bash(command))
        self.assertEqual(result.returncode, 2, f"{command!r} deveria bloquear: {result.stdout} {result.stderr}")
        self.assertTrue(result.stderr.strip(), "o motivo deve ir para stderr")
        self.assertNoTraceback(result)
        return result

    def assertAllowedClaude(self, command: str):
        result = self.run_hook(BASH, claude_bash(command))
        self.assertEqual(result.returncode, 0, f"{command!r} deveria passar: {result.stderr}")
        self.assertNoTraceback(result)
        return result

    # --- Bloqueios embutidos valem sem configuração

    def test_defesas_embutidas_sem_configuracao(self):
        for command in (
            "git push origin main",
            "git reset --hard HEAD~1",
            "git clean -fd",
            "git branch -D velha",
            "rm -rf build",
            "rm -Rf build",
            "echo X > .env",
        ):
            with self.subTest(command=command):
                self.assertBlockedClaude(command)

    def test_comandos_inofensivos_passam(self):
        for command in ("git status", "git branch -vv", "git branch -a", "git log --oneline", "ls -la", "git add -A"):
            with self.subTest(command=command):
                self.assertAllowedClaude(command)

    # --- Só o comando bloqueia; a menção em texto não

    def test_mencao_em_texto_nao_bloqueia(self):
        for command in (
            'echo "lembrete: git push so com ok do usuario"',
            'git commit -m "docs: explica o bloqueio de git push"',
            "grep -rn 'git reset --hard' docs/",
            "cat notas.txt # rm -rf nao rodar",
            "echo 'texto com `git push` entre crases e (git push depois) entre parenteses'",
            "gh pr create --body 'bloqueia `git push`, `git reset --hard` e `rm -rf`'",
        ):
            with self.subTest(command=command):
                self.assertAllowedClaude(command)

    def test_comando_em_qualquer_posicao_de_comando_bloqueia(self):
        for command in (
            "ls && git push origin main",
            "ls; git push",
            "ls | git push",
            "(git push)",
            "echo $(git push)",
            "  git push",
            "ls\ngit push",
            "sudo rm -rf /x",
            "make clean && rm -rf build",
        ):
            with self.subTest(command=command):
                self.assertBlockedClaude(command)

    # --- Decisão no formato de cada host

    def test_bloqueio_no_copilot_e_json_com_codigo_zero(self):
        result = self.run_hook(BASH, copilot_bash("git push origin main"))
        self.assertEqual(result.returncode, 0)
        decision = json.loads(result.stdout)
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertTrue(decision["permissionDecisionReason"])

    def test_permissao_no_copilot_e_json_allow(self):
        result = self.run_hook(BASH, copilot_bash("git status"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["permissionDecision"], "allow")

    def test_permissao_no_claude_nao_imprime_nada(self):
        result = self.assertAllowedClaude("git status")
        self.assertEqual(result.stdout, "")

    # --- Configuração e payload inválidos nunca travam

    def test_configuracao_corrompida_permite_o_inofensivo_e_mantem_as_defesas(self):
        self.write_config("{ isto não é json")
        self.assertAllowedClaude("ls")
        self.assertBlockedClaude("git push")

    def test_configuracao_que_nao_e_objeto(self):
        self.write_config("[1, 2, 3]")
        self.assertAllowedClaude("ls")
        self.assertBlockedClaude("git push")

    def test_entradas_malformadas_na_configuracao_sao_ignoradas(self):
        self.write_config(
            {
                "blocked_bash_patterns": [
                    {"reason": "sem pattern"},
                    {"pattern": "[regex quebrada"},
                    "texto solto",
                    {"pattern": "\\bsudo\\b", "reason": "sudo bloqueado"},
                ],
                "proposal_blocked_bash_patterns": "não é lista",
            }
        )
        self.assertAllowedClaude("ls")
        result = self.assertBlockedClaude("sudo ls")
        self.assertIn("sudo bloqueado", result.stderr)

    def test_payload_invalido_nao_trava(self):
        for stdin in ("isto não é json", "", "[1, 2]", "null"):
            with self.subTest(stdin=stdin):
                result = self.run_hook(BASH, stdin)
                self.assertEqual(result.returncode, 0)
                self.assertNoTraceback(result)

    def test_payload_de_host_desconhecido_permite(self):
        result = self.run_hook(BASH, {"qualquer": "coisa"})
        self.assertEqual(result.returncode, 0)

    # --- Fase proposal

    def test_proposal_bloqueia_commit_e_apply_libera(self):
        self.write_config(
            {"proposal_blocked_bash_patterns": [{"pattern": "\\bgit\\s+commit\\b", "label": "git commit"}]}
        )
        self.set_phase("proposal")
        self.assertBlockedClaude("git commit -m x")
        self.set_phase("apply")
        self.assertAllowedClaude("git commit -m x")

    def test_estado_de_fase_corrompido_nao_bloqueia(self):
        self.write_config(
            {"proposal_blocked_bash_patterns": [{"pattern": "\\bgit\\s+commit\\b", "label": "git commit"}]}
        )
        (self.root / ".harness").mkdir()
        (self.root / ".harness" / "change-phase.json").write_text("[1, 2]", encoding="utf-8")
        self.assertAllowedClaude("git commit -m x")


class WriteGuardTest(ProjectCase):
    def blocked(self, path: str, payload_factory=claude_write):
        result = self.run_hook(WRITE, payload_factory(path))
        self.assertEqual(result.returncode, 2, f"{path!r} deveria bloquear: {result.stdout} {result.stderr}")
        self.assertTrue(result.stderr.strip())
        self.assertNoTraceback(result)
        return result

    def allowed(self, path: str):
        result = self.run_hook(WRITE, claude_write(path))
        self.assertEqual(result.returncode, 0, f"{path!r} deveria passar: {result.stderr}")
        self.assertNoTraceback(result)
        return result

    # --- Defesas embutidas e contenção de caminho

    def test_credenciais_bloqueadas_sem_configuracao(self):
        for name in (".env", "service_account.json", "id_rsa", "chave.pem", "app.keystore"):
            with self.subTest(name=name):
                self.blocked(str(self.root / name))

    def test_caminho_dentro_do_repositorio_passa(self):
        (self.root / "src").mkdir()
        self.allowed(str(self.root / "src" / "a.py"))
        self.allowed("src/b.py")

    def test_pasta_irma_com_nome_parecido_e_bloqueada(self):
        outro = self.parent / "proj-outro"
        outro.mkdir()
        self.blocked(str(outro / "arquivo.txt"))

    def test_path_traversal_e_bloqueado(self):
        self.blocked("../fora.txt")

    def test_caminho_absoluto_fora_e_bloqueado(self):
        self.blocked(str(self.parent / "fora.txt"))

    # --- Raízes extras permitidas (opt-in; o padrão continua estrito)

    def test_raiz_extra_permitida_libera_so_ela(self):
        liberada = self.parent / "liberada"
        outra = self.parent / "outra"
        liberada.mkdir()
        outra.mkdir()
        self.write_config({"allowed_write_roots": [str(liberada)]})
        self.allowed(str(liberada / "a.txt"))
        self.blocked(str(outra / "a.txt"))
        self.blocked(str(self.parent / "liberada-irma" / "a.txt"))

    def test_raiz_extra_nao_libera_credencial(self):
        liberada = self.parent / "liberada"
        liberada.mkdir()
        self.write_config({"allowed_write_roots": [str(liberada)]})
        self.blocked(str(liberada / ".env"))

    def test_raiz_extra_relativa_ou_invalida_e_ignorada(self):
        (self.parent / "rel").mkdir()
        self.write_config({"allowed_write_roots": ["../rel", 5, None, ""]})
        self.blocked(str(self.parent / "rel" / "a.txt"))

    def test_raiz_extra_aceita_variavel_de_ambiente(self):
        liberada = self.parent / "viaenv"
        liberada.mkdir()
        self.extra_env["HARNESS_TESTE_RAIZ"] = str(liberada)
        self.write_config({"allowed_write_roots": ["$HARNESS_TESTE_RAIZ"]})
        self.allowed(str(liberada / "a.txt"))

    def test_raiz_extra_vale_tambem_na_fase_proposal(self):
        liberada = self.parent / "liberada"
        liberada.mkdir()
        self.write_config(
            {"allowed_write_roots": [str(liberada)], "planning_write_prefixes": ["openspec/"], "code_prefixes": ["src/"]}
        )
        self.set_phase("proposal")
        self.allowed(str(liberada / "a.txt"))
        self.blocked("src/a.py")

    # --- Decisão no formato de cada host

    def test_bloqueio_no_copilot_e_json_com_codigo_zero(self):
        result = self.run_hook(WRITE, copilot_write(str(self.root / ".env")))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["permissionDecision"], "deny")

    def test_payload_sem_caminho_permite(self):
        result = self.run_hook(WRITE, {"tool_name": "Write", "tool_input": {}})
        self.assertEqual(result.returncode, 0)

    # --- Configuração e payload inválidos nunca travam

    def test_configuracao_corrompida_permite_o_inofensivo(self):
        self.write_config("{ nope")
        self.allowed("src/a.py")
        self.blocked(str(self.root / ".env"))

    def test_configuracao_que_nao_e_objeto(self):
        self.write_config('"texto"')
        self.allowed("src/a.py")

    def test_tipos_errados_na_configuracao_viram_padrao(self):
        self.write_config(
            {
                "blocked_filenames": "não é lista",
                "blocked_filename_suffixes": 7,
                "planning_write_prefixes": {"a": 1},
                "code_prefixes": [1, None],
            }
        )
        self.allowed("src/a.py")
        self.blocked(str(self.root / ".env"))

    def test_payload_invalido_nao_trava(self):
        for stdin in ("isto não é json", "", "[1, 2]"):
            with self.subTest(stdin=stdin):
                result = self.run_hook(WRITE, stdin)
                self.assertEqual(result.returncode, 0)
                self.assertNoTraceback(result)

    # --- Fase proposal

    def test_proposal_bloqueia_codigo_e_libera_planejamento(self):
        self.write_config({"planning_write_prefixes": ["openspec/"], "code_prefixes": ["src/"]})
        self.set_phase("proposal")
        result = self.blocked("src/a.py")
        self.assertIn("proposal", result.stderr)
        self.allowed("openspec/changes/x/proposal.md")
        self.set_phase("apply")
        self.allowed("src/a.py")


class SessionStartTest(ProjectCase):
    def context(self, stdin=None) -> str:
        result = self.run_hook(SESSION, stdin if stdin is not None else {"source": "new"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNoTraceback(result)
        return json.loads(result.stdout)["additionalContext"]

    def test_sem_configuracao_injeta_contexto(self):
        self.assertIn("Harness", self.context())

    def test_resume_nao_injeta_nada(self):
        result = self.run_hook(SESSION, {"source": "resume"})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {})

    def test_configuracao_corrompida_ou_que_nao_e_objeto(self):
        for text in ("{ nope", "[1, 2]", "null"):
            with self.subTest(text=text):
                self.write_config(text)
                self.assertIn("Harness", self.context())

    def test_guias_malformados_sao_ignorados(self):
        self.write_config({"guide_files": [1, "x", {"label": "sem path"}, {"path": "CLAUDE.md", "label": "regras"}]})
        (self.root / "CLAUDE.md").write_text("x", encoding="utf-8")
        context = self.context()
        self.assertIn("regras", context)

    def test_payload_invalido_nao_trava(self):
        for stdin in ("isto não é json", "", "[1]"):
            with self.subTest(stdin=stdin):
                result = self.run_hook(SESSION, stdin)
                self.assertEqual(result.returncode, 0)
                self.assertNoTraceback(result)

    def test_mostra_a_fase_declarada(self):
        self.set_phase("proposal", "minha-change")
        self.assertIn("proposal (minha-change)", self.context())


if __name__ == "__main__":
    import unittest

    unittest.main()
