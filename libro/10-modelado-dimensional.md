# Capítulo 10. Modelado dimensional: de tablas operativas a preguntas de negocio

## 10.1. Definición académica

El modelado dimensional organiza datos analíticos mediante tablas de hechos, que registran eventos o mediciones, y tablas de dimensiones, que aportan contexto descriptivo. El esquema estrella sitúa los hechos en el centro y los conecta a dimensiones. El enfoque de Kimball exige definir primero el proceso de negocio, el grano, las dimensiones y los hechos.

## 10.2. Explicación simple

Una tabla de hechos responde «¿qué pasó y cuánto?». Una dimensión responde «¿cuándo, dónde, con quién, por qué canal o con qué producto?». Si la tabla de hechos representa una línea de pedido, cada fila describe un producto comprado en una operación concreta. La dimensión producto permite agrupar esas líneas por tipo de botella; la dimensión tiempo, por mes.

## 10.3. El grano, una decisión innegociable

| Tabla de hechos | Grano | Adecuada para |
|---|---|---|
| `fact_order` | Una fila por pedido | Total pagado y ticket |
| `fact_order_item` | Una fila por línea de producto | Cantidades y ranking de producto |
| `fact_web_session` | Una fila por sesión web | Actividad |
| `fact_nps` | Una fila por respuesta a encuesta | Satisfacción |

No se deben sumar montos de cabecera después de multiplicar pedidos por su cantidad de ítems. La definición de grano se escribe antes de elegir campos.

## 10.4. Dimensiones posibles

- `dim_date`: fecha, mes, año, trimestre y día de semana.
- `dim_channel`: ONLINE y OFFLINE.
- `dim_product`: producto, SKU, categoría y familia.
- `dim_customer`: identificador analítico y atributos permitidos.
- `dim_province`: provincia.
- `dim_store`: tienda.

La viabilidad exacta depende de las claves disponibles y de las preguntas del reporte. El repositorio ya trae un ejemplo de `dim_product` en `sql/01_dimensiones.sql`.

## 10.5. Claves y manejo de cambios

La clave natural proviene del sistema de origen, por ejemplo `product_id`. Una clave subrogada es creada por el warehouse, por ejemplo `product_key`. Permite desacoplar el modelo de los identificadores de origen y soportar ciertas estrategias de historial. Las Slowly Changing Dimensions (SCD) definen cómo registrar variaciones: tipo 1 suele sobrescribir el atributo; tipo 2 incorpora una nueva versión histórica; la selección depende de si importa reconstruir el estado pasado.

## 10.6. Propuesta técnica mínima

En `sql/01_dimensiones.sql` crear y cargar dimensiones, con PK, tipos y tratamiento explícito de claves faltantes. En `sql/02_hechos.sql` declarar los hechos, PK, FK y medidas con un grano escrito en comentarios. En `sql/03_consultas.sql` agregar verificaciones y KPIs. El archivo de dimensiones ya trae resuelta `dim_product` como ejemplo; el resto lo completa cada estudiante.

## 10.7. Ejercicios

1. Declarar el grano de cuatro hechos y explicar qué pregunta habilita cada uno.
2. Dibujar un esquema estrella basado en las fuentes de EcoBottle.
3. Construir una dimensión fecha y una dimensión canal.
4. Diseñar dos pruebas para detectar claves foráneas huérfanas.
5. Explicar cuándo necesitaríamos preservar historial con SCD tipo 2.

**Evidencia:** modelo estrella, diccionario de dimensiones y hechos, SQL ejecutable.

---

[← Capítulo 9](09-ciclo-de-vida.md) · [Índice](README.md) · [Capítulo 11 →](11-kpis.md)
