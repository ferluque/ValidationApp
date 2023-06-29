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
    
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")

templates = Jinja2Templates(directory="templates")

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

@app.get("/", response_class=HTMLResponse)
async def login(request : Request):
    return templates.TemplateResponse("login.html", {"request": request})
  

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
  
@app.post("/main")
async def login(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]):
    passwordHash = hashlib.md5(password.encode("utf-8"))
    statement = "select * from users where username='" + username + "'"
    statement = cur.execute(statement)
    result = statement.fetchone()
    
# Añadir información a respuestas
    if result is None or result[1] != passwordHash.hexdigest():
        return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Not existing user / Incorrect password"})
    if result[1] == passwordHash.hexdigest():
        # Standard user
        if result[2]==1 and result[3]==0:
            image = getNextImage(username)
            if image is not None:
                return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data,\
                                                    "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                    "ignored": str(getIgnored(username))+"/"+str(getTotal())})
            else:
                return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
        # Manager
        if result[2]==1 and result[3]==1:
            return RedirectResponse(app.url_path_for('admin')+"?adminUsername="+username)
        # Administrator
        if result[2]==1 and result[3]==2:
            return RedirectResponse(app.url_path_for('adminsManagement')+"?username="+username)
        if result[2]==0:
            return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Your user has been disabled"})

@app.post("/getCategories")
def getCategories(category : str):
    category = category.replace("%20", " ")
    return {"list": list(data[category])}

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
            

@app.post("/submit", response_class=HTMLResponse)
def submit(request: Request, imgUrl: Annotated[str, Form()], username: Annotated[str, Form()], 
           combo11: Annotated[str, Form()], combo12: Annotated[str, Form()] = "High Detail", 
           combo21: Annotated[str, Form()] = "Low Detail", combo22: Annotated[str, Form()] = "High Detail", combo31: Annotated[str, Form()] = "Low Detail", combo32: Annotated[str, Form()] = "High Detail",
           combo41: Annotated[str, Form()] = "Low Detail", combo42: Annotated[str, Form()] = "High Detail"):
    if (combo11!="Low Detail"):
        validations = [(combo11, combo12),(combo21, combo22), (combo31, combo32), (combo41, combo42)]
        insertValidation(validations, imgUrl, username)
        image = getNextImage(username)
        if image is not None:
            return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data,\
                                                      "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                      "ignored": str(getIgnored(username))+"/"+str(getTotal())})
        else:
            return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
    else:
        # return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Not existing user"})
            return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": imgUrl, "highLevel": data,\
                                                      "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                      "ignored": str(getIgnored(username))+"/"+str(getTotal())})


def ignoreImage(imgUrl, username):
    sentence = "insert into validation (file_name, username, timestamp, ignored) values (\""\
        +imgUrl+"\",\""+username+"\", \""+str(datetime.datetime.now())+"\","+str(1)+")"
    print(sentence)
    sentence = cur.execute(sentence)
    connection.commit()
    
@app.post("/ignore", response_class=HTMLResponse)
def submit(request: Request, imgUrl: Annotated[str, Form()], username: Annotated[str, Form()]):
    ignoreImage(imgUrl, username)
    image = getNextImage(username)
    if image is not None:
        return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data,\
                                                      "validated" : str(getValidated(username))+"/"+str(getTotal()),\
                                                      "ignored": str(getIgnored(username))+"/"+str(getTotal())})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
  
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
    
@app.post("/admin", response_class=HTMLResponse)
def admin(request : Request, adminUsername : str):
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
    return templates.TemplateResponse("admin.html", {"request" : request, "statistics" : statistics, "adminUsername":adminUsername})

@app.post("/changeVisibility")
def changeVisibility(request: Request, selection : Annotated[str, Form()], adminUsername : Annotated[str, Form()]):
    select = "select active from statistics where name=\""+selection+"\""
    select = cur.execute(select)
    visibility = (select.fetchone()[0]+1)%2
    print(visibility)
    select = "update statistics set active="+str(visibility)+" where name=\""+selection+"\""
    cur.execute(select)
    connection.commit()
    return RedirectResponse(app.url_path_for('admin')+"?adminUsername="+adminUsername)

@app.post("/users", response_class= HTMLResponse)
def getUsers(request : Request, adminUsername : Annotated[str, Form()]):
    select = "select * from users where admin=0"
    users = []
    for user in cur.execute(select):
        users.append({"name":user[0], "active":user[2]})
    return templates.TemplateResponse("users.html", {"request":request, "users":users, "adminUsername": adminUsername})
    
@app.post("/changeUserActive")
def changeVisibility(request: Request, selection : Annotated[str, Form()], adminUsername : Annotated[str, Form()]):
    select = "select active from users where username=\""+selection+"\""
    select = cur.execute(select)
    visibility = (select.fetchone()[0]+1)%2
    select = "update users set active="+str(visibility)+" where username=\""+selection+"\""
    cur.execute(select)
    connection.commit()
    return RedirectResponse(app.url_path_for('getUsers')+"?adminUsername="+adminUsername)

@app.post("/existsUser")
def existsUser(request: Request, username : str):
    return {"result":(cur.execute("select * from users where username='{username}'".format(username=username)).fetchone() is not None)}

@app.post("/register")
def register(request: Request, username : Annotated[str, Form()], password : Annotated[str, Form()]):
    passHash = hashlib.md5(password.encode("utf-8"))
    statement = "insert into users (username, password, active, admin) values (\""+username+"\", \""+passHash.hexdigest()+"\", 1, 0)"
    cur.execute(statement)
    connection.commit()
    return RedirectResponse(request.url_for('getUsers'))

@app.post("/changePassword")
def changePassword(request: Request, usernameChange : Annotated[str, Form()], passwordChange : Annotated[str, Form()]):
    passHash = hashlib.md5(passwordChange.encode("utf-8"))
    statement = "update users set password='{passHash}' where username='{username}'".format(passHash=passHash.hexdigest()   , username=usernameChange)
    cur.execute(statement)
    connection.commit()
    return RedirectResponse(request.url_for('getUsers'))
    
    
@app.post("/statistic")
def statistic(request : Request, selection : Annotated[str, Form()]):
    if selection=="General Accuracy":
        figs = generateAllLevelsAccuracyTables()
        return templates.TemplateResponse("generalAccuracy.html",{"request":request, "name":selection, "figs":figs})
    if selection=="Accuracy per Model":
        figs = generateAllLevelsModelAccuracyTables()
        return templates.TemplateResponse("accuracy.html",{"request":request, "name":selection, "figs": figs})
    if selection=="Accuracy per User":
        figs = generateAllLevelsUserAccuracyTables()
        return templates.TemplateResponse("accuracy.html",{"request":request, "name":selection, "figs":figs})

def generateAllLevelsAccuracyTables(model: str="", user:str=""):
    i = 1
    figs = []
    fig = generateAccuracyBarChart(str(i), model, user)
    while fig is not None:
        figs.append(fig)
        i+=1
        fig = generateAccuracyBarChart(str(i), model, user)
    return figs

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

def generateAllLevelsUserAccuracyTables():
    users = "select distinct username from users where username!='admin' and admin==0"
    figs = {}
    usersList = []
    for item in cur.execute(users):
        usersList.append(item[0])
    for user in usersList:
        figsUser = generateAllLevelsAccuracyTables(user=user)
        figs[user] = figsUser
    return figs
    
@app.post("/getFileStatistic")
def getStatisticFile(request: Request, name: Annotated[str, Form()], option:Annotated[str, Form()]):
    path = "static/exports/"
    file_name = name
    if (option!=""):
        file_name += "_"+option
    file_name += ".xlsx"
    path += file_name
    
    isModel = (cur.execute("select * from modelOutput where model='{model}'".format(model=option)).fetchone() is not None)
    isUser = not isModel
    if not isModel:
        isUser = (cur.execute("select * from users where username='{user}'".format(user=option)).fetchone() is not None)
    
    with pd.ExcelWriter(path) as writer:
        i=1
        if isModel:
            df = generateDataFrame(str(i), option)
        elif isUser:
            df = generateDataFrame(str(i), user=option)
        else:
            df = generateDataFrame(str(i))
        while df is not None:
            df.to_excel(writer, sheet_name="Level "+str(i))
            i+=1
            if isModel:
                df = generateDataFrame(str(i), option)
            elif isUser:
                df = generateDataFrame(str(i), user=option)
            else:
                df = generateDataFrame(str(i))
    return FileResponse(path, filename=file_name)


def generateDataFrame(level, model:str="", user:str=""):
    modelGroups = []
    selectModel = "select modelOutput.level{level}, count(*) from modelOutput, validation where modelOutput.file_name==validation.file_name\
        and validation.ignored==0 group by modelOutput.level{level}".format(level=level)
    if (model!=""):
        selectModel += " and modelOutput.model='{model}'".format(model=model)
    if (user!=""):
        selectModel += " and validation.username='{user}'".format(user=user)
    try:
        for item in cur.execute(selectModel):
            modelGroups.append([item[0], item[1]])
    except:
        modelGroups = None
        
    if modelGroups is not None:
        modelGroupsDF = pd.DataFrame(modelGroups, columns=["Category", "Total matches"])

        usersGroups = []
        selectUsers = "select modelOutput.level{level}, count(*) from modelOutput, validation where modelOutput.file_name==validation.file_name\
            and validation.ignored==0 and validation.level{level}==modelOutput.level{level} group by modelOutput.level{level}".format(level=level)     
        if (model!=""):
            selectUsers += " and modelOutput.model='{model}'".format(model=model)
        if (user!=""):
            selectUsers += " and validation.username='{user}'".format(user=user)
        
        for item in cur.execute(selectUsers):
            usersGroups.append([item[0], item[1]])
        
        usersGroupsDF = pd.DataFrame(usersGroups, columns=["Category", "Coincident matches"])

        finalDF = modelGroupsDF.merge(usersGroupsDF, on="Category", how="left").fillna(0.0)    
        return finalDF
    else:
        return None
        
def generateAccuracyBarChart(level, model : str="", user:str=""):
    df = generateDataFrame(level, model, user)
    if df is None:
        return None
    else:
        fig = px.histogram(df, x="Category", y=["Total matches", "Coincident matches"], 
                            title="Level "+level, barmode="group")
        fig = fig.update_layout(yaxis_title="Number of labels", showlegend=False) 
        return plotly.io.to_html(fig, full_html=False)  

@app.post("/adminsManagement")
def adminsManagement(request : Request, username:str):
    select = "select * from users where admin=1"
    users = []
    for user in cur.execute(select):
        users.append({"name":user[0], "active":user[2]})
    return templates.TemplateResponse("adminsManagement.html", {"request":request, "users":users, "username":username})
    
@app.post("/registerAdmin")
def registerAdmin(request: Request, username : Annotated[str, Form()], password : Annotated[str, Form()], adminUsername:Annotated[str, Form()]):
    passHash = hashlib.md5(password.encode("utf-8"))
    statement = "insert into users (username, password, active, admin) values (\""+username+"\", \""+passHash.hexdigest()+"\", 1, 1)"
    cur.execute(statement)
    connection.commit()
    return RedirectResponse(app.url_path_for('adminsManagement')+"?username="+adminUsername)