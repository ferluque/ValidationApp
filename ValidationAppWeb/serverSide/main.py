from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import sqlite3 as sql
import datetime

app = FastAPI()
connection = sql.connect("validation.db")

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
async def getImage():
    cur = connection.cursor()
    a = {}
    for i, row in enumerate(cur.execute("SELECT rowid, file_name from images where file_name not in (select file_name from validation)")):
        a[row[0]] = row[1]
    return a

@app.get("/insertValidation")
async def insertValidation(file_name, cat_name, act_name):
    cur = connection.cursor()

    count_statement = "select count(*) from validation where file_name=\""+file_name+"\""
    count_statement = cur.execute(count_statement)
    if (count_statement.fetchone()[0]<4):
        insert = "Insert into validation (file_name, cat_name, act_name, timestamp) values (\""+ file_name+ "\", \""+ cat_name+ "\", \""+ act_name+ "\", \""+ str(datetime.datetime.now())+"\")"
        result = cur.execute(insert)
        connection.commit()
        return {"OK"}
    else:
        return {"Already_validated"}

@app.get("/countValidated")
async def countValidated():
    cur = connection.cursor()
    statement = "select count(*) from images where file_name in (select file_name from validation)"
    statement = cur.execute(statement)
    return {statement.fetchone()[0]}