#!/usr/bin/env python3
"""
atualizar-site.py — versão 2.0 portfólio unificado
────────────────────────────────────────────────────────────────────
O que este script faz:

  1. Lê sua planilha "douglasnschimidt-fotos" no Google Sheets
  2. Lê as 5 pastas do Google Drive (terra, agua, fogo, ar, vida)
  3. Gera UMA única portfolio.html com todas as fotos em seções
     — filtros por categoria e por disponibilidade na loja
     — lightbox com descrição + opção de compra ao clicar
     — quem vem pelo link "Loja" chega com filtros de venda ativos
  4. Remove as páginas categoria-*.html antigas (não são mais usadas)
  5. Remove a loja.html antiga (a loja está integrada no portfólio)

  COLUNA na_loja na planilha — valores possíveis:
     nao      → só no portfólio, sem botão de venda
     digital  → venda de download (Gumroad)
     fisica   → venda de impressão (Shopify)
     ambos    → tanto digital quanto física

  Você nunca precisa mexer neste arquivo.
  Tudo que você controla fica na planilha e nas pastas do Drive.
────────────────────────────────────────────────────────────────────
"""

import os, csv, io, requests

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

def ler_planilha():
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

FONTES = '<link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin /><link href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Caveat:wght@400;600&family=Karla:wght@300;400&display=swap" rel="stylesheet" />'

def nav_html(ativa_portfolio=False, ativa_loja=False):
    p = ' class="ativa"' if ativa_portfolio else ""
    return f"""  <nav id="nav">
    <a href="index.html" class="nav-logo">Douglas N. Schimidt<small>adventure photography</small></a>
    <button class="nav-toggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="nav-links" id="navLinks">
      <li><a href="portfolio.html"{p} onclick="fecharMenu()">Portfólio</a></li>
      <li><a href="portfolio.html?loja=1" onclick="fecharMenu()">Loja</a></li>
      <li><a href="expedicoes.html" onclick="fecharMenu()">Expedições</a></li>
      <li><a href="contato.html" onclick="fecharMenu()">Contato</a></li>
    </ul>
  </nav>"""

RODAPE = """  <footer>
    <span class="footer-logo">Douglas N. Schimidt</span>
    <span>© 2025 — atualizado via Google Drive + Sheets</span>
  </footer>"""

def gerar_portfolio(todas_fotos):
    """
    todas_fotos: lista de dicts com keys:
      slug, nome_cat, foto_id, foto_nome, titulo, descricao,
      na_loja, preco_digital, link_gumroad, link_shopify
    """

    # Monta seções por categoria
    secoes_html = ""
    for slug, info in INFO_CATEGORIA.items():
        fotos_cat = [f for f in todas_fotos if f["slug"] == slug]
        if not fotos_cat:
            continue

        itens = []
        for i, f in enumerate(fotos_cat):
            na_loja       = f["na_loja"]
            tem_digital   = na_loja in ("digital", "ambos")
            tem_fisica    = na_loja in ("fisica",  "ambos")
            tem_venda     = tem_digital or tem_fisica
            tipo_venda    = ""
            if tem_digital and tem_fisica: tipo_venda = "digital fisica"
            elif tem_digital:              tipo_venda = "digital"
            elif tem_fisica:               tipo_venda = "fisica"

            preco_str = f"R$ {f['preco_digital']}" if tem_digital else ""

            # badges para filtro
            badge_html = ""
            if tem_digital:
                badge_html += '<span class="badge-tipo digital">Digital</span>'
            if tem_fisica:
                badge_html += '<span class="badge-tipo fisica">Impressão</span>'

            itens.append(f"""      <div class="foto-item"
        data-cat="{slug}"
        data-loja="{tipo_venda}"
        data-id="{f['foto_id']}"
        data-titulo="{f['titulo']}"
        data-descricao="{f['descricao']}"
        data-na-loja="{na_loja}"
        data-preco-digital="{f['preco_digital']}"
        data-link-gumroad="{f['link_gumroad']}"
        data-link-shopify="{f['link_shopify']}"
        onclick="abrirLightbox(this)">
        <img src="{thumb(f['foto_id'])}" alt="{f['titulo']}" loading="lazy" />
        <div class="foto-overlay">
          <span class="foto-titulo-hover">{f['titulo']}</span>
          <div class="foto-badges">{badge_html}</div>
        </div>
      </div>""")

        grid = "\n".join(itens)
        secoes_html += f"""
  <section class="categoria-secao" id="cat-{slug}" data-slug="{slug}">
    <div class="cat-header reveal">
      <div>
        <p class="cat-label">{slug}</p>
        <h2 class="cat-titulo">{info['nome']}</h2>
      </div>
      <p class="cat-subtitulo">{info['sub']}</p>
    </div>
    <div class="fotos-grid">
{grid}
    </div>
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>Portfólio — Douglas N. Schimidt</title>
  {FONTES}
  <link rel="stylesheet" href="estilo.css" />
  <style>
    /* ── Topo da página ── */
    .pagina-topo{{padding:9rem 3rem 2rem;border-bottom:1px solid var(--borda)}}
    .pagina-label{{font-family:var(--detalhe);font-size:.85rem;color:var(--destaque);letter-spacing:.25em;text-transform:uppercase;margin-bottom:.4rem}}
    .pagina-titulo{{font-family:var(--titulo);font-size:clamp(2.5rem,6vw,4rem);color:var(--texto);line-height:1;margin-bottom:2rem}}

    /* ── Filtros ── */
    .filtros{{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:1.5rem;margin-top:1.5rem}}
    .filtros-bloco{{display:flex;flex-direction:column;gap:.5rem}}
    .filtros-label{{font-family:var(--detalhe);font-size:.72rem;color:var(--texto2);letter-spacing:.18em;text-transform:uppercase;opacity:.6}}
    .filtros-grupo{{display:flex;gap:.5rem;flex-wrap:wrap}}
    .btn-filtro{{font-family:var(--detalhe);font-size:.82rem;letter-spacing:.1em;padding:.35rem .9rem;border:1px solid var(--borda);background:transparent;color:var(--texto2);cursor:pointer;transition:all var(--transicao)}}
    .btn-filtro:hover{{color:var(--texto);border-color:var(--texto2)}}
    .btn-filtro.ativo{{background:var(--destaque);border-color:var(--destaque);color:#0d0d0d}}

    /* ── Seções de categoria ── */
    .categoria-secao{{padding:4rem 0;border-bottom:1px solid var(--borda)}}
    .categoria-secao.oculta{{display:none}}
    .cat-header{{display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:1rem;padding:0 3rem 2rem}}
    .cat-label{{font-family:var(--detalhe);font-size:.8rem;color:var(--destaque);letter-spacing:.25em;text-transform:uppercase;margin-bottom:.3rem}}
    .cat-titulo{{font-family:var(--titulo);font-size:clamp(1.8rem,4vw,2.8rem);color:var(--texto);line-height:1}}
    .cat-subtitulo{{font-family:var(--detalhe);font-size:clamp(.95rem,2vw,1.2rem);color:var(--texto2);font-style:italic;border-left:2px solid var(--destaque);padding-left:1rem}}

    /* ── Grade de fotos ── */
    .fotos-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:3px;padding:0 3px}}
    .foto-item{{position:relative;aspect-ratio:4/3;overflow:hidden;cursor:pointer;background:#1a1a1a;
      -webkit-user-select:none;user-select:none}}
    .foto-item img{{transition:transform .5s ease;pointer-events:none;-webkit-user-drag:none;user-drag:none}}
    .foto-item:hover img{{transform:scale(1.05)}}
    .foto-overlay{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:1rem;
      background:rgba(13,13,13,0);transition:background var(--transicao)}}
    .foto-item:hover .foto-overlay{{background:rgba(13,13,13,.65)}}
    .foto-titulo-hover{{font-family:var(--detalhe);font-size:1rem;color:var(--texto);opacity:0;transform:translateY(6px);transition:all var(--transicao)}}
    .foto-item:hover .foto-titulo-hover{{opacity:1;transform:translateY(0)}}
    .foto-badges{{display:flex;gap:.3rem;margin-top:.4rem}}
    .badge-tipo{{font-family:var(--detalhe);font-size:.7rem;letter-spacing:.08em;padding:.15rem .5rem;border-radius:2px;opacity:0;transition:opacity var(--transicao)}}
    .foto-item:hover .badge-tipo{{opacity:1}}
    .badge-tipo.digital{{background:rgba(224,123,57,.2);color:var(--destaque);border:1px solid rgba(224,123,57,.4)}}
    .badge-tipo.fisica{{background:rgba(255,255,255,.08);color:var(--texto2);border:1px solid var(--borda)}}
    .foto-item.oculta{{display:none}}

    /* ── Lightbox ── */
    .lightbox{{position:fixed;inset:0;z-index:1000;display:flex;background:rgba(10,10,10,.97);opacity:0;pointer-events:none;transition:opacity .3s ease}}
    .lightbox.aberto{{opacity:1;pointer-events:all}}
    .lb-esquerda{{flex:1;display:flex;align-items:center;justify-content:center;padding:5rem 2rem 2rem;min-width:0}}
    .lb-foto{{max-width:100%;max-height:85vh;object-fit:contain;pointer-events:none;-webkit-user-drag:none;user-drag:none;-webkit-user-select:none;user-select:none}}
    .lb-direita{{width:340px;flex-shrink:0;border-left:1px solid var(--borda);display:flex;flex-direction:column;padding:6rem 2rem 2rem;overflow-y:auto}}
    .lb-fechar{{position:absolute;top:1.5rem;right:2rem;font-size:1.8rem;color:var(--texto2);cursor:pointer;background:none;border:none;transition:color var(--transicao);z-index:10}}
    .lb-fechar:hover{{color:var(--texto)}}
    .lb-nav{{position:absolute;top:50%;transform:translateY(-50%);font-size:1.6rem;color:var(--texto2);cursor:pointer;background:none;border:none;transition:color var(--transicao);z-index:10;padding:.5rem}}
    .lb-nav:hover{{color:var(--destaque)}}
    .lb-prev{{left:1rem}}
    .lb-next{{right:360px}}
    .lb-cat{{font-family:var(--detalhe);font-size:.8rem;color:var(--destaque);letter-spacing:.2em;text-transform:uppercase;margin-bottom:.6rem}}
    .lb-titulo{{font-family:var(--titulo);font-size:1.5rem;color:var(--texto);line-height:1.2;margin-bottom:1rem}}
    .lb-desc{{font-size:.9rem;color:var(--texto2);line-height:1.8;margin-bottom:2rem;flex:1}}
    .lb-sem-venda{{font-family:var(--detalhe);font-size:.9rem;color:var(--texto2);opacity:.5;margin-top:auto}}
    .lb-secao-compra{{border-top:1px solid var(--borda);padding-top:1.5rem;margin-top:auto}}
    .lb-preco-label{{font-family:var(--detalhe);font-size:.8rem;color:var(--texto2);letter-spacing:.1em;text-transform:uppercase;margin-bottom:.3rem}}
    .lb-preco{{font-family:var(--detalhe);font-size:1.6rem;color:var(--destaque);font-weight:600;margin-bottom:1.2rem}}
    .lb-btn{{display:block;width:100%;font-family:var(--detalhe);font-size:.95rem;text-align:center;padding:.7rem;background:var(--destaque);color:#0d0d0d;border:none;cursor:pointer;transition:background var(--transicao);text-decoration:none;margin-bottom:.6rem;letter-spacing:.04em}}
    .lb-btn:hover{{background:var(--destaque2)}}
    .lb-btn.secundario{{background:transparent;border:1px solid var(--borda);color:var(--texto2)}}
    .lb-btn.secundario:hover{{border-color:var(--destaque);color:var(--destaque)}}
    .lb-opcoes{{display:flex;flex-direction:column;gap:.5rem;margin-bottom:1rem}}
    .lb-opcao-grupo{{display:flex;flex-direction:column;gap:.2rem}}
    .lb-opcao-grupo label{{font-family:var(--detalhe);font-size:.75rem;color:var(--texto2);letter-spacing:.08em}}
    .lb-opcao-grupo select{{background:#1a1a1a;border:1px solid var(--borda);color:var(--texto);font-family:var(--corpo);font-size:.85rem;padding:.35rem .5rem;outline:none;cursor:pointer;width:100%}}
    .lb-opcao-grupo select:focus{{border-color:var(--destaque)}}
    .lb-tabs{{display:flex;gap:0;margin-bottom:1.5rem}}
    .lb-tab{{flex:1;font-family:var(--detalhe);font-size:.8rem;letter-spacing:.08em;padding:.4rem;border:1px solid var(--borda);background:transparent;color:var(--texto2);cursor:pointer;transition:all var(--transicao);text-align:center}}
    .lb-tab.ativo{{background:var(--destaque);border-color:var(--destaque);color:#0d0d0d}}
    .lb-tab-content{{display:none}}
    .lb-tab-content.ativo{{display:block}}
    .lb-contador{{font-family:var(--detalhe);font-size:.8rem;color:var(--texto2);opacity:.5;text-align:center;margin-top:1.5rem}}

    /* Proteção de imagem — camada invisível sobre cada foto */
    .foto-item::after{{content:'';position:absolute;inset:0;z-index:1;cursor:pointer}}

    /* ── Responsivo ── */
    @media(max-width:768px){{
      .lightbox{{flex-direction:column}}
      .lb-esquerda{{padding:4rem 1rem 0;flex:0 0 55vh}}
      .lb-direita{{width:100%;border-left:none;border-top:1px solid var(--borda);padding:1.5rem}}
      .lb-nav.lb-prev{{left:.3rem}}
      .lb-nav.lb-next{{right:.3rem}}
      .pagina-topo{{padding:8rem 1.5rem 2rem}}
      .cat-header{{padding:0 1.5rem 1.5rem}}
      .fotos-grid{{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}}
    }}
  </style>
</head>
<body>
{nav_html(ativa_portfolio=True)}

  <div class="pagina-topo reveal">
    <p class="pagina-label">portfólio</p>
    <h1 class="pagina-titulo">Portfólio</h1>

    <div class="filtros">
      <div class="filtros-bloco">
        <span class="filtros-label">Categorias</span>
        <div class="filtros-grupo" id="filtros-cat">
          <button class="btn-filtro" data-cat="terra" onclick="filtrarCat(this)">Terra</button>
          <button class="btn-filtro" data-cat="agua" onclick="filtrarCat(this)">Água</button>
          <button class="btn-filtro" data-cat="fogo" onclick="filtrarCat(this)">Fogo</button>
          <button class="btn-filtro" data-cat="ar" onclick="filtrarCat(this)">Ar</button>
          <button class="btn-filtro" data-cat="vida" onclick="filtrarCat(this)">Vida</button>
        </div>
      </div>
      <div class="filtros-bloco">
        <span class="filtros-label">Loja</span>
        <div class="filtros-grupo" id="filtros-loja">
          <button class="btn-filtro" data-loja="digital" onclick="filtrarLoja(this)">Digital</button>
          <button class="btn-filtro" data-loja="fisica" onclick="filtrarLoja(this)">Impressão</button>
        </div>
      </div>
    </div>
  </div>

{secoes_html}

  <!-- ── Lightbox ── -->
  <div class="lightbox" id="lightbox">
    <button class="lb-fechar" onclick="fecharLightbox()">&#215;</button>
    <button class="lb-nav lb-prev" onclick="navLightbox(-1)">&#8592;</button>
    <button class="lb-nav lb-next" onclick="navLightbox(1)">&#8594;</button>

    <div class="lb-esquerda">
      <img class="lb-foto" id="lb-img" src="" alt="" />
    </div>

    <div class="lb-direita">
      <p class="lb-cat" id="lb-cat"></p>
      <h2 class="lb-titulo" id="lb-titulo"></h2>
      <p class="lb-desc" id="lb-desc"></p>
      <p class="lb-contador" id="lb-contador"></p>

      <div class="lb-secao-compra" id="lb-compra">
        <!-- preenchido via JS -->
      </div>
    </div>
  </div>

{RODAPE}
  <script>
    /* ── Nav ── */
    const _nav = document.getElementById('nav');
    window.addEventListener('scroll', () => _nav.classList.toggle('rolada', window.scrollY > 50));
    document.getElementById('navToggle').addEventListener('click', () => document.getElementById('navLinks').classList.toggle('aberto'));
    function fecharMenu() {{ document.getElementById('navLinks').classList.remove('aberto'); }}
    document.querySelectorAll('.reveal').forEach(el => {{
      new IntersectionObserver(([e],o) => {{ if(e.isIntersecting){{ el.classList.add('visivel'); o.unobserve(el); }} }},{{threshold:.08}}).observe(el);
    }});

    /* ── Proteção de imagem ── */
    document.addEventListener('contextmenu', e => {{ if(e.target.tagName==='IMG') e.preventDefault(); }});
    document.addEventListener('dragstart',   e => {{ if(e.target.tagName==='IMG') e.preventDefault(); }});
    document.addEventListener('keyup', e => {{
      if((e.key==='PrintScreen')||(e.metaKey&&e.shiftKey&&(e.key==='3'||e.key==='4'||e.key==='5'))) {{
        navigator.clipboard?.writeText('').catch(()=>{{}});
      }}
    }});

    /* ── Filtros ── */
    let catsAtivas = new Set();
    let lojaAtiva  = new Set();

    function filtrarCat(btn) {{
      const cat = btn.dataset.cat;
      if(catsAtivas.has(cat)) {{ catsAtivas.delete(cat); btn.classList.remove('ativo'); }}
      else                    {{ catsAtivas.add(cat);    btn.classList.add('ativo');    }}
      aplicarFiltros();
      if(catsAtivas.size === 1 && catsAtivas.has(cat)) {{
        const sec = document.getElementById('cat-' + cat);
        if(sec) sec.scrollIntoView({{behavior:'smooth', block:'start'}});
      }}
    }}

    function filtrarLoja(btn) {{
      const tipo = btn.dataset.loja;
      if(lojaAtiva.has(tipo)) {{ lojaAtiva.delete(tipo); btn.classList.remove('ativo'); }}
      else                    {{ lojaAtiva.add(tipo);    btn.classList.add('ativo');    }}
      aplicarFiltros();
    }}

    function aplicarFiltros() {{
      document.querySelectorAll('.categoria-secao').forEach(sec => {{
        const slug  = sec.dataset.slug;
        const catOk = catsAtivas.size === 0 || catsAtivas.has(slug);
        sec.classList.toggle('oculta', !catOk);

        sec.querySelectorAll('.foto-item').forEach(item => {{
          const lojaItem = item.dataset.loja;
          let lojaOk = true;
          if(lojaAtiva.size > 0) {{
            lojaOk = false;
            lojaAtiva.forEach(t => {{ if(lojaItem.includes(t)) lojaOk = true; }});
          }}
          item.classList.toggle('oculta', !lojaOk);
        }});

        if(catOk) {{
          const visiveis = sec.querySelectorAll('.foto-item:not(.oculta)').length;
          sec.classList.toggle('oculta', visiveis === 0);
        }}
      }});
      atualizarVisiveisLightbox();
    }}

    /* ── Lightbox ── */
    const PRECOS = {{
      "20x30": {{ fosco: 129, brilhante: 129, fineart: 189 }},
      "30x40": {{ fosco: 189, brilhante: 189, fineart: 269 }},
      "40x60": {{ fosco: 269, brilhante: 269, fineart: 389 }},
      "50x70": {{ fosco: 349, brilhante: 349, fineart: 499 }},
    }};
    const MOLDURA = {{ sem: 0, preta: 120, branca: 120, natural: 150 }};

    let itensVisiveis = [];
    let idxAtual = 0;

    function atualizarVisiveisLightbox() {{
      itensVisiveis = Array.from(document.querySelectorAll('.foto-item:not(.oculta)'));
    }}

    function abrirLightbox(el) {{
      atualizarVisiveisLightbox();
      idxAtual = itensVisiveis.indexOf(el);
      carregarLightbox(idxAtual);
      document.getElementById('lightbox').classList.add('aberto');
      document.body.style.overflow = 'hidden';
    }}

    function carregarLightbox(idx) {{
      const el      = itensVisiveis[idx];
      const fid     = el.dataset.id;
      const titulo  = el.dataset.titulo;
      const desc    = el.dataset.descricao;
      const naLoja  = el.dataset.naLoja;
      const cat     = el.dataset.cat;
      const precoD  = el.dataset.precoDigital;
      const gumroad = el.dataset.linkGumroad;
      const shopify = el.dataset.linkShopify;

      document.getElementById('lb-img').src    = `https://drive.google.com/thumbnail?id=${{fid}}&sz=w1600`;
      document.getElementById('lb-img').alt    = titulo;
      document.getElementById('lb-titulo').textContent = titulo;
      document.getElementById('lb-desc').textContent   = desc || '';
      document.getElementById('lb-cat').textContent    = cat.toUpperCase();
      document.getElementById('lb-contador').textContent = `${{idx+1}} / ${{itensVisiveis.length}}`;

      const compra = document.getElementById('lb-compra');
      const temDigital = naLoja === 'digital' || naLoja === 'ambos';
      const temFisica  = naLoja === 'fisica'  || naLoja === 'ambos';

      if(!temDigital && !temFisica) {{
        compra.innerHTML = '<p class="lb-sem-venda">Esta foto não está à venda.</p>';
        return;
      }}

      let tabs = '', conteudos = '';

      if(temDigital && temFisica) {{
        tabs = `<div class="lb-tabs">
          <button class="lb-tab ativo" onclick="trocarTab('digital',this)">Download Digital</button>
          <button class="lb-tab"       onclick="trocarTab('fisica',this)">Impressão Física</button>
        </div>`;
      }}

      if(temDigital) {{
        const ativo = !temFisica ? 'ativo' : 'ativo';
        conteudos += `<div class="lb-tab-content ${{ativo}}" id="tab-digital">
          <p class="lb-preco-label">Preço</p>
          <p class="lb-preco">R$ ${{precoD}}</p>
          <p style="font-size:.8rem;color:var(--texto2);margin-bottom:1rem;line-height:1.6">JPEG alta resolução — download imediato via Gumroad</p>
          <a class="lb-btn" href="${{gumroad}}" target="_blank" rel="noopener">Comprar download</a>
        </div>`;
      }}

      if(temFisica) {{
        const ativo = !temDigital ? 'ativo' : '';
        conteudos += `<div class="lb-tab-content ${{ativo}}" id="tab-fisica">
          <div class="lb-opcoes">
            <div class="lb-opcao-grupo">
              <label>Tamanho</label>
              <select id="lb-tam" onchange="calcLbPreco('${{fid}}','${{shopify}}')">
                <option value="20x30">20×30 cm</option>
                <option value="30x40">30×40 cm</option>
                <option value="40x60">40×60 cm</option>
                <option value="50x70">50×70 cm</option>
              </select>
            </div>
            <div class="lb-opcao-grupo">
              <label>Papel</label>
              <select id="lb-papel" onchange="calcLbPreco('${{fid}}','${{shopify}}')">
                <option value="fosco">Fosco</option>
                <option value="brilhante">Brilhante</option>
                <option value="fineart">Fine Art</option>
              </select>
            </div>
            <div class="lb-opcao-grupo">
              <label>Moldura</label>
              <select id="lb-moldura" onchange="calcLbPreco('${{fid}}','${{shopify}}')">
                <option value="sem">Sem moldura</option>
                <option value="preta">Preta (+R$120)</option>
                <option value="branca">Branca (+R$120)</option>
                <option value="natural">Natural (+R$150)</option>
              </select>
            </div>
          </div>
          <p class="lb-preco-label">Total</p>
          <p class="lb-preco" id="lb-preco-fisica">R$ 129</p>
          <a class="lb-btn" id="lb-btn-shopify" href="${{shopify}}" target="_blank" rel="noopener">Comprar impressão</a>
        </div>`;
      }}

      compra.innerHTML = tabs + conteudos;
      if(temFisica) calcLbPreco(fid, shopify);
    }}

    function trocarTab(tipo, btn) {{
      document.querySelectorAll('.lb-tabs .lb-tab').forEach(b => b.classList.remove('ativo'));
      document.querySelectorAll('.lb-tab-content').forEach(c => c.classList.remove('ativo'));
      btn.classList.add('ativo');
      document.getElementById('tab-'+tipo)?.classList.add('ativo');
    }}

    function calcLbPreco(fid, shopify) {{
      const tam     = document.getElementById('lb-tam')?.value    || '20x30';
      const papel   = document.getElementById('lb-papel')?.value  || 'fosco';
      const moldura = document.getElementById('lb-moldura')?.value|| 'sem';
      const base    = PRECOS[tam]?.[papel] ?? 0;
      const extra   = MOLDURA[moldura] ?? 0;
      const total   = base + extra;
      const el = document.getElementById('lb-preco-fisica');
      if(el) el.textContent = 'R$ ' + total;
      const btn = document.getElementById('lb-btn-shopify');
      if(btn) btn.href = shopify + '?tamanho='+tam+'&papel='+papel+'&moldura='+moldura;
    }}

    function fecharLightbox() {{
      document.getElementById('lightbox').classList.remove('aberto');
      document.body.style.overflow = '';
      document.getElementById('lb-img').src = '';
    }}

    function navLightbox(dir) {{
      idxAtual = (idxAtual + dir + itensVisiveis.length) % itensVisiveis.length;
      carregarLightbox(idxAtual);
    }}

    document.addEventListener('keydown', e => {{
      const lb = document.getElementById('lightbox');
      if(!lb.classList.contains('aberto')) return;
      if(e.key === 'Escape')      fecharLightbox();
      if(e.key === 'ArrowRight')  navLightbox(1);
      if(e.key === 'ArrowLeft')   navLightbox(-1);
    }});

    /* ── Ativa filtros se vier da Loja ── */
    if(new URLSearchParams(location.search).get('loja') === '1') {{
      ['digital','fisica'].forEach(tipo => {{
        const btn = document.querySelector(`#filtros-loja [data-loja="${{tipo}}"]`);
        if(btn) {{ lojaAtiva.add(tipo); btn.classList.add('ativo'); }}
      }});
      aplicarFiltros();
    }}

    /* Ancora por categoria via URL hash (ex: portfolio.html#cat-agua) */
    if(location.hash) {{
      const slug = location.hash.replace('#cat-','');
      const btn  = document.querySelector(`#filtros-cat [data-cat="${{slug}}"]`);
      if(btn) filtrarCat(btn);
    }}

    atualizarVisiveisLightbox();
  </script>
</body>
</html>"""


def main():
    print("Atualizando site via Google Drive + Sheets...\n")
    if not API_KEY:
        print("ERRO: variavel GOOGLE_API_KEY nao encontrada.")
        return

    ctx = ler_planilha()
    todas_fotos = []

    for slug in PASTAS:
        info  = INFO_CATEGORIA[slug]
        print(f"{info['nome']}: lendo Drive...")
        fotos = listar_drive(PASTAS[slug])
        print(f"  {len(fotos)} foto(s)")

        for f in fotos:
            c = ctx.get(f["name"], {})
            todas_fotos.append({
                "slug":          slug,
                "nome_cat":      info["nome"],
                "foto_id":       f["id"],
                "foto_nome":     f["name"],
                "titulo":        c.get("titulo") or titulo_fallback(f["name"]),
                "descricao":     c.get("descricao", ""),
                "na_loja":       c.get("na_loja", "nao"),
                "preco_digital": c.get("preco_digital", "29"),
                "link_gumroad":  c.get("link_gumroad", ""),
                "link_shopify":  c.get("link_shopify", ""),
            })

    print(f"\nTotal: {len(todas_fotos)} foto(s)")
    with open("portfolio.html", "w", encoding="utf-8") as fh:
        fh.write(gerar_portfolio(todas_fotos))
    print("  portfolio.html gerado\n")

    # Remove arquivos antigos que não são mais usados
    import os as _os
    for slug in PASTAS:
        arq = f"categoria-{slug}.html"
        if _os.path.exists(arq):
            _os.remove(arq)
            print(f"  removido: {arq}")
    if _os.path.exists("loja.html"):
        _os.remove("loja.html")
        print("  removido: loja.html")

    print("\nFeito. Netlify publica em ~30s.")

if __name__ == "__main__":
    main()
