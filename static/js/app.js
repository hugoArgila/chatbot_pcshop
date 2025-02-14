// Función para cargar productos en la página principal
async function cargarProductos() {
    try {
        const response = await axios.get('/productos');
        const productos = response.data;
        const catalogo = document.getElementById('catalogo');
        catalogo.innerHTML = ''; // Limpiar antes de cargar

        productos.forEach(producto => {
            // Comprobamos que las propiedades necesarias no sean undefined ni vacías
            if (producto.nombre && producto.precio && producto._id && producto.imagen !== undefined) {
                console.log('ID del producto:', producto._id); // Depuración
                
                // Crear un nuevo div para el producto
                const productoDiv = document.createElement('div');
                productoDiv.className = 'widget';

                // Si no hay imagen, usar imagen por defecto
                const imagenUrl = producto.imagen || 'default-image.jpg';

                // Llenamos el HTML del widget con los detalles del producto
                productoDiv.innerHTML = `
                    <img src="${imagenUrl}" alt="${producto.nombre}">
                    <h3>${producto.nombre}</h3>
                    <p>${producto.precio}€</p>
                    <a href="/detalles/${producto._id}" class="boton">Ver detalles</a>
                `;
                
                // Añadimos el widget al catálogo
                catalogo.appendChild(productoDiv);
            } else {
                // Si algún valor clave es undefined o vacío, no mostrar el producto
                console.log(`Producto con ID ${producto._id} omitido debido a datos incompletos`);
            }
        });
    } catch (error) {
        console.error('Error al cargar los productos:', error);
    }
}

window.addEventListener('load', cargarProductos);
