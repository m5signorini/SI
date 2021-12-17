# -*- coding: utf-8 -*-

import io
import time
import logging

import sqlalchemy as sqla
from sqlalchemy import create_engine
from pymongo import MongoClient

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1",
                          echo=False, execution_options={"autocommit": False})
meta_data = sqla.MetaData(bind=db_engine)
meta_data.reflect(bind=db_engine)

# Configurar logging para las trazas de ejecucion
logging.basicConfig()
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.INFO)
formatter = logging.Formatter()
stream = io.StringIO()
handler = logging.StreamHandler(stream)
handler.setFormatter(formatter)
logger.addHandler(handler)


# Crea la conexión con MongoDB
mongo_client = MongoClient()


def getMongoCollection(mongoDB_client):
    mongo_db = mongoDB_client.si1
    return mongo_db.topUK


def mongoDBCloseConnect(mongoDB_client):
    mongoDB_client.close()


def dbConnect():
    return db_engine.connect()


def dbCloseConnect(db_conn):
    db_conn.close()


def delCity(city, bFallo, bSQL, duerme, bCommit):

    # Array de trazas a mostrar en la página
    dbr = []
    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para
    #   forzar deadlock
    # - ir guardando trazas mediante dbr.append()

    try:
        # TODO: ejecutar consultas
        # (?) Eliminar constraint ON DELETE CASCADE de los pedidos
        db_conn = dbConnect()
        db_conn.execution_options(autocommit=False)
        trans = comenzar_transaccion(db_conn, city, bSQL, dbr)

        borrar_orderdetails(db_conn, city, bSQL, dbr)
        time.sleep(duerme)
        if bCommit:
            hacer_commit(db_conn, trans, city, bSQL, dbr)
            # BEGIN para poder iniciar transaccion pues commit la acaba
            trans = comenzar_transaccion(db_conn, city, bSQL, dbr)
        if not bFallo:
            borrar_orders(db_conn, city, bSQL, dbr)
            borrar_customers(db_conn, city, bSQL, dbr)
        else:
            borrar_customers(db_conn, city, bSQL, dbr)
            borrar_orders(db_conn, city, bSQL, dbr)
    except Exception as e:
        # TODO: deshacer en caso de error
        if bSQL:
            db_conn.execute((
                'ROLLBACK;'
            ))
        else:
            trans.rollback()
        print_stream_to_traces(stream, dbr)
        dbr.append(f'-- ERROR OCURRIDO: {e}')
        dbr.append('-- ACCION: Rollback realizado')
        print_tables_state_to_traces(db_conn, city, dbr, stream)
    else:
        # TODO: confirmar cambios si todo va bien
        hacer_commit(db_conn, trans, city, bSQL, dbr)
        dbr.append('-- OK: Ejecucion correcta')
    dbCloseConnect(db_conn)
    return dbr


def comenzar_transaccion(connection, city, bSQL, dbr):
    # Ejecutar con SQL
    trans = None
    if bSQL:
        connection.execute((
            'BEGIN;'
        ))
    # Ejecutar con SQLAlchemy
    else:
        trans = connection.begin()
    print_stream_to_traces(stream, dbr)
    print_tables_state_to_traces(connection, city, dbr, stream)
    dbr.append('-- OK: Comienzo de transaccion')
    return trans


def borrar_orderdetails(db_conn, city, bSQL, dbr):
    try:
        if not bSQL:
            detail_table = meta_data.tables['orderdetail']
            orders_table = meta_data.tables['orders']
            custom_table = meta_data.tables['customers']
            stmt = detail_table.delete().where(
                detail_table.c.orderid == orders_table.c.orderid
            ).where(
                orders_table.c.customerid == custom_table.c.customerid
            ).where(
                custom_table.c.city == city
            )
            result = db_conn.execute(stmt)
        else:
            result = db_conn.execute((
                'DELETE FROM orderdetail '
                '   USING orders AS od, customers AS ct'
                '   WHERE orderdetail.orderid = od.orderid'
                '       AND od.customerid = ct.customerid'
                f'      AND ct.city = \'{city}\''
            ))
        print_stream_to_traces(stream, dbr)
        print_tables_state_to_traces(db_conn, city, dbr, stream)
        dbr.append(f'-- OK: Eliminadas {result.rowcount} orderdetails ')
    except Exception as e:
        dbr.append('-- ERROR: Eliminacion de orderdetails ')
        print_stream_to_traces(stream, dbr)
        raise e


def borrar_orders(db_conn, city, bSQL, dbr):
    try:
        if not bSQL:
            orders_table = meta_data.tables['orders']
            custom_table = meta_data.tables['customers']
            # OBSERVACION:
            # DELETE ... USING ...
            # se traduce como
            # WHERE ... IN ...
            stmt = orders_table.delete().where(
                orders_table.c.customerid == custom_table.c.customerid
            ).where(
                custom_table.c.city == city
            )
            result = db_conn.execute(stmt)
        else:
            result = db_conn.execute((
                'DELETE FROM orders '
                '   USING customers AS ct'
                '   WHERE orders.customerid = ct.customerid'
                f'       AND ct.city = \'{city}\''
            ))
        print_stream_to_traces(stream, dbr)
        print_tables_state_to_traces(db_conn, city, dbr, stream)
        dbr.append(f'-- OK: Eliminadas {result.rowcount} orders ')
    except Exception as e:
        print_stream_to_traces(stream, dbr)
        dbr.append('-- ERROR: Eliminacion de orders ')
        raise e


def borrar_customers(db_conn, city, bSQL, dbr):
    try:
        if not bSQL:
            custom_table = meta_data.tables['customers']
            stmt = custom_table.delete().where(
                custom_table.c.city == city
            )
            result = db_conn.execute(stmt)
        else:
            result = db_conn.execute((
                'DELETE FROM customers '
                f'   WHERE city = \'{city}\'; '
            ))
        print_stream_to_traces(stream, dbr)
        print_tables_state_to_traces(db_conn, city, dbr, stream)
        dbr.append(f'-- OK: Eliminados {result.rowcount} customers')
    except Exception as e:
        print_stream_to_traces(stream, dbr)
        dbr.append('-- ERROR: Eliminacion de customers ')
        raise e


def hacer_commit(conn, trans, city, bSQL, dbr):
    try:
        if bSQL:
            conn.execute((
                'COMMIT;'
            ))
        else:
            trans.commit()
        print_stream_to_traces(stream, dbr)
        print_tables_state_to_traces(conn, city, dbr, stream)
        dbr.append('-- OK: Commit realizado con exito')
    except Exception as e:
        print_stream_to_traces(stream, dbr)
        dbr.append('-- ERROR: Commit ha fallado')
        raise e


def print_stream_to_traces(str, dbr):
    dbr.append(str.getvalue())
    str.seek(0)
    str.truncate(0)


def print_tables_state_to_traces(db_conn, city, dbr, str):
    details = db_conn.execute((
        'SELECT count(*)'
        '   FROM customers AS ct'
        '   JOIN orders AS od'
        f'   ON ct.city = \'{city}\''
        '       AND ct.customerid = od.customerid'
        '   JOIN orderdetail AS ot'
        '   ON od.orderid = ot.orderid'
    ))
    orders = db_conn.execute((
        'SELECT count(*)'
        '   FROM customers AS ct'
        '   JOIN orders AS od'
        f'   ON ct.city = \'{city}\''
        '       AND ct.customerid = od.customerid'
    ))
    customers = db_conn.execute((
        'SELECT count(*)'
        '   FROM customers AS ct'
        f'  WHERE ct.city = \'{city}\''
    ))
    state = (
        '-- ESTADO ACTUAL: \n'
        f'Orderdetails con cliente en {city} actuales: '
        f'{list(details)[0]}.\n'
        f'Orders con cliente en {city} actuales: '
        f'{list(orders)[0]}.\n'
        f'Customers en {city} actuales: '
        f'{list(customers)[0]}'
    )
    dbr.append(state)
    str.getvalue()
    str.seek(0)
    str.truncate(0)
