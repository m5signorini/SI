

// Esperar a que todos los elementos del DOM estén cargados
$('document').ready(init);

function init() {
    $('.user_form').on('submit', validate_form);
    $('#signpassword').on('input', password_input);
    $('#confsignpassword').on('input', confirm_input);
    $('#signusername').on('input', username_input);
    $('#email').on('input', email_input);
    $('#address').on('input', address_input);
    $('#payment').on('input', payment_input);
}

function validate_form(e) {
    let pass = $('#signpassword').val();
    let conf = $('#confsignpassword').val();
    // Misma contraseña
    if(pass != conf) {
        set_span_message($('#submit_result'), 'Contraseñas distintas', 'red');
        return false;
    }
    // Contraseña al menos intermedia
    if(get_password_strength(pass) < 4) {
        set_span_message($('#submit_result'), 'Contraseña demasiado débil', 'red');
        return false;
    }
    if(!validate_email()) {
        set_span_message($('#submit_result'), 'Correo no válido', 'red');
        return false;
    }
    if(!validate_username()) {
        set_span_message($('#submit_result'), 'Nombre de usuario al menos 6 caracteres', 'red');
        return false;
    }
    if(!validate_address()) {
        set_span_message($('#submit_result'), 'Dirección de entrega máximo 50 caracteres, no especiales', 'red');
        return false;
    }
    if(!validate_payment()) {
        set_span_message($('#submit_result'), 'Número de tarjeta de crédito no válido (16 digitos)', 'red');
        return false;
    }
}

function validate_email() {
    let mail = $('#email').val();
    let regex = /^([a-z]|[A-Z]|[0-9]|_)+@[a-zA-Z0-9_]+\.[a-z]+$/gm;
    return regex.test(mail);
}

function validate_username() {
    let name = $('#signusername').val();
    let regex = /^([a-zA-Z0-9]){6,}$/gm;
    return regex.test(name);
}

function validate_address() {
    let address = $('#address').val();
    let regex = /^(.){1,50}$/gm;
    return regex.test(address);
}

function validate_payment() {
    let payment = $('#payment').val();
    let regex = /^([0-9]){16,16}$/gm;
    return regex.test(payment);
}




/**
Funcion de callback para el evento de modificar la entrada de la contraseña para
el formulario de registro. Reconoce la contraseña y muestra su nivel de seguridad
*/
function password_input(e) {
    let target = $(e.target);
    let value = target.val();
    let stren = get_password_strength(value);
    let mens, color;
    if(stren > 3) {
        if(stren > 6) {
            mens = 'Contraseña fuerte';
            color = 'green';
        }
        else {
            mens = 'Contraseña media';
            color = 'orange';
        }
    }
    else {
        mens = 'Contraseña débil';
        color = 'red';
    }
    set_span_message($('#strength_1'), mens, color);
    return;
}

function confirm_input(e) {
    let target = $(e.target);
    let value = target.val();
    let mens = 'Contraseña incorrecta, debe ser la misma';
    let color = 'red';
    // Comparamos con password
    if(value == $('#signpassword').val()) {
        mens = 'Contraseña correcta, es la misma';
        color = 'green';
    }
    set_span_message($('#strength_3'), mens, color);
    return;
}

function username_input(e) {
    set_border_color_by_test($(e.target), validate_username());
}
function email_input(e) {
    set_border_color_by_test($(e.target), validate_email());
}
function payment_input(e) {
    set_border_color_by_test($(e.target), validate_payment());
}
function address_input(e) {
    set_border_color_by_test($(e.target), validate_address());
}

/**
FUNCIONES AUXILIARES
*/
function get_password_strength(password) {
    let tests = [/[0-9]+/,/[a-z]+/,/[A-Z]+/,/.{9,}/,/.{10,}/,/.{11,}/,/.{12,}/,/[-!$%^&*()_+|~=`{}\[\]:";'<>?,.\/]+/];
    let stren = 0;
    if(password.length < 8) {
        return 0;
    }
    tests.forEach(t => {
        if(password.match(t)) {
            stren++;
        }
    })
    return stren;
}

function set_span_message(element, message, color) {
    element.text(message);
    element.css({'color':color});
}

function set_border_color_by_test(element, test) {
    if(test == true) {
        element.css({'border-color':'green'});
    }
    else {
        element.css({'border-color':'red'});
    }
}
