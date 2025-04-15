from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt 
from app.models import User, Articulo
from app.forms import CreateItemForm, CreateQrForm

item = Blueprint('articulo', __name__)


@item.route('/crear', methods=['GET'])
def seleccionar_crear():
    return render_template('seleccionar_crear.html')

@item.route('/crear/articulo', methods=['GET', 'POST'])
def crear_articulo():
    form = CreateItemForm()
    
    # Limpiar flashes anteriores
    from flask import get_flashed_messages
    get_flashed_messages()  # Consume los flashes existentes
    
    if form.validate_on_submit():
        articulo = Articulo.query.filter_by(itemcode=form.itemcode.data).first()
        
        if articulo is not None:
            flash(f'El artículo {articulo.itemcode} ya existe en el sistema.', 'danger')
        else:
            nuevo_articulo = Articulo(
                itemcode=form.itemcode.data,
                descripcion=form.descripcion.data,
                frngname=form.frngname.data
            )
            db.session.add(nuevo_articulo)
            db.session.commit()
            flash(f'Artículo {nuevo_articulo.itemcode} creado exitosamente!', 'success')
        
        return redirect(url_for('articulo.crear_articulo'))

    return render_template('crear_articulo.html', form=form)


@item.route('/crear/codigo', methods=['GET', 'POST'])
def crear_codigo():
    form = CreateQrForm()
    if form.validate_on_submit():
        # Lógica para generar el código QR
        return redirect(url_for('articulo.seleccionar_crear'))
    return render_template('crear_codigo.html', form=form)
