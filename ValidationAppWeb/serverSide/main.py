from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import sqlite3 as sql
import datetime
import hashlib

app = FastAPI()
connection = sql.connect("validation.db")
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


@app.get("/getImage")
async def getImage(username):
    cur = connection.cursor()
    a = {}
    sentence = "SELECT rowid, file_name from images where file_name not in (select file_name from validation where username=\""+username+"\")"
    for i, row in enumerate(cur.execute(sentence)):
        a[row[0]] = row[1]
    return a


@app.get("/insertValidation")
async def insertValidation(file_name, cat_name, act_name, username, priority):
    cur = connection.cursor()

    priority = priority.split('[')[0]
    insert = "Insert into validation (file_name, cat_name, act_name, username, priority, timestamp, ignored) values (\"" + file_name + "\", \"" + cat_name + \
             "\", \"" + act_name + "\", \"" + username + "\"," + priority + ",\"" + str(
        datetime.datetime.now()) + "\", 0)"
    result = cur.execute(insert)
    connection.commit()
    return {"OK"}


@app.get("/ignoreImage")
async def ignoreImage(file_name, username):
    cur = connection.cursor()
    insert = "Insert into validation (file_name, username, priority, timestamp, ignored) values (\""+file_name+"\",\""+username+\
    "\", -1,\""+str(datetime.datetime.now())+"\", 1)"
    result = cur.execute(insert)
    connection.commit()
    return {"OK"}

@app.get("/countValidated")
async def countValidated(username):
    cur = connection.cursor()
    statement = "select count(*) from images where file_name in (select file_name from validation where ignored=0 and username=\""+username+"\")"
    statement = cur.execute(statement)
    return {statement.fetchone()[0]}
@app.get("/countTotal")
async def countValidated():
    cur = connection.cursor()
    statement = "select count(*) from images"
    statement = cur.execute(statement)
    return {statement.fetchone()[0]}
@app.get("/countIgnored")
async def countIgnored(username):
    cur = connection.cursor()
    statement = "select count(*) from images where file_name in (select file_name from validation where ignored=1 and username=\""+username+"\")"
    statement = cur.execute(statement)
    return {statement.fetchone()[0]}


@app.get("/login")
async def login(username, password):
    cur = connection.cursor()
    # passwordHash = hashlib.md5(password.encode("utf-8"))
    statement = "select * from users where username='" + username + "'"
    statement = cur.execute(statement)
    result = statement.fetchone()
    if result is None:
        return {"Not Registered"}
    else:
        if result[1] == password:
            return {"OK"}
        else:
            return {"Incorrect password"}


@app.get("/register")
async def register(username, password):
    cur = connection.cursor()
    # passwordHash = hashlib.md5(password.encode("utf-8"))
    statement = "insert into users (username, password) values ('" + username + "', '" +password+"')"
    try:
        statement = cur.execute(statement)
    except:
        return {"Already Existing"}
    connection.commit()
    return {"Created"}

@app.get("/getPassword")
async def register(username):
    cur = connection.cursor()
    statement = "select password from users where username=\""+username+"\""
    statement = cur.execute(statement)
    return {statement.fetchone()[0]}

