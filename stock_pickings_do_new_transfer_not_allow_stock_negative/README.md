Valida los stock.picking de salida para NO permitir que se quede en stock negativos.

En la ficha de producto (product.template) se añade un campo dentro de la pestaña de Inventario llamado "Permitir stock negativo" que nos permitirá omitir la validación para ese producto.

En caso de que algún producto y/o partida el stock actual - la cantidad que se saca sea < 0 se mostrará un mensaje de error NO permitiendo validar el picking.
