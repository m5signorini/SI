
-- ELIMINAR DUPLICADOS DE ORDERDETAIL AGRUPANDO CANTIDADES
SELECT DISTINCT orderid, prod_id, SUM(quantity) AS quantity, AVG(price) AS price
INTO duplicates_orderdetail
FROM orderdetail
    GROUP BY (orderid, prod_id)
    HAVING COUNT((orderid, prod_id)) > 1;

DELETE FROM orderdetail
    WHERE (orderid, prod_id)
    IN (SELECT orderid, prod_id FROM duplicates_orderdetail);

INSERT INTO orderdetail
SELECT *
FROM duplicates_orderdetail;

DROP TABLE duplicates_orderdetail;

-- ORDER
ALTER TABLE orders ADD FOREIGN KEY (customerid) REFERENCES customers(customerid);

--ORDERDETAIL
ALTER TABLE orderdetail ADD FOREIGN KEY (orderid) REFERENCES orders(orderid);
ALTER TABLE orderdetail ADD FOREIGN KEY (prod_id) REFERENCES products(prod_id);
ALTER TABLE orderdetail ADD CONSTRAINT PK_orderdetail PRIMARY KEY (orderid, prod_id);

--INVENTORY
ALTER TABLE inventory ADD FOREIGN KEY (prod_id) REFERENCES products(prod_id);

-- ACTORMOVIES
ALTER TABLE imdb_actormovies ADD FOREIGN KEY (actorid) REFERENCES imdb_actors(actorid);
ALTER TABLE imdb_actormovies ADD FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid);
ALTER TABLE imdb_actormovies ADD CONSTRAINT PK_actormovies PRIMARY KEY (actorid,movieid);


-- SET INITIAL CUSTOMER BALANCE
CREATE OR REPLACE PROCEDURE setCustomersBalance (IN maxBalance bigint)
    AS  $$
        BEGIN
        	UPDATE customers SET balance = floor(random() * (maxBalance + 1))::int;
        END
        $$
    LANGUAGE plpgsql;




-- QUERIES UTILIZADAS EN PRUEBAS

--SELECT actormovies1.actorid , actormovies1.movieid FROM imdb_actormovies AS actormovies1 JOIN imdb_actormovies AS actormovies2
	--ON actormovies1.movieid = actormovies2.movieid AND actormovies1.actorid = actormovies2.actorid
	--WHERE actormovies1.character != actormovies2.character;
