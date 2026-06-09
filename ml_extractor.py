import requests
import urllib.parse

def obtener_tendencias_ml():
    url = "https://api.mercadolibre.com/trends/MLM"
    # El disfraz para que parezca un navegador real
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    try:
        respuesta = requests.get(url, headers=headers, timeout=5)
        if respuesta.status_code == 200:
            return [item['keyword'].title() for item in respuesta.json()][:15]
    except:
        pass
    return ["Minisplit", "Llantas", "Ventilador", "Alberca", "Tenis", "Laptop", "iPhone"]

def buscar_precio_promedio_ml(producto_o_marca):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    termino_codificado = urllib.parse.quote(producto_o_marca)
    url = f"https://api.mercadolibre.com/sites/MLM/search?q={termino_codificado}&limit=5"
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            resultados = res.json().get("results", [])
            precios = [item["price"] for item in resultados if item.get("price")]
            if precios:
                promedio = sum(precios) / len(precios)
                return f"${promedio:,.2f} MXN"
    except:
        pass
    return "Sin datos"
