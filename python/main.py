import os
import logging
import pathlib
import json
import hashlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

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

def getItems():
    with open(fileName, 'r') as itemsFile:
        try:
            file = json.load(itemsFile)
            if "items" in file:
                allItems = file
            else:
                allItems = { 'items': [] }
        except:
            allItems = { 'items': [] }
    return allItems

async def hashImage(image: UploadFile = File(...)):
    imageContent = await image.read()
    hashedImage = hashlib.sha256(imageContent).hexdigest()
    return hashedImage + os.path.splitext(image.filename)[1]

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item, name: {name}, category: {category}")
    
    hashedImageName = await hashImage(image)
    newItem = {
        'name': name,
        'category': category,
        'image_filename': hashedImageName
    }
    allItems = getItems()
    allItems["items"].append(newItem)

    with open(fileName, 'w') as itemsFile:
        json.dump(allItems, itemsFile)

    return {"message": f"item received with name: {name}, category: {category}, image: {hashedImageName}"}

@app.get("/items")
def get_items_reponse():
    allItems = getItems()
    return allItems

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