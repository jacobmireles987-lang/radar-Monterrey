import requests

def obtener_tendencias_ml():
    try:
        url = "https://api.mercadolibre.com/trends/MLM"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return [item['keyword'].title() for item in res.json()][:10]
    except:
        pass
    return ["Minisplit", "Llantas", "Celular", "Laptop", "iPhone",
            "Pantalla", "Refrigerador", "Lavadora", "Bicicleta", "Silla Gamer"]

def buscar_precio_promedio_ml(producto):
    return None  # ya no se usa
