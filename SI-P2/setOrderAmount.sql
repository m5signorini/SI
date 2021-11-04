

-- NOTA: llamar antes que actualiza.sql
-- PROCEDURE
CREATE OR REPLACE PROCEDURE setOrderAmount ()
    LANGUAGE plpgsql
    AS  $$
        BEGIN
            UPDATE orders
                SET netamount =
                FROM (

                )
                WHERE
        END
        $$;


SELECT  FROM orderdetail
WHERE
