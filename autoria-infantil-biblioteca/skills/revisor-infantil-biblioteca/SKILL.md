---
name: revisor-infantil-biblioteca
description: >-
  Confere entradas novas ou editadas da Biblioteca Digital da Educação Infantil do Intercriativa
  Lab (Infantil 3, 4 e 5) contra os 8 templates: Jogo ou Prática Lúdica, Estratégia, Rotina,
  Material Imprimível, Música/Canto/Parlenda/Aquecimento, Imagem Projetável/Áudio/Vídeo,
  Proposta do Banco de Ideias e Guia de Prática Pedagógica. Diz se o template é o certo, se os
  campos fixos estão completos, na ordem e sem seção vazia, e se a escrita segue as regras da
  casa. Use sempre que pedirem para revisar, conferir, validar ou aprovar uma entrada da
  Biblioteca, mesmo sem citar a skill: "revisa esta entrada da Biblioteca", "confere as
  entradas novas", "esse jogo está no template certo?", "check this Library entry". Não escreve
  a entrada do zero, não escreve a aula nem as Orientações do Educador e não revisa a aula
  (outras skills da família). Apenas Educação Infantil.
metadata:
  version: "0.1"
  updated: "2026-10-03"
  terms: "v8"
---

# Revisor da Biblioteca Digital · Educação Infantil

## Para que serve
Confere se uma entrada da Biblioteca Digital segue o template do seu tipo e as regras de escrita
da casa. Devolve um relatório curto: o que está certo, o que precisa mudar e o que só uma pessoa
decide. Não reescreve a entrada, a menos que peçam.

Tudo o que pode ser conferido por regra roda no validador. Você cuida do resto: o template certo,
a qualidade das instruções e o tom.

## O que a pessoa fornece
1. A entrada (texto colado, arquivo `.md` ou pasta de entradas).
2. Se souber, o template. Sem isso, o validador reconhece pelos campos e avisa quando não tem certeza.

Se faltar a entrada, peça só ela. Para "entradas novas ou editadas" num repositório, use
`--git-base <ref>` (ver Conferência).

## Passo a passo
1. **Leia** `dados/templates-biblioteca.md` (o que entra na Biblioteca, a regra de ouro, o quadro
   de escolha e os campos dos 8 templates) e `dados/regras-de-escrita.md`.
2. **Escolha o template pelo conteúdo, antes de rodar o validador.** O que a pessoa faz com o
   recurso decide. Se a entrada declara um template que não combina com o conteúdo (por exemplo,
   uma música no template de Jogo), diga isso primeiro: é a falha mais cara, porque muda todos
   os campos. Se nenhum dos 8 serve, não proponha um nono: sinalize.
3. **Rode o validador** (ver Conferência), uma vez por entrada ou na pasta inteira.
4. **Leia o que o validador não lê** (lista em `dados/regras-de-escrita.md`): se cada campo cumpre
   o que o nome promete, se cada instrução tem uma ação principal e cabe na faixa etária, se as
   falas exatas só aparecem quando ajudam, se a entrada não repete explicação longa de currículo
   e se não duplica outro recurso já cadastrado com outro nome.
5. **Entregue o relatório** (ver Formato) e espere a decisão da pessoa.

## Regras
**Um recurso, uma entrada.** Se o mesmo recurso aparece em duas entradas, aponte a duplicata e
peça para manter só uma. Não aprove "uma cópia por projeto".

**Campos fixos.** Os nomes e a ordem vêm de `dados/templates-biblioteca.md`. Campo faltando,
campo extra, campo fora de ordem ou campo vazio é problema. Não crie campo "só desta vez" e não
copie a forma de outro template.

**Nunca invente.** Termos e nomes do programa de `termos-e-nomes.md` (v8) na skill
editor-infantil-estilo-de-casa. Código da Biblioteca fica como `[código biblioteca]` até alguém
atribuir o código. Se uma informação falta na entrada, sinalize em vez de preencher.

**O que é da Biblioteca e o que é da aula.** O detalhe completo mora na entrada. As Orientações do
Educador ficam enxutas e só citam a entrada pelo nome em itálico com [código biblioteca]. Se a
entrada traz texto de currículo ou de Orientações do Educador, aponte.

**Idioma.** A entrada fica em português do Brasil. O relatório segue o idioma de quem pede.

## Formato do relatório
Tudo no chat. Não gere arquivo a menos que peçam. Uma seção por entrada:

> **[Título da entrada]** · Template [n] · [nome do template]
> **Resultado:** pronta · precisa de ajustes · template errado
> **Precisa mudar**
> - uma linha por problema, com o campo e o que fazer
> **Para você decidir**
> - uma linha por decisão que o validador não toma
> **Está certo**
> - o que já cumpre o template, em uma linha

Cada linha de "Precisa mudar" tem três partes, em palavras de todo dia, até 25 palavras: a
regra, onde ela falha, o que fazer. Exemplo: *Estratégia pede exatamente 3 passos. Em Como
conduzir há 2. Divida o segundo passo em dois.* Sem nome de código de regra. Se não há problema
em uma seção, escreva "nenhum". Com várias entradas, abra com um quadro de uma linha por
entrada (título, template, resultado) e só depois os detalhes.

## Conferência
Rode na entrada, na pasta, ou só nas entradas novas e editadas:

    python3 scripts/verificar_biblioteca.py entrada.md
    python3 scripts/verificar_biblioteca.py biblioteca/ --git-base origin/main
    python3 scripts/verificar_biblioteca.py entrada.md --template 3

Confere: template reconhecido; campos fixos, na ordem, sem extra e sem vazio; exatamente 3 passos
numerados em Como conduzir (Estratégia e Rotina); as 4 partes do Jogo e as 6 do Imprimível;
travessão, marcadores de preenchimento, colchetes que não são [código biblioteca], termos
proibidos e nomes aposentados (erros); inglês, instrução longa ou com várias ações e currículo
repetido (avisos); título igual em outra entrada (erro). Sai com código 1 se houver erro.

## Dados embutidos
- `dados/templates-biblioteca.md` · o que entra na Biblioteca, a regra de ouro, como escolher e os
  campos dos 8 templates.
- `dados/regras-de-escrita.md` · as 12 regras de escrita e a divisão entre validador e pessoa.
- `scripts/verificar_biblioteca.py` · conferência mecânica.
