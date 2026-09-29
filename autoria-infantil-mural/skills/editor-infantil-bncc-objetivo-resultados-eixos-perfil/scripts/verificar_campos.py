#!/usr/bin/env python3
"""
verificar_campos.py - conferencias mecanicas dos cinco campos de uma aula da Educacao Infantil
(Intercriativa Lab): Objetivo da Aula, Habilidades BNCC, Eixos Transversais, Perfil da Crianca
Protagonista e Resultados da Aprendizagem.

Adaptado de verificar_aula.py (editor-aulas-intercriativa-infantil). Sairam as conferencias de
Documentacao, Dica e Momentos, que sao de outras skills. A voz so e conferida dentro dos cinco
campos. Le os dados EMPACOTADOS na propria skill (../dados/bncc.md e ../dados/eixos.csv).

Entrada (mesmas convencoes do verificar_aula.py):
  ## A1 · Tipo de aula · Modo            <- uma secao por aula
  ### Objetivo da Aula                   <- a frase no paragrafo seguinte
  ### Habilidades BNCC                   <- linhas "- **EI03ET07** descritor verbatim"
  ### Eixos Transversais                 <- itens "- Familia: frase"
  ### Perfil da Crianca Protagonista     <- linha "A · B · C"
  ### Resultados da Aprendizagem         <- tabela "| Resultado | Vem de |"
Os Momentos podem estar no arquivo: o script le so os cinco campos.

Nao julga se a aula e boa. Isso continua com a pessoa.

Uso:
  python3 verificar_campos.py aula.md --nivel "Infantil 4"
  python3 verificar_campos.py dia.md --nivel 5 --semana 3
  python3 verificar_campos.py aula.md --nivel 3 --sem-verbatim
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import argparse, csv, difflib, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.normpath(os.path.join(HERE, "..", "dados"))

BNCC_PREFIX = {"G3": "EI02", "G4": "EI03", "G5": "EI03"}
EIXO_PREFIX = {"G3": "EI03", "G4": "EI04", "G5": "EI05"}
NIVEL_MAP = {"3": "G3", "4": "G4", "5": "G5", "infantil 3": "G3",
             "infantil 4": "G4", "infantil 5": "G5", "g3": "G3", "g4": "G4", "g5": "G5"}
NIVEL_NOME = {"G3": "Infantil 3", "G4": "Infantil 4", "G5": "Infantil 5"}

BNCC_FAMILIES = {"EO", "CG", "TS", "EF", "ET"}
EIXO_FAMILIES = {"SEL", "EMP", "FIN", "CID"}
EIXO_FAMILY_NAMES = {"socioemocional", "empreendedorismo", "educacao financeira",
                     "cidadania digital"}
PERFIL = ["investigacao", "pensamento critico", "resolucao de problemas", "comunicacao",
          "colaboracao", "empatia", "autonomia", "integridade", "autoconsciencia",
          "cidadania global"]

NOMES_PERFIL = {"investigacao": "Investigacao", "pensamento critico": "Pensamento Critico",
                "resolucao de problemas": "Resolucao de Problemas", "comunicacao": "Comunicacao",
                "colaboracao": "Colaboracao", "autoconsciencia": "Autoconsciencia",
                "autonomia": "Autonomia"}

# Fase -> Perfil predominante (termos-e-nomes.md, secao 9). Enfases, nao exclusivas.
FASES = [(1, 2, "Imersao", ["autoconsciencia", "empatia"]),
         (3, 4, "Investigacao", ["investigacao", "pensamento critico"]),
         (5, 6, "Criacao", ["resolucao de problemas", "colaboracao"]),
         (7, 9, "Experimentacao", ["resolucao de problemas", "colaboracao"]),
         (10, 11, "Apresentacao", ["comunicacao"]),
         (12, 12, "Avaliacao e Reflexao", ["autoconsciencia", "autonomia"])]

INVISIVEL = ["compreende", "entende", "sabe", "conhece", "aprende", "percebe", "valoriza",
             "aprecia", "assimila", "internaliza", "adquire", "interioriza", "domina",
             "memoriza", "familiariza-se", "se familiariza", "familiarizar-se"]
ABERTURAS_RUINS = ["ao final da aula", "ao final da atividade", "espera-se que", "sera capaz",
                   "o aluno", "a aluna", "os alunos", "a crianca sera", "as criancas serao"]
OBJ_PROIBIDOS = ["criar espaco para", "mobilizar", "consolidar", "promover", "proporcionar",
                 "oportunizar", "trabalhar", "estimular", "favorecer",
                 "desenvolver a capacidade", "possibilitar", "propiciar"]
PROIBIDOS_VOZ = ["aluno", "aluna", "alunos", "alunas", "estudante", "estudantes", "educando",
                 "educandos"]
# Marcas de que o Resultado descreve a tarefa desta aula, nao a capacidade do ciclo.
MARCAS_DE_AULA = ["hoje", "nesta aula", "desta aula", "na aula de", "durante a aula"]
POR_EXTENSO = ["dois", "duas", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove",
               "dez", "onze", "doze", "treze", "quatorze", "catorze", "quinze", "vinte"]

# Idade (so avisos). Tirado de dados/marcos-aprendizagem-desenvolvimento.md.
# Secao 3, relacao numero e quantidade: 3a6m a 4a "3 ate 5" · 4a a 5a "5 a 8" · 5a a 6a "ate 10".
NUM_QTD = {"G3": 5, "G4": 8, "G5": 10}
# Secao 5, erros comuns: letra e som antes dos 5 anos; leitura de palavras aos 4 anos;
# escrita autonoma convencional em nenhuma faixa ate 6 anos.
LETRA_SOM = ["letra e som", "letras e sons", "letras aos sons", "sons das letras",
             "som de cada letra", "som das letras", "letra ao som", "sons as letras"]
LER_PALAVRAS = ["ler palavras", "leitura de palavras", "ler as palavras"]
ESCRITA_CONVENCIONAL = ["escrita convencional", "escrita autonoma", "escrever sozinh",
                        "escrever com autonomia", "escrever corretamente", "ortografia"]

CODE_RE = re.compile(r"\bEI0[2-5][A-Z]{2,3}\d{2}\b")
FAMILY_RE = re.compile(r"^EI0[2-5]([A-Z]{2,3})\d{2}$")
CODELINE_RE = re.compile(r"^\s*-\s*\*\*(EI0[2-5][A-Z]{2,3}\d{2})\*\*\s*(?:·\s*)?(.+)$")
HEAD_RE = re.compile(r"^#{2,4}\s+(.+)$")
BOLDLINE_RE = re.compile(r"^\*\*[^*]+\*\*\s*$")
LESSON_RE = re.compile(r"\bS(\d{1,2})\.D\d\.A\d\b")

# Titulos aceitos para cada campo (comparados sem acento, pelo comeco).
CAMPOS = [("objetivo", "Objetivo da Aula", ["objetivo da aula"]),
          ("bncc", "Habilidades BNCC", ["habilidades bncc", "bncc"]),
          ("eixos", "Eixos Transversais", ["eixos transversais"]),
          ("perfil", "Perfil da Crianca Protagonista", ["perfil"]),
          ("resultados", "Resultados da Aprendizagem", ["resultados"])]


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


def plain(s):
    """Tira marcas de Markdown (negrito, italico, crase) e espacos extras."""
    return " ".join(re.sub(r"[*_`]+", "", s).split())


class Report:
    def __init__(self): self.errors = []; self.warnings = []
    def error(self, w, m): self.errors.append((w, m))
    def warn(self, w, m): self.warnings.append((w, m))
    def show(self):
        if self.errors:
            print("ERROS (%d)" % len(self.errors))
            for w, m in self.errors: print("  [%s] %s" % (w, m))
        if self.warnings:
            print("\nAVISOS (%d)" % len(self.warnings))
            for w, m in self.warnings: print("  [%s] %s" % (w, m))
        if not self.errors and not self.warnings:
            print("Nenhum problema mecanico encontrado.")
        print("\nO que este script NAO confere: se o codigo descreve o que a crianca faz nos "
              "Momentos, se o Resultado e honesto quanto a profundidade e a idade, e se o "
              "eixo e o Perfil aparecem de verdade na aula. Confira a mao.")


def load_bncc():
    path = os.path.join(DADOS, "bncc.md")
    if not os.path.exists(path): return None
    out = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*-\s*\*\*(EI0[23][A-Z]{2}\d{2})\*\*\s*(.+)$", line.strip())
        if m: out[m.group(1)] = m.group(2).strip()
    return out or None


def load_eixos(level):
    """Habilidades de eixos.csv do nivel (prefixo EI03/EI04/EI05). Uso interno."""
    path = os.path.join(DADOS, "eixos.csv")
    if not os.path.exists(path): return []
    with open(path, encoding="utf-8", newline="") as f:
        return [r["habilidade"] for r in csv.DictReader(f)
                if r.get("codigo", "").startswith(EIXO_PREFIX[level])]


def split_sections(text):
    parts = re.split(r"^##\s+(.+)$", text, flags=re.M)
    if len(parts) == 1: return [("documento", text)]
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def field_blocks(body):
    """{campo: [linhas]} com o texto abaixo de cada titulo de campo, ate o proximo titulo."""
    out, cur = {}, None
    for line in body.splitlines():
        if BOLDLINE_RE.match(line.strip()) or line.strip() == "---":
            cur = None; continue  # titulo em negrito (ex.: um Momento) ou linha fecha o campo
        h = HEAD_RE.match(line.strip())
        if h:
            name = acc(plain(h.group(1)))
            cur = None
            for key, _, heads in CAMPOS:
                if any(name.startswith(x) for x in heads):
                    cur = key; out.setdefault(key, []); break
            continue
        if cur: out[cur].append(line)
    return out


def parse_resultados(lines):
    rows, in_t = [], False
    for line in lines:
        s = line.strip()
        if not s.startswith("|"): in_t = False; continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2: continue
        if acc(cells[0]) == "resultado": in_t = True; continue
        if set(cells[0]) <= set("-: "): continue
        if in_t: rows.append((cells[0], cells[1]))
    return rows


def parse_perfil(body, blocks):
    """Lista de competencias, ou None se o campo nao esta na aula."""
    tail = None
    if "perfil" in blocks:
        lines = [l.strip() for l in blocks["perfil"] if l.strip()]
        if not lines: return []
        if lines[0].startswith("- "):
            return [plain(l[2:]).rstrip(". ") for l in lines if l.startswith("- ")]
        tail = lines[0]
    else:  # linha solta: **Perfil da Crianca Protagonista:** A · B
        for line in body.splitlines():
            if acc(line).lstrip("*#> -").startswith("perfil d") and ":" in line:
                tail = line.split(":", 1)[1]; break
    if tail is None: return None
    return [plain(a).strip(" .") for a in re.split(r"·|\||,|;", tail) if plain(a).strip(" .")]


def first_word(s):
    w = acc(plain(s)).split()
    return w[0] if w else ""


def check_outcome(sent, where, rep, label):
    flat = acc(plain(sent)); words = flat.split(); first = words[0] if words else ""
    snip = sent[:55] + ("..." if len(sent) > 55 else "")
    for v in INVISIVEL:
        if flat.startswith(v) or first == v:
            rep.error(where, "%s abre com verbo invisivel (\"%s\"): \"%s\"" % (label, first, snip)); break
    stem = re.sub(r"-(se|lo|la|los|las|lhe|lhes|o|a|os|as)$", "", first)
    if stem and not re.search(r"(ar|er|ir|or)$", stem):
        rep.error(where, "%s nao abre no infinitivo (\"%s\"): \"%s\"" % (label, first, snip))
    for op in ABERTURAS_RUINS:
        if flat.startswith(op):
            rep.error(where, "%s com abertura fora do formato (\"%s\")." % (label, op)); break
    if len(words) > 22:
        rep.warn(where, "%s longo (%d palavras): \"%s\"" % (label, len(words), snip))


def check_voice(lines, where, rep):
    for line in lines:
        if CODELINE_RE.match(line.strip()):  # descritor BNCC e verbatim: nao se mexe
            continue
        flat = acc(line); snip = plain(line)[:45]
        for w in PROIBIDOS_VOZ:
            if re.search(r"\b%s\b" % w, flat):
                rep.error(where, "Use 'crianca(s)', nunca '%s': \"%s\"" % (w, snip)); break
        if "cada crianca" in flat:
            rep.error(where, "Use 'a crianca', nunca 'cada crianca': \"%s\"" % snip)
        if "—" in line or "–" in line:
            rep.warn(where, "Travessao num campo. A casa nao usa travessao: \"%s\"" % snip)
        if re.search(r"\b(professor|professora|tia)\b", flat):
            rep.warn(where, "Prefira 'educador' a professor/tia: \"%s\"" % snip)
        for n in POR_EXTENSO:
            if re.search(r"\b%s\b" % n, flat):
                rep.warn(where, "Numero por extenso (\"%s\"). Na pagina, use algarismo." % n); break


def check_age(text, where, rep, level, label):
    """Avisos de idade tirados da secao 5 do documento de marcos. Pedem confirmacao."""
    flat = acc(plain(text))
    if re.search(r"\b(cont|quantidade|quantos|numer|numeral)", flat):
        for n in re.findall(r"\b(\d{1,3})\b", flat):
            if int(n) > NUM_QTD[level]:
                rep.warn(where, "%s pede quantidade %s. Em %s, a relacao numero e quantidade da "
                         "faixa vai ate %d (marcos, secao 3). Acima disso, so com apoio do "
                         "educador, nunca como criterio." % (label, n, NIVEL_NOME[level], NUM_QTD[level]))
                break
    if level in ("G3", "G4"):
        if any(k in flat for k in LETRA_SOM):
            rep.warn(where, "%s pede relacao entre letra e som. Antes dos 5 anos a crianca "
                     "escolhe letras de forma arbitraria (marcos, secao 5)." % label)
        if any(k in flat for k in LER_PALAVRAS):
            rep.warn(where, "%s pede leitura de palavras. Ela aparece de 5 a 6 anos; antes, "
                     "leitura por imagens, rotulos e simbolos (marcos, secao 5)." % label)
    if any(k in flat for k in ESCRITA_CONVENCIONAL):
        rep.warn(where, "%s parece pedir escrita autonoma convencional. Nenhuma faixa ate 6 anos "
                 "preve isso (marcos, secao 5)." % label)


def fase_da_semana(semana):
    for a, b, nome, comps in FASES:
        if a <= semana <= b: return nome, comps
    return None, None


def check_section(title, body, level, ref, eixos_ref, semana_arg, semana_doc, rep):
    where = title
    blocks = field_blocks(body)
    code_lines = [(m.group(1), m.group(2).strip()) for m in
                  (CODELINE_RE.match(l.strip()) for l in blocks.get("bncc", body.splitlines())) if m]
    res_lines = blocks.get("resultados", body.splitlines())
    res = parse_resultados(res_lines)
    perfil = parse_perfil(body, blocks)

    presentes = {"objetivo": "objetivo" in blocks,
                 "bncc": "bncc" in blocks or bool(code_lines),
                 "eixos": "eixos" in blocks,
                 "perfil": perfil is not None,
                 "resultados": "resultados" in blocks or bool(res)}
    if not any(presentes.values()):
        return  # secao sem nenhum dos cinco campos (rotina, notas): nada a conferir
    for key, nome, _ in CAMPOS:
        if not presentes[key]:
            rep.error(where, "Campo ausente: %s." % nome)

    # Voz, so dentro dos cinco campos
    voz = []
    for key in blocks: voz.extend(blocks[key])
    if "perfil" not in blocks:
        voz.extend(l for l in body.splitlines() if acc(l).lstrip("*#> -").startswith("perfil d"))
    check_voice(voz, where, rep)

    modo = acc(title + " " + " ".join(l for l in body.splitlines()
                                      if re.match(r"^[*_\s>-]*(modo|bloco)", acc(l))))
    exploratoria = "dirigida pela crianca" in modo or "exploratoria" in modo

    # Objetivo da Aula
    if "objetivo" in blocks:
        para = []
        for l in blocks["objetivo"]:
            if l.strip(): para.append(l.strip())
            elif para: break
        obj = plain(" ".join(para)); low = acc(obj)
        if not obj:
            rep.error(where, "Objetivo da Aula vazio.")
        else:
            nw = len(obj.split())
            if CODE_RE.search(obj):
                rep.error(where, "O Objetivo carrega codigo.")
            for v in OBJ_PROIBIDOS:
                if low.startswith(v):
                    rep.error(where, "Objetivo abre com abstracao proibida (\"%s\")." % v); break
            if nw < 10 or nw > 15:
                rep.warn(where, "Objetivo com %d palavras. O formato pede de 10 a 15." % nw)
            sents = [x for x in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÜÇ])", obj) if x.strip()]
            if len(sents) > 1:
                rep.warn(where, "Objetivo com %d frases. O formato pede uma." % len(sents))
            if not re.search(r"\bpara\b|\ba fim de\b", low):
                rep.warn(where, "Objetivo sem finalidade (normalmente com 'para').")
            acao = re.split(r"\bpara\b|\ba fim de\b", low)[0]
            if re.search(r"\be\s+\w+(ar|er|ir)\b", acao):
                rep.warn(where, "Objetivo parece juntar duas acoes com 'e'. Uma acao, uma finalidade.")
            fw = re.sub(r"-(se|lo|la|los|las)$", "", first_word(obj))
            if fw and not re.search(r"(ar|er|ir|or)$", fw):
                rep.warn(where, "Objetivo nao abre com verbo no infinitivo (\"%s\")." % fw)
            if exploratoria and "escolh" not in low:
                rep.warn(where, "Aula Dirigida pela crianca: a acao do Objetivo e a escolha da "
                         "crianca. Confira se o Objetivo diz isso.")
            check_age(obj, where, rep, level, "Objetivo")

    # Habilidades BNCC
    bncc_codes = []
    for code, desc in code_lines:
        fam = FAMILY_RE.match(code); family = fam.group(1) if fam else ""
        if family in EIXO_FAMILIES:
            rep.error(where, "Eixo %s aparece como codigo BNCC. Eixos sao familia + frase, sem codigo." % code); continue
        if family not in BNCC_FAMILIES:
            rep.error(where, "Familia de codigo desconhecida em %s." % code); continue
        if code in bncc_codes:
            rep.error(where, "Codigo %s repetido." % code); continue
        bncc_codes.append(code)
        if code[:4] != BNCC_PREFIX[level]:
            rep.error(where, "BNCC %s tem prefixo %s. Em %s, BNCC usa %s."
                      % (code, code[:4], NIVEL_NOME[level], BNCC_PREFIX[level]))
        if ref is not None:
            off = ref.get(code)
            if off is None:
                rep.error(where, "Codigo %s nao existe em dados/bncc.md." % code)
            elif acc(off).rstrip(". ") != acc(desc).rstrip(". "):
                rep.error(where, "Descritor de %s diverge da base. Copie verbatim.\n"
                          "      aula: %s\n      base: %s" % (code, desc, off))
    if "bncc" in blocks:
        soltos = [c for c in CODE_RE.findall("\n".join(blocks["bncc"]))
                  if c not in bncc_codes and (FAMILY_RE.match(c).group(1) in BNCC_FAMILIES)]
        for c in dict.fromkeys(soltos):
            rep.warn(where, "Codigo %s sem a linha '- **%s** descritor'. O descritor nao foi conferido." % (c, c))
            bncc_codes.append(c)
    if presentes["bncc"]:
        if len(bncc_codes) < 2:
            rep.error(where, "%d codigo(s) BNCC. Minimo 2." % len(bncc_codes))
        elif len(bncc_codes) > 4:
            rep.error(where, "%d codigos BNCC. Maximo 4." % len(bncc_codes))

    # Resultados da Aprendizagem
    if "resultados" in blocks and not res:
        rep.error(where, "Secao Resultados sem tabela '| Resultado | Vem de |'.")
    if res:
        if len(res) < 2: rep.error(where, "Apenas %d Resultado(s). Minimo 2." % len(res))
        elif len(res) > 4: rep.error(where, "%d Resultados. Maximo 4." % len(res))
        usados = {}
        for r, vem in res:
            codes = CODE_RE.findall(vem)
            snip = r[:50] + ("..." if len(r) > 50 else "")
            if not codes:
                rep.error(where, "Resultado sem codigo em 'Vem de': \"%s\"" % snip)
            elif len(codes) > 1:
                rep.error(where, "Um Resultado por codigo. 'Vem de' traz %s." % ", ".join(codes))
            for c in codes:
                fm = FAMILY_RE.match(c)
                if fm and fm.group(1) in EIXO_FAMILIES:
                    rep.error(where, "Eixo %s na coluna 'Vem de'. So BNCC gera Resultado." % c); continue
                usados[c] = usados.get(c, 0) + 1
                if bncc_codes and c not in bncc_codes:
                    rep.error(where, "Resultado vem de %s, que nao esta nas Habilidades BNCC." % c)
                desc = (ref or {}).get(c)
                if desc:
                    if first_word(r) == first_word(desc):
                        rep.warn(where, "Resultado copia o verbo do descritor de %s (\"%s\"). "
                                  "O codigo ancora, nao redige." % (c, first_word(desc)))
                    elif difflib.SequenceMatcher(None, acc(plain(r)), acc(desc)).ratio() > 0.75:
                        rep.error(where, "Resultado repete o descritor de %s. Escreva a capacidade "
                                  "que a aula mostra." % c)
            check_outcome(r, where, rep, "Resultado")
            flat = acc(plain(r))
            if any(re.search(r"\b%s\b" % m, flat) for m in MARCAS_DE_AULA) or "*" in r:
                rep.warn(where, "Resultado fala da aula ou do material (\"%s\"). O Resultado e do ciclo." % snip)
            check_age(r, where, rep, level, "Resultado")
        for c, n in usados.items():
            if n > 1: rep.error(where, "%s gera %d Resultados. Um por codigo." % (c, n))
        for c in bncc_codes:
            if c not in usados: rep.error(where, "Codigo %s sem Resultado. Um por codigo." % c)

    # Eixos Transversais
    if "eixos" in blocks:
        eixos = [l.strip()[2:].strip() for l in blocks["eixos"] if l.strip().startswith("- ")]
        if len(eixos) == 0: rep.error(where, "Secao Eixos Transversais sem nenhum eixo.")
        elif len(eixos) > 2: rep.error(where, "%d eixos. Maximo 2 por aula." % len(eixos))
        for raw in eixos:
            if CODE_RE.search(raw):
                rep.error(where, "Codigo na linha do eixo. E familia + frase, sem codigo: \"%s\"" % raw[:45])
            if ":" not in raw:
                rep.error(where, "Eixo fora do formato 'Familia: frase': \"%s\"" % raw[:45]); continue
            fam, frase = raw.split(":", 1)
            fam = plain(fam)
            if acc(fam) not in EIXO_FAMILY_NAMES:
                rep.error(where, "\"%s\" nao e familia de eixo valida." % fam)
            frase = plain(frase)
            if not frase:
                rep.error(where, "Eixo sem frase de aprendizagem."); continue
            check_outcome(frase, where, rep, "Frase do eixo")
            for hab in eixos_ref:
                if difflib.SequenceMatcher(None, acc(frase).rstrip(". "), acc(hab).rstrip(". ")).ratio() > 0.85:
                    rep.error(where, "Frase do eixo copia a habilidade de eixos.csv (\"%s\"). "
                              "Escreva a frase da aula com a regua do Resultado." % hab[:50]); break
            check_age(frase, where, rep, level, "Frase do eixo")

    # Perfil da Crianca Protagonista (2 a 3)
    if perfil is not None:
        raw_perfil = " ".join(perfil)
        if CODE_RE.search(raw_perfil):
            rep.error(where, "Codigos no campo Perfil (%s). Escreva os nomes das competencias."
                      % ", ".join(CODE_RE.findall(raw_perfil)))
        else:
            if len(perfil) < 2: rep.error(where, "Perfil com %d competencia(s). Minimo 2." % len(perfil))
            elif len(perfil) > 3: rep.error(where, "Perfil com %d competencias. Maximo 3." % len(perfil))
            vistos = []
            for a in perfil:
                if acc(a) not in PERFIL:
                    rep.error(where, "\"%s\" nao esta entre as dez competencias do Perfil." % a)
                elif acc(a) in vistos:
                    rep.error(where, "\"%s\" repetida no Perfil." % a)
                vistos.append(acc(a))
            m = LESSON_RE.search(title)
            semana = semana_arg or (int(m.group(1)) if m else semana_doc)
            if semana and perfil:
                fase, comps = fase_da_semana(semana)
                if fase and acc(perfil[0]) not in comps:
                    rep.warn(where, "Semana %d, fase %s: a primeira competencia vem da fase (%s). "
                             "Se a enfase da fase nao aparece na aula, sinalize nas Decisoes em aberto."
                             % (semana, fase, " ou ".join(NOMES_PERFIL[c] for c in comps)))
            elif perfil:
                rep.warn(where, "Semana nao encontrada (S#.D#.A# no titulo ou --semana). "
                         "A competencia da fase nao foi conferida.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--nivel", required=True)
    ap.add_argument("--semana", type=int, help="semana do projeto (1 a 12), para a fase do Perfil")
    ap.add_argument("--sem-verbatim", action="store_true")
    a = ap.parse_args()
    lvl = NIVEL_MAP.get(acc(a.nivel).strip())
    if not lvl: sys.exit("Nivel invalido: use Infantil 3, 4 ou 5.")
    if a.semana is not None and not 1 <= a.semana <= 12:
        sys.exit("Semana invalida: use de 1 a 12.")
    if not os.path.exists(a.file): sys.exit("Arquivo nao encontrado: %s" % a.file)
    text = open(a.file, encoding="utf-8").read()
    ref = None if a.sem_verbatim else load_bncc()
    if ref is None and not a.sem_verbatim:
        print("AVISO: nao achei dados/bncc.md. Descritores nao conferidos.\n")
    eixos_ref = load_eixos(lvl)
    m = LESSON_RE.search(text)
    semana_doc = int(m.group(1)) if m else None
    rep = Report()
    for t, b in split_sections(text):
        check_section(t, b, lvl, ref, eixos_ref, a.semana, semana_doc, rep)
    rep.show()
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
