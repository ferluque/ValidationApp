from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from typing import Annotated

import hashlib
import json

import sqlite3 as sql
import datetime

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
    if result is None:
        return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Not existing user"})
    else:
        if username=="admin":
            return RedirectResponse(request.url_for('admin'))
        else:
            if result[1] == passwordHash.hexdigest():
                image = getNextImage(username)
                if image is not None:
                    return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data})
                else:
                    return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
            else:
                return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Incorrect password"})

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
            sentence = "insert into validation (file_name, cat_name, act_name, username, priority, timestamp, ignored) values (\""\
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
            return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data})
        else:
            return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
    else:
        # return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "Not existing user"})
            return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": imgUrl, "highLevel": data})


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
        return templates.TemplateResponse("mainpage.html", {"request": request, "username" : username, "imgUrl": image, "highLevel": data})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "loginInfo" : "No more images"})
    
@app.get("/statistics", response_class=HTMLResponse)
def statistics(request : Request):
    select = "select * from statistics"
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
def admin(request : Request):
    select = "select * from statistics"
    statistics = []
    for row in enumerate(cur.execute(select)):
        row = row[1]
        style = "danger"
        status = "Disabled"
        changeColor = "success"
        if row[1]==1:
            style = "success"
            status = "Enabled"
            changeColor = "danger"
        statistics.append({"style":style, "name": row[0], "status": status, "changeColor": changeColor})
    return templates.TemplateResponse("admin.html", {"request" : request, "statistics" : statistics})

@app.post("/changeVisibility")
def changeVisibility(request: Request, selection : Annotated[str, Form()]):
    select = "select active from statistics where name=\""+selection+"\""
    select = cur.execute(select)
    visibility = (select.fetchone()[0]+1)%2
    print(visibility)
    select = "update statistics set active="+str(visibility)+" where name=\""+selection+"\""
    cur.execute(select)
    connection.commit()
    return RedirectResponse(request.url_for('admin'))

@app.post("/statistic")
def statistic(request : Request, selection : Annotated[str, Form()]):
    print(selection)
    return templates.TemplateResponse("singleStatistic.html",{"request":request, "name":selection})