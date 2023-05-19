import os
import logging
import pathlib
import json
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

fileName = "items.json"
dataBase = pathlib.Path(__file__).parent.resolve() / "db" / "mercari.sqlite3"

def getDbItems():
    conn = sqlite3.connect(dataBase)
    cursor = conn.cursor()
    getQuery = "SELECT items.id, items.name, category.name, image_filename FROM items INNER JOIN category ON items.category_id = category.id;"
    cursor.execute(getQuery)
    allItems = cursor.fetchall()
    conn.close()
    return allItems

def postDbItem(name: str, category: str, image_name: str):
    conn = sqlite3.connect(dataBase)
    cursor = conn.cursor()
    formattedCategory = category.lower()

    getCategoryQuery = "SELECT id FROM category WHERE name = ?"
    cursor.execute(getCategoryQuery, (formattedCategory,))
    categoryId = cursor.fetchone()
    addItemQuery = "INSERT INTO items (name, category_id, image_filename) VALUES (?, ?, ?)"

    if categoryId:
        values = (name, categoryId[0], image_name)
        cursor.execute(addItemQuery, values)
        conn.commit()
    else:
        addCategoryQuery = "INSERT INTO category (name) VALUES (?)"
        cursor.execute(addCategoryQuery, (formattedCategory,))
        conn.commit()
        cursor.execute(getCategoryQuery, (formattedCategory,))
        newCategoryId = cursor.fetchone()
        values = (name, newCategoryId[0], image_name)
        cursor.execute(addItemQuery, values)
        conn.commit()

    conn.close()
    

def getLatestId():
    conn = sqlite3.connect(dataBase)
    cursor = conn.cursor()
    getLatestQuery = "SELECT id FROM items ORDER BY id DESC LIMIT 1;"
    cursor.execute(getLatestQuery)
    addedId = cursor.fetchone()
    return addedId[0]


def searchForDbItem(keyword: str):
    conn = sqlite3.connect(dataBase)
    cursor = conn.cursor()
    searchQuery = "SELECT items.name, category.name, image_filename FROM items INNER JOIN category ON items.category_id = category.id WHERE items.name LIKE ?"
    cursor.execute(searchQuery, ('%' + keyword + '%',))
    matches = cursor.fetchall()
    conn.close()
    return matches

def formatItemsForReturn(allItems):
    returnItems = { 'items': [] }
    
    for item in allItems:
        returnItem = { 'id': item[0], 'name': item[1], 'category': item[2], 'image_filename': item[3]  }
        returnItems["items"].append(returnItem)
    
    return returnItems

async def hashImage(imageBinary, imageExtension):
    hashedImage = hashlib.sha256(imageBinary).hexdigest()
    return hashedImage + imageExtension

app.mount("/image", StaticFiles(directory="images"), name="image")

async def uploadImage(itemId: int, imageBinary, imageExtension):
    imageFileName = f"{itemId}{imageExtension}"
    imagePath = images / imageFileName
    try: 
        with open(imagePath, "wb") as file:
            file.write(imageBinary)
            file.flush()
    except Exception as e:
        print(f"Error while writing the image file: {e}")

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
async def addItem(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item, name: {name}, category: {category}")

    imageExtension = os.path.splitext(image.filename)[1]
    imageBinary = await image.read()
    hashedImageName = await hashImage(imageBinary, imageExtension)
    postDbItem(name, category, hashedImageName)
    addedId = getLatestId()
    await uploadImage(addedId, imageBinary, imageExtension)

    return {"message": f"item received with name: {name}, category: {category}, image: {hashedImageName}"}

@app.get("/items")
def getAllItems():
    allItems = getDbItems()
    if len(allItems) > 0:
        returnItems = formatItemsForReturn(allItems)
        return returnItems
    else:
        raise HTTPException(status_code=404, detail="Database is empty")

@app.get("/search")
def getSearchedItem(keyword: str):
    matches = searchForDbItem(keyword)
    if len(matches) > 0:
        returnItems = formatItemsForReturn(matches)
        return returnItems
    else:
        raise HTTPException(status_code=404, detail=f"No matches found for: {keyword}")

@app.get("/items/{item_id}")
def get_target_item(item_id: int):
    allItems = getItems()
    
    if item_id >= len(allItems["items"]):
        raise HTTPException(status_code=404, detail="Item Id does not exist")

    target = allItems["items"][item_id]
    
    return target

@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.warning(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)