# ADR 0022: Backend stub y desarrollo offline

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0010 (Puntos de integración), ADR 0014 (Infraestructura de
evaluación), ADR 0021 (Patrón de registro)

## Descripción

El pipeline requiere un backend de LMS para recuperar el hilo de discusión
(`LMSBackend.get_thread`). En desarrollo local, en pruebas automatizadas, y en
los experimentos de evaluación, no hay un LMS disponible. Se necesita un
mecanismo para ejecutar el pipeline sin depender de una instancia de Open edX.

## Decisión

`StubLMSBackend` es un backend de LMS que sirve hilos desde un diccionario en
memoria:

```python
class StubLMSBackend(LMSBackend, key="stub"):
    def __init__(self, threads: dict[str, DiscussionThread] | None = None):
        self._threads: dict[str, DiscussionThread] = threads or {}

    def register(self, thread: DiscussionThread) -> None:
        self._threads[thread.id] = thread

    async def get_thread(self, thread_id: str) -> DiscussionThread:
        return self._threads[thread_id]
```

Se activa con `FACILITATION_LMS_BACKEND=stub`. No hay dependencias externas,
no hay persistencia, no hay red.

### Usos actuales del stub

**Evaluación experimental**: el runner `eval-models` crea el pipeline con
`lms_backend="stub"` y carga los hilos de los fixtures antes de cada ejecución.
Los seis hilos de evaluación (ADR 0023) son instancias de `DiscussionThread`
registradas en el stub en tiempo de ejecución.

**Tests automatizados**: los tests de integración crean instancias de
`StubLMSBackend` con hilos específicos y los inyectan en `PipelineDeps`. Esto
permite verificar el comportamiento del pipeline sin llamas al LMS.

**Playground local**: durante el desarrollo, el pipeline se puede ejecutar
localmente con un hilo definido a mano registrado en el stub, sin necesidad de
tener Open edX en ejecución.

### Por qué no mockar el backend en los tests

Una alternativa es usar `unittest.mock.AsyncMock` para sustituir `get_thread`
en los tests. El stub es preferible porque:

- El stub implementa la misma interfaz pública que el backend real. Los tests
  que usan el stub verifican la ruta completa de inyección de dependencias.
- Un mock de `get_thread` no valida que el resto del código llame al método
  correcto con los argumentos correctos.
- El stub es reutilizable y nombrado: añadirlo a la configuración de test
  (`conftest.py`) crea un vocabulario compartido, no una serie de mocks anónimos.

### Separación entre stub y fixtures

El stub (`StubLMSBackend`) es mecanismo de transporte: sirve cualquier
`DiscussionThread` que se le registre. Los fixtures de evaluación (`threads.py`)
son contenido: hilos concretos con participación, mensajes y contexto académico
definidos.

Esta separación permite reutilizar el stub en tests unitarios con hilos mínimos
y en los experimentos con hilos realistas de evaluación, sin mezclar el contenido
con el mecanismo.

## Consecuencias

### Positivas

- El pipeline se puede desarrollar, testear y evaluar sin un LMS real.
- El diseño offline-first permite iterar sobre el pipeline sin esperar a que
  la integración con Open edX esté lista.
- El stub y el backend real implementan la misma interfaz: cambiar de stub a
  OpenEdXBackend no requiere modificar el código del pipeline.
- Los experimentos de evaluación son completamente reproducibles porque los hilos
  están definidos en código, no recuperados de una instancia externa.

### Negativas

- El stub no replica la latencia, la paginación, ni los formatos de error reales
  del API de Open edX. Los tests que usan el stub no detectan problemas de
  integración en la capa HTTP.
- El diccionario en memoria no persiste entre ejecuciones. Si un experimento
  largo falla a mitad, el estado del stub no está disponible para reinspectar.
- El stub no implementa autenticación ni control de acceso. El comportamiento
  del sistema ante errores de autenticación solo puede verificarse con el backend
  real.

### Cuestiones abiertas

- ¿Debe el stub soportar persistencia opcional (por ejemplo, cargar hilos de un
  fichero JSON) para facilitar la reproducción de escenarios ad hoc sin
  modificar el código?
- ¿Debe existir un modo de logging más detallado en el stub para diagnosticar
  qué hilos se registraron y cuáles se solicitaron durante un experimento?

## Alternativas consideradas

- **Mocks de `unittest.mock`**: sustituyen el método `get_thread` en los tests.
  Más compactos para tests unitarios, pero no validan la ruta de inyección de
  dependencias y no son reutilizables fuera de los tests. Descartado como
  mecanismo principal.
- **Ficheros JSON como fuente de hilos**: el stub carga hilos desde ficheros
  JSON en disco. Permite definir hilos fuera del código Python, pero añade
  serialización y deserialización sin beneficio para el caso de uso actual.
  Descartado.
- **Servidor HTTP local que imita el API de Open edX**: replica mejor el
  comportamiento real pero añade complejidad operativa sin aportar valor en la
  fase de prototipo. Puede ser relevante en integración.

## Referencias

- ADR 0010: puntos de integración; define la interfaz `LMSBackend`.
- ADR 0014: infraestructura de evaluación; documenta el uso del stub en el runner.
- ADR 0021: patrón de registro; documenta cómo el stub se registra como backend.
