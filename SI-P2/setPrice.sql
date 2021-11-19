
-- NOTA: llamar despues que actualiza.sql para usar indices
-- Explicacion:
--      Hacemos join de las tres tablas a usar, extrayendo los datos necesarios
--      Actualizamos coincidentes con la tabla con el nuevo dato
--      Casteamos a numeric para poder usar round con precision a 2 decimales
--      Para calcular la inflacion usamos que:
--          y := precio tras n años
--          x := precio original
--          n := numero de años
--          p := porcentaje de inflacion
--      Por lo tanto:
--          => y = x * (1+p)^n
--          => x = y / ((1+p)^n) : que es lo que queremos, pues tenemos el precio en la actualidad

UPDATE orderdetail
    SET price = inflated.inflation
    FROM (
        SELECT pd.prod_id, od.orderid, quantity*ROUND((pd.price / ((1 + 0.02 )^(DATE_PART('year', CURRENT_DATE) - DATE_PART('year', orderdate))))::numeric, 2) AS inflation
        FROM products AS pd
			JOIN orderdetail AS od ON pd.prod_id = od.prod_id
			JOIN orders 	 AS os ON os.orderid = od.orderid
    ) AS inflated
    WHERE inflated.prod_id = orderdetail.prod_id AND inflated.orderid = orderdetail.orderid;

-- LLAMADA A SET ORDER AMOUNT YA QUE ESTA FUNCION REQUIERE DE LOS RESULTADOS DE SET PRICE
SELECT setOrderAmount();
