# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine, func
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

import random, string

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_movies = Table('imdb_movies', db_meta, autoload=True, autoload_with=db_engine)

def db_listOfMovies1949():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Seleccionar las peliculas del anno 1949
        db_movies_1949 = select([db_table_movies]).where(text("year = '1949'"))
        db_result = db_conn.execute(db_movies_1949)
        #db_result = db_conn.execute("Select * from imdb_movies where year = '1949'")

        db_conn.close()

        return  list(db_result)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_topActorsByGenre(genre):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("Select * from getTopActors('Adventure') as top \
                                    join imdb_movies on imdb_movies.movietitle=top.film \
                                    order by top.Num desc".format(genre))

        db_conn.close()

        aux = list(db_result)

        return aux[0:10]
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_getMovieInfo(movie):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Seleccionar las peliculas del anno 1949
        #action_movies = select([func.getTopActors('Action')])
        #db_result = db_conn.execute(action_movies)
        db_result = db_conn.execute("Select imdb_movies.movieid, imdb_movies.movietitle, imdb_movies.year, imdb_directors.directorname, imdb_genres.genre from imdb_movies \
            join imdb_directormovies on imdb_directormovies.movieid=imdb_movies.movieid \
            join imdb_directors on imdb_directormovies.directorid = imdb_directors.directorid \
            join imdb_genremovies on imdb_genremovies.movieid = imdb_movies.movieid \
            join imdb_genres on imdb_genres.genreid = imdb_genremovies.genreid \
            where imdb_movies.movieid = {};".format(movie))


        db_conn.close()

        result_list = list(db_result)
        aux = result_list[0]

        movieDict = dict()

        movieDict["id"] = aux[0]
        movieDict["title"] = aux[1]
        movieDict["year"] = aux[2]
        letters = string.ascii_lowercase
        movieDict["description"] = ''.join(random.choice(letters) for i in range(100))
        movieDict["director"] = set()

        for director in result_list:
            movieDict["director"].add(director[3])

        movieDict["categoria"] = set()

        for genre in result_list:
            movieDict["categoria"].add(genre[4])


        return movieDict
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_genres():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("Select genre from imdb_genres")

        db_conn.close()

        aux = list(db_result)

        return aux
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'
