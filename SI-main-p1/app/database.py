# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine, func
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select, func, column

import random, string

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_movies = Table('imdb_movies', db_meta, autoload=True, autoload_with=db_engine)

descripcion_resumen = "Star Wars: Episodio I - La amenaza fantasma (título original en inglés: Star Wars: Episode I - The Phantom Menace; también conocida en español como La guerra de las galaxias: Episodio I - La amenaza fantasma) es una película de space opera nota 1. de 1999, escrita y dirigida por el director de cine estadounidense George Lucas.",

descripcion_extra="Es la cuarta entrega de la saga Star Wars y la primera en el orden cronológico de la misma, después de un paréntesis de veintidós años del lanzamiento de Una nueva esperanza.La trama describe la historia del maestro jedi Qui-Gon Jinn y de su aprendiz Obi-Wan Kenobi, que escoltan y protegen a la Reina Amidala desde su planeta Naboo hasta Coruscant con la esperanza de encontrar una salida pacífica a un conflicto comercial interplanetario a gran escala. También trata del joven Anakin Skywalker antes de convertirse en Jedi, presentado como un esclavo con un potencial de la Fuerza inusualmente fuerte, y debe lidiar con el misterioso regreso de los Sith.",

#Macro para determinar cuantas peliculas cargamos en la pagina inicializa
LIMIT = 100

# METODOS AUXILIARES
####################

def generate_movieList(result):
    """
    Given a result from execute containing a movieid column
    generates the necessary data for each id.
    """
    # Convertimos el proxy 'result' en una lista de dicts mas legible
    as_list = [{column: value for column, value in rowproxy.items()} for rowproxy in result]

    # Si la lista es vacia o no de la forma correcta, devolvemos []
    if len(as_list) < 1:
        return []
    if not 'movieid' in as_list[0].keys():
        return []

    movieList = []
    for item in as_list:
        movieDict = dict()
        id = item.get('movieid', None)
        if not id:
            continue
        movieDict['descripcion_resumen'] = item.get('descripcion_resumen', descripcion_resumen)
        movieDict['titulo'] = item.get('titulo', item.get('movietitle', None))
        if not movieDict['titulo']:
            info = db_getMovieInfo(id)
            if not info:
                continue
            movieDict['titulo'] = info['title']
        movieDict['director'] = db_getMovieDirectors(id)
        movieDict['categoria'] = db_getMovieGenres(id)
        movieDict['id'] = id
        movieList.append(movieDict)

    return movieList

# METODOS DE ACCESO A DATOS
###########################

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

        db_result = db_conn.execute("Select * from getTopActors('{}') as top \
                                    join imdb_movies on imdb_movies.movietitle=top.film \
                                    order by top.Num desc limit 10".format(genre))

        db_conn.close()
        as_list = [{column: value for column, value in rowproxy.items()} for rowproxy in db_result]
        return as_list
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

        ##############################################################################
        # ATENCION:
        # ERROR - HAY PELICULAS SIN DIRECTORES POR LO TANTO LOS DETALLES ACABAN VACIOS
        # SOLUCION: REFACTORIZAR EL CODIGO PARA HACER LAS CONSULTAS DE DETALLES,
        # GENEROS Y DIRECTORES POR SEPARADO
        # EJEMPLO: MOVIEID = 77860
        ###############################################################################

        aux = result_list[0]

        movieDict = dict()

        movieDict["id"] = aux[0]
        movieDict["title"] = aux[1]
        movieDict["year"] = aux[2]
        movieDict["description_resumen"] = descripcion_resumen
        movieDict["description_extra"] = descripcion_extra
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

        # Devolver None para poder gestionar el error
        return None

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

def db_getMovieGenres(movieid):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("Select imdb_genres.genre\
                                    from imdb_movies join imdb_genremovies on imdb_movies.movieid=imdb_genremovies.movieid \
                                    join imdb_genres on imdb_genremovies.genreid=imdb_genres.genreid \
                                    where imdb_movies.movieid={}".format(movieid))

        db_conn.close()
        aux = list(db_result)

        ret = set()

        for item in aux:
            ret.add(item[0])

        return list(ret)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_getMovieDirectors(movieid):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("Select imdb_directors.directorname\
                                    from imdb_movies join imdb_directormovies on imdb_movies.movieid=imdb_directormovies.movieid \
                                    join imdb_directors on imdb_directormovies.directorid=imdb_directors.directorid \
                                    where imdb_movies.movieid={}".format(movieid))

        db_conn.close()
        aux = list(db_result)

        ret = set()

        for item in aux:
            ret.add(item[0])

        return list(ret)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_populateCatalog():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("select imdb_movies.movietitle, imdb_movies.movieid from imdb_movies")

        db_conn.close()

        aux = list(db_result)

        moviesList = list()

        for item in aux[0:LIMIT]:
            movieDict = dict()
            movieDict["descripcion_resumen"] = descripcion_resumen
            movieDict["titulo"] = item[0]
            movieDict["director"] = db_getMovieDirectors(item[1])
            movieDict["id"] = item[1]
            movieDict["categoria"] = db_getMovieGenres(item[1])
            moviesList.append(movieDict)

        return moviesList
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_getCustomersUsernames():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("select distinct username from customers;")

        db_conn.close()
        aux = list(db_result)

        ret = []

        for item in aux:
            ret.append(item[0])

        return ret
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_getLastCustomerId():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("select customerid from customers order by customerid desc limit 1;")

        db_conn.close()
        aux = list(db_result)

        for item in aux:
            ret = item[0]

        return ret
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_insertCustomer(data):
    try:
        aux = db_getLastCustomerId()+1
        query = "insert into customers (customerid,address1, email,creditcard,username, \
                password, balance, loyalty) values \
                (" + str(aux) + ",'" + data["address"] +"','" + \
                data["email"] +"','" + data["payment"] +"','" +data["username"] +"','" +\
                data["password"] + "'," + data["money"] +","+ data["points"]+ ");"
        print(query)

        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        return True
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_getCustomerById(customerid):
    try:
        query = "select * from customers where customerid = {}".format(customerid)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        aux = list(db_result)
        ret= dict()

        item = aux[0]
        ret["id"]=item[0]
        ret["address"]=item[1]
        ret["email"]=item[2]
        ret["payment"]=item[3]
        ret["username"]=item[4]
        ret["money"]=item[6]
        ret["points"]=item[7]

        print(ret)

        return ret
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_updateCustomerById(id, data):
    try:
        query = "update customers \
        set 'address1' = '" + str(data['address']) +"', \
        'email' = '" + str(data['email']) + "', \
        'creditcard' = '" + str(data['payment']) + "', \
        'username' = '" + str(data['username']) + "', \
        'balance' = " + str(data['money']) + " \
        'loyalty' = " + str(data['points']) + " where customerid = {}".format(id)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        return True
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_getCustomerByUsername(username, password):
    try:
        print(username)
        print(password)
        query = "select * from customers where username = '{}' and password = '{}';".format(username, password)
        print(query)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        aux = list(db_result)
        item = aux[0]

        ret = dict()
        ret["id"]=item[0]
        ret["address"]=item[1]
        ret["email"]=item[2]
        ret["payment"]=item[3]
        ret["username"]=item[4]
        ret["money"]=item[6]
        ret["points"]=item[7]

        return ret
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_generateHistoryData(userid):
    try:
        query = "select orderid, totalamount, orderdate from orders \
        where customerid = {} and status is not NULL \
        order by orderdate;".format(userid)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        aux = list(db_result)

        history = dict()
        history["Compras"] = []

        for item in aux:
            details = db_getMoviesByOrder(userid, item[0])
            compras = []
            for movie in details:
                compras.append({'pelicula':movie[0], 'cantidad':movie[2], 'importe':movie[2]*movie[1]})
            history["Compras"].append({"fecha":str(item[2]), "peliculas_compradas": compras, "precio_compra": item[1]})

        return history
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_getMoviesByOrder(userid, orderid):
    try:
        query = "select imdb_movies.movietitle, products.price, orderdetail.quantity, products.prod_id \
        from orders \
        join orderdetail on orderdetail.orderid = orders.orderid \
        join products on orderdetail.prod_id = products.prod_id \
        join imdb_movies on products.movieid = imdb_movies.movieid \
        where orders.orderid = {} and orders.customerid = {};".format(orderid, userid)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

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

def db_getProductsByMovie(movieid):
    try:
        query = "select * from products where movieid = {};".format(movieid)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        aux = list(db_result)

        print(aux)

        return aux
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'


def db_getUserActualCart(userid):
    try:
        query = "select * from orders where customerid = {} and status is NULL;".format(userid)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        order = list(db_result)
        order = order[0]

        query = "select imdb_movies.movietitle, orderdetail.quantity, orderdetail.price, products.price, products.description, products.prod_id  from orderdetail\
                join products on products.prod_id = orderdetail.prod_id\
                join inventory on inventory.prod_id = orderdetail.prod_id\
                join imdb_movies on products.movieid = imdb_movies.movieid\
                where orderid = {};".format(order[0])
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

        db_conn.close()

        cart_entries = list(db_result)

        cart = {'order':order,'orderdetails':cart_entries}
        return cart
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

# Esta funcion la usaremos para ver si sigue habiendo productos de este tipo, en caso de que len(aux)
# sea 0, sigue habiendo stock de dicho producto
def db_getProductByIdAlert(product_id):
    try:
        query = "select * from products join alerts on alerts.inventoryid = inventory.inventoryid \
        join inventory on inventory.prod_id = products.prod_id \
        where prod_id = {};".format(product_id)
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute(query)

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

def db_insertOrderdetail(orderid, product_id, userid):
    try:
        order_info = db_getMoviesByOrder(userid, product_id)
        flag = 0
        actual_quantity = 0

        for item in order_info:
            if item[3] == product_id:
                flag = 1
                actual_quantity = item[2]
                break

        if flag == 0:
            query = "insert into orderdetail \
                    values ({}, {}, (select products.price\
                                    from products \
                                    where prod_id = {}),1);".format(orderid, product_id, product_id)
            # conexion a la base de datos
            db_conn = None
            db_conn = db_engine.connect()

            db_result = db_conn.execute(query)

            db_conn.close()

        else:
            db_updateOrderdetail(orderid, product_id, actual_quantity + 1)

        return True
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def db_updateOrderdetail(orderid, product_id, new_quantity):
    try:
        if new_quantity != 0:
            query = "update orderdetail \
                    set price = {}*(select products.price from products \
                                join orderdetail on products.prod_id=orderdetail.prod_id\
                                where orderdetail.orderid = {} and products.prod_id={}), \
                        quantity = {} where orderid = {} and prod_id = {};".format(new_quantity, orderid, product_id, new_quantity, orderid, product_id)
            # conexion a la base de datos
            db_conn = None
            db_conn = db_engine.connect()

            db_result = db_conn.execute(query)

            db_conn.close()
        else:
            query = "delete from orderdetail\
                    where prod_id = {} and orderid = {};".format(product_id, orderid)
            # conexion a la base de datos
            db_conn = None
            db_conn = db_engine.connect()

            db_result = db_conn.execute(query)

            db_conn.close()

        return True
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'



def db_searchMovies(title, categories):
    try:
        # query = "select * from searchMovies(:title, :categories)"
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute(
            select([column('movieid')])
                .select_from(func.searchMovies(title, categories))
                .limit(1000)
            )
        db_conn.close()
        # db_result has a list of tuples with title and id
        movieList = generate_movieList(db_result)
        return movieList
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'
