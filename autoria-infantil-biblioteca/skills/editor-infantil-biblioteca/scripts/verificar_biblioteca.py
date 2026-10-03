#!/usr/bin/env python3
"""
verificar_biblioteca.py - conferencia mecanica de entradas da Biblioteca Digital (Educacao
Infantil, Intercriativa Lab) contra os 8 templates (dados/templates-biblioteca.md).

Confere:
  - template reconhecido (linha "Template: ..." ou pelo conjunto de campos)
  - campos fixos, na ordem, sem campo extra, sem campo vazio
  - Como conduzir com exatamente 3 passos numerados (Estrategia e Rotina)
  - as 4 partes de Como jogar ou brincar (Jogo) e as 6 de Orientacoes para producao (Imprimivel)
  - travessao (erro), marcadores de preenchimento (erro), termos proibidos e nomes aposentados
  - texto em ingles (aviso), instrucao longa ou com varias acoes (aviso), curriculo repetido
    na entrada (aviso)
  - titulo igual em outra entrada conferida junto (erro: um recurso, uma entrada)

Uso:
  python3 verificar_biblioteca.py entrada.md [outra.md ...]
  python3 verificar_biblioteca.py pasta/                    (todos os .md da pasta)
  python3 verificar_biblioteca.py pasta/ --git-base origin/main   (so os novos ou editados)
  python3 verificar_biblioteca.py entrada.md --template 3   (forca o template: numero ou nome)
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import os, re, subprocess, sys, unicodedata


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


def norm(s):
    s = re.sub(r"[*_`#]", "", acc(s))
    s = re.sub(r"\s*/\s*", "/", s)
    return re.sub(r"\s+", " ", s).strip(" :.").strip()


# (numero, nome, campos em ordem, partes por campo)
JOGO_PARTES = ["Começar", "Primeira rodada", "Alternar, repetir ou avançar", "Fechar"]
IMPR_PARTES = ["Formato", "Composição", "Texto", "Imagens", "Manuseio", "Integridade do recurso"]
TEMPLATES = [
    (1, "Jogo ou Prática Lúdica",
     ["O que é", "Materiais e preparação", "Como jogar ou brincar", "Apoio e desafio", "Observe"],
     {"Como jogar ou brincar": JOGO_PARTES}),
    (2, "Estratégia",
     ["O que é", "Quando utilizar", "Materiais e preparação", "Como conduzir", "Observe", "Dica"],
     {}),
    (3, "Rotina",
     ["Finalidade", "Quando utilizar", "Materiais e preparação", "Como conduzir", "Retomadas",
      "Dica"], {}),
    (4, "Material Imprimível",
     ["O que é", "Conteúdo do recurso", "Orientações para produção", "Como usar",
      "Arquivos finais"], {"Orientações para produção": IMPR_PARTES}),
    (5, "Música, Canto, Parlenda ou Aquecimento",
     ["O que é", "Conteúdo", "Áudio/ritmo e movimentos", "Como conduzir",
      "Variações e cuidados", "Arquivos finais"], {}),
    (6, "Imagem Projetável, Áudio ou Vídeo",
     ["O que é", "Conteúdo", "Orientações para produção", "Como usar", "Acessibilidade",
      "Arquivos finais"], {}),
    (7, "Proposta do Banco de Ideias",
     ["O que é", "Modo de Brincar e papel do adulto", "Materiais e organização do espaço",
      "Convite para brincar", "Apoio/ampliação e segurança", "Observe"], {}),
    (8, "Guia de Prática Pedagógica",
     ["O que é", "Por que é importante", "Quando utilizar", "Princípios essenciais",
      "Como aparece na prática", "Exemplo", "Cuidados", "Observe"], {}),
]
PASSOS_3 = {2, 3}  # Estrategia e Rotina: Como conduzir em 3 passos numerados

# variantes aceitas de nome de campo (normalizadas) -> nome canonico normalizado
SINONIMOS = {
    "apoio, ampliacao e seguranca": "apoio/ampliacao e seguranca",
    "apoio e ampliacao e seguranca": "apoio/ampliacao e seguranca",
    "audio, ritmo e movimentos": "audio/ritmo e movimentos",
    "audio e ritmo e movimentos": "audio/ritmo e movimentos",
}

PROIBIDOS = ["aluno", "aluna", "alunos", "alunas", "estudante", "estudantes", "educando",
             "educandos", "professor", "professora", "professores", "tia", "tias", "pais",
             "educadora"]
APOSENTADOS = [
    ("atelie de artes", "Ateliê de Arte"), ("artes visuais", "Ateliê de Arte"),
    ("expressao criativa", "Ateliê de Arte"),
    ("g3", "Infantil 3"), ("g4", "Infantil 4"), ("g5", "Infantil 5"),
    ("rotina de organizacao", "Rotina de Encerramento"),
    ("roteiro do educador", "Orientações do Educador"),
    ("protagonistas lab", "Intercriativa Lab"), ("story time", "Hora do Conto"),
    ("caderno fazer e brincar", "Fazer e Brincar"),
    ("conexao com as familias", "Conexão Casa-Escola"),
]
PLACEHOLDER_RE = re.compile(r"\{\{|\}\}|\bTBD\b|\ba definir\b|lorem ipsum|\bxxx+\b|<[^>]*>", re.I)
COLCHETE_RE = re.compile(r"\[([^\]]*)\]")
INGLES = {"the", "and", "with", "your", "you", "then", "when", "children", "teacher", "use",
          "this", "that", "for", "are", "will", "have"}
SEQ_RE = re.compile(r"\b(e depois|e em seguida|em seguida|depois disso|e entao|e logo apos)\b")
CURRICULO_RE = re.compile(r"\bei0[1-3][a-z]{2}\d{2}\b|\bbncc\b|campos? de experiencia|eixos? transversais?")

HEAD_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
BOLD_RE = re.compile(r"^\*\*([^*]+?)\*\*\s*:?\s*$")
PASSO_RE = re.compile(r"^\s*\d+[.)]\s+\S")


def ler_entrada(texto):
    """-> titulo, template_declarado, secoes [(nivel, nome, linhas)]"""
    titulo, declarado, secoes, atual = None, None, [], None
    for linha in texto.splitlines():
        m = HEAD_RE.match(linha)
        b = BOLD_RE.match(linha.strip())
        if m and len(m.group(1)) == 1 and titulo is None:
            titulo = m.group(2).strip()
            continue
        if m:
            atual = [len(m.group(1)), m.group(2).strip(), []]
            secoes.append(atual)
            continue
        if b:
            atual = [2, b.group(1).strip(), []]
            secoes.append(atual)
            continue
        t = re.match(r"^\s*template\s*:\s*(.+)$", linha, re.I)
        if t and atual is None:
            declarado = t.group(1).strip()
            continue
        if atual is not None:
            atual[2].append(linha)
    return titulo, declarado, secoes


def campos_do_topo(secoes):
    """Os campos sao as secoes do nivel mais alto; as partes ficam abaixo."""
    if not secoes:
        return []
    topo = min(s[0] for s in secoes)
    campos, atual = [], None
    for nivel, nome, linhas in secoes:
        if nivel == topo:
            atual = {"nome": nome, "linhas": list(linhas), "partes": []}
            campos.append(atual)
        elif atual is not None:
            atual["partes"].append({"nome": nome, "linhas": list(linhas)})
    return campos


def chave(nome):
    n = norm(nome)
    return SINONIMOS.get(n, n)


def escolher_template(declarado, nomes, forcado):
    por_num = {t[0]: t for t in TEMPLATES}
    alvo = forcado or declarado
    if alvo:
        a = norm(alvo)
        m = re.match(r"^(\d)\b", a)
        if m and int(m.group(1)) in por_num:
            return por_num[int(m.group(1))], None
        for t in TEMPLATES:
            if a in norm(t[1]) or norm(t[1]) in a:
                return t, None
        return None, "Template '%s' nao reconhecido. Use um numero de 1 a 8 ou o nome." % alvo
    achados = set(chave(n) for n in nomes)
    pont = []
    for t in TEMPLATES:
        fixos = [chave(c) for c in t[2]]
        inter = len(achados & set(fixos))
        pont.append((inter / len(set(fixos) | achados), inter, t))
    pont.sort(key=lambda x: (-x[0], -x[1]))
    melhor = pont[0]
    if melhor[1] < 3:
        return None, "Nao consegui reconhecer o template pelos campos. Escreva 'Template: <n>'."
    if len(pont) > 1 and pont[1][0] == melhor[0]:
        return None, ("Template ambiguo entre %d e %d. Escreva 'Template: <n>'."
                      % (melhor[2][0], pont[1][2][0]))
    return melhor[2], ("Template reconhecido pelos campos: %d · %s. Confirme se e o certo."
                       % (melhor[2][0], melhor[2][1]))


def texto_de(linhas):
    return "\n".join(linhas).strip()


def verificar(caminho, forcado=None):
    erros, avisos = [], []
    texto = open(caminho, encoding="utf-8").read()
    titulo, declarado, secoes = ler_entrada(texto)
    if not titulo:
        erros.append("Falta o titulo da entrada (primeira linha com '# ').")
    campos = campos_do_topo(secoes)
    nomes = [c["nome"] for c in campos]
    tpl, nota = escolher_template(declarado, nomes, forcado)
    if tpl is None:
        erros.append(nota)
        return titulo, erros, avisos
    if nota:
        avisos.append(nota)
    _, nome_tpl, fixos, partes_fixas = tpl
    esperado = [chave(c) for c in fixos]
    achado = [chave(n) for n in nomes]

    faltam = [f for f, e in zip(fixos, esperado) if e not in achado]
    extras = [n for n, a in zip(nomes, achado) if a not in esperado]
    if faltam:
        erros.append("Faltam campos do template %d (%s): %s." % (tpl[0], nome_tpl, "; ".join(faltam)))
    if extras:
        erros.append("Campos que nao existem no template %d: %s. Nao force a forma de outro "
                     "template e nao invente campo." % (tpl[0], "; ".join(extras)))
    if not faltam and not extras and achado != esperado:
        erros.append("Os campos estao fora de ordem. Ordem fixa: %s." % " > ".join(fixos))
    dups = sorted(set(a for a in achado if achado.count(a) > 1))
    if dups:
        erros.append("Campo repetido: %s." % "; ".join(dups))

    por_chave = {chave(c["nome"]): c for c in campos}
    for canon in fixos:
        c = por_chave.get(chave(canon))
        if not c:
            continue
        partes = partes_fixas.get(canon)
        corpo = texto_de(c["linhas"])
        if partes:
            nomes_p = [chave(p["nome"]) for p in c["partes"]]
            esp_p = [chave(p) for p in partes]
            f_p = [p for p, e in zip(partes, esp_p) if e not in nomes_p]
            if f_p:
                erros.append("[%s] faltam partes: %s." % (canon, "; ".join(f_p)))
            elif nomes_p != esp_p:
                erros.append("[%s] partes fora de ordem. Ordem fixa: %s." % (canon, " > ".join(partes)))
            for p in c["partes"]:
                if chave(p["nome"]) in esp_p and not texto_de(p["linhas"]):
                    erros.append("[%s > %s] parte vazia." % (canon, p["nome"]))
            if not c["partes"] and not corpo:
                erros.append("[%s] campo vazio." % canon)
        elif not corpo:
            erros.append("[%s] campo vazio. Nao deixe secao vazia." % canon)
        if canon == "Como conduzir" and tpl[0] in PASSOS_3:
            n = sum(1 for l in c["linhas"] if PASSO_RE.match(l))
            if n != 3:
                erros.append("[Como conduzir] precisa de exatamente 3 passos numerados "
                             "(encontrei %d)." % n)

    # regras de escrita, no texto inteiro
    for i, linha in enumerate(texto.splitlines(), 1):
        if "—" in linha or "–" in linha:
            erros.append("[linha %d] travessao. Use dois-pontos, virgula, ponto ou ·." % i)
        if PLACEHOLDER_RE.search(linha):
            erros.append("[linha %d] marcador de preenchimento na versao final." % i)
        for c in COLCHETE_RE.findall(linha):
            if acc(c).strip() != "codigo biblioteca" and not re.match(r"^\s*[x ]?\s*$", c):
                if re.search(r"\]\(", linha):  # link markdown
                    continue
                erros.append("[linha %d] colchetes '[%s]'. So [código biblioteca] e permitido." % (i, c))
        low = acc(linha)
        for p in PROIBIDOS:
            if re.search(r"\b%s\b" % re.escape(p), low):
                erros.append("[linha %d] termo proibido '%s' (educador e crianças)." % (i, p))
        for velho, novo in APOSENTADOS:
            if re.search(r"\b%s\b" % re.escape(velho), low):
                erros.append("[linha %d] nome aposentado '%s'. Use: %s." % (i, velho, novo))
        palavras = re.findall(r"[a-z']+", low)
        if len(palavras) >= 6 and sum(1 for w in palavras if w in INGLES) >= 3:
            avisos.append("[linha %d] parece estar em ingles. A entrada fica em portugues." % i)
        if CURRICULO_RE.search(low):
            avisos.append("[linha %d] curriculo dentro da entrada (BNCC, campos, Eixos). "
                          "Isso mora nas skills de campos." % i)

    # instrucoes: um marcador ou passo = uma acao principal, curta
    for c in campos:
        for l in c["linhas"] + [x for p in c["partes"] for x in p["linhas"]]:
            if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\S", l):
                corpo = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", l)
                n = len(corpo.split())
                if n > 35:
                    avisos.append("[%s] instrucao com %d palavras. Uma acao principal por "
                                  "instrucao: '%s...'" % (c["nome"], n, corpo[:50]))
                elif SEQ_RE.search(acc(corpo)):
                    avisos.append("[%s] parece ter mais de uma acao ('e depois', 'em seguida'): "
                                  "'%s...'" % (c["nome"], corpo[:50]))
    return titulo, erros, avisos


def arquivos(alvos, git_base):
    saida = []
    for a in alvos:
        if os.path.isdir(a):
            if git_base:
                r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", git_base,
                                    "--", a], capture_output=True, text=True)
                u = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", a],
                                   capture_output=True, text=True)
                lista = [l for l in (r.stdout + u.stdout).splitlines() if l.endswith(".md")]
            else:
                lista = [os.path.join(d, f) for d, _, fs in os.walk(a) for f in sorted(fs)
                         if f.endswith(".md")]
            saida.extend(sorted(set(lista)))
        else:
            saida.append(a)
    return saida


def main(argv):
    args, forcado, git_base, alvos = argv[1:], None, None, []
    i = 0
    while i < len(args):
        if args[i] == "--template" and i + 1 < len(args):
            forcado = args[i + 1]; i += 2
        elif args[i] == "--git-base" and i + 1 < len(args):
            git_base = args[i + 1]; i += 2
        else:
            alvos.append(args[i]); i += 1
    if not alvos:
        print(__doc__); return 2
    lista = arquivos(alvos, git_base)
    if not lista:
        print("Nenhuma entrada nova ou editada para conferir."); return 0
    total_erros, titulos = 0, {}
    for caminho in lista:
        if not os.path.exists(caminho):
            print("Arquivo nao encontrado: %s" % caminho); total_erros += 1; continue
        titulo, erros, avisos = verificar(caminho, forcado)
        if titulo:
            k = norm(titulo)
            if k in titulos and titulos[k] != caminho:
                erros.append("Titulo igual ao de %s. Um recurso, uma entrada: atualize a "
                             "existente." % titulos[k])
            titulos.setdefault(k, caminho)
        print("== %s%s" % (caminho, " · %s" % titulo if titulo else ""))
        if not erros and not avisos:
            print("   Nenhum problema mecanico encontrado.")
        for e in erros:
            print("   ERRO  %s" % e)
        for a in avisos:
            print("   aviso %s" % a)
        total_erros += len(erros)
    print("\nO que este script NAO confere: se o template e o certo para o recurso, se cada "
          "instrucao e boa e cabe na faixa etaria, se cada campo cumpre o que o nome promete e "
          "se a entrada nao duplica outra com outro nome. Confira a mao (regras-de-escrita.md).")
    return 1 if total_erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
