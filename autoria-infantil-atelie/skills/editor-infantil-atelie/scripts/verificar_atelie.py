#!/usr/bin/env python3
"""
verificar_atelie.py - conferencia mecanica dos Momentos e dos Materiais de uma aula de Atelie
de Arte (Educacao Infantil, Intercriativa Lab).

Confere:
  - os 4 Momentos fixos, nesta ordem (termos-e-nomes 6.1) (linhas "N | Nome" seguidas de itens "- ")
  - nome do Momento ate 28 caracteres (com Criar + nome da obra)
  - bloco acima de 600 caracteres visiveis e Materiais acima de 270 (aviso: o ajuste final e da
    editor-infantil-orientacoes-do-educador)
  - travessao, falas entre aspas, termos proibidos

A pagina da crianca e conferida a mao contra o template.

Uso:
  python3 verificar_atelie.py aula.md
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import os, re, sys, unicodedata

FIXOS = ["apresentar o desafio", "explorar e experimentar", "criar *",
         "organizar e encerrar"]  # termos-e-nomes 6.1; "criar *" = Criar + nome da obra
LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)")
PROIBIDOS = ["aluno", "aluna", "alunos", "alunas", "estudante", "estudantes", "educando",
             "educandos", "professor", "professora"]


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


def visivel(s):
    return re.sub(r"\*+", "", LINK_RE.sub(r"\1", s)).strip()


def momentos(text):
    out, cur = [], None
    for line in text.splitlines():
        t = line.strip()
        core = re.sub(r"\*+", "", t).lstrip("#").strip()
        if re.match(r"^\d+\s*\|\s*.+", core):
            cur = [core, []]; out.append(cur); continue
        if re.match(r"^#{1,4}\s+\S", t) or re.match(r"^\*\*[^*]+\*\*\s*$", t):
            cur = None; continue
        if cur is not None:
            if t.startswith("- "):
                cur[1].append(t[2:].strip())
            elif t and cur[1] and line[:1] in (" ", "\t"):
                cur[1][-1] += " " + t
            elif t:
                cur = None
    return out


def materiais(text):
    m = re.search(r"^#{2,4}\s*Materiais e Prepara\S*\s*\n(.*?)(?=^#{1,4}\s|^\**\s*\d+\s*\||\Z)", text, re.M | re.S | re.I)
    return m.group(1).strip() if m else None


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 verificar_atelie.py aula.md")
    if not os.path.exists(sys.argv[1]):
        sys.exit("Arquivo nao encontrado: %s" % sys.argv[1])
    text = open(sys.argv[1], encoding="utf-8").read()
    erros, avisos = [], []

    ms = momentos(text)
    nomes = [acc(re.sub(r"^\d+\s*\|\s*", "", t)).strip() for t, _ in ms]
    ok = len(nomes) == 4 and all(
        (n.startswith("criar ") and len(n) > 6 if f == "criar *" else n == f)
        for n, f in zip(nomes, FIXOS))
    if not ok:
        erros.append("Os Momentos devem ser os 4 fixos, nesta ordem: Apresentar o desafio · "
                     "Explorar e experimentar · Criar [nome da obra] · Organizar e Encerrar. "
                     "Encontrados: %s" % (" · ".join(t for t, _ in ms) or "nenhum"))
    if any("[nome da obra]" in acc(t) for t, _ in ms):
        erros.append("O marcador [nome da obra] ficou na pagina. Troque pelo nome da obra.")
    for titulo, itens in ms:
        nome = re.sub(r"^\d+\s*\|\s*", "", titulo).strip()
        if len(nome) > 28:
            erros.append("[%s] nome com %d caracteres (max 28)." % (titulo, len(nome)))
        n = sum(len(visivel(i)) for i in itens)
        if n > 600:
            avisos.append("[%s] bloco com %d caracteres (pagina: max 600)." % (titulo, n))

    mat = materiais(text)
    if mat is None:
        avisos.append("Nao achei a secao Materiais e Preparacao.")
    elif len(visivel(mat)) > 270:
        avisos.append("Materiais e Preparacao com %d caracteres (pagina: max 270)." % len(visivel(mat)))

    for i, line in enumerate(text.splitlines(), 1):
        flat = acc(line)
        if "—" in line or "–" in line:
            erros.append("linha %d: travessao. A casa nao usa travessao." % i)
        if re.search(r"[\"“”][^\"“”]{3,}[\"“”]", line):
            erros.append("linha %d: texto entre aspas. Fala do educador vai em italico, sem aspas." % i)
        for w in PROIBIDOS:
            if re.search(r"\b%s\b" % w, flat):
                erros.append("linha %d: use crianca(s) ou educador, nunca '%s'." % (i, w)); break
        if "cada crianca" in flat:
            erros.append("linha %d: use a crianca ou as criancas, nunca cada crianca." % i)
        if re.search(r"\batelier\b", flat):
            avisos.append("linha %d: grafia Atelier. No texto, use Ateliê." % i)

    if erros:
        print("ERROS (%d)" % len(erros)); [print("  " + e) for e in erros]
    if avisos:
        print("\nAVISOS (%d)" % len(avisos)); [print("  " + a) for a in avisos]
    if not erros and not avisos:
        print("Nenhum problema mecanico encontrado.")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
