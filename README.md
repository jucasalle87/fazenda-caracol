# Dataroom — Fazenda 400 ha, Caracol/MS

App em Streamlit com login por usuário/senha, painel master para cadastrar/remover
usuários e log de acessos (quem entrou e em que horário). Mesmo padrão de
autenticação, persistência e visual usado nos outros portais DarkPool (ex.:
Resort em Porto Seguro, Fazenda Barra II).

## 1. Credenciais do master (DarkPool)

- **Usuário:** `darkpool`
- **Senha:** `dark123@`

Troque essa senha assim que possível pelo menu lateral **"Alterar Senha"**,
depois de logar (a senha acima ficou visível nesta conversa/arquivo, então
vale trocar antes de dar acesso a qualquer pessoa de fora).

## 2. Conteúdo já incluído

- **13 fotos** da propriedade (`assets/01.jpg` a `assets/13.jpg`), com
  legendas descritivas na galeria.
- **Descrição, números e diferenciais** extraídos do resumo da fazenda:
  área total (400 ha), área agricultável (280 ha, com potencial de abertura
  de mais 20 ha), topografia de planalto, região de forte vocação agrícola,
  município de Caracol/MS, distância de Bela Vista (70 km) e da Rota
  Bioceânica (10 km), e valor (R$ 22.000.000,00).

## 3. O que falta completar

- **Mapa da propriedade**: por enquanto a seção "Mapa" mostra apenas a
  localização aproximada do município de Caracol/MS, com um aviso de que o
  perímetro exato ainda não foi recebido. Assim que o **arquivo KML/KMZ**
  da fazenda for enviado:
  1. Converta o KML para GeoJSON (ex.: [kml2geojson](https://github.com/mrcagney/kml2geojson),
     ou abrindo o KML no [geojson.io](https://geojson.io) e exportando).
  2. Salve o resultado como `data/fazenda_caracol.geojson` (mesma pasta
     deste README).
  3. Pronto — o app detecta o arquivo automaticamente e passa a exibir o
     mapa com o perímetro real da fazenda sobre imagem de satélite, sem
     precisar alterar nenhuma linha de código.
- **Vídeos** (se houver): pode-se adicionar uma seção de vídeos do YouTube
  seguindo o mesmo padrão dos outros portais DarkPool, quando o material
  estiver disponível.
- **Documentos** (matrícula, CAR, ITR etc.): quando disponíveis, podem ser
  adicionados como imagens em `assets/pdf_pages/` e exibidos em uma nova
  seção "Documentos", como no portal da Fazenda Barra II.

## 4. Como publicar (GitHub + Streamlit Community Cloud)

1. Crie um repositório novo no GitHub (recomendado: **privado**, já que o
   `config.yaml` guarda e-mails e senhas com hash dos usuários cadastrados).
2. Suba todo o conteúdo desta pasta (`app.py`, `github_storage.py`,
   `requirements.txt`, `config.yaml`, `assets/`, `data/`) para esse
   repositório.
3. Acesse [share.streamlit.io](https://share.streamlit.io), conecte sua conta
   GitHub e clique em "New app".
4. Selecione o repositório, branch `main` e o arquivo `app.py`.
5. **Configure o secret do GitHub** (veja seção 5 abaixo) — sem isso o app
   funciona, mas perde usuários/log a cada restart do container.
6. Deploy. Em alguns minutos o app estará no ar com uma URL tipo
   `https://seu-app.streamlit.app`.
7. Compartilhe essa URL só com quem deve ter acesso — o login protege o
   conteúdo, mas a própria URL não é secreta.

## 5. Cadastrando e removendo usuários

Logado como `darkpool` (master), aparece no menu lateral a opção
**"Administração"**, com duas abas:

- **Usuários** — formulário para cadastrar um novo login (usuário, nome,
  e-mail, senha provisória) e lista de quem tem acesso, com botão para
  remover.
- **Log de Acessos** — tabela com todo login realizado (usuário, nome,
  e-mail, data/hora em horário de Brasília), com botão para baixar em CSV.

Cada usuário cadastrado pode trocar a própria senha pelo menu lateral.

## 6. Persistência via GitHub (resolve o problema de perder dados)

O Streamlit Community Cloud roda o app num container que pode ser reiniciado
do zero (a partir do que está no GitHub) depois de um novo `git push` ou de
um período longo sem uso. Se `config.yaml` (usuários) e `data/access_log.csv`
(log) só existirem no disco desse container, tudo que foi cadastrado depois
do último commit se perde.

Pra resolver isso, o app já vem preparado para sincronizar os dois arquivos
com o próprio repositório GitHub via API (`github_storage.py`) — o mesmo
mecanismo usado nos outros portais DarkPool. Com isso configurado, toda vez
que o master cadastra/remove um usuário, ou que alguém faz login, o arquivo
correspondente é atualizado tanto localmente quanto no GitHub — e mesmo que
o container reinicie, o app busca a versão mais recente do GitHub assim que
sobe de novo.

**Como ativar:**

1. Gere um token no GitHub: `Settings da conta > Developer settings >
   Personal access tokens > Fine-grained tokens > Generate new token`.
   Dê acesso só a este repositório, com permissão **Contents: Read and
   write**.
2. No Streamlit Cloud: `Manage app > Settings > Secrets`, cole:

   ```toml
   [github]
   token = "seu-token-aqui"
   repo = "seu-usuario/nome-do-repositorio"
   branch = "main"
   ```

   (Veja `secrets_exemplo.toml` nesta pasta.) Rodando local, o mesmo
   conteúdo vai em `.streamlit/secrets.toml` (esse arquivo não deve ir pro
   GitHub — já está no `.gitignore`).
3. Pronto. Sem esse secret, o app continua funcionando normalmente (fallback
   local), só sem sobreviver a restarts — então vale configurar antes de
   colocar em uso real com investidores.

## 7. Estrutura de arquivos

```
app.py                        # aplicação Streamlit
github_storage.py             # sincronização de config.yaml/log com o GitHub
requirements.txt              # dependências
config.yaml                   # usuários (senhas com hash) + config do cookie de sessão
secrets_exemplo.toml          # modelo do secret do GitHub (não é lido pelo app)
assets/
  darkpool_logo.png           # logo
  01.jpg ... 13.jpg           # fotos da fazenda
data/
  access_log.csv              # cópia local do log de acessos (espelha o GitHub)
  fazenda_caracol.geojson     # (a adicionar) perímetro da fazenda, convertido do KML
```
