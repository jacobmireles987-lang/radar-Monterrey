def obtener_mas_buscado_amazon():
    """Top 10 más buscados en Amazon México — actualizados manualmente."""
    return [
        {"pos": 1,  "keyword": "iPhone 15"},
        {"pos": 2,  "keyword": "Laptop HP"},
        {"pos": 3,  "keyword": "Minisplit Inverter"},
        {"pos": 4,  "keyword": "Samsung Galaxy A55"},
        {"pos": 5,  "keyword": "PlayStation 5"},
        {"pos": 6,  "keyword": "AirPods Pro"},
        {"pos": 7,  "keyword": "Lavadora LG"},
        {"pos": 8,  "keyword": "Cafetera Nespresso"},
        {"pos": 9,  "keyword": "Roomba"},
        {"pos": 10, "keyword": "iPad"},
    ]

def obtener_mas_vendido_amazon():
    return obtener_mas_buscado_amazon()

def buscar_precio_amazon(x=None):
    return None
