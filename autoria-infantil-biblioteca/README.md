# Revisor · Biblioteca Digital · Educação Infantil

Plugin do Intercriativa Lab com uma skill só: a **revisor-infantil-biblioteca**. Ela confere
entradas novas ou editadas da Biblioteca Digital contra os 8 templates (Jogo ou Prática Lúdica,
Estratégia, Rotina, Material Imprimível, Música/Canto/Parlenda/Aquecimento, Imagem Projetável/
Áudio/Vídeo, Proposta do Banco de Ideias, Guia de Prática Pedagógica) e contra as regras de
escrita da casa.

## Como usar
Cole a entrada, ou aponte um arquivo ou pasta, e peça a revisão: "revisa esta entrada da
Biblioteca". A skill escolhe o template pelo conteúdo, roda o validador e devolve um relatório
curto: o que mudar e o que só você decide. Para conferir só o que mudou num repositório:

    python3 skills/revisor-infantil-biblioteca/scripts/verificar_biblioteca.py biblioteca/ --git-base origin/main

## Versão
0.1.0 · 2026-10-03.
