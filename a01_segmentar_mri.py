import subprocess
from pathlib import Path
import nibabel as nib
import numpy as np

from a00_metadata import hay_tumor

import subprocess
from pathlib import Path


def segmentar_imagenes_wholetumor(input_dir: str, output_dir: str, identificador: str, combinacion: str) -> None:
    """
    Identifica imagenes de pacientes en un directorio de entrada y ejecuta 
    el segmentador mri_tumorsynth mediante bash para cada paciente, permitiendo
    seleccionar que combinacion especifica de imagenes se utilizara como entrada.

    Parametros de entrada:
    input_dir (str): Ruta de la carpeta que contiene los archivos .nii.gz.
    output_dir (str): Ruta de la carpeta donde se guardaran los archivos resultantes.
    identificador (str): "FLENI", "LUMIERE" O "VENULA" para determinar el formato de los nombres.
    combinacion (str): Letra que define la composicion de los archivos de entrada:
        't1': img_000
        't1-t2-flair': img_0000, img_0002 y img_000
        't1c': img_0001
        't1c-t2': img_0001 y img_0002
        't1c-t2-flair': img_0001, img_0002 y img_0003
        't2-flair': img_0002 y img_0003
        't1c-flair': img_0001 y img_0003
        't2': img_0002
        'flair': img_0003

    Parametros de salida:
    None
    """
    ruta_entrada = Path(input_dir)
    ruta_salida = Path(output_dir)
    ruta_salida.mkdir(parents=True, exist_ok=True)

    if identificador == "FLENI":
        ids_pacientes = set()
        for archivo in ruta_entrada.glob("*_*.nii.gz"):
            partes = archivo.name.split('_')
            if len(partes) > 1:
                id_paciente = partes[1]
                if len(id_paciente) == 3 and id_paciente.isdigit():
                    ids_pacientes.add(id_paciente)

        for paciente in sorted(ids_pacientes):
            img_0000 = ruta_entrada / f"FLENI_{paciente}_0000.nii.gz"
            img_0001 = ruta_entrada / f"FLENI_{paciente}_0001.nii.gz"
            img_0002 = ruta_entrada / f"FLENI_{paciente}_0002.nii.gz"
            img_0003 = ruta_entrada / f"FLENI_{paciente}_0003.nii.gz"
            
            imgs_requeridas = []

            if combinacion == 't1':
                imgs_requeridas = [img_0000]
            elif combinacion == 't1-t2-flair':
                imgs_requeridas = [img_0000, img_0002, img_0003]
            elif combinacion == 't1c':
                imgs_requeridas = [img_0001]
            elif combinacion == 't1c-t2':
                imgs_requeridas = [img_0001, img_0002]
            elif combinacion == 't1c-t2-flair':
                imgs_requeridas = [img_0001, img_0002, img_0003]
            elif combinacion == 't2-flair':
                imgs_requeridas = [img_0002, img_0003]
            elif combinacion == 't1c-flair':
                imgs_requeridas = [img_0001, img_0003]
            elif combinacion == 't2':
                imgs_requeridas = [img_0002]
            elif combinacion == 'flair':
                imgs_requeridas = [img_0003]

            if all(img.exists() for img in imgs_requeridas) and imgs_requeridas:
                argumento_i = ",".join(str(img) for img in imgs_requeridas)
                argumento_o = ruta_salida / f"fleni_{paciente}.nii.gz"

                if argumento_o.exists():
                    print(f"El archivo fleni_{paciente}.nii.gz ya existe. Saltando.")
                    continue

                comando = [
                    "mri_tumorsynth",
                    "--i", argumento_i,
                    "--o", str(argumento_o),
                    "--wholetumor"
                ]
                print(f"Comenzando segmentacion wholetumor el paciente: {paciente}...")
                subprocess.run(comando, check=True)
                print(f"Se segmentó correctamente con wholetumor el paciente: {paciente}!")

    elif identificador == "LUMIERE":
        nombres_base = set()
        for archivo in ruta_entrada.glob("*.nii.gz"):
            if "_000" in archivo.name:
                nombre_base = archivo.name.rsplit('_', 1)[0]
                nombres_base.add(nombre_base)

        for nombre_base in sorted(nombres_base):
            img_0000 = ruta_entrada / f"{paciente}_0000.nii.gz"
            img_0001 = ruta_entrada / f"{nombre_base}_0001.nii.gz"
            img_0002 = ruta_entrada / f"{nombre_base}_0002.nii.gz"
            img_0003 = ruta_entrada / f"{nombre_base}_0003.nii.gz"

            imgs_requeridas = []
            if combinacion == 't1':
                imgs_requeridas = [img_0000]
            elif combinacion == 't1-t2-flair':
                imgs_requeridas = [img_0000, img_0002, img_0003]
            elif combinacion == 't1c':
                imgs_requeridas = [img_0001]
            elif combinacion == 't1c-t2':
                imgs_requeridas = [img_0001, img_0002]
            elif combinacion == 't1c-t2-flair':
                imgs_requeridas = [img_0001, img_0002, img_0003]
            elif combinacion == 't2-flair':
                imgs_requeridas = [img_0002, img_0003]
            elif combinacion == 't1c-flair':
                imgs_requeridas = [img_0001, img_0003]
            elif combinacion == 't2':
                imgs_requeridas = [img_0002]
            elif combinacion == 'flair':
                imgs_requeridas = [img_0003]

            if all(img.exists() for img in imgs_requeridas) and imgs_requeridas:
                argumento_i = ",".join(str(img) for img in imgs_requeridas)
                argumento_o = ruta_salida / f"{nombre_base}.nii.gz"
                
                if argumento_o.exists():
                    print(f"El archivo {nombre_base}.nii.gz ya existe. Saltando.")
                    continue

                comando = [
                    "mri_tumorsynth",
                    "--i", argumento_i,
                    "--o", str(argumento_o),
                    "--wholetumor"
                ]
                
                print(f"Comenzando segmentacion wholetumor para: {nombre_base}...")
                subprocess.run(comando, check=True)
                print(f"Se segmentó correctamente con wholetumor para: {nombre_base}!")

    elif identificador == "VENULA":
        for carpeta in ruta_entrada.iterdir():
            
            if not carpeta.is_dir():
                continue
                
            nombre_carpeta = carpeta.name
            if not (nombre_carpeta.startswith("NN-") or nombre_carpeta.startswith("NNOD-")):
                continue

            ruta_alpaca_output = carpeta / "alpaca-output"
            t1_path = ruta_alpaca_output / "t1_final.nii.gz"
            flair_path = ruta_alpaca_output / "flair_final.nii.gz"

            if not (t1_path.exists() and flair_path.exists()):
                continue

            imgs_requeridas = []
            if combinacion == 't1':
                imgs_requeridas = [t1_path]
            elif combinacion == 'flair':
                imgs_requeridas = [flair_path]
            elif combinacion == 't1-flair':
                imgs_requeridas = [t1_path,flair_path]

            if imgs_requeridas:
                ruta_destino_final = ruta_salida / nombre_carpeta / combinacion
                ruta_destino_final.mkdir(parents=True, exist_ok=True)
                
                argumento_i = ",".join(str(img) for img in imgs_requeridas)
                argumento_o = ruta_destino_final / f"{nombre_carpeta}.nii.gz"

                if argumento_o.exists():
                    print(f"El archivo {argumento_o.name} ya existe. Saltando.")
                    continue

                comando = [
                    "mri_tumorsynth",
                    "--i", argumento_i,
                    "--o", str(argumento_o),
                    "--wholetumor"
                ]

                print(f"Comenzando segmentacion wholetumor para: {nombre_carpeta}...")
                subprocess.run(comando, check=True)
                print(f"Se segmentó correctamente con wholetumor para: {nombre_carpeta}!")
                print(f"Hay tumor: {hay_tumor(argumento_o)}")

    elif identificador == "VOLUNTARIOS":
        if combinacion != 't1':
            print("Combinacion erronea, solo hay t1")
            return

        numeros_validos = {f"{i:02d}" for i in range(1, 18)}
        visitas_validas = {"1A", "1B", "2A", "2B"}

        #print("archivos 1: ", sorted(ruta_entrada.rglob("T1_brain.nii.gz")))

        for archivo in sorted(ruta_entrada.glob("*_*/Visita_*/FSL/BET/T1_brain.nii.gz")):
            
            partes_relativas = archivo.relative_to(ruta_entrada).parts
            if len(partes_relativas) != 5:
                continue

            carpeta_sujeto = partes_relativas[0]
            carpeta_visita = partes_relativas[1]

            partes_sujeto = carpeta_sujeto.split('_')
            if len(partes_sujeto) != 2:
                continue
            xx, yyy = partes_sujeto
            if xx not in numeros_validos or len(yyy) != 3 or not yyy.isalpha():
                continue

            partes_visita = carpeta_visita.split('_')
            if len(partes_visita) != 2:
                continue
            zz = partes_visita[1]
            if zz not in visitas_validas:
                continue

            directorio_destino = ruta_salida / f"NN-0{xx}" / f"Vista_{zz}" / "t1"
            directorio_destino.mkdir(parents=True, exist_ok=True)
            argumento_o = directorio_destino / f"NN-0{xx}.nii.gz"

            if argumento_o.exists():
                print(f"El archivo {argumento_o.name} en Vista_{zz} ya existe. Saltando.")
                continue

            comando = [
                "mri_tumorsynth",
                "--i", str(archivo),
                "--o", str(argumento_o),
                "--wholetumor"
            ]

            print(f"Comenzando segmentacion wholetumor para: NN-0{xx} (Vista_{zz})...")
            subprocess.run(comando, check=True)
            print(f"Se segmento correctamente con wholetumor para: NN-0{xx} (Vista_{zz})!")
            print(f"Hay tumor: {hay_tumor(argumento_o)}")
            

def recortar_roi(dir_wholetumor: str, dir_t1ce: str, output_dir: str, identificador:str) -> None:
    """
    Identifica imagenes en un primer directorio, busca su correspondencia en un 
    segundo directorio y ejecuta el comando fslmaths mediante bash para cada par.

    Parametros de entrada:
    dir_wholetumor (str): Ruta de la carpeta con archivos formato 'fleni_XXX.nii.gz'.
    dir_t1ce (str): Ruta de la carpeta con archivos formato 'FLENI_XXX_0001.nii.gz'.
    output_dir (str): Ruta de la carpeta donde se guardaran los archivos resultantes.

    Parametros de salida:
    None
    """
    ruta_entrada_1 = Path(dir_wholetumor)
    ruta_entrada_2 = Path(dir_t1ce)
    ruta_salida = Path(output_dir)
    
    ruta_salida.mkdir(parents=True, exist_ok=True)

    if identificador == "FLENI":
        for archivo_1 in ruta_entrada_1.glob("fleni_*.nii.gz"):
            partes_nombre = archivo_1.name.split('_')
            
            if len(partes_nombre) > 1:
                id_paciente = partes_nombre[1].split('.')[0]
                
                if len(id_paciente) == 3 and id_paciente.isdigit():
                    archivo_2 = ruta_entrada_2 / f"FLENI_{id_paciente}_0001.nii.gz"
                    
                    if archivo_2.exists():
                        archivo_salida = ruta_salida / f"fleni_{id_paciente}.nii.gz"
                        
                        comando = [
                            "fslmaths",
                            str(archivo_1),
                            "-thr", "17.5",
                            "-uthr", "18.5",
                            "-bin",
                            "-mul", str(archivo_2),
                            str(archivo_salida)
                        ]
                        
                        subprocess.run(comando, check=True)
    elif identificador == "LUMIERE":
        for archivo_1 in ruta_entrada_1.glob("*.nii.gz"):
            nombre_sin_ext = archivo_1.name.replace(".nii.gz", "")
            partes_nombre = nombre_sin_ext.split('_')
            
            if len(partes_nombre) >= 2:
                zzz_yyy = f"{partes_nombre[-2]}_{partes_nombre[-1]}"
                archivos_2 = list(ruta_entrada_2.glob(f"*{zzz_yyy}_0001.nii.gz"))
                
                if archivos_2:
                    archivo_2 = archivos_2[0]
                    archivo_salida = ruta_salida / archivo_1.name
                    
                    comando = [
                        "fslmaths",
                        str(archivo_1),
                        "-thr", "17.5",
                        "-uthr", "18.5",
                        "-bin",
                        "-mul", str(archivo_2),
                        str(archivo_salida)
                    ]
                    
                    subprocess.run(comando, check=True)

def segmentar_roi_innertumor(dir_roi: str, dir_innertumor: str, identificador:str) -> None:
    """
    Parametros de entrada:
    dir_roi (str): Ruta de la carpeta que contiene los archivos originales 'fleni_XXX.nii.gz'.
    dir_innertumor (str): Ruta de la carpeta donde se guardaran las imagenes .

    Parametros de salida:
    None
    """
    ruta_entrada = Path(dir_roi)
    ruta_salida = Path(dir_innertumor)
    
    ruta_salida.mkdir(parents=True, exist_ok=True)

    if identificador == "FLENI":
        for archivo in ruta_entrada.glob("fleni_*.nii.gz"):

            img_data = nib.load(archivo).get_fdata()
            if not np.any(img_data > 0):
                print(f"El ROI para {archivo} está vacío. Saltando segmentación innertumor.")
                continue

            partes_nombre = archivo.name.split('_')
            
            if len(partes_nombre) == 2:
                id_paciente = partes_nombre[1].split('.')[0]

                if len(id_paciente) == 3 and id_paciente.isdigit():
                    archivo_salida = ruta_salida / archivo.name

                    if archivo_salida.exists():
                        print(f"El archivo {archivo_salida.name} ya existe. Saltando.")
                        continue

                    comando = [
                        "mri_tumorsynth",
                        "--i", str(archivo),
                        "--o", str(archivo_salida),
                        "--innertumor"]

                    try:
                        subprocess.run(comando, check=True)

                    except subprocess.CalledProcessError as e:
                        print(f"Saltando paciente {input_path} por error en TumorSynth.")
                        continue
    elif identificador == "LUMIERE":
        for archivo in ruta_entrada.glob("*.nii.gz"):
        
            img_data = nib.load(archivo).get_fdata()
            if not np.any(img_data > 0):
                print(f"El ROI para {archivo.name} esta vacio. Saltando segmentacion innertumor.")
                continue

            archivo_salida = ruta_salida / archivo.name

            if archivo_salida.exists():
                print(f"El archivo {archivo_salida.name} ya existe. Saltando.")
                continue

            comando = [
              "mri_tumorsynth",
              "--i", str(archivo),
              "--o", str(archivo_salida),
              "--innertumor"
            ]

            try:
                subprocess.run(comando, check=True)
            except subprocess.CalledProcessError:
                print(f"Saltando paciente {archivo.name} por error en TumorSynth.")
                continue        
                

if __name__ == "__main__":
    #segmentar_imagenes_wholetumor("proyecto_base/data/FLENI/glioma_bajo_anonimizado/imagesTs","images/fleni/glioma_bajo_anonimizado/labelsTS-wholetumor", "FLENI", "a")
    #recortar_roi("images/fleni/glioma_bajo_anonimizado/labelsTS-wholetumor","proyecto_base/data/FLENI/glioma_bajo_anonimizado/imagesTs","images/fleni/glioma_bajo_anonimizado/labelsTS-roi")
    #segmentar_roi_innertumor("images/fleni/glioma_bajo_anonimizado/labelsTS-roi","images/fleni/glioma_bajo_anonimizado/labelsTS-innertumor")
    
    #segmentar_imagenes_wholetumor("proyecto_base/LUMIERE/imaging_processed/images","images/lumiere/labelsTS-wholetumor", "LUMIERE", "a")
    #recortar_roi("images/lumiere/labelsTS-wholetumor","proyecto_base/LUMIERE/imaging_processed/images","images/lumiere/labelsTS-roi", "LUMIERE")
    #segmentar_roi_innertumor("images/lumiere/labelsTS-roi","images/lumiere/labelsTS-innertumor","LUMIERE")

    for combinacion in ["t1"]:
        
        carpeta_output_wholetumor = f"images/voluntarios-segmentated/"
        #carpeta_output_roi = f"images/fleni/glioma_alto_anonimizado/{combinacion}/labelsTS-roi"
        #carpeta_output_innertumor = f"images/fleni/glioma_alto_anonimizado/{combinacion}/labelsTS-innertumor"
    
        segmentar_imagenes_wholetumor("images/voluntarios-raw",carpeta_output_wholetumor, "VOLUNTARIOS", combinacion)


        #recortar_roi(carpeta_output_wholetumor,"proyecto_base/data/FLENI/glioma_alto_anonimizado/imagesTs",carpeta_output_roi, "FLENI")
        #segmentar_roi_innertumor(carpeta_output_roi,carpeta_output_innertumor,"FLENI")
