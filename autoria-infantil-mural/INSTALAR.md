# Como instalar · autoria-infantil-mural

Plugin de autoria de **Mural do Projeto** do Intercriativa Lab. Tudo o que o plugin precisa está nesta
pasta: as 6 skills, os dados de cada uma e os manifestos do Claude e do ChatGPT.

Primeiro, abra o arquivo `autoria-infantil-mural.zip` e guarde a pasta `autoria-infantil-mural` num lugar fixo do seu
computador (por exemplo, em Documentos). Não apague a pasta depois de instalar. Abaixo,
`CAMINHO` é o caminho dessa pasta (no Mac, arraste a pasta para a janela do Terminal ou da
conversa e o caminho aparece).

## No Claude (app para desktop, aba Code, ou Claude Code)
1. Numa conversa da aba Code, digite:
   `/plugin marketplace add CAMINHO`
2. Depois:
   `/plugin install autoria-infantil-mural@intercriativa-mural`
3. Comece uma conversa nova. As skills aparecem sozinhas.

## No ChatGPT (app para desktop, modo de trabalho) ou no Codex
1. No Terminal, digite:
   `codex plugin marketplace add CAMINHO`
2. Feche e abra o ChatGPT de novo.
3. Abra **Plugins**, escolha *Intercriativa Lab · Mural do Projeto* e selecione o **+** do plugin.
4. Comece uma conversa nova. As skills aparecem sozinhas.

## Ordem de uso
Veja o `README.md` desta pasta.

## Observação
As skills têm pequenos scripts de conferência em Python 3, que rodam no seu computador. Se o Mac
pedir para instalar as ferramentas de desenvolvedor, aceite.
