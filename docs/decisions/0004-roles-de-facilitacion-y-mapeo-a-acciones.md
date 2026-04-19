# ADR 0004: Roles de facilitación y mapeo a acciones

**Estado**: Propuesto
**Fecha**: 2026-03-11
**Depende de**: ADR 0002 (Repertorio de técnicas), ADR 0003 (Modelo de
intervención)

## Descripción

El modelo de intervención (ADR 0003) organiza las acciones de la Fase 2 en
cinco categorías: organizacionales, intelectuales, sociales, de moderación y
afectivas. Esta organización necesita una justificación teórica que explique
por qué estas categorías y no otras, y cómo se fundamentan en la literatura
sobre roles del facilitador en discusiones en línea.

## Decisión

Adoptar un marco de tres roles de facilitación — organizacional, intelectual
y social — como estructura que fundamenta las categorías de acción del modelo
de intervención. Los tres roles provienen de una línea de investigación
convergente que se inicia con Paulsen (1995) y se confirma en múltiples
taxonomías independientes.

### Origen: la clasificación de Paulsen (1995)

Paulsen (1995), basándose en el trabajo de Feenberg (1989), Hiltz (1988) y
Mason (1991) sobre moderación en comunicación mediada por computadora,
propuso una clasificación de la participación del instructor en tres roles
interrelacionados (citado en Abdous, 2011, p. 62):

| Rol | Función según Paulsen |
|-----|----------------------|
| **Organizacional** | Clarificar objetivos de discusión, establecer calendario, definir reglas de procedimiento y normas de toma de decisiones |
| **Social** | Crear un entorno amigable y propicio para el aprendizaje, dar la bienvenida a los estudiantes, fomentar la participación, modelar comportamiento y proporcionar retroalimentación constructiva de forma amable |
| **Intelectual** | Mantener la discusión enfocada en puntos clave, resumir ideas principales, animar a los estudiantes a expandir y construir sobre los comentarios de otros |

### Convergencia con otras taxonomías

Múltiples clasificaciones independientes convergen en una estructura
equivalente, con variaciones terminológicas pero roles funcionalmente
similares:

| Fuente | Rol organizacional | Rol intelectual | Rol social |
|--------|-------------------|----------------|-----------|
| Paulsen (1995) | Organizacional | Intelectual | Social |
| Berge (1995) | Managerial | Pedagogical | Social |
| Coppola et al. (2002) | Managerial | Cognitive | Affective |
| Pilkington (2003) | Management | Argumentation | Community building |
| Baker (2011) | Managerial | Pedagogical | — (implícito) |
| Abdous (2011) | Managerial | Pedagogical | Social |

**Fuentes factuales para cada fila**:

- **Berge (1995)**: Propuso un modelo de cuatro dimensiones — pedagogical,
  social, managerial y technical — similar al de Paulsen pero con la adición
  de un rol *technical* orientado a competencias tecnológicas del instructor.
  El modelo fue revisado para incluir entornos virtuales y sigue siendo válido
  (Berge, 2008). Citado en Abdous (2011, p. 62).
- **Coppola et al. (2002)**: Mediante análisis de patrones identificaron tres
  roles que los docentes necesitan desarrollar al transicionar a entornos en
  línea: *cognitive* (procesos mentales de aprendizaje, almacenamiento de
  información y pensamiento), *affective* (relación instructor-estudiantes,
  expresión de emociones) y *managerial* (gestión de clase y curso). Citado
  en Abdous (2011, p. 62).
- **Pilkington (2003)**: Identifica tres clases de roles en el análisis del
  diálogo educativo: *community building* (construcción de comunidad),
  *management* (gestión) y *argumentation* (argumentación).
- **Baker (2011)**: Define dos roles principales para el diseño y orquestación
  de discusiones en línea: *pedagogical* (diseño de preguntas, contenido) y
  *managerial* (organización de grupos, parámetros, normas). El rol social
  está presente en sus recomendaciones pero no se nombra como categoría
  separada.
- **Abdous (2011)**: Sintetiza el consenso emergente como cuatro roles —
  pedagogical, managerial, social y technical — y lo organiza en un marco de
  tres fases temporales (Before, During, After). El rol *technical* se
  excluye de nuestro alcance porque corresponde a competencias tecnológicas
  del instructor, no a acciones de facilitación en la discusión (Abdous,
  2011, p. 63).

**Nota**: Berge (1995) y Abdous (2011) incluyen un cuarto rol *technical*
relacionado con la competencia tecnológica del instructor. Este rol queda
fuera del alcance del sistema de facilitación porque no corresponde a acciones
de intervención en el hilo de discusión.

### La taxonomía empírica de Blignaut & Trollip (2003)

Blignaut & Trollip (2003) desarrollaron una taxonomía de seis categorías
mediante análisis de contenido empírico de publicaciones de instructores en
18 cursos de posgrado. Las categorías resultantes fueron: Administrative,
Affective, Other, Corrective, Informative y Socratic (Blignaut & Trollip,
2003, Tabla 3).

Esta taxonomía, derivada inductivamente de datos, se mapea a los tres roles:

| Categoría Blignaut & Trollip | Rol correspondiente |
|------------------------------|-------------------|
| Administrative | Organizacional |
| Affective | Social |
| Corrective | Intelectual |
| Informative | Intelectual |
| Socratic | Intelectual |
| Other | — (fuera de los tres roles) |

Tres de las seis categorías (Corrective, Informative, Socratic) corresponden
al rol intelectual, lo que indica que este rol es el más diverso en cuanto a
tipos de acción. El rol social se concentra en una categoría (Affective) y
el organizacional en otra (Administrative).

### Mapeo de las categorías de acción (ADR 0003) a los tres roles

Las cinco categorías de acción del modelo de intervención se mapean a los
tres roles:

| Categoría de acción (ADR 0003) | Rol de facilitación | Justificación |
|-------------------------------|-------------------|--------------|
| Acciones organizacionales | **Organizacional** | Lanzar discusión, sintetizar, cerrar, redirigir. Corresponden a la gestión de la estructura y flujo de la discusión (Paulsen, 1995; Baker, 2011, Rol Managerial) |
| Acciones intelectuales | **Intelectual** | Responder con contenido, redirigir malentendidos, conectar contribuciones, aportar fuentes. Corresponden a mantener la discusión enfocada y profundizar el pensamiento (Paulsen, 1995; Blignaut & Trollip, 2003, categorías Corrective, Informative y Socratic) |
| Acciones sociales y de participación | **Social** | Fomentar participación, redistribuir atención, gestionar conflictos. Corresponden a crear un entorno propicio y gestionar la dinámica social (Paulsen, 1995; Coppola et al., 2002, rol Affective) |
| Acciones afectivas | **Social** | Reconocer y reforzar positivamente. Corresponden a la retroalimentación constructiva y el apoyo emocional del rol social (Paulsen, 1995; Blignaut & Trollip, 2003, categoría Affective) |
| Acciones de moderación (pasiva) | — (rol distinto) | Señalar contenido inapropiado para revisión. No corresponde a facilitación sino a moderación (Korre et al., 2025, Apéndice C). Queda fuera del marco de tres roles |

Las acciones sociales y las acciones afectivas comparten el mismo rol
(social). Se mantienen como categorías separadas en ADR 0003 porque sus
disparadores son distintos: las sociales responden a problemas de
participación, las afectivas a oportunidades de refuerzo positivo.

Las acciones de moderación (pasiva) no se asignan a ninguno de los tres
roles porque corresponden a un rol distinto — el de moderador — con
disparadores y lógica diferentes (Korre et al., 2025, Apéndice C).

## Consecuencias

### Positivas

- Los tres roles proporcionan un marco teórico fundamentado para la
  organización de las acciones del modelo de intervención, con trazabilidad
  a la literatura.
- La convergencia de múltiples taxonomías independientes (Paulsen, Berge,
  Coppola, Pilkington, Baker, Abdous) en una estructura equivalente aumenta
  la confianza en la validez del marco.
- La taxonomía empírica de Blignaut & Trollip (2003) confirma que las
  categorías derivadas inductivamente de datos se alinean con el marco
  teórico deductivo.
- La distinción explícita entre facilitación (tres roles) y moderación (rol
  separado) clarifica los límites del sistema.

### Negativas

- El marco de tres roles simplifica la complejidad de la facilitación. En la
  práctica, una misma intervención puede cumplir funciones de más de un rol
  simultáneamente (por ejemplo, una pregunta socrática que también reconoce
  la contribución del estudiante combina los roles intelectual y social).
- La exclusión del rol *technical* (Berge, 1995; Abdous, 2011) limita el
  alcance del sistema a la facilitación de contenido, no a la asistencia
  técnica con la plataforma.
- Las taxonomías citadas fueron desarrolladas para facilitadores humanos. Su
  transferencia a un agente de IA es una decisión de diseño, no un resultado
  empírico.

### Cuestiones abiertas

- ¿Cómo se prioriza entre roles cuando múltiples condiciones se cumplen
  simultáneamente? (Por ejemplo: una discusión necesita tanto redirección
  intelectual como intervención social.)
- ¿Debe el sistema mantener un equilibrio explícito entre roles a lo largo
  del tiempo, o la distribución natural de los disparadores es suficiente?
- ¿Cómo se evalúa si el sistema está cubriendo adecuadamente los tres roles
  en la práctica?

## Referencias

- Abdous, M. (2011). A process-oriented framework for acquiring online
  teaching competencies.
- Baker, D. L. (2011). Designing and orchestrating online discussions.
- Berge, Z. L. (1995). Facilitating computer conferencing: Recommendations
  from the field. (Citado en Abdous, 2011.)
- Berge, Z. L. (2008). Changing instructor's roles in virtual worlds.
  (Citado en Abdous, 2011.)
- Blignaut, A. S., & Trollip, S. R. (2003). Developing a taxonomy of faculty
  participation in asynchronous learning environments.
- Coppola, N. W., Hiltz, S. R., & Rotter, N. G. (2002). Becoming a virtual
  professor: Pedagogical roles and asynchronous learning networks. (Citado
  en Abdous, 2011.)
- Korre, D., Tsipas, N., & Peppes, N. (2025). Facilitation and moderation in
  online discussions: A systematic review.
- Paulsen, M. F. (1995). Moderating educational computer conferencing.
  (Citado en Abdous, 2011.)
- Pilkington, R. (2003). Analysing educational dialogue interaction: Towards
  models that support learning.
