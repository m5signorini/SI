

-- NOTA: llamar antes que actualiza.sql

CREATE OR REPLACE PROCEDURE setOrderAmount ()
    LANGUAGE plpgsql
    AS  $$
        BEGIN
            -- UPDATE: netamount & totalamount (para reducir tiempo, solo un update)
            WITH totals AS (
                SELECT orderid, SUM(price) AS total
                    FROM orderdetail
                    GROUP BY orderid
            )
            UPDATE orders
                SET netamount = total, totalamount = total + tax
                FROM totals
                WHERE totals.orderid = orders.orderid AND ((netamount IS NULL) OR (totalamount IS NULL));
        END
        $$;

