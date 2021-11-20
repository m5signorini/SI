select imdb_movies.movietitle, orderdetail.quantity, orderdetail.price, products.price  from orderdetail
            join products on products.prod_id = orderdetail.prod_id
            join inventory on inventory.prod_id = orderdetail.prod_id
            join imdb_movies on products.movieid = imdb_movies.movieid
            where orderid = 100;
