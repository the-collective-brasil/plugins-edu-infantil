#!/usr/bin/env python3
"""
verificar_centros_propostas.py - conferencia mecanica do que a editor-infantil-centros-propostas
escreve (Educacao Infantil, Intercriativa Lab): o texto padrao da aula de Centros de
Aprendizagem ou de Brincar ao Ar Livre (Materiais e Preparacao + 4 Momentos), com a linha de
cada proposta no Momento 1. A entrada da Biblioteca e de outra familia de skills: aqui so se
cita, e este script nao a confere.

Adaptado de verificar_aula.py (editor-centros e editor-propostas, v1.0). Sairam as conferencias
dos campos que esta skill nao escreve: Objetivo, BNCC, Resultados, Eixos, Perfil, Documentacao
e Dica da aula (skills irmas).

AULA
  - os 4 Momentos do ramo e do modo (lidos de dados/boilerplates-*.md), nesta ordem
  - itens fixos iguais ao boilerplate; os nomes dos Momentos sao fixos
  - linhas das propostas: subitens do Momento 1, logo depois do item da Rotina (posicao do
    marcador no boilerplate); forma da linha, conector, codigo, sem negrito, nome em italico
    (aviso); sem linhas de Resultado ou Eixo (aviso se aparecerem)
  - nome do Momento ate 30; bloco acima de 600 (aviso, com a parte fixa e a das propostas; caso
    conhecido: o Momento 1 passa de 600 com mais de 1 proposta, e a edicao final resolve)
  - Materiais e Preparacao: so nome e [codigo biblioteca]; em Dirigida pela crianca, abre com a
    linha fixa do boilerplate; acima de 270 (aviso)
  - com --codigo (ou S#.D#.A# no texto): modo x dia e bloco pela grade (termos v8, secao 4)
  - com --area: a area existe no tipo de aula (templates-de-aula.md, secao 7) e os Campos de
    Experiencia dela sao mostrados; se o texto trouxer uma linha "Campos de Experiencia",
    principal e secundarios sao conferidos contra a area
  - travessao, aspas, termos proibidos e aposentados, numeros por extenso (aviso)
  - com --nivel: avisos de idade (marcos-aprendizagem-desenvolvimento.md, secoes 3 e 5)

Nao julga se a proposta e boa nem se cabe na idade.

Uso:
  python3 verificar_centros_propostas.py aula.md [--nivel "Infantil 4"] [--codigo S3.D2.A2]
      [--area "Construção e Engenharia"] [--tipo centros|ar-livre] [--modo guiada|dirigida]
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import argparse, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.normpath(os.path.join(HERE, "..", "dados"))

TIPO_NOME = {"centros": "Centros de Aprendizagem", "ar-livre": "Brincar ao Ar Livre"}
MODO_NOME = {"guiada": "Guiada pelo educador", "dirigida": "Dirigida pela criança"}
BOILER = {"centros": "boilerplates-centros.md", "ar-livre": "boilerplates-brincar-ao-ar-livre.md"}
MAT_FIXA = {}  # (tipo, modo) -> linha fixa de Materiais e Preparacao, lida do boilerplate
# Grade da semana (termos-e-nomes.md v8, secao 4): o bloco define o modo.
# Centros: Guiada em D2 e D4 (A2), Dirigida pela crianca em D3 (A3).
# Ar Livre: Guiada em D3 (A2), Dirigida pela crianca em D1, D2, D4 e D5 (A3).
DIAS = {("centros", "guiada"): {2, 4}, ("centros", "dirigida"): {3},
        ("ar-livre", "guiada"): {3}, ("ar-livre", "dirigida"): {1, 2, 4, 5}}
# Bloco (A#) de cada tipo por dia, pela mesma grade: o bloco nao e escolha do autor.
SLOT = {("ar-livre", 1): 3, ("ar-livre", 2): 3, ("ar-livre", 3): 2, ("ar-livre", 4): 3,
        ("ar-livre", 5): 3, ("centros", 2): 2, ("centros", 3): 3, ("centros", 4): 2}
EIXO_FAM = ["socioemocional", "empreendedorismo", "educacao financeira",
            "cidadania digital e computacao"]
NIVEL_MAP = {"3": 3, "4": 4, "5": 5, "infantil 3": 3, "infantil 4": 4, "infantil 5": 5}

CODE_RE = re.compile(r"\bEI0[2-5][A-Z]{2,3}\d{2}\b")
AULA_RE = re.compile(r"\bS(\d{1,2})\.D(\d)\.A(\d)\b")
LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)")
LINHA_RE = re.compile(
    r"^(?P<nome>.+?)\s*\[(?P<cod>[^\]]+)\]\s+As crian[çc]as\s+(?P<acao>.+?),\s+"
    r"(?P<con>de modo que possam|o que convida a|com a chance de|para)\s+(?P<int>.+?)\s*$")
TRAVESSAO_OK = "Eu Faço – Nós Fazemos – Você Faz"

PROIBIDOS_ERRO = ["aluno", "aluna", "alunos", "alunas", "estudante", "estudantes", "educando",
                  "educandos"]
PROIBIDOS_AVISO = ["professor", "professora", "professores", "professoras", "tia", "tias"]
# (trecho sem acento, em minusculas) -> o que escrever. termos-e-nomes.md v8, secao 8.
APOSENTADOS = [("outdoor play", "Brincar ao Ar Livre"), ("learning cent", "Centros de Aprendizagem"),
               ("roteiro do educador", "Orientações do Educador"),
               ("revista impacto", "Orientações do Educador"),
               ("hora da mesinha", "Oficina de Descobertas"), ("table time", "Oficina de Descobertas"),
               ("story time", "Hora do Conto"), ("protagonistas lab", "Intercriativa Lab"),
               ("early years", "Educação Infantil"),
               ("aprendizagem personalizada", "Aprendizagem Exploratória"),
               ("roda de abertura", "Roda"), ("expressao criativa", "Ateliê de Arte"),
               ("atelie de artes", "Ateliê de Arte"), ("artes visuais", "Ateliê de Arte"),
               ("dirigida pelas criancas", "Dirigida pela criança"),
               ("perfil do estudante", "Perfil da Criança Protagonista"),
               ("perfil do protagonista", "Perfil da Criança Protagonista"),
               ("roda de partilha", "Roda (Roda de Partilha não é termo)"),
               ("conexao com as familias", "Conexão Casa-Escola"),
               ("rotina de organizacao", "Rotina de Encerramento"),
               ("rotina dos centros de aprendizagem", "Rotina dos Centros"),
               ("rotina do brincar ao ar livre", "Rotina das Propostas"),
               ("resolucao de problemas", "Criatividade (Resolução de Problemas não é competência)"),
               ("caderno fazer e brincar", "Fazer e Brincar"),
               ("educadora", "educador"), ("pergunta-guia", "Pergunta Norteadora"),
               ("questao norteadora", "Pergunta Norteadora")]
G_RE = re.compile(r"\bg[345]\b")
EXTENSO_RE = re.compile(r"\b(dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez|onze|doze|"
                        r"quinze|vinte)\b")

CORES = {"vermelh": "vermelho", "azul": "azul", "azuis": "azul", "amarel": "amarelo",
         "verde": "verde", "laranja": "laranja", "rox": "roxo", "rosa": "rosa", "pret": "preto",
         "branc": "branco", "marrom": "marrom", "marrons": "marrom", "cinza": "cinza",
         "lilas": "lilas", "bege": "bege", "dourad": "dourado", "pratead": "prateado",
         "violeta": "violeta", "turquesa": "turquesa"}
CORES_RE = re.compile(r"\b(vermelh[oa]s?|azu(?:l|is)|amarel[oa]s?|verdes?|laranjas?|rox[oa]s?|"
                      r"rosas?|pret[oa]s?|branc[oa]s?|marro(?:m|ns)|cinzas?|lilas|bege|"
                      r"dourad[oa]s?|pratead[oa]s?|violetas?|turquesa)\b")
FORMAS_RE = re.compile(r"\b(circulo|quadrado|triangulo|retangulo|losango|oval|estrela|hexagono|"
                       r"pentagono|trapezio)s?\b")


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


def visivel(s):
    return re.sub(r"\*+", "", LINK_RE.sub(r"\1", s)).strip()


def norm_item(s):
    t = re.sub(r"\[[^\]]*\]", "[]", visivel(s))
    return re.sub(r"\s+", " ", t).strip()


def bib_ok(cod):
    """Marcador [codigo biblioteca] ou um codigo ja atribuido por uma pessoa. A forma do codigo
    nao esta definida em nenhuma fonte: aceita-se EI#.PRO.## como palpite permissivo."""
    c = acc(cod).strip()
    return c == "codigo biblioteca" or bool(re.match(r"^ei\d\.pro\.(##|\d+)$", c))


class Report:
    def __init__(self):
        self.errors, self.warnings, self.notes = [], [], []

    def error(self, w, m): self.errors.append((w, m))
    def warn(self, w, m): self.warnings.append((w, m))
    def note(self, m): self.notes.append(m)

    def show(self):
        for n in self.notes:
            print(n)
        if self.notes:
            print()
        if self.errors:
            print("ERROS (%d)" % len(self.errors))
            for w, m in self.errors:
                print("  [%s] %s" % (w, m))
        if self.warnings:
            print("\nAVISOS (%d)" % len(self.warnings))
            for w, m in self.warnings:
                print("  [%s] %s" % (w, m))
        if not self.errors and not self.warnings:
            print("Nenhum problema mecanico encontrado.")
        print("\nO que este script NAO confere: se a proposta e boa, se cada acao esperada cabe "
              "na faixa etaria e se a linha da proposta resume bem a entrada da Biblioteca. "
              "Confira a mao.")


# ---------------------------------------------------------------- dados

def load_areas():
    """Campos de Experiencia de termos-e-nomes.md (v8, secao 7, tabela) e as 12 areas de
    templates-de-aula.md (v2, secao 7). Cada area e uma linha
    "- **Nome da area:** ... Campos: <principal>; articulado(s) <...>. Exemplo: ... Conexao: ...",
    sob "**Areas dos Centros de Aprendizagem**" ou "**Areas do Brincar ao Ar Livre**"."""
    text = open(os.path.join(DADOS, "termos-e-nomes.md"), encoding="utf-8").read()
    campos = []
    m = re.search(r"### Campos de Experi\S+\s*\n(.+?)\n\s*\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and not cells[0].startswith(("Campo", "---")):
                campos.append(cells[0])
    tpl = open(os.path.join(DADOS, "templates-de-aula.md"), encoding="utf-8").read()
    areas = {"centros": {}, "ar-livre": {}}
    sec = re.search(r"^## 7\. .*?\n(.*?)(?=^## |\Z)", tpl, re.S | re.M)
    if sec:
        tipo = None
        for line in sec.group(1).splitlines():
            low = acc(line)
            if low.startswith("**areas dos centros"):
                tipo = "centros"
                continue
            if low.startswith("**areas do brincar"):
                tipo = "ar-livre"
                continue
            mm = re.match(r"^- \*\*([^:*]+):\*\* .*?Campos: (.+?)\. Exemplo:", line)
            if not mm or not tipo:
                continue
            princ, artic, flag = [], [], False
            for part in mm.group(2).split(";"):
                p = part.strip().rstrip(".")
                a = re.match(r"^articulados?\s+(.+)$", p)
                if a:
                    flag, p = True, a.group(1)
                (artic if flag else princ).append(p)
            areas[tipo][acc(mm.group(1)).strip()] = (mm.group(1).strip(), princ, artic)
    return campos, areas


def load_boilerplates():
    """Momentos por (tipo, modo). Cada item e (texto, variavel). O item variavel e o marcador
    da linha da proposta ({{ }}), subitem do Momento 1. MAT_FIXA guarda a linha fixa de
    Materiais e Preparacao, quando o modo tem uma."""
    out = {}
    for tipo, fn in BOILER.items():
        modo, cur, mat = None, None, False
        for line in open(os.path.join(DADOS, fn), encoding="utf-8"):
            s = line.strip()
            if s.startswith("## "):
                h = acc(s[3:])
                modo = "guiada" if h.startswith("guiada") else (
                    "dirigida" if h.startswith("dirigida") else None)
                cur, mat = None, False
                continue
            if modo and re.match(r"^\*\*materiais e preparacao", acc(s)):
                cur, mat = None, True
                continue
            m = re.match(r"^\*\*(\d+)\s*\|\s*(.+?)\*\*\s*(\(vari[aá]vel\))?\s*$", s)
            if m and modo:
                mat = False
                cur = {"num": int(m.group(1)), "nome": m.group(2).strip(), "itens": []}
                out.setdefault((tipo, modo), []).append(cur)
                continue
            if s.startswith("- "):
                if mat and modo:
                    MAT_FIXA[(tipo, modo)] = s[2:].strip()
                elif cur is not None:
                    cur["itens"].append((s[2:].strip(), "{{" in s))
    for ms in out.values():
        for cur in ms:
            cur["variavel"] = any(v for _, v in cur["itens"])
    return out


# ---------------------------------------------------------------- comuns

def check_voz(lines, rep):
    for i, line in lines:
        w = "linha %d" % i
        flat = acc(line)
        if ("—" in line or "–" in line) and TRAVESSAO_OK not in line:
            rep.error(w, "Travessao. A casa nao usa travessao (so em fala citada de livro e em "
                         "Eu Faço – Nós Fazemos – Você Faz).")
        if re.search(r"[\"“”][^\"“”]{3,}[\"“”]", line):
            rep.error(w, "Texto entre aspas. Fala do educador vai em italico, sem aspas.")
        for p in PROIBIDOS_ERRO:
            if re.search(r"\b%s\b" % p, flat):
                rep.error(w, "Use crianca ou criancas, nunca '%s'." % p)
                break
        if "cada crianca" in flat:
            rep.error(w, "Use a crianca ou as criancas, nunca cada crianca.")
        for p in PROIBIDOS_AVISO:
            if re.search(r"\b%s\b" % p, flat):
                rep.warn(w, "'%s': para quem ensina, use educador. Se for papel de faz de conta, "
                            "ignore." % p)
                break
        for old, new in APOSENTADOS:
            if old in flat:
                rep.error(w, "Termo aposentado '%s'. Use %s." % (old, new))
        if G_RE.search(flat):
            rep.error(w, "Termo aposentado G3/G4/G5. Use Infantil 3/4/5.")
        if re.search(r"\batelier\b", flat):
            rep.warn(w, "Grafia Atelier. No texto, use Ateliê.")
        if re.search(r"\bpais\b", flat):
            rep.warn(w, "'pais': se for quem cuida em casa, use famílias e responsáveis.")
        m = EXTENSO_RE.search(flat)
        if m:
            rep.warn(w, "Numero por extenso ('%s'). A casa usa algarismos." % m.group(1))


def check_marcadores(lines, rep, pular=()):
    for i, line in lines:
        if i in pular:
            continue
        if "{{" in line:
            rep.warn("linha %d" % i, "Marcador {{ }} nao preenchido.")
        sem_link = LINK_RE.sub("", line)
        for nota in re.findall(r"\[([^\]]+)\]", sem_link):
            if len(nota) > 25:
                rep.warn("linha %d" % i, "Nota entre colchetes do boilerplate ficou no texto: "
                                         "\"[%s...]\"" % nota[:40])


def check_idade(lines, nivel, rep):
    if not nivel:
        return
    tag = "Idade · Infantil %d" % nivel
    achados = {}

    def add(chave, i):
        achados.setdefault(chave, []).append(i)

    cores, formas = set(), set()
    for i, raw in lines:
        t = raw.strip()
        if t.startswith("#"):
            continue
        f = acc(visivel(raw))
        nums = [int(n) for n in re.findall(r"(?<![\w.#])(\d{1,3})(?![\w.])", f)]
        if re.search(r"tesoura|recort", f) and nivel == 3:
            add("tesoura", i)
        if re.search(r"\b(cont(ar|e|em|am|agem|ando)|quantidades?|quantos|quantas|numeral|"
                     r"numeros?)\b", f) and nums:
            lim = {3: 5, 4: 8, 5: 10}[nivel]
            if max(nums) > lim:
                add("quantidade", i)
        for c in CORES_RE.findall(f):
            for k, v in CORES.items():
                if c.startswith(k):
                    cores.add(v)
                    break
        mc = re.search(r"(\d+)\s+cores", f)
        if mc and nivel == 3 and int(mc.group(1)) > 8:
            add("cores", i)
        for fm in FORMAS_RE.findall(f):
            formas.add(fm)
        if re.search(r"\bescrev\w*|\bescrita\b", f):
            if nivel in (3, 4):
                add("escrita", i)
            elif re.search(r"sozinh|autonom|convencional|corretamente|sem ajuda", f):
                add("escrita5", i)
        if nivel in (3, 4) and re.search(r"\b(leia|leiam|ler|leem|lendo)\b|leitura de palavra", f):
            add("leitura", i)
        mm = re.search(r"(\d+)\s*min", f)
        if mm and nivel == 3 and int(mm.group(1)) > 15:
            add("minutos", i)
        if "quebra-cabeca" in f and nivel in (3, 4) and nums and max(nums) > 24:
            add("quebra", i)
        if nivel in (3, 4) and "conflit" in f and re.search(
                r"sozinh|sem (a )?ajuda|sem o educador|autonom", f):
            add("conflito", i)
    if nivel == 3 and len(cores) > 8:
        achados.setdefault("cores", []).append(0)
    if nivel == 3 and len(formas) > 4:
        achados.setdefault("formas", []).append(0)

    msg = {
        "tesoura": "tesoura sem ponta; de 2a6m a 3a, com auxilio para posicionar os dedos; de 3a a "
                   "3a6m, linhas retas e curvas com auxilio do adulto. Recorte de formas complexas "
                   "aos 3 anos e erro comum (secao 5): linhas retas, papel firme, apoio nas curvas.",
        "quantidade": {3: "numeral e quantidade de 3 ate 5 (3a6m a 4a); recita 1 a 5 antes disso. "
                          "Quantidades acima de 5 so com apoio do adulto.",
                       4: "numero e quantidade de 5 a 8. Contagem com correspondencia ate 10 aos "
                          "4 anos e erro comum (secao 5): trabalhe ate 8 com material concreto.",
                       5: "quantidade e numero ate 10, decompondo e unindo objetos. Acima de 10, "
                          "so com apoio do adulto."}[nivel],
        "cores": "de 2a6m a 3a, nomeia de 6 a 8 cores. Mais de 8 cores numa classificacao aos 3 "
                 "anos e erro comum (secao 5): reduza ou use pares de contraste.",
        "formas": "identifica ate 3 formas geometricas (3a a 3a6m) e ate 4 (3a6m a 4a).",
        "escrita": "antes dos 5 anos, registro por desenho, ditado ao adulto, marcas e simbolos "
                   "proprios, nunca correspondencia entre letra e som (secao 5). Se quem escreve "
                   "e o educador, ignore.",
        "escrita5": "nenhuma faixa ate 6 anos preve escrita autonoma convencional (secao 5); de "
                    "5a a 6a, escreve palavras ou frases do seu jeito.",
        "leitura": "leitura de palavras conhecidas aparece de 5a a 6a; antes, leitura por imagens, "
                   "rotulos, pictogramas e simbolos (secao 5). Se quem le e o educador, ignore.",
        "minutos": "atencao de 6 a 15 min (3a a 3a6m) e de 10 a 20 min (3a6m a 4a). Planeje em "
                   "ciclos curtos que a crianca pode repetir.",
        "quebra": "quebra-cabeca de mais de 24 pecas so aparece de 5a a 6a.",
        "conflito": "aos 3 e 4 anos, a crianca resolve conflitos com orientacao ou mediacao do "
                    "adulto (secao 5): a mediacao faz parte da proposta.",
    }
    for chave, ls in achados.items():
        onde = ", ".join(str(x) for x in sorted(set(ls)) if x) or "texto todo"
        rep.warn(tag, "confira (linhas %s): %s" % (onde, msg[chave]))


# ---------------------------------------------------------------- aula

def parse_momentos(lines):
    """Momentos da aula. Cada item e (linha, texto, sub): sub = subitem (linha recuada que
    comeca por - ou *), onde ficam as linhas das propostas."""
    out, cur = [], None
    for i, line in lines:
        t = line.strip()
        core = re.sub(r"\*+", "", t).lstrip("#").strip()
        m = re.match(r"^(\d+)\s*\|\s*(.+)$", core)
        if m:
            nome = m.group(2).strip()
            marca = bool(re.search(r"\(vari[aá]vel\)\s*$", nome))
            nome = re.sub(r"\s*\(vari[aá]vel\)\s*$", "", nome)
            cur = {"num": int(m.group(1)), "nome": nome, "itens": [], "linha": i, "marca": marca}
            out.append(cur)
            continue
        if re.match(r"^#{1,4}\s+\S", t) or re.match(r"^\*\*[^*]+\*\*\s*$", t):
            cur = None
            continue
        if cur is not None:
            recuada = line[:1] in (" ", "\t")
            if re.match(r"^[-*]\s+\S", t) and (recuada or t.startswith("- ")):
                cur["itens"].append((i, t[2:].strip(), recuada))
            elif t and cur["itens"] and recuada:
                j, prev, sub = cur["itens"][-1]
                cur["itens"][-1] = (j, prev + " " + t, sub)
            elif t:
                cur = None
    return out


def parse_materiais(lines):
    start = None
    for idx, (i, line) in enumerate(lines):
        t = line.strip()
        core = acc(re.sub(r"\*+", "", t).lstrip("#").strip())
        if core.startswith("materiais e preparacao") and (t.startswith("#") or t.startswith("**")):
            start = idx
            break
    if start is None:
        return None
    items = []
    for i, line in lines[start + 1:]:
        t = line.strip()
        core = re.sub(r"\*+", "", t).lstrip("#").strip()
        if t.startswith("#") or t.startswith("**") or re.match(r"^\d+\s*\|", core):
            break
        if t.startswith("- "):
            items.append((i, t[2:].strip()))
    return items


def eh_fecho(raw):
    vis = visivel(raw)
    f = acc(vis)
    return (raw.strip().startswith("{{") or f.startswith("resultado de aprendizagem")
            or f.startswith("eixo") or any(f.startswith(x + ":") for x in EIXO_FAM)
            or bool(re.search(r"\(EI0[2-5][A-Z]{2}\d{2}\)", vis)))


def check_linha_proposta(i, raw, rep):
    w = "linha %d" % i
    if "{{" in raw:
        rep.error(w, "Linha da proposta com marcador {{ }}. Escreva a linha a partir da entrada "
                     "da Biblioteca citada (ou do que a pessoa contou dela).")
        return
    if "**" in raw:
        rep.error(w, "Linha da proposta com negrito. Sem negrito no texto final.")
    vis = visivel(raw)
    m = LINHA_RE.match(vis)
    if not m:
        rep.error(w, "Linha da proposta fora da forma '<Nome> [codigo biblioteca] As criancas "
                     "<acao>, <conector> <intencao>.' Conectores: para, de modo que possam, o que "
                     "convida a, com a chance de. Lido: \"%s\"" % vis[:80])
        return
    if not bib_ok(m.group("cod")):
        rep.error(w, "Codigo da proposta '[%s]'. Use [codigo biblioteca] ou o codigo atribuido "
                     "por uma pessoa." % m.group("cod"))
    if not vis.endswith("."):
        rep.warn(w, "Linha da proposta sem ponto final.")
    if not re.match(r"^\*[^*]", raw.strip()):
        rep.warn(w, "Nome da proposta sem italico (nome de recurso; estilo-da-casa.md, "
                    "Formatacao).")


def check_linhas(m, b, rep):
    """Linhas das propostas: subitens do Momento, na posicao do marcador do boilerplate."""
    where = "%d | %s" % (m["num"], m["nome"])
    subs = [(i, raw) for i, raw, sub in m["itens"] if sub]
    if not b["variavel"]:
        for i, _ in subs:
            rep.error("linha %d" % i, "Subitem fora do Momento das propostas. As linhas das "
                                      "propostas ficam so no Momento %d." % 1)
        return 0
    if not subs:
        rep.error(where, "Nenhuma linha de proposta. Escreva uma por proposta, como subitem, "
                         "logo depois do item da Rotina.")
        return 0
    pos_esp = sum(1 for _, v in b["itens"][:next(k for k, (_, v) in enumerate(b["itens"]) if v)]
                  if not v)
    pos_got = next(k for k, (_, _, sub) in enumerate(m["itens"]) if sub)
    if pos_got != pos_esp:
        rep.warn(where, "As linhas das propostas vem depois do item %d (o da Rotina), como no "
                        "boilerplate." % pos_esp)
    n = 0
    for i, raw in subs:
        if eh_fecho(raw):
            rep.warn("linha %d" % i, "Linha de Resultado ou Eixo embaixo da proposta. Nesta "
                                     "estrutura a proposta vai so com a sua linha.")
            continue
        n += 1
        check_linha_proposta(i, raw, rep)
    if n == 0:
        rep.error(where, "Nenhuma linha de proposta valida.")
    return n


def check_grade(cod, tipo, modo, rep):
    """Modo x dia e bloco pela grade da semana (termos-e-nomes.md v8, secao 4)."""
    mc = AULA_RE.search(cod.upper())
    if not mc:
        rep.error("--codigo", "Codigo de aula fora da forma S#.D#.A#: '%s'." % cod)
        return
    if any(x.startswith("0") for x in mc.groups()):
        rep.error("--codigo", "Codigo de aula com zero a esquerda: %s." % mc.group(0))
    s_, d_, a_ = (int(x) for x in mc.groups())
    if not (1 <= s_ <= 12 and 1 <= d_ <= 5 and 1 <= a_ <= 4):
        rep.error("--codigo", "Codigo de aula fora da grade (S1-12, D1-5, A1-4): %s." % mc.group(0))
        return
    rep.note("Codigo da aula: %s" % mc.group(0))
    if (tipo, d_) not in SLOT:
        rep.warn("--codigo", "%s nao acontece no D%d pela grade da semana (termos v8, secao 4)."
                 % (TIPO_NOME[tipo], d_))
        return
    if SLOT[(tipo, d_)] != a_:
        rep.warn("--codigo", "%s no D%d e A%d pela grade da semana (termos v8, secao 4), nao A%d."
                 % (TIPO_NOME[tipo], d_, SLOT[(tipo, d_)], a_))
    if d_ not in DIAS[(tipo, modo)]:
        rep.warn("--codigo", "%s em %s no D%d: a grade (termos v8, secao 4) poe esse modo em D%s. "
                             "Se o pedido trouxe esse modo, siga e sinalize nas Decisoes em aberto."
                 % (TIPO_NOME[tipo], MODO_NOME[modo], d_,
                    ", D".join(str(x) for x in sorted(DIAS[(tipo, modo)]))))


def check_area(lines, area, tipo, campos, areas, rep):
    """A area existe no tipo de aula (templates-de-aula.md, secao 7); mostra os Campos dela.
    Se o texto trouxer uma linha "Campos de Experiencia", confere principal e secundarios."""
    a = areas[tipo].get(acc(area).strip())
    if not a:
        rep.error("--area", "Area '%s' nao existe em %s (templates-de-aula.md, secao 7). Areas: %s."
                  % (area, TIPO_NOME[tipo], " · ".join(v[0] for v in areas[tipo].values())))
        return
    nome, ap, aa = a
    rep.note("Area: %s · Campos: principal %s; articulados %s (templates-de-aula.md, secao 7)."
             % (nome, " ou ".join(ap), "; ".join(aa) or "nenhum"))
    cl = next(((i, l) for i, l in lines if "campos de experiencia" in acc(l)), None)
    if not cl or "{{" in cl[1]:
        return
    w = "linha %d" % cl[0]
    f = acc(visivel(cl[1]))
    partes = re.split(r"secundari\w*:?|articulad\w*:?", f, maxsplit=1)
    ppart = partes[0].split("principal", 1)[-1]
    spart = partes[1] if len(partes) > 1 else ""
    princ = [c for c in campos if acc(c) in ppart]
    sec = [c for c in campos if acc(c) in spart]
    if len(princ) != 1:
        rep.error(w, "Campo principal: exatamente um dos 5 Campos de Experiencia (termos v8, "
                     "secao 7). Encontrados: %d." % len(princ))
    if princ and acc(princ[0]) not in [acc(x) for x in ap]:
        rep.error(w, "Campo principal '%s' nao e principal da area %s. Principal: %s."
                  % (princ[0], nome, " ou ".join(ap)))
    todos = [acc(x) for x in ap + aa]
    for c in sec:
        if acc(c) not in todos:
            rep.warn(w, "Secundario '%s' fora dos Campos da area %s." % (c, nome))
        if princ and acc(c) == acc(princ[0]):
            rep.warn(w, "O Campo principal repetido nos secundarios.")


def check_aula(lines, args, rep, bps):
    ms = parse_momentos(lines)
    proprias = set()
    for m in ms:
        proprias.add(m["linha"])
        proprias.update(i for i, _, _ in m["itens"])
    for m in ms:
        if len(m["nome"]) > 30:
            rep.error("%d | %s" % (m["num"], m["nome"]),
                      "Nome do Momento com %d caracteres (max 30)." % len(m["nome"]))
    nomes = [acc(m["nome"]) for m in ms]
    validos = [(t, mo) for (t, mo) in bps
               if (not args.tipo or t == args.tipo) and (not args.modo or mo == args.modo)]

    def pontos(k):
        # nomes iguais primeiro; em empate, itens fixos iguais ao boilerplate
        n = sum(1 for x, b in zip(nomes, bps[k]) if x == acc(b["nome"]))
        itens = 0
        for m, b in zip(ms, bps[k]):
            fixos_b = [norm_item(x) for x, v in b["itens"] if not v]
            fixos_m = [norm_item(x) for _, x, sub in m["itens"] if not sub]
            itens += sum(1 for x, y in zip(fixos_m, fixos_b) if x == y)
        return (n, itens)

    ranking = sorted(((pontos(k), k) for k in validos), reverse=True)
    tipo = modo = None
    n_prop = None
    fixos = set()
    forcado = len(validos) == 1
    if ranking and (forcado or (ranking[0][0][0] >= 2 and
                                (len(ranking) == 1 or ranking[0][0] > ranking[1][0]))):
        tipo, modo = ranking[0][1]
    if not tipo:
        esperados = "; ".join("%s · %s: %s" % (TIPO_NOME[t], MODO_NOME[mo],
                                               " · ".join(b["nome"] for b in bps[(t, mo)]))
                              for (t, mo) in sorted(validos))
        rep.error("Momentos", "Os Momentos nao batem com nenhum boilerplate. Encontrados: %s. "
                              "Esperados: %s" % (" · ".join(m["nome"] for m in ms) or "nenhum",
                                                 esperados))
    else:
        bp = bps[(tipo, modo)]
        rep.note("Lido como: aula · %s · %s" % (TIPO_NOME[tipo], MODO_NOME[modo]))
        if len(ms) != len(bp):
            rep.error("Momentos", "%d Momentos. O boilerplate tem %d." % (len(ms), len(bp)))
        n_prop = 0
        for m, b in zip(ms, bp):
            where = "%d | %s" % (m["num"], m["nome"])
            if acc(m["nome"]) != acc(b["nome"]):
                rep.error(where, "Nome do Momento fixo no boilerplate: '%s'." % b["nome"])
            if m["num"] != b["num"]:
                rep.error(where, "Numero do Momento: esperado %d." % b["num"])
            if m["marca"]:
                rep.warn(where, "Tire a marca (variavel) do titulo.")
            got = [norm_item(x) for _, x, sub in m["itens"] if not sub]
            exp = [norm_item(x) for x, v in b["itens"] if not v]
            if got != exp:
                k = next(k for k in range(max(len(got), len(exp)))
                         if k >= len(got) or k >= len(exp) or got[k] != exp[k])
                esperado = exp[k][:80] if k < len(exp) else "(nada: item a mais)"
                rep.error(where, "Momento fixo difere do boilerplate no item %d. Copie de "
                                 "dados/%s. Esperado: \"%s\"" % (k + 1, BOILER[tipo], esperado))
            fixos.update(i for i, _, sub in m["itens"] if not sub)
            n_prop += check_linhas(m, b, rep)
            fixo = sum(len(visivel(x)) for _, x, sub in m["itens"] if not sub)
            prop = sum(len(visivel(x)) for _, x, sub in m["itens"] if sub)
            if fixo + prop > 600:
                rep.warn(where, "Bloco com %d caracteres (pagina: max 600): %d do texto fixo e %d "
                                "das propostas. Caso conhecido com mais de 1 proposta: nao corte "
                                "aqui; informe a contagem e a editor-infantil-orientacoes-do-"
                                "educador ajusta." % (fixo + prop, fixo, prop))

    mat = parse_materiais(lines)
    if mat is None:
        rep.error("Materiais e Preparacao", "Falta a secao Materiais e Preparacao.")
    else:
        proprias.update(i for i, _ in mat)
        if not mat:
            rep.error("Materiais e Preparacao", "Secao sem nenhum item.")
        total = sum(len(visivel(t)) for _, t in mat)
        if total > 270:
            rep.warn("Materiais e Preparacao", "%d caracteres (pagina: max 270 por aula)." % total)
        nomes_mat = mat
        fixa = MAT_FIXA.get((tipo, modo)) if tipo else None
        if fixa:
            if mat and norm_item(mat[0][1]) == norm_item(fixa):
                nomes_mat = mat[1:]
                fixos.add(mat[0][0])
            else:
                rep.warn("Materiais e Preparacao", "Em %s, a secao abre com a linha fixa do "
                                                    "boilerplate: \"%s...\"" % (MODO_NOME[modo], fixa[:60]))
        for i, t in nomes_mat:
            check_item_materiais(i, t, rep)
        if n_prop is not None and nomes_mat and n_prop != len(nomes_mat):
            rep.warn("Materiais e Preparacao", "%d item(ns) em Materiais e %d proposta(s) no "
                                               "Momento 1. Devem ser as mesmas, na mesma ordem."
                     % (len(nomes_mat), n_prop))
    own = [(i, l) for i, l in lines if i in proprias]
    return own, fixos, tipo, modo


def check_item_materiais(i, t, rep):
    w = "linha %d" % i
    vis = visivel(t)
    mm = re.search(r"\[([^\]]+)\]", vis)
    if not mm or not bib_ok(mm.group(1)):
        rep.error(w, "Item de Materiais sem [codigo biblioteca]. Liste so o nome da proposta com "
                     "o codigo.")
    resto = re.sub(r"\[[^\]]*\]", "", vis).strip()
    if len(resto) > 50 or "," in resto or ":" in resto:
        rep.warn(w, "Item de Materiais parece trazer mais que o nome. O detalhe fica na entrada "
                    "da Biblioteca.")
    if not re.match(r"^\*[^*]", t.strip()):
        rep.warn(w, "Nome da proposta sem italico (nome de recurso; estilo-da-casa.md, "
                    "Formatacao).")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Confere o texto padrao da aula de Centros de "
                                             "Aprendizagem e Brincar ao Ar Livre.")
    ap.add_argument("file")
    ap.add_argument("--nivel", help='"Infantil 3", "Infantil 4" ou "Infantil 5" (avisos de idade)')
    ap.add_argument("--codigo", help="codigo da aula S#.D#.A# (modo x dia e bloco pela grade)")
    ap.add_argument("--area", help="area da proposta (templates-de-aula.md, secao 7)")
    ap.add_argument("--tipo", choices=["centros", "ar-livre"])
    ap.add_argument("--modo", choices=["guiada", "dirigida"])
    a = ap.parse_args()

    nivel = None
    if a.nivel:
        nivel = NIVEL_MAP.get(acc(a.nivel).strip())
        if not nivel:
            sys.exit("Nivel invalido: use Infantil 3, 4 ou 5.")
    if not os.path.exists(a.file):
        sys.exit("Arquivo nao encontrado: %s" % a.file)
    text = open(a.file, encoding="utf-8").read()
    lines = list(enumerate(text.splitlines(), 1))
    rep = Report()

    bps = load_boilerplates()
    own, fixos, tipo, modo = check_aula(lines, a, rep, bps)
    if tipo:
        cod = a.codigo or (AULA_RE.search(text) or [None])[0]
        if cod:
            check_grade(cod, tipo, modo, rep)
        else:
            rep.note("Sem --codigo (nem S#.D#.A# no texto): modo x dia nao conferido.")
        if a.area:
            campos, areas = load_areas()
            if not areas[tipo]:
                rep.error("--area", "Nenhuma area lida de dados/templates-de-aula.md, secao 7.")
            else:
                check_area(lines, a.area, tipo, campos, areas, rep)
    check_voz(own, rep)
    check_marcadores(own, rep, pular=fixos)
    check_idade([(i, l) for i, l in own if i not in fixos], nivel, rep)
    if not nivel:
        rep.note("Sem --nivel: avisos de idade nao rodaram.")
    rep.show()
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
