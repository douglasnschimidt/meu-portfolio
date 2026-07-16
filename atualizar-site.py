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

PLANILHA_ID  = "1DnSWBiIMxd-BqfgUQkcHa-58IeZ85hcquxwGlNvDC80"
PLANILHA_GID = "1134133275"  # Página2 — tabela de preços

PASTAS = {
    "terra": "1tHbeHivJircA47WZnzAK4cmR2iogUWd1",
    "agua":  "1V14qDp6lnMaC1OtEzh6zcm0Gqnq3SfYU",
    "fogo":  "1l8x_isgLIGvE8sJ6HvhDWEyb9loACKQl",
    "ar":    "15gd7fxCIKiW4UqOLpNod7d_R0KjqC99R",
    "vida":  "1P2eNUhjzhITeJ2XwUhdop6xHxVubRvzu",
}

INFO_CATEGORIA = {
    "terra": {"nome": "Terra", "sub": "Gigante e magnífica."},
    "agua":  {"nome": "Água",  "sub": "Aqui estou em casa."},
    "fogo":  {"nome": "Fogo",  "sub": "Impossível ignorar."},
    "ar":    {"nome": "Ar",    "sub": "Sempre presente."},
    "vida":  {"nome": "Vida",  "sub": "Seja cotidiana ou selvagem."},
}

API_KEY = os.environ.get("GOOGLE_API_KEY", "")

def ler_planilha():
    url  = f"https://docs.google.com/spreadsheets/d/{PLANILHA_ID}/export"
    resp = requests.get(url, params={"format": "csv", "key": API_KEY})
    resp.encoding = 'utf-8'
    if not resp.ok:
        print(f"  aviso: nao consegui ler a planilha (codigo {resp.status_code})")
        return {}
    dados = {}
    # enumerate começa em 0 — guardamos a posição para ordenar as fotos depois
    for posicao, linha in enumerate(csv.DictReader(io.StringIO(resp.text))):
        arq = linha.get("arquivo", "").strip()
        if arq:
            dados[arq] = {
                "posicao":       posicao,          # ordem na planilha
                "titulo":        linha.get("titulo",        "").strip(),
                "descricao":     linha.get("descricao",     "").strip(),
                "na_loja":       linha.get("na_loja",       "nao").strip().lower(),
                "preco_digital": linha.get("preco_digital", "29").strip(),
                "link_gumroad":  linha.get("link_gumroad",  "").strip(),
                "link_shopify":  linha.get("link_shopify",  "").strip(),
            }
    print(f"  planilha: {len(dados)} foto(s) com contexto")
    return dados

def ler_precos():
    """
    Lê a Página2 da planilha com tamanhos, papéis e molduras.
    Retorna três dicts: tamanhos, papeis, molduras
    Formato da aba:
      Tamanho | Preço || Papel | Preço adicional || Moldura | Preço adicional
    """
    url  = f"https://docs.google.com/spreadsheets/d/{PLANILHA_ID}/export"
    resp = requests.get(url, params={"format": "csv", "gid": PLANILHA_GID, "key": API_KEY})
    resp.encoding = 'utf-8'
    if not resp.ok:
        print(f"  aviso: nao consegui ler a tabela de precos (codigo {resp.status_code})")
        # fallback com valores padrão
        return (
            {"20x30 cm": 120, "30x40 cm": 270, "40x60 cm": 350, "50x70 cm": 500},
            {"Fosco": 0, "Brilhante": 50, "Fine art": 120},
            {"Sem moldura": 0, "Preta": 120, "Branca": 120, "Natural": 150},
        )
    tamanhos, papeis, molduras = {}, {}, {}
    for linha in csv.DictReader(io.StringIO(resp.text)):
        tam = linha.get("Tamanho", "").strip()
        if tam:
            try: tamanhos[tam] = int(float(linha.get("Preço", "0").strip() or "0"))
            except: pass
        papel = linha.get("Papel", "").strip()
        if papel:
            try: papeis[papel] = int(float(linha.get("Preço adicional", "0").strip() or "0"))
            except: pass
        moldura = linha.get("Moldura", "").strip()
        if moldura:
            try: molduras[moldura] = int(float(linha.get("Preço adicional", "0").strip() or "0"))
            except: pass
    print(f"  precos: {len(tamanhos)} tamanho(s), {len(papeis)} papel(is), {len(molduras)} moldura(s)")
    return tamanhos, papeis, molduras

def listar_drive(pasta_id):
    r = requests.get("https://www.googleapis.com/drive/v3/files", params={
        "q": f"'{pasta_id}' in parents and trashed=false and (mimeType='image/jpeg' or mimeType='image/png')",
        "fields": "files(id,name)", "orderBy": "name", "key": API_KEY,
    })
    return r.json().get("files", []) if r.ok else []

def thumb(fid):  return f"https://drive.google.com/thumbnail?id={fid}&sz=w800"
def grande(fid): return f"https://drive.google.com/thumbnail?id={fid}&sz=w1600"
def titulo_fallback(name): return name.rsplit(".",1)[0].replace("-"," ").replace("_"," ").title()

FONTES = '<link rel="stylesheet" href="https://use.typekit.net/zeo6kqs.css" />'

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
  </nav>
  <style>
    /* Nav some ao rolar para baixo, volta ao rolar para cima */
    #nav {{ transition: transform 0.35s ease, background var(--transicao); }}
    #nav.oculta-nav {{ transform: translateY(-100%); }}
  </style>"""

RODAPE = """  <footer>
    <span class="footer-logo">Douglas N. Schimidt</span>
    <button class="tema-toggle" id="temaToggle" onclick="toggleTema()">Modo claro</button>
    <span>© 2026</span>
  </footer>"""

TEMA_INIT = """  <script>if(localStorage.getItem('tema')==='claro'){document.documentElement.setAttribute('data-tema','claro');}</script>"""

TEMA_SCRIPT = """    function toggleTema() {
      const claro = document.documentElement.getAttribute('data-tema') === 'claro';
      if (claro) { document.documentElement.removeAttribute('data-tema'); localStorage.setItem('tema','escuro'); }
      else       { document.documentElement.setAttribute('data-tema','claro'); localStorage.setItem('tema','claro'); }
      atualizarBotaoTema();
    }
    function atualizarBotaoTema() {
      const btn = document.getElementById('temaToggle');
      if (btn) btn.textContent = document.documentElement.getAttribute('data-tema') === 'claro' ? 'Modo escuro' : 'Modo claro';
    }
    atualizarBotaoTema();"""

def gerar_portfolio(todas_fotos, tamanhos, papeis, molduras):
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
        # Faixa de categoria — divisor de largura total acima das fotos
        cat_faixa = f"""    <div class="cat-faixa">
      <h2 class="cat-faixa-titulo">{info['nome']}</h2>
      <p class="cat-faixa-sub">{info['sub']}</p>
    </div>"""
        secoes_html += f"""
  <section class="categoria-secao" id="cat-{slug}" data-slug="{slug}">
{cat_faixa}
    <div class="fotos-grid">
{grid}
    </div>
  </section>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width,initial-scale=1.0" />
{TEMA_INIT}
  <title>Portfólio — Douglas N. Schimidt</title>
  {FONTES}
  <link rel="stylesheet" href="estilo.css" />
  <style>
    /* ── Topo da página — removido ── */
    .pagina-topo{{display:none}}

    /* ── Filtros sticky — sempre visíveis, top dinâmico via JS ── */
    .filtros-sticky{{position:sticky;top:0;z-index:90;background:rgba(var(--fundo-rgb),.97);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid var(--borda);padding:.7rem 3rem;display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap;}}
    .filtros-sep{{width:1px;height:1.1rem;background:var(--borda);flex-shrink:0}}
    .filtros-grupo{{display:flex;gap:.3rem;flex-wrap:wrap;align-items:center}}
    .filtros-label-inline{{font-family:var(--detalhe);font-size:.7rem;color:var(--texto2);letter-spacing:.15em;text-transform:uppercase;opacity:.5;white-space:nowrap}}
    .btn-filtro{{font-family:var(--detalhe);font-size:.78rem;letter-spacing:.07em;padding:.25rem .7rem;border:1px solid var(--borda);background:transparent;color:var(--texto2);cursor:pointer;transition:all var(--transicao);white-space:nowrap;}}
    .btn-filtro:hover{{color:var(--texto);border-color:var(--texto2)}}
    .btn-filtro.ativo{{background:var(--destaque);border-color:var(--destaque);color:#0d0d0d}}

    /* ── Seções de categoria ── */
    .categoria-secao{{padding:0;border-bottom:none}}
    .categoria-secao.oculta{{display:none}}

    /* ── Grade — colunas CSS (column-count), sequência vertical por bloco ──
       Cada foto entra na coluna atual e empilha por cima da anterior,
       sem depender de JavaScript — é o navegador quem distribui as fotos
       nas colunas, preenchendo de cima para baixo, sem buracos. */
    .fotos-grid{{column-count:3;column-gap:6px;padding:0 6px 6px;}}
    .foto-item{{position:relative;overflow:hidden;cursor:pointer;background:#1a1a1a;break-inside:avoid;margin-bottom:6px;-webkit-user-select:none;user-select:none;--texto:#f0ece4;--texto2:#8a8378;--borda:#222;}}
    .foto-item img{{width:100%;height:auto;display:block;transition:transform .5s ease;pointer-events:none;-webkit-user-drag:none;}}
    .foto-item:hover img{{transform:scale(1.04)}}
    .foto-overlay{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding:1rem;background:rgba(13,13,13,0);transition:background var(--transicao)}}
    .foto-item:hover .foto-overlay{{background:rgba(13,13,13,.65)}}
    .foto-titulo-hover{{font-family:var(--detalhe);font-size:1rem;color:var(--texto);opacity:0;transform:translateY(6px);transition:all var(--transicao)}}
    .foto-item:hover .foto-titulo-hover{{opacity:1;transform:translateY(0)}}
    .foto-badges{{display:flex;gap:.3rem;margin-top:.4rem}}
    .badge-tipo{{font-family:var(--detalhe);font-size:.7rem;letter-spacing:.08em;padding:.15rem .5rem;border-radius:2px;opacity:0;transition:opacity var(--transicao)}}
    .foto-item:hover .badge-tipo{{opacity:1}}
    .badge-tipo.digital{{background:rgba(224,123,57,.2);color:var(--destaque);border:1px solid rgba(224,123,57,.4)}}
    .badge-tipo.fisica{{background:rgba(255,255,255,.08);color:var(--texto2);border:1px solid var(--borda)}}
    .foto-item.oculta{{display:none}}

    /* Proteção de imagem */
    .foto-item::after{{content:'';position:absolute;inset:0;z-index:1;cursor:pointer}}

    /* ── Faixa de categoria — divisor de largura total acima das fotos ── */
    .cat-faixa{{padding:2.4rem 3rem 1.2rem;border-top:1px solid var(--borda);}}
    .categoria-secao:first-of-type .cat-faixa{{border-top:none;padding-top:1.4rem;}}
    .cat-faixa-titulo{{font-family:var(--titulo);font-size:clamp(1.6rem,3vw,2.2rem);color:var(--texto);line-height:1;margin-bottom:.6rem;}}
    .cat-faixa-sub{{font-family:var(--detalhe);font-size:clamp(.9rem,1.5vw,1.05rem);color:var(--texto2);font-style:italic;border-left:2px solid var(--destaque);padding-left:.8rem;line-height:1.4;}}

    /* ── Lightbox — acompanha o tema do site (claro/escuro) ── */
    .lightbox{{position:fixed;inset:0;z-index:1000;display:flex;background:rgba(var(--fundo-rgb),.97);opacity:0;pointer-events:none;transition:opacity .3s ease}}
    .lightbox.aberto{{opacity:1;pointer-events:all}}
    .lb-esquerda{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:5rem 2rem 2rem;min-width:0;gap:0}}
    .lb-foto{{max-width:100%;max-height:75vh;object-fit:contain;pointer-events:none;-webkit-user-drag:none;user-drag:none;-webkit-user-select:none;user-select:none}}
    .lb-direita{{width:340px;flex-shrink:0;border-left:1px solid var(--borda);display:flex;flex-direction:column;padding:6rem 2rem 2rem;overflow-y:auto}}
    .lb-fechar{{position:absolute;top:1.5rem;right:2rem;font-size:1.8rem;color:var(--texto2);cursor:pointer;background:none;border:none;transition:color var(--transicao);z-index:10}}
    .lb-fechar:hover{{color:var(--texto)}}
    .lb-nav{{position:absolute;top:50%;transform:translateY(-50%);font-size:1.6rem;color:var(--texto2);cursor:pointer;background:none;border:none;transition:color var(--transicao);z-index:10;padding:.5rem}}
    .lb-nav:hover{{color:var(--destaque)}}
    .lb-prev{{left:1rem}}
    .lb-next{{right:360px}}
    .lb-cat{{font-family:var(--detalhe);font-size:.8rem;color:var(--destaque);letter-spacing:.2em;text-transform:uppercase;margin-bottom:.6rem}}
    .lb-titulo{{font-family:var(--titulo);font-size:1.5rem;color:var(--texto);line-height:1.2;margin-bottom:1rem}}
    .lb-desc{{font-size:.9rem;color:var(--texto2);line-height:1.8;margin-bottom:2rem}}
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
    .lb-opcao-grupo select{{background:var(--painel);border:1px solid var(--borda);color:var(--texto);font-family:var(--corpo);font-size:.85rem;padding:.35rem .5rem;outline:none;cursor:pointer;width:100%}}
    .lb-opcao-grupo select:focus{{border-color:var(--destaque)}}
    .lb-tabs{{display:flex;gap:0;margin-bottom:1.5rem}}
    .lb-tab{{flex:1;font-family:var(--detalhe);font-size:.8rem;letter-spacing:.08em;padding:.4rem;border:1px solid var(--borda);background:transparent;color:var(--texto2);cursor:pointer;transition:all var(--transicao);text-align:center}}
    .lb-tab.ativo{{background:var(--destaque);border-color:var(--destaque);color:#0d0d0d}}
    .lb-tab-content{{display:none}}
    .lb-tab-content.ativo{{display:block}}
    .lb-contador{{font-family:var(--detalhe);font-size:.8rem;color:var(--texto2);opacity:.5;text-align:center;margin-top:1.5rem}}

    /* ── Responsivo mobile ── */
    @media(max-width:768px){{
      .lightbox{{flex-direction:column}}
      .lb-esquerda{{padding:4.5rem 1rem 0;flex:none;width:100%;justify-content:flex-start}}
      .lb-foto{{max-height:52vh}}
      .lb-direita{{width:100%;border-left:none;border-top:1px solid var(--borda);padding:1.2rem 1.2rem 1.5rem;flex:1;overflow-y:auto}}
      .lb-nav.lb-prev{{left:.3rem}}
      .lb-nav.lb-next{{right:.3rem}}
      .fotos-grid{{column-count:2;padding:0 6px 6px}}
      .cat-faixa{{padding:1.6rem 1.2rem .8rem;}}
      .filtros-sticky{{padding:.45rem 1rem;gap:.5rem}}
      .filtros-sep{{display:none}}
    }}
  </style>
</head>
<body>
{nav_html(ativa_portfolio=True)}

  <div class="filtros-sticky">
    <span class="filtros-label-inline">Cat.</span>
    <div class="filtros-grupo" id="filtros-cat">
      <button class="btn-filtro" data-cat="terra" onclick="filtrarCat(this)">Terra</button>
      <button class="btn-filtro" data-cat="agua" onclick="filtrarCat(this)">Água</button>
      <button class="btn-filtro" data-cat="fogo" onclick="filtrarCat(this)">Fogo</button>
      <button class="btn-filtro" data-cat="ar" onclick="filtrarCat(this)">Ar</button>
      <button class="btn-filtro" data-cat="vida" onclick="filtrarCat(this)">Vida</button>
    </div>
    <div class="filtros-sep"></div>
    <span class="filtros-label-inline">Loja</span>
    <div class="filtros-grupo" id="filtros-loja">
      <button class="btn-filtro" data-loja="digital" onclick="filtrarLoja(this)">Digital</button>
      <button class="btn-filtro" data-loja="fisica" onclick="filtrarLoja(this)">Impressão</button>
    </div>
  </div>
  <div class="portfolio-spacer" id="portfolioSpacer"></div>

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
    /* ── Nav — some ao rolar para baixo, volta ao rolar para cima ── */
    const _nav = document.getElementById('nav');
    const _filtros = document.querySelector('.filtros-sticky');
    const _spacer = document.getElementById('portfolioSpacer');
    let _ultimoScroll = 0;

    function ajustarLayout() {{
      const navH = _nav.offsetHeight;
      const filtrosH = _filtros.offsetHeight;
      const navOculta = _nav.classList.contains('oculta-nav');
      _filtros.style.top = navOculta ? '0' : navH + 'px';
      _spacer.style.height = (navH + filtrosH) + 'px';
    }}

    window.addEventListener('scroll', () => {{
      const atual = window.scrollY;
      const navAltura = _nav.offsetHeight;
      if (atual > _ultimoScroll && atual > navAltura) {{
        _nav.classList.add('oculta-nav');
        _filtros.style.top = '0';
      }} else {{
        _nav.classList.remove('oculta-nav');
        _filtros.style.top = _nav.offsetHeight + 'px';
      }}
      _nav.classList.toggle('rolada', atual > 50);
      _ultimoScroll = atual;
    }});

    window.addEventListener('load', ajustarLayout);
    window.addEventListener('resize', ajustarLayout);

{TEMA_SCRIPT}

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
    const TAMANHOS = {{{",".join(f'"{k}":{v}' for k,v in tamanhos.items())}}};
    const PAPEIS   = {{{",".join(f'"{k}":{v}' for k,v in papeis.items())}}};
    const MOLDURAS = {{{",".join(f'"{k}":{v}' for k,v in molduras.items())}}};

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
        compra.innerHTML = '<p class="lb-sem-venda">Entre em contato caso queira comprar essa foto</p>';
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
        const opcoesTam    = Object.keys(TAMANHOS).map(k => `<option value="${{k}}">${{k}}</option>`).join('');
        const opcoesPapel  = Object.keys(PAPEIS).map(k => `<option value="${{k}}">${{k}}</option>`).join('');
        const opcoesMold   = Object.keys(MOLDURAS).map(k => `<option value="${{k}}">${{k}}</option>`).join('');
        conteudos += `<div class="lb-tab-content ${{ativo}}" id="tab-fisica">
          <div class="lb-opcoes">
            <div class="lb-opcao-grupo">
              <label>Tamanho</label>
              <select id="lb-tam" onchange="calcLbPreco('${{fid}}','${{shopify}}')">${{opcoesTam}}</select>
            </div>
            <div class="lb-opcao-grupo">
              <label>Papel</label>
              <select id="lb-papel" onchange="calcLbPreco('${{fid}}','${{shopify}}')">${{opcoesPapel}}</select>
            </div>
            <div class="lb-opcao-grupo">
              <label>Moldura</label>
              <select id="lb-moldura" onchange="calcLbPreco('${{fid}}','${{shopify}}')">${{opcoesMold}}</select>
            </div>
          </div>
          <p class="lb-preco-label">Total</p>
          <p class="lb-preco" id="lb-preco-fisica">R$ 0</p>
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
      const tam     = document.getElementById('lb-tam')?.value    || Object.keys(TAMANHOS)[0];
      const papel   = document.getElementById('lb-papel')?.value  || Object.keys(PAPEIS)[0];
      const moldura = document.getElementById('lb-moldura')?.value|| Object.keys(MOLDURAS)[0];
      const base    = (TAMANHOS[tam] ?? 0) + (PAPEIS[papel] ?? 0);
      const extra   = MOLDURAS[moldura] ?? 0;
      const total   = base + extra;
      const el = document.getElementById('lb-preco-fisica');
      if(el) el.textContent = 'R$ ' + total;
      const btn = document.getElementById('lb-btn-shopify');
      if(btn) btn.href = shopify + '?tamanho='+encodeURIComponent(tam)+'&papel='+encodeURIComponent(papel)+'&moldura='+encodeURIComponent(moldura);
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
    print("Atualizando site...\n")
    if not API_KEY:
        print("ERRO: variavel GOOGLE_API_KEY nao encontrada.")
        return

    ctx = ler_planilha()
    tamanhos, papeis, molduras = ler_precos()
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
                # fotos sem linha na planilha vão para o final (posição 999999)
                "posicao":       c.get("posicao", 999999),
            })

    # Ordena cada categoria pela posição na planilha
    # Fotos sem linha na planilha ficam no final, na ordem que o Drive retornou
    todas_fotos.sort(key=lambda f: (f["slug"], f["posicao"]))

    print(f"\nTotal: {len(todas_fotos)} foto(s)")
    with open("portfolio.html", "w", encoding="utf-8") as fh:
        fh.write(gerar_portfolio(todas_fotos, tamanhos, papeis, molduras))
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
