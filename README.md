﻿﻿﻿﻿﻿﻿﻿﻿# entel-discount-report Procesamiento de ficheros planos para generación de reportes financieros asociados a descuentos aplicados en planes tarifarios al contratar una segunda línea dentro de Perú. ## 1 Instrucciones de ejecuciónEs necesario que el equipo cuente con una versión de Python3.X instalada, para la ejecución desde la terminal de Linux:$python view.pyPara la ejecución desde Windows se dispone del archivo discount-report.exe##Instrucciones de uso*- Ejecute el programa. Dispondrá de una ventana para seleccionar el directorio donde se encuentra el archivo (Es necesario indicar el directorio donde se encuentra el archivo que desea ser analizado).*- Se leerá el archivo y se creará un directorio llamada reports con los reportes solicitados: 1. financial-report.txt = reporte con las estadísticas financieras.2. execution-report.txt = reporte con las estadísticas de ejecución. 3. ejecución.discarded-records.txt = listado de líneas descartadas.Sugerencia: Cree un directorio nuevo que solo contenga el archivo que desea ser analizado, la carpeta reports se creará dentro de este directorio.