from app import app
from flask import render_template, flash, redirect, url_for, request
from plotly.subplots import make_subplots
from app.forms import SelectDateParamForm, SelectTableForm
from Connect2DB import *
import json
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.io as pio
connect = Connect2MDB()
cursor = GetCursor(connect)
selectedTable = "0"

def GetStructure(selectedParamsList, table, dataStart, dataEnd):
    selectedParamsStr = ", ".join(selectedParamsList)
    max_values, min_values = GetMaxMinValuesSelectedParams(cursor=cursor,
                                                           dateStart=dataStart, 
                                                           dateEnd=dataEnd,
                                                           tableName=table,
                                                           selParamsList=selectedParamsList)
   
    # Запрос только на получение данных выбранных категорий 
    selectedQuery = QueryDataGeneration(tablename=table, 
                                        startDate=dataStart, 
                                        endDate=dataEnd, 
                                        parameter=selectedParamsStr)
    ExecuteQuery(cursor=cursor, query=selectedQuery)
    selectedResult=GetResult(cursor=cursor)

    dateTimeList = GetDateTimeList(selectedResult)

    # Сортируем пары (параметр, максимум) в порядке возрастания максимума
    sorted_par_max_pares = GetSortedParamsMaxPares(selectedResult=selectedResult, 
                                                   selectedParamsList=selectedParamsList, 
                                                   max_values=max_values)
    # Делаем категории 
    categoriesList = MakeCategories(sorted_par_max_pares)    
    checkCount = 0
    for i, cl in enumerate(categoriesList):
        checkCount += len(cl)
        print("Category: ",i+1)
        for v in cl:
            print(v)
    print("Check count is: ", checkCount)
    # В этой структуре список категорий данных, в каждой категории список словарей, в каждом словаре 
    # ключи: max_value, min_value, paramName, values = []
    general_data_structure = GetDataStructure(categoriesList=categoriesList, 
                                                 dateTimeList=dateTimeList,
                                                 selectedResult=selectedResult) # отправляем на график
    
    return general_data_structure
    

def TS(ST):
    time = ST.pop()
    traces = []
    for ic, cat in enumerate(ST):
        for ip, param in enumerate(cat):
            traces.append({'y':param['values'], 'x':time, 'name':param['paramName'], 'yaxis':'y'+str(ic+1)})
    layout = {'title': 'Архивные данные'}
    layout['xaxis'] = dict(autorange=True,rangeslider=dict(autorange=True))
    startDom = 0
    stepDom = 1/len(ST)
    for i in range(len(ST)):
        layout['yaxis'+str(i+1)] = {'title': 'Category №'+str(i+1), "domain":[startDom, startDom+stepDom], "autorange":True} 
        startDom+=stepDom
    layout['height'] = 800
    graphJSON = pio.to_json({'data': traces, 'layout': layout})
    return graphJSON  


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():  
    global selectedTable
    formST = SelectTableForm()
    formST.tableSelector.choices = archives_gen
    formDP = SelectDateParamForm()
    if request.method == "POST":
        if len(formDP.Parameters.data) == 0:
            selectedTable = formST.tableSelector.data
        if selectedTable is not None:
            tableParam = GetParametersFromTable(cursor, selectedTable)
            formDP.Parameters.choices = tableParam
        if len(formDP.Parameters.data) == 0:
            return render_template('index.html', formST=formST, formDP=formDP)
        else:
            flash('Выбраны параметры: {} таблицы: {} в интервале времени от {} до {}'.format(
            formDP.Parameters.data, selectedTable, formDP.dateStart.data, formDP.dateEnd.data))
            # Вызов метода для графика:
            DS=GetStructure(selectedParamsList=formDP.Parameters.data, 
            table=selectedTable, 
            dataStart=formDP.dateStart.data, 
            dataEnd=formDP.dateEnd.data)
            graph = TS(DS)
            return render_template('index.html', formST=formST, formDP=formDP, chart=graph)
    return render_template("index.html", formST=formST, formDP=None)
