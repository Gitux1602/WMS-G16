from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt 
from app.models import CodigoBarras, User, Articulo
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
        # Convertir a mayúsculas (excepto números, que se mantienen igual)
        itemcodeform = form.itemcode.data.upper() if isinstance(form.itemcode.data, str) else form.itemcode.data
        descripcion = form.descripcion.data.upper() if isinstance(form.descripcion.data, str) else form.descripcion.data
        frngname = form.frngname.data.upper() if isinstance(form.frngname.data, str) else form.frngname.data
        
        articulo = Articulo.query.filter_by(itemcode=itemcodeform).first()
        
        if articulo is not None:
            flash(f'El artículo {articulo.itemcode} ya existe en el sistema', 'danger')
        else:
            nuevo_articulo = Articulo(
                itemcode=itemcodeform,
                descripcion=descripcion,
                frngname=frngname
            )
            db.session.add(nuevo_articulo)
            db.session.commit()
            flash(f'Artículo {nuevo_articulo.itemcode} creado exitosamente!', 'success')
        
        return redirect(url_for('articulo.seleccionar_crear'))

    return render_template('crear_articulo.html', form=form)


@item.route('/crear/codigo', methods=['GET', 'POST'])
def crear_codigo():
    form = CreateQrForm()
    
    if form.validate_on_submit():
        # Primero validar que el itemcode exista
        articulo = Articulo.query.filter_by(itemcode=form.itemcode.data).first()
        if not articulo:
            flash(f'El artículo con código {form.itemcode.data} no existe en el sistema', 'danger')
            return redirect(url_for('articulo.seleccionar_crear'))
        
        # Luego validar que el código de barras no exista
        codigo = CodigoBarras.query.filter_by(codigo_barras=form.codigo_barras.data).first()
        if codigo is not None:
            flash(f'El código de barras {codigo.codigo_barras} ya existe en el sistema', 'danger')
            return redirect(url_for('articulo.seleccionar_crear'))
        
        # Validación de formato del código de barras
        pipes = 0
        pipe_positions = []
        data = form.codigo_barras.data

        # Encontrar las posiciones de los pipes
        for i, char in enumerate(data):
            if char == "|":
                pipes += 1
                pipe_positions.append(i)

        if pipes != 2:
            flash('El código de barras debe tener exactamente 2 pipes (|)', 'danger')
            return redirect(url_for('articulo.seleccionar_crear'))
        
        # Obtener la parte después del segundo pipe
        part_after_last_pipe = data[pipe_positions[1]+1:]
    
        # Verificar que solo contenga números
        if not part_after_last_pipe.isdigit():
            flash('Después del segundo pipe solo deben haber números', 'danger')
            return redirect(url_for('articulo.seleccionar_crear'))
        
        nuevo_codigo = CodigoBarras(
            codigo_barras=form.codigo_barras.data,
            itemcode=form.itemcode.data,
            proveedor_id=form.proveedor_id.data,
            pqt=form.pqt.data
        )
        
        db.session.add(nuevo_codigo)
        db.session.commit()
        
        flash(f'Código de barras {form.codigo_barras.data} creado exitosamente', 'success')
        return redirect(url_for('articulo.seleccionar_crear'))
    
    return render_template('crear_codigo.html', form=form)