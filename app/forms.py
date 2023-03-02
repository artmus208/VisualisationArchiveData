from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, widgets, SubmitField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired
from Connect2DB import archives_gen

class SelectTableForm(FlaskForm):
    submit = SubmitField('Выбрать')    
    tableSelector = SelectField("Выбор таблицы: ", validators=[DataRequired()])

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SelectDateParamForm(FlaskForm):
    dateStart = DateField("Дата от: ", format="%Y-%m-%d")
    dateEnd = DateField("Дата до: ", format="%Y-%m-%d")
    submit = SubmitField('Визуализировать!')
    Parameters = MultiCheckboxField("Выбор параметров: ")

    


