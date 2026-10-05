import nibabel as nib
import numpy as np

def imprimir_metadata_nifti(ruta_imagen: str) -> None:
    """
    Carga una imagen NIfTI y muestra por consola toda su metadata, 
    incluyendo las dimensiones, el tipo de dato, la matriz afin y el encabezado completo.

    Parametros:
    - ruta_imagen (str): Ruta completa al archivo .nii o .nii.gz.

    Retorna:
    - None
    """
    img = nib.load(ruta_imagen)
    
    print("Informacion Basica:")
    print(f"Dimensiones: {img.shape}")
    print(f"Tipo de dato: {img.get_data_dtype()}")
    
    print("\nMatriz Afin:")
    print(img.affine)
    
    print("\nEncabezado Completo:")
    print(img.header)


def analizar_informacion_nifti(ruta_imagen: str) -> None:
    """
    Carga una imagen NIfTI y muestra por consola su metadata básica,
    la matriz afín, el encabezado completo y realiza un conteo de los 
    valores únicos (clases) y la cantidad de vóxeles correspondientes a cada uno.

    Parametros:
    - ruta_imagen (str): Ruta completa al archivo .nii o .nii.gz.

    Retorna:
    - None
    """
    img = nib.load(ruta_imagen)
    
    print("Informacion Basica:")
    print(f"Dimensiones: {img.shape}")
    print(f"Tipo de dato: {img.get_data_dtype()}")
    
    print("\nMatriz Afin:")
    print(img.affine)
    
    print("\nEncabezado Completo:")
    print(img.header)
    
    datos = img.get_fdata()
    clases, conteos = np.unique(datos, return_counts=True)
    
    print("\nAnalisis de Segmentacion (Clases y Voxeles):")
    for clase, conteo in zip(clases, conteos):
        print(f"Clase {clase}: {conteo} voxeles")

def hay_tumor(ruta_imagen: str) -> bool:
    """
    Carga una segmentacion de wholetumor de tumorSynth en formato NIfTI y devuelve True si hay tumor, False en caso contrario.

    Parametros:
    - ruta_imagen (str): Ruta completa al archivo .nii o .nii.gz.

    Retorna:
    - Bool
    """
    img = nib.load(ruta_imagen)
    datos = img.get_fdata()
    clases, conteos = np.unique(datos, return_counts=True)
    return int(clases[-1]) == 18
    

if __name__ == "__main__":
    hay_tumor("images/fleni/glioma_alto_anonimizado/t1c-t2-flair/labelsTS-wholetumor/fleni_000.nii.gz")
    hay_tumor("images/fleni/glioma_bajo_anonimizado/labelsTS-wholetumor/fleni_007.nii.gz")