#!/usr/bin/env python3
"""Conferência mecânica de uma aula de Hora do Conto (Educação Infantil, Intercriativa Lab).

Confere os 4 Momentos fixos (templates-de-aula.md, seção 3), Lançamento do Projeto só em
S1.D1.A1, nomes de Momento aposentados, Rotina de Abertura e Rotina de Encerramento no lugar
(seção 4), PEER em leitura dialógica, travessão (inclusive -- e ---), falas entre aspas, termos
aposentados e pessoas fora do vocabulário (termos-e-nomes.md, seção 8), Momentos acima de 600 e
Materiais e Preparação acima de 270 (avisos; o marcador [código biblioteca] não conta).

Uso:
  python3 verificar_aula.py aula.md --codigo S3.D4.A1
  python3 verificar_aula.py --self-test
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path


LANCAMENTO = (
    "Lançamento do Projeto",
    "Preparar para a Leitura",
    "Ler e Explorar",
    "Conversar e Compartilhar",
)

GERAL = (
    "Preparar para a Leitura",
    "Ler e Explorar",
    "Conversar e Compartilhar",
    "Organizar e Encerrar",
)

# títulos de Momento aposentados (references/etapas-canonicas.md)
APOSENTADOS = {
    "Abertura",
    "Exploração",
    "Roda de Partilha",
    "Encerramento e Transição",
    "Antes da Leitura",
    "Durante da Leitura",
    "Durante a Leitura",
    "Depois da Leitura",
    "Organização e Transição",
}

# termos aposentados no corpo do texto -> o que escrever (termos-e-nomes.md, seção 8);
# comparados sem acento e em minúsculas
TERMOS_APOSENTADOS = [
    ("roteiro do educador", "Orientações do Educador"),
    ("story time", "Hora do Conto"),
    ("roda de partilha", "Roda (não é termo)"),
    ("rotina de organizacao", "Rotina de Encerramento"),
    ("rotina de abertura da hora do conto", "Rotina de Abertura"),
    ("rotina de encerramento da hora do conto", "Rotina de Encerramento"),
    ("dirigida pelas criancas", "Dirigida pela criança"),
    ("g3", "Infantil 3"),
    ("g4", "Infantil 4"),
    ("g5", "Infantil 5"),
    ("protagonistas lab", "Intercriativa Lab"),
    ("caderno fazer e brincar", "Fazer e Brincar"),
    ("conexao com as familias", "Conexão Casa-Escola"),
    ("storyboard", "quadro de cenas"),
]

# pessoas: nunca (termos-e-nomes.md, seção 8)
PESSOAS_PROIBIDAS = ["aluno", "aluna", "alunos", "alunas", "estudante", "estudantes",
                     "educando", "educandos", "professor", "professora", "professores",
                     "tia", "tias", "pais", "educadora"]

TODOS_OS_TITULOS = set(LANCAMENTO) | set(GERAL) | APOSENTADOS

HEADING_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\*\*)?([1-4])\s*(?:\||\.)\s*(.+?)\s*(?:\*\*)?\s*$",
    re.MULTILINE,
)
CODIGO_RE = re.compile(r"\bS(\d+)\.D(\d+)\.A(\d+)\b")
MARCADOR_RE = re.compile(r"\s*\[c[oó]digo biblioteca\]", re.IGNORECASE)
TRAVESSAO_OK = "eu faco - nos fazemos - voce faz"


def acc(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def visivel(s: str) -> str:
    """Texto como aparece na página: sem marcador da Biblioteca, sem marcas de tópico ou itálico."""
    s = MARCADOR_RE.sub("", s)
    s = re.sub(r"^\s*-\s+", "", s, flags=re.MULTILINE)
    s = re.sub(r"\*+", "", s)
    return " ".join(s.split())


def extrair_momentos(texto: str) -> list[tuple[int, str, int]]:
    momentos: list[tuple[int, str, int]] = []
    for match in HEADING_RE.finditer(texto):
        numero = int(match.group(1))
        titulo = match.group(2).strip().rstrip("#").strip().strip("*").strip()
        if titulo in TODOS_OS_TITULOS:
            momentos.append((numero, titulo, match.start()))
    return momentos


def extrair_codigo(texto: str, codigo: str | None) -> str | None:
    if codigo:
        return codigo.upper()
    match = CODIGO_RE.search(texto.upper())
    return match.group(0) if match else None


def materiais(texto: str) -> str | None:
    m = re.search(r"^(?:#{1,4}\s*|\*\*)Materiais e Prepara\S*?\**\s*\n(.*?)(?=^#{1,6}\s|^\**\s*[1-4]\s*[|.]|\Z)",
                  texto, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else None


def validar_texto(texto: str, codigo: str | None) -> tuple[list[str], list[str]]:
    erros: list[str] = []
    avisos: list[str] = []

    codigo_resolvido = extrair_codigo(texto, codigo)
    if codigo_resolvido is None:
        erros.append("Código da aula ausente. Informe --codigo S#.D#.A#.")
        esperado = GERAL
    else:
        esperado = LANCAMENTO if codigo_resolvido == "S1.D1.A1" else GERAL

    momentos = extrair_momentos(texto)
    nomes = tuple(titulo for _, titulo, _ in momentos)
    numeros = tuple(numero for numero, _, _ in momentos)

    aposentados_encontrados = [titulo for titulo in nomes if titulo in APOSENTADOS]
    if aposentados_encontrados:
        erros.append(
            "Títulos de Momento aposentados encontrados: "
            + ", ".join(dict.fromkeys(aposentados_encontrados))
        )

    if len(momentos) != 4:
        erros.append(f"A aula deve ter 4 Momentos; foram encontrados {len(momentos)}.")
    if numeros != (1, 2, 3, 4):
        erros.append(f"Numeração dos Momentos incorreta: {numeros or 'nenhuma'}.")
    if nomes != esperado:
        erros.append(
            "Sequência esperada: " + " | ".join(esperado) + ". "
            "Sequência encontrada: " + (" | ".join(nomes) if nomes else "nenhuma") + "."
        )

    if "Lançamento do Projeto" in nomes and codigo_resolvido != "S1.D1.A1":
        erros.append("Lançamento do Projeto só pode aparecer em S1.D1.A1.")

    minusculo = texto.lower()
    if "dialógica" in minusculo and "peer" not in minusculo:
        erros.append("Uma leitura dialógica deve explicitar o uso de PEER.")

    if "[ATUALIZAR]" in texto:
        erros.append("Marcador [ATUALIZAR] ainda presente.")

    for i, linha in enumerate(texto.splitlines(), 1):
        flat = acc(linha)
        if "—" in linha or "–" in linha or re.search(r"\s-{2,3}\s|-{3}", linha):
            if TRAVESSAO_OK in flat.replace("—", "-").replace("–", "-"):
                pass
            elif re.search(r"[\"“”]", linha) or re.search(r"\b(disse|diz|falou|gritou|perguntou)\b", flat):
                avisos.append(f"linha {i}: travessão. Só vale em fala citada de um livro; confira.")
            else:
                erros.append(f"linha {i}: travessão. O estilo da casa não usa travessão (nem -- ou ---).")
        if re.search(r"[\"“”][^\"“”]{3,}[\"“”]", linha):
            erros.append(f"linha {i}: texto entre aspas. Fala do educador vai em itálico, sem aspas.")
        for velho, novo in TERMOS_APOSENTADOS:
            if re.search(r"\b%s\b" % re.escape(velho), flat):
                erros.append(f"linha {i}: termo aposentado '{velho}'; escreva {novo}.")
                break
        for w in PESSOAS_PROIBIDAS:
            if re.search(r"\b%s\b" % w, flat):
                erros.append(f"linha {i}: use criança(s), educador ou famílias e responsáveis, nunca '{w}'.")
                break
        if "cada crianca" in flat:
            erros.append(f"linha {i}: use a criança ou as crianças, nunca cada criança.")
        if re.search(r"\bfamilias?\b", flat) and "familias e responsaveis" not in flat:
            avisos.append(f"linha {i}: 'família(s)' sozinho; a casa escreve famílias e responsáveis.")
        if re.search(r"\bamigos?\b|\bamigas?\b", flat):
            avisos.append(f"linha {i}: 'amigo' como termo neutro; a casa usa colega.")

    if len(momentos) == 4:
        corpos: list[str] = []
        for index, (numero, titulo, inicio) in enumerate(momentos):
            fim = momentos[index + 1][2] if index + 1 < len(momentos) else len(texto)
            bloco = texto[inicio:fim]
            corpo = bloco.split("\n", 1)[1] if "\n" in bloco else ""
            corpos.append(corpo)
            n = len(visivel(corpo))
            if n > 600:
                avisos.append(f"Momento {numero} | {titulo} ultrapassa 600 caracteres ({n}).")

        # rotinas (templates-de-aula.md, seção 4): abertura no começo de Preparar para a Leitura,
        # encerramento no fim do Momento 4
        idx_prep = next((k for k, (_, t, _) in enumerate(momentos) if t == "Preparar para a Leitura"), None)
        if idx_prep is not None:
            primeiro = acc(corpos[idx_prep].strip().split("\n", 1)[0])
            if not ("rotina de abertura" in primeiro and "codigo biblioteca" in primeiro):
                erros.append(f"Momento {momentos[idx_prep][0]} | Preparar para a Leitura deve abrir com "
                             "'Siga a *Rotina de Abertura* [código biblioteca]'.")
        linhas4 = [l for l in corpos[3].strip().split("\n") if l.strip()]
        ultimo = acc(linhas4[-1]) if linhas4 else ""
        if not ("rotina de encerramento" in ultimo and "codigo biblioteca" in ultimo):
            erros.append(f"Momento 4 | {momentos[3][1]} deve fechar com "
                         "'Siga a *Rotina de Encerramento* [código biblioteca]'.")

    mat = materiais(texto)
    if mat is None:
        avisos.append("Não achei a seção Materiais e Preparação.")
    elif len(visivel(mat)) > 270:
        avisos.append(f"Materiais e Preparação com {len(visivel(mat))} caracteres (página: máx 270).")

    if "[código biblioteca]" in texto:
        avisos.append("Há [código biblioteca] a atribuir (normal até alguém dar o código).")

    return erros, avisos


def self_test() -> int:
    casos = [
        (
            "lançamento válido",
            """S1.D1.A1
### 1 | Lançamento do Projeto
- Convide a turma a observar uma pista.
### 2 | Preparar para a Leitura
- Siga a *Rotina de Abertura* [código biblioteca]. Mostre a capa.
### 3 | Ler e Explorar
- Leia o texto inteiro.
### 4 | Conversar e Compartilhar
- Retome as imagens. Siga a *Rotina de Encerramento* [código biblioteca].
""",
            "S1.D1.A1",
            True,
        ),
        (
            "dialógica válida",
            """S3.D4.A1 · Releitura dialógica
### 1 | Preparar para a Leitura
- Siga a *Rotina de Abertura* [código biblioteca]. Retome a história.
### 2 | Ler e Explorar
- Use PEER em páginas selecionadas.
### 3 | Conversar e Compartilhar
- Convide a turma a explicar as pistas.
### 4 | Organizar e Encerrar
- Guarde o livro.
- Siga a *Rotina de Encerramento* [código biblioteca].
""",
            "S3.D4.A1",
            True,
        ),
        (
            "nomes antigos inválidos",
            """S2.D1.A1
1. Abertura
texto
2. Exploração
texto
3. Roda de Partilha
texto
4. Encerramento e Transição
texto
""",
            "S2.D1.A1",
            False,
        ),
        (
            "sem rotinas, com travessão, aspas e termo aposentado",
            """S3.D1.A1
### 1 | Preparar para a Leitura
- Retome a história -- com os alunos.
### 2 | Ler e Explorar
- Pergunte "o que aconteceu?" e use o storyboard.
### 3 | Conversar e Compartilhar
- Converse — sem pressa.
### 4 | Organizar e Encerrar
- Guarde o livro.
""",
            "S3.D1.A1",
            False,
        ),
    ]

    falhas = 0
    for nome, texto, codigo, deve_passar in casos:
        erros, _ = validar_texto(texto, codigo)
        passou = not erros
        if passou != deve_passar:
            falhas += 1
            print(f"FALHOU: {nome}: {erros}")
    if falhas:
        return 1
    print(f"Self-test: {len(casos)} casos aprovados.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo", nargs="?", type=Path)
    parser.add_argument("--codigo")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.arquivo is None:
        parser.error("informe o arquivo ou use --self-test")

    texto = args.arquivo.read_text(encoding="utf-8")
    erros, avisos = validar_texto(texto, args.codigo)

    for erro in erros:
        print(f"ERRO: {erro}")
    for aviso in avisos:
        print(f"AVISO: {aviso}")

    if erros:
        print(f"Resultado: reprovado com {len(erros)} erro(s).")
        return 1
    print(f"Resultado: aprovado com {len(avisos)} aviso(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
