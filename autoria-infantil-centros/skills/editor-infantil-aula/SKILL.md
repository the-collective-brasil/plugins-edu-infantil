---
name: editor-infantil-aula
description: >-
  Coordena a escrita ou a revisão de uma aula da Educação Infantil do Intercriativa Lab
  (Infantil 3, 4 e 5): pede o que falta, lê o projeto e a semana, e roda as skills da família
  editor-infantil em etapas, parando para aprovação ao fim de cada uma. Use quando pedirem uma
  aula inteira a partir de notas ou a revisão completa de uma aula, mesmo sem citar a skill:
  "monta a aula S3.D2.A1 do Infantil 4", "transforma estas anotações numa aula", "revisa esta
  aula inteira", "build the lesson from these notes", "review this whole lesson". Para uma etapa
  só (Momentos, linguagem e conversa, campos, Dica, Documentação, edição final), chama só a skill daquela
  etapa. Não escreve nada ela mesma. Apenas Educação Infantil.
metadata:
  version: "0.1"
  updated: "2026-10-01"
  terms: "v8"
---

# Coordenadora · Educação Infantil

## Para que serve
Recebe o pedido, situa a aula e roda as etapas de `dados/fluxo-de-trabalho.md`, uma por vez.
Não escreve conteúdo: cada etapa é de uma skill da família.

## Passo a passo
1. **Situar.** Leia o pedido. Se faltar nível, projeto, semana e dia, tipo de aula, ou as notas
   ou a aula, pergunte só o que falta, uma pergunta de cada vez. Com o código S#.D#.A#, deduza o tipo de
   aula e o modo pela grade de `dados/termos-e-nomes.md`. Leia `dados/fases-e-semanas.md` (a
   semana) e o arquivo do projeto em `dados/projetos/` (um por projeto; `n` é o número do
   projeto no ano, 1 a 3; sem o número, procure o título do projeto na primeira linha dos
   arquivos do nível). Nenhum campo de etapa posterior aparece na entrega da etapa 1: a aula
   mostra só o que a etapa escreveu, e a linha final diz quais campos vêm nas próximas etapas.
2. **Decidir as etapas.** Pedido de uma etapa só: só ela. Sem pedido específico: etapas 1 a 3,
   depois 4 quando a pessoa aprovar tudo. "Roda tudo de uma vez": sem paradas.
3. **Anunciar** em 2 linhas o que vai rodar e em que ordem.
4. **Rodar uma etapa**, com a skill certa, passando a aula inteira e o contexto da etapa 0.
5. **Entregar** a aula inteira e o quadro da skill, e **parar**. Siga com "pode seguir".
6. Ao fim da etapa 3, pergunte se pode rodar a edição final (etapa 4): o texto do dia dentro dos limites, só texto.

## Regras
- Nunca invente nem acrescente conteúdo: isso é das skills de cada etapa.
- Nunca pule a etapa 0. Sem projeto e semana, a aula não se alinha a nada.
- Entregas compactas: a aula inteira, o quadro Mudanças e Decisões em aberto, uma linha dizendo
  qual é a próxima etapa.
- Entradas da Biblioteca e páginas da criança não são escritas aqui: outra família de skills.
- Idioma: responda no idioma em que a pessoa escreve (em inglês, tudo em inglês, menos o texto
  da página e os nomes do material). A aula fica sempre em português do Brasil.

## Dados embutidos
- `dados/fluxo-de-trabalho.md` · as etapas e as paradas.
- `dados/termos-e-nomes.md` · nomes, grade da semana.
- `dados/fases-e-semanas.md` e `dados/projetos/` · a fase, a semana e o projeto.
