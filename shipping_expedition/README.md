El módulo contiene el desarrollo que permite crear el apartado de expediciones para su posterior uso.

En Inventario > Operaciones se añade el apartado del menú "Expediciones"

## Crones

## Shipping Expedition Update State
Frecuencia: 1 vez cada hora

Descripción:
Respecto a todas las expediciones que no estén en estados: delivered o canceled se actualizan los estados de las mismas para que los addons de cada tipo de transporte (shipping_expedition_nacex, shipping_expedition_cbl, shipping_expedition_txt) incluya la función para actualizar la expedición correspondiente.
