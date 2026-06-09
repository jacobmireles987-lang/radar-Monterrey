import streamlit as st
import pandas as pd
import plotly.express as px
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
st.caption("Top 10 más vendidos en MeLi y Amazon · Demanda en Facebook MTY")

if st.button("🔄 Actualizar"):
    st.rerun()

# ── TOP 10 MERCADO LIBRE ─────────────────────────────────────
st.header("🟡 Top 10 Más Vendidos — Mercado Libre México")

meli_data = obtener_tendencias_ml()
df_meli   = pd.DataFrame(meli_data)

filas_meli = ""
for _, row in df_meli.iterrows():
    filas_meli += (
        f"<tr>"
        f"<td style='font-weight:bold;color:#FF7733;font-size:18px'>#{row['pos']}</td>"
        f"<td><span style='background:#FFF3CD;padding:2px 8px;"
        f"border-radius:8px;font-size:12px'>{row['departamento']}</span></td>"
        f"<td>{row['producto']}</td>"
        f"<td style='font-weight:bold;color:#00a650'>{row['precio']}</td>"
        f"</tr>"
    )

st.markdown(f"""
<style>
.t{{width:100%;border-collapse:collapse;font-size:14px}}
.t th{{background:#FFE600;color:#333;padding:10px 14px;text-align:left}}
.t tr:nth-child(even){{background:#FFFDE7}}
.t td{{padding:9px 14px;border-bottom:1px solid #eee}}
</style>
<table class="t">
<thead><tr><th>#</th><th>Departamento</th><th>Producto</th><th>Precio</th></tr></thead>
<tbody>{filas_meli}</tbody>
</table>
""", unsafe_allow_html=True)

st.divider()

# ── TOP 10 AMAZON ────────────────────────────────────────────
st.header("🟠 Top 10 Más Vendidos — Amazon México")

amz_data = obtener_mas_vendido_amazon()
df_amz   = pd.DataFrame(amz_data)

filas_amz = ""
for _, row in df_amz.iterrows():
    filas_amz += (
        f"<tr>"
        f"<td style='font-weight:bold;color:#FF9900;font-size:18px'>#{row['pos']}</td>"
        f"<td><span style='background:#FFE0B2;padding:2px 8px;"
        f"border-radius:8px;font-size:12px'>{row['departamento']}</span></td>"
        f"<td>{row['producto']}</td>"
        f"<td style='font-weight:bold;color:#00a650'>{row['precio']}</td>"
        f"</tr>"
    )

st.markdown(f"""
<table class="t">
<thead><tr>
<th style='background:#232F3E;color:#FF9900'>#</th>
<th style='background:#232F3E;color:white'>Departamento</th>
<th style='background:#232F3E;color:white'>Producto</th>
<th style='background:#232F3E;color:#FF9900'>Precio</th>
</tr></thead>
<tbody>{filas_amz}</tbody>
</table>
""", unsafe_allow_html=True)

st.divider()

# ── DEMANDA FACEBOOK MTY ─────────────────────────────────────
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
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        height=max(300, len(df_fb) * 55),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

    df_show = df_fb[["Producto","Marca","Menciones","Presupuesto_FB"]].copy()
    df_show.columns = ["Producto","Marca","Menciones","Presupuesto Promedio"]
    df_show["Presupuesto Promedio"] = df_show["Presupuesto Promedio"].apply(
        lambda x: f"${x:,.0f}" if pd.notna(x) else "No especificado"
    )
    st.dataframe(df_show, use_container_width=True, hide_index=True)

st.divider()

# ── OPORTUNIDADES ────────────────────────────────────────────
st.header("🎯 Oportunidades detectadas en Monterrey")

if not df_fb.empty:
    productos_meli = [r["producto"].lower() for r in meli_data]
    productos_amz  = [r["producto"].lower() for r in amz_data]
    productos_fb   = df_fb["Producto"].str.lower().tolist()

    oportunidades = []
    for prod_fb in productos_fb:
        en_meli = any(prod_fb in p or p.split()[0] in prod_fb for p in productos_meli)
        en_amz  = any(prod_fb in p or p.split()[0] in prod_fb for p in productos_amz)
        if en_meli or en_amz:
            oportunidades.append({
                "Producto buscado en FB" : prod_fb.title(),
                "En MeLi Top 10"         : "✅" if en_meli else "❌",
                "En Amazon Top 10"       : "✅" if en_amz  else "❌",
                "Nivel de oportunidad"   : "🔥 ALTA" if (en_meli and en_amz) else "⚡ MEDIA",
            })

    if oportunidades:
        st.success(f"¡{len(oportunidades)} productos buscados en Monterrey coinciden con los más vendidos!")
        st.dataframe(pd.DataFrame(oportunidades), use_container_width=True, hide_index=True)
    else:
        st.info("Esta semana no hay coincidencias directas.")

st.divider()
st.caption("MeLi y Amazon — datos de referencia actualizados · Facebook simulado · Monterrey NL 🇲🇽")
