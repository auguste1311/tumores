import os
import glob
import csv
import numpy as np
import pandas as pd
import SimpleITK as sitk
#import itk
from medpy import metric

def create_region_from_mask(mask, join_labels: tuple):
    mask_new = np.zeros_like(mask, dtype=np.uint8)
    for l in join_labels:
        mask_new[mask == l] = 1
    return mask_new

def compute_hd95(ref, pred):
    num_ref = np.sum(ref)
    num_pred = np.sum(pred)
    if num_ref == 0:
        if num_pred == 0:
            return 0
        else:
            return 373.12866
    elif num_pred == 0 and num_ref != 0:
        return 373.12866
    else:
        return metric.hd95(pred, ref, (1, 1, 1))

def sort_key(filepath):
    filename = os.path.basename(filepath).replace('.nii.gz', '')
    parts = filename.split('_')
    if len(parts) >= 2:
        return (parts[-1], parts[-2])
    return ('', '')

def metricas_imagen_por_region(dir_groundtruth: str, dir_tumorsynth: str, output_csv: str, regiones:str) -> None:
    """
    Calcula los coeficientes DICE y Hausdorff (HD95) entre segmentaciones 
    Ground Truth y TumorSynth, unificando las clases correspondientes.
    Identifica los archivos con el formato *_YYY_XXX.nii.gz, asigna el 
    Patient_ID como YYY_XXX, ordena su procesamiento primero por XXX 
    y luego por YYY, y escribe los resultados en el CSV línea a línea.

    Parámetros de entrada:
    dir_groundtruth (str): Ruta al directorio con archivos ground truth (*_YYY_XXX.nii.gz).
    dir_tumorsynth (str): Ruta al directorio con archivos de tumorsynth (*_YYY_XXX.nii.gz).
    output_csv (str): Ruta y nombre del archivo CSV de salida para guardar los resultados.
    regiones (str): si calcula la metrica por region o clases

    Parámetros de salida:
    None
    """


    if "FLENI" in dir_groundtruth:
        print("procesando las metricas de FLENI...")
        gt_files = sorted(glob.glob(os.path.join(dir_groundtruth, '*_*.nii.gz')))
        ts_files = sorted(glob.glob(os.path.join(dir_tumorsynth, '*_*.nii.gz')))

        evaluations = []

        if regiones == "clases":
            regions_gt = {
                'Edema': (1,),
                'Enhancing': (3,),
                'Necrosis and Non-Enhancing': (2,4)}
            regions_ts = {
                'Edema': (1,),
                'Enhancing': (3,),
                'Necrosis and Non-Enhancing': (2,)}

        elif regiones == "regiones":
            regions_gt = {
                'Wholetumor':(1,2,3,4),
                'Core':(2,3,4),
                'Enhancing':(3,)
            }
            regions_ts ={
                'Wholetumor':(1,2,3),
                'Core':(2,3),
                'Enhancing':(3,)
            }

        for gt_path in gt_files:
            basename = gt_path.split('_')[-1]
            ts_path_matches = [f for f in ts_files if f.endswith(basename)]
            
            if not ts_path_matches:
                print(f"No se encontro coincidencia para: {gt_path}")
                continue
                
            ts_path = ts_path_matches[0]
            patient_id = basename.split('.')[0]
            print(f"Computando paciente: {patient_id}")
            image_gt = sitk.GetArrayFromImage(sitk.ReadImage(gt_path))
            image_ts = sitk.GetArrayFromImage(sitk.ReadImage(ts_path))

            row_data = {'Patient_ID': patient_id}

            for region_name in regions_gt.keys():
                labels_gt = regions_gt[region_name]
                labels_ts = regions_ts[region_name]

                mask_gt = create_region_from_mask(image_gt, labels_gt)
                mask_ts = create_region_from_mask(image_ts, labels_ts)

                dc = np.nan if np.sum(mask_gt) == 0 and np.sum(mask_ts) == 0 else metric.dc(mask_ts, mask_gt)
                hd95 = compute_hd95(mask_gt, mask_ts)

                row_data[f'DICE_{region_name}'] = dc
                row_data[f'HD95_{region_name}'] = hd95

            evaluations.append(row_data)

        df_results = pd.DataFrame(evaluations)
        df_results.to_csv(output_csv, index=False)


    elif "LUMIERE" in dir_groundtruth:

        gt_files = sorted(glob.glob(os.path.join(dir_groundtruth, '*_*_*.nii.gz')), key=sort_key)
        ts_files = glob.glob(os.path.join(dir_tumorsynth, '*_*_*.nii.gz'))

        if regiones == "clases":
            regions_gt = {
                'Edema': (3,),
                'Enhancing': (1,),
                'Necrosis and Non-Enhancing': (2,)}
            regions_ts = {
                'Edema': (1,),
                'Enhancing': (2,),
                'Necrosis and Non-Enhancing': (3,)}
            fieldnames = [
                'Patient_ID', 
                'DICE_Edema', 'HD95_Edema', 
                'DICE_Enhancing', 'HD95_Enhancing', 
                'DICE_Necrosis and Non-Enhancing', 'HD95_Necrosis and Non-Enhancing'
            ]

        elif regiones == "regiones":
            regions_gt = {
                'Wholetumor':(1,2,3),
                'Core':(1,2),
                'Enhancing':(1,)
            }
            regions_ts ={
                'Wholetumor':(1,2,3),
                'Core':(2,3),
                'Enhancing':(2,)
            }
            fieldnames = [
                'Patient_ID', 
                'DICE_Wholetumor', 'HD95_Wholetumor', 
                'DICE_Core', 'HD95_Core', 
                'DICE_Enhancing', 'HD95_Enhancing'
            ]

        with open(output_csv, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for gt_path in gt_files:
                basename = os.path.basename(gt_path)
                name_without_ext = basename.replace('.nii.gz', '')
                parts = name_without_ext.split('_')
                
                if len(parts) < 2:
                    continue
                    
                yyy_xxx = f"{parts[-2]}_{parts[-1]}"
                patient_id = yyy_xxx

                ts_path_matches = [f for f in ts_files if f.endswith(f"_{yyy_xxx}.nii.gz")]
                
                if not ts_path_matches:
                    print(f"No se encontro coincidencia para: {gt_path}")
                    continue
                    
                ts_path = ts_path_matches[0]

                print(f"Computando semana_paciente: {patient_id}")

                image_gt = sitk.GetArrayFromImage(sitk.ReadImage(gt_path))
                image_ts = sitk.GetArrayFromImage(sitk.ReadImage(ts_path))

                row_data = {'Patient_ID': patient_id}

                for region_name in regions_gt.keys():
                    labels_gt = regions_gt[region_name]
                    labels_ts = regions_ts[region_name]

                    mask_gt = create_region_from_mask(image_gt, labels_gt)
                    mask_ts = create_region_from_mask(image_ts, labels_ts)

                    dc = np.nan if np.sum(mask_gt) == 0 and np.sum(mask_ts) == 0 else metric.dc(mask_ts, mask_gt)
                    hd95 = compute_hd95(mask_gt, mask_ts)

                    row_data[f'DICE_{region_name}'] = dc
                    row_data[f'HD95_{region_name}'] = hd95

                writer.writerow(row_data)

if __name__ == "__main__":

    for combinacion in ["t1","t1-t2-flair","t1c","t1c-t2","t2-flair","t1c-flair","t2","flair"]:
        for regiones in ["clases","regiones"]:
            carpeta_groundtruth = f"proyecto_base/data/FLENI/glioma_alto_anonimizado/labelsTs"
            carpeta_segmentacion = f"images/fleni/glioma_alto_anonimizado/{combinacion}/labelsTS-innertumor"
            carpeta_output_csv = f"resultados_metricas/{regiones}/dice_tumorsynth_fleni_glioma_alto_{combinacion}.csv"

            metricas_imagen_por_region(carpeta_groundtruth,carpeta_segmentacion,carpeta_output_csv, regiones)
    