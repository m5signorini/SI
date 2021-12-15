#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
from flask import render_template, request, url_for
import os
import sys
import time

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/borraCiudad', methods=['POST', 'GET'])
def borraCiudad():
    if 'city' in request.form:
        city    = request.form["city"]
        bSQL    = request.form["txnSQL"]
        bCommit = "bCommit" in request.form
        bFallo  = "bFallo"  in request.form
        duerme  = request.form["duerme"]
        dbr = database.delCity(city, bFallo, bSQL == '1', int(duerme), bCommit)
        return render_template('borraCiudad.html', dbr=dbr)
    else:
        return render_template('borraCiudad.html')


@app.route('/topUK', methods=['POST', 'GET'])
def topUK():
    # TODO: consultas a MongoDB ...
    movies = [[], [], []]
    topUK = database.getMongoCollection(database.mongo_client)
    # SCI-FI 1994-1998
    results = topUK.find(
        {
            'genres': 'Sci-Fi',
            'year': {'$gte': 1994, '$lte': 1998}
        }
    )
    movies[0] = list(results)

    # DRAMAS 1998 : ***, The
    results = topUK.find(
        {
            'genres': 'Drama',
            'year': 1998,
            'title': {
                '$regex': '.*, The$'
            }
        }
    )
    movies[1] = list(results)
    print(movies[0])

    # Julia Roberts & Alec Baldwin
    results = topUK.find(
        {
            'actors': {
                '$all': ['Roberts, Julia', 'Baldwin, Alec']
            }
        }
    )
    movies[2] = list(results)

    return render_template('topUK.html', movies=movies)