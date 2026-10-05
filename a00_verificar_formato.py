import os

def verificar_guiones_bajos(ruta_carpeta: str, cant) -> bool:
    """
    Lee todos los archivos de una carpeta y devuelve un valor booleano indicando 
    si hay algun nombre de archivo que contenga mas de 3 caracteres '_'.

    Parametros de entrada:
    ruta_carpeta (str): Ruta absoluta o relativa de la carpeta a analizar.

    Parametros de salida:
    bool: True si existe al menos un archivo con mas de 3 guiones bajos en su nombre. 
          False en caso contrario o si la carpeta no existe.
    """
    try:
        for nombre_archivo in os.listdir(ruta_carpeta):
            ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
            if os.path.isfile(ruta_completa):
                if nombre_archivo.count('_') != cant:
                    return nombre_archivo
        return False
    except FileNotFoundError:
        return False

print(verificar_guiones_bajos("proyecto_base/LUMIERE/imaging_processed/images/", 4), verificar_guiones_bajos("proyecto_base/LUMIERE/imaging_processed/labels/",3))