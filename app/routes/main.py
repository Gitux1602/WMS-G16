from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import current_user, login_required
from app.forms import RegistrationForm
from app.models import BaseDatosEnum, User
from app import db, bcrypt

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    return render_template('home.html')

@main.route('/seleccionar_base_datos', methods=['GET', 'POST'])
@login_required
def seleccionar_base_datos():
    if request.method == 'POST':
        basedatos = request.form.get('basedatos')
        if basedatos:
            # Guardar la base de datos seleccionada
            basedatos_seleccionada = basedatos
            return render_template('seleccionar_base_datos.html', 
                                 opciones_basedatos=[bd.value for bd in BaseDatosEnum],
                                 basedatos_seleccionada=basedatos_seleccionada)
        else:
            flash('Debes seleccionar una base de datos', 'danger')

    opciones_basedatos = [bd.value for bd in BaseDatosEnum]
    return render_template('seleccionar_base_datos.html', 
                         opciones_basedatos=opciones_basedatos,
                         basedatos_seleccionada=None)

@main.route('/conteo_sap/<basedatos>') 
@login_required
def conteo_sap(basedatos):
    return render_template('conteo_sap.html', basedatos=basedatos)


# Ruta para el registro de nuevos usuarios
@main.route('/register', methods=['GET', 'POST'])
def register():

    # Crea una instancia del formulario de registro
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Crea un nuevo usuario con los datos del formulario
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Tu cuenta ha sido creada. Ahora puedes iniciar sesión.', 'success') 
        return redirect(url_for('main.home'))  # Redirige a la página de inicio de sesión
    
    return render_template('register.html', form=form)