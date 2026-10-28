# Capítulo 8. ETL y ELT: integrar datos de diferentes fuentes

## 8.1. Definición académica

ETL significa Extract, Transform, Load: extracción desde fuentes, transformación y validación antes del destino definitivo, y carga posterior. ELT significa Extract, Load, Transform: adquisición, carga inicial en un repositorio y procesamiento posterior sobre los datos ingresados. La diferencia sustantiva es el orden y lugar de la transformación, no simplemente el lenguaje empleado.

## 8.2. Explicación para principiantes

Imaginar un centro de distribución: llegan cajas desde varios proveedores. En ETL, el equipo las revisa, etiqueta y clasifica antes de colocarlas en la estantería definitiva. En ELT, las cajas ingresan a un área preparada para recibirlas y se clasifican dentro del centro. En los dos casos son necesarios controles de calidad y criterios de almacenamiento.

## 8.3. La extracción

El origen puede ser una API, un CSV, una base relacional o un sistema de eventos. Una extracción completa relee todos los datos; una incremental obtiene nuevas filas o modificaciones desde un punto de control. Cada extracción debe documentar fuente, fecha, esquema, volumen, permisos y posibles fallos. Una copia de datos no debe confundirse con su validación.

## 8.4. Transformaciones frecuentes

Homogeneizar nombres y tipos de columnas; normalizar fechas; convertir unidades; resolver duplicados; tratar `NULL` según significado; validar rangos y estados; verificar claves y relaciones; unir fuentes; derivar indicadores; crear dimensiones y tablas de hechos. No se deben reemplazar silenciosamente los valores faltantes por cero si esto altera su sentido.

## 8.5. La carga

Puede producirse mediante inserción inicial, sobrescritura completa, cargas incrementales o actualización de claves. Importan la idempotencia —una repetición produce el mismo resultado esperado—, la observabilidad, el manejo de errores, el control de acceso y la recuperabilidad. Para fines pedagógicos, la práctica reconstruye el warehouse desde cero al ejecutar `run_sql.py`.

## 8.6. Cómo se relaciona con la práctica

El programa `run_sql.py` utiliza DuckDB para exponer los CSV como vistas `raw.<tabla>`, ejecutar en orden alfabético los archivos SQL, crear el archivo `warehouse.duckdb`, exportar tablas a `dw/` y generar el diagrama `dw/modelo_estrella.md`. Es un flujo de transformación y materialización local. Puede describirse como ingestión de fuentes crudas y transformación dentro del motor, pero un repositorio local y un ELT empresarial no poseen automáticamente la misma complejidad operacional.

## 8.7. Ejemplo simple de tratamiento de nulos

```sql
SELECT
    order_id,
    COALESCE(shipping_fee, 0) AS envio
FROM raw.sales_order;
```

`COALESCE` es útil cuando la regla de negocio justifica un valor alternativo. No sirve como atajo general para ocultar errores de captura. Antes de convertir una ausencia en cero debe demostrarse qué significa esa ausencia.

## 8.8. Ejercicios

1. Dibujar los flujos ETL y ELT y explicar dónde se ejecuta la transformación.
2. Elaborar una tabla de validaciones: valores nulos, claves sin correspondencia, totales contables, estados no válidos y fechas fuera de rango.
3. Diseñar una estrategia para reconstruir el warehouse sin modificar los CSV originales.
4. Justificar cuándo convendría ETL y cuándo ELT considerando infraestructura, escala, costo y requerimientos.

**Evidencia:** diseño de pipeline con reglas de calidad y manejo de errores.

---

[← Capítulo 7](07-olap-y-data-warehousing.md) · [Índice](README.md) · [Capítulo 9 →](09-ciclo-de-vida.md)
