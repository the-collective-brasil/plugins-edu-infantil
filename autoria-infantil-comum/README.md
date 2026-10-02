# Autoria · skills comuns · Educação Infantil

Plugin de autoria do Intercriativa Lab com as skills comuns da família editor-infantil, para
autores de qualquer trilha (Infantil 3, 4 e 5). Não traz skill de tipo de aula: a aula da sua
trilha já chega escrita, e estas skills cuidam da conversa, da linguagem, dos campos, da
Documentação e da Dica. Cada skill faz um trabalho só; a coordenadora roda tudo em etapas.

## Como usar
Traga a aula da sua trilha (título, linha de abertura, Materiais e os 4 Momentos, com os títulos
fixos de `templates-de-aula.md`, seção 3) e peça a revisão inteira: a **editor-infantil-aula** roda
as etapas, parando para a sua aprovação ao fim de cada uma. Ou peça uma etapa só.
1. **editor-infantil-estilo-de-casa** · a conversa e a linguagem, na voz da casa.
2. **editor-infantil-bncc-objetivo-resultados-eixos-perfil** · Objetivo, Habilidades BNCC, Eixos,
   Perfil e Resultados; depois **editor-infantil-observar-documentar-icones** · Documentação
   Pedagógica e ícones; depois **editor-infantil-dica** · a Dica.
3. Edição final (editor-infantil-orientacoes-do-educador, fora deste plugin): o texto do dia dentro
   dos limites, só texto.

## Regras da família
- Tudo se ajusta à faixa etária pelos Marcos da Aprendizagem e Desenvolvimento (Joinville).
- Nomes de `termos-e-nomes.md` (v8); forma e limites de `templates-de-aula.md`; linguagem de
  `estilo-da-casa.md`, `exemplos-da-voz.md` e `vocabulario-controlado.md`; etapas de
  `fluxo-de-trabalho.md`, dentro de cada skill.
- O texto da aula fica em português do Brasil. As notas seguem o idioma de quem pede.
- Nenhuma skill cria arquivo sem pedido: tudo sai no chat.

## Versão
0.4.0 · montado em 2026-10-02 a partir de `Skills_Infantil/_compartilhado/montar_plugins.py`.
Não edite as skills aqui dentro: edite a skill ou a mestre em `_compartilhado` e monte de novo.
