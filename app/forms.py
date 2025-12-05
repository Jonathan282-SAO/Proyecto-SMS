try:
	from flask_wtf import FlaskForm
	from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField, HiddenField
	from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional


	class LoginForm(FlaskForm):
		username = StringField('Usuario', validators=[DataRequired(), Length(max=80)])
		password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=128)])


	class ChangePasswordForm(FlaskForm):
		actual = PasswordField('Actual', validators=[DataRequired()])
		nueva = PasswordField('Nueva', validators=[DataRequired(), Length(min=8)])
		confirmar = PasswordField('Confirmar', validators=[DataRequired(), EqualTo('nueva')])


	class GroupForm(FlaskForm):
		nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
		usuarios = SelectMultipleField('Usuarios', coerce=int, validators=[Optional()])


	class AddUserForm(FlaskForm):
		username = StringField('Usuario', validators=[DataRequired(), Length(max=80)])
		email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
		password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
		role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])


	class CampaignForm(FlaskForm):
		name = StringField('Name', validators=[DataRequired(), Length(max=100)])
		message = TextAreaField('Message', validators=[DataRequired(), Length(max=4000)])
except Exception:
	# Fallback lightweight forms if WTForms/Flask-WTF not installed.
	# These provide only validate_on_submit() so routes can still work using request.form as fallback.
	from flask import request

	class _BaseFallbackForm:
		def validate_on_submit(self):
			return request.method == 'POST'

	class LoginForm(_BaseFallbackForm):
		pass

	class ChangePasswordForm(_BaseFallbackForm):
		pass

	class GroupForm(_BaseFallbackForm):
		pass

	class AddUserForm(_BaseFallbackForm):
		pass

	class CampaignForm(_BaseFallbackForm):
		pass
