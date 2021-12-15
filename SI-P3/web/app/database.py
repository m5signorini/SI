# -*- coding: utf-8 -*-

import os
import sys, traceback, time

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
        # Ejecutar con SQL
        if bSQL:
            db_conn.execute((
                'BEGIN;'
            ))
        # Ejecutar con SQLAlchemy
        else:
            trans = db_conn.begin()

        if not bFallo:
            borrar_orderdetails(db_conn, city, dbr)
            borrar_orders(db_conn, city, dbr)
            borrar_customers(db_conn, city, dbr)
        else:
            borrar_orderdetails(db_conn, city, dbr)
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
        dbr.append(f'-- Excepcion {e} ocurrida')
        dbr.append('-- Rollback al comienzo')
    else:
        # TODO: confirmar cambios si todo va bien
        if bSQL:
            db_conn.execute((
                'COMMIT;'
            ))
        else:
            trans.commit()
        dbr.append('-- Ejecucion correcta')
        dbr.append('-- Commit realizado')

    return dbr


def borrar_orderdetails(db_conn, city, dbr):
    db_conn.execute((
            'DELETE FROM orderdetail '
            '   WHERE orderid IN '
            '   (SELECT orderid '
            '    FROM orders AS od '
            '    JOIN customers AS ct '
            '    ON od.customerid = ct.customerid '
            f'   AND ct.city = \'{city}\'); '
    ))
    dbr.append('-- Eliminadas orderdetail ')


def borrar_orders(db_conn, city, dbr):
    db_conn.execute((
        'DELETE FROM orders '
        '   WHERE orderid IN '
        '   (SELECT orderid '
        '    FROM orders AS od '
        '    JOIN customers AS ct '
        '    ON od.customerid = ct.customerid '
        f'   AND ct.city = \'{city}\');'
    ))
    dbr.append('-- Eliminadas orders ')


def borrar_customers(db_conn, city, dbr):
    db_conn.execute((
            'DELETE FROM customers '
            f'   WHERE city = \'{city}\'; '
        ))
    dbr.append('-- Eliminadas customers ')
