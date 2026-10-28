# Capítulo 9. Ciclo de vida de los datos y de los proyectos de data warehousing

## 9.1. Definición académica

El ciclo de vida de los datos incluye generación, captura, almacenamiento, procesamiento, utilización, conservación y eventual eliminación o anonimización, bajo políticas de seguridad y gobierno. El ciclo de vida de un proyecto de data warehousing, abordado por Kimball y Ross, comprende planificación, relevamiento de requisitos, arquitectura, modelado dimensional, diseño físico, construcción de procesos, desarrollo de aplicaciones de BI, despliegue y mantenimiento. Ambos ciclos están relacionados, pero no deben confundirse.

## 9.2. Explicación sencilla

Los datos son como un producto que atraviesa una cadena de valor. Nacen cuando alguien compra o visita un sitio; se recogen, verifican, transforman y usan para decidir. Luego deben protegerse, revisarse y, cuando no exista un motivo legítimo para conservarlos, retirarse. El proyecto que permite aprovecharlos también recorre fases de diseño y mejora.

## 9.3. Iteración

El ciclo no es una línea rígida. Una vez publicado el tablero, las personas usuarias formulan nuevas preguntas o detectan problemas de definición. Eso puede exigir revisar el diccionario de datos, cambiar una dimensión, corregir un cálculo y desplegar otra versión. La fase de mantenimiento alimenta nuevas iteraciones.

## 9.4. Aplicación del ciclo a EcoBottle

- **Planificación:** ¿para quién y para qué se construye el tablero?
- **Requisitos:** ¿qué significa exactamente una venta válida o un usuario activo?
- **Arquitectura:** ¿cómo se conectan `raw/`, SQL, DuckDB, `dw/` y BI?
- **Modelado:** ¿qué dimensiones y hechos responden esas preguntas?
- **Desarrollo:** ¿cómo se ejecutan los scripts y verifican las reglas?
- **Despliegue:** ¿cómo se entrega un repositorio reproducible y un reporte comprensible?
- **Mantenimiento:** ¿cómo se modifican KPIs y fuentes sin romper resultados previos?

## 9.5. Gobierno, seguridad y ética

Los permisos deberían respetar el principio de mínimo privilegio; la disponibilidad de datos no equivale a permiso de uso irrestricto. Considerar minimización, finalidad, transparencia, exactitud, plazos de conservación, confidencialidad y derechos de las personas. En un contexto argentino, estudiar la Ley 25.326 y el artículo 43 de la Constitución Nacional; en contextos sujetos a normativa europea, el GDPR. Las reglas legales, sanciones y vigencia se verifican con fuentes oficiales antes de aplicarlas a un caso real.

## 9.6. Ejercicios

1. Diferenciar en un esquema las etapas de vida de un registro y las etapas del proyecto analítico.
2. Proponer controles para proteger la identidad de clientes al compartir resultados.
3. Describir tres cambios de requisitos que obligarían a iterar el modelo.
4. Debatir un caso de segmentación comercial técnicamente factible pero éticamente cuestionable.

**Evidencia:** política breve de ciclo de vida, acceso y conservación.

---

[← Capítulo 8](08-etl-y-elt.md) · [Índice](README.md) · [Capítulo 10 →](10-modelado-dimensional.md)
