#!/usr/bin/env python3
"""verificar_dica.py · conferência mecânica da Dica (Educação Infantil, termos v8 · templates v2).

Formato (templates-de-aula.md, seção 2):
    Se a criança precisar de apoio para [ação de aprendizagem observável]: [andaime].
    Para aprofundar o desafio: [ampliação].
Duas linhas, sem negrito, até 300 caracteres no total. A segunda linha é opcional. Passar de 300
é aviso, não erro: só a edição final (editor-infantil-orientacoes-do-educador) corta para caber.

Uso:
    python3 verificar_dica.py dicas.md

Um arquivo pode ter várias Dicas (as quatro aulas de um dia): separe cada uma com um título de
markdown, por exemplo "#### S1.D1.A2 · Dica". Títulos, linhas em branco, blocos de código e
linhas de citação (>) são ignorados.

Sai com código 1 se houver erro. Avisos sozinhos saem 0. O script não julga se a Dica é boa
(se a ação é a certa, se respeita o modo e a idade): isso continua com a pessoa.
"""
import re
import sys
import unicodedata

ABERTURA_APOIO = "Se a criança precisar de apoio para "
ABERTURA_AMPLIACAO = "Para aprofundar o desafio:"
LIMITE = 300
GRAFIA_FIXA_TRAVESSAO = "Eu Faço – Nós Fazemos – Você Faz"


def plano(t):
    """Minúsculas e sem acento, para comparar."""
    t = unicodedata.normalize("NFD", t)
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower()


def visivel(linha):
    """Texto como aparece na página: sem marcas de itálico ou negrito."""
    return re.sub(r"[*_]", "", linha).strip()


# ---------------------------------------------------------------------------
# Listas (comparadas sobre o texto sem acento e em minúsculas)
# ---------------------------------------------------------------------------

ROTULOS = [
    r"se as criancas estiverem com dificuldade",
    r"para quem tem (mais )?dificuldade",
    r"para quem (esta|estiver) confiante",
    r"quem tem mais facilidade",
    r"\bcriancas? (mais )?(timid|agitad|atrasad|adiantad|avancad|confiant|lent[ao]s?\b|rapid"
    r"|novas?\b|velhas?\b|pequen)\w*",
    r"\bcriancas? com (mais )?(dificuldade|facilidade)",
    r"\bcriancas? que (ainda )?nao (sabe|sabem|consegue|conseguem|fala|falam)\b",
    r"\bpara as (mais )?(novas|velhas|timidas|avancadas|rapidas|lentas)\b",
]

ENCHIMENTOS = [
    r"\bfaca mais uma?\b",
    r"\bfaca outr[oa]\b",
    r"\batividade extra\b",
    r"\btarefa extra\b",
    r"\bfolha extra\b",
    r"\bquem terminar\b",
]

TERMOS_PROIBIDOS = [
    (r"\balun[oa]s?\b", "aluno (use a criança, as crianças)"),
    (r"\bestudantes?\b", "estudante (use a criança, as crianças)"),
    (r"\beducand[oa]s?\b", "educando (use a criança, as crianças)"),
    (r"\bcada crianca\b", "cada criança (use a criança, as crianças)"),
    (r"\bprofessor(a|es|as)?\b", "professor (use educador)"),
    (r"\bdocentes?\b", "docente (use educador)"),
]

# Estratégias de conversa: na família, oralidade fica só nos Momentos.
CONVERSA = [
    r"\bparceir[oa]s?\b",
    r"\bem (duplas?|trios?)\b",
    r"\bconvers\w*",
    r"\b(conte|diga|fale|explique)m? (primeiro )?(ao|a|para o|para a|para um|para uma|com o|com a|"
    r"com um|com uma) (colega|amig[oa]|parceir[oa])",
    r"\bconte(m)? primeiro\b",
    r"\bfale(m)? primeiro\b",
    r"\btroque(m)? ideias\b",
    r"\bcompartilhe(m)? com\b",
    r"\broda de conversa\b",
    r"\bretom\w* (a|as) falas?\b",
    r"\bvire(m)? e (converse|conte|fale)",
    r"\bturn and talk\b",
    r"\btempo para pensar\b",
    r"\boralidade\b",
]

# Conteúdo que tem outro campo como casa.
OUTRO_CAMPO = [
    (r"\bregistre\b|\bfotografe\b|\bfilme\b|\bdocumente\b|\bobserve se\b",
     "parece Documentação Pedagógica (editor-infantil-observar-documentar-icones)"),
    (r"\bprepare\b|\bsepare os materiais\b|\bantes da aula\b",
     "parece Materiais e Preparação (skill do tipo de aula)"),
    (r"\bna proxima aula\b|\bno proximo dia\b",
     "parece Orientações do Dia (o que vem depois)"),
    (r"\bcuidado com\b|\bseguranca\b",
     "segurança não entra na Dica"),
]

NUMERO_POR_EXTENSO = r"\b(dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez)\b"

MARCO_NA_PAGINA = [
    r"\b\d+\s*anos\b",
    r"\bja deve\b",
    r"\bdeveria\b",
    r"\besperado para a idade\b",
    r"\bpara a idade\b",
]

VERBOS_NAO_OBSERVAVEIS = {
    "entender", "compreender", "aprender", "saber", "conhecer", "prestar", "concentrar",
    "comportar", "participar", "interessar", "gostar",
}

ARTIGOS = {"a", "o", "as", "os", "um", "uma", "uns", "umas"}


def eh_infinitivo(palavra):
    p = plano(palavra).split("-")[0]
    return bool(re.fullmatch(r"[a-z]+(ar|er|ir|or)", p)) or p == "por"


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------

def blocos(texto):
    """Separa as Dicas pelos títulos (#). Devolve [(titulo, [linhas])]."""
    saida, titulo, linhas, cerca = [], None, [], False
    for bruta in texto.splitlines():
        s = bruta.strip()
        if s.startswith("```"):
            cerca = not cerca
            continue
        if cerca:
            continue
        if s.startswith("#"):
            if titulo is not None or linhas:
                saida.append((titulo, linhas))
            titulo, linhas = s.lstrip("#").strip(), []
            continue
        if not s or s.startswith(">"):
            continue
        linhas.append(s)
    if titulo is not None or linhas:
        saida.append((titulo, linhas))
    return saida


# ---------------------------------------------------------------------------
# Conferência de uma Dica
# ---------------------------------------------------------------------------

def conferir(linhas):
    erros, avisos, notas = [], [], []

    # Rótulo do campo colado como linha ("Dica" ou "Dica:").
    if linhas and re.fullmatch(r"\**dica:?\**", plano(linhas[0])):
        avisos.append("A linha \"Dica\" é o nome do campo, não faz parte do texto. Ignorada.")
        linhas = linhas[1:]

    if not linhas:
        erros.append("Dica vazia.")
        return erros, avisos, notas, 0

    # Marcadores de lista.
    limpas, marcadas = [], 0
    for ln in linhas:
        if re.match(r"^([-*+]|\d+[.)])\s+", ln):
            marcadas += 1
            ln = re.sub(r"^([-*+]|\d+[.)])\s+", "", ln)
        limpas.append(ln)
    linhas = limpas
    if marcadas:
        avisos.append("Linha com marcador de lista. A Dica são linhas de texto, não itens.")

    if len(linhas) > 2:
        erros.append(f"{len(linhas)} linhas. A Dica tem no máximo 2 (apoio e ampliação), cada uma "
                     "numa linha só, sem quebra no meio.")

    if any("**" in ln or "__" in ln for ln in linhas):
        erros.append("Negrito encontrado. A Dica fica sem negrito (templates v2, seção 2).")

    # --- Aberturas em itálico -----------------------------------------------
    if any(re.match(r"^(\*[^*]|_[^_])", ln) for ln in linhas[:2]):
        avisos.append("Abertura em itálico. O itálico fica para a fala do educador e para nomes "
                      "de recursos; as aberturas ficam em texto normal.")

    # --- Quem é apoio, quem é ampliação -------------------------------------
    l1 = visivel(linhas[0])
    l2 = visivel(linhas[1]) if len(linhas) >= 2 else None
    p1 = plano(l1)
    apoio, ampliacao = l1, l2
    if p1.startswith("para aprofundar o desafio"):
        if l2 is not None and plano(l2).startswith("se a crianca precisar de apoio"):
            erros.append("Ordem invertida: a linha de apoio vem primeiro, a de ampliação depois.")
            apoio, ampliacao = l2, l1
        elif l2 is None:
            erros.append("Falta a linha de apoio. Sem ela a Dica não existe; a ampliação é que é "
                         "opcional.")
            apoio, ampliacao = None, l1

    if apoio is not None:
        conferir_apoio(apoio, erros, avisos)
    if ampliacao is not None:
        conferir_ampliacao(ampliacao, erros, avisos)
    elif apoio is not None:
        notas.append("Só a linha de apoio. Certo quando a ampliação não agrega complexidade real "
                     "(brincar dirigido pela criança que já se sustenta).")

    # --- Tamanho ------------------------------------------------------------
    total = sum(len(visivel(ln)) for ln in linhas[:2])
    if total > LIMITE:
        avisos.append(f"{total} caracteres; a caixa da Dica tem {LIMITE}. Ao escrever, mire em {LIMITE}. "
                      "Se a Dica é do autor e está certa, não corte: leve a contagem para as "
                      "Decisões em aberto (só a edição final corta).")

    # --- Texto inteiro ------------------------------------------------------
    texto = " ".join(visivel(ln) for ln in linhas)
    flat = plano(texto)
    sem_grafia_fixa = texto.replace(GRAFIA_FIXA_TRAVESSAO, "")
    if "\u2014" in sem_grafia_fixa or re.search(r"\s[\u2013-]{1,2}\s", sem_grafia_fixa):
        erros.append("Travessão encontrado. Reescreva sem travessão (exceções: citação de fala de "
                     "um livro e a grafia fixa Eu Faço – Nós Fazemos – Você Faz).")
    if re.search(r"[\"\u201c\u201d\u00ab\u00bb]", texto):
        erros.append("Aspas encontradas. Fala do educador vai em itálico, sem aspas.")
    for padrao, rotulo in TERMOS_PROIBIDOS:
        if re.search(padrao, flat):
            erros.append(f"Termo proibido: {rotulo}.")
    if re.search(r"\btias?\b", flat):
        avisos.append("\"tia\": se for o educador, escreva educador.")
    for padrao in ROTULOS:
        m = re.search(padrao, flat)
        if m:
            erros.append(f"Rótulo de criança: \"{trecho(texto, flat, m)}\". Parta de uma ação de aprendizagem "
                         "observável, nunca de um tipo de criança.")
    for padrao in ENCHIMENTOS:
        m = re.search(padrao, flat)
        if m:
            erros.append(f"Ampliação vazia: \"{trecho(texto, flat, m)}\". Aprofunde a mesma aprendizagem em vez "
                         "de pedir mais quantidade.")
    achados = []
    for padrao in CONVERSA:
        for m in re.finditer(padrao, flat):
            t = trecho(texto, flat, m)
            if any(t in a for a in achados):
                continue
            achados = [a for a in achados if a not in t] + [t]
    if achados:
        lista = ", ".join(f"\"{a}\"" for a in achados)
        avisos.append(f"Possível estratégia de conversa: {lista}. Na Dica, apoio e ampliação "
                      "mexem na ação de aprendizagem; conversa fica nos Momentos "
                      "(editor-infantil-estilo-de-casa).")
    for padrao, casa in OUTRO_CAMPO:
        m = re.search(padrao, flat)
        if m:
            avisos.append(f"\"{trecho(texto, flat, m)}\" {casa}. Confira se é mesmo apoio ou ampliação.")
    m = re.search(NUMERO_POR_EXTENSO, flat)
    if m:
        avisos.append(f"Número por extenso: \"{trecho(texto, flat, m)}\". Na página, números em algarismo.")
    for padrao in MARCO_NA_PAGINA:
        m = re.search(padrao, flat)
        if m:
            avisos.append(f"\"{trecho(texto, flat, m)}\": os marcos de idade não vão para a página como "
                          "expectativa.")
            break

    return erros, avisos, notas, total


def conferir_apoio(linha, erros, avisos):
    """Confere a linha de apoio (texto já sem marcas de itálico)."""
    p = plano(linha)
    if p.startswith(plano(ABERTURA_APOIO)):
        if not linha.startswith(ABERTURA_APOIO):
            erros.append("Abertura da linha de apoio fora da grafia exata. Escreva: "
                         f"\"{ABERTURA_APOIO.strip()}\" (S maiúsculo, acento em criança).")
        resto = linha[len(ABERTURA_APOIO):]
        if ":" not in resto:
            erros.append("Linha de apoio sem dois-pontos depois da ação: \"Se a criança precisar "
                         "de apoio para [ação]: [andaime].\"")
        else:
            acao, andaime = (s.strip() for s in resto.split(":", 1))
            if acao:
                conferir_acao(acao, avisos)
            else:
                erros.append("Falta a ação de aprendizagem depois de \"apoio para\".")
            if not andaime:
                erros.append("Falta o andaime depois dos dois-pontos na linha de apoio.")
    elif "precisar de apoio para" in p:
        erros.append(f"A linha de apoio deve começar com \"{ABERTURA_APOIO.strip()}\".")
    else:
        erros.append(f"A primeira linha deve começar com \"{ABERTURA_APOIO.strip()}\" seguida "
                     "de uma ação de aprendizagem observável.")
    if not linha.rstrip().endswith((".", "?", "!")):
        avisos.append("A linha de apoio não termina com ponto.")


def conferir_ampliacao(linha, erros, avisos):
    """Confere a linha de ampliação (texto já sem marcas de itálico)."""
    p = plano(linha)
    if linha.startswith(ABERTURA_AMPLIACAO):
        if not linha[len(ABERTURA_AMPLIACAO):].strip():
            erros.append("Falta a ampliação depois de \"Para aprofundar o desafio:\".")
    elif p.startswith("para ampliar o desafio"):
        erros.append("Abertura antiga \"Para ampliar o desafio:\". Use \"Para aprofundar o "
                     "desafio:\".")
    elif p.startswith("nao force uma ampliacao"):
        erros.append("\"Não force uma ampliação\" saiu do formato. Sem ampliação, deixe só a "
                     "linha de apoio.")
    elif p.startswith("outra opcao"):
        erros.append("\"Outra opção:\" saiu do formato. Use uma linha de apoio e, se couber, "
                     "\"Para aprofundar o desafio:\".")
    elif p.startswith(plano(ABERTURA_AMPLIACAO)):
        erros.append(f"Abertura da ampliação fora da grafia exata. Escreva: "
                     f"\"{ABERTURA_AMPLIACAO}\".")
    elif p.startswith("para aprofundar o desafio"):
        erros.append("Faltam os dois-pontos depois de \"Para aprofundar o desafio\".")
    elif p.startswith("se a crianca precisar de apoio"):
        erros.append("Duas linhas de apoio. A segunda linha é a ampliação, ou não existe.")
    else:
        erros.append(f"A segunda linha deve começar com \"{ABERTURA_AMPLIACAO}\".")
    if not linha.rstrip().endswith((".", "?", "!")):
        avisos.append("A linha de ampliação não termina com ponto.")


def trecho(texto, flat, m):
    """Mostra o trecho encontrado com os acentos do original, quando possível."""
    if len(texto) == len(flat):
        return texto[m.start():m.end()]
    return m.group(0)


def conferir_acao(acao, avisos):
    palavras = acao.split()
    primeira = palavras[0]
    if plano(primeira) == "se" and len(palavras) > 1:  # "se juntar à brincadeira"
        primeira = palavras[1]
    pp = plano(primeira).split("-")[0]
    if pp in ARTIGOS or not eh_infinitivo(primeira):
        avisos.append(f"A ação \"{acao}\" não começa por verbo no infinitivo. Escreva o que a "
                      "criança faz: comparar, encaixar, registrar, escolher...")
    elif pp in VERBOS_NAO_OBSERVAVEIS:
        avisos.append(f"\"{primeira}\" não dá para observar. Escreva o que a criança faz quando "
                      "consegue (apontar, separar, contar, desenhar...).")


# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 verificar_dica.py <arquivo.md>")
        sys.exit(2)
    try:
        texto = open(sys.argv[1], encoding="utf-8").read()
    except OSError as e:
        print(f"Não foi possível ler o arquivo: {e}")
        sys.exit(2)

    lista = blocos(texto)
    if not lista:
        print("Nenhuma Dica encontrada no arquivo.")
        sys.exit(1)

    n_erros = n_avisos = 0
    for i, (titulo, linhas) in enumerate(lista, 1):
        nome = titulo or f"Dica {i}"
        erros, avisos, notas, total = conferir(linhas)
        n_erros += len(erros)
        n_avisos += len(avisos)
        print(f"== {nome} ==")
        print(f"   {total}/{LIMITE} caracteres")
        for e in erros:
            print(f"   ERRO  {e}")
        for a in avisos:
            print(f"   Aviso {a}")
        for n in notas:
            print(f"   Nota  {n}")
        if not erros and not avisos:
            print("   OK")
        print()

    print(f"Resultado: {len(lista)} Dica(s), {n_erros} erro(s), {n_avisos} aviso(s).")
    sys.exit(1 if n_erros else 0)


if __name__ == "__main__":
    main()
