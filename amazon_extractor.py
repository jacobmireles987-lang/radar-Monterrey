import requests
from bs4 import BeautifulSoup

def buscar_precio_amazon(producto):
    # Amazon bloquea conexiones que parecen robots, así que usamos "headers" 
    # para engañarlos y hacerles creer que somos una computadora normal.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "es-MX,es;q=0.9"
    }
    
    # Formateamos la búsqueda (ej. "minisplit+mirage")
    url = f"https://www.amazon.com.mx/s?k={producto.replace(' ', '+')}"
    
    try:
        respuesta = requests.get(url, headers=headers, timeout=3)
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        # El código extrae específicamente la etiqueta visual del precio en Amazon
        precio_texto = sopa.find("span", {"class": "a-price-whole"}).text
        return float(precio_texto.replace(',', ''))
    except:
        return None  # Si Amazon bloquea o no hay producto
