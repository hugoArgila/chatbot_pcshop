import os
import fitz  # PyMuPDF

def pdf_to_txt(pdf_filename, output_txt_path):
    try:
        # Ruta completa para los archivos PDF y los archivos de salida
        pdf_path = os.path.join(r"C:\Users\Alumno_AI\Documents\HugoIATradic\ProyectoFinalModulo1\raw_data", pdf_filename)
        
        # Usando PyMuPDF para leer el PDF y extraer el texto
        extracted_text = ""
        
        with fitz.open(pdf_path) as pdf_document:
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)  # Cargar la página
                text = page.get_text("text")  # Extraer el texto
                extracted_text += text + "\n"
        
        # Escribir el texto extraído en el archivo TXT
        output_txt_filename = os.path.splitext(pdf_filename)[0] + ".txt"
        output_txt_full_path = os.path.join(output_txt_path, output_txt_filename)
        
        with open(output_txt_full_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(extracted_text)

        print(f"Texto extraído y guardado en: {output_txt_full_path}")
    
    except Exception as e:
        print(f"Error: {e}")

def process_all_pdfs_in_directory(directory, output_txt_path):
    try:
        # Listar todos los archivos en la carpeta raw_data
        for filename in os.listdir(directory):
            if filename.lower().endswith(".pdf"):  # Solo procesar archivos PDF
                print(f"Procesando archivo: {filename}")
                pdf_to_txt(filename, output_txt_path)
            else:
                print(f"Archivo ignorado (no es un PDF): {filename}")
    except Exception as e:
        print(f"Error al procesar los archivos: {e}")

# Rutas de entrada y salida
raw_data_dir = r"C:\Users\Alumno_AI\Documents\HugoIATradic\ProyectoFinalModulo1\raw_data"
output_txt_dir = r"C:\Users\Alumno_AI\Documents\HugoIATradic\ProyectoFinalModulo1\data"

# Procesar todos los PDFs en la carpeta 'raw_data' y guardar el texto extraído en los archivos TXT
process_all_pdfs_in_directory(raw_data_dir, output_txt_dir)
