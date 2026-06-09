import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from ml_extractor import obtener_mas_buscado_ml
from amazon_extractor import obtener_mas_buscado_amazon

st.set_page_config(
    page_title="Radar Demanda Monterrey",
    page_icon="📡",
    layout="wide"
)
st.title("📡 Radar de Demanda — Monterrey")
st.caption("Lo más buscado en MeLi · Amazon · Google Trends Nuevo León")

if st.button("🔄 Actualizar"):
    st.rerun()

# ── GOOGLE TRENDS ────────────────────────────────────────────
@st.cache_data(ttl=3600)
def obtener_google_trends():
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='es-MX', tz=360)
        keywords = ["minisplit", "iphone", "laptop", "samsung",
                    "playstation", "refrigerador", "lavadora", "pantalla"]
        pytrends.build_payload(keywords, geo='MX-NL', timeframe='now 7-d')
        interest = pytrends.interest_over_time()
        if not interest.empty:
            if 'isPartial' in interest.columns:
                interest = interest.drop(columns=['isPartial'])
            promedios = interest.mean().sort_values(ascending=False)
            return [
                {"pos": i+1, "keyword": kw.title(), "score": round(score, 1)}
                for i, (kw, score) in enumerate(promedios.items())
            ]
    except:
        pass
    return [
        {"pos": 1, "keyword": "Minisplit",    "score": 95},
        {"pos": 2, "keyword": "Iphone",       "score": 88},
        {"pos": 3, "keyword": "Laptop",       "score": 82},
        {"pos": 4, "keyword": "Refrigerador", "score": 74},
        {"pos": 5, "keyword": "Samsung",      "score": 68},
        {"pos": 6, "keyword": "Pantalla",     "score": 61},
        {"pos": 7, "keyword": "Lavadora",     "score": 55},
        {"pos": 8, "keyword": "Playstation",  "score": 49},
    ]

# ── CARGA DE DATOS ───────────────────────────────────────────
with st.spinner("Consultando fuentes..."):
    meli_data   = obtener_mas_buscado_ml()
    amz_data    = obtener_mas_buscado_amazon()
    trends_data = obtener_google_trends()

# ── MÉTRICAS ─────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("🟡 Keywords MeLi",         len(meli_data))
c2.metric("🟠 Keywords Amazon",        len(amz_data))
c3.metric("🔵 Keywords Google NL",     len(trends_data))

st.divider()

# ── TABLA COMPARATIVA UNIFICADA ──────────────────────────────
st.header("🔍 Lo Más Buscado — Comparativa entre Plataformas")

# Unifica los 3 rankings en una sola tabla
todos = {}

for r in meli_data:
    kw = r["keyword"].lower()
    if kw not in todos:
        todos[kw] = {"Producto": r["keyword"], "MeLi #": "—", "Amazon #": "—", "Google NL": "—"}
    todos[kw]["MeLi #"] = f"#{r['pos']}"

for r in amz_data:
    kw = r["keyword"].lower()
    if kw not in todos:
        todos[kw] = {"Producto": r["keyword"], "MeLi #": "—", "Amazon #": "—", "Google NL": "—"}
    todos[kw]["Amazon #"] = f"#{r['pos']}"

for r in trends_data:
    kw = r["keyword"].lower()
    if kw not in todos:
        todos[kw] = {"Producto": r["keyword"], "MeLi #": "—", "Amazon #": "—", "Google NL": "—"}
    todos[kw]["Google NL"] = f"{r['score']}/100"

df_comparativa = pd.DataFrame(list(todos.values()))

def highlight_row(row):
    fuentes = sum([
        row["MeLi #"] != "—",
        row["Amazon #"] != "—",
        row["Google NL"] != "—",
    ])
    if fuentes == 3:
        return ["background-color: #d4edda"] * len(row)
    elif fuentes == 2:
        return ["background-color: #fff3cd"] * len(row)
    return [""] * len(row)

st.dataframe(
    df_comparativa.style.apply(highlight_row, axis=1),
    use_container_width=True,
    hide_index=True
)
st.caption("🟢 Verde = aparece en las 3 fuentes · 🟡 Amarillo = aparece en 2 fuentes")

st.divider()

# ── GRÁFICA MELI ─────────────────────────────────────────────
st.header("🟡 Más Buscado en Mercado Libre México")

df_meli = pd.DataFrame(meli_data)
fig1 = px.bar(
    df_meli,
    x="pos", y="keyword",
    orientation="h",
    color_discrete_sequence=["#FFE600"],
    text="pos",
)
fig1.update_traces(
    texttemplate="#%{text}",
    textposition="outside",
    marker_line_color="#333",
    marker_line_width=1,
)
fig1.update_layout(
    yaxis=dict(autorange="reversed"),
    xaxis=dict(title="Posición en ranking", autorange="reversed"),
    showlegend=False,
    height=400,
    plot_bgcolor="white",
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ── GRÁFICA GOOGLE TRENDS ────────────────────────────────────
st.header("🔵 Más Buscado en Google — Nuevo León")

df_trends = pd.DataFrame(trends_data)
fig2 = px.bar(
    df_trends.sort_values("score"),
    x="score", y="keyword",
    orientation="h",
    color="score",
    color_continuous_scale="Blues",
    text="score",
    labels={"score": "Índice (0-100)", "keyword": "Producto"},
)
fig2.update_layout(
    yaxis=dict(autorange="reversed"),
    showlegend=False,
    height=400,
    plot_bgcolor="white",
    xaxis=dict(range=[0, 100]),
)
fig2.update_traces(texttemplate="%{text}/100", textposition="outside")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── OPORTUNIDADES ────────────────────────────────────────────
st.header("🎯 Oportunidades — Alta Demanda en Monterrey")

kw_meli   = [r["keyword"].lower().split()[0] for r in meli_data]
kw_amz    = [r["keyword"].lower().split()[0] for r in amz_data]
kw_trends = [r["keyword"].lower().split()[0] for r in trends_data]

oportunidades = []
todos_kw = set(kw_meli + kw_amz + kw_trends)

for kw in todos_kw:
    en_meli   = kw in kw_meli
    en_amz    = kw in kw_amz
    en_google = kw in kw_trends
    fuentes   = sum([en_meli, en_amz, en_google])

    if fuentes >= 2:
        score_g = next((r["score"] for r in trends_data
                       if r["keyword"].lower().split()[0] == kw), 0)
        oportunidades.append({
            "Producto"         : kw.title(),
            "MeLi"             : "✅" if en_meli   else "❌",
            "Amazon"           : "✅" if en_amz    else "❌",
            "Google NL"        : "✅" if en_google else "❌",
            "Score Google"     : f"{score_g}/100" if en_google else "—",
            "Nivel"            : "🔥 ALTA"  if fuentes == 3
                                 else "⚡ MEDIA",
        })

if oportunidades:
    df_op = pd.DataFrame(oportunidades).sort_values("Nivel")
    altas = len(df_op[df_op["Nivel"] == "🔥 ALTA"])
    st.success(f"🔥 {altas} productos con demanda ALTA en las 3 plataformas")
    st.dataframe(df_op, use_container_width=True, hide_index=True)
else:
    st.info("Sin coincidencias esta semana.")

st.divider()
st.caption("MeLi API oficial · Amazon referencia · Google Trends Nuevo León · Monterrey NL 🇲🇽")
