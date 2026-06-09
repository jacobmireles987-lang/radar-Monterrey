import requests
import urllib.parse

def obtener_tendencias_ml():
    url = "https://api.mercadolibre.com/trends/MLM"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        respuesta = requests.get(url, headers=headers, timeout=5)
        if respuesta.status_code == 200:
            return [item['keyword'].title() for item in respuesta.json()][:15]
    except:
        pass
    return ["Minisplit", "Llantas", "Ventilador", "Laptop", "Tenis", "iPhone"]

def buscar_precio_promedio_ml(producto_o_marca):
    headers = {"User-Agent": "Mozilla/5.0"}

    # ── CORRECCIÓN CLAVE: usar solo la primera palabra (el producto)
    # "Celular Samsung" → "Celular", "Laptop Apple" → "Laptop"
    termino_limpio = producto_o_marca.split()[0] if producto_o_marca else producto_o_marca

    termino_codificado = urllib.parse.quote(termino_limpio)
    url = f"https://api.mercadolibre.com/sites/MLM/search?q={termino_codificado}&limit=5"

    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            resultados = res.json().get("results", [])
            precios = [item["price"] for item in resultados if item.get("price")]
            if precios:
                return sum(precios) / len(precios)
    except:
        pass
    return None
