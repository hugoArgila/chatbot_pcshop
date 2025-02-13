// Función para cargar productos
async function cargarProductos() {
    try {
        const response = await axios.get('/productos');  // Aquí deberías tener una API que te devuelva los productos
        const productos = response.data;
        const catalogo = document.getElementById('catalogo');

        console.log('Productos recibidos:', productos); // Verifica los datos

        productos.forEach(producto => {
            const productoDiv = document.createElement('div');
            productoDiv.className = 'widget'; // Añadimos clase para estilo

            productoDiv.innerHTML = `
                <!-- Imagen del producto -->
                <img src="${producto.imagen || 'default-image.jpg'}" alt="${producto['Nombre_producto']}">

                <!-- Nombre del producto -->
                <h3>${producto['Nombre_producto']}</h3>

                <!-- Precio del producto -->
                <p>${producto['Precio']}</p>

                <!-- Botón para ver más detalles -->
                <button class="boton" onclick="mostrarDetalles('${producto._id}')">Ver más</button>

                <!-- Detalles del producto -->
                <div class="producto-info" id="info-${producto._id}" style="display: none;">
                    <p><strong>Descripción:</strong> ${producto['Descripción'] || 'No disponible'}</p>
                    <p><strong>Características:</strong> 
                        ${producto['RAM'] ? `RAM: ${producto['RAM'].Instalada}` : 'N/A'} 
                        | 
                        ${producto['Almacenamiento'] ? `Almacenamiento: ${producto['Almacenamiento'].Capacidad_disco}` : 'N/A'}
                    </p>
                    <p><strong>Garantía:</strong> ${producto['Garantía']}</p>
                    <p><strong>Procesador:</strong> ${producto['Procesador'].Modelo}</p>
                    <p><strong>Batería:</strong> ${producto['Batería'].Duración}</p>
                    <p><strong>Dimensiones:</strong> Peso: ${producto['Dimensiones'].Peso}</p>
                </div>
            `;
            catalogo.appendChild(productoDiv);
        });
    } catch (error) {
        console.error('Error al cargar los productos:', error);
    }
}

// Función para mostrar detalles de un producto (opcional)
function mostrarDetalles(id) {
    const infoDiv = document.getElementById(`info-${id}`);
    if (infoDiv.style.display === 'none') {
        infoDiv.style.display = 'block';
    } else {
        infoDiv.style.display = 'none';
    }
}

// Llamamos a la función para cargar los productos cuando la página se cargue
window.onload = function() {
    cargarProductos();
};
