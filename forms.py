from flask_wtf import FlaskForm
from flask import Markup
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

alfabecik = Markup('Alfabet, <br> np. abcdefghijklmnopqrstuvwxyz_ąćęłńóśźż1234567890, <br> abcdefghijklmnopqrstuvwxyz_かたかなカタカナ片仮名')


class Szyfrowanie(FlaskForm):
    message = StringField('Wiadomość do zaszyfowania',
                        validators=[DataRequired()])
    key = StringField('Tajny klucz', validators=[DataRequired()])
    alphabet = StringField(alfabecik, validators=[DataRequired()])
    submit = SubmitField('Szyfruj')


class Deszyfrowanie(FlaskForm):
    message = StringField('Wiadomość do odszyfrowania',
                        validators=[DataRequired()])
    key = StringField('Tajny klucz', validators=[DataRequired()])
    alphabet = StringField(alfabecik, validators=[DataRequired()])
    submit = SubmitField('Deszyfruj')


class Zgadywane(FlaskForm):
    word = StringField('Pierwsze 4 litery wiadomości',
                        validators=[DataRequired(), Length(max=4, min=4)])
    encrypted = StringField('Zaszyfrowana wiadomość na razie tylko o długości alfabetu wynoszącą 26', validators=[DataRequired()])
    submit = SubmitField('Deszyfruj')


class BruteForce(FlaskForm):
    message = StringField('Zaszyfrowana wiadomośc',
                        validators=[DataRequired(), Length(max=30)])
    alphabet = StringField(alfabecik, validators=[DataRequired(), Length(max=55)])
    submit = SubmitField('ZŁam wiadomość')