# from pymongo import MongoClient
# from sqlalchemy import create_engine
import database
import pymongo
# import sys
# import json

_mongo_database = 'si1'


def drop_mongo_db(client):
    """
    Espera un MongoClient
    """
    client.drop_database(_mongo_database)


def do_everything(client):
    """
    Espera un MongoClient
    """
    # Crea la conexión con MongoDB
    # Por defecto localhost port 27017

    dblist = client.list_database_names()
    if _mongo_database not in dblist:
        print('#'*30)
        print('MongoDB')
        print('Base de datos si1 no existente')
        print('Se creara la base de datos si1 con topUK')
        print('#'*30)

    # INICIO DE CONEXION
    ##########################################

    # Obtenemos collection topUk
    topUk = database.getMongoCollection(client)
    # Conectamos con postgresql
    pg_conn = database.dbConnect()

    # POBLADO DE MONGODB
    ###########################################

    # Peliculas de UK mas recientes (400)
    # Notese que country y movieid son clave primaria,
    # luego no habra repetidos
    pg_result = pg_conn.execute((
        r"SELECT "
        r"mv.movieid as id, "
        r"SUBSTRING(mv.movietitle from '.*(?= \((\d|\/|[a-zA-Z])+\)$)')"
        r"AS title, "
        r"split_part(mv.year, '-', 1)::SMALLINT AS year "
        r"FROM imdb_movies AS mv "
        r"   JOIN imdb_moviecountries AS mc "
        r"   ON mv.movieid = mc.movieid "
        r"   AND mc.country = 'UK' "
        r"ORDER BY mv.year DESC "
        r"LIMIT 400 "
    ))
    results = [{column: value for column, value in rowproxy._mapping.items()}
               for rowproxy in pg_result]

    # Parsear resultados para mongo
    # Obtener listados de generos
    # Obtener listados de directores
    # Obtener listados de actores
    movies = []
    for mov in results:
        movieid = mov['id']
        g_res = pg_conn.execute((
            f"SELECT genre "
            f"FROM imdb_moviegenres "
            f"WHERE movieid = {movieid} "
        ))
        d_res = pg_conn.execute((
            f"SELECT dt.directorname AS name "
            f"FROM imdb_directormovies AS dm "
            f"   JOIN imdb_directors AS dt "
            f"   ON dm.movieid = {movieid} "
            f"   AND dm.directorid = dt.directorid "
        ))
        a_res = pg_conn.execute((
            f"SELECT at.actorname AS name "
            f"FROM imdb_actormovies AS am "
            f"   JOIN imdb_actors AS at "
            f"   ON am.movieid = {movieid} "
            f"   AND am.actorid = at.actorid "
        ))
        directors = [r for r, in d_res]
        actors = [r for r, in a_res]
        genres = [r for r, in g_res]
        movies.append({
            'title': mov['title'],
            'genres': genres,
            'year': mov['year'],
            'directors': directors,
            'actors': actors
        })

    topUk.insert_many(movies)

    # Obtener mas relacionadas
    # Obtener relacionadas
    max_related = 10
    movies = topUk.find()
    for movie in movies:
        # Coincidencia 100% unidireccional
        most_related = topUk.find(
            {
                'genres': {'$all': movie['genres']},
                '_id': {'$ne': movie['_id']}
            },
            {
                'title': 1,
                'year': 1,
                '_id': 0
            }
        ).sort('year', pymongo.DESCENDING).limit(max_related)
        most_related = list(most_related)
        # Coincidencia 50% unidireccional
        # Contamos numeros de coincidencia con un 'group_by'
        aggregate = topUk.aggregate([
            {'$unwind': '$genres'},
            {'$match': {'genres': {'$in': movie['genres']}}},
            {'$group': {
                '_id': {'_id': '$_id', 'title': '$title', 'year': '$year'},
                'number': {'$sum': 1}
            }},
            {'$match': {
                'number': {
                    '$gte': len(movie['genres'])*0.5,
                    '$lt': len(movie['genres'])
                }
            }},
            {'$sort': {
                'number': pymongo.DESCENDING
            }},
            {'$limit': max_related},
            {'$sort': {
                '_id.year': pymongo.DESCENDING
            }}
        ])
        related = [{'title': rel['_id']['title'], 'year': rel['_id']['year']}
                   for rel in aggregate]
        # Insertamos aquellos con 100% > number > 50%
        topUk.update_one({'_id': movie['_id']}, {'$set': {
            'most_related_movies': most_related,
            'related_movies': related
        }})

    # CERRADO DE CONEXION
    ###########################################

    # Cerramos conexion
    database.dbCloseConnect(pg_conn)
    print('#'*30)
    print('MongoDB')
    print('Base de datos si1 creada y poblada')
    print('#'*30)


if __name__ == "__main__":

    # RESETEAMOS POR COMPLETO LA BASE DE DATOS
    ###########################################
    client = database.mongo_client
    dblist = client.list_database_names()
    if _mongo_database in dblist:
        print('#'*30)
        print('MongoDB')
        print('Base de datos si1 ya existe')
        print('Se procede a borrarla ')
        print('#'*30)
    drop_mongo_db(client)
    do_everything(client)
    database.mongoDBCloseConnect(client)
