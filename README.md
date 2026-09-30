# Trabajo Práctico Final — Introducción al Marketing Online y los Negocios Digitales

Este repositorio tiene los datos de **EcoBottle AR** para el trabajo práctico final.

- **Consigna:** [Trabajo Práctico Final](https://docs.google.com/document/d/15RNP3FVqLjO4jzh80AAkK6mUR5DOLqPxLjQxqvdzrYg/edit?usp=sharing)
- **Diagrama de tablas (DER):** [assets/DER.png](./assets/DER.png)

## ¿Qué hay en el repositorio?

```
raw/         los datos de origen: un archivo CSV por tabla   ← con esto vas a trabajar
generator/   el programa que creó los datos de raw/ (no hace falta usarlo)
assets/      el diagrama de tablas (DER)
```

> ⚠️ **No modifiques los archivos de `raw/`.** Son los datos de origen. Tus scripts tienen que leerlos y guardar los resultados en otra carpeta (DW).

## Los datos en un minuto

- Son una **foto del sistema de ventas** de EcoBottle, tomada el **30/09/2025 a las 23:59:59**.
- Tienen los pedidos del **01/01/2024 al 30/09/2025**.
- Los montos están en **pesos argentinos**, y los precios de lista **no incluyen IVA**.
- Las fechas y horas están en **hora de Argentina**.
- Una **celda vacía** en un CSV significa que ese dato no existe (en SQL sería `NULL`; en pandas aparece como `NaN`).

## Las tablas

| Archivo | Qué guarda | Filas |
|---|---|---:|
| `channel.csv` | Los 2 canales de venta: `ONLINE` (web) y `OFFLINE` (tiendas) | 2 |
| `province.csv` | Las 4 provincias donde opera la empresa | 4 |
| `product_category.csv` | Categorías de producto: *Bottles* → *Classic* y *Sport* | 3 |
| `product.csv` | Los 2 productos: Classic A y Sport B | 2 |
| `store.csv` | Las 4 tiendas físicas | 4 |
| `customer.csv` | Los clientes | ~3.500 |
| `address.csv` | Las direcciones de clientes y tiendas | ~3.800 |
| `sales_order.csv` | Los pedidos: quién compró, cuándo, por qué canal y cuánto pagó | ~12.000 |
| `sales_order_item.csv` | Los productos de cada pedido (una fila por producto) | ~14.500 |
| `payment.csv` | El pago de cada pedido | ~12.000 |
| `shipment.csv` | Los envíos por correo | ~7.000 |
| `web_session.csv` | Las visitas a la web | ~100.000 |
| `nps_response.csv` | Las respuestas a la encuesta de satisfacción (NPS) | ~3.000 |

## Cómo leer los datos

### Pedidos
- **Pedido online:** `store_id` está vacío.
- **Compra en tienda:** `store_id` indica la tienda, y la "dirección de envío" es la dirección de la tienda (el cliente se lleva el producto en el momento).
- **Las cuentas siempre cierran:**
  - `line_total` = cantidad × precio − descuento
  - `subtotal` = suma de los `line_total` del pedido
  - `tax_amount` = 21 % del subtotal (IVA)
  - `total_amount` = subtotal + IVA + costo de envío

### Estados de un pedido (`sales_order.status`)

| Estado | Qué significa | ¿Cuenta como venta? |
|---|---|:---:|
| `CREATED` | Se hizo el pedido pero todavía no se pagó | No |
| `PAID` | Está pagado pero todavía no se entregó | Sí |
| `FULFILLED` | Ya se entregó (o se compró en la tienda) | Sí |
| `CANCELLED` | Se canceló: el pago fue rechazado, no se pagó a tiempo o el cliente se arrepintió | No |
| `REFUNDED` | Se entregó, pero después se devolvió el dinero | No |

### Pagos y envíos
- Cada pedido tiene **un pago**. Si el pago no se concretó, `paid_at` está vacío.
- **Solo tienen envío** (`shipment`) los pedidos que viajan por correo: los online y algunos que la tienda manda a domicilio. Las compras en tienda no tienen envío.
- **Estados del envío:**
  - `READY`: se está preparando.
  - `SHIPPED`: está viajando.
  - `DELIVERED`: se entregó.
  - `CANCELLED`: no salió.

### Clientes y visitas a la web
- Un cliente con `status = 'I'` dio de baja su cuenta. Sus compras anteriores siguen en los datos.
- En `web_session`, un `customer_id` vacío es un visitante que no inició sesión.
- **Origen de la visita** (`source`):
  - `ads`: publicidad en redes.
  - `direct`: entró directo o desde el newsletter.
  - `referral`: vino de otro sitio o del newsletter.
  - `organic`: buscadores.

### Encuesta NPS
- **Cuándo se manda:**
  - Pedidos entregados por correo: **7 días después de la entrega**.
  - Compras en tienda: **al día siguiente**.
- El puntaje va de 0 a 10. Un `customer_id` vacío es una respuesta anónima.
- La encuesta **no tiene número de pedido**: se relaciona con el cliente (`customer_id`) y con el canal (`channel_id`).

## Para empezar

1. Hacé un **fork** de este repositorio y clonalo en tu computadora.
2. Abrí los CSV de `raw/` con Python. Por ejemplo, con pandas: `pd.read_csv("raw/sales_order.csv")`.
3. Seguí la [consigna](https://docs.google.com/document/d/15RNP3FVqLjO4jzh80AAkK6mUR5DOLqPxLjQxqvdzrYg/edit?usp=sharing).

## ¿Y la carpeta `generator/`?

Es el programa que **inventó estos datos** simulando el negocio: clientes que se registran, compran, pagan, reciben el envío y responden la encuesta. **No lo necesitás para el TP.** Si te interesa ver cómo se arma un conjunto de datos de prueba, podés leerlo; el detalle está en [`generator/README.md`](./generator/README.md).

Si alguna vez querés volver a generar los datos o comprobar que están bien:

```bash
python generator/generate_raw.py     # vuelve a crear los CSV de raw/ (salen idénticos)
python generator/validate_raw.py     # revisa que los datos cumplan todas las reglas
```
