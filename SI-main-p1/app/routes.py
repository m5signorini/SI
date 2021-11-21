#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, database
from flask import render_template, request
from flask import url_for, redirect, session, abort, jsonify
import os
import random
import re

# Borrar todas las sesiones, para cuando se cambian tipos de datos
app.secret_key = os.urandom(32)

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
        self.id = 0
        self.username = None
        self.email = None
        self.address = None
        self.payment = None
        self.points = 0
        self.money = 0      # En centimos, dividir por 100

    def validate_checkout(self, cart, form):
        """
        Valida el formulario de pago, comprobando dinero y puntos suficientes,
        utilizando el carrito pasado como argumento que debe ser el de la
        actual sesion, reescribiendo si es correcto en servidor
        """
        if not self.is_authenticated:
            return False
        if not form:
            return False

        if len(cart['orderdetails']) < 1:
            return False

        total_price = cart['order'][5]

        use_money = True
        paymethod = form.get('points', '')
        if paymethod == 'use_points':
            use_money = False
        if not use_money:
            if self.points < total_price * 100:
                return False
            self.points -= int(total_price * 100)
            self.update_on_server()
            database.db_updateOrder(cart['order'][0], 'Paid')
            return True
        else:
            if self.money < total_price * 100:
                return False
            self.money -= int(total_price * 100)
            self.update_on_server()
            database.db_updateOrder(cart['order'][0], 'Paid')
            return True

    def validate_signup_form(self, form):
        """
        Valida un formulario con los datos de usuario actualizando el objeto
        actual y devolviendo True si la validacion ha tenido exito
        """
        data = form.to_dict()
        # Comprobar username:
        # InvalidForm
        if 'signusername' not in data.keys():
            return False
        # ValidUsername
        regex = r"^([a-zA-Z0-9]){6,}$"
        if not re.match(regex, data['signusername']):
            return False
        # ExistingUsername
        if data['signusername'] in database.db_getCustomersUsernames():
            raise ExistingUserException(data['signusername'])
        # Comprobar email:
        # InvalidForm
        if 'email' not in data.keys():
            return False
        # ValidEmail
        regex = r"^([a-z]|[A-Z]|[0-9]|_)+@[a-zA-Z0-9_]+\.[a-z]+$"
        if not re.match(regex, data['email']):
            return False

        # Comprobar direccion:
        # InvalidForm
        if 'address' not in data.keys():
            return False
        # ValidAddress
        regex = r"^(.){1,50}$"
        if not re.match(regex, data['address']):
            return False

        # Comprobar tarjeta:
        # InvalidForm
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
        self.money = random.randint(0, 100) * 100
        self.points = 0

        return True

    def update_from_server(self):
        """
        Obtiene de nuevo los datos a partir de su data.dat,
        usando self.username.
        Solamente es necesario por ahora recargar dinero y puntos
        """
        data = database.db_getCustomerById(self.id)
        self.money = data['money']
        self.points = data['points']
        return True

    def update_on_server(self):
        """
        Usando los datos de este objeto, actualiza los valores guardados en
        su correspondiente fichero data.dat y en historial.json
        """
        # Comprobar validez del usuario
        if not self.is_authenticated:
            return False

        data = database.db_getCustomerById(self.id)
        # Por ahora solo se puede modificar el dinero y los puntos
        data['points'] = self.points
        data['money'] = self.money
        database.db_updateCustomerById(self.id, data)
        return True

    def create_on_server(self, form):
        """
        Dada la informacion de un formulario, la valida y crea el usuario del
        lado del servidor actualizando este objeto a su vez
        """
        if not self.validate_signup_form(form):
            return False
        data = {
            'username': str(self.username),
            'password': str(form['signpassword']),
            'payment': str(self.payment),
            'email': str(self.email),
            'address': str(self.address),
            'money': str(self.money),
            'points': str(self.points)
        }
        database.db_insertCustomer(data)
        return True

    def get_from_server(self, form):
        """
        Dado un formulario de inicio de sesion inicializa este
        objeto obteniendo
        los datos necesarios de la carpeta correspondiente,
        devolviendo True en
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

        if form['username'] not in database.db_getCustomersUsernames():
            return False

        data = database.db_getCustomerByUsername(
            form['username'], form['password'])
        if not data:
            return False

        # Actualizar usuario con los datos:
        self.username = data['username']
        self.id = data['id']
        self.email = data['email']
        self.address = data['address']
        self.payment = data['payment']
        self.money = data['money']
        self.points = data['points']
        self.is_authenticated = True
        return True

    def toJSON(self):
        data = self.__dict__
        return data

    def loadJSON(self, data):
        self.username = data.get('username', None)
        self.email = data.get('email', None)
        self.address = data.get('address', None)
        self.payment = data.get('payment', None)
        self.id = data.get('id', 0)
        self.money = data.get('money', 0)
        self.points = data.get('points', 0)
        self.is_authenticated = data.get('is_authenticated', False)
        return


class Cart:
    def __init__(self):
        # Diccionario product_id : cantidad
        self.items = dict()

    def add_movie_to_cart(self, product_id):
        if len(database.db_getProductByIdAlert(product_id)) != 0:
            return False

        if product_id not in self.items:
            self.items[product_id] = 0
        self.items[product_id] += 1
        return True

    def update_movie_in_cart(self, product_id, number):
        if len(database.db_getProductByIdAlert(product_id)) != 0:
            return
        if number <= 0:
            self.items.pop(product_id, None)
            return
        if product_id not in self.items:
            self.items[product_id] = 0
        self.items[product_id] = number
        return

    def get_movies_in_cart(self):
        result = []
        for product_id, quantity in self.items.items():
            movie = database.db_getCartDataFromProdId(product_id)
            item = movie['orderdetail'][0]
            result.append({'pelicula': {
                'titulo': item[0],
                'precio': item[1],
                'descripcion': item[2],
                'id': product_id},
                'cantidad': quantity,
                'importe': quantity * item[1],
                'stock': database.db_getStockLeft(product_id)})
        return result

    def get_total_items(self):
        total = 0
        for id, quantity in self.items.items():
            total += 1
        return total

    def get_total_price(self):
        accum = 0
        for product_id in self.items:
            accum += self.get_item_price(product_id)
        return accum

    def get_item_price(self, product_id):
        # El catalogo se haya indexado por id:
        # id = int(product_id)
        if len(database.db_getProductByIdAlert(product_id)) != 0:
            return 0
        quantity = self.items.get(product_id, 0)
        price = database.db_getProductPrice(product_id)
        return price * quantity

    def toJSON(self):
        data = self.__dict__
        return data

    def loadJSON(self, data):
        self.items = data.get('items', dict())
        return

# Adicionalmente podria plantearse el uso de una clase pelicula


"""
METODOS AUXILIARES
"""


def get_session_user():
    user = User()
    if 'usuario' in session:
        user.loadJSON(session['usuario'])
    return user


def get_session_cart():
    cart = Cart()
    if 'cart' in session:
        cart.loadJSON(session['cart'])
    return cart


def get_all_categories():
    aux = database.db_genres()
    categories = list()
    for item in aux:
        categories.append(item[0])
    return categories


"""
FUNCIONES DE ENRUTAMIENTO
"""


@app.route('/')
@app.route('/index')
def index():
    categories = get_all_categories()
    movies = database.db_populateCatalog()
    return render_template(
        'index.html',
        movies=movies,
        categories=categories,
        user=get_session_user())


# doc sobre request object en
# http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
@app.route('/login', methods=['GET', 'POST'])
def login():
    # TODO: Mensaje de error si una sesion ya iniciada intenta hacer login
    if request.form:
        # Si se manda formulario de inicio de sesion
        user_login = User()
        login_ok = user_login.get_from_server(request.form)
        if login_ok:
            # Login Correcto
            # Settear usuario para la sesion
            session['usuario'] = user_login.toJSON()
            session['last_user'] = user_login.username
            # Automatico aun asi en este caso
            session.modified = True
            if 'return' in session:
                url = session['return']
                session.pop('return')
                return redirect(url)
            return redirect(url_for('index'))
        else:
            # Login Erroneo
            return render_template(
                'login.html',
                user=get_session_user(),
                last_user=None)
    # Si no hay formulario
    last_user = session.get('last_user', None)
    return render_template(
        'login.html',
        user=get_session_user(),
        last_user=last_user)

# Ejemplo de uso distinto para GET y POST, no necesario estrictamente


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html', user=get_session_user())


@app.route('/signup', methods=['POST'])
def signup_post():
    if request.form:
        # Si se manda formulario de registro
        user_signup = User()
        try:
            signup_ok = user_signup.create_on_server(request.form)
        except ExistingUserException:
            # TODO: Aviso de usuario ya existente
            error = "El usuario introducido ya estaba registrado"
            return render_template(
                'signup.html',
                user=get_session_user(),
                error=error)

        # Si no ocurre ExistingUserException:
        if signup_ok:
            # Registro Correcto
            return redirect(url_for('login'))
        else:
            # Registro Erroneo
            # TODO: Aviso error de registro
            return redirect(url_for('index'))
    # Si solo se quiere la pagina
    return render_template('signup.html', user=get_session_user())


@app.route('/top_actors/<string:genre>', methods=['GET'])
def top_actors(genre):
    top_actors = database.db_topActorsByGenre(genre)
    return render_template(
        'top_actors.html',
        user=get_session_user(),
        top_actors=top_actors,
        genre=genre)


@app.route('/cart', methods=['GET'])
def cart():
    user = get_session_user()

    if user.is_authenticated:
        # Primero revisamos si antes de loggear habia
        # un carrito con algun articulo cargado
        # para cargar los articulos de este en el carrito
        # de nuestro usuario al
        # loguear
        cart = get_session_cart()

        if cart.get_total_items() != 0:
            database_cart = database.db_getUserActualCart(user.id)
            for item in cart.get_movies_in_cart():
                flag = 0
                for ele in database_cart['orderdetails']:
                    if item['pelicula']['id'] == ele[5] and flag == 0:
                        dif = abs(item['cantidad'] - ele[1])
                        if dif != 0:
                            database.db_updateOrderdetail(
                                database_cart['order'][0],
                                item['pelicula']['id'],
                                item['cantidad'])
                        cart.update_movie_in_cart(item['pelicula']['id'], 0)
                        flag = 1
                if flag == 0:
                    database.db_insertOrderdetail(
                        database_cart['order'][0],
                        item['pelicula']['id'],
                        user.id)
                    if item['cantidad'] > 1:
                        database.db_updateOrderdetail(
                            database_cart['order'][0],
                            item['pelicula']['id'],
                            item['cantidad'])
                    cart.update_movie_in_cart(item['pelicula']['id'], 0)

        session['cart'] = cart.toJSON()
        cart = database.db_getUserActualCart(user.id)
        movies_data = []    # Includes prices and quantity
        for item in cart['orderdetails']:
            movies_data.append(
                {
                    'pelicula': {
                        'titulo': item[0],
                        'precio': item[3],
                        'descripcion': item[4],
                        'id': item[5]},
                    'cantidad': item[1],
                    'importe': item[2],
                    'stock': database.db_getStockLeft(
                        item[5])})
        total_price = cart['order'][5]
        return render_template(
            'cart.html',
            movies_in_cart=movies_data,
            user=user,
            total_price=total_price)

    else:
        cart = get_session_cart()
        movies_data = cart.get_movies_in_cart()
        total_price = cart.get_total_price()
        total_price = round(total_price * 1.15, 2)
        return render_template(
            'cart.html',
            movies_in_cart=movies_data,
            user=user,
            total_price=total_price)


@app.route('/cart_update/<int:new_number>/<string:id>',
           methods=['GET', 'POST'])
def cart_update(new_number, id):

    user = get_session_user()
    if user.is_authenticated:
        cart = database.db_getUserActualCart(user.id)
        database.db_updateOrderdetail(cart['order'][0], id, new_number)

        cart = database.db_getUserActualCart(user.id)

        for item in cart['orderdetails']:
            if item[5] == int(id):
                price = item[2]             # cart.get_item_price(id)
                total = cart['order'][5]    # cart.get_total_price()
                return f"{price}/{total}"

        price = 0                           # cart.get_item_price(id)
        total = cart['order'][5]            # cart.get_total_price()
        return f"{price}/{total}"

    else:
        cart = get_session_cart()
        cart.update_movie_in_cart(id, new_number)

        price = cart.get_item_price(id)
        total = cart.get_total_price()
        total = round(total * 1.15, 2)

        session['cart'] = cart.toJSON()
        session.modified = True

        return f"{price}/{total}"


@app.route('/movie_page/add_to_cart/<string:prod_id>', methods=['GET', 'POST'])
def add_to_cart(prod_id):
    user = get_session_user()

    if not prod_id.isdigit():
        return jsonify(False)

    if user.is_authenticated:
        cart = database.db_getUserActualCart(user.id)
        result = database.db_insertOrderdetail(
            cart['order'][0], prod_id, user.id)
        return jsonify(result)

    else:
        cart = get_session_cart()
        result = cart.add_movie_to_cart(prod_id)

        session['cart'] = cart.toJSON()
        session.modified = True

        return jsonify(result)


@app.route('/movie_page/<int:id>', methods=['GET', 'POST'])
def movie_page(id):
    movie = database.db_getMovieInfo(id)
    products = database.db_getProductsByMovie(id)
    return render_template(
        'movie_page.html',
        user=get_session_user(),
        movie=movie,
        products=products)


@app.route('/history', methods=['GET'])
def history():
    user = get_session_user()
    if user.is_authenticated:
        history = database.db_generateHistoryData(user.id)
        return render_template(
            'history.html',
            user=user,
            history=history['Compras'])
    else:
        abort(401)      # Acceso denegado si no esta iniciado sesion


@app.route('/checkout', methods=['GET'])
def checkout():
    user = get_session_user()
    if user.is_authenticated:
        # aux = get_movies_in_cart_total_price()
        cart = database.db_getUserActualCart(user.id)
        num_products = 0
        for prod in cart['orderdetails']:
            num_products += prod[1]
        total_price = cart['order'][5]
        if num_products < 1:
            return redirect('/cart')
        return render_template(
            'checkout.html',
            user=get_session_user(),
            num_products=num_products,
            total_price=total_price)
    else:
        # TODO: Añadir mensaje de aviso de inicio de sesion necesario
        session['return'] = url_for('checkout')
        return redirect(url_for('login'))


@app.route('/checkout_pay', methods=['POST'])
def checkout_pay():
    if not request.form:
        return redirect(url_for('index'))
    user = get_session_user()
    if not user.is_authenticated:
        # TODO: Acceso restringido
        return abort(401)
    # Actualizamos usuario desde el servidor por si se ha realizado algun
    # cambio
    cart = database.db_getUserActualCart(user.id)
    user.update_from_server()
    session['usuario'] = user.toJSON()
    session.modified = True
    # Comprobamos formulario enviado es valido
    if not user.validate_checkout(cart, request.form):
        # TODO: Mensaje de error pago erroneo
        return redirect(url_for('checkout'))
    else:
        # Si lo era se habra realizado la transaccion
        # session.pop('cart')
        user.update_from_server()
        session['usuario'] = user.toJSON()
        session.modified = True
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Hacer logout siempre se puede pese a no estar iniciado sesion
    session.pop('usuario', None)
    session.pop('cart', None)
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET'])
def profile():
    user = get_session_user()
    if not user.is_authenticated:
        abort(401)
    user.update_from_server()
    session['usuario'] = user.toJSON()
    session.modified = True
    return render_template('profile.html', user=user)


@app.route('/profile_add_money', methods=['POST'])
def profile_add_money():
    user = get_session_user()
    if not user.is_authenticated:
        abort(401)
    if request.form:
        added_money = int(request.form.get('add_money', 0))
        if added_money < 0:
            added_money = 0
        user.update_from_server()
        user.money += added_money
        user.update_on_server()
        session['usuario'] = user.toJSON()
        session.modified = True
        return redirect(url_for('profile'))
    else:
        abort(401)

# @app.route('/user/<string:user>/history')

# Ruta para numero visitas


@app.route('/num_visitors', methods=['GET'])
def num_visitors():
    n = random.randint(0, 100)
    return str(n)

# Ruta para restar numero de puntos


@app.route('/num_points/<int:change>', methods=['GET', 'POST'])
def num_points(change):
    user = get_session_user()
    user.update_from_server()
    session['usuario'] = user.toJSON()
    session.modified = True
    balance = user.points - change
    if balance < 0:
        return "No tienes puntos suficientes"
    else:
        return "Te quedarían " + str(balance) + " puntos"

# Ruta para realizar busquedas


@app.route('/search', methods=['GET'])
def search_movies():
    # request.form es multidict, asi pues:
    # usar request.form.getlist('category')
    try:
        query = request.values.get('search', '')
        categories = request.values.getlist('category')
        if len(categories) < 1:
            categories = get_all_categories()
        results = database.db_searchMovies(query, categories)
        return render_template(
            'search.html',
            movies=results,
            categories=get_all_categories(),
            user=get_session_user())
    except BaseException:
        abort(401)

# Ruta para obtener listado de top actores


@app.route('/get_topactors', methods=['GET'])
def get_topactors():
    genre = request.values.get('genre', None)
    if not genre:
        return jsonify([])
    results = database.db_topActorsByGenre(genre)
    to_json = jsonify(results)
    return to_json


"""
RUTAS DE CODIGOS DE ESTADO
Invocadas mediante el metodo abort, e.g: abort(401)
"""


@app.errorhandler(401)
def no_access(error):
    mensaje = jsonify({'message': 'Acceso denegado'})
    # TODO: Usar template de error
    return mensaje, 401


def existing_user():
    mensaje = jsonify({'message': 'Usuario ya existente'})
    # TODO: Usar template de error
    return mensaje, 409


def login_error():
    mensaje = jsonify({'message': 'Credenciales no validas'})
    # TODO: Usar template de error
    return mensaje, 400
