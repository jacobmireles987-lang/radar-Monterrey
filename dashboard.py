import streamlit as st
import pandas as pd
import plotly.express as px
from ml_extractor import buscar_precio_promedio_ml
from amazon_extractor import buscar_precio_amazon
from fb_extractor import obtener_posts_monterrey
from processor import analizar_demanda_y_marcas

st.set_page_config(
    page_title="Radar Compra-Venta Monterrey",
    page_icon="📡",
    layout="wide"
)
st.title("📡 Radar de Compra-Venta — Monterrey")
st.caption("Cruza demanda de Facebook con precios de Mercado Libre y Amazon")

if st.button("🔄 Actualizar datos"):
    st.rerun()

def correr_pipeline():
    posts = obtener_posts_monterrey()
    df    = analizar_demanda_y_marcas(posts)
    if df.empty:
        return pd.DataFrame()

    filas = []
    for _, row in df.iterrows():
        termino    = f"{row['Producto']} {row['Marca']}".strip()
        precio_ml  = buscar_precio_promedio_ml(termino)
        precio_amz = buscar_precio_amazon(termino)

        precios_validos = [p for p in [precio_ml, precio_amz] if p and p > 0]
        mejor_costo     = min(precios_validos) if precios_validos else None
        presupuesto_fb  = row.get("Presupuesto_FB", None)
        ganancia        = (presupuesto_fb - mejor_costo
                           if presupuesto_fb and mejor_costo else None)

        filas.append({
            "Producto"      : row["Producto"],
            "Marca"         : row["Marca"],
            "Menciones FB"  : int(row["Menciones"]),
            "Presupuesto FB": presupuesto_fb,
            "Precio MeLi"   : precio_ml,
            "Precio Amazon" : precio_amz,
            "Mejor Costo"   : mejor_costo,
            "Ganancia Est." : ganancia,
        })

    return pd.DataFrame(filas).sort_values("Menciones FB", ascending=False)

with st.spinner("Analizando mercado..."):
    df = correr_pipeline()

if df.empty:
    st.warning("No se encontraron productos con intención de compra.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Productos detectados", len(df))
c2.metric("Total menciones FB",   int(df["Menciones FB"].sum()))
ganancias = df["Ganancia Est."].dropna()
if not ganancias.empty:
    c3.metric("Mejor oportunidad", f"${ganancias.max():,.0f} MXN")

st.divider()
st.subheader("📊 Ranking de Oportunidades")

def fmt(v, sin_dato="—"):
    try:
        return f"${v:,.0f}" if pd.notna(v) else sin_dato
    except:
        return sin_dato

def fila_a_html(row):
    gan = row["Ganancia Est."]
    if pd.notna(gan):
        color  = "#16a34a" if gan > 0 else "#dc2626"
        gan_td = f'<td style="color:{color};font-weight:bold">{fmt(gan)}</td>'
    else:
        gan_td = "<td>—</td>"
    return (
        f"<tr>"
        f"<td>{row['Producto']}</td>"
        f"<td>{row['Marca']}</td>"
        f"<td style='text-align:center'>{row['Menciones FB']}</td>"
        f"<td>{fmt(row['Presupuesto FB'])}</td>"
        f"<td>{fmt(row['Precio MeLi'])}</td>"
        f"<td>{fmt(row['Precio Amazon'], 'Sin dato')}</td>"
        f"<td>{fmt(row['Mejor Costo'])}</td>"
        f"{gan_td}"
        f"</tr>"
    )

cabeceras = ["Producto","Marca","Menciones FB","Presupuesto FB",
             "Precio MeLi","Precio Amazon","Mejor Costo","Ganancia Est."]
ths = "".join(f"<th>{h}</th>" for h in cabeceras)
trs = "".join(fila_a_html(row) for _, row in df.iterrows())

st.markdown(f"""
<style>
  .radar-tabla {{ width:100%; border-collapse:collapse; font-size:14px; }}
  .radar-tabla th {{ background:#1e3a5f; color:white; padding:8px 12px; text-align:left; }}
  .radar-tabla tr:nth-child(even) {{ background:#f0f4ff; }}
  .radar-tabla td {{ padding:7px 12px; border-bottom:1px solid #dde3f0; }}
</style>
<table class="radar-tabla">
  <thead><tr>{ths}</tr></thead>
  <tbody>{trs}</tbody>
</table>
""", unsafe_allow_html=True)

st.subheader("🔥 Productos más buscados en Facebook")
fig = px.bar(
    df, x="Menciones FB", y="Producto", orientation="h",
    color="Menciones FB", color_continuous_scale="Blues", text="Menciones FB",
)
fig.update_layout(
    yaxis=dict(autorange="reversed"), showlegend=False,
    height=max(300, len(df) * 55), plot_bgcolor="white",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("💰 Comparador de Precios por Producto")
producto_sel = st.selectbox("Selecciona un producto:", df["Producto"].tolist())
fila = df[df["Producto"] == producto_sel].iloc[0]

m1, m2, m3 = st.columns(3)
m1.metric("💬 Presupuesto Facebook", fmt(fila["Presupuesto FB"], "No especificado"))
m2.metric("🛒 Precio Mercado Libre", fmt(fila["Precio MeLi"],    "Sin dato"))
m3.metric("📦 Precio Amazon",        fmt(fila["Precio Amazon"],  "Sin dato"))

if pd.notna(fila["Ganancia Est."]):
    if fila["Ganancia Est."] > 0:
        st.success(f"✅ Oportunidad de reventa: **${fila['Ganancia Est.']:,.0f} MXN** por unidad")
    else:
        st.error(f"❌ Sin margen: el costo supera el presupuesto en ${abs(fila['Ganancia Est.']):,.0f} MXN")
else:
    st.info("ℹ️ Sin suficientes datos de precio para calcular ganancia.")

st.divider()
st.caption("Facebook simulado · Precios de referencia MeLi y Amazon · Monterrey NL")
