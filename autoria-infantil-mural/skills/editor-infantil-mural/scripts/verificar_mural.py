#!/usr/bin/env python3
"""
verificar_mural.py - conferencia mecanica de uma aula de Mural do Projeto (Educacao Infantil,
Intercriativa Lab), pelos tipos de termos-e-nomes secao 6.2.

Confere:
  - o tipo de Mural pelo codigo S#.D#.A4 (e que a aula e A4)
  - os 4 Momentos, na ordem, com os nomes do tipo
  - Peca da Fase e Marco quando alocados; adesivo so com o Marco
  - Conexao Casa-Escola no Momento 4 dos Murais de D5 (Fechamento e Construcao do Marco)
  - pagina Registro da Semana no D4
  - marcadores sem explicacao ("Foco Semanal"), modo de brincar, travessao, aspas, termos

Uso:
  python3 verificar_mural.py aula.md [--codigo S3.D2.A4]
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import argparse, os, re, sys, unicodedata

FIXO_1, FIXO_2, FIXO_4 = "Relembrar e Compartilhar", "Conectar Ideias e Vivências", "Organizar e Encerrar"
PECAS = {(3, 2): "Cartões de Entrevista", (7, 2): "Convite do Teste", (10, 2): "Convite da Apresentação",
         (2, 5): "Persona Cards", (6, 5): "Etiquetas e Placas do Protótipo"}
MARCOS = {2: "Perguntas que Precisamos Responder", 4: "Painel de Evidências", 6: "Protótipo",
          9: "Produto Final", 11: "Apresentação Final"}
LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)")


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


def tipo_do_mural(s, d):
    """Devolve (tipo, [4 nomes]) ou (None, motivo)."""
    if s == 12 and d == 5:
        return "Encerramento da Jornada", [FIXO_1, "Revisitar a Jornada", "Refletir e Celebrar", FIXO_4]
    if d == 1:
        if s == 1:
            return "Abertura do Projeto", [FIXO_1, FIXO_2, "Conhecer o Mural e a Jornada", FIXO_4]
        if s in (3, 5, 7, 10, 12):
            return "Abertura de Fase", [FIXO_1, FIXO_2, "Abrir a Nova Fase", FIXO_4]
        return "Abertura da Semana", [FIXO_1, FIXO_2, "Revisitar o Mural do Projeto", FIXO_4]
    if s == 12:
        return None, "S12 · D%d.A4 segue o plano proprio da semana 12, nao a tabela de tipos (termos 6.2)." % d
    if d in (2, 3):
        return "Desenvolvimento", [FIXO_1, FIXO_2, "Revisitar o Mural do Projeto", FIXO_4]
    if d == 4:
        return "Registro da Semana", [FIXO_1, FIXO_2, "Criar o Registro da Semana", FIXO_4]
    if s in (2, 4, 6, 9, 11):
        return "Construção do Marco e Conexão Casa-Escola", [FIXO_1, FIXO_2, "Construir o Marco da Fase", FIXO_4]
    return "Fechamento da Semana e Conexão Casa-Escola", [FIXO_1, FIXO_2, "Registrar no Canvas", FIXO_4]


def momentos(text):
    out, cur = [], None
    for line in text.splitlines():
        t = line.strip()
        core = re.sub(r"\*+", "", t).lstrip("#").strip()
        m = re.match(r"^(\d+)\s*\|\s*(.+)$", core)
        if m:
            cur = [int(m.group(1)), m.group(2).strip(), []]; out.append(cur); continue
        if re.match(r"^#{1,4}\s+\S", t) or re.match(r"^\*\*[^*]+\*\*\s*$", t):
            cur = None; continue
        if cur is not None:
            if t.startswith("- "):
                cur[2].append(t[2:].strip())
            elif t and cur[2] and line[:1] in (" ", "\t"):
                cur[2][-1] += " " + t
            elif t:
                cur = None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--codigo")
    a = ap.parse_args()
    if not os.path.exists(a.arquivo):
        sys.exit("Arquivo nao encontrado: %s" % a.arquivo)
    text = open(a.arquivo, encoding="utf-8").read()
    flat = acc(text)
    erros, avisos = [], []

    cod = a.codigo or (re.search(r"\bS\d{1,2}\.D\d\.A\d\b", text) or [None])[0]
    if not cod:
        sys.exit("Codigo da aula ausente. Use --codigo S#.D#.A4.")
    s, d, aula = map(int, re.match(r"S(\d+)\.D(\d)\.A(\d)", cod.upper()).groups())
    if aula != 4:
        erros.append("%s: o Mural do Projeto e sempre A4." % cod)
    tipo, esperado = tipo_do_mural(s, d)
    if tipo is None:
        erros.append(esperado)
        esperado = None
    else:
        print("Tipo de Mural: %s (%s)" % (tipo, cod))

    ms = momentos(text)
    nomes = [n for _, n, _ in ms]
    if esperado:
        if len(ms) != 4 or [acc(n) for n in nomes] != [acc(x) for x in esperado]:
            erros.append("Momentos esperados: %s. Encontrados: %s."
                         % (" · ".join(esperado), " · ".join(nomes) or "nenhum"))
    for num, nome, itens in ms:
        if len(nome) > 30:
            avisos.append("Momento %d: nome com %d caracteres (max 30)." % (num, len(nome)))
        if sum(len(re.sub(r"\*+", "", LINK_RE.sub(r"\1", i))) for i in itens) > 600:
            avisos.append("Momento %d acima de 600 caracteres (a orientacoes-do-educador ajusta)." % num)
    m3 = acc(" ".join(ms[2][2])) if len(ms) >= 3 else ""
    m4 = acc(" ".join(ms[3][2])) if len(ms) >= 4 else ""

    if (s, d) in PECAS and acc(PECAS[(s, d)]) not in flat:
        erros.append("Peca da Fase alocada nesta aula ausente: %s." % PECAS[(s, d)])
    if tipo and tipo.startswith("Construção do Marco"):
        if s in MARCOS and acc(MARCOS[s]) not in flat:
            erros.append("Construcao do Marco sem o nome do Marco da semana: %s." % MARCOS[s])
        for k, msg in [("canvas", "registro no Canvas do Projeto"), ("pagina de marco", "Pagina de Marco"),
                       ("jornada", "atualizacao da Jornada do Projeto"), ("adesivo", "adesivo do Marco")]:
            if k not in m3:
                erros.append("Construcao do Marco: falta %s no Momento 3." % msg)
    elif "adesivo" in flat and tipo not in ("Abertura de Fase", "Abertura do Projeto", "Encerramento da Jornada"):
        avisos.append("Adesivo fora da Construcao do Marco ou da Abertura de Fase: confira.")
    if tipo and "Conexão Casa-Escola" in tipo and "conexao casa-escola" not in m4:
        erros.append("%s: a Conexao Casa-Escola vai no Momento 4." % tipo)
    if tipo == "Registro da Semana" and "registro da semana" not in m3:
        erros.append("Registro da Semana: o Momento 3 usa a pagina destacavel Registro da Semana.")
    if tipo == "Fechamento da Semana e Conexão Casa-Escola" and "canvas" not in m3:
        erros.append("Fechamento da Semana: o Momento 3 registra no Canvas do Projeto.")

    if "foco semanal" in flat:
        avisos.append("'Foco Semanal' na aula: diga o que as criancas vao investigar.")
    if re.search(r"modo de brincar\s*:", flat):
        erros.append("O Mural nao tem Modo de Brincar.")
    for i, line in enumerate(text.splitlines(), 1):
        if "—" in line or "–" in line:
            erros.append("linha %d: travessao." % i)
        if re.search(r"[\"“”][^\"“”]{3,}[\"“”]", line):
            erros.append("linha %d: texto entre aspas; fala do educador em italico, sem aspas." % i)
        if re.search(r"\b(aluno|alunos|estudante|estudantes|professor|professora)\b", acc(line)):
            erros.append("linha %d: use crianca(s) ou educador." % i)

    if erros:
        print("ERROS (%d)" % len(erros)); [print("  " + e) for e in erros]
    if avisos:
        print("\nAVISOS (%d)" % len(avisos)); [print("  " + x) for x in avisos]
    if not erros and not avisos:
        print("Nenhum problema mecanico encontrado.")
    print("\nO script nao julga se a evidencia e boa nem se o Momento 3 diz o bastante. Confira a mao.")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
