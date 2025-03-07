"""
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt
from app.models import User
from app.forms import LoginForm, RegistrationForm 

auth = Blueprint('auth', __name__)  

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Inicio de sesión fallido. Verifica tus credenciales.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Tu cuenta ha sido creada. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
"""
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt  # Importa la base de datos y el sistema de hashing de contraseñas
from app.models import User  # Importa el modelo de Usuario
from app.forms import LoginForm, RegistrationForm  # Importa los formularios de inicio de sesión y registro

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
            flash('Inicio de sesión exitoso', 'success')  # Muestra un mensaje de éxito
            return redirect(url_for('main.home'))  # Redirige a la página principal
        else:
            flash('Inicio de sesión fallido. Verifica tus credenciales.', 'danger')  # Muestra un mensaje de error
    
    # Renderiza la plantilla de inicio de sesión con el formulario
    return render_template('login.html', form=form)

# Ruta para el registro de nuevos usuarios
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Si el usuario ya está autenticado, redirige a la página principal
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Crea una instancia del formulario de registro
    form = RegistrationForm()
    
    # Valida si el formulario se envió correctamente
    if form.validate_on_submit():
        # Hashea la contraseña proporcionada por el usuario
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Crea un nuevo usuario con los datos del formulario
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        # Añade el usuario a la base de datos y guarda los cambios
        db.session.add(user)
        db.session.commit()
        
        flash('Tu cuenta ha sido creada. Ahora puedes iniciar sesión.', 'success')  # Muestra un mensaje de éxito
        return redirect(url_for('auth.login'))  # Redirige a la página de inicio de sesión
    
    # Renderiza la plantilla de registro con el formulario
    return render_template('register.html', form=form)

# Ruta para cerrar sesión
@auth.route('/logout')
def logout():
    logout_user()  # Cierra la sesión del usuario actual
    return redirect(url_for('auth.login'))  # Redirige a la página de inicio de sesión
