from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso. Elige otro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese correo electrónico ya está registrado. Inicia sesión o usa otro.')
 
class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')


class CreateItemForm(FlaskForm):
    itemcode  = StringField('Artículo', validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Crear Articulo')

from wtforms import SelectField

class CreateQrForm(FlaskForm):
    codigo_barras = StringField('Código', validators=[DataRequired()])
    itemcode = StringField('Artículo', validators=[DataRequired()])
    proveedor_id = SelectField('Proveedor', choices=[('P0001', 'P0001'), ('P0008', 'P0008')],validators=[DataRequired()])
    pqt = IntegerField('Piezas por paquete', validators=[DataRequired(), NumberRange(min=1, message='El valor debe ser entero positivo')])
    submit = SubmitField('Crear Código')