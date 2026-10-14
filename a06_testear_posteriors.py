import os
import glob
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

def generar_histograma_mascara(dir_input, dir_output):
    """
    Busca un archivo .nii.gz en el directorio de entrada, extrae los valores de 
    probabilidad de la máscara y genera un histograma. El gráfico resultante 
    se guarda como un archivo .png en el directorio de salida.

    Parámetros:
    dir_input (str): Ruta al directorio que contiene el archivo de máscara .nii.gz.
    dir_output (str): Ruta al directorio donde se guardará el histograma en formato .png.

    Salida:
    None
    """
    os.makedirs(dir_output, exist_ok=True)
    
    imagen = nib.load(dir_input)
    datos = imagen.get_fdata()
    
    valores = datos[datos > 0.01]
    
    plt.figure(figsize=(8, 6))
    plt.hist(valores, bins=50, color='indigo', alpha=0.8)
    plt.title('Histograma de la Máscara de Probabilidades')
    plt.xlabel('Valor de Probabilidad')
    plt.ylabel('Frecuencia')
    plt.grid(True, alpha=0.3)

    nombre_base = os.path.basename(dir_input).replace('.nii.gz', '_histograma.png')
    ruta_salida = os.path.join(dir_output, nombre_base)

    #print(f"ruta archivo: {dir_input}, nombre base: {nombre_base}, ruta salida: {ruta_salida}")
    plt.savefig(ruta_salida, bbox_inches='tight')
    plt.close()



if __name__ == "__main__":
    # generar_histograma_mascara("images/pruebas/fleni_000_0001_prob_label18.nii.gz","images/pruebas/")
    # generar_histograma_mascara("images/pruebas/roi_fleni_000_0001_prob_class0.nii.gz","images/pruebas/")
    # generar_histograma_mascara("images/pruebas/roi_fleni_000_0001_prob_class1.nii.gz","images/pruebas/")
    # generar_histograma_mascara("images/pruebas/roi_fleni_000_0001_prob_class2.nii.gz","images/pruebas/")
    # generar_histograma_mascara("images/pruebas/roi_fleni_000_0001_prob_class3.nii.gz","images/pruebas/")
    for i in range(1,10):
        source = f"images/voluntarios-segmentated/NN-00{i}/Vista_1A/t1/NN-00{i}_prob_label18.nii.gz"
        dst = f"images/pruebas/voluntarios/NN-00{i}/Vista_1A/t1/"
        generar_histograma_mascara(source,dst)