# Autoria · Ateliê de Arte · Educação Infantil

Plugin de autoria do Intercriativa Lab para quem escreve as aulas de **Ateliê de Arte** (Infantil
3, 4 e 5). Traz a skill da trilha e as skills comuns da família editor-infantil. Cada skill faz
um trabalho só; a coordenadora roda tudo em etapas.

## Como usar
Peça a aula inteira ("monta a aula S3.D2.A1 do Infantil 4 a partir destas notas", "revisa esta
aula inteira") e a **editor-infantil-aula** roda as etapas, parando para a sua aprovação ao fim de
cada uma. Ou peça uma etapa só.
1. **editor-infantil-atelie** · escreve a aula de Ateliê de Arte: título, linha de abertura, Materiais e
   Preparação e os 4 Momentos.
2. **editor-infantil-estilo-de-casa** · a conversa e a linguagem, na voz da casa.
3. **editor-infantil-bncc-objetivo-resultados-eixos-perfil** · Objetivo, Habilidades BNCC, Eixos,
   Perfil e Resultados; depois **editor-infantil-observar-documentar-icones** · Documentação
   Pedagógica e ícones; depois **editor-infantil-dica** · a Dica.
4. Edição final (editor-infantil-orientacoes-do-educador, fora deste plugin): o texto do dia dentro
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
