### Paso a paso para ejecutar desde tu carpeta de imágenes 

**1. Navega a tu carpeta de imágenes**
Abre tu terminal y ubícate directamente donde están los archivos `.nii.gz`:

```bash
cd ruta/hacia/tumores/imagenes

```

*(Asegúrate de reemplazar `ruta/hacia/` con la ubicación real en tu disco).*

**2. Ejecuta el Docker desde allí**
Como estás parado en `imagenes`, necesitas llamar al script que está "una carpeta más arriba y luego dentro de TumorSynth/docker". El comando sería así:

```bash
../TumorSynth/docker/docker_run.sh

```

Al hacer esto, Docker tomará tu carpeta `imagenes` y la compartirá internamente. El contenedor de Docker está configurado para utilizar tu directorio actual como el directorio de trabajo por defecto.

**3. Activa el entorno (Dentro de Docker)**
Una vez que el prompt de tu terminal cambie (indicando que el contenedor ya arrancó y estás adentro), debes activar el entorno Conda necesario antes de correr la herramienta:

```bash
source /opt/init.sh

```

**4. Ejecuta TumorSynth**
Ahora, como el Docker está "viendo" directamente el interior de tu carpeta `imagenes`, no necesitas poner rutas largas. Simplemente llama a tus archivos por su nombre, siguiendo el formato del manual:

```bash
mri_tumorsynth --i tu_imagen_t1ce.nii.gz --o mascara_resultado.nii.gz --id WholeTumor

```

¡Y listo! El archivo `mascara_resultado.nii.gz` aparecerá mágicamente en tu carpeta local `tumores/imagenes`, ya que esa carpeta está conectada en tiempo real con el contenedor.

