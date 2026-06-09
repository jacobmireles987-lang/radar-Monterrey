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

    # Usamos el término completo para mejor precisión
    termino_codificado = urllib.parse.quote(producto_o_marca)
    url = f"https://api.mercadolibre.com/sites/MLM/search?q={termino_codificado}&limit=10"

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            resultados = res.json().get("results", [])
            # Filtramos precios razonables (entre $100 y $500,000 MXN)
            precios = [
                item["price"] for item in resultados
                if item.get("price") and 100 < item["price"] < 500000
            ]
            if precios:
                return sum(precios) / len(precios)
    except:
        pass
    return None
