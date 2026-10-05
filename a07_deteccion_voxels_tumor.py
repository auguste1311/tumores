import os
import csv
import re
import shutil
from a00_metadata import hay_tumor

def detectar_tumor_segmentaciones(dir_input, dir_output):
    """
    Recorre los directorios de pacientes, evalúa las imágenes y guarda los resultados en un CSV.
    
    Parámetros:
    dir_input (str): Ruta al directorio donde se encuentran las carpetas de los pacientes.
    dir_output (str): Ruta completa del archivo CSV destino.
    
    Salida:
    None.
    """
    if os.path.isdir(dir_output):
        shutil.rmtree(dir_output)

    directorio_base = os.path.dirname(dir_output)
    if directorio_base:
        os.makedirs(directorio_base, exist_ok=True)

    vistas = ["Vista_1A", "Vista_1B", "Vista_2A", "Vista_2B"]

    with open(dir_output, mode='w', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv, delimiter=';')
        escritor_csv.writerow(["paciente", "Vista_1A", "Vista_1B", "Vista_2A", "Vista_2B"])

        if not os.path.exists(dir_input):
            return

        for nombre_carpeta in os.listdir(dir_input):
            print(f"analizando paciente: {nombre_carpeta}")
            if re.match("NN-*", nombre_carpeta):
                ruta_paciente = os.path.join(dir_input, nombre_carpeta)
                fila = [nombre_carpeta]

                for vista in vistas:
                    print(f"analizando vista: {vista}")
                    ruta_imagen = os.path.join(ruta_paciente, vista, "t1", f"{nombre_carpeta}.nii.gz")
                    
                    if os.path.isfile(ruta_imagen):
                        fila.append(hay_tumor(ruta_imagen))
                    else:
                        print(f"No hay imagen: {ruta_imagen}")
                        
                escritor_csv.writerow(fila)

if __name__ == "__main__":
    detectar_tumor_segmentaciones("images/voluntarios-segmentated","resultados_metricas/detectar_tumor/voluntarios.csv")