#!/usr/bin/env python3
"""Valida a estrutura canônica de uma aula de Hora do Conto."""

from __future__ import annotations

import argparse
import re
import sys
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

TODOS_OS_TITULOS = set(LANCAMENTO) | set(GERAL) | APOSENTADOS

HEADING_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?([1-4])\s*(?:\||\.)\s*(.+?)\s*$",
    re.MULTILINE,
)

CODIGO_RE = re.compile(r"\bS(\d+)\.D(\d+)\.A(\d+)\b")


def extrair_etapas(texto: str) -> list[tuple[int, str, int]]:
    etapas: list[tuple[int, str, int]] = []
    for match in HEADING_RE.finditer(texto):
        numero = int(match.group(1))
        titulo = match.group(2).strip().rstrip("#").strip()
        if titulo in TODOS_OS_TITULOS:
            etapas.append((numero, titulo, match.start()))
    return etapas


def extrair_codigo(texto: str, codigo: str | None) -> str | None:
    if codigo:
        return codigo.upper()
    match = CODIGO_RE.search(texto.upper())
    return match.group(0) if match else None


def validar_texto(texto: str, codigo: str | None) -> tuple[list[str], list[str]]:
    erros: list[str] = []
    avisos: list[str] = []

    codigo_resolvido = extrair_codigo(texto, codigo)
    if codigo_resolvido is None:
        erros.append("Código da aula ausente. Informe --codigo S#.D#.A#.")
        esperado = GERAL
    else:
        esperado = LANCAMENTO if codigo_resolvido == "S1.D1.A1" else GERAL

    etapas = extrair_etapas(texto)
    nomes = tuple(titulo for _, titulo, _ in etapas)
    numeros = tuple(numero for numero, _, _ in etapas)

    aposentados_encontrados = [titulo for titulo in nomes if titulo in APOSENTADOS]
    if aposentados_encontrados:
        erros.append(
            "Etapas aposentadas encontradas: "
            + ", ".join(dict.fromkeys(aposentados_encontrados))
        )

    if len(etapas) != 4:
        erros.append(f"A aula deve ter 4 etapas canônicas; foram encontradas {len(etapas)}.")
    if numeros != (1, 2, 3, 4):
        erros.append(f"Numeração das etapas incorreta: {numeros or 'nenhuma'}.")
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

    if "\u2014" in texto:
        erros.append("Travessão não permitido pelo estilo da casa.")
    if "[ATUALIZAR]" in texto:
        erros.append("Marcador [ATUALIZAR] ainda presente.")
    if re.search(r"\bROTEIRO DO EDUCADOR\b", texto, re.IGNORECASE):
        erros.append("Use Orientações do Educador; Roteiro do Educador está aposentado.")

    if len(etapas) == 4:
        for index, (numero, titulo, inicio) in enumerate(etapas):
            fim = etapas[index + 1][2] if index + 1 < len(etapas) else len(texto)
            bloco = texto[inicio:fim]
            corpo = bloco.split("\n", 1)[1] if "\n" in bloco else ""
            if len(corpo.strip()) > 600:
                avisos.append(
                    f"Etapa {numero} | {titulo} ultrapassa 600 caracteres "
                    f"({len(corpo.strip())})."
                )

    if "[código biblioteca]" in texto:
        avisos.append("Há código da Biblioteca ainda não resolvido.")

    return erros, avisos


def self_test() -> int:
    casos = [
        (
            "lançamento válido",
            """S1.D1.A1
### 1 | Lançamento do Projeto
- Convide a turma a observar uma pista.
### 2 | Preparar para a Leitura
- Mostre a capa.
### 3 | Ler e Explorar
- Leia o texto inteiro.
### 4 | Conversar e Compartilhar
- Retome as imagens.
""",
            "S1.D1.A1",
            True,
        ),
        (
            "dialógica válida",
            """S3.D4.A1 · Releitura dialógica
### 1 | Preparar para a Leitura
- Retome a história.
### 2 | Ler e Explorar
- Use PEER em páginas selecionadas.
### 3 | Conversar e Compartilhar
- Convide a turma a explicar as pistas.
### 4 | Organizar e Encerrar
- Guarde o livro.
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
    print("Self-test: 3 casos aprovados.")
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
