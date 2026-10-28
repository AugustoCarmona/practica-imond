# Capítulo 5. Modelo relacional, claves y consultas SQL

## 5.1. Definición académica

El modelo relacional representa información en relaciones (tablas) compuestas por filas y columnas. Una clave primaria (PK) identifica de forma única cada fila. Una clave foránea (FK) referencia otra tabla y permite expresar relaciones. SQL es un lenguaje declarativo para describir qué información se desea obtener o modificar, dejando al motor resolver una estrategia de ejecución.

## 5.2. Analogía para principiantes

En una planilla de pedidos hay un identificador de pedido y otro de cliente. No hace falta repetir el domicilio completo del cliente en cada fila si podemos relacionar la tabla de pedidos con la de clientes mediante un identificador estable. Esta separación facilita actualizaciones coherentes, aunque aumenta el número de uniones para algunos análisis.

## 5.3. Comandos esenciales para leer datos

```sql
-- Primeras filas de una tabla y su estructura
SELECT * FROM raw.sales_order LIMIT 10;
DESCRIBE raw.sales_order;

-- Cantidad de pedidos por estado
SELECT status, COUNT(*) AS cantidad
FROM raw.sales_order
GROUP BY status
ORDER BY cantidad DESC;

-- Pedidos con el nombre del cliente
SELECT o.order_id, o.order_date, c.first_name
FROM raw.sales_order AS o
JOIN raw.customer AS c ON c.customer_id = o.customer_id
LIMIT 10;
```

Los componentes deben leerse por su función: `SELECT` decide columnas, `FROM` indica origen, `JOIN` relaciona, `WHERE` filtra registros, `GROUP BY` define grupos, `HAVING` filtra grupos y `ORDER BY` ordena. La agregación `COUNT(*)` cuenta filas; `COUNT(campo)` ignora `NULL`; `COUNT(DISTINCT campo)` cuenta valores diferentes no nulos.

## 5.4. Precauciones iniciales

Una unión con cardinalidad uno-a-muchos puede multiplicar filas. Si un pedido contiene dos artículos, unir la cabecera a sus ítems produce dos filas para ese pedido. Sumar `total_amount` después del `JOIN` puede duplicar ventas. Por esta razón se declara primero la unidad de análisis o grano. Las comparaciones con nulos se expresan con `IS NULL` o `IS NOT NULL`, no con `= NULL`.

## 5.5. Ejercicios propuestos

- **Ejercicio inicial.** Obtener la cantidad de pedidos por estado y por canal usando las tablas de origen.
- **Ejercicio guiado.** Identificar PK y FK entre `sales_order`, `sales_order_item`, `product` y `customer`.
- **Ejercicio de detección.** Explicar por qué `SUM(o.total_amount)` puede aumentar al unir pedidos con ítems; proponer una consulta que calcule ventas en el grano correcto.
- **Ejercicio técnico.** Practicar `SELECT`, `JOIN`, filtros, agregaciones y ordenamiento en [SQLBolt](https://sqlbolt.com/).

**Evidencia:** archivo `sql/consultas_exploratorias.sql` documentado.

---

[← Capítulo 4](04-bases-de-datos-y-motores.md) · [Índice](README.md) · [Capítulo 6 →](06-oltp.md)
