import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from ml_extractor import obtener_tendencias_ml
from amazon_extractor import obtener_mas_vendido_amazon
from fb_extractor import obtener_posts_monterrey
from processor import analizar_demanda_y_marcas

st.set_page_config(
    page_title="Radar Compra-Venta Monterrey",
    page_icon="📡",
    layout="wide"
)
st.title("📡 Radar de Compra-Venta — Monterrey")
st.caption("Lo más vendido en Mercado Libre y Amazon · Demanda en Facebook MTY")

if st.button("🔄 Actualizar datos"):
    st.rerun()

# ── SECCIÓN 1: Tendencias Mercado Libre ─────────────────────
st.header("🛒 Tendencias en Mercado Libre México")

with st.spinner("Consultando Mercado Libre..."):
    try:
        url = "https://api.mercadolibre.com/trends/MLM"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            tendencias = res.json()[:10]
        else:
            tendencias = []
    except:
        tendencias = []

if tendencias:
    df_meli = pd.DataFrame(tendencias)
    df_meli.index = df_meli.index + 1
    df_meli.index.name = "Posición"
    df_meli.columns = ["Producto en Tendencia", "URL"]
    df_meli = df_meli[["Producto en Tendencia"]]

    st.markdown("""
    <style>
    .meli-tabla { width:100%; border-collapse:collapse; font-size:15px; }
    .meli-tabla th { background:#FFE600; color:#333; padding:10px; text-align:left; }
    .meli-tabla tr:nth-child(even) { background:#FFFDE7; }
    .meli-tabla td { padding:8px 12px; border-bottom:1px solid #eee; }
    .meli-tabla .pos { font-weight:bold; color:#FF7733; font-size:18px; }
    </style>
    """, unsafe_allow_html=True)

    filas_meli = ""
    for i, row in enumerate(tendencias, 1):
        keyword = row['keyword'].title()
        filas_meli += f"<tr><td class='pos'>#{i}</td><td>{keyword}</td></tr>"

    st.markdown(f"""
    <table class="meli-tabla">
      <thead><tr><th>#</th><th>🔥 Producto más buscado</th></tr></thead>
      <tbody>{filas_meli}</tbody>
    </table>
    """, unsafe_allow_html=True)
else:
    st.warning("No se pudo conectar a Mercado Libre en este momento.")

st.divider()

# ── SECCIÓN 2: Más vendidos Amazon ──────────────────────────
st.header("📦 Más Vendidos en Amazon México")

mas_vendidos_amz = obtener_mas_vendido_amazon("")

cols = st.columns(2)
items = list(mas_vendidos_amz.items())
for i, (categoria, producto) in enumerate(items):
    with cols[i % 2]:
        st.markdown(f"""
        <div style="background:#232F3E;color:white;border-radius:10px;
                    padding:14px;margin:6px 0;">
            <div style="color:#FF9900;font-weight:bold;font-size:13px;">
                {categoria}
            </div>
            <div style="font-size:15px;margin-top:4px;">{producto}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── SECCIÓN 3: Demanda en Facebook MTY ──────────────────────
st.header("💬 Lo que busca la gente en Facebook Monterrey")

posts = obtener_posts_monterrey()
df_fb = analizar_demanda_y_marcas(posts)

if not df_fb.empty:
    fig = px.bar(
        df_fb.head(10),
        x="Menciones",
        y="Producto",
        orientation="h",
        color="Menciones",
        color_continuous_scale="Reds",
        text="Menciones",
        title="Productos más buscados en grupos de Facebook MTY"
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        height=max(300, len(df_fb) * 55),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Detalle de búsquedas")
    df_show = df_fb[["Producto","Marca","Menciones","Presupuesto_FB"]].copy()
    df_show.columns = ["Producto","Marca","Menciones","Presupuesto Promedio FB"]
    df_show["Presupuesto Promedio FB"] = df_show["Presupuesto Promedio FB"].apply(
        lambda x: f"${x:,.0f}" if pd.notna(x) else "No especificado"
    )
    st.dataframe(df_show, use_container_width=True, hide_index=True)
else:
    st.warning("No se detectaron búsquedas en Facebook.")

st.divider()

# ── SECCIÓN 4: Oportunidades cruzadas ───────────────────────
st.header("🎯 Oportunidades: Lo que buscan vs lo que hay")

if tendencias and not df_fb.empty:
    keywords_meli = [t['keyword'].lower() for t in tendencias]
    productos_fb  = df_fb["Producto"].str.lower().tolist()

    coincidencias = []
    for kw in keywords_meli:
        for prod in productos_fb:
            if kw in prod or prod in kw:
                coincidencias.append({
                    "Producto"           : kw.title(),
                    "En tendencia MeLi"  : "✅ Sí",
                    "Buscado en FB MTY"  : "✅ Sí",
                    "Oportunidad"        : "🔥 ALTA",
                })

    if coincidencias:
        st.success(f"¡Se encontraron {len(coincidencias)} productos que están en tendencia en MeLi Y se buscan en Facebook Monterrey!")
        st.dataframe(pd.DataFrame(coincidencias), use_container_width=True, hide_index=True)
    else:
        st.info("No hay coincidencias directas esta semana entre MeLi y Facebook MTY.")

st.divider()
st.caption("MeLi vía API oficial · Amazon datos de referencia · Facebook simulado · Monterrey NL 🇲🇽")
