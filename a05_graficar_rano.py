import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import seaborn as sns
from collections import Counter
from sklearn.metrics import confusion_matrix, f1_score

def graficar_comparativa_rano(direccion_json: str, direccion_ExpertRANO: str, direccion_output: str) -> None:
    """
    Genera gráficos comparativos de la evolución volumétrica y las clasificaciones RANO
    (IA vs. Experto) para cada paciente, basándose en datos JSON y un archivo CSV.

    Parámetros de entrada:
    - direccion_json (str): Ruta al archivo JSON que contiene las métricas de volumen y RANO calculadas.
    - direccion_ExpertRANO (str): Ruta al archivo CSV con las evaluaciones clínicas expertas.
    - direccion_output (str): Ruta al directorio donde se exportarán las imágenes resultantes.

    Parámetros de salida:
    - Ninguno. La función genera y guarda gráficos en formato PNG en el directorio indicado.
    """
    with open(direccion_json, 'r') as f:
        datos_json = json.load(f)

    df_expert = pd.read_csv(direccion_ExpertRANO)
    col_rating = "Rating (according to RANO, PD: Progressive disease, SD: Stable disease, PR: Partial response, CR: Complete response, Pre-Op: Pre-Operative, Post-Op: Post-Operative)"

    os.makedirs(direccion_output, exist_ok=True)
    plt.style.use('dark_background')

    colores_rano = {
        "Pre-Op": "#ffbb78",
        "Post-Op": "#ff7f0e",
        "SD": "#2ca02c",
        "CR": "#1f77b4",
        "PD": "#aec7e8",
        "PR": "#9467bd",
        "N/A": "#7f7f7f"
    }

    for paciente, info in datos_json.items():
        print(f"Computando paciente: {paciente}...")
        semanas_json = sorted(list(info.get("volumenes_DeepBraTumIA", {}).keys()))
        if not semanas_json:
            continue

        df_paciente = df_expert[df_expert['Patient'] == f"Patient-{paciente}"]
        
        fechas_csv = df_paciente['Date'].tolist()
        ratings_expert = df_paciente[col_rating].tolist()

        if len(semanas_json) != len(fechas_csv):
            continue

        vol_deep = [info.get("volumenes_DeepBraTumIA", {}).get(s, 0) / 1000.0 for s in semanas_json]
        vol_synth = [info.get("volumenes_TumorSynth", {}).get(s, 0) / 1000.0 for s in semanas_json]

        fig = plt.figure(figsize=(16, 6))
        gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)
        
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        ax1.plot(range(len(fechas_csv)), vol_deep, marker='o', color='#8dd3c7', label='DeepBraTumIA')
        ax1.plot(range(len(fechas_csv)), vol_synth, marker='o', color='#ffffb3', label='TumorSynth')
        
        ax1.set_ylabel("Volume/cm^3")
        ax1.set_title(f"Volume and RANO Ratings Over Time for Patient-{paciente}")
        ax1.grid(axis='y', linestyle='--', alpha=0.6)
        ax1.legend(loc="upper right")
        plt.setp(ax1.get_xticklabels(), visible=False)

        clasif_synth = info.get("clasificacion_rano_TumorSynth", {})

        for i in range(len(fechas_csv)):
            semana = semanas_json[i]
            
            cat_expert = str(ratings_expert[i]).strip() if pd.notna(ratings_expert[i]) else "N/A"
            
            if i == 0:
                cat_ai = "Pre-Op"
            elif i == 1:
                cat_ai = "Post-Op"
            else:
                cat_ai = clasif_synth.get(semana, "N/A")

            rect_ai = patches.Rectangle((i - 0.4, 0.55), 0.8, 0.35, color=colores_rano.get(cat_ai, "#7f7f7f"))
            ax2.add_patch(rect_ai)
            ax2.text(i, 0.725, cat_ai, ha='center', va='center', color='white', fontweight='bold', fontsize=10)

            rect_exp = patches.Rectangle((i - 0.4, 0.1), 0.8, 0.35, color=colores_rano.get(cat_expert, "#7f7f7f"))
            ax2.add_patch(rect_exp)
            ax2.text(i, 0.275, cat_expert, ha='center', va='center', color='white', fontweight='bold', fontsize=10)

        ax2.set_xlim(-0.5, len(fechas_csv) - 0.5)
        ax2.set_ylim(0, 1)
        ax2.set_yticks([0.275, 0.725])
        ax2.set_yticklabels(["Expert RANO", "AI RANO"])
        ax2.set_xticks(range(len(fechas_csv)))
        ax2.set_xticklabels(fechas_csv, rotation=45, ha='right')
        ax2.tick_params(axis='y', length=0)
        
        for spine in ax2.spines.values():
            spine.set_visible(False)

        plt.tight_layout()
        ruta_salida = os.path.join(direccion_output, f"RANO_{paciente}.png")
        plt.savefig(ruta_salida, dpi=800, bbox_inches='tight')
        plt.close(fig)

def graficar_matriz_y_f1(direccion_json: str, direccion_output_1: str, direccion_output_2: str) -> None:
    """
    Lee un archivo JSON con las clasificaciones RANO para extraer las etiquetas
    verdaderas y predichas. Genera una matriz de confusión en formato PNG y calcula la métrica F1-score para cada clase, 
    exportándola a un archivo CSV.

    Parámetros de entrada:
    - direccion_json (str): Ruta al directorio o archivo JSON que contiene las métricas RANO.
    - direccion_output_1 (str): Ruta al directorio donde se guardará la imagen de la matriz de confusión.
    - direccion_output_2 (str): Ruta al directorio donde se guardará el archivo CSV con los F1-scores.
    """
    with open(direccion_json, 'r') as f:
        datos = json.load(f)

    y_true = []
    y_pred = []

    for paciente, info in datos.items():
        clasif_gt = info.get("clasificacion_rano_ground_truth", {})
        clasif_pred = info.get("clasificacion_rano_prediccion", {})

        semanas_comunes = set(clasif_gt.keys()).intersection(set(clasif_pred.keys()))

        for semana in semanas_comunes:
            y_true.append(clasif_gt[semana])
            y_pred.append(clasif_pred[semana])

    etiquetas = ["CR", "PR", "SD", "PD"]

    cm = confusion_matrix(y_true, y_pred, labels=etiquetas)

    os.makedirs(direccion_output_1, exist_ok=True)
    
    plt.figure(figsize=(8, 6), dpi=800)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                xticklabels=etiquetas, yticklabels=etiquetas)
    plt.title('Confusion Matrix: TumorSynth RANO')
    plt.xlabel('TumorSynth RANO (Predicted)')
    plt.ylabel('Expert RANO (Ground Truth)')
    plt.tight_layout()
    plt.savefig(os.path.join(direccion_output_1, 'confusion_matrix_rano.png'))
    plt.close()

    f1 = f1_score(y_true, y_pred, labels=etiquetas, average=None, zero_division=0)
    
    df_f1 = pd.DataFrame({
        'Clase': etiquetas,
        'F1_Score': f1
    })

    os.makedirs(direccion_output_2, exist_ok=True)
    df_f1.to_csv(os.path.join(direccion_output_2, 'f1_score_rano.csv'), index=False)


def graficar_matrices_y_metricas(direccion_json: str, direccion_ExpertRANO: str, direccion_output_1: str, direccion_output_2: str) -> None:
    """
    Lee un archivo JSON con predicciones RANO y un CSV con el ground truth experto.
    Genera matrices de confusión para TumorSynth y DeepBraTumIA, y calcula
    el F1-score junto con el chance-level baseline para cada clase, exportando
    los resultados en archivos CSV.

    Parámetros de entrada:
    - direccion_json (str): Ruta al archivo JSON con las métricas de TumorSynth y DeepBraTumIA.
    - direccion_ExpertRANO (str): Ruta al archivo CSV con la clasificación experta RANO.
    - direccion_output_1 (str): Ruta al directorio para guardar las imágenes de las matrices.
    - direccion_output_2 (str): Ruta al directorio para guardar los CSVs con métricas.

    Parámetros de salida:
    - Ninguno. La función guarda imágenes PNG y archivos CSV en los directorios indicados.
    """
    with open(direccion_json, 'r') as f:
        datos = json.load(f)

    df_expert = pd.read_csv(direccion_ExpertRANO)
    col_rating = "Rating (according to RANO, PD: Progressive disease, SD: Stable disease, PR: Partial response, CR: Complete response, Pre-Op: Pre-Operative, Post-Op: Post-Operative)"

    y_true_ts, y_pred_ts = [], []
    y_true_db, y_pred_db = [], []

    etiquetas = ["CR", "PR", "SD", "PD"]

    for paciente, info in datos.items():
        semanas_json = sorted(list(info.get("volumenes_DeepBraTumIA", {}).keys()))
        
        if not semanas_json:
            continue

        df_paciente = df_expert[df_expert['Patient'] == f"Patient-{paciente}"]
        
        if df_paciente.empty or len(df_paciente) != len(semanas_json):
            print(f"salteando paciente: {paciente}...")
            continue

        ratings_expert = df_paciente[col_rating].astype(str).str.strip().tolist()
        clasif_ts = info.get("clasificacion_rano_TumorSynth", {})
        clasif_db = info.get("clasificacion_rano_DeepBraTumIA", {})

        for i, semana in enumerate(semanas_json):
            gt = ratings_expert[i]

            if semana in clasif_ts and gt in etiquetas:
                pred_ts = clasif_ts[semana]
                if pred_ts in etiquetas:
                    y_true_ts.append(gt)
                    y_pred_ts.append(pred_ts)

            if semana in clasif_db and gt in etiquetas:
                pred_db = clasif_db[semana]
                if pred_db in etiquetas:
                    y_true_db.append(gt)
                    y_pred_db.append(pred_db)

    os.makedirs(direccion_output_1, exist_ok=True)
    os.makedirs(direccion_output_2, exist_ok=True)

    modelos = [
        ("TumorSynth", y_true_ts, y_pred_ts),
        ("DeepBraTumIA", y_true_db, y_pred_db)
    ]

    for modelo, y_t, y_p in modelos:
        if not y_t:
            continue

        cm = confusion_matrix(y_t, y_p, labels=etiquetas)

        plt.figure(figsize=(8, 6), dpi=800)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                    xticklabels=etiquetas, yticklabels=etiquetas)
        plt.title(f'Confusion Matrix: {modelo} RANO')
        plt.xlabel(f'{modelo} RANO (Predicted)')
        plt.ylabel('Expert RANO (Ground Truth)')
        plt.tight_layout()
        plt.savefig(os.path.join(direccion_output_1, f'confusion_matrix_{modelo}.png'))
        plt.close()

        f1 = f1_score(y_t, y_p, labels=etiquetas, average=None, zero_division=0)
        
        total_muestras = len(y_t)
        contador_clases = Counter(y_t)
        chance_level = [contador_clases.get(clase, 0) / total_muestras if total_muestras > 0 else 0 for clase in etiquetas]

        df_metricas = pd.DataFrame({
            'Clase': etiquetas,
            'F1_Score': f1,
            'Chance_Level': chance_level
        })
        
        df_metricas.to_csv(os.path.join(direccion_output_2, f'metricas_{modelo}.csv'), index=False)


def graficar_matrices_y_metricas_rano(direccion_json: str, direccion_ExpertRANO: str, direccion_output_1: str, direccion_output_2: str) -> None:
    """
    Lee un archivo JSON con predicciones volumétricas y un CSV con el ground truth experto.
    Filtra las semanas etiquetadas como "Pre-Op" o "Post-Op", alinea las semanas entre 
    el CSV y el JSON, y genera dos matrices de confusión y dos archivos CSV con métricas 
    (F1-score y chance-level baseline) para los modelos TumorSynth y DeepBraTumIA.

    Parámetros de entrada:
    - direccion_json (str): Ruta al archivo JSON con las métricas y predicciones de los modelos.
    - direccion_ExpertRANO (str): Ruta al archivo CSV con la clasificación experta (ground truth).
    - direccion_output_1 (str): Ruta al directorio donde se guardarán las matrices de confusión (.png).
    - direccion_output_2 (str): Ruta al directorio donde se guardarán los archivos con métricas (.csv).

    Parámetros de salida:
    - None
    """
    with open(direccion_json, 'r') as f:
        datos_json = json.load(f)

    df_expert = pd.read_csv(direccion_ExpertRANO)
    col_rating = "Rating (according to RANO, PD: Progressive disease, SD: Stable disease, PR: Partial response, CR: Complete response, Pre-Op: Pre-Operative, Post-Op: Post-Operative)"

    gt_dict = {}
    for _, row in df_expert.iterrows():
        rating = str(row[col_rating]).strip()
        
        if pd.isna(row[col_rating]) or rating in ["Pre-Op", "Post-Op", "nan", "N/A"]:
            
            continue
            
        patient_id = str(row['Patient']).replace("Patient-", "")
        week_id = str(row['Date']).replace("week-", "")
        
        if patient_id not in gt_dict:
            gt_dict[patient_id] = {}
        gt_dict[patient_id][week_id] = rating

    y_true_deep = []
    y_pred_deep = []
    y_true_synth = []
    y_pred_synth = []

    for paciente, info in datos_json.items():
        if paciente not in gt_dict:
            print(f"saltenando paciente: {paciente}...")
            continue

        gt_paciente = gt_dict[paciente]
        pred_deep = info.get("clasificacion_rano_DeepBraTumIA", {})
        pred_synth = info.get("clasificacion_rano_TumorSynth", {})

        for semana, true_rating in gt_paciente.items():
            if semana in pred_deep:
                y_true_deep.append(true_rating)
                y_pred_deep.append(pred_deep[semana])
                
            if semana in pred_synth:
                y_true_synth.append(true_rating)
                y_pred_synth.append(pred_synth[semana])

    etiquetas = ["CR", "PR", "SD", "PD"]

    os.makedirs(direccion_output_1, exist_ok=True)
    os.makedirs(direccion_output_2, exist_ok=True)

    modelos = [
        ("DeepBraTumIA", y_true_deep, y_pred_deep),
        ("TumorSynth", y_true_synth, y_pred_synth)
    ]

    for modelo, y_true, y_pred in modelos:
        if not y_true:
            continue

        cm = confusion_matrix(y_true, y_pred, labels=etiquetas)

        plt.figure(figsize=(10, 8), dpi=800)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                    xticklabels=etiquetas, yticklabels=etiquetas)
        plt.title(f'Confusion Matrix: {modelo} RANO')
        plt.xlabel(f'{modelo} RANO (Predicted)')
        plt.ylabel('Expert RANO (Ground Truth)')
        plt.tight_layout()
        plt.savefig(os.path.join(direccion_output_1, f'confusion_matrix_{modelo}.png'))
        plt.close()

        f1 = f1_score(y_true, y_pred, labels=etiquetas, average=None, zero_division=0)
        
        total_instances = len(y_true)
        chance_levels = [y_true.count(c) / total_instances if total_instances > 0 else 0 for c in etiquetas]

        df_metrics = pd.DataFrame({
            'Clase': etiquetas,
            'F1_Score': f1,
            'Chance_Level_Baseline': chance_levels
        })

        df_metrics.to_csv(os.path.join(direccion_output_2, f'metricas_{modelo}.csv'), index=False)

if __name__ == "__main__":

    #graficar_comparativa_rano("resultados_metricas/rano/resultados_rano.json", "proyecto_base/LUMIERE/LUMIERE-ExpertRating-v202211.csv" ,"graficos/rano")
    graficar_matrices_y_metricas_rano("resultados_metricas/rano/resultados_rano.json","proyecto_base/LUMIERE/LUMIERE-ExpertRating-modificado.csv","graficos/rano-matriz","resultados_metricas/rano/")
