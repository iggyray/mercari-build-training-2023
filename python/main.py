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

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item, name: {name}, category: {category}")

    # hash image
    imageContent = await image.read()
    hashedImage = hashlib.sha256(imageContent).hexdigest()
    hashedImageName = hashedImage + os.path.splitext(image.filename)[1]

    # update items.json file
    newItem = {
        'name': name,
        'category': category,
        'image_filename': hashedImageName
    }

    with open("items.json", 'r') as itemsFile:
        allItems = json.load(itemsFile)
        if not "items" in allItems:
            raise HTTPException(status_code=502, detail="items.json file is corrupted")
        itemsFile.close()

    allItems["items"].append(newItem) 

    with open("items.json", 'w') as itemsFile:
        json.dump(allItems, itemsFile)

    return {"message": f"item received with name: {name}, category: {category}, image: {hashedImageName}"}

@app.get("/items")
def get_item():
    with open('items.json') as f:
        items = json.load(f)
    return items

@app.get("/items/{item_id}")
def get_target_item(item_id: int):
    with open('items.json') as f:
        allItems = json.load(f)
    
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