# Capítulo 7. OLAP y data warehousing: comprender la historia del negocio

## 7.1. Definición académica

Online Analytical Processing (OLAP) denomina al procesamiento orientado a consultas analíticas, agregaciones, exploración multidimensional y apoyo a decisiones. Un data warehouse es una arquitectura de integración y almacenamiento que reúne información consistente, orientada a temas y con perspectiva temporal para responder preguntas de gestión. La formulación clásica de Inmon destaca cuatro propiedades: orientación temática, integración, variación temporal y no volatilidad.

## 7.2. Explicación sencilla

La caja registradora necesita saber cuánto cobrar ahora; el área comercial necesita conocer cómo evolucionaron las ventas cada mes, cuáles productos crecieron, qué provincias presentan mayores oportunidades y si la satisfacción mejoró. El primer problema es operacional (OLTP); el segundo, analítico (OLAP). No es conveniente depender de las mismas tablas y recursos para ambas tareas cuando aumenta la escala del negocio.

## 7.3. Comparación OLTP/OLAP

| Criterio | OLTP | OLAP |
|---|---|---|
| Propósito | Registra operaciones | Explora resultados y tendencias |
| Operaciones | Privilegia escrituras y lecturas puntuales | Procesa lecturas amplias, agregaciones y joins |
| Granularidad | Conserva el detalle operativo actual | Puede combinar detalle histórico con agregados |
| Diseño habitual | Suele normalizar | Suele usar esquemas dimensionales o almacenamiento columnar, según necesidad |
| Usuarios | Aplicaciones y personal operativo | Analistas, responsables de negocio y sistemas de BI |
| Ejemplos | PostgreSQL para pedidos online | DuckDB, BigQuery o Snowflake para exploración analítica, según contexto |

No son categorías mutuamente excluyentes de software: describen cargas y decisiones arquitectónicas.

## 7.4. Las cuatro propiedades del warehouse

- **Orientación a temas:** tablas y modelos dedicados a ventas, clientes, productos, campañas.
- **Integración:** reconciliación de nombres, formatos, monedas y reglas entre fuentes.
- **Variación en el tiempo:** fechas y conservación del historial necesarias para comparar períodos.
- **No volatilidad:** estabilidad histórica y predominio de lectura; no implica que un warehouse moderno jamás pueda corregir registros, actualizar dimensiones o realizar mantenimiento.

## 7.5. Capas típicas

Fuentes de origen → adquisición e integración → almacenamiento intermedio (staging/raw) → modelado y datos confiables → data marts y herramientas de BI. Un data mart es un subconjunto orientado a un área. Un data lake puede alojar información en formatos diversos, incluso sin modelar; no equivale automáticamente a un warehouse. Las arquitecturas modernas pueden combinar ambos enfoques.

## 7.6. Ejemplo EcoBottle

Las fuentes son los 13 CSV en `raw/`. El proceso crea tablas analíticas a partir de esos archivos y las exporta en `dw/`. Una vez definidas dimensiones y hechos, un dashboard puede calcular ventas, ticket promedio, NPS y desempeño por canal, fecha, producto y provincia. El warehouse actúa como una fuente consistente cuando las definiciones de cada indicador se documentan y comprueban.

## 7.7. Ejercicios

1. Explicar por qué una consulta histórica de millones de registros podría interferir con una aplicación de pagos.
2. Elegir cuatro dimensiones con las cuales explorar las ventas de EcoBottle.
3. Dibujar la arquitectura de origen, transformación, warehouse, tablero y destinatario de negocio.
4. Comparar data warehouse y data lake sin afirmar que sean conceptos equivalentes.

**Evidencia:** esquema de arquitectura comentado y tabla OLTP/OLAP con cinco criterios.

---

[← Capítulo 6](06-oltp.md) · [Índice](README.md) · [Capítulo 8 →](08-etl-y-elt.md)
