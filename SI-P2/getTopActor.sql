CREATE OR REPLACE FUNCTION getTopActors (genre CHAR, OUT Actor CHAR, OUT Num INT, OUT Debut INT,  
                                        OUT Film CHAR, OUT Director CHAR)
	RETURNS SETOF RECORD
    LANGUAGE plpgsql
	-- RECORD: PALABRA RESERVADA PARA TUPLA DE TIPOS DE OUT
    AS  $$
        BEGIN
			RETURN QUERY
            WITH all_data AS (
            SELECT imdb_actors.actorname, imdb_movies.movietitle, imdb_movies.start_year,
                imdb_actors.actorid, imdb_movies.movieid
            FROM imdb_moviegenres
                JOIN imdb_movies ON imdb_moviegenres.movieid = imdb_movies.movieid 
                    AND imdb_moviegenres.genre = $1 
                JOIN imdb_actormovies ON imdb_movies.movieid = imdb_actormovies.movieid
                JOIN imdb_actors ON imdb_actors.actorid = imdb_actormovies.actorid
            ),
            actor_filt AS (
            SELECT ad.*, cc.count
            FROM all_data AS ad
                JOIN (
                    -- NOS QUEDAMOS CON ACTORES QUE PARTICIPEN
                    -- EN MAS DE 4 PELICULAS
                    SELECT count(*), actorid
                    FROM all_data
                    GROUP BY actorid
                    HAVING count(*) > 4
                ) AS cc ON cc.actorid = ad.actorid
            )
            SELECT actorname::BPCHAR, af.count::INT, start_year::INT, movietitle::BPCHAR, dir.directorname::BPCHAR
			--into Actor, Num, Debut, Film, Director
            FROM actor_filt AS af
                JOIN (
                    -- AGRUPAMOS POR ACTOR Y DE CADA GRUPO
                    -- OBTENEMOS EL MINIMO start_year, HACEMOS
                    -- JOIN USANDO TAMBIEN EL min_year
                    SELECT actorid, min(start_year) AS min_year
                    FROM actor_filt
                    GROUP BY actorid
                ) AS my ON my.actorid = af.actorid
                    AND my.min_year = af.start_year
                JOIN imdb_directormovies AS dm ON dm.movieid = af.movieid
                JOIN imdb_directors AS dir ON dir.directorid = dm.directorid
            ORDER BY af.count DESC;
        END
        $$;