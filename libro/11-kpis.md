# Capítulo 11. KPIs de marketing y analítica de negocios

## 11.1. Definición académica

Una métrica cuantifica una actividad o resultado; un indicador clave de desempeño (KPI) vincula una medición con objetivos estratégicos u operativos. Para que resulte útil debe contar con definición inequívoca, fórmula, unidad, periodicidad, filtros, dueño y criterio de interpretación.

## 11.2. Explicación sencilla

Que una web reciba 20.000 visitas es una métrica. Si el objetivo es incrementar compras sin aumentar el costo de adquisición, la conversión y el costo por venta pueden actuar como KPIs. Un buen tablero no es una colección de números vistosos: es una herramienta para responder preguntas y decidir acciones.

## 11.3. Definiciones para EcoBottle

- **Ventas.** Sumar `sales_order.total_amount` de pedidos con estado `PAID` o `FULFILLED`, asignados al período de `order_date`. Evitar sumar ese total después de unir directamente con las líneas de pedido.
- **Ticket promedio.** Ventas de pedidos válidos divididas por la cantidad de pedidos válidos en el mismo período y con los mismos filtros. Usar `NULLIF` en el denominador para evitar división por cero.
- **NPS.** Porcentaje de respuestas promotoras (9–10) menos porcentaje de respuestas detractoras (0–6); las puntuaciones 7–8 son pasivas. Si se expresa en escala de −100 a 100: NPS = 100 × (promotores / total − detractores / total).
- **Ventas por provincia.** Agrupar pedidos válidos por la provincia asociada a la dirección de envío, según la convención de los datos de origen. La definición geográfica se debe declarar.
- **Ranking de productos.** Agregar importes por ítems de pedidos válidos y agrupar por mes y producto. El campo `line_total` refleja importe neto de descuento antes de IVA; la comparación no debe presentarse como total final facturado si no incluye impuestos y envío.
- **Usuarios activos.** La consigna permite contar clientes identificados distintos o sesiones anónimas. Son unidades diferentes: conviene etiquetar y reportar por separado «clientes identificados con sesión» = `COUNT(DISTINCT customer_id)` no nulo y «sesiones anónimas» = `COUNT` de `session_id` con `customer_id` nulo; no sumarlos y llamarlos «usuarios únicos» sin una estrategia de identificación.

## 11.4. Ejemplo SQL de ventas y ticket sin duplicar pedidos

```sql
SELECT
  DATE_TRUNC('month', order_date) AS mes,
  COUNT(*) AS pedidos_validos,
  SUM(total_amount) AS ventas_ars,
  SUM(total_amount) / NULLIF(COUNT(*), 0) AS ticket_promedio_ars
FROM raw.sales_order
WHERE status IN ('PAID', 'FULFILLED')
GROUP BY 1
ORDER BY 1;
```

## 11.5. Ejemplo SQL de NPS

```sql
SELECT
  COUNT(*) AS respuestas,
  100.0 * (
    SUM(CASE WHEN score >= 9 THEN 1 ELSE 0 END)
    - SUM(CASE WHEN score <= 6 THEN 1 ELSE 0 END)
  ) / NULLIF(COUNT(*), 0) AS nps
FROM raw.nps_response;
```

## 11.6. Precauciones

Una correlación entre campañas y ventas no prueba causalidad. Los datos de sesiones no permiten identificar automáticamente a las personas que navegan sin iniciar sesión. Las encuestas NPS pueden incluir sesgo de no respuesta. Definir desde el comienzo los estados excluidos, las fechas consideradas, la moneda, los impuestos y las unidades del gráfico.

## 11.7. Ejercicios

1. Escribir consultas SQL para los seis KPIs exigidos en la práctica.
2. Comprobar que las ventas calculadas desde los hechos coincidan con el origen bajo la misma definición.
3. Justificar qué gráficos usar para tendencia, distribución provincial, comparación entre productos y evolución de NPS.
4. Formular tres recomendaciones de negocio, cada una respaldada por una métrica y una limitación explícita.

**Evidencia:** SQL de KPIs, validaciones y pequeño informe ejecutivo.

---

[← Capítulo 10](10-modelado-dimensional.md) · [Índice](README.md) · [Capítulo 12 →](12-fundamentos-de-marketing.md)
