import requests

def obtener_tendencias_ml():
    url = "https://api.mercadolibre.com/trends/MLM"
    try:
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            return [item['keyword'].title() for item in respuesta.json()][:15]
    except:
        pass
    return ["Minisplit", "Llantas", "Ventilador", "Alberca", "Tenis", "Laptop", "iPhone"]

def buscar_precio_promedio_ml(producto_o_marca):
    # Buscamos el producto en ML y promediamos los primeros 5 resultados
    url = f"https://api.mercadolibre.com/sites/MLM/search?q={producto_o_marca}&limit=5"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            resultados = res.json().get("results", [])
            precios = [item["price"] for item in resultados if item.get("price")]
            if precios:
                promedio = sum(precios) / len(precios)
                return f"${promedio:,.2f} MXN"
    except:
        pass
    return "Sin datos"
