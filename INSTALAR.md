# Como instalar os plugins de autoria · Intercriativa Lab · Educação Infantil

Esta pasta é um "marketplace": uma lista de plugins que o Claude e o ChatGPT sabem ler. Cada
autor instala só o plugin da sua trilha:

- `autoria-infantil-hora-do-conto`
- `autoria-infantil-mural`
- `autoria-infantil-atelie`
- `autoria-infantil-comum` (para as outras trilhas)
- `autoria-infantil-biblioteca` (para quem revisa entradas da Biblioteca Digital)

Os plugins ficam no GitHub: https://github.com/the-collective-brasil/plugins-edu-infantil
Cada autor adiciona o marketplace uma vez e recebe as atualizações sozinho.

## No Claude (app para desktop, aba Code, ou Claude Code)
1. Numa conversa da aba Code, digite:
   `/plugin marketplace add the-collective-brasil/plugins-edu-infantil`
2. Depois, instale o plugin da sua trilha, por exemplo:
   `/plugin install autoria-infantil-mural@intercriativa-infantil`
   (ou abra **+ → Plugins**, escolha o marketplace *intercriativa-infantil* e instale).
3. Comece uma conversa nova. As skills aparecem sozinhas.

## No ChatGPT (app para desktop, modo de trabalho) ou no Codex
1. No Terminal, digite uma vez:
   `codex plugin marketplace add the-collective-brasil/plugins-edu-infantil`
2. Feche e abra o ChatGPT de novo.
3. Abra **Plugins**, escolha o marketplace *Intercriativa Lab · Educação Infantil* e selecione o
   **+** do plugin da sua trilha.
4. Comece uma conversa nova. As skills aparecem sozinhas.

## Para quem administra a conta
- **ChatGPT:** o admin do workspace pode importar e sincronizar este marketplace do GitHub para a
  equipe.
- **Claude:** o admin da organização pode registrar este marketplace nas configurações
  gerenciadas do Claude Code, para ele aparecer para todos.

## Para atualizar
Quem cuida das skills roda `montar_plugins.py` (em `_compartilhado`) com uma versão nova e envia
para o GitHub (Commit e Push no GitHub Desktop). Os autores recebem a atualização pelo
marketplace. No Claude, para forçar: `/plugin marketplace update intercriativa-infantil`.

## Observação
As skills têm pequenos scripts de conferência em Python 3. No Claude Code e no Codex, eles rodam no
computador do autor: se o Mac pedir para instalar as ferramentas de desenvolvedor, aceite.
