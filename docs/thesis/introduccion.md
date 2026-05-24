---
title: "Introducción"
author: "María Grimaldi"
lang: es
bibliography: "references.bib"
csl: "apa.csl"
---

<!--
DOCUMENTO DE TRABAJO: introduccion.md
Este archivo mezcla el scaffold de trabajo con el texto que vas escribiendo.
Los bloques HTML como este no aparecen en el PDF de salida de pandoc.

Cada seccion tiene:
  [OBSERVACION] Mis notas como companera de escritura (problemas concretos, citas disponibles).
  [NOTEBOOKLM]  Preguntas self-contained para buscar referencias que faltan.
  [TEXTO]       Espacio en blanco para que escribas el parrafo.

Cuando un parrafo este listo, borra el bloque [OBSERVACION] correspondiente.
Las citas van en formato [@ClaveAutorAnio]. Las pendientes van [@PENDIENTE: descripcion].
-->

# Introducción

<!-- ===========================================================
SECCION 1: Las discusiones como herramienta de aprendizaje
Notas originales: lineas 1-4 de Notas - TFM - Intro.md
=========================================================== -->

<!--
[OBSERVACION S1]

Claim principal: Los debates en clase son una estrategia que aumenta el pensamiento
critico y fomenta el aprendizaje colaborativo.

Problema de apertura: Las notas dicen "desde siempre", que es demasiado coloquial.
La alternativa es abrir con el claim directo sin el adverbio temporal. Por ejemplo:
"Las discusiones en clase son una estrategia de ensenanza con respaldo empirico en
el desarrollo del pensamiento critico y el aprendizaje colaborativo en educacion
superior [@Brown2015]."

Segundo claim: el aprendizaje es un proceso colectivo que requiere interaccion social
(constructivismo social). Cita disponible: [@WooReeves2007].

Tercer claim: "un debate, como tecnica de generacion de conocimiento". La URL de las
notas (wlv.openrepository.com) apunta a un paper sin citar correctamente. Ver
pregunta NotebookLM #S1 abajo.

Patron a evitar: no abrir con "Desde los inicios de la educacion..." ni con
"Es bien sabido que...". Ve directo al claim.
-->

<!--
[NOTEBOOKLM S1]

Pregunta 1 de 5 (para copiar y pegar directamente en NotebookLM):

"Estoy escribiendo la introduccion de una tesis sobre facilitacion de discusiones
academicas en linea. Necesito una referencia fundacional (no un paper del corpus
principal) que respalde el claim de que el aprendizaje es un proceso social que
requiere interaccion con otros, idealmente desde el constructivismo social
(Vygotsky, Dewey, Mercer). ¿Aparece alguno de estos autores citado en el corpus?
¿Que dice exactamente sobre el aprendizaje como proceso social?"
-->

[texto por escribir]

<!-- ===========================================================
SECCION 2: La educacion se mueve en linea
Notas originales: lineas 5-8 de Notas - TFM - Intro.md
=========================================================== -->

<!--
[OBSERVACION S2]

Claim principal: en los ultimos anos la educacion superior se da cada vez mas en
entornos en linea, con cifras concretas de plataformas MOOC en Europa.

Problema: todos los datos son placeholders ("desde el X", "XXX graduados",
"plataformas X, Y, Z", "un % en universidades publicas"). Dos opciones:
a) Llenamos los datos con fuentes reales (ver NotebookLM #S2 abajo).
b) Si no encontramos los datos, reformulamos el parrafo sin cifras especificas
   y con epistemic hedging correcto: "El crecimiento de la educacion en linea
   en Europa es consistente con..." en vez de afirmar un numero que no tenemos.

Observacion sobre la frase "La interaccion entre estudiantes es usualmente 100%
moderada por computador": el termino correcto es "mediada por computador"
(computer-mediated), no "moderada". "Mediada" describe el canal; "moderada"
implica supervision de contenido. Este es el primer punto donde el termino
tecnico importa para el resto de la tesis (CMC = Computer-Mediated Communication).
-->

<!--
[NOTEBOOKLM S2]

Pregunta 2 de 5:

"Estoy buscando estadisticas sobre el crecimiento de la educacion en linea o los
MOOCs en Europa para la introduccion de mi tesis (defendida en 2026). Necesito
especificamente: (1) el numero aproximado de estudiantes matriculados en MOOCs en
Europa en los ultimos anos, (2) el porcentaje de universidades que usan plataformas
virtuales como complemento o sustituto de la presencialidad, (3) alguna referencia
a plataformas concretas con datos de cobertura. ¿Aparece algun dato de este tipo en
el corpus? Si no, ¿que fuentes recomendarias consultar?"
-->

[texto por escribir]

<!-- ===========================================================
SECCION 3: Foros academicos, CMC y sus ventajas
Notas originales: lineas 7, 11-16 de Notas - TFM - Intro.md
=========================================================== -->

<!--
[OBSERVACION S3]

Claims y funciones de los foros segun las notas:
  - Escalar la participacion
  - Aumentar la accesibilidad
  - Assessment innovation
  - CMC da a estudiantes mas oportunidades de participar que en clase presencial

Cita disponible para el punto de participacion: La cita de Sullivan & Pratt (1996)
sobre el 80% del dialogo que acapara el tutor en clase presencial es util y concreta.
Usar: [@SullivanPratt1996]. Ya tiene entrada en references.bib, pero el titulo
exacto y el journal necesitan verificacion (ver nota TODO en el .bib).

Observacion: el ejemplo numerico de "10 estudiantes x 3 comentarios = 30 mensajes"
(linea 21 de las notas) es una ilustracion tuya, no un dato empirico. Si no hay
un estudio que lo respalde, hay que marcarlo como tal: "Para ilustrar el problema..."
o eliminarlo y usar el dato de Sullivan & Pratt directamente.

Cita disponible para funciones de los foros: [@Baker2011] cubre diseno y
orquestacion de discusiones en linea, incluyendo funciones pedagogicas y
de gestion. [@Rovai2007] cubre facilitacion efectiva de discusiones online.
-->

<!--
[NOTEBOOKLM S3]

Pregunta 3 de 5:

"En la introduccion de mi tesis quiero describir las funciones que tienen los
foros de discusion en plataformas educativas (MOOCs, LMS como Moodle, Canvas,
Open edX). Las funciones que tengo en mis notas son: escalar la participacion,
aumentar la accesibilidad, innovacion en evaluacion (assessment). ¿El corpus de
papers que tengo cargado contiene referencias que documenten alguna de estas
funciones especificas de los foros academicos, con datos empiricos o revisiones
sistematicas que pueda citar?"
-->

[texto por escribir]

<!-- ===========================================================
SECCION 4: El problema: la facilitacion no escala
Notas originales: lineas 17-28 de Notas - TFM - Intro.md
=========================================================== -->

<!--
[OBSERVACION S4]

Esta es la seccion mejor respaldada por el corpus. El argumento esta bien
estructurado en las notas. Los riesgos son:

1. La transicion entre "el instructor facilita" y "la facilitacion no escala"
   necesita un parrafo puente que no este en las notas. Sin ese puente, el salto
   es abrupto.

2. "En muchos casos" (linea 22 de las notas) es demasiado vago. O se especifica
   el contexto (MOOCs, clases con >50 estudiantes) o se elimina el hedge y se
   afirma directamente con una cita.

Citas disponibles para esta seccion:
  - Rol del instructor como facilitador de CMC: [@BlignautTrollip2003] (taxonomy),
    [@RichardsonEtAl2015] (instructor presence), [@Abdous2011] (tres roles).
  - Facilitacion activa mejora resultados: [@LimEtAl2011] (79.3% pensamiento
    critico), [@AnEtAl2009] (participacion distribuida), [@DeWeverEtAl2010] (roles).
  - El problema de escala: [@BlignautTrollip2003] (correctivo = 4.9% de postings),
    [@RichardsonEtAl2015] (57% de presencia es social, no instruccional).
  - Sin facilitacion, las discusiones no generan aprendizaje: [@AnEtAl2009],
    [@LimEtAl2011], [@WooReeves2007].

Tres roles de facilitacion: [@Abdous2011] sintetiza a Paulsen (1995). Mencionar
los tres roles (organizacional, intelectual, social) con esa cita.
-->

<!--
[NOTEBOOKLM S4]

Pregunta 4 de 5:

"Estoy argumentando que la facilitacion de discusiones en linea es efectiva pero
no escala: un instructor no puede seguir cada hilo de una clase grande. Tengo
evidencia empirica de que la facilitacion activa mejora el aprendizaje (Lim 2011,
An et al. 2009, De Wever et al. 2010). Pero necesito una referencia adicional
que documente el problema de escala especificamente: estudios que muestren que
en cursos grandes o MOOCs la presencia del instructor en los foros disminuye o
que los instructores reportan no poder mantener esa presencia. ¿Aparece algo
asi en el corpus?"
-->

[texto por escribir]

<!-- ===========================================================
SECCION 5: La IA como respuesta posible
Notas originales: lineas 29-37 de Notas - TFM - Intro.md
=========================================================== -->

<!--
[OBSERVACION S5]

El argumento de esta seccion tiene dos partes:
  a) La IA generativa ha mostrado capacidad para resolver problemas de dominio
     especifico a escala (claim general).
  b) En educacion, la IA se ha usado principalmente para tutoria y evaluacion,
     no para facilitacion de discusiones grupales (el gap).

Problema con la parte a): "era de LLMs" es coloquial. Y el claim de que
"la escalabilidad se resuelve con IA generativa" necesita evidencia o hay que
formularlo con mas cuidado: no es que este resuelto, es que hay evidencia de
que la IA puede operar en este espacio.

Citas disponibles para la parte b):
  - Gap en facilitacion generativa: [@KorreEtAl2025] ("la mayoria del NLP se
    centra en clasificacion, no en facilitacion generativa").
  - ~70% de estudios AI como entorno, no como agente activo: [@CasebourneEtAl2025].
  - Sistemas existentes con limitaciones: [@YuEtAl2024maic] (MAIC: impacto
    limitado en pensamiento profundo), [@GuEtAl2021] (CBR, precision 0.679).
  - AI personas que influyen en dinamicas de grupo: [@YanEtAl2025social],
    [@JinEtAl2025].

La lista de lo que NO buscamos resolver (lineas 34-37 de las notas: cuando
intervenir, estado de la conversacion, que decir) funciona mejor en la seccion
de alcance (S6), no aqui. Aqui el foco es el gap y la oportunidad.

Cita para Coursera u otras plataformas: no hay en el corpus. Ver NotebookLM #S5.
-->

<!--
[NOTEBOOKLM S5]

Pregunta 5 de 5:

"En la introduccion de mi tesis quiero hacer el claim de que la IA generativa
(LLMs) ha mostrado capacidad para abordar problemas de dominio especifico a
escala, como punto de partida para proponer su uso en facilitacion de
discusiones academicas. ¿El corpus contiene referencias que documenten
aplicaciones concretas de LLMs o IA generativa en educacion a escala, mas
alla de los sistemas especificos de facilitacion? Me interesa especialmente
cualquier referencia a plataformas comerciales (Coursera, edX, Khan Academy)
que hayan integrado IA generativa, con datos de cobertura o uso."
-->

[texto por escribir]

<!-- ===========================================================
SECCION 6: Alcance y supuestos del trabajo
Notas originales: lineas 25-27 de Notas - TFM - Intro.md
"asumiremos": CMC asincrono, responsabilidad del instructor
=========================================================== -->

<!--
[OBSERVACION S6]

Esta seccion no necesita citas: es la delimitacion de tu trabajo.

Problema de formulacion: "asumiremos" suena a nota interna de las notas de
trabajo. Para la tesis, esto se convierte en una declaracion de alcance.
Algo como: "El trabajo se centra en..." o "El sistema propuesto opera en..."

Dos supuestos que tienes en las notas:
  1. Discusiones asincronas mediadas por computador (no presenciales, no sincronas).
  2. La responsabilidad de facilitacion recae sobre el instructor (no sobre
     los estudiantes, aunque la literatura los considera igualmente importantes).

El segundo supuesto es un decision deliberada, no un olvido. Cuanto mas explicites
el por que de la decision, mas solida queda la delimitacion. Las notas dicen
"no sera nuestro enfoque" pero no dicen por que. Vale la pena justificarlo.
-->

[texto por escribir]

<!-- ===========================================================
SECCION 7: Objetivo general y objetivos especificos
Notas originales: lineas 39-51 de Notas - TFM - Intro.md
=========================================================== -->

<!--
[OBSERVACION S7]

El objetivo general esta bien formulado en las notas. Los problemas son de forma,
no de fondo:
  - "basandonos en caracteristicas identificables" es una construccion de gerundio
    que retrasa el verbo principal. Mejor formular como: "El objetivo de este trabajo
    es implementar... a partir de caracteristicas identificables en..."
  - "communicative AI / agentic AI" aparece en ingles en medio del texto. Si usas
    estos terminos en la tesis, deben estar definidos antes o en un glosario. Si los
    introduces aqui, ponlos en cursiva la primera vez y define brevemente.

Los objetivos especificos estan bien en su logica pero varios tienen placeholders
("sin mucha capacidad - aqui tenemos que definir..."). Estos van a necesitar
revision una vez que el sistema este mas definido.

Observacion general: los objetivos especificos tal como estan en las notas mezclan
objetivos de investigacion con objetivos de implementacion. No es necesariamente
un problema, pero si la tesis tiene una estructura que separa ambos (como es comun
en TFMs de ingenieria), puede valer la pena revisarlo cuando estes escribiendo
este parrafo.
-->

[texto por escribir]
