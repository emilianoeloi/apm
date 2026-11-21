#!/usr/bin/env python3
"""Confere o vínculo cenário-teste: cada `Cenário:` novo ou alterado das changes ativas tem de ter um teste.

Uso:
  spec-trace.py [--root DIR] [--change NOME] [--tests CAMINHO ...]

O vínculo é a linha literal `Spec: <capability> / <requisito> / <cenário>` (comentário, nome ou rótulo do
teste). Estados por linha de saída (`spec-trace: <ESTADO> <trinca> [@ arquivo:linha]`):
  COBERTO            a trinca aparece em algum arquivo de texto da busca
  SEM_TESTE          cenário novo ou alterado sem a linha (pesa na saída)
  HERDADO_SEM_TESTE  cenário de requisito MODIFIED idêntico ao da spec principal, sem a linha (informativo)
  ORFAO              linha com `Spec:` e dois ou mais ` / ` que não casa com nenhum cenário efetivo
  AMBIGUO            trincas distintas com o mesmo literal (nomes com ` / ` que colidem)
Casamento por prefixo mais longo, para aceitar fechamento de comentário depois do título.

Busca padrão: arquivos de texto da raiz, menos pastas de controle e de dependências, `.md`, binários e
arquivos acima de 1 MiB. `--tests` restringe a busca aos caminhos dados (as exclusões de pasta não valem).

Saída 2 não é o veredito: `SEM_TESTE` pesa como severidade alta (o reviewer reprova), mas `ORFAO` e
`AMBIGUO` também saem 2 e são de severidade média (ressalva, não reprovação); quem decide é o agente.
Fim do título: o resto da linha deve ser vazio ou começar (após espaço, tab ou NBSP) por um fechamento
conhecido (CLOSERS: `*/`, `-->`, `--]]`, `--}}`, `%}`, `?>`, `"`, `'`, `` ` ``, `)`, `]`, `}`, `#`, `//`); qualquer
outro sufixo (`-`, `_`, `.`, `(`, letra ou dígito) deixa a linha sem casar, e ela vira `ORFAO`.
Depois do fechamento, só vale o fim da linha, espaço (tab e NBSP inclusive) ou outro fechamento conhecido: `#2`,
`"abc` e `*/x` não casam; `") # x` e `*/ -->` casam.

Somente leitura: não cria nem altera arquivo, não grava bytecode e não chama git. Prova o vínculo, nunca a
qualidade do teste. Saída: 0 se não há SEM_TESTE, ORFAO nem AMBIGUO; 2 nos demais casos (erro inesperado inclusive).
"""

import argparse
import os
import stat
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # antes de importar os módulos locais: nenhum __pycache__ novo
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common  # noqa: E402
import _gherkin  # noqa: E402

EXCLUDED_DIRS = frozenset({
    ".git", "openspec", "spdd", ".harness", ".claude", ".github", ".agents", ".apm", "apm_modules",
    "node_modules", "vendor", "target", "build", "dist", "__pycache__", ".venv", "venv",
})
MAX_BYTES = 1024 * 1024
MARK = "Spec:"
SEP = " / "
CLOSERS = ("*/", "-->", "--]]", "--}}", "%}", "?>", '"', "'", "`", ")", "]", "}", "#", "//")


def norm(steps: str) -> str:
    return " ".join(steps.split())


def literal(capability: str, name: str, title: str) -> str:
    return f"{capability}{SEP}{name}{SEP}{title}"


def required_scenarios(root: Path, only: str):
    """(lista de (trinca, estado), extras, nomes das changes vistas); estado `NOVO` ou `HERDADO`."""
    changes = root / "openspec" / "changes"
    found, extras, seen = {}, 0, set()
    for path in sorted(changes.glob("*/specs/*/spec.md")):
        change = path.relative_to(changes).parts[0]
        if change == "archive" or (only and change != only):
            continue
        seen.add(change)
        capability = path.parent.name
        text, problem = _gherkin._read(path)
        if text is None:
            sys.stderr.write(f"spec-trace: {path.relative_to(root)}: {problem}\n")
            continue
        delta = _gherkin.parse_delta(text)
        base_text, _ = _gherkin._read(root / "openspec" / "specs" / capability / "spec.md")
        base = _gherkin.parse_requirements(base_text) if base_text else {}
        back = {new: old for old, new in delta["RENAMED"].items()}
        for kind in ("MODIFIED", "ADDED"):
            for name, body in delta[kind].items():
                scenarios = _gherkin.parse_scenarios(body)
                titles = {title for title, _ in scenarios}
                extras += len([t for t in _gherkin.SCENARIO.findall(body) if t not in titles])
                old = {t: norm(s) for t, s in _gherkin.parse_scenarios(base.get(back.get(name, name), ""))}
                for title, steps in scenarios:
                    key = (capability, name, title)
                    inherited = kind == "MODIFIED" and old.get(title) == norm(steps)
                    if found.get(key) != "NOVO":
                        found[key] = "HERDADO" if inherited else "NOVO"
    return list(found.items()), extras, seen


def candidate_files(root: Path, tests: list):
    seen = set()
    roots = [Path(t) if os.path.isabs(t) else root / t for t in tests] if tests else [root]
    for start in roots:
        if start.is_file():
            walked = [(start.parent, [], [start.name])]
        else:
            walked = os.walk(start)
        for folder, dirs, files in walked:
            if not tests:
                dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
            else:
                dirs.sort()
            for name in sorted(files):
                path = Path(folder) / name
                if path not in seen:
                    seen.add(path)
                    yield path


def read_text(path: Path):
    """Texto do arquivo ou None se não for arquivo regular, for link, `.md`, grande, binário ou ilegível.

    Abre sem seguir link e sem bloquear (onde o sistema oferece) e confere o tipo no descritor já aberto:
    o arquivo trocado por FIFO, dispositivo ou link depois da listagem é ignorado, sem janela de corrida.
    """
    if path.suffix.lower() == ".md":
        return None
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return None
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):  # FIFO, dispositivo: ler pode travar
            return None
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            data = handle.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES or b"\0" in data:
            return None
        return data.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    finally:
        os.close(descriptor)


def ends_title(rest: str) -> bool:
    """True se o resto da linha após o título é vazio ou começa (após espaços) por um fechamento conhecido.

    Depois de cada fechamento vem uma fronteira: fim da linha, espaço (tab e NBSP inclusive) ou outro
    fechamento conhecido; qualquer outro caractere colado ao fechamento (`#2`, `"abc`, `*/x`) não casa.
    """
    rest = rest.lstrip()
    if not rest:
        return True
    while True:
        closer = next((c for c in CLOSERS if rest.startswith(c)), None)
        if closer is None:
            return False
        rest = rest[len(closer):]
        if not rest or rest[0].isspace():
            return True


def scan(root: Path, tests: list, literals: set):
    """({literal: [arquivo:linha]}, [(arquivo:linha, texto)] de órfãos)."""
    hits, orphans = {}, []
    ordered = sorted(literals, key=len, reverse=True)
    for path in candidate_files(root, tests):
        text = read_text(path)
        if text is None or MARK not in text:
            continue
        try:
            shown = path.relative_to(root).as_posix()
        except ValueError:
            shown = str(path)
        for number, line in enumerate(text.splitlines(), 1):
            index = line.find(MARK)
            if index < 0:
                continue
            after = line[index + len(MARK):].lstrip()
            match = next((lit for lit in ordered if after.startswith(lit) and ends_title(after[len(lit):])), None)
            if match:
                hits.setdefault(match, []).append(f"{shown}:{number}")
            elif after.count(SEP) >= 2:
                orphans.append((f"{shown}:{number}", after.rstrip()))
    return hits, orphans


def trace(root: Path, only: str, tests: list) -> int:
    if not (root / "openspec").is_dir():
        sys.stderr.write(f"spec-trace: sem openspec/ em {root}; não há specs para conferir.\n")
        return 0
    required, extras, seen = required_scenarios(root, only)
    if only and only not in seen:
        sys.stderr.write(f"spec-trace: change '{only}' não encontrada entre as changes ativas.\n")
        return 2
    if not seen:
        sys.stderr.write("spec-trace: nenhuma change ativa com deltas de spec; nada a conferir.\n")
        return 0
    owners = {}
    for item in _gherkin.effective_requirements(root):
        if item.error:
            continue
        for title, _ in _gherkin.parse_scenarios(item.body):
            owners.setdefault(literal(item.capability, item.name, title), set()).add((item.capability, item.name, title))
    ambiguous = {key for keys in owners.values() if len(keys) > 1 for key in keys}
    hits, orphans = scan(root, tests, set(owners))
    counts = {"coberto": 0, "sem_teste": 0, "herdado_sem_teste": 0, "orfao": 0, "ambiguo": 0}
    out = []

    def emit(state: str, text: str, where: str = "") -> None:
        counts[state.lower() if state != "COBERTO" else "coberto"] += 1
        out.append(f"spec-trace: {state} {text}" + (f" @ {where}" if where else ""))

    for key in sorted(ambiguous):
        emit("AMBIGUO", literal(*key))
    for key, state in required:
        if key in ambiguous:
            continue
        lit = literal(*key)
        if hits.get(lit):
            emit("COBERTO", lit, ", ".join(hits[lit]))
        else:
            emit("SEM_TESTE" if state == "NOVO" else "HERDADO_SEM_TESTE", lit)
    for where, text in orphans:
        emit("ORFAO", text, where)
    summary = ", ".join(f"{name} {count}" for name, count in counts.items())
    print("\n".join(out + [f"spec-trace: resumo: {summary}, extras: {extras}"]))
    return 2 if counts["sem_teste"] or counts["orfao"] or counts["ambiguo"] else 0


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(
        prog="spec-trace.py",
        description="Confere o vínculo cenário-teste. A saída 2 não é o veredito: ORFAO e AMBIGUO também saem 2, "
        "mas são de severidade média; só SEM_TESTE reprova.",
    )
    parser.add_argument("--root", help="raiz do projeto (padrão: a do harness)")
    parser.add_argument("--change", default="", help="só os deltas desta change são exigidos")
    parser.add_argument("--tests", action="append", default=[], help="caminho a pesquisar (repetível)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else _common.project_root()
    try:
        return trace(root, args.change, args.tests)
    except Exception as error:  # noqa: BLE001 - conferência que não roda não pode declarar aprovação
        sys.stderr.write(f"spec-trace: erro inesperado ({type(error).__name__}: {error}).\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
