# Guia Shopify — Loja de impressões físicas
## Douglas N. Schimidt

---

## Como o sistema de venda física funciona

```
Cliente escolhe tamanho + papel + moldura no seu site
              ↓
O preço é calculado automaticamente
              ↓
Clica em "Encomendar" → vai para o checkout do Shopify
              ↓
Paga com PIX, cartão ou boleto
              ↓
Você recebe e-mail com o pedido completo
(nome, endereço, produto, valor pago)
              ↓
Cliente recebe confirmação automática por e-mail
```

Você não precisa falar com ninguém. O pedido chega pronto.

---

## PARTE 1 — Criar a conta no Shopify

1. Acesse **shopify.com/br**
2. Clique em **"Iniciar teste grátis"** (14 dias sem cobrar)
3. Preencha: e-mail, senha, nome da loja → `douglasnschimidt`
4. Na pergunta "o que você vende?" → escolha **"Produtos físicos"**
5. Pule as etapas de configuração inicial clicando em **"Fazer isso depois"**

**Plano recomendado após o teste:** Shopify Starter (~R$ 25/mês)
→ Permite vender sem precisar de loja Shopify separada.
→ Os clientes pagam direto pelo link, você gerencia pelo painel.

---

## PARTE 2 — Cadastrar cada foto como produto

Para cada foto que você marcou como "fisica" na planilha:

1. No painel do Shopify → clique em **"Produtos" → "Adicionar produto"**
2. **Título:** nome da foto (ex: `Patagônia — Cume`)
3. **Descrição:** contexto da foto (o mesmo da planilha)
4. **Mídia:** adicione a foto (pode ser uma versão menor, só para visualização)
5. **Preços:** deixe em branco por enquanto — os preços vêm das variantes
6. **Variantes:** clique em **"Adicionar opções"**:

   **Opção 1 — Tamanho:**
   - Nome: `Tamanho`
   - Valores: `20x30 cm`, `30x40 cm`, `40x60 cm`, `50x70 cm`

   **Opção 2 — Papel:**
   - Nome: `Papel`
   - Valores: `Fosco`, `Brilhante`, `Fine Art`

   **Opção 3 — Moldura:**
   - Nome: `Moldura`
   - Valores: `Sem moldura`, `Preta`, `Branca`, `Natural (madeira)`

7. O Shopify vai gerar automaticamente todas as combinações possíveis
8. Para cada combinação, defina o preço (use a tabela abaixo como base)
9. Clique em **"Salvar"**

### Tabela de preços sugerida

| Tamanho | Fosco | Brilhante | Fine Art |
|---------|-------|-----------|----------|
| 20×30 cm | R$ 129 | R$ 129 | R$ 189 |
| 30×40 cm | R$ 189 | R$ 189 | R$ 269 |
| 40×60 cm | R$ 269 | R$ 269 | R$ 389 |
| 50×70 cm | R$ 349 | R$ 349 | R$ 499 |

**Adicional por moldura:** + R$ 120 (preta ou branca) / + R$ 150 (natural)

> Esses valores são sugestões. Ajuste conforme o custo do seu laboratório de impressão.
> No site, esses mesmos preços estão no arquivo `atualizar-site.py`, na seção `TABELA DE PREÇOS`.
> Quando você mudar aqui, mude lá também para ficarem iguais.

---

## PARTE 3 — Configurar pagamentos no Brasil

1. No painel Shopify → **"Configurações" → "Pagamentos"**
2. Clique em **"Shopify Payments"** → ative
3. Adicione seus dados bancários (CPF, conta corrente para receber)
4. Ative as opções:
   - ✅ PIX
   - ✅ Cartão de crédito (parcelamento em até 12x)
   - ✅ Boleto bancário

> O Shopify retém uma pequena % por transação (~2%). Sem mensalidade extra para pagamentos.

---

## PARTE 4 — Configurar notificação de pedido por e-mail

O Shopify já envia e-mail automático para você a cada pedido. Para confirmar:

1. **"Configurações" → "Notificações"**
2. Em **"Pedidos"** → verifique que **"Novo pedido"** está ativo
3. Confirme que o e-mail de destino é o seu (`contato@douglasnschimidt.com`)

O e-mail que você recebe contém:
- Nome e e-mail do cliente
- Endereço de entrega completo
- Produto + variante escolhida (tamanho, papel, moldura)
- Valor pago
- Número do pedido

---

## PARTE 5 — Pegar o link de cada produto para o site

Após cadastrar cada produto no Shopify:

1. Vá em **"Produtos"** → clique no produto
2. Clique em **"Ver"** (olho) no canto superior direito
3. Copie a URL da página do produto
   → Vai ter este formato: `https://douglasnschimidt.myshopify.com/products/patagonia-cume`
4. Abra a planilha `douglasnschimidt-fotos`
5. Na linha da foto correspondente, cole esse link na coluna **`link_shopify`**
6. Na próxima atualização automática (ou manual), o botão "Encomendar" já vai apontar para o produto certo

---

## PARTE 6 — Conectar seu domínio ao Shopify (opcional)

Se quiser que a loja apareça como `loja.douglasnschimidt.com`:

1. **"Configurações" → "Domínios" → "Conectar domínio existente"**
2. Digite: `loja.douglasnschimidt.com`
3. Siga as instruções para adicionar um registro CNAME na GoDaddy
   (igual ao que você fez para o site principal, mas com subdomínio `loja`)

---

## PARTE 7 — Resumo do fluxo de um pedido

1. 📦 Cliente faz o pedido e paga no Shopify
2. 📧 Você recebe e-mail com todos os dados
3. 🖨️ Você envia o arquivo para o laboratório de impressão
4. 📮 O laboratório entrega para o cliente (ou você mesmo envia)
5. ✅ No painel Shopify → marque o pedido como **"Concluído"** → cliente recebe notificação automática

---

## Laboratórios de impressão em São Paulo (sugestões)

| Lab | Especialidade | Site |
|-----|--------------|------|
| Fotosite | Fine Art, grande formato | fotosite.com.br |
| Revelação | Papel fotográfico, rápido | revelacao.com.br |
| Graphium | Fine Art, papel algodão | graphium.com.br |

Peça amostras antes de fechar com um laboratório — qualidade varia bastante.

---

*Dúvidas? Traga este guia para o chat e peça ajuda.*
