# DDA-0044: Almacenamiento de resultados de evaluación en S3

## Estado

Aceptado

## Contexto

Los resultados de las evaluaciones se persisten actualmente en el sistema de archivos local bajo `docs/experiments/results/`. En el servidor EC2, esto implica que los resultados se pierden si la instancia se termina o se reconstruye. Los resultados acumulados hasta la fecha representan trabajo experimental valioso que no debería depender de la disponibilidad de la instancia.

El servicio ya dispone de credenciales de AWS para ECR. Añadir acceso a S3 no requiere infraestructura adicional. El código tiene una abstracción `RunResultStore` con un registro de backends, pensada precisamente para soportar múltiples destinos de almacenamiento.

El módulo `evals/artifacts.py` ha crecido hasta 700 líneas mezclando modelos Pydantic, helpers de parseo, backends de almacenamiento y funciones públicas. La incorporación de un nuevo backend es el momento natural para dividirlo en módulos cohesivos.

## Decisión

Decidimos añadir `S3RunResultStore` como backend de almacenamiento para resultados de evaluación, activable mediante la variable de entorno `FACILITATION_RUN_RESULTS_BACKEND=s3`, y dividir `evals/artifacts.py` en cuatro módulos enfocados: `models.py`, `store.py`, `s3_store.py` y un `artifacts.py` reducido con solo las funciones públicas.

## Consecuencias

### Positivas

- Los resultados de evaluación sobreviven a reinicios y reconstrucciones del servidor EC2.
- El sistema de archivos local sigue recibiendo escrituras; S3 actúa como espejo adicional, no como sustituto exclusivo.
- La configuración `FACILITATION_RUN_RESULTS_BACKEND=filesystem` (valor por defecto) mantiene el comportamiento actual sin cambios para entornos locales.
- El módulo `evals/` queda dividido en unidades con responsabilidad única, más fáciles de leer y testear.
- Los resultados se organizan por entorno (`local`, `ec2`, `idril`), permitiendo distinguir el origen de cada ejecución.

### Negativas

- Añadimos la dependencia `boto3`, que aumenta el tamaño del entorno y requiere credenciales de AWS en producción.
- La operación `list_runs()` sobre S3 requiere múltiples peticiones GET (una por manifiesto), lo que puede ser lento si el número de ejecuciones crece mucho.
- Los resultados existentes no se migran automáticamente; la migración inicial es una operación manual.

## Alternativas Consideradas

- **Solo filesystem en EC2 con volumen EBS persistente**: descartada porque requiere gestionar montajes de volumen y aumenta la complejidad del despliegue sin añadir durabilidad frente a errores de instancia.
- **Base de datos (PostgreSQL)**: descartada porque añade una dependencia de infraestructura significativa para un caso de uso que es esencialmente almacenamiento de documentos JSON.
- **Mantener `artifacts.py` sin dividir**: descartada porque el fichero ya supera las 700 líneas y añadir otro backend lo haría aún menos manejable.
