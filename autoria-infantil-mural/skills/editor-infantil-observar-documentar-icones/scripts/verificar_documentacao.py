#!/usr/bin/env python3
"""
verificar_documentacao.py - conferencia mecanica da Documentacao Pedagogica (Observar e
Documentar) e dos icones de registro das aulas da Educacao Infantil do Intercriativa Lab.

Autossuficiente: so usa a biblioteca padrao do Python. Le dois tipos de entrada:
  - aula(s) em Markdown ou texto (.md, .txt): o campo "Documentação Pedagógica" com as duas
    linhas, os Momentos no formato "número | título", os Resultados e, se houver, a linha
    "Marca no Momento" da entrega da skill. Varias aulas no mesmo arquivo: cada uma comeca num
    titulo (# ou **) com o codigo S#.D#.A#.
  - o arquivo de conteudo do PDF (.json com "card3"): confere card3.aulas[n].documentacao e os
    icones nos titulos dos Momentos (card4 a card7).

Uso:
  python3 verificar_documentacao.py aula.md --nivel "Infantil 4"
  python3 verificar_documentacao.py S2.D1.md S2.D2.md S2.D3.md S2.D4.md S2.D5.md
  python3 verificar_documentacao.py S2.D3.json

Com 2 aulas ou mais, mostra a distribuicao dos meios de registro por semana.
Sai com 1 se houver erro, 0 se so houver avisos ou nada, 2 se a entrada for ilegivel.

Nao julga se a lente e boa, se desce um nivel abaixo do Resultado, nem se o Momento e o
melhor. Isso continua com a pessoa.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

# --------------------------------------------------------------------------------------------
# Icones. O padrao e o mesmo do render.py da etapa do PDF: o que passa aqui, o PDF desenha.
# --------------------------------------------------------------------------------------------
ICONE_RE = re.compile(r"<\s*icone\s*:\s*([^<>]+?)\s*>", re.I)
ICONES = ["observar", "foto", "video", "audio", "escrita", "producao"]
MEIOS = ["foto", "escrita", "audio", "video", "producao"]
NOME_MEIO = {"foto": "foto", "escrita": "escrita", "audio": "áudio", "video": "vídeo",
             "producao": "produção"}

LIMITE_LINHA = 82   # celula de Documentacao do card 3 no PDF; o icone conta 1
LIMITE_TITULO = 30  # titulo do Momento, termos-e-nomes v7 (30 desde 29/09/2026; o numero nao conta)

CODIGO_RE = re.compile(r"\bS(\d{1,2})\.D([1-5])\.A([1-4])\b")
ROTULO_RE = re.compile(r"^[\s*_>•-]*(observar|documentar)[\s*_]*:[\s*_]*", re.I)

ABRE_OBSERVAR = ("escute", "observe", "repare", "note", "perceba", "acompanhe", "compare",
                 "preste atencao")
# verbo de abertura da linha Documentar -> meio
METODO = {"anote": "escrita", "escreva": "escrita", "transcreva": "escrita",
          "fotografe": "foto", "filme": "video", "grave": None,
          "recolha": "producao", "guarde": "producao"}
ABRE_MOMENTO = ("na conversa", "na roda", "no momento", "ao voltar", "durante", "depois de",
                "depois que", "antes de", "no fim", "no final", "ao final", "no comeco",
                "no inicio", "enquanto", "quando a", "quando as", "quando o", "ao longo")
MOMENTO_VAGO = ("durante a atividade", "durante a aula", "durante toda", "ao longo da aula",
                "ao longo da atividade", "ao longo do dia", "na conversa", "a qualquer momento",
                "em qualquer momento", "no decorrer")

MENTAL_RE = re.compile(r"\b(compreend\w*|entend(e|em|er|eu)\b|sab(e|em|er)\b|conhec(e|em|er)\b|"
                       r"perceb(e|em|er|eu)\b|reconhec(e|em|er|eu)\b|investig(a|am|ar)\b|"
                       r"aprend(e|em|er|eu)\b|domin(a|am|ar)\b|assimil\w*)")
PARTICIPA_ERRO_RE = re.compile(r"\b(participa\w*|interesse|interessad\w*|envolvimento|"
                               r"engajament\w*|engajad\w*|comportament\w*)")
PARTICIPA_AVISO_RE = re.compile(r"\b(criatividade|criativ\w*|autonomia|atencao|atent[ao]s?|"
                                r"concentrad\w*|concentracao|gost(a|am|ou|aram)\b)")
EDUCADOR_RE = re.compile(r"\b(o apoio que|a ajuda que|as respostas (a|as) pergunta|"
                         r"o que o educador|a intervencao|as perguntas do educador|"
                         r"o educador (fez|disse|perguntou))")
VOZ = [(re.compile(r"\b(aluno|aluna|alunos|alunas|estudante|estudantes|educando|educandos)\b"),
        "Use criança ou crianças."),
       (re.compile(r"\bcada crianca\b"), "Nunca 'cada criança': use a criança ou as crianças."),
       (re.compile(r"\b(professor|professora|professores|tia|tias)\b"), "Use educador.")]

# Idade e etica (marcos-aprendizagem-desenvolvimento.md, secoes 1, 5 e 6)
ROTULO_CRIANCA_RE = re.compile(r"\b(adiantad[ao]s?|atrasad[ao]s?|timid[ao]s?|"
                               r"mal adaptad[ao]s?|avancad[ao]s?)\b")
ROTULO_AVISO_RE = re.compile(r"\b(com dificuldades?|imatur[ao]s?|bagunceir[ao]s?|"
                             r"preguicos[ao]s?|mais esperto|mais esperta)\b")
EXPECTATIVA_RE = re.compile(r"(\bja deve\w*|\bdeveria\w*|\bdeve ser capaz|\bespera-se|"
                            r"\be esperado|\besperad[ao]s? para|\bpara a (sua )?idade|"
                            r"\badequad[ao]s? (a|para) (a )?idade|"
                            r"\bmarcos? (do|da|de) (desenvolvimento|aprendizagem|idade|faixa)|"
                            r"\bchecklist|\blista de verificacao)")
CRITERIO_RE = re.compile(r"(\bse (ela |ele |a crianca |as criancas )?(consegue|conseguiu|"
                         r"acerta|acertou|erra|errou)\b|\bconseguiu ou nao|\bacertou ou errou|"
                         r"\bcerto ou errado|\bse fez certo|\bse esta corret|\bcorretamente)")
AUSENCIA_RE = re.compile(r"\b(nao (consegue|conseguiu|sabe|faz|fez)|ainda nao)\b")
COLEGA_ERRO_RE = re.compile(r"\b(classifi\w*|julg\w*|vot(e|em|ar|am|acao)\b|de nota|"
                            r"dar nota|o melhor|a melhor)")
COLEGA_AVISO_RE = re.compile(r"\bavali\w*")
LETRA_SOM_RE = re.compile(r"(letra\w*.{0,40}\b(som|sons)\b|\b(som|sons)\b.{0,40}letra|"
                          r"correspond\w* (entre )?(letra|som|sonora)|valor sonoro)")
LER_PALAVRAS_RE = re.compile(r"\b(le|leia|lendo|ler|leem)\b (as |a |uma |umas )?palavras|"
                             r"leitura de palavras")
ESCRITA_CONV_RE = re.compile(r"escrita (autonoma|convencional|correta)|escreve corretamente")
QUANTIDADE_10_RE = re.compile(r"(quantidade|cont\w*).{0,40}\bat[e] (10|dez)\b")
CONFLITO_RE = re.compile(r"conflito")
SOZINHA_RE = re.compile(r"sozinh|sem (ajuda|apoio|media)|autonom")

STOP = set("""a o as os um uma uns umas de da do das dos em na no nas nos por para pela pelo
com sem que como e ou se sua seu suas seus ao aos crianca criancas educador sobre entre ate
mais menos quando qual quais isso isto essa esse ela ele elas eles lhe cada todo toda todos
todas outra outro outras outros mesma mesmo quem onde""".split())


def fold(s):
    """Minusculas e sem acento: 'Produção' -> 'producao'."""
    n = unicodedata.normalize("NFKD", str(s)).lower()
    return "".join(c for c in n if not unicodedata.combining(c))


def n_car(s):
    """Tamanho como sai na pagina: cada icone conta 1 (igual ao check_budgets.py do PDF)."""
    return len(ICONE_RE.sub("•", unicodedata.normalize("NFC", str(s))))


def limpa_marcadores(linha):
    s = linha.strip()
    s = re.sub(r"^(>\s*)+", "", s)
    s = re.sub(r"^([-*•]\s+|\d+[.)]\s+)", "", s)
    s = s.strip().strip("`").strip()
    return s


def limpa_titulo(linha):
    s = linha.strip()
    s = re.sub(r"^(>\s*)+", "", s)
    s = s.lstrip("#").strip()
    s = s.strip("*_` ").strip()
    return s


class Relatorio:
    def __init__(self):
        self.aulas = []  # (titulo, linhas, erros, avisos)

    def nova(self, titulo):
        item = {"titulo": titulo, "linhas": [], "erros": [], "avisos": []}
        self.aulas.append(item)
        return item


class Aula:
    def __init__(self, nome, codigo="", nivel=None, par=None, resultados=None, momentos=None,
                 outros=None, pdf=False, indice=None):
        self.nome = nome
        self.codigo = codigo
        self.nivel = nivel
        self.par = par or []
        self.resultados = resultados or []
        self.momentos = momentos or []   # (numero, titulo com icones, 'aula' ou 'marca')
        self.outros = outros or []       # textos fora do par e dos titulos
        self.pdf = pdf
        self.indice = indice
        self.meio = None


# --------------------------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------------------------
LABELS_PARADA = ("dica", "eixos", "perfil", "resultados", "objetivo", "habilidades",
                 "materiais", "descricao", "momentos", "lente", "no pdf", "marca no momento",
                 "biblioteca", "bncc")


def e_parada(linha):
    s = linha.strip()
    if not s:
        return False
    if s.startswith("#") or s.startswith("```"):
        return True
    if re.match(r"^\*\*[^*]+\*\*:?\s*$", s):
        return True
    f = fold(limpa_titulo(s))
    for lab in LABELS_PARADA:
        if f.startswith(lab) and (f == lab or f[len(lab):len(lab) + 1] in (":", " ", "")):
            if lab in ("lente", "no pdf", "marca no momento") or ":" in f[:40] or f == lab:
                return True
    return bool(re.match(r"^(\d)\s*\|\s*\S", limpa_titulo(s)))


def titulo_momento(linha):
    s = limpa_titulo(linha)
    m = re.match(r"^(?:momento\s*)?(\d)\s*\|\s*(.+)$", s, re.I)
    if m:
        return int(m.group(1)), m.group(2).strip()
    return None


def marca_momento(linha):
    """Linha da entrega: Marca no Momento: card4.momentos[3].titulo = Titulo <icone: ...>"""
    s = limpa_marcadores(linha).replace("`", "")
    if not fold(s).startswith("marca no momento"):
        return None
    m = re.search(r"momentos\[(\d)\]\.titulo\s*[=:]\s*(.+)$", s)
    if m:
        return int(m.group(1)), m.group(2).strip().strip('"')
    m = re.search(r"(\d)\s*\|\s*(.+)$", s)
    if m:
        return int(m.group(1)), m.group(2).strip()
    return None


def nivel_de(texto):
    m = re.search(r"Infantil\s*([345])", texto)
    return int(m.group(1)) if m else None


def ler_bloco_md(nome, linhas, nivel_padrao):
    texto = "\n".join(linhas)
    codigo_m = CODIGO_RE.search(nome)
    aula = Aula(nome=nome, codigo=codigo_m.group(0) if codigo_m else "",
                nivel=nivel_de(texto) or nivel_padrao)
    usadas = set()

    # Momentos e marcas
    for i, l in enumerate(linhas):
        mm = marca_momento(l)
        if mm:
            aula.momentos.append((mm[0], mm[1], "marca"))
            usadas.add(i)
            continue
        tm = titulo_momento(l)
        if tm:
            aula.momentos.append((tm[0], tm[1], "aula"))
            usadas.add(i)

    # Documentacao Pedagogica
    inicio = None
    for i, l in enumerate(linhas):
        if "documentacao pedagogica" in fold(l):
            inicio = i
            break
    par = []
    if inicio is not None:
        usadas.add(inicio)
        resto = re.split(r"(?i)documenta[çc][ãa]o pedag[óo]gica", linhas[inicio], 1)
        resto = resto[1].strip(" *:_#") if len(resto) > 1 else ""
        if ICONE_RE.search(resto) or ROTULO_RE.match(resto):
            par.append(resto)
        for j in range(inicio + 1, len(linhas)):
            l = linhas[j]
            if not l.strip():
                continue
            if e_parada(l) and not ROTULO_RE.match(limpa_marcadores(l)):
                break
            usadas.add(j)
            par.append(limpa_marcadores(l))
    else:
        for i, l in enumerate(linhas):
            if i in usadas:
                continue
            s = limpa_marcadores(l)
            if re.match(r"^<\s*icone", s, re.I) or ROTULO_RE.match(s):
                par.append(s)
                usadas.add(i)
    aula.par = par

    # Resultados
    for i, l in enumerate(linhas):
        f = fold(limpa_titulo(l))
        if f.startswith("resultados"):
            for j in range(i + 1, len(linhas)):
                s = linhas[j].strip()
                if not s:
                    if aula.resultados:
                        break
                    continue
                if e_parada(s) or "documentacao pedagogica" in fold(s):
                    break
                if s.startswith("|"):
                    celulas = [c.strip() for c in s.strip("|").split("|")]
                    if not celulas or set(celulas[0]) <= set("-: "):
                        continue
                    if fold(celulas[0]) in ("resultado", "resultados"):
                        continue
                    aula.resultados.append(celulas[0])
                else:
                    aula.resultados.append(limpa_marcadores(s))
            break

    aula.outros = [linhas[i] for i in range(len(linhas)) if i not in usadas]
    return aula


def ler_md(caminho, texto, nivel_padrao):
    linhas = texto.splitlines()
    inicios = [i for i, l in enumerate(linhas)
               if (l.strip().startswith("#") or l.strip().startswith("**"))
               and CODIGO_RE.search(l) and not titulo_momento(l)]
    nivel_arquivo = nivel_de(texto) if len(set(re.findall(r"Infantil\s*([345])", texto))) == 1 \
        else None
    nivel_padrao = nivel_padrao or nivel_arquivo
    if not inicios:
        nome = next((limpa_titulo(l) for l in linhas if l.strip().startswith("#")),
                    os.path.basename(caminho))
        return [ler_bloco_md(nome, linhas, nivel_padrao)]
    preambulo = "\n".join(linhas[:inicios[0]])
    nivel_padrao = nivel_padrao or nivel_de(preambulo)
    aulas = []
    for k, ini in enumerate(inicios):
        fim = inicios[k + 1] if k + 1 < len(inicios) else len(linhas)
        aulas.append(ler_bloco_md(limpa_titulo(linhas[ini]), linhas[ini + 1:fim], nivel_padrao))
    return aulas


def ler_json(caminho, d, nivel_padrao):
    if "card3" not in d:
        raise ValueError("JSON sem 'card3': nao parece o arquivo de conteudo do PDF.")
    c3 = d["card3"]
    turma = (d.get("card2", {}).get("footer", {}).get("turma", "")
             or c3.get("footer", {}).get("turma", ""))
    nivel = nivel_padrao or nivel_de(turma)
    aulas = []
    for i, a in enumerate(c3.get("aulas", []), 1):
        card = d.get("card%d" % (i + 3), {})
        momentos = [(k, m.get("titulo", ""), "aula")
                    for k, m in enumerate(card.get("momentos", []), 1)]
        outros = [card.get("intro", ""), (card.get("dica") or {}).get("text", "")]
        for m in card.get("momentos", []):
            outros.extend(m.get("bullets", []))
        outros.extend(a.get("resultados", []))
        codigo = card.get("code", "") or ""
        nome = "card3.aulas[%d] · %s%s" % (i, a.get("nome", "?"), (" · " + codigo) if codigo else "")
        aula = Aula(nome=nome, codigo=codigo, nivel=nivel, par=list(a.get("documentacao", [])),
                    resultados=a.get("resultados", []), momentos=momentos, outros=outros,
                    pdf=True, indice=i)
        aulas.append(aula)
    return aulas


# --------------------------------------------------------------------------------------------
# Conferencia
# --------------------------------------------------------------------------------------------
def raizes(texto):
    return {w[:5] for w in re.findall(r"[a-z]+", fold(texto)) if len(w) > 3 and w not in STOP}


def sem_abertura(corpo_f):
    """Tira o verbo de abertura, para os testes de conteudo nao pegarem 'Perceba' ou 'Preste atencao'."""
    for ab in ("preste atencao em", "preste atencao", "repare em", "repare"):
        if corpo_f.startswith(ab):
            return corpo_f[len(ab):].strip()
    partes = corpo_f.split(" ", 1)
    return partes[1] if len(partes) > 1 else ""


def meio_da_palavra(palavras, i):
    w = palavras[i]
    if w not in METODO:
        return None, False
    meio = METODO[w]
    if w == "grave":
        prox = " ".join(palavras[i + 1:i + 6])
        if "video" in prox:
            return "video", False
        return "audio", "audio" not in prox
    return meio, False


def confere_linha_comum(linha, corpo, E, A, rotulo, aula):
    f = fold(corpo)
    if rotulo:
        E.append("Rótulo '%s:' impresso. O ícone faz esse papel; tire o rótulo." % rotulo.capitalize())
    t = n_car(linha)
    if t > LIMITE_LINHA:
        A.append("%d caracteres (limite %d, o ícone conta 1). Ao escrever, reescreva dentro do "
                 "limite; no texto do autor, informe a contagem e não corte." % (t, LIMITE_LINHA))
    if "(" in corpo or ")" in corpo:
        E.append("Parênteses na linha. Uma frase direta, sem parênteses.")
    if re.search(r"\bpor exemplo\b|\bex\.|\bcomo:|\betc\b", f):
        A.append("Lista de exemplos na frase. Diga o critério, não os exemplos.")
    if re.search(r"[.!?;]\s+\S", corpo.strip()):
        A.append("Mais de uma frase ou ponto e vírgula. Uma frase por linha.")
    if "—" in linha or "–" in linha:
        E.append("Travessão. A casa não usa travessão.")
    if re.search(r'["“”]', corpo):
        A.append("Aspas na linha. A Documentação não traz fala entre aspas.")
    for rx, msg in VOZ:
        mv = rx.search(f)
        if mv:
            E.append("'%s': %s" % (mv.group(0), msg))
    for vago in MOMENTO_VAGO:
        if vago in f:
            E.append("Momento vago ('%s'). Nomeie o Momento pelo número e título." % vago)
            break
    # idade e etica
    if ROTULO_CRIANCA_RE.search(f):
        E.append("Rótulo da criança ('%s'). Nenhum marco classifica a criança (marcos, seção 1)."
                 % ROTULO_CRIANCA_RE.search(f).group(0))
    elif ROTULO_AVISO_RE.search(f):
        A.append("Possível rótulo ('%s'). Descreva a ação, não a criança (marcos, seção 1)."
                 % ROTULO_AVISO_RE.search(f).group(0))
    if EXPECTATIVA_RE.search(f):
        E.append("Marco ou expectativa na página ('%s'). Os marcos orientam a observação; não "
                 "viram expectativa nem checklist (marcos, seções 1 e 6)."
                 % EXPECTATIVA_RE.search(f).group(0))
    if CRITERIO_RE.search(f):
        A.append("Registro como critério de sucesso ('%s'). Guarde o que a criança faz sozinha e "
                 "o que faz com apoio (marcos, seção 6)." % CRITERIO_RE.search(f).group(0))
    if AUSENCIA_RE.search(f):
        A.append("Ausência tratada como problema ('%s')? Ausência de marco é sinal para observar "
                 "mais; guarde o que a criança fez (marcos, seção 6)." % AUSENCIA_RE.search(f).group(0))
    if "colega" in f:
        if COLEGA_ERRO_RE.search(f):
            E.append("Crianças classificando colegas. Quem observa é o educador (marcos, seção 6).")
        elif COLEGA_AVISO_RE.search(f):
            A.append("Crianças avaliando colegas? Confira: quem observa é o educador (marcos, seção 6).")
    nv = aula.nivel
    if nv in (3, 4):
        if LETRA_SOM_RE.search(f):
            A.append("Relação entre letra e som: nos marcos aparece de 5a a 6a. Em Infantil %d, só "
                     "como experiência com apoio, nunca como critério (marcos, seções 1 e 5)." % nv)
        if LER_PALAVRAS_RE.search(f):
            A.append("Leitura de palavras conhecidas aparece de 5a a 6a. Em Infantil %d, leitura "
                     "por imagens, rótulos e símbolos (marcos, seção 5)." % nv)
        if QUANTIDADE_10_RE.search(f):
            A.append("Número e quantidade até 10: nos marcos, 3 até 5 (3a6m a 4a) e 5 a 8 (4a a "
                     "5a). Confira a faixa de Infantil %d (marcos, seção 3)." % nv)
        if CONFLITO_RE.search(f) and SOZINHA_RE.search(f):
            A.append("Resolução autônoma de conflito: aos 3 e 4 anos ainda com orientação ou "
                     "mediação do adulto (marcos, seção 5).")
    if ESCRITA_CONV_RE.search(f):
        A.append("Escrita convencional ou correta: nenhuma faixa até 6 anos prevê escrita "
                 "autônoma convencional (marcos, seção 5).")


def separa(linha):
    s = limpa_marcadores(linha)
    rotulo = None
    m = ROTULO_RE.match(s)
    if m:
        rotulo = m.group(1).lower()
        s = s[m.end():].strip()
    tokens = [mt.group(1) for mt in ICONE_RE.finditer(s)]
    comeca = bool(re.match(r"^<\s*icone", s, re.I))
    corpo = ICONE_RE.sub("", s).strip()
    return s, rotulo, tokens, comeca, corpo


def confere_tokens(tokens, E, A):
    validos = []
    for tk in tokens:
        chave = fold(tk).strip()
        if chave not in ICONES:
            E.append("Ícone desconhecido <icone: %s>. O PDF para. Válidos: %s."
                     % (tk, ", ".join(ICONES)))
            continue
        if tk != chave:
            A.append("Escreva <icone: %s>, na forma canônica (minúsculas, sem acento)." % chave)
        validos.append(chave)
    return validos


def confere_aula(aula, item):
    E, A = item["erros"], item["avisos"]
    par = [l for l in aula.par if l.strip()]
    if not par:
        E.append("Sem Documentação Pedagógica. Uma aula, uma lente, um par.")
        return
    if len(par) == 1:
        E.append("Só uma linha. O par tem duas: Observar e Documentar.")
    if len(par) > 2:
        E.append("%d linhas. Uma aula, uma lente, um par: escolha a lente e fique com duas linhas."
                 % len(par))

    # linha 1 · Observar
    s1, rot1, tk1, comeca1, corpo1 = separa(par[0])
    item["linhas"].append(("Observar", s1, n_car(s1)))
    v1 = confere_tokens(tk1, E, A)
    if not tk1:
        E.append("Observar sem <icone: observar> no início.")
    elif not comeca1:
        E.append("O ícone vem no início da linha Observar, antes do verbo.")
    if v1:
        if v1[0] != "observar":
            E.append("A linha Observar abre com <icone: observar>, não com <icone: %s>." % v1[0])
        if len(v1) > 1:
            E.append("Mais de um ícone na linha Observar. Um ícone por linha.")
    if rot1 == "documentar":
        E.append("A primeira linha é Observar; a ordem está trocada.")
    f1 = fold(corpo1)
    if not f1.startswith(ABRE_OBSERVAR):
        E.append("Observar abre com '%s'. Abra com verbo de observação: Escute, Observe, Repare "
                 "em, Note, Perceba, Acompanhe, Compare, Preste atenção em."
                 % (corpo1.split()[0] if corpo1.split() else ""))
    resto1 = sem_abertura(f1)
    mm = MENTAL_RE.search(resto1)
    if mm:
        E.append("Verbo mental ('%s'). Não se vê: descreva o que a criança faz." % mm.group(0))
    pe = PARTICIPA_ERRO_RE.search(resto1)
    if pe:
        E.append("Participação como evidência ('%s'). É interpretação: descreva a ação." % pe.group(0))
    else:
        pa = PARTICIPA_AVISO_RE.search(resto1)
        if pa:
            A.append("'%s' é interpretação. Confira se a linha diz o que a criança faz." % pa.group(0))
    confere_linha_comum(s1, corpo1, E, A, rot1, aula)

    # repete o Resultado?
    r_obs = raizes(resto1)
    for k, res in enumerate(aula.resultados, 1):
        r_res = raizes(res)
        if len(r_res) >= 3 and r_obs:
            taxa = len(r_res & r_obs) / float(len(r_res))
            if taxa >= 0.6:
                A.append("Observar pode estar repetindo o Resultado %d (%d%% das palavras): desça "
                         "um nível." % (k, round(taxa * 100)))

    if len(par) < 2:
        return

    # linha 2 · Documentar
    s2, rot2, tk2, comeca2, corpo2 = separa(par[1])
    item["linhas"].append(("Documentar", s2, n_car(s2)))
    v2 = confere_tokens(tk2, E, A)
    meio_icone = None
    if not tk2:
        E.append("Documentar sem ícone do meio no início (foto, video, audio, escrita, producao).")
    elif not comeca2:
        E.append("O ícone vem no início da linha Documentar, antes do verbo.")
    if v2:
        if v2[0] == "observar":
            E.append("A linha Documentar leva o ícone do meio, não <icone: observar>.")
        else:
            meio_icone = v2[0]
        meios_tk = [v for v in v2 if v != "observar"]
        if len(meios_tk) > 1:
            E.append("Dois ícones de meio na linha Documentar (%s). Um meio por par."
                     % ", ".join(meios_tk))
    if rot2 == "observar":
        E.append("A segunda linha é Documentar; a ordem está trocada.")
    aula.meio = meio_icone

    f2 = fold(corpo2)
    palavras = re.findall(r"[a-z0-9-]+", f2)
    meio_metodo = None
    if re.match(r"(registre|registrar|registra)\b", f2):
        E.append("'Registre' não diz o método. Use Anote, Fotografe, Grave o áudio, Filme ou Recolha.")
    elif f2.startswith(ABRE_MOMENTO):
        E.append("Documentar abre por um momento. Comece pelo método.")
    elif palavras and palavras[0] in METODO:
        meio_metodo, ambiguo = meio_da_palavra(palavras, 0)
        if ambiguo:
            A.append("'Grave' sem dizer áudio ou vídeo. Escreva 'Grave o áudio' ou 'Filme'.")
    else:
        E.append("Documentar abre com '%s'. Abra pelo método: Anote, Fotografe, Grave o áudio, "
                 "Filme ou Recolha." % (corpo2.split()[0] if corpo2.split() else ""))
    if meio_metodo and meio_icone and meio_metodo != meio_icone:
        E.append("Ícone <icone: %s>, mas o método é '%s' (%s). O ícone e o método dizem o mesmo meio."
                 % (meio_icone, corpo2.split()[0], NOME_MEIO[meio_metodo]))
    # mais de um metodo na mesma linha ('guarde' no meio da frase nao conta: guarde as fotos)
    metodos = []
    for i in range(len(palavras)):
        if palavras[i] in METODO and (i == 0 or palavras[i] != "guarde"):
            mi, _ = meio_da_palavra(palavras, i)
            metodos.append((i, palavras[i], mi))
    if meio_icone and not (metodos and metodos[0][0] == 0):
        metodos.insert(0, (0, "<icone: %s>" % meio_icone, meio_icone))
    difs = [(i, w, j, wj, mj) for (i, w, mi), (j, wj, mj) in zip(metodos, metodos[1:]) if mi != mj]
    alternativa = [d for d in difs if "ou" in palavras[d[0] + 1:d[2]]]
    if alternativa:
        E.append("Dois meios em alternativa ('%s ... ou %s'). Um meio por par."
                 % (alternativa[0][1], alternativa[0][3]))
    elif difs:
        A.append("Segundo registro na linha ('%s', %s). Confira se é uma só evidência; "
                 "um meio por par." % (difs[0][3], NOME_MEIO[difs[0][4]]))
    pe2 = PARTICIPA_ERRO_RE.search(f2)
    if pe2:
        E.append("Participação como evidência ('%s'). É interpretação: guarde a ação." % pe2.group(0))
    if EDUCADOR_RE.search(f2):
        A.append("Parece documentar o educador ('%s'). Guarde o que a criança faz."
                 % EDUCADOR_RE.search(f2).group(0))
    mm2 = MENTAL_RE.search(sem_abertura(f2))
    if mm2:
        E.append("Verbo mental na linha Documentar ('%s'). Guarde o que se vê ou ouve." % mm2.group(0))
    confere_linha_comum(s2, corpo2, E, A, rot2, aula)

    # marca no Momento
    marcas = [(num, tit) for num, tit, _ in aula.momentos if ICONE_RE.search(tit)]
    # a marca nunca muda o nome do Momento (termos-e-nomes, secao 6.1: grafia exata)
    nomes_aula = {}
    for num, tit, origem in aula.momentos:
        if origem == "aula" and not ICONE_RE.search(tit):
            nomes_aula[num] = " ".join(tit.split())
    for num, tit in marcas:
        nome_marca = " ".join(ICONE_RE.sub("", tit).split())
        if num in nomes_aula and unicodedata.normalize("NFC", nome_marca) != \
                unicodedata.normalize("NFC", nomes_aula[num]):
            E.append("A marca muda o nome do Momento %d ('%s' na aula, '%s' na marca). O nome "
                     "fica exatamente como está; só os ícones entram." % (num, nomes_aula[num], nome_marca))
    if marcas:
        icones_marca = []
        for num, tit in marcas:
            vm = confere_tokens([t.group(1) for t in ICONE_RE.finditer(tit)], E, A)
            icones_marca.extend(vm)
            texto_tit = ICONE_RE.sub("", tit).strip()
            t = n_car(tit)
            if t > LIMITE_TITULO:
                A.append("Título marcado do Momento %d com %d caracteres (limite %d, cada ícone "
                         "conta 1). Informe; não mude as palavras do título." % (num, t, LIMITE_TITULO))
            if not re.search(r"\s*(<\s*icone\s*:[^<>]+>\s*)+$", tit, re.I):
                A.append("No Momento %d, os ícones vêm depois das palavras do título." % num)
            if not texto_tit:
                E.append("Momento %d marcado sem título." % num)
        esperado = {"observar", meio_icone} - {None}
        estranhos = set(icones_marca) - esperado
        if estranhos:
            E.append("Marca no Momento com ícone que não está no par: %s."
                     % ", ".join(sorted(estranhos)))
        if "observar" not in icones_marca:
            A.append("A marca no Momento não traz <icone: observar>.")
        if meio_icone and meio_icone not in icones_marca:
            A.append("A marca no Momento não traz <icone: %s>." % meio_icone)
        obs_em = [num for num, tit in marcas if "observar" in [fold(x.group(1)).strip()
                                                               for x in ICONE_RE.finditer(tit)]]
        if len(obs_em) > 1:
            A.append("<icone: observar> em mais de um Momento (%s). Um par, uma lente, um Momento."
                     % ", ".join(str(x) for x in obs_em))

    # linhas a mais: nao entram no par, mas o PDF para se o icone for invalido
    for extra in par[2:]:
        sx, rotx, tkx, _, corpox = separa(extra)
        item["linhas"].append(("(a mais)", sx, n_car(sx)))
        confere_tokens(tkx, E, A)
        confere_linha_comum(sx, corpox, E, A, rotx, aula)

    # icones fora do lugar
    for txt in aula.outros:
        if ICONE_RE.search(str(txt)):
            A.append("Ícone fora da Documentação e dos títulos dos Momentos: '%s'."
                     % limpa_marcadores(str(txt))[:60])


# --------------------------------------------------------------------------------------------
# Semana
# --------------------------------------------------------------------------------------------
def distribuicao(aulas):
    por_semana = {}
    for a in aulas:
        m = CODIGO_RE.search(a.codigo or a.nome)
        semana = "Semana %s" % m.group(1) if m else "Sem código de semana"
        por_semana.setdefault(semana, []).append(a)
    saida = []
    for semana in sorted(por_semana, key=lambda s: (len(s), s)):
        lista = por_semana[semana]
        k = len(lista)
        cont = {m: [] for m in MEIOS}
        sem = []
        for a in lista:
            (cont[a.meio] if a.meio in cont else sem).append(a.codigo or a.nome)
        linha = "%s · %d aula%s: " % (semana, k, "" if k == 1 else "s") + " · ".join(
            "%s %d" % (NOME_MEIO[m], len(cont[m])) for m in MEIOS)
        if sem:
            linha += " · sem ícone %d" % len(sem)
        saida.append(linha)
        for m in MEIOS:
            if cont[m]:
                saida.append("    %s: %s" % (NOME_MEIO[m], ", ".join(cont[m])))
        avisos = []
        if k >= 4:
            for m in MEIOS:
                if len(cont[m]) >= 0.6 * k:
                    avisos.append("%s em %d de %d aulas. Cada meio guarda um tipo de evidência; "
                                  "concentrar num só deixa os outros sem registro."
                                  % (NOME_MEIO[m], len(cont[m]), k))
            if not cont["audio"] and not cont["escrita"]:
                avisos.append("Nenhuma aula guarda o que as crianças disseram (áudio ou escrita).")
            if not cont["foto"] and not cont["video"] and not cont["producao"]:
                avisos.append("Nenhuma aula guarda o que as crianças fizeram ou produziram "
                              "(foto, vídeo ou produção).")
        for av in avisos:
            saida.append("  AVISO %s" % av)
        if avisos:
            saida.append("  Sugira a aula mais fácil de mudar de meio sem mudar a lente.")
    return saida


# --------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Confere a Documentação Pedagógica e os ícones.")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--nivel", help='"Infantil 3", "Infantil 4", "Infantil 5" (ou 3, 4, 5)')
    a = ap.parse_args()

    nivel = None
    if a.nivel:
        m = re.search(r"([345])", a.nivel)
        if not m:
            print("Nível inválido: use Infantil 3, 4 ou 5.")
            return 2
        nivel = int(m.group(1))

    aulas = []
    for caminho in a.arquivos:
        if not os.path.exists(caminho):
            print("Arquivo não encontrado: %s" % caminho)
            return 2
        try:
            with open(caminho, encoding="utf-8-sig") as f:
                texto = f.read()
            if caminho.lower().endswith(".json"):
                aulas.extend(ler_json(caminho, json.loads(texto), nivel))
            else:
                aulas.extend(ler_md(caminho, texto, nivel))
        except (ValueError, KeyError, TypeError) as e:
            print("Não consegui ler %s: %s" % (caminho, e))
            return 2

    rel = Relatorio()
    for aula in aulas:
        item = rel.nova(aula.nome)
        confere_aula(aula, item)
        item["erros"] = list(dict.fromkeys(item["erros"]))
        item["avisos"] = list(dict.fromkeys(item["avisos"]))
        item["nivel"] = aula.nivel
        item["meio"] = aula.meio

    total_e = total_a = 0
    for item in rel.aulas:
        nv = " (Infantil %d)" % item["nivel"] if item["nivel"] else " (nível não informado)"
        print("== %s%s" % (item["titulo"], nv))
        for rotulo, texto, t in item["linhas"]:
            print("   %-10s %s  [%d car.]" % (rotulo, texto, t))
        if item["meio"]:
            print("   Meio:      %s" % NOME_MEIO[item["meio"]])
        for e in item["erros"]:
            print("   ERRO  %s" % e)
        for w in item["avisos"]:
            print("   AVISO %s" % w)
        if not item["erros"] and not item["avisos"]:
            print("   Nenhum problema mecânico.")
        print()
        total_e += len(item["erros"])
        total_a += len(item["avisos"])

    if len(aulas) >= 2:
        print("Distribuição dos meios de registro")
        for l in distribuicao(aulas):
            print("  " + l)
            if l.lstrip().startswith("AVISO"):
                total_a += 1
        print()

    print("%d aula%s · %d erro%s · %d aviso%s" % (
        len(aulas), "" if len(aulas) == 1 else "s", total_e, "" if total_e == 1 else "s",
        total_a, "" if total_a == 1 else "s"))
    if any(i["nivel"] is None for i in rel.aulas):
        print("Sem nível: os alertas de idade não rodaram. Use --nivel.")
    print("O script não julga se a lente é boa, se desce um nível abaixo do Resultado nem se o "
          "Momento é o melhor. Isso continua com você.")
    return 1 if total_e else 0


if __name__ == "__main__":
    sys.exit(main())
