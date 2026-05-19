# Guia do site — Douglas N. Schimidt
## Tudo que você precisa saber para colocar e manter o site no ar

---

## Como o sistema funciona (visão geral)

```
Você joga foto no Google Drive
          ↓
Todo dia às 9h (ou quando você pedir),
o GitHub lê suas fotos automaticamente
          ↓
O site atualiza sozinho em ~1 minuto
```

Você só precisa mexer em **uma coisa**: o Google Drive.
O resto é automático.

---

## PARTE 1 — Subir o site pela primeira vez

### Passo 1 — Criar conta no GitHub
> GitHub é onde os arquivos do seu site ficam guardados.
> Pense nele como uma gaveta organizada na internet.

1. Acesse **github.com** e crie uma conta gratuita
2. Clique em **"New repository"** (botão verde)
3. Nome: `meu-portfolio`
4. Marque **"Public"** → clique **"Create repository"**
5. Na próxima tela, clique em **"uploading an existing file"**
6. Arraste **todos os arquivos desta pasta** (incluindo a pasta `.github/`)
7. Clique **"Commit changes"** — feito!

> ⚠️ A pasta `.github/` pode estar oculta no seu computador.
> No Mac: pressione **Cmd + Shift + .** para mostrar arquivos ocultos.
> No Windows: clique em "Ver" → marque "Itens ocultos".

### Passo 2 — Publicar no Netlify
> Netlify é o serviço que coloca o site no ar a partir dos seus arquivos.

1. Acesse **netlify.com** → crie conta com o GitHub ("Sign up with GitHub")
2. Clique em **"Add new site"** → **"Import an existing project"**
3. Escolha **"GitHub"** e selecione o repositório `meu-portfolio`
4. Deixe tudo padrão → clique **"Deploy site"**
5. Aguarde ~1 minuto. Seu site estará no ar.

### Passo 3 — Conectar o domínio douglasnschimidt.com

**No Netlify:**
1. **Site Settings → Domain management → Add custom domain**
2. Digite `douglasnschimidt.com` → confirme
3. Anote os dados de DNS que aparecer

**Na GoDaddy:**
1. Acesse **godaddy.com → Meus Produtos → Domínios → douglasnschimidt.com**
2. Clique em **"Gerenciar DNS"**
3. Edite o registro **"A"**: aponte para `75.2.60.5`
4. Adicione **"CNAME"**: Nome `www` / Valor `[seusite].netlify.app`
5. Salve — aguarde até 1h para funcionar

---

## PARTE 2 — Configurar a chave do Google Drive (uma vez só)

> Esta etapa é o que permite o script ler suas fotos do Drive.
> Parece complicado mas são cliques — sem digitar código.

### 2.1 — Criar uma chave de acesso no Google

1. Acesse **console.cloud.google.com** (entre com sua conta Google)
2. No topo, clique em **"Selecionar projeto"** → **"Novo projeto"**
3. Nome: `Site Douglas` → clique **"Criar"**
4. No menu lateral, vá em **"APIs e serviços" → "Biblioteca"**
5. Pesquise `Google Drive API` → clique nela → clique **"Ativar"**
6. Vá em **"APIs e serviços" → "Credenciais"**
7. Clique em **"Criar credenciais" → "Chave de API"**
8. Uma chave vai aparecer — **copie ela** (parece com `AIzaSy...`)
9. Clique em **"Restringir chave"** → em "Restrições de API" selecione `Google Drive API` → salve

### 2.2 — Tornar as pastas do Drive públicas

> O script precisa que suas pastas sejam visíveis para ele acessar.
> Não se preocupe: as fotos só aparecem no *seu* site.

1. Acesse **drive.google.com**
2. Abra a pasta **`douglasnschimidt-site`** (que já está criada)
3. Clique com o botão direito em cada pasta (terra, agua, fogo, ar, vida)
4. Clique em **"Compartilhar"**
5. Em "Acesso geral", mude de "Restrito" para **"Qualquer pessoa com o link"**
6. Permissão: **"Leitor"** → clique **"Concluído"**
7. Repita para as 5 pastas

### 2.3 — Colocar a chave no GitHub

> O GitHub guarda a chave em segredo — nem você vai ver ela de novo.

1. Acesse seu repositório no GitHub
2. Clique em **"Settings"** (engrenagem, no topo)
3. No menu lateral, clique em **"Secrets and variables" → "Actions"**
4. Clique em **"New repository secret"**
5. Name: `GOOGLE_API_KEY`
6. Secret: cole a chave que você copiou (`AIzaSy...`)
7. Clique **"Add secret"**

✅ Pronto. O sistema agora consegue ler suas fotos.

---

## PARTE 3 — Como adicionar fotos (o dia a dia)

Esta é a parte mais simples. Você faz isso para sempre:

1. Abra o **Google Drive**
2. Navegue até **`douglasnschimidt-site`**
3. Abra a pasta da categoria que quer atualizar (ex: `agua`)
4. Arraste suas fotos para dentro da pasta
5. **Pronto.** Até às 9h do dia seguinte, o site atualiza sozinho.

**Quer atualizar agora, sem esperar?**
1. Acesse seu repositório no GitHub
2. Clique em **"Actions"** (no topo)
3. Clique em **"Atualizar galeria via Google Drive"**
4. Clique em **"Run workflow" → "Run workflow"**
5. Aguarde ~2 minutos

---

## PARTE 4 — Dicas para as fotos

| O que | Recomendado |
|---|---|
| Tamanho do arquivo | Até 8MB por foto |
| Formato | JPEG (`.jpg`) ou PNG (`.png`) |
| Nome do arquivo | Use o nome que quer que apareça no site. Ex: `ondas-maldivas.jpg` → aparece como "Ondas Maldivas" |
| Traços e underlines | Ambos funcionam: `minha-foto.jpg` ou `minha_foto.jpg` |
| Dimensões mínimas | 1200px no lado maior |

---

## PARTE 5 — Editar textos do site

Os textos (bio, contato, loja) ficam nos arquivos HTML.
Você pode editá-los direto no GitHub:

1. Acesse seu repositório
2. Clique no arquivo que quer editar (ex: `expedicoes.html`)
3. Clique no ícone de lápis (canto superior direito)
4. Edite o texto
5. Clique **"Commit changes"**
6. O site atualiza em ~30 segundos

Cada parte editável tem um comentário em português explicando o que é.

---

## PARTE 6 — Se algo der errado

**O site não atualizou as fotos:**
→ Verifique se as pastas do Drive estão com acesso "Qualquer pessoa com o link"
→ Verifique se a chave `GOOGLE_API_KEY` está salva no GitHub (Settings → Secrets)
→ No GitHub, vá em "Actions" e veja se há algum erro em vermelho

**O site sumiu:**
→ Acesse o Netlify — provavelmente é só re-publicar (botão "Trigger deploy")

**Esqueceu como fazer alguma coisa:**
→ Traga este guia para o chat e peça ajuda — com o guia em mãos fica fácil retomar.

---

*Site de Douglas N. Schimidt — sistema de atualização via Google Drive*
