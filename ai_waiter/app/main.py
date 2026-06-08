from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import glob
import os
import shutil

from app.database import init_db, SessionLocal, Order, Menu
from app.ml import classify_intent, recommend_dishes
from app.etl import run_etl

app = FastAPI(title="AI Waiter")

class OrderRequest(BaseModel):
    text: str

class RecommendationRequest(BaseModel):
    preference: str

class StatusUpdate(BaseModel):
    status: str

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Waiter API!",
        "docs": "Go to /docs to see the interactive API documentation and test the endpoints."
    }

@app.on_event("startup")
def startup_event():
    init_db()
    run_etl()

@app.post("/order")
def create_order(request: OrderRequest, db: Session = Depends(get_db)):
    intent = classify_intent(request.text)
    
    # Only actually create an order if intent is 'order'
    status = "pending" if intent == "order" else "question"
    
    new_order = Order(
        customer_intent=intent,
        order_text=request.text,
        status=status
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return {
        "message": f"Received. Intent classified as: {intent}",
        "order_id": new_order.id,
        "intent": intent,
        "status": status
    }

@app.post("/recommend")
def get_recommendations(request: RecommendationRequest):
    recs = recommend_dishes(request.preference)
    return {"recommendations": recs}

from app.llm import generate_chat_response

@app.post("/chat")
def chat_endpoint(request: OrderRequest, db: Session = Depends(get_db)):
    # 1. Classify intent using Scikit-Learn (thesis requirement)
    intent = classify_intent(request.text)
    
    # 2. Save order if the intent is 'order'
    if intent == "order":
        new_order = Order(customer_intent=intent, order_text=request.text, status="pending")
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
    # 3. Fetch menu from database
    menu_items = db.query(Menu).all()
    
    # 4. Generate dynamic response using ChatGPT
    bot_reply = generate_chat_response(request.text, intent, menu_items)
    
    return {"response": bot_reply}

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.id.desc()).all()
    return {"orders": orders}

@app.put("/orders/{order_id}")
def update_order_status(order_id: int, request: StatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = request.status
        db.commit()
        return {"message": f"Order {order_id} updated"}
    return {"error": "Order not found"}

@app.get("/menu/pdf")
def list_menu_pdfs():
    pdf_files = glob.glob("data/*.pdf")
    return {"files": [os.path.basename(f) for f in pdf_files]}

@app.get("/menu/pdf/{filename}")
def get_specific_menu_pdf(filename: str):
    file_path = os.path.join("data", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=filename)
    return {"error": "File not found"}

@app.post("/menu/pdf/upload")
def upload_menu_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Ensure data folder exists
    os.makedirs("data", exist_ok=True)
    
    file_path = os.path.join("data", file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        return {"error": f"Failed to save file: {str(e)}"}
    
    # Trigger the ETL for this specific file
    from app.etl import extract_menu_from_pdf, load_data_to_db
    df = extract_menu_from_pdf(file_path)
    if not df.empty:
        menu_type = file.filename.replace(".pdf", "").replace("_", " ").title()
        load_data_to_db(df, menu_type)
        return {"message": f"Successfully uploaded {file.filename} and imported {len(df)} items."}
    else:
        # Delete invalid file
        try:
            os.remove(file_path)
        except:
            pass
        return {"error": "Failed to extract menu items from the PDF."}

@app.delete("/menu/pdf/{filename}")
def delete_specific_menu_pdf(filename: str, db: Session = Depends(get_db)):
    file_path = os.path.join("data", filename)
    if not os.path.exists(file_path):
        return {"error": f"File {filename} not found."}
        
    try:
        os.remove(file_path)
    except Exception as e:
        return {"error": f"Failed to delete file: {str(e)}"}
        
    # Also delete database items matching this menu type
    menu_type = filename.replace(".pdf", "").replace("_", " ").title()
    db.query(Menu).filter(Menu.menu_type == menu_type).delete()
    db.commit()
    return {"message": f"Successfully deleted {filename} and removed its menu items"}

@app.delete("/menu/pdf")
def delete_all_menu_pdfs(db: Session = Depends(get_db)):
    pdf_files = glob.glob("data/*.pdf")
    for file_path in pdf_files:
        try:
            os.remove(file_path)
        except Exception as e:
            return {"error": f"Failed to delete {file_path}: {str(e)}"}
    db.query(Menu).delete()
    db.commit()
    return {"message": "All PDF menus and database items deleted successfully"}

@app.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    menu_items = db.query(Menu).all()
    return {"menu": menu_items}

@app.post("/menu")
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    new_item = Menu(
        name=item.name,
        description=item.description,
        price=item.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"message": "Menu item created", "id": new_item.id}

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Menu).filter(Menu.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return {"message": "Menu item deleted"}
    return {"error": "Item not found"}
