#!/usr/bin/env python3
"""
atualizar-site.py  —  versão final com loja digital + física
────────────────────────────────────────────────────────────────────
O que este script faz (em português simples):

  1. Lê sua planilha "douglasnschimidt-fotos" no Google Sheets
  2. Lê as 5 pastas do Google Drive (terra, agua, fogo, ar, vida)
  3. Gera as 5 páginas de categoria do portfólio
  4. Gera a loja em duas seções separadas:
       - "Download digital"  → botão vai para o Gumroad
                               (coluna na_loja = "digital")
       - "Impressão física"  → seletor de tamanho/papel/moldura
                               + botão vai para o Shopify
                               (coluna na_loja = "fisica")

  COLUNA na_loja na planilha — valores possíveis:
     nao      → só no portfólio, sem botão de venda
     digital  → venda de download (Gumroad)
     fisica   → venda de impressão (Shopify)

  Você nunca precisa mexer neste arquivo.
  Tudo que você controla fica na planilha e nas pastas do Drive.
────────────────────────────────────────────────────────────────────
"""

import os, csv, io, requests

# ── IDs fixos — não mexa aqui ────────────────────────────────────
PLANILHA_ID = "1DnSWBiIMxd-BqfgUQkcHa-58IeZ85hcquxwGlNvDC80"

PASTAS = {
    "terra": "1tHbeHivJircA47WZnzAK4cmR2iogUWd1",
    "agua":  "1V14qDp6lnMaC1OtEzh6zcm0Gqnq3SfYU",
    "fogo":  "1l8x_isgLIGvE8sJ6HvhDWEyb9loACKQl",
    "ar":    "15gd7fxCIKiW4UqOLpNod7d_R0KjqC99R",
    "vida":  "1P2eNUhjzhITeJ2XwUhdop6xHxVubRvzu",
}

INFO_CATEGORIA = {
    "terra": {"nome": "Terra", "sub": "Onde tudo começa."},
    "agua":  {"nome": "Água",  "sub": "Meu habitat."},
    "fogo":  {"nome": "Fogo",  "sub": "Impossível ignorar."},
    "ar":    {"nome": "Ar",    "sub": "O que você não vê."},
    "vida":  {"nome": "Vida",  "sub": "Seja cotidiana ou selvagem."},
}

API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# ── Leitura de dados ─────────────────────────────────────────────

def ler_planilha():
    """
    Colunas esperadas na planilha:
      arquivo | categoria | titulo | descricao | na_loja | preco_digital | link_gumroad | link_shopify
    """
    url  = f"https://docs.google.com/spreadsheets/d/{PLANILHA_ID}/export"
    resp = requests.get(url, params={"format": "csv", "key": API_KEY})
    if not resp.ok:
        print(f"  aviso: nao consegui ler a planilha (codigo {resp.status_code})")
        return {}
    dados = {}
    for linha in csv.DictReader(io.StringIO(resp.text)):
        arq = linha.get("arquivo", "").strip()
        if arq:
            dados[arq] = {
                "titulo":        linha.get("titulo",        "").strip(),
                "descricao":     linha.get("descricao",     "").strip(),
                "na_loja":       linha.get("na_loja",       "nao").strip().lower(),
                "preco_digital": linha.get("preco_digital", "29").strip(),
                "link_gumroad":  linha.get("link_gumroad",  "").strip(),
                "link_shopify":  linha.get("link_shopify",  "").strip(),
            }
    print(f"  planilha: {len(dados)} foto(s) com contexto")
    return dados


def listar_drive(pasta_id):
    r = requests.get("https://www.googleapis.com/drive/v3/files", params={
        "q": f"'{pasta_id}' in parents and trashed=false and (mimeType='image/jpeg' or mimeType='image/png')",
        "fields": "files(id,name)", "orderBy": "name", "key": API_KEY,
    })
    return r.json().get("files", []) if r.ok else []


def thumb(fid):  return f"https://drive.google.com/thumbnail?id={fid}&sz=w800"
def grande(fid): return f"https://drive.google.com/thumbnail?id={fid}&sz=w1600"
def titulo_fallback(name): return name.rsplit(".",1)[0].replace("-"," ").replace("_"," ").title()

# ── Partes HTML reutilizáveis ─────────────────────────────────────

FONTES = '<link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin /><link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Caveat:wght@400;600&family=Karla:wght@300;400&display=swap" rel="stylesheet" />'

def nav_html(ativa_portfolio=False, ativa_loja=False):
    p = ' class="ativa"' if ativa_portfolio else ""
    l = ' class="ativa"' if ativa_loja      else ""
    return f"""  <nav id="nav">
    <a href="index.html" class="nav-logo">Douglas N. Schimidt<small>adventure photography</small></a>
    <button class="nav-toggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="nav-links" id="navLinks">
      <li><a href="portfolio.html"{p} onclick="fecharMenu()">Portfólio</a></li>
      <li><a href="loja.html"{l} onclick="fecharMenu()">Loja</a></li>
      <li><a href="expedicoes.html" onclick="fecharMenu()">Expedições</a></li>
      <li><a href="contato.html"    onclick="fecharMenu()">Contato</a></li>
    </ul>
  </nav>"""

RODAPE = """  <footer>
    <span class="footer-logo">Douglas N. Schimidt</span>
    <span>© 2025 — atualizado via Google Drive + Sheets</span>
  </footer>"""

JS_NAV = """    const _nav = document.getElementById('nav');
    window.addEventListener('scroll', () => _nav.classList.toggle('rolada', window.scrollY > 50));
    document.getElementById('navToggle').addEventListener('click', () => document.getElementById('navLinks').classList.toggle('aberto'));
    function fecharMenu() { document.getElementById('navLinks').classList.remove('aberto'); }
    document.querySelectorAll('.reveal').forEach(el => {
      new IntersectionObserver(([e],o) => { if(e.isIntersecting){ el.classList.add('visivel'); o.unobserve(el); } },{threshold:.08}).observe(el);
    });"""

# ── Gerador de categoria ──────────────────────────────────────────

def gerar_categoria(slug, fotos, ctx):
    info = INFO_CATEGORIA[slug]
    nome, sub = info["nome"], info["sub"]
    qtd = len(fotos)

    itens = []
    for f in fotos:
        c    = ctx.get(f["name"], {})
        tit  = c.get("titulo")    or titulo_fallback(f["name"])
        desc = c.get("descricao") or ""
        d_at = f' data-descricao="{desc}"' if desc else ""
        d_hv = f'<span class="foto-desc-hover">{desc}</span>' if desc else ""
        itens.append(f"""    <div class="foto-item" data-titulo="{tit}"{d_at} data-src="{grande(f['id'])}">
      <img src="{thumb(f['id'])}" alt="{tit}" loading="lazy" />
      <div class="foto-info">
        <span class="foto-titulo-hover">{tit}</span>{d_hv}
      </div>
    </div>""")

    grid = "\n".join(itens) if itens else '    <div class="vazio"><p>Nenhuma foto ainda.</p></div>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>{nome} — Douglas N. Schimidt</title>
  {FONTES}
  <link rel="stylesheet" href="estilo.css" />
  <style>
    .cat-topo{{padding:9rem 3rem 3rem;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:1rem;border-bottom:1px solid var(--borda);margin-bottom:3px}}
    .cat-label{{font-family:var(--detalhe);font-size:.85rem;color:var(--destaque);letter-spacing:.25em;text-transform:uppercase;margin-bottom:.4rem}}
    .cat-titulo{{font-family:var(--titulo);font-size:clamp(2.5rem,6vw,4rem);color:var(--texto);line-height:1}}
    .cat-subtitulo{{font-family:var(--detalhe);font-size:clamp(1rem,2.5vw,1.4rem);color:var(--texto2);font-style:italic;border-left:2px solid var(--destaque);padding-left:1rem}}
    .cat-voltar{{font-family:var(--detalhe);font-size:.9rem;color:var(--texto2);letter-spacing:.08em;display:flex;align-items:center;gap:.5rem;transition:color var(--transicao)}}
    .cat-voltar:hover{{color:var(--destaque)}}
    .cat-qtd{{font-family:var(--detalhe);font-size:.8rem;color:var(--texto2);opacity:.5;padding:0 3rem 1rem}}
    .fotos-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:3px;padding:0 3px}}
    .foto-item{{position:relative;aspect-ratio:4/3;overflow:hidden;cursor:pointer;background:#1a1a1a}}
    .foto-item img{{transition:transform .5s ease}}
    .foto-item:hover img{{transform:scale(1.05)}}
    .foto-info{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:1rem;background:rgba(13,13,13,0);transition:background var(--transicao)}}
    .foto-item:hover .foto-info{{background:rgba(13,13,13,.65)}}
    .foto-titulo-hover{{font-family:var(--detalhe);font-size:1rem;color:var(--texto);opacity:0;transform:translateY(6px);transition:all var(--transicao)}}
    .foto-desc-hover{{font-family:var(--corpo);font-size:.78rem;color:var(--texto2);opacity:0;transform:translateY(6px);transition:all var(--transicao) .04s;margin-top:.2rem;line-height:1.4}}
    .foto-item:hover .foto-titulo-hover,.foto-item:hover .foto-desc-hover{{opacity:1;transform:translateY(0)}}
    .lightbox{{display:none;position:fixed;inset:0;z-index:200;background:rgba(8,8,8,.97);align-items:center;justify-content:center;flex-direction:column;gap:1rem}}
    .lightbox.aberto{{display:flex}}
    .lightbox-img{{max-width:88vw;max-height:78vh;width:auto;height:auto;object-fit:contain}}
    .lightbox-info{{text-align:center;max-width:600px;padding:0 1rem}}
    .lightbox-titulo{{font-family:var(--titulo);font-size:1.2rem;color:var(--texto);margin-bottom:.3rem}}
    .lightbox-desc{{font-family:var(--detalhe);font-size:1rem;color:var(--texto2);font-style:italic}}
    .lightbox-fechar{{position:absolute;top:1.5rem;right:2rem;font-size:2rem;color:var(--texto2);cursor:pointer;background:none;border:none;font-family:var(--detalhe);line-height:1;transition:color var(--transicao)}}
    .lightbox-fechar:hover{{color:var(--destaque)}}
    .lightbox-nav{{position:absolute;top:40%;transform:translateY(-50%);background:none;border:none;color:var(--texto2);font-size:2.5rem;cursor:pointer;padding:1rem;transition:color var(--transicao);font-family:var(--detalhe)}}
    .lightbox-nav:hover{{color:var(--destaque)}}
    .lightbox-nav.anterior{{left:1rem}}.lightbox-nav.proximo{{right:1rem}}
    .vazio{{grid-column:1/-1;text-align:center;padding:4rem;color:#555;font-family:var(--detalhe);font-size:1.4rem}}
    .fim{{padding:4rem 3rem}}
    @media(max-width:600px){{.cat-topo{{padding:7rem 1.5rem 2rem}}.fotos-grid{{grid-template-columns:repeat(2,1fr)}}}}
  </style>
</head>
<body>
{nav_html(ativa_portfolio=True)}
  <div class="cat-topo reveal">
    <div><p class="cat-label">portfólio</p><h1 class="cat-titulo">{nome}</h1></div>
    <p class="cat-subtitulo">{sub}</p>
    <a href="portfolio.html" class="cat-voltar">← voltar</a>
  </div>
  <p class="cat-qtd">{qtd} foto{"s" if qtd!=1 else ""}</p>
  <main class="fotos-grid reveal" id="galeria">
{grid}
  </main>
  <div class="fim"></div>
  <div class="lightbox" id="lightbox">
    <button class="lightbox-fechar" id="lbFechar">×</button>
    <button class="lightbox-nav anterior" id="lbAnt">‹</button>
    <img class="lightbox-img" src="" alt="" id="lbImg" />
    <div class="lightbox-info">
      <p class="lightbox-titulo" id="lbTit"></p>
      <p class="lightbox-desc"   id="lbDsc"></p>
    </div>
    <button class="lightbox-nav proximo" id="lbPro">›</button>
  </div>
{RODAPE}
  <script>
    {JS_NAV}
    const its=Array.from(document.querySelectorAll('.foto-item'));
    const lb=document.getElementById('lightbox'),lbImg=document.getElementById('lbImg'),lbTit=document.getElementById('lbTit'),lbDsc=document.getElementById('lbDsc');
    let cur=0;
    function abrir(i){{cur=i;const e=its[i];lbImg.src=e.dataset.src;lbImg.alt=e.dataset.titulo;lbTit.textContent=e.dataset.titulo||'';lbDsc.textContent=e.dataset.descricao||'';lb.classList.add('aberto');document.body.style.overflow='hidden';}}
    function fechar(){{lb.classList.remove('aberto');document.body.style.overflow='';}}
    its.forEach((e,i)=>e.addEventListener('click',()=>abrir(i)));
    document.getElementById('lbFechar').addEventListener('click',fechar);
    document.getElementById('lbAnt').addEventListener('click',()=>abrir((cur-1+its.length)%its.length));
    document.getElementById('lbPro').addEventListener('click',()=>abrir((cur+1)%its.length));
    lb.addEventListener('click',e=>{{if(e.target===lb)fechar();}});
    document.addEventListener('keydown',e=>{{if(e.key==='Escape')fechar();if(e.key==='ArrowLeft')document.getElementById('lbAnt').click();if(e.key==='ArrowRight')document.getElementById('lbPro').click();}});
  </script>
</body>
</html>"""


# ── Gerador de loja ───────────────────────────────────────────────

def card_digital(f, c):
    tit   = c.get("titulo")        or titulo_fallback(f["name"])
    desc  = c.get("descricao")     or "Download digital em alta resolução."
    preco = c.get("preco_digital") or "29"
    link  = c.get("link_gumroad")  or "#"
    return f"""      <div class="produto-card">
        <div class="produto-foto"><img src="{thumb(f['id'])}" alt="{tit}" loading="lazy" /></div>
        <div class="produto-info">
          <span class="produto-badge digital">Download</span>
          <h3 class="produto-nome">{tit}</h3>
          <p class="produto-desc">{desc}</p>
          <p class="produto-detalhe">Arquivo JPEG em alta resolução — fundo de tela, impressão própria, arte.</p>
          <div class="produto-rodape">
            <span class="produto-preco">R$ {preco}</span>
            <a href="{link}" target="_blank" rel="noopener"><button class="produto-btn">Comprar</button></a>
          </div>
        </div>
      </div>"""


def card_fisica(f, c):
    """
    Card com seletores de tamanho, papel e moldura.
    O preço é calculado dinamicamente em JavaScript com base
    na tabela de preços definida abaixo em TABELA_PRECOS.
    Ao clicar em "Encomendar", o cliente é redirecionado para
    o Shopify com os parâmetros da variante já selecionados.
    """
    tit  = c.get("titulo")    or titulo_fallback(f["name"])
    desc = c.get("descricao") or "Impressão artística sob encomenda."
    link = c.get("link_shopify") or "#"
    # ID único para este card (baseado no nome do arquivo, sem extensão)
    cid  = f["name"].rsplit(".",1)[0].replace(" ","_").replace("-","_")

    return f"""      <div class="produto-card fisica" id="card_{cid}">
        <div class="produto-foto"><img src="{thumb(f['id'])}" alt="{tit}" loading="lazy" /></div>
        <div class="produto-info">
          <span class="produto-badge fisica">Impressão</span>
          <h3 class="produto-nome">{tit}</h3>
          <p class="produto-desc">{desc}</p>

          <div class="opcoes">
            <div class="opcao-grupo">
              <label>Tamanho</label>
              <select class="sel-tamanho" onchange="calcPreco('{cid}')">
                <option value="20x30">20 × 30 cm</option>
                <option value="30x40">30 × 40 cm</option>
                <option value="40x60" selected>40 × 60 cm</option>
                <option value="50x70">50 × 70 cm</option>
              </select>
            </div>
            <div class="opcao-grupo">
              <label>Papel</label>
              <select class="sel-papel" onchange="calcPreco('{cid}')">
                <option value="fosco">Fosco</option>
                <option value="brilhante">Brilhante</option>
                <option value="fineart" selected>Fine Art</option>
              </select>
            </div>
            <div class="opcao-grupo">
              <label>Moldura</label>
              <select class="sel-moldura" onchange="calcPreco('{cid}')">
                <option value="sem" selected>Sem moldura</option>
                <option value="preta">Preta</option>
                <option value="branca">Branca</option>
                <option value="natural">Natural (madeira)</option>
              </select>
            </div>
          </div>

          <div class="produto-rodape">
            <span class="produto-preco" id="preco_{cid}">R$ —</span>
            <a href="{link}" id="btn_{cid}" target="_blank" rel="noopener">
              <button class="produto-btn" onclick="atualizarLink('{cid}','{link}')">Encomendar</button>
            </a>
          </div>
        </div>
      </div>"""


def gerar_loja(digitais, fisicas):
    tem_digital = bool(digitais)
    tem_fisica  = bool(fisicas)

    sec_digital = ""
    if tem_digital:
        cards = "\n".join(card_digital(f,c) for f,c in digitais)
        sec_digital = f"""  <section class="loja-secao reveal">
    <div class="secao-header">
      <h2 class="secao-titulo">Download Digital</h2>
      <p class="secao-desc">Arquivo em alta resolução entregue instantaneamente. Sem espera, sem frete.</p>
    </div>
    <div class="loja-grid">
{cards}
    </div>
  </section>"""

    sec_fisica = ""
    if tem_fisica:
        cards = "\n".join(card_fisica(f,c) for f,c in fisicas)
        sec_fisica = f"""  <section class="loja-secao reveal">
    <div class="secao-header">
      <h2 class="secao-titulo">Impressão Física</h2>
      <p class="secao-desc">Impressão profissional sob encomenda. Escolha o tamanho, papel e moldura. Produção e envio em até 10 dias úteis.</p>
    </div>
    <div class="loja-grid">
{cards}
    </div>
  </section>"""

    vazio = "" if (tem_digital or tem_fisica) else """  <div style="text-align:center;padding:6rem 2rem;color:#555;">
    <p style="font-family:'Caveat',cursive;font-size:1.4rem;">Nenhum produto na loja ainda.<br>Marque "digital" ou "fisica" na coluna na_loja da planilha.</p>
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>Loja — Douglas N. Schimidt</title>
  {FONTES}
  <link rel="stylesheet" href="estilo.css" />
  <style>
    .pagina-topo{{padding:10rem 3rem 1rem}}
    .pagina-label{{font-family:var(--detalhe);font-size:.9rem;color:var(--destaque);letter-spacing:.25em;text-transform:uppercase;margin-bottom:.5rem}}
    .pagina-titulo{{font-family:var(--titulo);font-size:clamp(2rem,5vw,3.5rem);color:var(--texto);line-height:1.1}}

    /* seções digital / física */
    .loja-secao{{padding:4rem 3rem}}
    .loja-secao+.loja-secao{{border-top:1px solid var(--borda)}}
    .secao-header{{margin-bottom:2.5rem}}
    .secao-titulo{{font-family:var(--titulo);font-size:clamp(1.4rem,3vw,2rem);color:var(--texto);margin-bottom:.4rem}}
    .secao-desc{{font-family:var(--detalhe);font-size:1rem;color:var(--texto2)}}

    /* grid de cards */
    .loja-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.5rem}}
    .produto-card{{background:#111;border:1px solid var(--borda);overflow:hidden;transition:border-color var(--transicao),transform var(--transicao)}}
    .produto-card:hover{{border-color:var(--destaque);transform:translateY(-3px)}}
    .produto-foto{{aspect-ratio:4/3;overflow:hidden;background:#1a1a1a}}
    .produto-foto img{{transition:transform .5s ease}}
    .produto-card:hover .produto-foto img{{transform:scale(1.04)}}
    .produto-info{{padding:1rem 1.2rem 1.3rem}}

    /* badge digital / física */
    .produto-badge{{display:inline-block;font-family:var(--detalhe);font-size:.75rem;letter-spacing:.12em;padding:.2rem .7rem;margin-bottom:.6rem;border-radius:2px}}
    .produto-badge.digital{{background:rgba(224,123,57,.15);color:var(--destaque);border:1px solid rgba(224,123,57,.3)}}
    .produto-badge.fisica{{background:rgba(255,255,255,.05);color:var(--texto2);border:1px solid var(--borda)}}

    .produto-nome{{font-family:var(--titulo);font-size:1rem;color:var(--texto);margin-bottom:.3rem}}
    .produto-desc{{font-size:.82rem;color:var(--texto2);line-height:1.6;margin-bottom:.5rem}}
    .produto-detalhe{{font-size:.78rem;color:var(--texto2);opacity:.6;margin-bottom:1rem;line-height:1.5}}
    .produto-rodape{{display:flex;align-items:center;justify-content:space-between;margin-top:1rem}}
    .produto-preco{{font-family:var(--detalhe);font-size:1.2rem;color:var(--destaque);font-weight:600}}
    .produto-btn{{font-family:var(--detalhe);font-size:.9rem;color:#0d0d0d;background:var(--destaque);border:none;padding:.45rem 1.1rem;cursor:pointer;transition:background var(--transicao);letter-spacing:.04em}}
    .produto-btn:hover{{background:var(--destaque2)}}

    /* seletores de variante (tamanho, papel, moldura) */
    .opcoes{{display:flex;flex-direction:column;gap:.6rem;margin:1rem 0}}
    .opcao-grupo{{display:flex;flex-direction:column;gap:.2rem}}
    .opcao-grupo label{{font-family:var(--detalhe);font-size:.8rem;color:var(--texto2);letter-spacing:.08em}}
    .opcao-grupo select{{background:#1a1a1a;border:1px solid var(--borda);color:var(--texto);font-family:var(--corpo);font-size:.88rem;padding:.4rem .6rem;outline:none;cursor:pointer;transition:border-color var(--transicao)}}
    .opcao-grupo select:focus{{border-color:var(--destaque)}}

    @media(max-width:600px){{
      .pagina-topo{{padding:8rem 1.5rem 1rem}}
      .loja-secao{{padding:3rem 1.5rem}}
      .loja-grid{{grid-template-columns:1fr}}
    }}
  </style>
</head>
<body>
{nav_html(ativa_loja=True)}
  <div class="pagina-topo reveal">
    <p class="pagina-label">loja</p>
    <h1 class="pagina-titulo">Loja</h1>
  </div>

{sec_digital}
{sec_fisica}
{vazio}

{RODAPE}
  <script>
    {JS_NAV}

    /*
      TABELA DE PREÇOS — impressão física
      ─────────────────────────────────────────────────────────
      Edite os valores abaixo para alterar os preços.
      Formato: PRECOS[tamanho][papel] = preço base em reais.
      O preço da moldura é somado por cima.
      ─────────────────────────────────────────────────────────
    */
    const PRECOS = {{
      "20x30": {{ fosco: 129, brilhante: 129, fineart: 189 }},
      "30x40": {{ fosco: 189, brilhante: 189, fineart: 269 }},
      "40x60": {{ fosco: 269, brilhante: 269, fineart: 389 }},
      "50x70": {{ fosco: 349, brilhante: 349, fineart: 499 }},
    }};

    /* Custo adicional por tipo de moldura */
    const MOLDURA = {{ sem: 0, preta: 120, branca: 120, natural: 150 }};

    function calcPreco(cid) {{
      const card    = document.getElementById('card_' + cid);
      const tam     = card.querySelector('.sel-tamanho').value;
      const papel   = card.querySelector('.sel-papel').value;
      const moldura = card.querySelector('.sel-moldura').value;
      const base    = PRECOS[tam]?.[papel] ?? 0;
      const extra   = MOLDURA[moldura] ?? 0;
      document.getElementById('preco_' + cid).textContent = 'R$ ' + (base + extra);
    }}

    function atualizarLink(cid, baseUrl) {{
      const card    = document.getElementById('card_' + cid);
      const tam     = card.querySelector('.sel-tamanho').value;
      const papel   = card.querySelector('.sel-papel').value;
      const moldura = card.querySelector('.sel-moldura').value;
      /* Passa as variantes como parâmetros na URL do Shopify */
      const url = baseUrl + '?tamanho=' + tam + '&papel=' + papel + '&moldura=' + moldura;
      document.getElementById('btn_' + cid).href = url;
    }}

    /* Calcula o preço inicial de todos os cards ao carregar a página */
    document.querySelectorAll('.produto-card.fisica').forEach(card => {{
      const cid = card.id.replace('card_', '');
      calcPreco(cid);
    }});
  </script>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────

def main():
    print("Atualizando site via Google Drive + Sheets...\n")
    if not API_KEY:
        print("ERRO: variavel GOOGLE_API_KEY nao encontrada.")
        return

    ctx = ler_planilha()
    digitais, fisicas = [], []

    for slug in PASTAS:
        info  = INFO_CATEGORIA[slug]
        print(f"{info['nome']}: lendo Drive...")
        fotos = listar_drive(PASTAS[slug])
        print(f"  {len(fotos)} foto(s)")

        for f in fotos:
            c = ctx.get(f["name"], {})
            tipo = c.get("na_loja", "nao")
            if tipo == "digital":
                digitais.append((f, c))
            elif tipo == "fisica":
                fisicas.append((f, c))

        with open(f"categoria-{slug}.html", "w", encoding="utf-8") as fh:
            fh.write(gerar_categoria(slug, fotos, ctx))
        print(f"  categoria-{slug}.html gerado\n")

    print(f"Loja: {len(digitais)} digital(is), {len(fisicas)} fisica(s)")
    with open("loja.html", "w", encoding="utf-8") as fh:
        fh.write(gerar_loja(digitais, fisicas))
    print("  loja.html gerada\n")
    print("Feito. Netlify publica em ~30s.")

if __name__ == "__main__":
    main()
