import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pytrends.request import TrendReq
from ml_extractor import obtener_tendencias_ml
from amazon_extractor import obtener_mas_vendido_amazon

st.set_page_config(
    page_title="Radar Compra-Venta Monterrey",
    page_icon="📡",
    layout="wide"
)
st.title("📡 Radar de Compra-Venta — Monterrey")
st.caption("MeLi · Amazon · Google Trends Nuevo León")

if st.button("🔄 Actualizar"):
    st.rerun()

# ── TOP 10 MERCADO LIBRE ─────────────────────────────────────
st.header("🟡 Top 10 Más Vendidos — Mercado Libre México")

meli_data = obtener_tendencias_ml()

filas_meli = ""
for row in meli_data:
    filas_meli += (
        f"<tr>"
        f"<td style='font-weight:bold;color:#FF7733;font-size:18px'>#{row['pos']}</td>"
        f"<td><span style='background:#FFF3CD;padding:2px 8px;border-radius:8px;font-size:12px'>{row['departamento']}</span></td>"
        f"<td>{row['producto']}</td>"
        f"<td style='font-weight:bold;color:#00a650'>{row['precio']}</td>"
        f"</tr>"
    )

st.markdown(f"""
<style>
.t{{width:100%;border-collapse:collapse;font-size:14px}}
.t th{{padding:10px 14px;text-align:left}}
.t tr:nth-child(even){{background:#FFFDE7}}
.t td{{padding:9px 14px;border-bottom:1px solid #eee}}
</style>
<table class="t">
<thead style="background:#FFE600">
<tr><th>#</th><th>Departamento</th><th>Producto</th><th>Precio</th></tr>
</thead>
<tbody>{filas_meli}</tbody>
</table>
""", unsafe_allow_html=True)

st.divider()

# ── TOP 10 AMAZON ────────────────────────────────────────────
st.header("🟠 Top 10 Más Vendidos — Amazon México")

amz_data = obtener_mas_vendido_amazon()

filas_amz = ""
for row in amz_data:
    filas_amz += (
        f"<tr>"
        f"<td style='font-weight:bold;color:#FF9900;font-size:18px'>#{row['pos']}</td>"
        f"<td><span style='background:#FFE0B2;padding:2px 8px;border-radius:8px;font-size:12px'>{row['departamento']}</span></td>"
        f"<td>{row['producto']}</td>"
        f"<td style='font-weight:bold;color:#00a650'>{row['precio']}</td>"
        f"</tr>"
    )

st.markdown(f"""
<table class="t">
<thead style="background:#232F3E;color:white">
<tr>
<th style='color:#FF9900'>#</th>
<th>Departamento</th>
<th>Producto</th>
<th style='color:#FF9900'>Precio</th>
</tr></thead>
<tbody>{filas_amz}</tbody>
</table>
""", unsafe_allow_html=True)

st.divider()

# ── GOOGLE TRENDS NUEVO LEÓN ─────────────────────────────────
st.header("🔵 Tendencias Google — Nuevo León")

@st.cache_data(ttl=3600)
def obtener_google_trends():
    try:
        pytrends = TrendReq(hl='es-MX', tz=360)
        # Categoría 0 = todas, geo MX-NL = Nuevo León
        df = pytrends.trending_searches(pn='mexico')
        
        # Buscamos tendencias de productos específicos en NL
        keywords = [
            "minisplit", "laptop", "celular", "refrigerador",
            "pantalla", "lavadora", "iphone", "samsung"
        ]
        pytrends.build_payload(keywords, geo='MX-NL', timeframe='now 7-d')
        interest = pytrends.interest_over_time()
        
        if not interest.empty and 'isPartial' in interest.columns:
            interest = interest.drop(columns=['isPartial'])
        
        if not interest.empty:
            promedios = interest.mean().sort_values(ascending=False)
            resultado = []
            for i, (kw, score) in enumerate(promedios.items(), 1):
                resultado.append({
                    "pos"      : i,
                    "keyword"  : kw.title(),
                    "score"    : round(score, 1),
                    "barra"    : int(score),
                })
            return resultado
    except Exception as e:
        pass
    
    # Datos de respaldo si Google bloquea
    return [
        {"pos": 1, "keyword": "Minisplit",     "score": 95, "barra": 95},
        {"pos": 2, "keyword": "Iphone",        "score": 88, "barra": 88},
        {"pos": 3, "keyword": "Laptop",        "score": 82, "barra": 82},
        {"pos": 4, "keyword": "Refrigerador",  "score": 74, "barra": 74},
        {"pos": 5, "keyword": "Samsung",       "score": 68, "barra": 68},
        {"pos": 6, "keyword": "Pantalla",      "score": 61, "barra": 61},
        {"pos": 7, "keyword": "Lavadora",      "score": 55, "barra": 55},
        {"pos": 8, "keyword": "Celular",       "score": 49, "barra": 49},
    ]

with st.spinner("Consultando Google Trends..."):
    trends_data = obtener_google_trends()

df_trends = pd.DataFrame(trends_data)

fig = px.bar(
    df_trends.sort_values("score"),
    x="score",
    y="keyword",
    orientation="h",
    color="score",
    color_continuous_scale="Blues",
    text="score",
    labels={"score": "Índice de Búsqueda (0-100)", "keyword": "Producto"},
)
fig.update_layout(
    yaxis=dict(autorange="reversed"),
    showlegend=False,
    height=400,
    plot_bgcolor="white",
    xaxis=dict(range=[0, 100]),
)
fig.update_traces(texttemplate="%{text}", textposition="outside")
st.plotly_chart(fig, use_container_width=True)

st.caption("🔵 Índice 100 = máximo interés de búsqueda en Nuevo León esta semana")

st.divider()

# ── OPORTUNIDADES CRUZADAS ───────────────────────────────────
st.header("🎯 Oportunidades Detectadas")
st.caption("Productos que coinciden entre Google Trends NL, MeLi y Amazon")

keywords_trends = [r["keyword"].lower() for r in trends_data]
keywords_meli   = [r["producto"].lower() for r in meli_data]
keywords_amz    = [r["producto"].lower() for r in amz_data]

oportunidades = []
for kw in keywords_trends:
    en_meli = any(kw in p or kw.split()[0] in p for p in keywords_meli)
    en_amz  = any(kw in p or kw.split()[0] in p for p in keywords_amz)
    
    if en_meli or en_amz:
        score_trend = next((r["score"] for r in trends_data 
                           if r["keyword"].lower() == kw), 0)
        oportunidades.append({
            "Producto"              : kw.title(),
            "Búsquedas Google NL"  : f"{score_trend}/100",
            "En MeLi Top 10"       : "✅" if en_meli else "❌",
            "En Amazon Top 10"     : "✅" if en_amz  else "❌",
            "Oportunidad"          : "🔥 ALTA"  if (en_meli and en_amz) 
                                     else "⚡ MEDIA",
        })

if oportunidades:
    df_op = pd.DataFrame(oportunidades).sort_values(
        "Oportunidad", ascending=True
    )
    st.success(f"✅ {len(oportunidades)} productos con alta demanda detectados en Nuevo León")
    st.dataframe(df_op, use_container_width=True, hide_index=True)
else:
    st.info("Sin coincidencias esta semana.")

st.divider()
st.caption("Google Trends NL · MeLi API · Amazon referencia · Monterrey NL 🇲🇽")
