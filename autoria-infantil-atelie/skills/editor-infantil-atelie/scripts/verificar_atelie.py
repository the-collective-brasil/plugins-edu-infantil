#!/usr/bin/env python3
"""
verificar_atelie.py - conferencia mecanica de uma aula de Atelie de Arte (Educacao Infantil,
Intercriativa Lab): titulo, Materiais e Preparacao e os 4 Momentos.

Confere:
  - os 4 Momentos fixos, nesta ordem (templates-de-aula.md, secao 3): linhas "N | Nome" seguidas
    de itens "- "
  - nome do Momento ate 30 caracteres (com Criar + nome da obra)
  - Rotina de Abertura no primeiro item do Momento 1 e Rotina de Encerramento no ultimo item do
    Momento 4, com [codigo biblioteca] (templates-de-aula.md, secao 4)
  - cabecalho da aula com "Atelie de Arte:" e titulo (aviso se faltar)
  - bloco acima de 600 caracteres visiveis e Materiais acima de 270, sem contar
    "[codigo biblioteca]" (aviso: o ajuste final e da editor-infantil-orientacoes-do-educador)
  - travessao (erro, menos "Eu Faco - Nos Fazemos - Voce Faz"; fala citada de livro e aviso),
    falas entre aspas, termos proibidos e nomes aposentados (termos-e-nomes.md, secao 8)

Uso:
  python3 verificar_atelie.py aula.md
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import os, re, sys, unicodedata

FIXOS = ["apresentar o desafio", "explorar e experimentar", "criar *",
         "organizar e encerrar"]  # templates-de-aula.md, secao 3; "criar *" = Criar + nome da obra
LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)")
MARCADOR_RE = re.compile(r"\s*\[c[oó]digo biblioteca\]", re.I)
# pessoas: nunca (termos-e-nomes.md, secao 8)
PROIBIDOS = ["aluno", "aluna", "alunos", "alunas", "estudante", "estudantes", "educando",
             "educandos", "professor", "professora", "professores", "tia", "tias", "pais",
             "educadora"]
# nomes aposentados -> nome atual (termos-e-nomes.md, secao 8)
APOSENTADOS = [
    ("atelie de artes", "Ateliê de Arte"),
    ("artes visuais", "Ateliê de Arte"),
    ("expressao criativa", "Ateliê de Arte"),
    ("g3", "Infantil 3"), ("g4", "Infantil 4"), ("g5", "Infantil 5"),
    ("dirigida pelas criancas", "Dirigida pela criança"),
    ("rotina de organizacao", "Rotina de Encerramento"),
    ("rotina de abertura do atelie", "Rotina de Abertura"),
    ("rotina de encerramento do atelie", "Rotina de Encerramento"),
    ("roda de partilha", "Roda (nao e termo)"),
    ("roteiro do educador", "Orientações do Educador"),
    ("protagonistas lab", "Intercriativa Lab"),
    ("story time", "Hora do Conto"),
    ("caderno fazer e brincar", "Fazer e Brincar"),
    ("conexao com as familias", "Conexão Casa-Escola"),
]
TRAVESSAO_OK = "eu faco - nos fazemos - voce faz"


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


def visivel(s):
    s = MARCADOR_RE.sub("", s)  # o marcador nao conta no limite
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
    m = re.search(r"^(?:#{2,4}\s*|\*\*)Materiais e Prepara\S*?\**\s*\n(.*?)(?=^#{1,4}\s|^\**\s*\d+\s*\||\Z)",
                  text, re.M | re.S | re.I)
    return m.group(1).strip() if m else None


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 verificar_atelie.py aula.md")
    if not os.path.exists(sys.argv[1]):
        sys.exit("Arquivo nao encontrado: %s" % sys.argv[1])
    text = open(sys.argv[1], encoding="utf-8").read()
    erros, avisos = [], []

    if not re.search(r"ateli[eê] de arte:\s*\S", text, re.I):
        avisos.append("Nao achei o cabecalho 'Ateliê de Arte: [Título da aula]' (titulo e linha de abertura).")

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
        if len(nome) > 30:
            erros.append("[%s] nome com %d caracteres (max 30)." % (titulo, len(nome)))
        n = sum(len(visivel(i)) for i in itens)
        if n > 600:
            avisos.append("[%s] bloco com %d caracteres (pagina: max 600)." % (titulo, n))

    if len(ms) == 4:
        primeiro = acc(ms[0][1][0]) if ms[0][1] else ""
        ultimo = acc(ms[3][1][-1]) if ms[3][1] else ""
        if not ("rotina de abertura" in primeiro and "codigo biblioteca" in primeiro):
            erros.append("O Momento 1 deve abrir com 'Siga a *Rotina de Abertura* [código biblioteca]'.")
        if not ("rotina de encerramento" in ultimo and "codigo biblioteca" in ultimo):
            erros.append("O Momento 4 deve fechar com 'Siga a *Rotina de Encerramento* [código biblioteca]'.")

    mat = materiais(text)
    if mat is None:
        avisos.append("Nao achei a secao Materiais e Preparacao.")
    elif len(visivel(mat)) > 270:
        avisos.append("Materiais e Preparacao com %d caracteres (pagina: max 270)." % len(visivel(mat)))

    for i, line in enumerate(text.splitlines(), 1):
        flat = acc(line)
        if "—" in line or "–" in line or re.search(r"\s-{2,3}\s|-{3}", line):
            if TRAVESSAO_OK in flat.replace("—", "-").replace("–", "-"):
                pass
            elif re.search(r"[\"“”]", line) or re.search(r"\b(disse|diz|falou|gritou|perguntou)\b", flat):
                avisos.append("linha %d: travessao. So vale em fala citada de um livro; confira." % i)
            else:
                erros.append("linha %d: travessao. A casa nao usa travessao (nem -- ou ---)." % i)
        if re.search(r"[\"“”][^\"“”]{3,}[\"“”]", line):
            erros.append("linha %d: texto entre aspas. Fala do educador vai em italico, sem aspas." % i)
        for w in PROIBIDOS:
            if re.search(r"\b%s\b" % w, flat):
                erros.append("linha %d: use crianca(s), educador ou familias e responsaveis, nunca '%s'." % (i, w)); break
        for velho, novo in APOSENTADOS:
            if re.search(r"\b%s\b" % re.escape(velho), flat):
                erros.append("linha %d: nome aposentado '%s'; escreva %s." % (i, velho, novo)); break
        if "cada crianca" in flat:
            erros.append("linha %d: use a crianca ou as criancas, nunca cada crianca." % i)
        if re.search(r"\bamigo?s?\b|\bamiga?s?\b", flat):
            avisos.append("linha %d: 'amigo' como termo neutro; a casa usa colega." % i)
        if re.search(r"\bfamilias?\b", flat) and "familias e responsaveis" not in flat:
            avisos.append("linha %d: 'familia(s)' sozinho; a casa escreve familias e responsaveis." % i)
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
