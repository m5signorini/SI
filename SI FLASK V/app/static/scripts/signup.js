

// Esperar a que todos los elementos del DOM estén cargados
$('document').ready(init);

function init() {
    $('#signpassword').on('change', password_input);
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
    set_password_message(target.next(), mens, color);
    return;
}

function get_password_strength(password) {

    return password.length;
}

function set_password_message(element, message, color) {
    element.text(message);
    element.css({'color':color});
}
