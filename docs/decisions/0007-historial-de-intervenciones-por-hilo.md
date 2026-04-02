# ADR 0007: Historial de intervenciones por hilo

**Estado**: Propuesto
**Fecha**: 2026-03-30
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0005 (Arquitectura
multi-agente)

## Descripción

Los principios de temporización establecidos en ADR 0003 - cooldown entre
intervenciones, escalada EMT en orden y targeting social por trayectoria -
requieren que el sistema conozca su historial de actuaciones en cada hilo.
Sin este historial, el pipeline ejecuta cada vez desde cero: no puede saber
si ya intervino recientemente, qué nivel de la escalada EMT ya intentó, ni
si un participante que ahora está en silencio era activo hace dos días.

El sistema actual (ADR 0005) no incluye persistencia entre ejecuciones del
pipeline sobre el mismo hilo. Esta decisión añade esa capacidad.

## Decisión

Introducir un componente `ThreadHistoryStore` como parte de las dependencias
del pipeline. El store registra cada intervención generada por el sistema,
indexada por `thread_id`, y es consultada por los nodos del grafo antes de
ejecutar.

### Interfaz (Protocol)

```python
class ThreadHistoryStore(Protocol):
    def get_history(self, thread_id: str) -> list[InterventionRecord]: ...
    def record_intervention(
        self, thread_id: str, record: InterventionRecord
    ) -> None: ...
```

Se usa un `Protocol` (tipado estructural) en lugar de una clase base abstracta
(ABC). La razón: las implementaciones son completamente independientes entre
sí y del archivo de la interfaz. Un mock de test no necesita importar ni
heredar de nada. El patrón sigue el precedente de `LMSBackend` en
`tools/openedx.py`.

### Registro de intervención (`InterventionRecord`)

Cada entrada almacena lo necesario para las tres funciones que habilita:

| Campo | Tipo | Para qué se usa |
|---|---|---|
| `thread_id` | `str` | Clave de búsqueda |
| `timestamp` | `datetime` | Guardia de cooldown |
| `role` | `FacilitationRole` | Escalada EMT; distribución de roles |
| `technique` | `str` | Escalada EMT (qué nivel se usó) |
| `reasoning` | `str` | Auditabilidad - razonamiento completo del clasificador y orquestador |
| `response_text` | `str` | Auditabilidad - texto generado |

El campo `reasoning` preserva la cadena de razonamiento completa, no solo la
salida. Esto cumple el requisito de auditabilidad identificado en ADR 0003
("estructura auditable: se puede inspeccionar qué estado se detectó, qué
acción se seleccionó y por qué").

### Implementaciones

#### `InMemoryThreadStore`

Dict en memoria. Resets al reiniciar el proceso. Uso: desarrollo, tests.

No tiene dependencias externas. Apropiada como implementación por defecto en
el entorno de pruebas y durante el desarrollo del PoC.

#### `SQLiteThreadStore`

Fichero SQLite local. Persiste entre reinicios del proceso. Uso: PoC de la
tesis, demos.

No requiere servidor. Un único fichero configurable por variable de entorno.
Migración al esquema inicial gestionada en el constructor.

### Integración con el pipeline

El store se inyecta a través de `PipelineDeps`, al mismo nivel que
`lms_backend`:

```python
@dataclass
class PipelineDeps:
    lms_backend: LMSBackend
    history_store: ThreadHistoryStore  # nuevo
    # ... resto de deps
```

El nodo `Classifier` llama a `get_history(thread_id)` para:
1. Comprobar si hay una intervención reciente (guardia de cooldown).
2. Incluir el historial de intervenciones previas en su razonamiento, de modo
   que la trayectoria que describe pueda reflejar el contexto real del hilo.

El nodo `Role` (intelectual) llama a `get_history(thread_id)` para determinar
qué nivel EMT intentar.

El nodo `ResponseEval` - o el nodo `Writer` si `ResponseEval` no está activo
- llama a `record_intervention` tras confirmar que la respuesta es viable.

### Camino a producción

En un entorno desplegado, el store se sustituiría por una implementación sobre
PostgreSQL o Redis sin cambios en el pipeline. Al estar inyectado como
dependencia, el cambio es de configuración, no de código. Este patrón es
idéntico al de `LMSBackend`.

## Consecuencias

### Positivas

- Habilita la guardia de cooldown: el sistema puede comprobar si ya intervino
  recientemente en un hilo antes de generar una nueva intervención (ADR 0003).
- Habilita la escalada EMT en orden: el rol intelectual puede inferir qué
  nivel de asistencia ya se intentó y comenzar desde el siguiente (ADR 0004).
- Habilita el targeting social por trayectoria: el sistema puede distinguir
  participantes que declinaron de participantes que nunca contribuyeron
  (ADR 0004; Kim et al., 2021).
- Proporciona auditabilidad completa: el razonamiento detrás de cada
  intervención queda registrado y es consultable.
- Las implementaciones son intercambiables sin cambios en el pipeline.

### Negativas

- Añade una dependencia de infraestructura al pipeline que antes no existía.
  El pipeline ya no es stateless.
- `InMemoryThreadStore` no escala a múltiples procesos ni sobrevive reinicios;
  es adecuada solo para desarrollo y tests.
- `SQLiteThreadStore` no es adecuada para carga concurrente alta. Es suficiente
  para el PoC; una instancia de producción necesitaría PostgreSQL o Redis.
- El `reasoning` almacenado puede contener texto de los mensajes de los
  estudiantes. Requiere gestión de datos personales (GDPR) en despliegues
  reales - este aspecto queda fuera del alcance del PoC.

### Cuestiones abiertas

- ¿Cuánto historial debe retener el store por hilo? ¿Todas las
  intervenciones, o solo las N más recientes?
- ¿Cuál es el periodo de cooldown por defecto? Configurable en `PipelineDeps`
  o fijo por rol.
- ¿Debe el nodo `Classifier` recibir el historial completo o solo la última
  intervención?

## Alternativas Consideradas

- **Sin persistencia, inferir del hilo**: el pipeline podría inferir su
  historial leyendo los mensajes del hilo y detectando los propios. Descartado
  porque requiere identificar mensajes propios en el hilo (no fiable) y no
  preserva el razonamiento interno que no es parte del mensaje visible.
- **Almacenar en `PipelineState`**: el estado mutable dentro de una ejecución
  ya existe, pero no persiste entre ejecuciones sobre el mismo hilo.
  `PipelineState` es correcto para estado intra-ejecución; `ThreadHistoryStore`
  es correcto para estado inter-ejecución.
- **Redis con TTL**: adecuado para la guardia de cooldown, pero descarta el
  razonamiento y no sirve para la escalada EMT ni para auditabilidad.
  Descartado como solución única; puede ser la implementación de producción
  si la auditabilidad se gestiona por separado.

## Referencias

- Baker, R. S. J. d., Corbett, A. T., & Koedinger, K. R. (2004). Detecting
  student misuse of intelligent tutoring systems. *Proceedings of ITS 2004*,
  pp. 531-540.
- Kim, S., Eun, J., Seering, J., & Lee, J. (2021). Moderator chatbot for
  deliberative discussion. *Proceedings of the ACM on Human-Computer
  Interaction*, 5(CSCW1), Article 38.
- Koedinger, K. R., & Aleven, V. (2007). Exploring the assistance dilemma in
  experiments with cognitive tutors. *Educational Psychology Review*, 19(3),
  239-264.
- Lippert, A., Shubeck, K., Morgan, B., Hampton, A., & Graesser, A. (2020).
  Multiple agent designs in conversational intelligent tutoring systems.
  *Technology, Knowledge and Learning*, 25, 443-463.
- Rovai, A. P. (2007). Facilitating online discussions effectively.
- VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent
  tutoring systems, and other tutoring systems. *Educational Psychologist*,
  46(4), 197-221.
