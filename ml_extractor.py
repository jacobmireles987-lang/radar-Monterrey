import requests

def obtener_tendencias_ml():
    url = "https://api.mercadolibre.com/trends/MLM"
    try:
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            return [item['keyword'].title() for item in respuesta.json()][:15]
    except:
        pass
    # Respaldo por si la API tarda en responder
    return ["Minisplit", "Llantas", "Ventilador", "Alberca", "Tenis", "Laptop", "iPhone", "Bicicleta", "Refrigerador", "Taladro"]
