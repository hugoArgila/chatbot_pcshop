from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_cors import CORS
from bson import ObjectId
import openai
import requests

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)

# --- Conexión a Cosmos DB ---
MONGO_URL = os.getenv('MONGO_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME')

try:
    client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)
    db = client[DATABASE_NAME]
    print("✅ Conexión establecida con Cosmos DB")
except Exception as e:
    print("❌ Error al conectar a Cosmos DB:", e)

# --- Configuración para Azure OpenAI (GPT-40-mini fallback) ---
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # Ej: "https://<tu-endpoint>.openai.azure.com/"
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-03-15-preview")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
GPT40_MINI_DEPLOYMENT = os.getenv("AZURE_OPENAI_GPT40_MINI_DEPLOYMENT")  # Nombre del deployment para gpt-40-mini

# --- Configuración para Azure Conversational Language ---
AZ_CONV_ENDPOINT = os.getenv("AZURE_CONVERSATIONAL_LANGUAGE_ENDPOINT")
AZ_CONV_KEY = os.getenv("AZURE_CONVERSATIONAL_LANGUAGE_KEY")
AZ_CONV_PROJECT = os.getenv("AZURE_CONVERSATIONAL_LANGUAGE_PROJECT")
AZ_CONV_DEPLOYMENT = os.getenv("AZURE_CONVERSATIONAL_LANGUAGE_DEPLOYMENT")
AZ_CONV_API_VERSION = os.getenv("AZURE_CONVERSATIONAL_LANGUAGE_API_VERSION", "2022-10-01")

# --- Rutas de la aplicación ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/productos', methods=['GET'])
def obtener_productos():
    try:
        try:
            colecciones = db.list_collection_names()
        except:
            colecciones = db.command("listCollections").get("cursor", {}).get("firstBatch", [])
            colecciones = [c['name'] for c in colecciones]
        print(f"📂 Colecciones encontradas: {colecciones}")

        productos_list = []
        for coleccion_nombre in colecciones:
            coleccion = db[coleccion_nombre]
            productos = list(coleccion.find())
            if len(productos) == 0:
                print(f"⚠️ No hay productos en la colección '{coleccion_nombre}'.")
            for producto in productos:
                print(f"📦 Producto encontrado en '{coleccion_nombre}': {producto}")
                producto['_id'] = str(producto['_id'])
                producto_corregido = {
                    "coleccion": coleccion_nombre,
                    "nombre": producto.get("Nombre_producto", ""),
                    "codigo": producto.get("Código_producto", ""),
                    "precio": producto.get("Precio", ""),
                    "garantia": producto.get("Garantía", ""),
                    "almacenamiento": {
                        "capacidad": producto.get("Almacenamiento", {}).get("Capacidad_disco", ""),
                        "tipo": producto.get("Almacenamiento", {}).get("Tipo_disco", ""),
                        "interfaz": producto.get("Almacenamiento", {}).get("Interfaz_disco", "")
                    },
                    "bateria": {
                        "numero_celdas": producto.get("Batería", {}).get("Número_celdas", ""),
                        "duracion": producto.get("Batería", {}).get("Duración", "")
                    },
                    "grafica": {
                        "integrada": producto.get("Gráfica", {}).get("Integrada", False),
                        "fabricante": producto.get("Gráfica", {}).get("Fabricante", ""),
                        "modelo": producto.get("Gráfica", {}).get("Modelo", ""),
                        "memoria": producto.get("Gráfica", {}).get("Memoria", "")
                    },
                    "procesador": {
                        "familia": producto.get("Procesador", {}).get("Familia", ""),
                        "modelo": producto.get("Procesador", {}).get("Modelo", ""),
                        "fabricante": producto.get("Procesador", {}).get("Fabricante", ""),
                        "frecuencia": producto.get("Procesador", {}).get("Frecuencia", "")
                    },
                    "pantalla": {
                        "tamano": producto.get("Pantalla", {}).get("Tamaño", ""),
                        "tactil": producto.get("Pantalla", {}).get("Táctil", False),
                        "tipo": producto.get("Pantalla", {}).get("Tipo", ""),
                        "resolucion": producto.get("Pantalla", {}).get("Resolución", "")
                    },
                    "dimensiones": {
                        "peso": producto.get("Dimensiones", {}).get("Peso", ""),
                        "altura": producto.get("Dimensiones", {}).get("Altura", ""),
                        "ancho": producto.get("Dimensiones", {}).get("Ancho", ""),
                        "profundidad": producto.get("Dimensiones", {}).get("Profundidad", "")
                    },
                    "color": producto.get("Color", ""),
                    "conectividad": {
                        "red_movil": producto.get("Conectividad", {}).get("Red_móvil", False),
                        "ethernet": producto.get("Conectividad", {}).get("Ethernet", ""),
                        "vga": producto.get("Conectividad", {}).get("VGA", False),
                        "bluetooth": producto.get("Conectividad", {}).get("Bluetooth", False),
                        "thunderbolt": producto.get("Conectividad", {}).get("Thunderbolt", False),
                        "hdmi": producto.get("Conectividad", {}).get("HDMI", False)
                    },
                    "ram": {
                        "instalada": producto.get("RAM", {}).get("Instalada", ""),
                        "maxima": producto.get("RAM", {}).get("Máxima", ""),
                        "libre": producto.get("RAM", {}).get("Libre", ""),
                        "velocidad": producto.get("RAM", {}).get("Velocidad", ""),
                        "tecnologia": producto.get("RAM", {}).get("Tecnología", "")
                    },
                    "extras": {
                        "microfono_integrado": producto.get("Extras", {}).get("Micrófono_integrado", False),
                        "webcam_integrada": producto.get("Extras", {}).get("Webcam_integrada", False),
                        "uso_gaming": producto.get("Extras", {}).get("Uso_gaming", False)
                    },
                    "sistema_operativo": producto.get("Sistema_operativo", "")
                }
                productos_list.append(producto_corregido)
        return jsonify(productos_list), 200
    except Exception as e:
        print("❌ Se produjo un error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/productos/<codigo_producto>')
def detalles_producto(codigo_producto):
    producto = db['productos'].find_one({'codigo': codigo_producto})
    if producto:
        return jsonify(producto)
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/chatbot', methods=['GET'])
def chatbot():
    return render_template('chatbot.html')

@app.route('/chatbot', methods=['POST'])
def chatbot_query():
    data = request.get_json()
    message = data.get('message', '')
    reply = ""
    m = message.lower()

    # Buscar el producto "LG gram" en las colecciones
    colecciones = db.list_collection_names()
    producto = None
    for coleccion_nombre in colecciones:
        coleccion = db[coleccion_nombre]
        producto = coleccion.find_one({"Nombre_producto": {"$regex": "LG gram", "$options": "i"}})
        if producto:
            break

    if producto:
        # --- Intents basados en el producto ---
        if "precio" in m:
            reply = f"El precio del {producto.get('Nombre_producto','producto')} es {producto.get('Precio','no especificado')}."
        elif "código" in m or "codigo" in m:
            reply = f"El código del producto es {producto.get('Código_producto', 'no especificado')}."
        elif "garantía" in m or "garantia" in m:
            reply = f"La garantía del producto es {producto.get('Garantía', 'no especificada')}."
        elif "almacenamiento" in m and ("capacidad" in m or "gb" in m):
            reply = f"La capacidad del disco es {producto.get('Almacenamiento', {}).get('Capacidad_disco', 'no especificada')}."
        elif "almacenamiento" in m and "tipo" in m:
            reply = f"El tipo de disco es {producto.get('Almacenamiento', {}).get('Tipo_disco', 'no especificado')}."
        elif "almacenamiento" in m and "interfaz" in m:
            reply = f"La interfaz del disco es {producto.get('Almacenamiento', {}).get('Interfaz_disco', 'no especificada')}."
        elif ("batería" in m or "bateria" in m) and ("celdas" in m or "número" in m):
            reply = f"La batería tiene {producto.get('Batería', {}).get('Número_celdas', 'no especificado')} celdas."
        elif ("batería" in m or "bateria" in m) and ("duración" in m or "tiempo" in m):
            reply = f"La batería dura {producto.get('Batería', {}).get('Duración', 'no especificada')}."
        elif "gráfica" in m and ("fabricante" in m or "marca" in m):
            reply = f"La gráfica es de {producto.get('Gráfica', {}).get('Fabricante', 'no especificado')}."
        elif "gráfica" in m and ("modelo" in m or "tipo" in m):
            reply = f"El modelo de la gráfica es {producto.get('Gráfica', {}).get('Modelo', 'no especificado')}."
        elif "gráfica" in m and "memoria" in m:
            reply = f"La gráfica tiene {producto.get('Gráfica', {}).get('Memoria', 'no especificada')} de memoria."
        elif "procesador" in m and ("familia" in m or "serie" in m):
            reply = f"La familia del procesador es {producto.get('Procesador', {}).get('Familia', 'no especificada')}."
        elif "procesador" in m and ("modelo" in m or "tipo" in m):
            reply = f"El modelo del procesador es {producto.get('Procesador', {}).get('Modelo', 'no especificado')}."
        elif "procesador" in m and ("frecuencia" in m or "ghz" in m):
            reply = f"La frecuencia del procesador es {producto.get('Procesador', {}).get('Frecuencia', 'no especificada')}."
        elif "pantalla" in m and ("tamaño" in m or "pulgadas" in m):
            reply = f"La pantalla tiene un tamaño de {producto.get('Pantalla', {}).get('Tamaño', 'no especificado')}."
        elif "pantalla" in m and "resolución" in m:
            reply = f"La resolución de la pantalla es {producto.get('Pantalla', {}).get('Resolución', 'no especificada')}."
        elif "pantalla" in m and "tipo" in m:
            reply = f"El tipo de pantalla es {producto.get('Pantalla', {}).get('Tipo', 'no especificado')}."
        elif "pantalla" in m and ("táctil" in m or "tactil" in m):
            tactil = producto.get('Pantalla', {}).get('Táctil', False)
            reply = "La pantalla es táctil." if tactil else "La pantalla no es táctil."
        elif "peso" in m:
            reply = f"El peso del producto es {producto.get('Dimensiones', {}).get('Peso', 'no especificado')}."
        elif "altura" in m:
            reply = f"La altura del producto es {producto.get('Dimensiones', {}).get('Altura', 'no especificada')}."
        elif "ancho" in m:
            reply = f"El ancho del producto es {producto.get('Dimensiones', {}).get('Ancho', 'no especificado')}."
        elif "profundidad" in m:
            reply = f"La profundidad del producto es {producto.get('Dimensiones', {}).get('Profundidad', 'no especificada')}."
        elif "color" in m:
            reply = f"El color del producto es {producto.get('Color', 'no especificado')}."
        elif ("red movil" in m or "red_movil" in m or ("red" in m and ("móvil" in m or "movil" in m))):
            red_movil = producto.get('Conectividad', {}).get('Red_móvil', False)
            reply = "El producto tiene conectividad móvil." if red_movil else "El producto no tiene conectividad móvil."
        elif "ethernet" in m:
            reply = f"La conectividad Ethernet es {producto.get('Conectividad', {}).get('Ethernet', 'no especificada')}."
        elif "bluetooth" in m:
            bluetooth = producto.get('Conectividad', {}).get('Bluetooth', False)
            reply = "El producto tiene Bluetooth." if bluetooth else "El producto no tiene Bluetooth."
        elif "thunderbolt" in m:
            thunderbolt = producto.get('Conectividad', {}).get('Thunderbolt', False)
            reply = "El producto tiene Thunderbolt." if thunderbolt else "El producto no tiene Thunderbolt."
        elif "hdmi" in m:
            hdmi = producto.get('Conectividad', {}).get('HDMI', False)
            reply = "El producto tiene puerto HDMI." if hdmi else "El producto no tiene puerto HDMI."
        elif "ram instalada" in m or ("ram" in m and "instalada" in m):
            reply = f"La memoria RAM instalada es {producto.get('RAM', {}).get('Instalada', 'no especificada')}."
        elif "ram máxima" in m or ("ram" in m and ("máxima" in m or "maxima" in m)):
            reply = f"La memoria RAM máxima es {producto.get('RAM', {}).get('Máxima', 'no especificada')}."
        elif "ram libre" in m or ("ram" in m and "libre" in m):
            reply = f"La memoria RAM libre es {producto.get('RAM', {}).get('Libre', 'no especificada')}."
        elif "ram velocidad" in m or ("ram" in m and "velocidad" in m):
            reply = f"La velocidad de la RAM es {producto.get('RAM', {}).get('Velocidad', 'no especificada')}."
        elif "ram tecnología" in m or ("ram" in m and "tecnología" in m):
            reply = f"La tecnología de la RAM es {producto.get('RAM', {}).get('Tecnología', 'no especificada')}."
        elif "micrófono" in m or "microfono" in m:
            mic = producto.get('Extras', {}).get('Micrófono_integrado', False)
            reply = "El producto tiene micrófono integrado." if mic else "El producto no tiene micrófono integrado."
        elif "webcam" in m:
            webcam = producto.get('Extras', {}).get('Webcam_integrada', False)
            reply = "El producto tiene webcam integrada." if webcam else "El producto no tiene webcam integrada."
        elif "gaming" in m:
            gaming = producto.get('Extras', {}).get('Uso_gaming', False)
            reply = "El producto está orientado al gaming." if gaming else "El producto no está orientado al gaming."
        elif "sistema operativo" in m:
            reply = f"El sistema operativo del producto es {producto.get('Sistema_operativo', 'no especificado')}."
        # --- Fin de intents específicos ---
        # Si no se detecta ningún intent relacionado con el producto...
        elif any(term in m for term in ["hola", "buenos", "qué tal", "cómo estás"]):
            # Usar Azure Conversational Language para preguntas conversacionales
            url = AZ_CONV_ENDPOINT  # Suponemos que este endpoint ya incluye la ruta requerida
            headers = {
                "Ocp-Apim-Subscription-Key": AZ_CONV_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "query": message,
                "projectName": AZ_CONV_PROJECT,
                "deploymentName": AZ_CONV_DEPLOYMENT,
                "api-version": AZ_CONV_API_VERSION
            }
            try:
                conv_response = requests.post(url, headers=headers, json=payload)
                if conv_response.status_code == 200:
                    conv_data = conv_response.json()
                    reply = conv_data.get("answer", "Lo siento, no tengo respuesta para eso.")
                else:
                    reply = "Error en el servicio de Conversational Language."
            except Exception as e:
                reply = "Error al conectar con el servicio de Conversational Language."
                print("Error con Conversational Language:", e)
        else:
            # Para preguntas no relacionadas con Conversational Language, usar GPT-40-mini
            try:
                completion = openai.ChatCompletion.create(
                    engine=GPT40_MINI_DEPLOYMENT,
                    model="gpt-40-mini",
                    messages=[
                        {"role": "system", "content": "Eres un asistente que responde preguntas generales."},
                        {"role": "user", "content": message}
                    ]
                )
                reply = completion.choices[0].message.content
            except Exception as e:
                reply = "Error al generar respuesta con GPT-40-mini."
                print("Error con GPT-40-mini:", e)
    else:
        reply = "No se encontró el producto LG gram en la base de datos."
    
    return jsonify({"reply": reply})

if __name__ == '__main__':
    print("🔥 Servidor Flask corriendo en http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)
