

// Esperar a que todos los elementos del DOM estén cargados
$('document').ready(init);

function init() {
    $('.user_form').on('submit', validate_form);
    $('#signpassword').on('input', password_input);
    $('#confsignpassword').on('input', confirm_input);
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
}

function validate_email() {
    let mail = $('#email').val();
    let regex = /^([a-z]|[A-Z]|[0-9]|_)+@[a-zA-Z0-9_]+\.[a-z]+$/gm;
    return regex.test(mail);
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
            mens = 'Contraseña segura';
            color = 'green';
        }
        else {
            mens = 'Contraseña intermedia';
            color = 'orange';
        }
    }
    else {
        mens = 'Contraseña insegura';
        color = 'red';
    }
    set_span_message($('#strength_1'), mens, color);
    return;
}

function get_password_strength(password) {
    let tests = [/[0-9]+/,/[a-z]+/,/[A-Z]+/,/.{6,}/,/.{7,}/,/.{8,}/,/.{9,}/,/[-!$%^&*()_+|~=`{}\[\]:";'<>?,.\/]+/];
    let stren = 0;
    if(password.length < 6) {
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


function confirm_input(e) {
    let target = $(e.target);
    let value = target.val();
    let mens = 'Contraseña incorrecta, debe ser la misma';
    let color = 'red';
    // Comparamos con password
    if(value == $('#signpassword').val()) {
        mens = 'Contraseña correcta';
        color = 'green';
    }
    set_span_message($('#strength_3'), mens, color);
    return;
}
