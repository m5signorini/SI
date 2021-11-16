select * from getTopActors('Adventure') as act join imdb_movies on imdb_movies.movietitle=act.film
order by act.num desc;
