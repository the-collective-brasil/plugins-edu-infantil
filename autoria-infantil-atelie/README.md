# Autoria · Ateliê de Arte · Educação Infantil

Plugin de autoria do Intercriativa Lab para quem escreve as aulas de **Ateliê de Arte** (Infantil
3, 4 e 5). Traz a skill da trilha e as cinco skills comuns da família editor-infantil. Cada skill
faz um trabalho só.

## Ordem de uso numa aula
1. **editor-infantil-atelie** · escreve a aula de Ateliê de Arte: título, linha de abertura, Materiais e
   Preparação e os 4 Momentos e a página da criança.
2. **editor-infantil-bncc-objetivo-resultados-eixos-perfil** · Objetivo, Habilidades BNCC, Eixos,
   Perfil e Resultados.
3. **editor-infantil-observar-documentar-icones** · Documentação Pedagógica (Observar e
   Documentar) e ícones de registro.
4. **editor-infantil-dica** · a Dica, em duas linhas.
5. **editor-infantil-oralidade** · revisa a conversa dentro dos Momentos.
6. **editor-infantil-estilo-de-casa** · revisa a linguagem.

Depois, a aula vai para a produção, que faz o ajuste final ao template e o PDF
(editor-infantil-orientacoes-do-educador, fora deste plugin).

## Regras da família
- Tudo se ajusta à faixa etária pelos Marcos da Aprendizagem e Desenvolvimento (Joinville).
- Nomes, termos, limites e os nomes fixos dos Momentos vêm de `termos-e-nomes.md` (v7), dentro
  de cada skill.
- O texto da aula fica em português do Brasil. As notas seguem o idioma de quem pede.
- Nenhuma skill cria arquivo sem pedido: tudo sai no chat.

## Versão
0.1.0 · montado em 2026-09-29 a partir de `Skills_Infantil/_compartilhado/montar_plugins.py`.
Não edite as skills aqui dentro: edite a skill ou a mestre em `_compartilhado` e monte de novo.
