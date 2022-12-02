import pymysql.cursors

def Merge_Date_Time(date, time):
    return date + "T" + time

def Connect2MDB():
    connect = None
    try:
        connect = pymysql.connect(
                            host='localhost',
                            user='root',
                            password='pesk-2020',
                            database='data_core_db',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
        print("Connection is OK")
    except:
        print("Connection is BAD")
    return connect

def CloseConnect(connect):
    try:
        connect.close()
        print("Connection closed")
    except:
        print("Connection is not close")

def CloseCursor(cursor):
    cursor.close()

def GetCursor(connect):
    return connect.cursor()

def QueryDataGeneration(tablename, startDate, endDate, parameter):
    query = f"SELECT date, time, {parameter} FROM `{tablename}` WHERE date BETWEEN '{startDate}' AND '{endDate}'"
    return query

def GetAllDataGeneration(tablename, startDate, endDate):
    query = f"SELECT * FROM `{tablename}` WHERE date BETWEEN '{startDate}' AND '{endDate}'"
    return query

def ExecuteQuery(cursor, query):
    try:
        cursor.execute(query)
        print("Query is executed")
    except:
        print("Query is not executed")


def GetResult(cursor):
    return cursor.fetchall()
    
def GetArchivesSec(cursor):
    archives = list()
    cursor.execute("""
    SELECT table_name
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE table_type = 'base table' and table_schema = 'data_core_db'and table_name LIKE 'archives__sec%'
    """)
    result = GetResult(cursor=cursor)
    for i in result:
        archives.append(i['table_name'])
    return archives

def DevideArchivesByFe(archives):
    archives_fe = list()
    for i in archives:
        if i.find("fe") != -1:
            print(i, i.find("__fe"))
            archives_fe.append(i)
    for i in archives:
        if i.find("__fe") != -1:
            archives.remove(i)
    archives_fe.sort()
    archives.sort()
    archives.pop(4)
    return archives_fe

def GetClearShihtaData(cursor, tablename, startDate, endDate, parameter):
    query = f"""
        SELECT date, time, {parameter} FROM `{tablename}` 
        WHERE date BETWEEN '{startDate}' AND '{endDate}' AND 
        shihta_status != 'Open Err'
    """
    ExecuteQuery(cursor=cursor, query=query)
    result = GetResult(cursor)
    return result

def GetParametersFromTable(cursor, tablename):
    cursor.execute(f"""
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_name = '{tablename}'
    """)
    result = GetResult(cursor=cursor)
    paramArr = list()
    result = result[3:]
    for i in range(len(result)):
        if result[i]['COLUMN_NAME'].find("status") == -1 and result[i]['COLUMN_NAME'].find("apc_on") == -1:
            paramArr.append(result[i]['COLUMN_NAME'])
    return paramArr

def GetShihta(cursor, tablename, dataStart, dataEnd):
    shihtaAllParamL = GetParametersFromTable(cursor=cursor, tablename=tablename)
    shihtaAllParamLStr = ", ".join(shihtaAllParamL)
    shihtaDataStruct = dict()
    for i in shihtaAllParamL:
        shihtaDataStruct[i] = list()
    shihtaDataStruct['dateTime'] = list()
    queryRes = GetClearShihtaData(cursor, tablename, dataStart, dataEnd, shihtaAllParamLStr)
    for q in queryRes:
        for key in q:
            if key == "date" or key == "time":
                pass
            else:
                shihtaDataStruct[key].append(q[key])

    for q in queryRes:
        shihtaDataStruct['dateTime'].append(Merge_Date_Time(q['date'], q['time']))
    return shihtaDataStruct

archives = ["archives__sec1", 
                "archives__sec2", 
                "archives__sec3", 
                "archives__sec4", 
                "archives__sec5", 
                "archives__sec6",
                "archives__sec7", 
                "archives__sec8", 
                "archives__sec9",
                "archives__sec10",
                "archives__sec11",
                "archives__sec12"]
archives_fe = ["archives__sec1__fe", 
                   "archives__sec2__fe", 
                   "archives__sec3__fe", 
                   "archives__sec4__fe",
                   "archives__sec5__fe",
                   "archives__sec6__fe",
                   "archives__sec7__fe",
                   "archives__sec8__fe", 
                   "archives__sec9__fe",
                   "archives__sec10__fe",
                   "archives__sec11__fe",
                   "archives__sec12__fe"]
archives_gen = archives + archives_fe

def MakeCategories(sorted_ParameterMaxValue_pare):
    """Разбиваем пары имя параметра максимум на категории."""
    category = list()
    categoriesList = list()
    for i in range(1, len(sorted_ParameterMaxValue_pare)+1):
        category.append(sorted_ParameterMaxValue_pare[i-1])
        try:
            if sorted_ParameterMaxValue_pare[i][1]/sorted_ParameterMaxValue_pare[i-1][1] > 2:
                categoriesList.append(category)
                category = list()
        except ZeroDivisionError:
            print("Null values in: ", sorted_ParameterMaxValue_pare[i-1])
        except IndexError:
            print("Index error by index: ", i)
    categoriesList.append(category)
    return categoriesList        

def GetMaxMinValuesSelectedParams(cursor, dateStart, dateEnd, tableName, selParamsList):
    """Возвращает два списка: максимумы и иминимумы выбранных параметров"""
    max_values = list()
    min_values = list()
    tempListParam = list()
    for i in range(len(selParamsList)):
        query = QueryDataGeneration(tablename=tableName, startDate=dateStart, endDate=dateEnd, parameter=selParamsList[i])
        ExecuteQuery(cursor=cursor, query=query)
        result = GetResult(cursor=cursor)
        for record in result:
            if type(record[selParamsList[i]]) in (float, int):
                tempListParam.append(record[selParamsList[i]])
        if len(tempListParam):
            max_values.append(max(tempListParam))
            min_values.append(min(tempListParam))
        tempListParam.clear()
    return max_values, min_values

def GetSortedParamsMaxPares(selectedResult, selectedParamsList, max_values):
    """Сортировка параметров в порядке возрастания"""
    onlyNumericParams = list()
    for r,p in zip(selectedResult,selectedParamsList):
        if type(r[p]) in (float, int):
            onlyNumericParams.append(p)
    par_max_pares = list(zip(onlyNumericParams, max_values))
    sorted_par_max_pares = sorted(par_max_pares, key=lambda item:item[1])
    return sorted_par_max_pares

def GetValuesListForParameter(selectedResult, param):
    valuesList = list()
    for i in selectedResult:
        valuesList.append(i[param])
    return valuesList


def GetDataStructure(categoriesList, dateTimeList, selectedResult):
    for cl in categoriesList:
        for i, v in enumerate(cl):
            valuesList = GetValuesListForParameter(selectedResult, v[0])
            cl[i] = dict(paramName=v[0], max_value = v[1], min_value=min(valuesList), values=valuesList)
    categoriesList.append(dateTimeList)
    return categoriesList

def GetDateTimeList(selectedResult):
    dateTimeList = list()
    for record in selectedResult:
        dateTimeList.append(Merge_Date_Time(record["date"],record["time"]))
    return dateTimeList


if __name__ == "__main__":
    connect = Connect2MDB()
    cursor = GetCursor(connect)
    # Инициализация данных с формы
    dataStart = "2022-06-28" # for without fe: 2022-04-23
    dataEnd = "2022-06-29" # for without fe: 2022-04-24
    table = archives[0] # for without fe: archives_gen[0]
    allParam = GetParametersFromTable(cursor=cursor, tablename=table) # выбранные параметры
    selectedParamsList = ["pribor_fe", allParam[5], allParam[6], allParam[7]]
    selectedParamsStr = ", ".join(selectedParamsList)

    print("ALL PARAM COUNT: ", len(allParam))

    # Список максимальных и минимальных значений
    max_values, min_values = GetMaxMinValuesSelectedParams(cursor=cursor,
                                                           dateStart=dataStart, 
                                                           dateEnd=dataEnd,
                                                           tableName=table,
                                                           selParamsList=selectedParamsList)
   
    # Запрос только на получение данных выбранных категорий 
    selectedQuery = QueryDataGeneration(tablename=table, 
                                        startDate=dataStart, 
                                        endDate=dataStart, 
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
                                                 dateTimeList=dateTimeList) # отправляем на график
    
    
    # Вывод структуры
    for j, cl in enumerate(general_data_structure):
        print("Category num:",j+1)
        print(cl)
        # for i, v in enumerate(cl):
        #     if type(v) is dict:
        #         for key in v:
        #             print(key)
        #             print(v[key])
        #     else:
        #         print(v)
        CloseCursor(cursor)
        CloseConnect(connect)

