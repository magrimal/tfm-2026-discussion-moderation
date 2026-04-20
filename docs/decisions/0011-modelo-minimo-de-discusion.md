# DDA-0011: Modelo mínimo de discusión y mecanismo de extensibilidad de plataforma

## Estado

Propuesto

## Contexto

El pipeline necesita datos de discusión como entrada. La implementación actual
tiene dos capas de modelos: `OpenEdXThread`/`OpenEdXComment` representan la
respuesta de la API, y `DiscussionThread`/`Comment` son los modelos de dominio
genéricos. La función `map_thread()` convierte entre ambas capas.

Este patrón asume que existe un modelo de dominio genérico al que todas las
plataformas deben adaptarse. En la práctica esto genera tres problemas:

- Añadir una plataforma nueva requiere implementar modelos de respuesta de API
  y un mapper hacia los modelos genéricos.
- El cuerpo del hilo (argumento de apertura) se inserta artificialmente como
  el primer elemento de `children`, lo que obliga a todos los consumidores a
  conocer esa convención.
- Campos como `learning_objectives` viven en `DiscussionThread` aunque no
  provienen de la API del hilo, lo que mezcla datos de plataforma con contexto
  inyectado externamente.

La API de Open edX ya separa el cuerpo del hilo (`raw_body`) de los comentarios.
No hay razón para colapsar esa distinción en el modelo interno.

## Decisión

Reemplazamos el modelo de dominio genérico y el mapper por un Protocol mínimo
(`DiscussionContext`, `CommentContext`) que especifica solo los campos que el
pipeline necesita. Los backends de plataforma implementan el Protocol
directamente con sus propios tipos.

Un Protocol en Python (módulo `typing`) define una interfaz estructural: cualquier
clase que tenga los atributos o métodos declarados satisface el Protocol
automáticamente, sin necesidad de herencia explícita. El pipeline puede recibir
cualquier objeto que cumpla la interfaz, independientemente de su tipo concreto.

El Protocol mínimo es:

```python
class CommentContext(Protocol):
    body: str
    author: str
    author_label: str | None
    created_at: datetime
    endorsed: bool
    replies: Sequence["CommentContext"]

class DiscussionContext(Protocol):
    id: str
    title: str
    body: str           # argumento de apertura del hilo
    author: str
    thread_type: str    # "discussion" | "question"
    course_id: str
    created_at: datetime
    closed: bool
    has_endorsed: bool
    comments: Sequence[CommentContext]
```

Open edX es la implementación inicial. `OpenEdXDiscussionContext` implementa
el Protocol sobre la respuesta nativa de la API v1: `raw_body` se expone como
`body`, `type` como `thread_type`, y `children` de cada comentario como
`replies`. No existe un paso de conversión a un modelo genérico intermedio.

El contexto del curso (`CourseContext`, que incluye `learning_objectives`)
permanece como argumento separado inyectado por el llamador. No forma parte
del Protocol de discusión.

Para añadir soporte a otra plataforma, se implementa el Protocol para el
formato nativo de esa plataforma. El pipeline no cambia.

## Consecuencias

### Positivas

- No hay conversión entre tipos concretos. El backend de Open edX devuelve un
  `OpenEdXDiscussionContext` que el pipeline usa directamente.
- Extender a una nueva plataforma equivale a implementar el Protocol, no a
  escribir un mapper hacia un modelo genérico.
- El cuerpo del hilo y los comentarios son campos distintos. No hay convención
  implícita sobre `children[0]`.
- Los campos inyectados externamente (objetivos de aprendizaje) permanecen
  separados y no contaminan el modelo de discusión.

### Negativas

- Campos específicos de plataforma que no están en el Protocol (por ejemplo,
  `vote_count` por comentario, `abuse_flagged` por comentario) no son accesibles
  a través de la interfaz. Si los agentes los necesitan, el Protocol debe
  extenderse o el agente debe recibir el tipo específico de plataforma, lo que
  rompe la abstracción.
- El Protocol es tipado estructuralmente. Requiere disciplina al añadir campos:
  un campo nuevo en el Protocol es un cambio que todas las implementaciones
  deben cubrir.

## Alternativas consideradas

- **Mantener el modelo genérico y el mapper**: descartado porque obliga a
  todo backend nuevo a escribir una conversión completa, y el modelo genérico
  acumula campos que no todas las plataformas pueden cubrir.
- **Modelo genérico sin mapper (Open edX como único target)**: descartado porque
  acopla el diseño del pipeline al formato de Open edX sin hacerlo explícito, y
  no deja un punto de extensión claro para otras plataformas.

## Preguntas abiertas

- ¿Debe el Protocol incluir `vote_count` a nivel de comentario para facilitar
  la detección de participación de alta calidad? Diferido hasta que los agentes
  lo requieran.
- ¿Cómo se obtiene el `CourseContext` cuando el pipeline se llama con un
  `thread_id`? El backend de Open edX puede usar el `course_id` incluido en la
  respuesta del hilo para hacer la llamada adicional a la API de bloques del
  curso. El diseño de esa llamada queda fuera del alcance de este ADR.
