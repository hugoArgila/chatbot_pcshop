import re
from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_cors import CORS
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

# --- Configuración para Azure Conversational Language (si se usa) ---
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
    
@app.route('/chatbot', methods=['GET'])
def chatbot():
    return render_template('chatbot.html')

@app.route('/productos/<codigo>', methods=['GET'])
def obtener_producto(codigo):
    # Buscar el producto en la colección correspondiente de MongoDB
    producto = None
    for coleccion_nombre in db.list_collection_names():
        coleccion = db[coleccion_nombre]
        producto = coleccion.find_one({"Código_producto": codigo})
        if producto:
            break  # Si encontramos el producto, no necesitamos seguir buscando

    if producto:
        # Limpiar el campo '_id' antes de devolver la respuesta
        producto['_id'] = str(producto['_id'])
        return jsonify(producto)  # Respuesta en formato JSON
    else:
        return jsonify({"error": "Producto no encontrado"}), 404


@app.route('/detalles/<codigo_producto>')
def detalles_producto(codigo_producto):
    producto = db['productos'].find_one({'codigo': codigo_producto})
    if producto:
        return render_template('detalles.html', producto=producto)
    return render_template('detalles.html', error='Producto no encontrado')

@app.route('/detalles/<codigo>', methods=['GET'])
def get_producto_detalles(codigo_producto):
    # Suponiendo que tienes una colección llamada 'productos' en tu base de datos MongoDB
    producto = db.productos.find_one({'codigo_producto': codigo})
    
    if producto is None:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    # Convertir el ObjectId de MongoDB a string para JSON
    producto['_id'] = str(producto['_id'])
    
    # Devolver los detalles del producto en formato JSON
    return jsonify(producto), 200


# Ruta /chatbot combinada
@app.route('/chatbot', methods=['POST'])
def chatbot_query():
    data = request.get_json()
    message = data.get('message', '')
    m = message.lower()

    # --- PARTE 1: BÚSQUEDA GLOBAL CON FILTROS EXTRAÍDOS ---
    # Mapeo de palabras clave a campos numéricos (atributos) de los productos.
    # Agrega o modifica los atributos según tus necesidades.
    attribute_mapping = {
    # Atributos de RAM
    "ram": ("RAM", "Instalada"),
    "ram instalada": ("RAM", "Instalada"),
    "ram máxima": ("RAM", "Máxima"),
    "ram libre": ("RAM", "Libre"),
    "velocidad ram": ("RAM", "Velocidad"),
    
    # Atributos de almacenamiento/disco
    "almacenamiento": ("Almacenamiento", "Capacidad_disco"),
    "disco": ("Almacenamiento", "Capacidad_disco"),
    "capacidad disco": ("Almacenamiento", "Capacidad_disco"),
    
    # Atributos de precio (si se almacena numéricamente)
    "precio": ("Precio", None),
    
    # Atributos de la batería
    "numero celdas bateria": ("Batería", "Número_celdas"),
    "celdas bateria": ("Batería", "Número_celdas"),
    "duracion bateria": ("Batería", "Duración"),
    
    # Atributos de la gráfica (por ejemplo, memoria de la gráfica en GB)
    "memoria grafica": ("Gráfica", "Memoria"),
    
    # Atributos del procesador
    "frecuencia procesador": ("Procesador", "Frecuencia"),
    
    # Atributos de la pantalla
    "tamano pantalla": ("Pantalla", "Tamaño"),
    
    # Atributos de las dimensiones
    "peso": ("Dimensiones", "Peso"),
    "altura": ("Dimensiones", "Altura"),
    "ancho": ("Dimensiones", "Ancho"),
    "profundidad": ("Dimensiones", "Profundidad")
    }


    # Extraer condiciones numéricas del mensaje.
    # Se asume que los valores se expresan en GB (por ejemplo, "32 gb").
    conditions = {}
    for keyword, field_path in attribute_mapping.items():
        if keyword in m:
            match = re.search(r'(\d+)\s*gb', m)
            if match:
                conditions[keyword] = float(match.group(1))

    # Si se extrajeron condiciones, realizamos la búsqueda global.
    if conditions:
        matching_products = []
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            for product in collection.find():
                cumple_todas = True  # Bandera: el producto debe cumplir todas las condiciones.
                for keyword, required_value in conditions.items():
                    field, subfield = attribute_mapping[keyword]
                    attr_value_str = product.get(field, {}).get(subfield, "")
                    try:
                        attr_value = float(''.join(ch for ch in attr_value_str if ch.isdigit() or ch == '.'))
                    except Exception as e:
                        attr_value = 0
                    if attr_value < required_value:
                        cumple_todas = False
                        break
                if cumple_todas:
                    product['_id'] = str(product['_id'])
                    matching_products.append(product)
        if matching_products:
            return jsonify(matching_products), 200
        else:
            return jsonify({"reply": "No se encontraron productos que cumplan con las condiciones especificadas."}), 200

    # --- PARTE 2: RESPUESTAS BASADAS EN INTENTS DEL PRODUCTO ---
    # Si no se extrajeron condiciones, se busca un producto (cualquiera) para responder intents específicos.
    colecciones = db.list_collection_names()
    producto = None
    for coleccion_nombre in colecciones:
        coleccion = db[coleccion_nombre]
        # Se usa una regex que coincida con cualquier nombre (.*)
        producto = coleccion.find_one({"Nombre_producto": {"$regex": ".*", "$options": "i"}})
        if producto:
            break

    if producto:
        print("Tipo de 'producto':", type(producto))
    else:
        print("No se encontró ningún producto.")

    producto_encontrado = False
    reply_parts = []

    if producto:
        if "precio" in m:
            reply_parts.append(
                f"El precio del {producto.get('Nombre_producto', 'producto')} es {producto.get('Precio', 'no especificado')}."
            )
            producto_encontrado = True
        if "código" in m or "codigo" in m:
            reply_parts.append(
                f"El código del producto es {producto.get('Código_producto', 'no especificado')}."
            )
            producto_encontrado = True
        if "garantía" in m or "garantia" in m:
            reply_parts.append(
                f"La garantía del producto es {producto.get('Garantía', 'no especificada')}."
            )
            producto_encontrado = True
        if "almacenamiento" in m:
            if "capacidad" in m or "gb" in m:
                reply_parts.append(
                    f"La capacidad del disco es {producto.get('Almacenamiento', {}).get('Capacidad_disco', 'no especificada')}."
                )
                producto_encontrado = True
            if "tipo" in m:
                reply_parts.append(
                    f"El tipo de disco es {producto.get('Almacenamiento', {}).get('Tipo_disco', 'no especificado')}."
                )
                producto_encontrado = True
            if "interfaz" in m:
                reply_parts.append(
                    f"La interfaz del disco es {producto.get('Almacenamiento', {}).get('Interfaz_disco', 'no especificada')}."
                )
                producto_encontrado = True
        if "batería" in m or "bateria" in m:
            if "celdas" in m or "número" in m:
                reply_parts.append(
                    f"La batería tiene {producto.get('Batería', {}).get('Número_celdas', 'no especificado')} celdas."
                )
                producto_encontrado = True
            if "duración" in m or "tiempo" in m:
                reply_parts.append(
                    f"La batería dura {producto.get('Batería', {}).get('Duración', 'no especificada')}."
                )
                producto_encontrado = True
        if "color" in m:
            reply_parts.append(
                f"El color del producto es {producto.get('Color', 'no especificado')}."
            )
            producto_encontrado = True
        if "sistema operativo" in m:
            reply_parts.append(
                f"El sistema operativo del producto es {producto.get('Sistema_operativo', 'no especificado')}."
            )
            producto_encontrado = True

    if producto_encontrado:
        reply = " ".join(reply_parts)
    else:
        # Fallback: usar GPT-40-mini para responder la consulta de forma general.
        try:
            completion = openai.ChatCompletion.create(
                engine=GPT40_MINI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "Eres un asistente que responde preguntas generales."},
                    {"role": "user", "content": message}
                ]
            )
            reply = completion.choices[0].message.content
        except Exception as e:
            reply = "Error al generar respuesta con GPT-40-mini."
            print("Error con GPT-40-mini:", e)

    return jsonify({"reply": reply})

if __name__ == '__main__':
    print("🔥 Servidor Flask corriendo en http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)
