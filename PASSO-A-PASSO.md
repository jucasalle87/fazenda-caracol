# Passo a passo — publicar o Dataroom da Fazenda Caracol/MS

Tudo pela web, sem instalar nada no computador. Leva uns 15-20 minutos na
primeira vez.

Tudo que você precisa está nesta pasta (`dataroom-fazenda-caracol`).

---

## O que você vai criar (grátis, sem cartão de crédito)

1. Uma conta no **GitHub** (se ainda não tiver) — é onde os arquivos do
   app ficam guardados.
2. Uma conta no **Streamlit Community Cloud** — é quem efetivamente
   "liga" o app e gera o link que você vai mandar pros investidores.

---

## Parte 1 — Criar o repositório no GitHub

1. Entre em [github.com](https://github.com) e crie uma conta (ou faça
   login se já tiver).
2. No canto superior direito, clique no **+** e depois em **"New
   repository"**.
3. Preencha:
   - **Repository name**: `dataroom-fazenda-caracol` (ou o nome que
     preferir, sem espaços).
   - Marque **Private** (importante — o repositório vai guardar e-mails e
     senhas com hash dos usuários cadastrados).
   - **Não** marque "Add a README file" nem mais nada — deixe tudo
     desmarcado (a pasta que você já tem já vem com tudo isso).
4. Clique em **Create repository**.

---

## Parte 2 — Subir os arquivos, direto pelo navegador

Depois de criar o repositório, o GitHub mostra uma página de "primeiros
passos" (Quick setup). Nela tem um link escrito algo como **"uploading an
existing file"** — clique nele. (Se você já saiu dessa página, dá pra
chegar lá de novo clicando em **Add file > Upload files**, no botão verde
**Code** da página principal do repositório.)

1. No computador, abra a pasta `dataroom-fazenda-caracol`.

2. **Importante**: primeiro ative a exibição de itens ocultos, senão o
   arquivo `.gitignore` fica de fora. No Explorador de Arquivos: aba
   **Exibir** → marque **Itens ocultos**.

3. Dentro da pasta `dataroom-fazenda-caracol`, aperte **Ctrl+A** pra
   selecionar **tudo que está dentro dela** (não a pasta em si — o que
   está dentro: `app.py`, `github_storage.py`, `requirements.txt`,
   `config.yaml`, `README.md`, `PASSO-A-PASSO.md`, `secrets_exemplo.toml`,
   `.gitignore`, e as pastas `assets` e `data`).

4. Arraste tudo que está selecionado direto para a área de upload do
   GitHub (a caixa pontilhada escrito algo como "Drag files here to add
   them to your repository"). O navegador pode demorar alguns segundos
   processando — são cerca de 20 arquivos, incluindo as 13 fotos.

5. Quando a lista de arquivos aparecer (confira se veio tudo, inclusive
   as pastas `assets/` e `data/` abertas com os arquivos dentro), desça
   até o final da página, escreva uma mensagem tipo `Primeira versão do
   dataroom` na caixa "Commit changes", e clique no botão verde **Commit
   changes**.

Pronto — os arquivos já estão no repositório. Dá pra conferir clicando de
volta na aba **Code** do repositório.

---

## Parte 3 — Publicar no Streamlit Community Cloud

1. Entre em [share.streamlit.io](https://share.streamlit.io) e faça login
   **com a mesma conta GitHub**.
2. Clique em **Create app** (ou **New app**).
3. Escolha **"Deploy a public app from GitHub"** (o app fica com login
   protegido mesmo sendo "público" no sentido do Streamlit — "público"
   aqui só quer dizer que não tem a autenticação extra do próprio
   Streamlit Cloud na frente, que é paga).
4. Preencha:
   - **Repository**: `seu-usuario/dataroom-fazenda-caracol`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Em **App URL**, você pode escolher um endereço customizado (ex:
   `darkpool-fazenda-caracol`), que vira
   `https://darkpool-fazenda-caracol.streamlit.app`.
6. Clique em **Deploy**. Vai aparecer uma tela de log instalando as
   dependências — leva uns 2-5 minutos na primeira vez.

Se der erro na instalação, geralmente é algum pacote no
`requirements.txt` — me chame que eu ajudo a resolver.

---

## Parte 4 — Ativar a persistência (pra não perder cadastros e log)

Sem esse passo o app já funciona, só que se o Streamlit reiniciar o
container, usuários cadastrados e o log de acesso voltam pro que estava
no último commit. Com esse passo, tudo fica salvo automaticamente no
próprio repositório GitHub.

1. Gere um token no GitHub:
   - No navegador, vá em
     [github.com/settings/tokens?type=beta](https://github.com/settings/tokens?type=beta)
     (Fine-grained tokens).
   - Clique em **Generate new token**.
   - **Token name**: `dataroom-fazenda-caracol`.
   - **Expiration**: escolha um prazo longo (ex: 1 ano) ou "No expiration".
   - **Repository access**: **Only select repositories** → escolha
     `dataroom-fazenda-caracol`.
   - **Permissions**: abra **Repository permissions** → **Contents** →
     mude de "No access" pra **"Read and write"**.
   - Clique em **Generate token** lá embaixo.
   - **Copie o token que aparecer** (começa com `github_pat_...`) — só
     aparece essa vez, se perder tem que gerar outro.

2. Volte pro app no Streamlit Cloud: clique nos **três pontinhos** (⋮) do
   seu app → **Settings** → aba **Secrets**.

3. Cole o seguinte, trocando os valores pelos seus:

   ```toml
   [github]
   token = "cole_o_token_aqui"
   repo = "seu-usuario/dataroom-fazenda-caracol"
   branch = "main"
   ```

4. Clique em **Save**. O app reinicia sozinho e já passa a usar o
   GitHub pra guardar os dados.

---

## Parte 5 — Testar

1. Abra o link do app (`https://seu-app.streamlit.app`).
2. Entre com:
   - **Usuário**: `darkpool`
   - **Senha**: `dark123@`
3. No menu lateral, abra **"Alterar Senha"** e troque por uma senha sua
   (a senha acima ficou visível nesta conversa, então vale trocar).
4. Clique em **Administração** (só aparece pro usuário master) → aba
   **Usuários** → cadastre um usuário de teste pra confirmar que
   funciona → depois pode remover esse usuário de teste.
5. Confira a aba **Log de Acessos** — deve aparecer o seu login e o do
   usuário de teste.

Se tudo isso funcionou, está pronto.

---

## Parte 6 — Quando o KML da fazenda chegar

1. Converta o KML/KMZ para GeoJSON (ex.: em [geojson.io](https://geojson.io),
   arrastando o arquivo e exportando como GeoJSON, ou com a ferramenta
   `kml2geojson`).
2. No repositório do GitHub, entre na pasta `data`, clique em **Add file
   > Upload files** e suba o arquivo salvando com o nome exato
   `fazenda_caracol.geojson`.
3. Commit. O Streamlit Cloud detecta a mudança e, em segundos, a seção
   "Mapa" do app passa a mostrar o contorno real da fazenda sobre imagem
   de satélite — sem precisar mexer em mais nada.

---

## Parte 7 — Compartilhar e manter (sempre pela web)

- Mande o link do app pra quem deve ter acesso, junto com o usuário/senha
  que você cadastrar pra cada pessoa pelo painel de Administração (não
  precisa mandar a senha do master pra ninguém).
- **Pra editar um arquivo de texto** (ex: um ajuste pontual no `app.py`):
  no repositório, abra o arquivo, clique no ícone de lápis (Edit), altere,
  e desça pra commitar direto no site do GitHub. O Streamlit Cloud
  detecta o commit e atualiza o app sozinho em segundos.
- **Pra trocar/adicionar fotos ou substituir vários arquivos de uma vez**:
  entre na pasta correspondente do repositório (ex: `assets`), clique em
  **Add file > Upload files**, e arraste os arquivos novos — se tiverem o
  mesmo nome de um arquivo já existente, o GitHub substitui; se o nome for
  novo, ele adiciona. Sempre me peça pra te mandar os arquivos já
  prontos/ajustados, se a mudança for na lógica do app (`app.py`,
  `github_storage.py`).

---

## Se algo travar

- **"Usuário ou senha incorretos" mesmo com a senha certa**: confira se
  não tem espaço em branco sobrando no campo de usuário.
- **App não sobe / fica em loop instalando**: geralmente é versão de
  pacote no `requirements.txt` incompatível — me manda um print do erro.
- **Cadastrei um usuário mas sumiu depois de um tempo**: sinal de que a
  Parte 4 (secret do GitHub) não foi configurada ou o token não tem
  permissão de escrita — revise o passo 1 da Parte 4.
- **Upload no GitHub travou ou não pegou todos os arquivos**: confira se
  as pastas `assets` e `data` realmente foram parar dentro do repositório
  (abra cada uma lá no site pra ver se tem conteúdo). Se faltou alguma,
  repita o upload só dela.
