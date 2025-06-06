from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt  # Importa la base de datos y el sistema de hashing de contraseñas
from app.models import User  
from app.forms import LoginForm

# Creación de un Blueprint para agrupar las rutas relacionadas con la autenticación
auth = Blueprint('auth', __name__)

# Ruta para el inicio de sesión
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está autenticado, redirige a la página principal
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Crea una instancia del formulario de inicio de sesión
    form = LoginForm()
    
    # Valida si el formulario se envió correctamente
    if form.validate_on_submit():
        # Busca al usuario en la base de datos por su correo electrónico
        user = User.query.filter_by(email=form.email.data).first()
        
        # Verifica si el usuario existe y si la contraseña es correcta
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Inicia sesión con el usuario
            login_user(user)
            return redirect(url_for('main.home'))  # Redirige a la página principal
        else:
            print("Credenciales incorrectas")
            # flash('Inicio de sesión fallido. Verifica tus credenciales.', 'danger')  # Muestra un mensaje de error
    
    # Renderiza la plantilla de inicio de sesión con el formulario
    return render_template('login.html', form=form)

# Ruta para cerrar sesión
@auth.route('/logout')
def logout():
    logout_user()  # Cierra la sesión del usuario actual
    return redirect(url_for('auth.login'))  # Redirige a la página de inicio de sesión
