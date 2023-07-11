from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
import random

from typing import Annotated

import hashlib
import json

import sqlite3 as sql
import datetime

import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px

with open('static/categories.json') as file:
    data = json.load(file)
    
# Creamos la App y le montamos el directorio static de recursos
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")
templates = Jinja2Templates(directory="templates")

# Establecemos conexión con el motor de BBDD
connection = sql.connect("validation.db", check_same_thread=False)
cur = connection.cursor()
cur.execute("pragma foreign_keys=ON")

# CORS Error
# https://stackoverflow.com/questions/65635346/how-can-i-enable-cors-in-fastapi
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

########## USUARIOS VALIDADORES ##########
# Acceder a la raíz es acceder a la página de login
@app.get("/", response_class=HTMLResponse)
async def login(request : Request):
    return templates.TemplateResponse("login.html", {"request": request})  

# Devuelve el nombre de fichero de una imagen pendiente de validar por un usuario
def getNextImage(username):
    statement = "SELECT file_name from images where file_name not in (select file_name from validation where username=\""+username+"\")"
    images = []
    for item in cur.execute(statement):
        images.append(item[0])
    try:
        img = images[random.randint(0, len(images)-1)]
    except:
        img = None
    return img

# Funciones que devuelven el número de imágenes validadas/ignoradas/total por un usuario
def getValidated(username):
    statement = "SELECT count(*) from images where file_name in (select file_name from validation where username=\""+username+"\" \
    and ignored=0)"
    statement = cur.execute(statement)
    statement = statement.fetchone()
    return statement[0]

def getIgnored(username):
    statement = "SELECT count(*) from images where file_name in (select file_name from validation where username=\""+username+"\" \
    and ignored=1)"
    statement = cur.execute(statement)
    statement = statement.fetchone()
    return statement[0]

def getTotal():
    statement = "SELECT count(*) from images"
    statement = cur.execute(statement)
    statement = statement.fetchone()
    return statement[0]
  
# Cuando un usuario se loggea
@app.post("/main")
async def login(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]):
    # Se obtiene el hash de su contraseña
    passwordHash = hashlib.md5(password.encode("utf-8"))
    statement = "select * from users where username='" + username + "'"
    statement = cur.execute(statement)
    result = statement.fetchone()
    
    # Se compara el hash de la contraseña proporcionada con el de la almacenada, si no coinciden
    # o el usuario no está registrado, se devuelve a la página de login
    if result is None or result[1] != passwordHash.hexdigest():
        return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Not existing user / Incorrect password"})
    if result[1] == passwordHash.hexdigest():
        # Validador
        if result[2]==1 and result[3]==0:
            image = getNextImage(username)
            if image is not None:
                return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data,\
                                                    "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                    "ignored": str(getIgnored(username))+"/"+str(getTotal())})
            # Si no le quedan imágenes que validar no inicia sesión y se le informa
            else:
                return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
        # Manager
        if result[2]==1 and result[3]==1:
            return RedirectResponse(app.url_path_for('manager')+"?adminUsername="+username)
        # Administrator
        if result[2]==1 and result[3]==2:
            return RedirectResponse(app.url_path_for('admin')+"?username="+username)
        # Usuario deshabilitado
        if result[2]==0:
            return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Your user has been disabled"})

# Devuelve la lista de actividades asociadas a una categoría
@app.post("/getCategories")
def getCategories(category : str):
    category = category.replace("%20", " ")
    return {"list": list(data[category])}

# Función para introducir una nueva validación (conjunto de etiquetas)
def insertValidation(validations, imgUrl, username):
    for i, (lowDetail, highDetail) in enumerate(validations):
        if (lowDetail!="Low Detail"):
            # print(lowDetail)
            # print(highDetail)
            if (highDetail=="High Detail"): 
                highDetail=""
            sentence = "insert into validation (file_name, level1, level2, username, priority, timestamp, ignored) values (\""\
            +imgUrl+"\",\""+lowDetail+"\",\""+highDetail+"\",\""+username+"\","+str(i+1)+", \""+str(datetime.datetime.now())+"\","+str(0)+")"
            sentence = cur.execute(sentence)
            connection.commit()
            

# Introducción de validación por parte de un usuario
@app.post("/submit", response_class=HTMLResponse)
def submit(request: Request, imgUrl: Annotated[str, Form()], username: Annotated[str, Form()], 
           combo11: Annotated[str, Form()], combo12: Annotated[str, Form()] = "High Detail", 
           combo21: Annotated[str, Form()] = "Low Detail", combo22: Annotated[str, Form()] = "High Detail", combo31: Annotated[str, Form()] = "Low Detail", combo32: Annotated[str, Form()] = "High Detail",
           combo41: Annotated[str, Form()] = "Low Detail", combo42: Annotated[str, Form()] = "High Detail"):
    # Solo es válida si se introduce al menos una categoría
    if (combo11!="Low Detail"):
        validations = [(combo11, combo12),(combo21, combo22), (combo31, combo32), (combo41, combo42)]
        insertValidation(validations, imgUrl, username)
        image = getNextImage(username)
        if image is not None:
            return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data,\
                                                      "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                      "ignored": str(getIgnored(username))+"/"+str(getTotal())})
        # Si no quedan más imágenes para ese usuario se le expulsa
        else:
            return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
    else:
        return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": imgUrl, "highLevel": data,\
                                                    "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                    "ignored": str(getIgnored(username))+"/"+str(getTotal())})


# Función para indicar que el usuario ignora la imagen
def ignoreImage(imgUrl, username):
    sentence = "insert into validation (file_name, username, timestamp, ignored) values (\""\
        +imgUrl+"\",\""+username+"\", \""+str(datetime.datetime.now())+"\","+str(1)+")"
    sentence = cur.execute(sentence)
    connection.commit()
    
# Usuario ignora la imagen (no introduce validación)
@app.post("/ignore", response_class=HTMLResponse)
def ignore(request: Request, imgUrl: Annotated[str, Form()], username: Annotated[str, Form()]):
    ignoreImage(imgUrl, username)
    image = getNextImage(username)
    if image is not None:
        return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data,\
                                                      "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                      "ignored": str(getIgnored(username))+"/"+str(getTotal())})
    else:
        # Si no quedan más imágenes para ese usuario se le expulsa
        return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})   


########## USUARIOS MANAGERS ##########
# Acceso de un usuario manager, lista las estadísticas que se pueden activar y desactivar
@app.post("/manager", response_class=HTMLResponse)
def manager(request : Request, adminUsername : str):
    select = "select * from statistics"
    statistics = []
    for row in enumerate(cur.execute(select)):
        row = row[1]
        style = "danger"
        status = "Not Visible"
        changeColor = "success"
        if row[1]==1:
            style = "success"
            status = "Visible"
            changeColor = "danger"
        statistics.append({"style":style, "name": row[0], "status": status, "changeColor": changeColor})
    return templates.TemplateResponse("manager.html", {"request" : request, "statistics" : statistics, "adminUsername":adminUsername})

# Cambia visibilidad de la estadística.
# Si por concurrencia de usuarios un manager2 ha modificado la visibilidad y manager1 aún no había visto el cambio, el cambio de manager2
# se aplicará a la vista de manager1 cuando este cambie la visibilidad también, aunque realmente su accion no haya tenido efecto
@app.post("/changeVisibility")
def changeVisibility(request: Request, selection : Annotated[str, Form()], adminUsername : Annotated[str, Form()], oldStatus : Annotated[str, Form()]):
    visibility = (int(oldStatus == "Visible")+1)%2
    select = "update statistics set active="+str(visibility)+" where name=\""+selection+"\""
    cur.execute(select)
    connection.commit()
    return RedirectResponse(app.url_path_for('manager')+"?adminUsername="+adminUsername)

# Lista los usuarios Validadores
@app.post("/users", response_class= HTMLResponse)
def getUsers(request : Request, adminUsername : Annotated[str, Form()]):
    select = "select * from users where admin=0"
    users = []
    for user in cur.execute(select):
        users.append({"name":user[0], "active":user[2]})
    return templates.TemplateResponse("users.html", {"request":request, "users":users, "adminUsername": adminUsername})
    
# Activa o desactiva un usuario
# La concurrencia se aborda de la misma forma que para el cambio de visibilidad de las estadísticas
@app.post("/changeUserActive")
def changeVisibility(request: Request, selection : Annotated[str, Form()], adminUsername : Annotated[str, Form()], oldStatus : Annotated[str, Form()]):
    visibility = (int(oldStatus)+1)%2
    select = "update users set active="+str(visibility)+" where username=\""+selection+"\""
    cur.execute(select)
    connection.commit()
    return RedirectResponse(app.url_path_for('getUsers')+"?adminUsername="+adminUsername)

# Método para consultar si existe un usuario, se usa antes de crear un nuevo Validador o manager
@app.post("/existsUser")
def existsUser(request: Request, username : str):
    return {"result":(cur.execute("select * from users where username='{username}'".format(username=username)).fetchone() is not None)}

# Función para crear validadores y usuarios (se reutiliza)
def createUser(username, password, type):
    passHash = hashlib.md5(password.encode("utf-8"))
    statement = "insert into users (username, password, active, admin) values ('{username}', '{passHash}', 1, {type})".format(
        username=username, passHash=passHash, type=type
    )
    cur.execute(statement)
    connection.commit()

# Registra un nuevo validador
@app.post("/register")
def register(request: Request, username : Annotated[str, Form()], password : Annotated[str, Form()]):
    createUser(username, password, 0)
    return RedirectResponse(request.url_for('getUsers'))

# Cambia la contraseña de un usuario
@app.post("/changePassword")
def changePassword(request: Request, usernameChange : Annotated[str, Form()], passwordChange : Annotated[str, Form()]):
    passHash = hashlib.md5(passwordChange.encode("utf-8"))
    statement = "update users set password='{passHash}' where username='{username}'".format(passHash=passHash.hexdigest()   , username=usernameChange)
    cur.execute(statement)
    connection.commit()
    return RedirectResponse(request.url_for('getUsers'))
    
    
########## USUARIOS ADMIN ##########
# Acceso a panel de gestión de Managers y Mínimo
@app.post("/admin")
def admin(request : Request, username:str):
    minimumConsensus = cur.execute("select consensus from users where admin=2").fetchone()[0]
    select = "select * from users where admin=1"
    users = []
    for user in cur.execute(select):
        users.append({"name":user[0], "active":user[2]})
    return templates.TemplateResponse("admin.html", {"request":request, "users":users, "username":username, "minimumConsensus":minimumConsensus})
    
# Registra nuevo manager
@app.post("/registerManager")
def registerManager(request: Request, username : Annotated[str, Form()], password : Annotated[str, Form()], adminUsername:Annotated[str, Form()]):
    createUser(username, password, 1)
    return RedirectResponse(app.url_path_for('admin')+"?username="+adminUsername)

# Actualiza el valor del mínimo consenso
@app.post("/saveMinimum")
def saveMinimum(request: Request, minimum : Annotated[str, Form()], username:Annotated[str, Form()]):
    print(minimum)
    cur.execute("update users set consensus="+minimum+" where admin=2")
    connection.commit()
    return RedirectResponse(app.url_path_for('admin')+"?username="+username)
    
########## ACCESO ESTADÍSTICAS ##########
# Lista estadísticas visibles
@app.get("/statistics", response_class=HTMLResponse)
def statistics(request : Request):
    select = "select * from statistics where active=1"
    statistics = []
    for row in enumerate(cur.execute(select)):
        row = row[1]
        style = "success"
        status = "Disabled"
        if row[1]==1:
            style = "danger"
            status = "Enabled"
        statistics.append({"style":style, "name": row[0], "status": status})
    
    return templates.TemplateResponse("statistics.html", {"request": request, "statistics": statistics})
    
# Carga una estadística concreta
@app.post("/statistic")
def statistic(request : Request, selection : Annotated[str, Form()]):
    if selection=="General Accuracy":
        figs = generateAllLevelsAccuracyTables()
        return templates.TemplateResponse("generalAccuracy.html",{"request":request, "name":selection, "figs":figs})
    if selection=="Accuracy per Model":
        figs = generateAllLevelsModelAccuracyTables()
        return templates.TemplateResponse("accuracy.html",{"request":request, "name":selection, "figs": figs})
    if selection=="User Progress":
        progresses = getUsersProgresses()
        return templates.TemplateResponse("progress.html",{"request":request, "name":selection, "progresses":progresses})

# Porcentajes de progreso de cada usuario
def getUsersProgresses():
    users = []
    total = cur.execute("select count(*) from images").fetchone()[0]
    usersValues = {}
    for item in cur.execute("select username from users where admin=0"):
        users.append(item[0])
    for user in users:
        validated = getValidated(user)
        ignored = getIgnored(user)
        usersValues[user] = [validated/total*100, ignored/total*100]
    return usersValues
        
# Genera las tablas de accuracy para todos los niveles en general o para un modelo en concreto
def generateAllLevelsAccuracyTables(model: str=""):
    i = 1
    figs = []
    fig = generateAccuracyBarChart(str(i), model)
    while fig is not None:
        figs.append(fig)
        i+=1
        fig = generateAccuracyBarChart(str(i), model)
    return figs

# Genera las tabls de accuracy para todos los niveles y para todos los modelos
def generateAllLevelsModelAccuracyTables():
    models = "select distinct model from modelOutput"
    modelsList = []
    figs = {}
    for item in cur.execute(models):
        modelsList.append(item[0])
    for model in modelsList: 
        figsModel = generateAllLevelsAccuracyTables(model=model)
        figs[model] = figsModel
    return figs
    
# Exporta las estadísticas a un fichero Excel
@app.post("/getFileStatistic")
def getStatisticFile(request: Request, name: Annotated[str, Form()], option:Annotated[str, Form()] = ""):
    path = "static/exports/"
    file_name = name
    if (option!=""):
        file_name += "_"+option
    file_name += ".xlsx"
    path += file_name
    isModel = option!=""      
    with pd.ExcelWriter(path) as writer:
        i=1
        if isModel:
            df = generateDataFrameV2(str(i), option)
        else:
            df = generateDataFrameV2(str(i))
        while df is not None:
            df.to_excel(writer, sheet_name="Level "+str(i))
            i+=1
            if isModel:
                df = generateDataFrameV2(str(i), option)
            else:
                df = generateDataFrameV2(str(i))
                
    return FileResponse(path, filename=file_name)

# Genera el dataframe de predicciones/aciertos
def generateDataFrameV2(level, model:str=""):
    images = []
    classCounts = {}
    classCoincidences = {}
    minimumConsent = cur.execute("select consensus from users where admin=2").fetchone()[0]
    for img in cur.execute("select * from images"):
        images.append(img[0])
    for img in images:
        usersLabels = {}
        selectUsersLabels = "select level{level} from validation where file_name='{img}' and ignored==0".format(level= level,img=img)
        # Nos guardamos todas las etiquetas de todos los usuarios para una imagen
        try:
            for item in cur.execute(selectUsersLabels):
                if item[0] in usersLabels.keys():
                    usersLabels[item[0]] += 1
                else:
                    usersLabels[item[0]] = 1
            if len(usersLabels.keys())>0:
                majorLabel = max(usersLabels, key=usersLabels.get)
                majorLabelCount = max(usersLabels.values())
                usersLabels.pop(majorLabel)
                consent = True
                if (len(usersLabels)>0):
                    secondMajorLabelCount = max(usersLabels.values())
                    # La etiqueta mayoritaria debe ser única, es decir, no puede haber más de una etiqueta con la misma cantidad
                    # de apariciones, si no, no se considera válida
                    consent = majorLabelCount>secondMajorLabelCount
                
                # Habrá consenso cuando la etiqueta mayoritaria, además de ser única, sea mayor que el porcentaje mínimo esperado
                consent = consent and (float(majorLabelCount)/(len(usersLabels)+1)*100)>=minimumConsent
                if consent:
                    # Si hay consenso entre humanos, se calcula la cantidad de aciertos de uno (o todos) los modelos
                    modelLabels = []
                    selectModelLabels = "select level{level} from modelOutput where file_name='{img}'".format(level=level, img=img)
                    if model!="":
                        selectModelLabels += " and model='{model}'".format(model=model)
                    try:
                        for item in cur.execute(selectModelLabels):
                            modelLabels.append(item[0])                        
                        coincidences = modelLabels.count(majorLabel)
                        if majorLabel in classCounts.keys():
                            classCounts[majorLabel] += len(modelLabels)
                        else:
                            classCounts[majorLabel] = len(modelLabels)
                        if majorLabel in classCoincidences.keys():
                            classCoincidences[majorLabel] += coincidences
                        else:
                            classCoincidences[majorLabel] = coincidences        
                    except: 
                        return None
        except:
            return None
    countsDF = pd.DataFrame(zip(classCounts.keys(), classCounts.values()), columns=["Category", "Labels"])
    coincidencesDF = pd.DataFrame(zip(classCoincidences.keys(), classCoincidences.values()), columns=["Category", "True Positives"])
    finalDF = countsDF.merge(coincidencesDF, on="Category", how="left").fillna(0)   
    return finalDF

# Genera el gráfico en HTML para un nivel en general o para un modelo
def generateAccuracyBarChart(level, model : str=""):
    df = generateDataFrameV2(level, model)
    if df is None:
        return None
    else:
        # print(df)
        fig = px.histogram(df, x="Category", y=["Labels", "True Positives"], 
                            title="Level "+level, barmode="group")
        fig = fig.update_layout(yaxis_title="Number of labels", showlegend=True) 
        fig.update_xaxes(tickangle=40)
        return plotly.io.to_html(fig, full_html=False)  