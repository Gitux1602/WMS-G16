from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_required
from app.models import BaseDatosEnum

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

@main.route('/conteo_sap/<basedatos>') #Redirige a conteo_sap.html
@login_required
def conteo_sap(basedatos):
    return render_template('conteo_sap.html', basedatos=basedatos)
