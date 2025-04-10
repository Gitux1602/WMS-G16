from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt 
from app.models import User  
from app.forms import CreateItemForm, CreateQrForm

item = Blueprint('articulo', __name__)


@item.route('/crear', methods=['GET'])
def seleccionar_crear():
    return render_template('seleccionar_crear.html')


@item.route('/crear/articulo', methods=['GET', 'POST'])
def crear_articulo():
    form = CreateItemForm()
    if form.validate_on_submit():
        # Lógica para guardar el artículo
        return redirect(url_for('articulo.seleccionar_crear'))
    return render_template('crear_articulo.html', form=form)


@item.route('/crear/codigo', methods=['GET', 'POST'])
def crear_codigo():
    form = CreateQrForm()
    if form.validate_on_submit():
        # Lógica para generar el código QR
        return redirect(url_for('articulo.seleccionar_crear'))
    return render_template('crear_codigo.html', form=form)
"""
@auth.route('/login', methods=['GET', 'POST'])
def login():
    
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
            flash('Inicio de sesión fallido. Verifica tus credenciales.', 'danger')  # Muestra un mensaje de error
    
    # Renderiza la plantilla de inicio de sesión con el formulario
    return render_template('login.html', form=form)

"""