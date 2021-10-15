#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, abort, jsonify
import json
import os
import sys
import random
from pathlib import Path
import hashlib
from hmac import compare_digest
import re
from datetime import datetime

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
CLASES AUXILIARES
"""
class ExistingUserException(Exception):
    def __init__(self, username):
        self.username = username
        super().__init__("User already registered: " + username)


class User:
    def __init__(self):
        self.is_authenticated = False
        self.username = None
        self.email = None
        self.address = None
        self.payment = None
        self.points = 0
        self.money = 0
        self.history = {'Compras':[]}

    def validate_signup_form(self, form):
        """
        Valida un formulario con los datos de usuario actualizando el objeto
        actual y devolviendo True si la validacion ha tenido exito
        """
        data = form.to_dict()
        # Comprobar username:
        #InvalidForm
        if 'signusername' not in data.keys():
            return False
        # ValidUsername
        regex = r"^([a-zA-Z0-9]){6,}$"
        if not re.match(regex, data['signusername']):
            return False
        # ExistingUsername
        path = os.path.join(app.root_path, "usuarios/"+data['signusername'])
        if os.path.isdir(path):
            raise ExistingUserException(data['signusername'])
            return False

        # Comprobar email:
        #InvalidForm
        if 'email' not in data.keys():
            return False
        # ValidEmail
        regex = r"^([a-z]|[A-Z]|[0-9]|_)+@[a-zA-Z0-9_]+\.[a-z]+$"
        if not re.match(regex, data['email']):
            return False

        # Comprobar direccion:
        #InvalidForm
        if 'address' not in data.keys():
            return False
        # ValidAddress
        regex = r"^(.){1,50}$"
        if not re.match(regex, data['address']):
            return False

        # Comprobar tarjeta:
        #InvalidForm
        if 'payment' not in data.keys():
            return False
        # ValidAddress
        regex = r"^([0-9]){16,16}$"
        if not re.match(regex, data['payment']):
            return False

        # Comprobar contraseña
        # InvalidForm:
        if 'signpassword' not in data.keys():
            return False
        if 'confsignpassword' not in data.keys():
            return False
        # ValidatePasswords
        if data['signpassword'] != data['confsignpassword']:
            return False

        # Inicializar variables si todas son correctas
        self.username = data['signusername']
        self.email = data['email']
        self.address = data['address']
        self.payment = data['payment']
        self.money = random.randint(0,100)
        self.points = 0
        return True


    def update_on_server(self, *, update_data=False, update_history=False):
        """
        Usando los datos de este objeto, actualiza los valores guardados en
        su correspondiente fichero data.dat y en history.json
        """
        # Comprobar validez del usuario
        if not self.is_authenticated:
            return False

        # Actualizar data.dat
        if update_data:
            path = os.path.join(app.root_path, "usuarios/"+self.username+"/data.dat")
            if not os.path.exists(path):
                return False

            # Obtiene previo y guarda
            file = open(path, encoding="utf-8").read()
            data = json.loads(file)
            # Por ahora solo se puede modificar el dinero y los puntos
            data['points'] = self.points
            data['money'] = self.money

            with open(path, 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=False, indent=4)

        # Actualizar history.json
        if update_history:
            return self.set_history_to_server()

        return True


    def create_on_server(self, form):
        """
        Dada la informacion de un formulario, la valida y crea el usuario del
        lado del servidor actualizando este objeto a su vez
        """
        if not self.validate_signup_form(form):
            return False

        # Obtenemos salt y hasheamos
        password = form['signpassword']
        salt = os.urandom(16)
        enco = bytes(password, 'utf-8')
        hash = hashlib.blake2b(enco, salt=salt).hexdigest()

        # Creamos directorio
        path = os.path.join(app.root_path, "usuarios/"+self.username)
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Succesfully created the directory %s" % path)

        data = {
            'username': self.username,
            'salt': salt.hex(),
            'password': hash,
            'payment': self.payment,
            'email': self.email,
            'address': self.address,
            'money': self.money,
            'points': self.points
        }

        with open(path+'/data.dat', 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)

        # Creamos historial.json
        self.history = {"Compras":[]}
        with open(path+'/historial.json', 'w', encoding='utf-8') as outfile:
            json.dump(self.history, outfile, ensure_ascii=False, indent=4)

        return True


    def get_from_server(self, form):
        """
        Dado un formulario de inicio de sesion inicializa este objeto obteniendo
        los datos necesarios de la carpeta correspondiente, devolviendo True en
        caso de que el inicio haya sido correcto
        """
        if 'username' not in form.keys():
            return False
        if 'password' not in form.keys():
            return False

        username = form['username']
        regex = r"^([a-zA-Z0-9]){6,}$"
        if not re.match(regex, username):
            return False

        path = os.path.join(app.root_path, "usuarios/"+username+"/data.dat")
        if not os.path.exists(path):
            return False

        file = open(path, encoding="utf-8").read()
        data = json.loads(file)

        # Comprobamos la contraseña
        password = form['password']
        hash = data['password']
        salt = bytes.fromhex(data['salt'])
        enco = bytes(password, 'utf-8')
        comp = hashlib.blake2b(enco, salt=salt).hexdigest()

        if compare_digest(hash, comp) is False:
            return False

        # Actualizar usuario con los datos:
        self.username = data['username']
        self.email = data['email']
        self.address = data['address']
        self.payment = data['payment']
        self.money = data['money']
        self.points = data['points']
        self.is_authenticated = True

        # Actualizar obteniendo historial:
        self.get_history_from_server()
        return True


    def set_history_to_server(self):
        """
        Si es un usario registrado guarda su historial en history.json
        """
        if not self.is_authenticated:
            return False

        path = os.path.join(app.root_path, "usuarios/"+self.username+"/history.json")
        if not os.path.exists(path):
            return False

        with open(path, 'w', encoding='utf-8') as outfile:
            json.dump(self.history, outfile, ensure_ascii=False, indent=4)
        return True


    def get_history_from_server(self):
        """
        Si es un usuario registrado carga en self.history su historial
        """
        if not self.is_authenticated:
            return False

        path = os.path.join(app.root_path, "usuarios/"+self.username+"/history.json")
        if not os.path.exists(path):
            return False

        file = open(path, encoding="utf-8").read()
        self.history = json.loads(file)
        return True

"""
METODOS AUXILIARES
"""

def get_session_user():
    user = User()
    if 'usuario' in session:
        user = session['usuario']
    return user


def get_movies_in_cart_total_price():
    movies_ids_cart = session.get('cart', [])
    movies_in_cart = []
    total_price = 0
    ret = []
    for i in movies_ids_cart:
        aux = catalogue['peliculas'][int(i[0])]
        movies_in_cart.append((aux,i[1],i[1]*aux["precio"]))
        total_price += aux["precio"]*i[1]

    ret.append(movies_in_cart)
    ret.append(total_price)
    return ret

"""
FUNCIONES DE ENRUTAMIENTO
"""

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', movies=catalogue['peliculas'], categories=dict_genres.keys(), user=get_session_user())


# Ejemplo de uso distinto para GET y POST, no necesario estrictamente
@app.route('/login', methods=['GET'])
def login():
    print(request.form)
    return render_template('login.html', user=get_session_user())

# doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
@app.route('/login', methods=['POST'])
def login_post():
    # TODO: Mensaje de error si una sesion ya iniciada intenta hacer login
    if request.form:
        # Si se manda formulario de inicio de sesion
        user_login = User()
        login_ok = user_login.get_from_server(request.form)
        if login_ok:
            # Login Correcto
            session['usuario'] = user_login     # Settear usuario para la sesion
            session.modified = True             # Automatico aun asi en este caso
            return redirect(request.referrer)
        else:
            # Login Erroneo
            return redirect(url_for('index', movies=catalogue['peliculas'], categories=dict_genres.keys(), user=get_session_user()))
    # Si no hay formulario
    return render_template('login.html', user=get_session_user())


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.form:
        # Si se manda formulario de registro
        user_signup = User()
        try:
            signup_ok = user_signup.create_on_server(request.form)
        except ExistingUserException:
            # TODO: Aviso de usuario ya existente
            return redirect(url_for('index'))

        # Si no ocurre ExistingUserException:
        if signup_ok:
            # Registro Correcto
            return redirect(url_for('login'))
        else:
            # Registro Erroneo
            return redirect(url_for('index'))
    # Si solo se quiere la pagina
    return render_template('signup.html', user=get_session_user())


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    aux = get_movies_in_cart_total_price()
    return render_template('cart.html', movies_in_cart=aux[0], user=get_session_user(), total_price=aux[1])


@app.route('/cart_update/<int:new_number>/<string:id>', methods=['GET', 'POST'])
def cart_update(new_number,id):

    for i in session['cart']:
        if i[0] == id:
            session['cart'].remove(i)
            if new_number != 0:
                session['cart'].append((id,new_number))
            break

    new_price = catalogue['peliculas'][int(id)]['precio']*new_number

    print(str(new_price) + "/" + str(get_movies_in_cart_total_price()[1]))

    return str(new_price) + "/" + str(get_movies_in_cart_total_price()[1])


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


@app.route('/movie_page/<int:id>',methods=['GET', 'POST'])
def movie_page(id):
    return render_template('movie_page.html', user=get_session_user(),movie=catalogue['peliculas'][id])


@app.route('/history',methods=['GET', 'POST'])
def history():
    user = get_session_user()
    if user.is_authenticated:
        history = user.history
        return render_template('history.html', user=user, history=history['Compras'])
    else:
        abort(401)      # Acceso denegado si no esta iniciado sesion


@app.route('/checkout',methods=['GET', 'POST'])
def checkout():
    user = get_session_user()
    if user.is_authenticated:
        aux = get_movies_in_cart_total_price()
        return render_template('checkout.html', user=get_session_user(), num_products=len(aux[0]), total_price=aux[1], user_money = user['saldo'], user_points = user['puntos'])
    else:
        # TODO: Añadir mensaje de aviso de inicio de sesion necesario
        return redirect(url_for('login'))


@app.route('/checkout_pay',methods=['GET', 'POST'])
def checkout_pay():
    logged_user = get_session_user()
    price = get_movies_in_cart_total_price()
    path = os.path.join(app.root_path,"usuarios/"+logged_user['username'] + "/data.dat")
    user_data = open(path, encoding="utf-8").read()
    user = json.loads(user_data)
    if user['saldo'] < price[1] or user['puntos'] < int(request.form['points']):
        return redirect(url_for('checkout',user=get_session_user()))
    else:
        user['puntos'] = user['puntos'] - int(request.form['points'])
        user['saldo'] = user['saldo'] - price[1] + (int(request.form['points'])/100)

        user['saldo'] = user['saldo'] - price[1]

        #Poblamos el JSON del historial
        path = os.path.join(app.root_path,"usuarios/"+logged_user['username'] + "/historial.json")
        history_data = open(path, encoding="utf-8").read()
        history = json.loads(history_data)

        purchase_date = datetime.today()
        aux = get_movies_in_cart_total_price()
        aux2 = aux[0]
        movies_purchased = []
        for i in aux2:
            movies_purchased.append((i[0]['titulo'],i[1]))
        total_purchase_price  = aux [1]

        history['Compras'].append({"fecha":str(datetime.today()),"peliculas_compradas":movies_purchased, "precio_compra":total_purchase_price})

        with open(path, 'w') as outfile:
            json.dump(history, outfile)

        session.pop('cart', None)
        logged_user = get_session_user()
        with open(os.path.join(app.root_path,'usuarios/'+logged_user['username']+'/data.dat'), 'w') as outfile:
            json.dump(user, outfile)
        return redirect(url_for('index', movies=catalogue['peliculas'], categories=dict_genres.keys(), user=get_session_user()))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    session.pop('cart', None)
    return redirect(url_for('index', movies=catalogue['peliculas'], categories=dict_genres.keys(), user=get_session_user()))

#@app.route('/user/<string:user>/history')

# Ruta para numero visitas
@app.route('/num_visitors', methods=['GET'])
def num_visitors():
    n = random.randint(0,100)
    return str(n)

# Ruta para numero de puntos
@app.route('/num_points/<int:change>', methods=['GET', 'POST'])
def num_points(change):
    logged_user = get_session_user()
    path = os.path.join(app.root_path,"usuarios/"+logged_user['username'] + "/data.dat")
    user_data = open(path, encoding="utf-8").read()
    user = json.loads(user_data)
    balance = user['puntos']-change
    if balance < 0:
        return "No tienes puntos suficientes"
    else:
        return "Te quedan " + str(balance) + " puntos"


"""
RUTAS DE CODIGOS DE ESTADO
Invocadas mediante el metodo abort, e.g: abort(401)
"""
@app.errorhandler(401)
def no_access(error):
    mensaje = jsonify({'message':'Failed'})
    # TODO: Usar template de error
    return mensaje, 401
