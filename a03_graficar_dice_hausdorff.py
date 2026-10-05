import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def graficar_boxplots_metricas(csv_path: str, output_dir: str, dominio:str, only_non_enhancing:bool = False, exclude_ids: list = None) -> None:
    """
    Lee un archivo CSV con métricas de segmentación, filtra pacientes si es necesario,
    y genera dos gráficos de boxplot (uno para DICE y otro para HD95),
    guardándolos en el directorio especificado.

    Parámetros de entrada:
    csv_path (str): Ruta al archivo CSV que contiene las métricas.
    output_dir (str): Ruta al directorio donde se guardarán los gráficos generados.
    dominio (str): Prefijo de texto para nombrar los archivos de imagen resultantes.
    only_non_enhancing (bool): si solo graficamos la unica clase en gliomas de bajo grado.
    exclude_ids (list, opcional): Lista de identificadores (Patient_ID) a excluir en el análisis.

    Parámetros de salida:
    None
    """
    renombres = {
        'Enhancing': 'Enhancing Tumor',
        'Necrosis and Non-Enhancing': 'Necrosis and Non-Enhancing Tumor',
        'Wholetumor': 'Whole Tumor',
        'Core': 'Core Tumor'
    }

    if only_non_enhancing:
        df = pd.read_csv(csv_path)

        if exclude_ids is not None:
            df = df[~df['Patient_ID'].isin(exclude_ids)]

        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(6, 4), dpi=300)
        ax_dice = sns.boxplot(data=df, y='DICE_Necrosis and Non-Enhancing')
        mediana_dice = df['DICE_Necrosis and Non-Enhancing'].median()
        ax_dice.text(0, mediana_dice, f'{mediana_dice:.3f}', ha='center', va='bottom', color='black', weight='bold')
        plt.title('DICE Coefficient: Necrosis and Non-Enhancing Tumor')
        plt.ylabel('DICE')
        plt.xticks([0], ['Necrosis and Non-Enhancing Tumor'])
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{dominio}_DICE.png"))
        plt.close()

        df_hd95 = df[df['HD95_Necrosis and Non-Enhancing'] <= 300]

        plt.figure(figsize=(6, 4), dpi=300)
        ax_hd95 = sns.boxplot(data=df_hd95, y='HD95_Necrosis and Non-Enhancing')
        mediana_hd95 = df_hd95['HD95_Necrosis and Non-Enhancing'].median()
        ax_hd95.text(0, mediana_hd95, f'{mediana_hd95:.3f}', ha='center', va='bottom', color='black', weight='bold')
        plt.title('Hausdorff Distance (HD95) for Necrosis and Non-Enhancing Tumor')
        plt.ylabel('HD95')
        plt.xticks([0], ['Necrosis and Non-Enhancing Tumor'])
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{dominio}_HD95.png"))
        plt.close()

    else:
        if "clases" in csv_path:
            dice_cols = ['DICE_Edema', 'DICE_Enhancing', 'DICE_Necrosis and Non-Enhancing']
            hd95_cols = ['HD95_Edema', 'HD95_Enhancing', 'HD95_Necrosis and Non-Enhancing']
        elif "regiones" in csv_path:
            dice_cols = ['DICE_Wholetumor', 'DICE_Core', 'DICE_Enhancing']
            hd95_cols = ['HD95_Wholetumor', 'HD95_Core', 'HD95_Enhancing']

        df = pd.read_csv(csv_path)

        if exclude_ids is not None:
            df = df[~df['Patient_ID'].isin(exclude_ids)]

        df_dice = df[['Patient_ID'] + dice_cols].melt(id_vars='Patient_ID', var_name='Region', value_name='DICE')
        df_dice['Region'] = df_dice['Region'].str.replace('DICE_', '')
        df_dice['Region'] = df_dice['Region'].replace(renombres)

        df_hd95 = df[['Patient_ID'] + hd95_cols].melt(id_vars='Patient_ID', var_name='Region', value_name='HD95')
        df_hd95['Region'] = df_hd95['Region'].str.replace('HD95_', '')
        df_hd95['Region'] = df_hd95['Region'].replace(renombres)
        
        df_hd95 = df_hd95[df_hd95['HD95'] <= 300]

        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(9, 4), dpi=300)
        ax_dice = sns.boxplot(data=df_dice, x='Region', y='DICE', hue='Region', palette='Set2', legend=False)
        for tick, label in zip(ax_dice.get_xticks(), ax_dice.get_xticklabels()):
            region_name = label.get_text()
            mediana_val = df_dice[df_dice['Region'] == region_name]['DICE'].median()
            if pd.notnull(mediana_val):
                ax_dice.text(tick, mediana_val, f'{mediana_val:.3f}', ha='center', va='bottom', color='black', weight='bold')
        if "clases" in csv_path:
            plt.title('DICE Coefficient per Class')
        else:
            plt.title('DICE Coefficient per Region')
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{dominio}_DICE.png"))
        plt.close()

        plt.figure(figsize=(9, 4), dpi=300)
        ax_hd95 = sns.boxplot(data=df_hd95, x='Region', y='HD95', hue='Region', palette='Set2', legend=False)
        for tick, label in zip(ax_hd95.get_xticks(), ax_hd95.get_xticklabels()):
            region_name = label.get_text()
            mediana_val = df_hd95[df_hd95['Region'] == region_name]['HD95'].median()
            if pd.notnull(mediana_val):
                ax_hd95.text(tick, mediana_val, f'{mediana_val:.3f}', ha='center', va='bottom', color='black', weight='bold')
        if "clases" in csv_path:
            plt.title('Hausdorff Distance (HD95) per Class')
        else:
            plt.title('Hausdorff Distance (HD95) per Region')
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{dominio}_HD95.png"))
        plt.close()

if __name__ == "__main__":

    for combinacion in ["t1","t1-t2-flair","t1c","t1c-t2","t2-flair","t1c-flair","t2","flair","t1c-t2-flair"]:
        for regiones in ["clases","regiones"]:
            csv_path = f"resultados_metricas/{regiones}/dice_tumorsynth_fleni_glioma_alto_{combinacion}.csv"
            output_dir =f"graficos/fleni/{regiones}"
            dominio = f"tumorsynth_fleni_glioma_alto_{combinacion}"
            graficar_boxplots_metricas(csv_path,output_dir,dominio,False)



    #graficamos por clase: edema, enhancing, necrosis and non enhancing
    
    #graficar_boxplots_metricas("resultados_metricas/clases/dice_tumorsynth_fleni_glioma_alto.csv", "graficos/fleni", "tumorsynth_fleni_glioma_alto_clases", False)
    #graficar_boxplots_metricas("resultados_metricas/clases/dice_tumorsynth_fleni_glioma_bajo.csv", "graficos/fleni", "tumorsynth_fleni_glioma_bajo_clases", True)
    #graficar_boxplots_metricas("resultados_metricas/clases/dice_tumorsynth_lumiere_clases.csv", "graficos/lumiere", "tumorsynth_lumiere_clases", False)

    #graficamos por region: wholetumor, nucleo (enhancing, non-enhancing, necrosis) y enhancing
    
    #graficar_boxplots_metricas("resultados_metricas/regiones/dice_tumorsynth_fleni_glioma_alto_regiones.csv", "graficos/fleni", "tumorsynth_fleni_glioma_alto_regiones", False)
    #graficar_boxplots_metricas("resultados_metricas/regiones/dice_tumorsynth_fleni_glioma_bajo_regiones.csv", "graficos/fleni", "tumorsynth_fleni_glioma_bajo_regiones", False)
    