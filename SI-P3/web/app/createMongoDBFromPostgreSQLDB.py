from pymongo import MongoClient
from sqlalchemy import create_engine
import database
import sys

_mongo_database = 'si1'
_mongo_collection = 'topUK'


def get_recent_uk_movies(conn):
    """
    Espera una postgresql connection
    Obtiene las peliculas de UK mas recientes (400)
    """
    pass


def insert_data_to_mongo(client, data):
    """
    Espera un MongoClient
    Inserta los datos en la coleccion de mongo
    """
    pass


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
    if not _mongo_database in dblist:
        print('#'*30)
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
    



    # CERRADO DE CONEXION
    ###########################################

    # Cerramos conexion
    database.dbCloseConnect(pg_conn)

if __name__ == "__main__":

    # RESETEAMOS POR COMPLETO LA BASE DE DATOS
    ###########################################
    client = database.mongo_client
    drop_mongo_db(client)
    do_everything(client)
    database.mongoDBCloseConnect(client)