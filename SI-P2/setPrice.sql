
-- NOTA: llamar antes que actualiza.sql

/*
-- USANDO VISTAS:

CREATE VIEW inflated_view AS
SELECT prod_id, (price + price * 0.02 *(DATE_PART('year', CURRENT_DATE) - DATE_PART('year', TO_DATE(year, 'YYYY')))) AS inflation
FROM products JOIN imdb_movies ON products.movieid=imdb_movies.movieid;

UPDATE orderdetail
    SET price = inflated.inflation
    FROM inflated_view AS inflated
    WHERE inflated.prod_id = orderdetail.prod_id;

DROP VIEW inflated_view;
*/

-- DIRECTAMENTE
UPDATE orderdetail
    SET price = inflated.inflation
    FROM (
        SELECT orderid, (current_price / (1 + 0.02 * (DATE_PART('year', CURRENT_DATE) - DATE_PART('year', orderdate)))) as inflation
        FROM (
            SELECT orderid, products.price AS current_price
            FROM products JOIN orderdetail ON products.prod_id = orderdetail.prod_id
        ) AS detail JOIN orders ON orders.orderid = detail.orderid
    ) AS inflated
    WHERE inflated.prod_id = orderdetail.prod_id;
