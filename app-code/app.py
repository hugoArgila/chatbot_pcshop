from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_cors import CORS  # Importar flask-cors
from bson import ObjectId

# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Habilitar CORS para todas las rutas
CORS(app)

# Configuración de MongoDB con Cosmos DB
MONGO_URL = os.getenv('MONGO_URL')  # URL de conexión desde el .env
DATABASE_NAME = os.getenv('DATABASE_NAME')  # Nombre de la base de datos

try:
    # Conexión a Cosmos DB con TLS
    client = MongoClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)
    db = client[DATABASE_NAME]
    print("✅ Conexión establecida con Cosmos DB")
except Exception as e:
    print("❌ Error al conectar a Cosmos DB:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/productos', methods=['GET'])
def obtener_productos():
    try:
        # Intentar obtener todas las colecciones
        try:
            colecciones = db.list_collection_names()
        except:
            # Workaround si no funciona list_collection_names()
            colecciones = db.command("listCollections").get("cursor", {}).get("firstBatch", [])
            colecciones = [c['name'] for c in colecciones]

        print(f"📂 Colecciones encontradas: {colecciones}")

        productos_list = []

        for coleccion_nombre in colecciones:
            coleccion = db[coleccion_nombre]
            productos = list(coleccion.find())  # Convertir cursor a lista

            if len(productos) == 0:
                print(f"⚠️ No hay productos en la colección '{coleccion_nombre}'.")

            for producto in productos:
                print(f"📦 Producto encontrado en '{coleccion_nombre}': {producto}")

                # Convertir ObjectId a string
                producto['_id'] = str(producto['_id'])

                # Formatear los datos
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

        return jsonify(productos_list), 200  # Devolver todos los productos

    except Exception as e:
        print("❌ Se produjo un error:", e)
        return jsonify({"error": str(e)}), 500  # Manejo de errores
    
@app.route('/productos/<codigo_producto>')
def detalles_producto(codigo_producto):
    producto = db['productos'].find_one({'codigo': codigo_producto})
    if producto:
        return jsonify(producto)  # Devuelve el producto como JSON
    return jsonify({'error': 'Producto no encontrado'}), 404


if __name__ == '__main__':
    print("🔥 Servidor Flask corriendo en http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)