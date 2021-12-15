# -*- coding: utf-8 -*-

import os
import sys, traceback, time

import sqlalchemy as sqla
from sqlalchemy import create_engine
from pymongo import MongoClient

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

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
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()

    try:
        # TODO: ejecutar consultas
        # (?) Eliminar constraint ON DELETE CASCADE de los pedidos
        db_conn = dbConnect()
        db_conn.execution_options(autocommit=False)
        trans = comenzar_transaccion(db_conn, bSQL, dbr)

        if not bFallo:
            borrar_orderdetails(db_conn, city, dbr)
            if bCommit:
                hacer_commit(db_conn, trans, bSQL, dbr)
                # BEGIN para poder iniciar transaccion pues commit la acaba
                trans = comenzar_transaccion(db_conn, bSQL, dbr)

            borrar_orders(db_conn, city, dbr)
            borrar_customers(db_conn, city, dbr)
        else:
            borrar_orderdetails(db_conn, city, dbr)
            if bCommit:
                hacer_commit(db_conn, trans, bSQL, dbr)
                # BEGIN para poder iniciar transaccion pues commit la acaba
                trans = comenzar_transaccion(db_conn, bSQL, dbr)
            borrar_customers(db_conn, city, dbr)
            borrar_orders(db_conn, city, dbr)
    except Exception as e:
        # TODO: deshacer en caso de error
        if bSQL:
            db_conn.execute((
                'ROLLBACK;'
            ))
        else:
            trans.rollback()
        dbr.append(f'-- ERROR: Excepcion {e} ocurrida')
        dbr.append('-- Accion: Rollback realizado')
    else:
        # TODO: confirmar cambios si todo va bien
        hacer_commit(db_conn, trans, bSQL, dbr)
        dbr.append('-- OK: Ejecucion correcta')

    return dbr


def comenzar_transaccion(connection, bSQL, dbr):
    # Ejecutar con SQL
    trans = None
    if bSQL:
        connection.execute((
            'BEGIN;'
        ))
    # Ejecutar con SQLAlchemy
    else:
        trans = connection.begin()
    dbr.append('-- Comienzo de transaccion')
    return trans


def borrar_orderdetails(db_conn, city, dbr):
    try:
        db_conn.execute((
                'DELETE FROM orderdetail '
                '   WHERE orderid IN '
                '   (SELECT orderid '
                '    FROM orders AS od '
                '    JOIN customers AS ct '
                '    ON od.customerid = ct.customerid '
                f'   AND ct.city = \'{city}\'); '
        ))
        dbr.append('-- OK: Eliminadas orderdetails correspondientes ')
    except Exception as e:
        dbr.append('-- ERROR: Eliminacion de orderdetails ')
        raise e


def borrar_orders(db_conn, city, dbr):
    try:
        db_conn.execute((
            'DELETE FROM orders '
            '   WHERE orderid IN '
            '   (SELECT orderid '
            '    FROM orders AS od '
            '    JOIN customers AS ct '
            '    ON od.customerid = ct.customerid '
            f'   AND ct.city = \'{city}\');'
        ))
        dbr.append('-- Eliminadas orders correspondientes ')
    except Exception as e:
        dbr.append('-- ERROR: Eliminacion de orders ')
        raise e


def borrar_customers(db_conn, city, dbr):
    try:
        db_conn.execute((
                'DELETE FROM customers '
                f'   WHERE city = \'{city}\'; '
            ))
        dbr.append(f'-- OK: Eliminados customers con ciudad {city}')
    except Exception as e:
        dbr.append('-- ERROR: Eliminacion de customers ')
        raise e


def hacer_commit(conn, trans, bSQL, dbr):
    try:
        if bSQL:
            conn.execute((
                'COMMIT;'
            ))
        else:
            trans.commit()
        dbr.append('-- OK: Commit realizado con existo')
    except Exception as e:
        dbr.append('-- ERROR: Commit ha fallado')
        dbr.append(f'-- Motivo: {e}')
    