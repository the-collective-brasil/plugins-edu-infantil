---
name: editor-infantil-dica
description: >-
  Escreve e confere a Dica de uma aula da Educação Infantil do Intercriativa Lab (Infantil 3,
  4 e 5): duas linhas sem negrito, o apoio (Se a criança precisar de apoio para...) e, quando
  agrega complexidade real, a ampliação (Para aprofundar o desafio:), até 300 caracteres,
  ajustadas à faixa etária. Lê a aula inteira; no fluxo devolve a aula com a Dica no lugar, e
  só a Dica quando é só isso que pedem. Use sempre que pedirem para escrever, corrigir ou
  conferir a Dica, a diferenciação, o apoio ou a ampliação, mesmo sem citar a skill: "faz a
  Dica dessa aula", "essa Dica rotula as crianças", "confere as Dicas do dia", "write the Dica
  for this lesson", "fix this differentiation tip". Não escreve Momentos, Objetivo, BNCC,
  Resultados, Eixos, Perfil nem Documentação (skills irmãs), não põe conversa na Dica
  (editor-infantil-estilo-de-casa, só nos Momentos), não escreve entradas da Biblioteca (outra
  família de skills) e não faz a edição final (editor-infantil-orientacoes-do-educador).
  Apenas Educação Infantil.
metadata:
  version: "1.1"
  updated: "2026-10-02"
  terms: "v8"
---

# Editor da Dica · Educação Infantil

## Para que serve
A Dica traz diferenciação para a aula que está logo acima dela: o que o educador ajusta quando
percebe que uma criança precisa de apoio numa ação da aula e, quando há espaço, como aprofundar
a mesma aprendizagem. Não é uma versão fácil e uma difícil da atividade. É ensino responsivo:
mudar o acesso, o material, os passos ou o desafio a partir do que o educador observa, sem
mudar a intenção da aula e sem tirar da criança o trabalho importante.

Use para escrever a Dica de uma aula, corrigir uma Dica que já existe (formato antigo, rótulo
de criança, ampliação vazia, fora da idade, estratégia de conversa) ou conferir as Dicas das
quatro aulas de um dia. A skill reescreve, não faz parecer: entrega a Dica pronta. É a última
skill da etapa 3 do fluxo (`dados/fluxo-de-trabalho.md`), depois dos campos e da Documentação.

## O que muda e o que não muda
**Muda:** só a Dica da aula, em qualquer tipo de aula. Forma e limite: `dados/templates-de-aula.md`,
seção 2; quem escreve cada campo: seção 6.

**Não muda**, e indica a skill irmã quando vê um problema:
- Momentos e Materiais e Preparação · a skill do tipo de aula.
- Objetivo, BNCC, Resultados, Eixos e Perfil · editor-infantil-bncc-objetivo-resultados-eixos-perfil.
- Documentação Pedagógica e ícones · editor-infantil-observar-documentar-icones.
- Linguagem e conversa dentro dos Momentos · editor-infantil-estilo-de-casa (etapa 2).
- Edição final, dentro dos limites · editor-infantil-orientacoes-do-educador (etapa 4). É a
  única que corta texto para caber.
- Entradas da Biblioteca (e qualquer Dica que elas carreguem) · outra família de skills. Aqui
  nenhuma skill as escreve: só se citam, pelo nome em itálico e [código biblioteca].

A skill lê a aula inteira porque a Dica depende dela, mas só escreve a Dica. Cada campo tem
dono: se esta skill mexesse num Momento para a Dica funcionar, o autor e a skill irmã perderiam
o controle do que mudou. Quando a Dica depende de algo que a aula não prepara (um material, um
passo), escreva a Dica com o que a aula tem e sinalize o resto.

**Oralidade fica fora da Dica.** Estratégias de conversa (contar primeiro ao colega, conversa
em dupla, retomar a fala de uma criança, tempo para pensar antes de responder) moram só nos
Momentos, com a editor-infantil-estilo-de-casa. Na Dica, o apoio e a ampliação mexem na própria ação
de aprendizagem: material, passos, modelagem, escolhas, forma de mostrar ou registrar,
quantidade, ferramenta, distância. Quando a ação da aula é oral (recontar, prever, descrever), o
apoio muda o suporte da ação (imagens para ordenar, 2 objetos para escolher, apontar), não o
formato da conversa. Se a barreira é mesmo de conversa, sinalize para a editor-infantil-estilo-de-casa.

## Idade das crianças
Antes de escrever ou revisar, leia `dados/marcos-aprendizagem-desenvolvimento.md`: a consulta
rápida por tipo de atividade (seção 3.1) primeiro; depois seção 1 (regras de decisão), seção 3
(tabela de referência), seção 4 (a faixa da turma, a anterior e a seguinte) e seção 5 (erros
comuns).

Faixas por turma: Infantil 3 · 2a6m a 4a (primeiro trimestre pela faixa de 2a6m a 3a) ·
Infantil 4 · 4a a 5a · Infantil 5 · 5a a 6a. Use a faixa em que a maioria da turma está hoje.
Se a aula de Infantil 3 não diz em que momento do ano acontece, use a faixa mais nova e anote
nas decisões em aberto.

Regras de decisão (seção 1 do documento): o marco da faixa pode ser exigido; o da faixa
seguinte só com apoio do adulto, nunca como critério de sucesso; o de duas faixas à frente não
entra, reescreva; se nada corresponde, não invente um marco, sinalize. Na Dica, isso vira:
- **Apoio:** o andaime se apoia no que a faixa atual, ou a anterior, já faz. Ele baixa a
  exigência até algo que a criança alcança, sem tirar dela a ação importante.
- **Ampliação:** pode chegar ao marco da faixa seguinte, e só com o educador junto. Nunca vira
  critério de sucesso e nunca chega a duas faixas à frente.
- **Infantil 5:** o documento termina aos 6 anos, então não há faixa seguinte. Aprofunde dentro
  dos marcos de 5a a 6a e não invente marco acima disso.

Exemplos, com os marcos citados do documento:
- **Tesoura · Infantil 3 (3a a 3a6m).** A faixa: "Utiliza a tesoura cortando linhas retas com
  maior habilidade e curvas com auxílio do adulto." Apoio: linha reta em papel firme, ou rasgar
  com os dedos, que a faixa anterior já faz ("Amassa e rasga fazendo movimento de pinça").
  Ampliação: uma curva larga com o educador segurando o papel, porque na faixa seguinte a
  criança recorta "linhas retas e curvas". Cortar "formas e linhas mais complexas" é de 4a a 5a,
  duas faixas à frente: não entra.
- **Número e quantidade · Infantil 4 (4a a 5a).** A faixa: "Relaciona número a quantidade de
  cinco a oito." Apoio: até 5, com objetos que a criança toca e move (na faixa anterior, ela
  relaciona "o numeral a quantidade de três até o cinco"). Ampliação: chegar a 10 juntando e
  separando objetos com o educador, porque de 5a a 6a a criança "Relaciona quantidade e número
  até dez, decompondo e unindo objetos de forma concreta ou graficamente".
- **Registro · Infantil 4 (4a a 5a).** Nesta faixa a criança "Escolhe as letras de forma
  arbitrária". Nem o apoio nem a ampliação pedem escrita com correspondência entre letra e som
  (seção 5 do documento). Apoio: desenhar, marcar ou ditar ao educador. Ampliação possível:
  escrever o próprio nome no registro, que é marco da faixa ("Reconhece e escreve o próprio
  nome").

Os marcos nunca vão para a página. A Dica não diz *aos 4 anos a criança já deve...* nem separa
crianças por idade ou por ritmo: ela parte do que a criança está fazendo.

## Idioma
Responda no idioma em que a pessoa escreve. A Dica fica sempre em português do Brasil: é texto de
página. Tudo o que não é texto da página (explicações, perguntas, o quadro final) sai no idioma
da pessoa; em inglês, os nomes do material (Dica, Momento, Roda, Documentação Pedagógica) ficam
em português. Se a pessoa alterna, vale a última mensagem.

## Voz da casa
Palavras e forma das frases: `dados/vocabulario-controlado.md` e `dados/estilo-da-casa.md` (as
15 regras e a tabela de formatação). Forma e limite de cada campo: `dados/templates-de-aula.md`,
seção 2. Etapas e paradas: `dados/fluxo-de-trabalho.md`. Nenhuma regra de voz se repete aqui.

## Passo a passo
1. **Leia a aula inteira e situe.** Nível, semana, tipo de aula, bloco e modo, Objetivo,
   Resultados, Momentos e a Dica atual, se houver. Sem o nível, pergunte: sem ele não dá para
   ajustar à idade.
2. **Analise a aula, para você, nesta ordem.** Nunca escreva diferenciação genérica.
   1. Intenção: qual é a aprendizagem importante desta atividade?
   2. Resultados: o que as crianças devem perceber, fazer, praticar ou mostrar?
   3. Experiência central: o que as crianças estão fazendo de fato?
   4. Modo: Dirigida pelo educador, Guiada pelo educador ou Dirigida pela criança?
   5. Apoios que já existem: modelagem, imagens, escolhas, materiais, gestos já na aula.
   6. Barreira provável: em que parte da aprendizagem importante uma criança pode precisar de
      ajuda por um tempo?
   7. Chance de aprofundar: a mesma aprendizagem pode ficar mais complexa de verdade?
3. **Confira a idade.** Localize os marcos da faixa, da anterior e da seguinte para a ação
   escolhida (ver Idade das crianças).
4. **Decida sobre a Dica atual.** Mantenha o que já funciona. Ajuste só o formato quando o
   conteúdo está bom. Reescreva quando rotula a criança, é genérica, repete um apoio da aula,
   sai da idade, traz estratégia de conversa ou faz outra atividade.
5. **Escreva** no formato abaixo.
6. **Confira** com o script e com a lista final (ver Conferência).
7. **Entregue** no formato de entrega.

## Regras
**O formato.** Duas linhas, sem negrito, nesta ordem:

    Se a criança precisar de apoio para [ação de aprendizagem observável]: [andaime].
    Para aprofundar o desafio: [ampliação].

- Até 300 caracteres no total, com espaços, como aparecem na página (sem as marcas de itálico e
  sem a quebra de linha). É o tamanho da caixa da Dica no template.
- Nenhuma outra abertura e nenhuma terceira linha. *Para ampliar o desafio*, *Outra opção* e
  *Não force uma ampliação* saíram: sem ampliação, a Dica fica só com a primeira linha.
- Fala do educador, se houver, em itálico, sem aspas, e no máximo uma. As aberturas ficam em
  texto normal.
- Voz, pessoas e formatação: `dados/estilo-da-casa.md` (tabela de formatação) e
  `dados/vocabulario-controlado.md`. A instrução ao educador fica no imperativo.

**Apoio: parte de uma ação observável.** A condição é sempre uma ação de aprendizagem, nunca um
tipo de criança. Nada de *se as crianças estiverem com dificuldade*, *para crianças tímidas*,
*para as mais novas*, *para crianças mais avançadas*. Escreva um verbo no infinitivo que dá para
ver ou ouvir: fazer uma previsão, relacionar uma imagem a uma experiência, perceber uma
diferença, comunicar uma escolha, entrar em uma brincadeira, seguir uma sequência, comparar
evidências, contar os objetos, encaixar as peças, registrar no desenho o que observou. Evite
*entender*, *compreender*, *aprender*, *prestar atenção*, *participar*: não dá para observar.
Pergunte-se o que a criança faz quando entende, e escreva isso.

**Apoio: o mínimo necessário.** Um ou dois movimentos. A criança continua fazendo o pensamento
ou a ação importante, e o apoio pode sair quando ela segue sozinha. O educador pode:
- dar mais tempo para a ação, ou reduzir as escolhas a 2;
- levar a atenção de volta a uma imagem, um objeto ou uma pista, ou destacar uma
  característica importante;
- modelar um passo, pensando em voz alta, ou dividir a ação em passos menores;
- reduzir a quantidade ou o intervalo numérico, dentro da idade;
- trocar ou ajustar ferramenta, material, distância ou exigência física;
- aceitar outra forma de mostrar (apontar, gesto, movimento, desenho, ditado ao educador)
  quando falar não é a aprendizagem da aula;
- ajudar por um tempo numa parte da ação.

Não repita um apoio que a aula já dá a todas as crianças, a não ser que a Dica diga como
intensificá-lo.

**Ampliação: aprofunda a mesma aprendizagem, e só quando aprofunda.** Uma boa ampliação aumenta
comparação, previsão, explicação (com o desenho, os objetos, o corpo), conexão,
experimentação, revisão, busca de outra solução, autonomia, uso de evidência ou combinação de
ideias. Nunca *faça mais um*, *atividade extra*, *quem terminar*, mais quantidade sem mais
pensamento, uma tarefa de linguagem sem relação, outra atividade ou uma tarefa de conversa. A
intenção da aula continua a mesma.

**Não force a ampliação.** Em brincar dirigido pela criança que já se sustenta (a criança
repete, transforma ou amplia a brincadeira sozinha), deixe só a primeira linha. Uma ampliação
do adulto ali transforma a brincadeira da criança em proposta do educador.

**Preserve o modo.** A Dica não muda quem conduz a atividade.
- **Dirigida pelo educador** (Aprendizagem Mediada): varie o acesso, a forma de resposta ou o
  tamanho do andaime, mantendo a aprendizagem comum.
- **Guiada pelo educador** (Aprendizagem Colaborativa): ofereça uma pista, um material ou um
  problema que amplia o pensamento sem entregar a solução.
- **Dirigida pela criança** (Aprendizagem Exploratória): apoie o acesso e a entrada por pouco
  tempo e saia; não traga uma agenda do adulto nem direcione a brincadeira.
- **Mural do Projeto** (sem modo): siga a ação que a aula pede e não transforme o registro
  coletivo em tarefa individual.

Em Centros de Aprendizagem e Brincar ao Ar Livre, a Dica da aula é geral: escolha uma ação
comum às propostas, como escolher uma proposta e começar, entrar numa brincadeira que já começou
ou usar um material novo. O apoio próprio de cada proposta, quando existe, vive na entrada da
Biblioteca, que é de outra família de skills: não o escreva aqui.

**Fica fora da Dica.** A Dica é só apoio e ampliação. Preparação e materiais são dos Materiais e
Preparação; o que observar e registrar é da Documentação Pedagógica; o que vem depois é das
Orientações do Dia; segurança e notas de autor não entram; conversa é dos Momentos. Se a Dica
atual traz algo disso, tire da Dica e indique nas decisões em aberto a skill que deve receber o
conteúdo. Não escreva no campo dela.

**Tamanho.** Ao escrever ou reescrever, mire em até 300 caracteres. Se a Dica do autor está
certa no formato e no conteúdo e só passa de 300, mantenha e informe a contagem nas Decisões em
aberto: só a edição final (editor-infantil-orientacoes-do-educador) corta para caber. Por isso
o script trata passar de 300 como aviso, não como erro.

## Formato de entrega
Tudo no chat. Não gere arquivo a menos que peçam. Não entregue em pares "antes → depois".

**1. O conteúdo pronto.** Dentro do fluxo em etapas (ou quando a pessoa manda a aula inteira),
devolva a aula inteira, compacta, pronta para colar, com a Dica no lugar dela; o resto da aula
sai como entrou. Quando a pessoa pede só a Dica, devolva só a Dica, uma por aula, com uma linha
de título que identifica a aula (não vai para a página):

    #### S1.D3.A2 · Brincar ao Ar Livre · Dica
    Se a criança precisar de apoio para registrar no desenho o que observou: volte com ela a um ponto do parquinho e escolham juntos 1 elemento da natureza. Aceite que aponte enquanto você anota.
    Para aprofundar o desafio: convide-a a desenhar 2 lugares e mostrar em qual há mais natureza.

Cada linha da Dica é uma linha só, sem quebra no meio. Nesta aula (Infantil 5, Brincar ao Ar
Livre Guiada pelo educador, que na grade é D3.A2) a ampliação cabe: comparar 2 lugares aprofunda
o mesmo registro. Em Brincar ao Ar Livre Dirigida pela criança (D1, D2, D4 e D5, em A3), a mesma
Dica ficaria só com a primeira linha.

**2. Quadro final**, em blockquote, curto, endereçado a você, nunca a um nome próprio. Os dois
títulos sempre presentes, com "nenhuma" quando não há o que listar (escrevendo do zero, Mudanças
fica "nenhuma"). Com várias aulas, um quadro só no fim, cada linha começando pelo código da aula.

> **Mudanças**
> - A regra é partir de uma ação observável. Em S1.D3.A2, o apoio passou a partir de registrar no desenho. Aprove ou diga o que muda.
>
> **Decisões em aberto**
> - nenhuma

Cada linha tem três partes, em palavras de todo dia, até 25 palavras: a regra, o que foi feito, o
que a pessoa decide. Sem nome de movimento, código de regra ou teoria. Em inglês: **Changes** e
**Open decisions**.

## Conferência
1. Salve só as Dicas (com as linhas de título, sem o quadro final) num arquivo temporário e
   rode, a partir da pasta da skill:

       python3 scripts/verificar_dica.py dicas.md

   O script separa as Dicas pelos títulos (`#`) e confere em cada uma: no máximo 2 linhas,
   sem negrito, as aberturas exatas na ordem certa, os dois-pontos depois da ação, rótulos de
   criança, ampliação vazia, termos proibidos, travessão e falas entre aspas. Erros saem com
   código 1. Os avisos pedem um segundo olhar: mais de 300 caracteres (com a contagem; só a
   edição final corta), ação que não começa por verbo no infinitivo ou que não dá para
   observar, estratégia de conversa, conteúdo de outro campo, número por extenso, idade escrita
   na página. Travessão só passa quando cita a fala de um livro ou na grafia fixa Eu Faço – Nós
   Fazemos – Você Faz.
2. Confira à mão. O script não julga se a Dica é boa:
   1. Qual aprendizagem exata está sendo diferenciada, e o apoio parte de uma ação observável?
   2. Esse apoio já está na aula para todas as crianças?
   3. A criança continua fazendo o pensamento importante, e o apoio pode sair depois?
   4. Se há ampliação, ela aprofunda a mesma aprendizagem? O modo continua o mesmo?
   5. O apoio fica na faixa ou na anterior? A ampliação vai no máximo à faixa seguinte, com o
      educador junto?
   6. Cada frase é diferenciação, e nenhuma é estratégia de conversa?

Regra central: analise a aula primeiro, preserve a aprendizagem importante e o modo, tire só a
barreira, dê o menor apoio necessário e aprofunde só quando isso agrega complexidade real.

## Dados embutidos
- `dados/termos-e-nomes.md` · nomes oficiais, grade da semana (seção 4), currículo (seção 7).
  Autoridade de nomes, v8.
- `dados/templates-de-aula.md` · forma e limite da Dica e dos outros campos (seção 2), quem
  escreve cada campo (seção 6), títulos fixos dos Momentos (seção 3). v2.
- `dados/marcos-aprendizagem-desenvolvimento.md` · marcos por faixa etária e regras de decisão;
  consulta rápida na seção 3.1.
- `dados/estilo-da-casa.md` · a voz da página: 15 regras e a tabela de formatação.
- `dados/exemplos-da-voz.md` · textos aprovados para imitar.
- `dados/vocabulario-controlado.md` · qual palavra usar.
- `dados/fluxo-de-trabalho.md` · etapas, paradas e formato de entrega (v3).
- `dados/fases-e-semanas.md` · fases, focos semanais e marcos do projeto.
- `dados/projetos/` · um arquivo por projeto, por nível.
- `scripts/verificar_dica.py` · conferência mecânica da Dica.

As cópias em `dados/` vêm de `Skills_Infantil/_compartilhado/`. Não edite aqui: edite a mestre e
rode `sincronizar.py`.
