#!/usr/bin/env python3
"""
verificar_oralidade.py - conferencia mecanica do que a skill de oralidade reescreve
(Educacao Infantil, Intercriativa Lab).

A skill so mexe nos Momentos da aula ou, nas entradas da Biblioteca, na secao de mediacao.
O script olha so esse texto. Dica, Documentacao e os outros campos ficam fora.

Confere:
  - Momentos (linhas "N | Nome" seguidas de itens "- "): informa nome acima de 30 caracteres e
    bloco acima de 600 caracteres de texto visivel (aviso: a skill nao corta; outra etapa
    ajusta o tamanho)
  - travessao, falas entre aspas
  - nomes de movimentos, "oracy" ou notas internas entre colchetes
  - padroes a evitar da secao 14 do documento de oralidade
  - excesso de perguntas ou de falas (aviso)

Nao julga se a conversa e boa. Isso fica com a lista da secao 17.

Uso:
  python3 verificar_oralidade.py aula_revisada.md
  python3 verificar_oralidade.py entrada.md --biblioteca
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import argparse, os, re, sys, unicodedata


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)")
MOVIMENTOS_PT = ["abrir", "construir junto", "esclarecer", "contrapor", "esticar", "supor",
                 "sugerir", "reconhecer"]
MOVIMENTOS_EN = ["instigate", "clarify", "speculate", "stretch", "encourage", "challenge",
                 "build", "suggest"]
# Em portugues varios nomes sao verbos comuns (Abrir, Sugerir): so o rotulo explicito conta.
ROTULO_RE = re.compile(r"\*\*\s*(%s)\s*\*\*|\bmovimento\s+(de\s+)?(%s)\b"
                       % ("|".join(MOVIMENTOS_PT), "|".join(MOVIMENTOS_PT)))
TERMOS_INTERNOS = ["oracy", "voice 21", "teacher talk tactics", "talk move"]
SECOES_BIBLIOTECA = ["observe e guie", "observe e amplie"]

# Padroes das secoes 10 e 14 do documento de oralidade: (padrao sem acento, mensagem, nivel)
PADROES = [
    (r"\*muito bem|muito bem\s*!", "Elogio generico (Muito bem!). Torne visivel a estrategia da crianca.", "erro"),
    (r"que lind[oa]", "Elogio generico (Que lindo!). Fale do processo ou da estrategia.", "erro"),
    (r"resposta perfeita", "Elogio generico (Resposta perfeita).", "erro"),
    (r"todas as criancas (devem )?(respond|compartilh|fal|diga|conte)",
     "Participacao forcada. Desenhe varias entradas na conversa (secao 10).", "erro"),
    (r"(peca|pedir) que todas", "Participacao forcada. Desenhe varias entradas na conversa (secao 10).", "erro"),
    (r"cada crianca", "Use a crianca ou as criancas, nunca cada crianca.", "erro"),
    (r"converse com as criancas", "Conversa generica. Nomeie a finalidade e como conduzir.", "aviso"),
    (r"faca perguntas", "Instrucao generica. Diga que pergunta e para que.", "aviso"),
    (r"promova uma roda", "Instrucao generica. Diga para que e como conduzir a conversa.", "aviso"),
    (r"roda de conversa", "Roda de conversa como padrao. Confira se o formato serve a finalidade (secao 6).", "aviso"),
    (r"quem sabe (por que|o que|qual)", "Adivinhar o que o educador pensa (secao 14).", "aviso"),
    (r"frases? complet", "Exigir frase completa contraria a secao 11.", "aviso"),
    (r"corrija a fala|corrija a crianca|corrija o que", "Corrigir a fala. Modele e amplie (secao 14).", "aviso"),
]
PROIBIDOS_VOZ = ["aluno", "aluna", "alunos", "alunas", "estudante", "estudantes", "educando",
                 "educandos"]


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, w, m):
        if (w, m) not in self.errors: self.errors.append((w, m))

    def warn(self, w, m):
        if (w, m) not in self.warnings: self.warnings.append((w, m))

    def show(self, alvo):
        print("Conferido: %s\n" % alvo)
        if self.errors:
            print("ERROS (%d)" % len(self.errors))
            for w, m in self.errors: print("  [%s] %s" % (w, m))
        if self.warnings:
            print("\nAVISOS (%d)" % len(self.warnings))
            for w, m in self.warnings: print("  [%s] %s" % (w, m))
        if not self.errors and not self.warnings:
            print("Nenhum problema mecanico encontrado.")
        print("\nO que este script NAO confere: se a conversa tem finalidade, se as perguntas "
              "abrem pensamento, se ha tempo real para pensar e se ha troca entre criancas. "
              "Confira a mao com a secao 17.")


def visivel(s):
    """Texto como aparece na pagina: link vira so o nome, marcacao sai."""
    s = LINK_RE.sub(r"\1", s)
    return re.sub(r"\*+", "", s).strip()


def _strip_md(t):
    return re.sub(r"\*+", "", t).strip().lstrip("#").strip()


def parse_momentos(text):
    """Momentos: linha 'N | Nome' (com ou sem negrito ou #) seguida de itens '- '."""
    momentos, cur = [], None
    for line in text.splitlines():
        t = line.strip()
        core = _strip_md(t)
        if re.match(r"^\d+\s*\|\s*.+", core):
            cur = [core, []]; momentos.append(cur); continue
        if re.match(r"^#{1,4}\s+\S", t) or re.match(r"^\*\*[^*]+\*\*\s*$", t):
            cur = None; continue
        if cur is not None:
            if t.startswith("- "):
                cur[1].append(t[2:].strip())
            elif t and cur[1] and line[:1] in (" ", "\t") and not t.startswith(">"):
                cur[1][-1] += " " + t  # continuacao recuada do item anterior
            elif t:
                cur = None  # outro bloco (Dica em citacao, paragrafo solto): o Momento acabou
    return momentos


def secoes_biblioteca(text):
    """Secoes de mediacao da entrada: '## 3 | Observe e guie...' e '## 5 | Observe e amplie...'."""
    out, cur = [], None
    for line in text.splitlines():
        h = re.match(r"^#{1,4}\s+(.+)$", line.strip())
        if h:
            titulo = _strip_md(h.group(1))
            cur = [titulo, []] if any(s in acc(titulo) for s in SECOES_BIBLIOTECA) else None
            if cur: out.append(cur)
            continue
        if cur is not None and line.strip():
            s = line.strip()
            cur[1].append(s[2:] if s.startswith("- ") else s)
    return out


def falas(s):
    """Falas em italico: trechos *...* que terminam em pontuacao (nomes de recurso nao contam)."""
    s = LINK_RE.sub(r"\1", s)
    s = re.sub(r"\*\*[^*]+\*\*", "", s)
    return [f for f in re.findall(r"(?<!\*)\*([^*]+)\*(?!\*)", s)
            if re.search(r"[?.!…]\s*$", f.strip())]


def check_linha(where, line, rep):
    flat = acc(line)
    if "—" in line or "–" in line:
        rep.error(where, "Travessao. A casa nao usa travessao.")
    if re.search(r"[\"“”][^\"“”]{3,}[\"“”]", line):
        rep.error(where, "Texto entre aspas. Fala do educador vai em italico, sem aspas.")
    sem_links = LINK_RE.sub(r"\1", line)
    for m in re.finditer(r"\[([^\]]+)\]", sem_links):
        inner = acc(m.group(1))
        if "biblioteca" in inner:
            continue
        if any(re.search(r"\b%s\b" % mv, inner) for mv in MOVIMENTOS_PT + MOVIMENTOS_EN):
            rep.error(where, "Nota interna com nomes de movimentos: [%s]" % m.group(1))
        else:
            rep.warn(where, "Texto entre colchetes: [%s]. Confira se e nota interna." % m.group(1))
    for termo in TERMOS_INTERNOS:
        if termo in flat:
            rep.error(where, "Termo interno (\"%s\"). Na casa, o termo e oralidade." % termo)
    for mv in MOVIMENTOS_EN:
        if re.search(r"\b%s\b" % mv, acc(sem_links)):
            rep.warn(where, "Palavra em ingles \"%s\". Se e nome de movimento, tire da pagina." % mv)
    if ROTULO_RE.search(flat):
        rep.error(where, "Nome de movimento como rotulo. Vire instrucao no imperativo.")
    for w in PROIBIDOS_VOZ:
        if re.search(r"\b%s\b" % w, flat):
            rep.error(where, "Use crianca(s), nunca '%s'." % w); break
    if re.search(r"\b(professor|professora|tia)\b", flat):
        rep.warn(where, "Prefira educador a professor ou tia.")
    for pat, msg, nivel in PADROES:
        if re.search(pat, flat):
            (rep.error if nivel == "erro" else rep.warn)(where, msg)


def check_blocos(blocos, rep, limite):
    for titulo, itens in blocos:
        for k, item in enumerate(itens, 1):
            where = "%s, item %d" % (titulo, k)
            check_linha(where, item, rep)
            if item.count("?") >= 3:
                rep.warn(where, "%d perguntas num item so. Confira se virou lista de perguntas (secao 14)."
                         % item.count("?"))
        if limite:
            nome = re.sub(r"^\d+\s*\|\s*", "", titulo).strip()
            if len(nome) > 30:
                rep.warn(titulo, "Nome com %d caracteres (pagina: max 30). Nao corte; leve para as decisoes em aberto." % len(nome))
            n = sum(len(visivel(i)) for i in itens)
            if n > 600:
                rep.warn(titulo, "Bloco com %d caracteres visiveis (pagina: max 600). Nao corte; "
                         "informe a contagem nas decisoes em aberto." % n)
        nf = len(falas(" ".join(itens)))
        if nf > (5 if limite else 8):  # a entrada da Biblioteca e mais longa que um Momento
            rep.warn(titulo, "%d falas do educador. O padrao e 1 ou 2 por movimento, poucas por bloco." % nf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--biblioteca", action="store_true",
                    help="entrada da Biblioteca: confere so as secoes de mediacao, sem limite de 600")
    a = ap.parse_args()
    if not os.path.exists(a.file):
        sys.exit("Arquivo nao encontrado: %s" % a.file)
    text = open(a.file, encoding="utf-8").read()
    rep = Report()
    if a.biblioteca:
        blocos = secoes_biblioteca(text)
        alvo = "secoes de mediacao da entrada (%d)" % len(blocos)
        if not blocos:
            rep.error("entrada", "Nao achei a secao 3 | Observe e guie a brincadeira nem a "
                      "5 | Observe e amplie a investigacao.")
        check_blocos(blocos, rep, limite=False)
    else:
        blocos = parse_momentos(text)
        alvo = "Momentos da aula (%d)" % len(blocos)
        if not blocos:
            rep.error("aula", "Nao achei Momentos no formato 'N | Nome' seguidos de itens '- '.")
        check_blocos(blocos, rep, limite=True)
    rep.show(alvo)
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
