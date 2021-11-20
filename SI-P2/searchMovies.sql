
-- FUNCTION para facilitar la implementacion de la busqueda de peliculas
-- por titulo y categoria


CREATE OR REPLACE FUNCTION searchMovies(title TEXT, categories TEXT[])
RETURNS TABLE (movieid imdb_movies.movietitle%TYPE, movieid imdb_movies.movieid%TYPE)
LANGUAGE plpgsql
AS $$
    BEGIN
		RETURN QUERY
        SELECT DISTINCT mov.movietitle, mov.movieid
		FROM imdb_genres as gen
			JOIN imdb_genremovies as gm ON gen.genre LIKE ANY(categories)
				AND gen.genreid = gm.genreid
			JOIN imdb_movies as mov ON gm.movieid = mov.movieid
				AND mov.movietitle ILIKE '%' || title || '%';
    END
$$;

-- EXAMPLE OF USAGE:
-- select * from searchMovies('Lord', '{Fantasy, Drama}')