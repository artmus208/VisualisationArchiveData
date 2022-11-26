from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired
from Connect2DB import archives_gen

class SelectTableForm(FlaskForm):
    submit = SubmitField('Выбрать')    
    tableSelector = SelectField("Выбор таблицы: ", validators=[DataRequired()])

class SelectDateParamForm(FlaskForm):
    dateStart = DateField("Дата от: ", format="%Y-%m-%d")
    dateEnd = DateField("Дата до: ", format="%Y-%m-%d")
    submit = SubmitField('Визуализировать!')
    Parameters = SelectMultipleField("Выбор параметров: ")

    


