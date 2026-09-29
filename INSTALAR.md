# Como instalar os plugins de autoria · Intercriativa Lab · Educação Infantil

Esta pasta é um "marketplace": uma lista de plugins que o Claude e o ChatGPT sabem ler. Cada
autor instala só o plugin da sua trilha:

- `autoria-infantil-hora-do-conto`
- `autoria-infantil-mural`
- `autoria-infantil-atelie`

O jeito mais simples é guardar esta pasta num repositório do GitHub da equipe. Aí cada autor
adiciona o marketplace uma vez e recebe as atualizações. Abaixo, `ENDERECO` é o endereço do
repositório (ex.: `intercriativa/plugins-infantil`) ou o caminho desta pasta no computador.

## No Claude (app para desktop, aba Code, ou Claude Code)
1. Numa conversa da aba Code, digite:
   `/plugin marketplace add ENDERECO`
2. Depois, instale o plugin da sua trilha, por exemplo:
   `/plugin install autoria-infantil-mural@intercriativa-infantil`
   (ou abra **+ → Plugins**, escolha o marketplace *intercriativa-infantil* e instale).
3. Comece uma conversa nova. As skills aparecem sozinhas.

## No ChatGPT (app para desktop, modo de trabalho) ou no Codex
1. No Terminal, digite uma vez:
   `codex plugin marketplace add ENDERECO`
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
a pasta para o repositório. Os autores recebem a atualização pelo marketplace.

## Observação
As skills têm pequenos scripts de conferência em Python 3. No Claude Code e no Codex, eles rodam no
computador do autor: se o Mac pedir para instalar as ferramentas de desenvolvedor, aceite.
