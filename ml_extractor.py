import requests
import urllib.parse

PRECIOS_ML = {
    "celular"   : 8500,
    "laptop"    : 15000,
    "llantas"   : 2800,
    "minisplit" : 7200,
    "minisplits": 7200,
    "usado"     : 4500,
    "samsung"   : 8500,
    "apple"     : 18000,
    "dell"      : 14000,
    "michelin"  : 2800,
    "pirelli"   : 2600,
    "lg"        : 7000,
    "mirage"    : 6500,
}

def obtener_tendencias_ml():
    url = "https://api.mercadolibre.com/trends/MLM"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        respuesta = requests.get(url, headers=headers, timeout=5)
        if respuesta.status_code == 200:
            return [item['keyword'].title() for item in respuesta.json()][:15]
    except:
        pass
    return ["Minisplit", "Llantas", "Celular", "Laptop", "iPhone"]

def buscar_precio_promedio_ml(producto_o_marca):
    texto = producto_o_marca.lower()
    for clave, precio in PRECIOS_ML.items():
        if clave in texto:
            return precio
    return 6000
