#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os
import sys
import random

catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
catalogue = json.loads(catalogue_data)

#Hacemos un diccionario para tener ya preparado el filtrado
dict_genres = dict()
for i in catalogue['peliculas']:
    for j in i["categoria"]:
        if j in dict_genres.keys():
            aux = dict_genres[j]
            aux.add(i["id"])
            dict_genres[j] = aux
        else:
            aux = set()
            aux.add(i["id"])
            dict_genres[j] = aux

"""
FUNCIONES AUXILIARES
"""

def get_session_user():
    user = {'is_authenticated': False, 'username': None}
    if 'usuario' in session:
        user['is_authenticated'] = True
    return user

def validate_user():
    return


"""
FUNCIONES DE ENRUTAMIENTO
"""

@app.route('/')
@app.route('/index')
def index():
    # Comprobar si la sesion actual es la de un usuario autenticado
    return render_template('index.html', movies=catalogue['peliculas'], categories=dict_genres.keys(), user=get_session_user())


@app.route('/login', methods=['GET', 'POST'])
def login():
    # doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if 'username' in request.form:
        # aqui se deberia validar con fichero .dat del usuario
        if request.form['username'] == 'pp':
            session['usuario'] = request.form['username']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', user=get_session_user())
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('login.html', user=get_session_user())


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html', user=get_session_user())


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    movies_ids_cart = session.get('cart', [])
    movies_in_cart = []
    for i in movies_ids_cart:
        aux = catalogue['peliculas'][int(i[0])]
        movies_in_cart.append((aux,i[1],i[1]*aux["precio"]))

    return render_template('cart.html', movies_in_cart=movies_in_cart, user=get_session_user())

@app.route('/add_to_cart/<string:movie_id>')
def add_to_cart(movie_id):

    if 'cart' not in session:
        session['cart'] = []

    aux = 0

    for i in session['cart']:
        if i[0] == movie_id:
            aux = i[1]
            session['cart'].remove(i)
            session['cart'].append((movie_id,aux+1))
            break

    if aux == 0:
        session['cart'].append((movie_id,1))

    return redirect("/cart")


@app.route('/movie_page',methods=['GET', 'POST'])
def movie_page():
    return render_template('movie_page.html', user=get_session_user())


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))


#@app.route('/user/<string:user>/history')

# Ruta para numero visitas
@app.route('/num_visitors', methods=['GET', 'POST'])
def num_visitors():
    n = random.randint(0,100)
    return n
