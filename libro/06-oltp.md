# Capítulo 6. Sistemas OLTP: operar sin perder consistencia

## 6.1. Definición académica

Online Transaction Processing (OLTP) es un patrón de procesamiento centrado en numerosas transacciones operativas, cortas y concurrentes, que requieren integridad y tiempos de respuesta reducidos. En bases relacionales transaccionales se emplean comúnmente esquemas normalizados para minimizar redundancia y dependencias indebidas.

## 6.2. Explicación intuitiva

Cuando una persona compra una botella, el negocio necesita registrar el pedido, confirmar el pago, descontar inventario y conservar evidencia. Lo prioritario no es producir un gráfico de ventas históricas, sino evitar que se cobre dos veces, se pierda una venta o dos compradores reciban el último artículo del inventario.

## 6.3. Propiedades ACID

- **Atomicidad:** o se realizan todas las operaciones de una transacción, o ninguna.
- **Consistencia:** cada transacción respeta las restricciones e invariantes del sistema.
- **Aislamiento:** la ejecución concurrente se controla según un nivel de aislamiento definido, para impedir anomalías no permitidas.
- **Durabilidad:** tras la confirmación de una transacción, sus cambios sobreviven a fallas según las garantías del sistema.

Conviene evitar una interpretación absoluta del aislamiento: el comportamiento observable depende del nivel configurado.

## 6.4. Normalización

La normalización organiza relaciones para reducir anomalías de inserción, actualización y eliminación. En primera forma normal se exigen atributos atómicos respecto del diseño; la segunda y la tercera tratan dependencias funcionales y atributos que dependen de claves. Para este nivel introductorio importa comprender el principio, no memorizar recetas sin analizar dependencias.

Ejemplo: guardar repetido el nombre y la provincia del cliente en cada pedido provoca problemas cuando cambia el cliente; relacionar `customer` con `sales_order` reduce ciertas duplicaciones. No significa que todos los datos se almacenen siempre normalizados: en un warehouse se pueden desnormalizar dimensiones deliberadamente.

## 6.5. Ejercicios propuestos

- **Ejercicio inicial.** Explicar las cuatro propiedades ACID con el ejemplo de una compra y un reintegro.
- **Ejercicio guiado.** Dibujar un DER sencillo con `customer`, `sales_order` y `sales_order_item`, marcando cardinalidades.
- **Ejercicio crítico.** Describir anomalías de una tabla hipotética que repite nombre de cliente, provincia y producto en todas las líneas de pedidos.

**Evidencia:** diagrama relacional con justificación de PK, FK y al menos dos reglas de integridad.

---

[← Capítulo 5](05-modelo-relacional-y-sql.md) · [Índice](README.md) · [Capítulo 7 →](07-olap-y-data-warehousing.md)
