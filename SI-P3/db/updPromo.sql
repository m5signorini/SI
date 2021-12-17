

-- Implementar columna promo en customers

ALTER TABLE customers ADD promo SMALLINT;

-- Trigger para modificar el carrito de un customer
-- Logica:
--  1. Se modifica el valor de promo del customer
--  2. Se encuentra su carrito (order con status a NULL)
--  3. Por cada orderdetail del carrito, reducir su
--      precio en funcion del precio del producto
--      correspondiente
--  4. Actualizar el netamount del carrito
--  Observaciones:
--      net = total * (1 + tax/100)
--      total = sum_i^j(orderdetail_i.precio * orderdetail_i.cantidad)
--      orderdetail.precio = f(producto.precio)
--  En nuestro caso NEW.f(x) = x * (1-customer.promo/100) = x * q
--  Notese que OLD.f es desconocido (no se sabe el precio del orderdetail
--  en funcion del product a priori aunque en la practica son el mismo)
--  Por lo tanto, recalculamos los valores correspondientes y listo.

CREATE OR REPLACE FUNCTION update_cart_from_promo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
    BEGIN
        -- Para producir el deadlock, realizamos una modificacion
        -- de la tabla orders en primer lugar, ya que los ordenes
        -- de acceso en ambas transacciones son el mismo, la manera
        -- de conseguir un deadlock es cambiando el orden:
        -- Diagramas:
        --  TRIGGER |   BORRAR  -   BORRAR  |   TRIGGER
        --  Lock 1  |           -   Lock 0  |
        --  Sleep   |   Lock 0  -   Sleep   |   Lock 1
        --  Lock 0  |           -   Lock 1  |         
        --          |   Lock 1  -           |   Lock 0
        --  => Deadlock pues no se desbloquean hasta el final que
        --      no puede llegar, pues el otro esta bloqueado

        -- Dummy update para poder bloquear orders y posibilitar deadlock
        UPDATE orders
        SET netamount = netamount
        WHERE orders.customerid = OLD.customerid;

        PERFORM pg_sleep(10);

        -- Modificar orderdetails
        UPDATE orderdetail AS to_upd
        SET price = pd.price * (1 - NEW.promo)    
        FROM orders AS ord
            JOIN orderdetail AS odt
            ON ord.orderid = odt.orderid AND
                ord.customerid = OLD.customerid
            JOIN products AS pd
            ON pd.prod_id = odt.prod_id
        WHERE to_upd.orderid = odt.orderid AND
            to_upd.prod_id = pd.prod_id;

        -- Modificar order
        WITH totals AS (
            SELECT odt.orderid, SUM(price*quantity) AS total
            FROM orderdetail AS odt
                JOIN orders AS ord
                ON ord.customerid = OLD.customerid AND
                    ord.orderid = odt.orderid
            GROUP BY odt.orderid
        )
        UPDATE orders
        SET netamount = total, totalamount = ROUND((total * (1 + tax/100))::numeric, 2)::numeric
        FROM totals
        WHERE totals.orderid = orders.orderid AND orders.status IS NULL;
        RETURN NEW;
    END;
$$;

CREATE TRIGGER UPD_PROMO_CUSTOMER AFTER UPDATE
ON customers FOR EACH ROW
EXECUTE PROCEDURE update_cart_from_promo();