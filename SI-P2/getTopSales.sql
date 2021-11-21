


CREATE OR REPLACE FUNCTION getTopSales(IN year1 INT, IN year2 INT,
                                    OUT year INT, OUT film CHAR, OUT sales BIGINT)
    RETURNS SETOF RECORD
    LANGUAGE plpgsql
    AS $$
        -- Por cada agno entre year1 y year2 encontrar la peli mas
        -- vendida dicho agno y ordenarlas por numero de ventas
        DECLARE
            start_year INT = GREATEST(year1, year2);
            init_year INT = LEAST(year1, year2);
        BEGIN
            RETURN QUERY
            WITH total_sales AS (
                -- Obtenemos cantidades vendidas por pelicula por agno
                SELECT DATE_PART('year', orderdate) as year, mov.movietitle as film, SUM(od.quantity) as sales
                FROM orders as ord 
                    JOIN orderdetail as od 
                        ON ord.status IS NOT NULL
                        AND DATE_PART('year', orderdate) <= start_year
                        AND DATE_PART('year', orderdate) >= init_year
                        AND ord.orderid = od.orderid
                    JOIN products as pr
                        ON pr.prod_id = od.prod_id
                    JOIN imdb_movies as mov
                        ON mov.movieid = pr.movieid
                GROUP BY DATE_PART('year', orderdate), mov.movieid
                ORDER BY SUM(od.quantity) DESC
            )
            SELECT total_sales.year::INT, total_sales.film::BPCHAR, total_sales.sales::BIGINT
            FROM total_sales
                JOIN (
                    SELECT ts.year, max(ts.sales) as mx
                    FROM total_sales as ts
                    GROUP BY ts.year
                ) AS max_sold 
                    ON total_sales.year = max_sold.year
                    AND total_sales.sales = max_sold.mx
            ORDER BY sales DESC;
        END
    $$;