import streamlit as st
import pandas as pd
from ml_extractor import obtener_tendencias_ml, buscar_precio_promedio_ml
from amazon_extractor import buscar_precio_amazon
from fb_extractor import obtener_posts_monterrey
from processor import analizar_demanda_y_marcas

# ── Configuración de la página ──────────────────────────────
st.set_page_config(
    page_title="Radar Compra-Venta Monterrey",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Radar de Compra-Venta — Monterrey")
st.caption("Cruza demanda de Facebook con precios de Mercado Libre y Amazon")

# ── Botón para refrescar ────────────────────────────────────
if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()

# ── Pipeline principal ──────────────────────────────────────
@st.cache_data(ttl=600)
def correr_pipeline():
    # 1. Posts de Facebook
    posts = obtener_posts_monterrey()

    # 2. Analizar demanda con processor.py
    df = analizar_demanda_y_marcas(posts)

    if df.empty:
        return pd.DataFrame()

    # 3. Para cada producto, buscar precios en MeLi y Amazon
    filas = []
    for _, row in df.iterrows():
        termino = f"{row['Producto']} {row['Marca']}".strip()

        precio_ml  = buscar_precio_promedio_ml(termino)
        precio_amz = buscar_precio_amazon(termino)

        # Mejor precio disponible entre las dos plataformas
        precios_validos = [p for p in [precio_ml, precio_amz] if p and p > 0]
        mejor_costo = min(precios_validos) if precios_validos else None

        # Ganancia estimada = lo que ofrece Facebook - mejor costo proveedor
        presupuesto_fb = row.get("Presupuesto_FB", None)
        if presupuesto_fb and mejor_costo:
            ganancia = presupuesto_fb - mejor_costo
        else:
            ganancia = None

        filas.append({
            "Producto"       : row["Producto"],
            "Marca"          : row["Marca"],
            "Menciones FB"   : row["Menciones"],
            "Presupuesto FB" : presupuesto_fb,
            "Precio MeLi"    : precio_ml,
            "Precio Amazon"  : precio_amz,
            "Mejor Costo"    : mejor_costo,
            "Ganancia Est."  : ganancia,
        })

    return pd.DataFrame(filas)

# ── Mostrar resultados ──────────────────────────────────────
with st.spinner("Analizando mercado..."):
    df_resultado = correr_pipeline()

if df_resultado.empty:
    st.warning("No se encontraron productos con intención de compra.")
    st.stop()

# ── Métricas rápidas ────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Productos detectados", len(df_resultado))
col2.metric("Total menciones FB",   int(df_resultado["Menciones FB"].sum()))

ganancias_validas = df_resultado["Ganancia Est."].dropna()
if not ganancias_validas.empty:
    col3.metric("Mejor oportunidad", f"${ganancias_validas.max():,.0f} MXN")

st.divider()

# ── Tabla principal ─────────────────────────────────────────
st.subheader("📊 Ranking de Oportunidades")

def colorear_ganancia(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    color = "green" if val > 0 else "red"
    return f"color: {color}; font-weight: bold"

formato = {
    "Presupuesto FB" : lambda x: f"${x:,.0f}" if pd.notna(x) else "—",
    "Precio MeLi"    : lambda x: f"${x:,.0f}" if pd.notna(x) else "—",
    "Precio Amazon"  : lambda x: f"${x:,.0f}" if pd.notna(x) else "Sin dato",
    "Mejor Costo"    : lambda x: f"${x:,.0f}" if pd.notna(x) else "—",
    "Ganancia Est."  : lambda x: f"${x:,.0f}" if pd.notna(x) else "—",
}

df_display = df_resultado.sort_values("Menciones FB", ascending=False)

st.dataframe(
    df_display.style
        .format(formato)
        .applymap(colorear_ganancia, subset=["Ganancia Est."]),
    use_container_width=True,
    hide_index=True
)

# ── Gráfica de menciones ────────────────────────────────────
st.subheader("🔥 Productos más buscados en Facebook")
import plotly.express as px

fig = px.bar(
    df_display,
    x="Menciones FB",
    y="Producto",
    orientation="h",
    color="Menciones FB",
    color_continuous_scale="Blues",
    text="Menciones FB",
)
fig.update_layout(
    yaxis=dict(autorange="reversed"),
    showlegend=False,
    height=max(300, len(df_display) * 50),
    plot_bgcolor="white",
)
st.plotly_chart(fig, use_container_width=True)

# ── Comparador de precios ───────────────────────────────────
st.subheader("💰 Comparador de Precios por Producto")

producto_sel = st.selectbox(
    "Selecciona un producto:",
    options=df_display["Producto"].tolist()
)

fila = df_display[df_display["Producto"] == producto_sel].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric(
    "💬 Presupuesto en Facebook",
    f"${fila['Presupuesto FB']:,.0f}" if pd.notna(fila['Presupuesto FB']) else "No especificado"
)
c2.metric(
    "🛒 Precio Mercado Libre",
    f"${fila['Precio MeLi']:,.0f}" if pd.notna(fila['Precio MeLi']) else "Sin dato"
)
c3.metric(
    "📦 Precio Amazon",
    f"${fila['Precio Amazon']:,.0f}" if pd.notna(fila['Precio Amazon']) else "Sin dato"
)

if pd.notna(fila['Ganancia Est.']):
    if fila['Ganancia Est.'] > 0:
        st.success(f"✅ Oportunidad de reventa estimada: **${fila['Ganancia Est.']:,.0f} MXN** por unidad")
    else:
        st.error(f"❌ Sin margen: el costo supera el presupuesto en Facebook por ${abs(fila['Ganancia Est.']):,.0f} MXN")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.caption("Datos de Facebook simulados · MeLi vía API pública · Amazon vía scraping (puede fallar)")
