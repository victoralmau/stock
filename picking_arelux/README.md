El módulo contiene el desarrollo que permite añadir funcionalidades al apartado de Almacén


## Crones

### Fix Odoo Stock Production Lot Product Qty Store 
Frecuencia: cada 3 horas

Descripción: Revisa todos los lotes (partidas) y re-calcula el 'product_qty_store' para actualizar el stock real de esa partida (Se utilizará ese dato por ejemplo, para no dejar seleccionar partidas en los AV que no tengan stock o no tengan stock suficiente)

### Autogenerate Invoices Stock Picking Return 
Frecuencia: 1 vez al día

Descripción: Revisa todos los AV con id > 125958 que NO tengan factura rectificativa relacionada y de cada uno de ellos revisa si procede generarla (si se ha generado del PV inicial un AD y NO existe ninguna reclamación respecto a ese PV inicial) y genera una FVR relacionada con el AD con las líneas que proceda del AD y las uds del mismo según los precios unitarios de la FV que ya existe del PV
