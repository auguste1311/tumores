import os
import json
import nibabel as nib
import numpy as np
from collections import defaultdict

def calcular_indice_rano(direccion_ground_truth, direccion_segmentaciones, direccion_output):
    """
    Calcula el índice RANO a partir de las diferencias volumétricas en segmentaciones de tumores a lo largo del tiempo.

    Parámetros de entrada:
    - direccion_ground_truth (str): Ruta al directorio con las imágenes de segmentación reales, nombradas como "*_XXX_YYY.nii.gz".
    - direccion_segmentaciones (str): Ruta al directorio con las imágenes predichas, nombradas como "*_XXX_YYY.nii.gz".
    - direccion_output (str): Ruta al directorio donde se guardará el archivo JSON resultante.

    Parámetros de salida:
    - No tiene valor de retorno. Escribe un archivo 'resultados_rano.json' en el directorio de salida especificado.
    """
    archivos_gt = [f for f in os.listdir(direccion_ground_truth) if f.endswith('.nii.gz')]
    
    pacientes = defaultdict(list)
    for archivo in archivos_gt:
        partes = archivo.replace('.nii.gz', '').split('_')
        if len(partes) >= 2:
            semana = partes[-2]
            paciente = partes[-1]
            pacientes[paciente].append((semana, archivo))
            
    resultados = {}
    
    for paciente in sorted(pacientes.keys()):
        print(f"calculando RANO para paciente: {paciente}...")
        semanas_ordenadas = sorted(pacientes[paciente], key=lambda x: x[0])
        
        historial_volumenes_gt = {}
        historial_volumenes_pred = {}
        clasificacion_rano_gt = {}
        clasificacion_rano_pred = {}
        
        volumenes_gt_lista = []
        volumenes_pred_lista = []
        semanas_validas = []
        
        for semana, archivo in semanas_ordenadas:
            ruta_gt = os.path.join(direccion_ground_truth, archivo)
            ruta_pred = os.path.join(direccion_segmentaciones, archivo)
            
            if not os.path.exists(ruta_pred):
                continue
                
            img_gt = nib.load(ruta_gt).get_fdata()
            img_pred = nib.load(ruta_pred).get_fdata()
            
            vol_gt = int(np.sum(img_gt == 1))
            vol_pred = int(np.sum(img_pred == 2))
            
            historial_volumenes_gt[semana] = vol_gt
            historial_volumenes_pred[semana] = vol_pred
            
            volumenes_gt_lista.append(vol_gt)
            volumenes_pred_lista.append(vol_pred)
            semanas_validas.append(semana)
            
        for i in range(1, len(semanas_validas)):
            semana_actual = semanas_validas[i]
            
            vt_gt = volumenes_gt_lista[i]
            vt_1_gt = volumenes_gt_lista[i-1]
            
            if vt_1_gt == 0:
                delta_gt = 0 if vt_gt == 0 else float('inf')
            else:
                delta_gt = ((vt_gt - vt_1_gt) / vt_1_gt) * 100
                
            if delta_gt == -100:
                clase_gt = "CR"
            elif -100 < delta_gt <= -65:
                clase_gt = "PR"
            elif delta_gt > 40:
                clase_gt = "PD"
            else:
                clase_gt = "SD"
                
            clasificacion_rano_gt[semana_actual] = clase_gt

            vt_pred = volumenes_pred_lista[i]
            vt_1_pred = volumenes_pred_lista[i-1]
            
            if vt_1_pred == 0:
                delta_pred = 0 if vt_pred == 0 else float('inf')
            else:
                delta_pred = ((vt_pred - vt_1_pred) / vt_1_pred) * 100
                
            if delta_pred == -100:
                clase_pred = "CR"
            elif -100 < delta_pred <= -65:
                clase_pred = "PR"
            elif delta_pred > 40:
                clase_pred = "PD"
            else:
                clase_pred = "SD"
                
            clasificacion_rano_pred[semana_actual] = clase_pred
            
        resultados[paciente] = {
            "volumenes_ground_truth": historial_volumenes_gt,
            "volumenes_prediccion": historial_volumenes_pred,
            "clasificacion_rano_ground_truth": clasificacion_rano_gt,
            "clasificacion_rano_prediccion": clasificacion_rano_pred
        }
        
    os.makedirs(direccion_output, exist_ok=True)
    ruta_salida = os.path.join(direccion_output, 'resultados_rano.json')
    with open(ruta_salida, 'w') as f:
        json.dump(resultados, f, indent=4)

if __name__ == "__main__":
    calcular_indice_rano("proyecto_base/LUMIERE/imaging_processed/labels","images/lumiere/labelsTS-innertumor","resultados_metricas/rano/" )