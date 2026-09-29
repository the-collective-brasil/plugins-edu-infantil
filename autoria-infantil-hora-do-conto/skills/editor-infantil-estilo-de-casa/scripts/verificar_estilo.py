#!/usr/bin/env python3
"""
verificar_estilo.py - conferencia mecanica da linguagem de uma aula (Educacao Infantil,
Intercriativa Lab), segundo o Estilo da Casa e termos-e-nomes v7.

Confere: travessao (fora das excecoes), fala entre aspas, termos proibidos, numeros por extenso
comuns, exclamacao, verbos proibidos e vagos, topico so com pergunta ou fala.
Nao julga tom nem calor. Nao confere tamanho (isso e da orientacoes-do-educador).

Uso:
  python3 verificar_estilo.py aula.md
Sai com codigo 1 se houver erro. Avisos sozinhos saem 0.
"""
import os, re, sys, unicodedata


def acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower()


CODELINE_RE = re.compile(r"^\s*-\s*\*\*EI0[2-5][A-Z]{2,3}\d{2}\*\*")
PROIBIDOS = {"aluno": "crianca", "aluna": "crianca", "alunos": "criancas", "alunas": "criancas",
             "estudante": "crianca", "estudantes": "criancas", "educando": "crianca",
             "educandos": "criancas", "professor": "educador", "professora": "educador",
             "tia": "educador"}
VERBOS_PROIBIDOS = ["mande", "exija", "corrija", "diga a eles", "obrigue", "faca com que"]
VERBOS_VAGOS = ["facilite", "facilitar", "desenvolva", "promova", "promover", "engaje", "engajar",
                "desperte a consciencia", "aprofunde a compreensao", "crie espaco para",
                "criar espaco para", "apoie a construcao de sentido"]
EXTENSO = ["dois", "duas", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez"]
EXCECAO_TRAVESSAO = "eu faco – nos fazemos – voce faz"


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 verificar_estilo.py aula.md")
    if not os.path.exists(sys.argv[1]):
        sys.exit("Arquivo nao encontrado: %s" % sys.argv[1])
    erros, avisos = [], []
    for i, line in enumerate(open(sys.argv[1], encoding="utf-8").read().splitlines(), 1):
        if CODELINE_RE.match(line):
            continue
        w = "linha %d" % i
        flat = acc(line)
        sem_excecao = flat.replace(EXCECAO_TRAVESSAO, "")
        if "—" in sem_excecao or "–" in sem_excecao:
            avisos.append("%s: travessao. So vale citando fala de um livro." % w)
        if re.search(r"[\"“”][^\"“”]{3,}[\"“”]", line):
            erros.append("%s: texto entre aspas. Fala do educador vai em italico, sem aspas." % w)
        for p, certo in PROIBIDOS.items():
            if re.search(r"\b%s\b" % p, flat):
                erros.append("%s: '%s' -> use %s." % (w, p, certo)); break
        if "cada crianca" in flat:
            erros.append("%s: 'cada crianca' -> use a crianca ou as criancas." % w)
        for v in VERBOS_PROIBIDOS:
            if re.search(r"\b%s\b" % v, flat):
                erros.append("%s: verbo proibido (%s). Use verbo facilitador." % (w, v))
        for v in VERBOS_VAGOS:
            if re.search(r"\b%s\b" % v, flat):
                avisos.append("%s: verbo vago (%s). Troque por acao concreta." % (w, v))
        if "!" in line:
            avisos.append("%s: exclamacao. A casa nao usa exclamacao." % w)
        for n in EXTENSO:
            if re.search(r"\b%s\b" % n, flat) and not re.search(r"\*[^*]*\b%s\b[^*]*\*" % n, flat):
                avisos.append("%s: numero por extenso (%s)? Use algarismo, salvo em fala ou nome." % (w, n)); break
        t = line.strip()
        if t.startswith("- "):
            # teste final do guia: tire a pergunta ou a fala; sobra acao concreta do educador?
            resto = re.sub(r"\*[^*]+\*", "", t[2:])
            resto = re.sub(r"(?i)\b(pergunte|diga|modele)\s*:", "", resto)
            resto = re.sub(r"[;:.,?\s\"“”]+", " ", resto).strip()
            if len(resto.split()) < 3:
                erros.append("%s: topico so com pergunta ou fala. Junte a acao do educador." % w)
            elif re.match(r"^-\s*(pergunte|diga|modele)\s*:", flat.strip()):
                avisos.append("%s: topico comeca por Pergunte/Diga/Modele. Comece pela acao." % w)
            seq = re.findall(r"(?:^|[.;,]\s*)(depois|em seguida|por fim|logo apos|entao)\b", acc(t[2:]))
            if seq:
                avisos.append("%s: '%s' dentro do topico. Pela regra dos 4 gatilhos, pode faltar um corte "
                              "(objeto, foco, espaco ou fala)." % (w, seq[0]))
    if erros:
        print("ERROS (%d)" % len(erros)); [print("  " + e) for e in erros]
    if avisos:
        print("\nAVISOS (%d)" % len(avisos)); [print("  " + a) for a in avisos]
    if not erros and not avisos:
        print("Nenhum problema mecanico encontrado.")
    print("\nO script nao julga tom nem calor. Leia a aula inteira.")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
