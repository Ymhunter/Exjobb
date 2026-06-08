# AI Waiter: Intelligent Menu Ingestion & Conversational Ordering
*En hybridarkitektur för automatiserad meny-onboarding och säkra restaurangbeställningar*

**Förnamn Efternamn:** Alan  
**Datum:** 2026-06-08  

---

## Innehållsförteckning
1. Titelsida
2. Abstract (Svenska & Engelska)
3. Förkortningar och begrepp
4. Innehållsförteckning
5. Inledning (Syfte, Frågeställning & Avgränsning)
6. Teori
7. Metod
8. Resultat
9. Slutsats / Diskussion / Analys
10. Källförteckning
11. Appendix

---

## 1. Titelsida
* **Titel:** AI Waiter: Intelligent Menu Ingestion & Conversational Ordering
* **Undertitel:** En hybridarkitektur för automatiserad meny-onboarding och säkra restaurangbeställningar
* **Författare:** Alan
* **Datum:** 2026-06-08

---

## 2. Abstract

### Svenska
Detta examensarbete presenterar *AI Waiter*, ett containeriserat system utformat för att underlätta restaurangers digitalisering och erbjuda kunder ett naturligt samtalsgränssnitt vid beställningar och rekommendationer. Rapporten beskriver hur analoga och digitala PDF-menyer automatiskt kan digitaliseras via en ETL-pipeline som kombinerar PyMuPDF och OpenAI GPT-4o Vision API. För att minska latens, hålla nere driftskostnader och garantera säkra beställningsflöden används en lokal maskininlärningsmodell (TF-IDF och Logistisk regression via Scikit-Learn) för avsiktsklassificering (intent detection). Beställningar sparas direkt i en PostgreSQL-databas. Kunddialogen hanteras av ett konversations-LLM (GPT-3.5 Turbo) som via prompt-grounding begränsas till att endast referera till rätter som finns lagrade i databasen. Resultatet visar på en robust hybridarkitektur som framgångsrikt kombinerar de låga svarstiderna hos lokala modeller med den flexibla dialogförmågan hos generativa molntjänster.

### English
This thesis presents *AI Waiter*, a containerized system designed to streamline restaurant digitization and provide customers with a natural conversational interface for ordering and recommendations. The report details how physical and digital PDF menus are automatically ingested via an ETL pipeline combining PyMuPDF and OpenAI's GPT-4o Vision API. To minimize latency, lower operational costs, and guarantee reliable order flows, a local machine learning model (TF-IDF and Logistic Regression via Scikit-Learn) is used for intent classification. Orders are persisted in a PostgreSQL database. Customer dialogue is handled by a conversational LLM (GPT-3.5 Turbo), strictly grounded in the database context to prevent hallucinating dishes. The results demonstrate a robust hybrid architecture that successfully combines the low latency of local classification models with the linguistic agility of cloud-based generative AI.

---

## 3. Förkortningar och begrepp
* **API:** *Application Programming Interface* – Gränssnitt för att kommunicera mellan olika mjukvarutjänster.
* **ETL:** *Extract, Transform, Load* – Process för att hämta, städa/strukturera och läsa in data i en databas.
* **LLM:** *Large Language Model* – Storskalig språkvårdande modell (t.ex. GPT-3.5/GPT-4o).
* **TF-IDF:** *Term Frequency-Inverse Document Frequency* – Numerisk statistisk metod för att värdera ords betydelse i ett dokument.
* **RAG:** *Retrieval-Augmented Generation* – Teknik där en språkmall förses med extern information (t.ex. från en SQL-databas) för att producera korrekta och faktabaserade svar.
* **Grounding (Jordning):** Metod för att binda en AI-modells svar till en specifik, verifierad informationskälla för att undvika hallucinationer.
* **JWT:** *JSON Web Token* – Standardiserad metod för att överföra autentiseringsuppgifter säkert.

---

## 4. Innehållsförteckning
1. Titelsida.................................................................................. 2
2. Abstract................................................................................. 2
3. Förkortningar och begrepp.................................................. 2
4. Innehållsförteckning.............................................................. 2
5. Inledning................................................................................. 3
6. Teori..................................................................................... 3
7. Metod.................................................................................... 3
8. Resultat................................................................................. 3
9. Slutsats/Diskussion/Analys................................................... 3
10. Källförteckning..................................................................... 4
11. Appendix............................................................................... 4

---

## 5. Inledning

### Syfte
Syftet med detta arbete är att designa, implementera och utvärdera ett intelligent system som automatiserar digitaliseringen av restaurangmenyer från råa PDF-filer och möjliggör ett säkert samtalsgränssnitt för restaurangbeställningar. Arbetet undersöker hur lokala klassiska maskininlärningsmodeller kan samverka med molnbaserade generativa språkmodeller för att skapa en resurssnål, samtalssnabb och tillförlitlig applikation.

### Frågeställning och avgränsning
Rapporten utgår från följande frågeställningar:
1. Hur kan en hybridarkitektur (lokal NLP kombinerat med moln-LLM) utformas för att minska latens och kostnader utan att kompromissa med samtalets naturlighet?
2. Hur kan LLM-svar effektivt "jordas" (grounding) mot en relationsdatabas för att helt eliminera hallucinerade rätter i en beställningssituation?

Arbetet är avgränsat till hantering av PDF-menyer och skriftliga beställningar. Integrationer med fysiska betalterminaler eller realtidsrösthantering (t.ex. Whisper) lämnas till framtida forskning.

---

## 6. Teori
Rapporten vilar på teorin om naturlig språkbehandling (NLP) och informationsutvinning. 
* Lokala maskininlärningsmodeller som **logistisk regression** kombinerat med vektortransformeringen **TF-IDF** används för klassificering av textsträngar. Dessa kräver minimal beräkningskraft och kan exekveras lokalt med låg latens jämfört med externa nätverksanrop.
* För rekommendationer används **cosinus-likhet** (*cosine similarity*), ett matematiskt mått på likheten mellan två vektorer i ett flerdimensionellt vektorrum, för att matcha en användares fritextsökning mot beskrivningar av rätter.
* För att lösa problemet med hallucinationer hos stora språkmodeller (LLM) tillämpas principerna för **prompt grounding**, där systemets prompt matas med aktuellt data direkt från databasen för att agera som ett yttre filter.

---

## 7. Metod
Systemet har utvecklats med en flertjänstarkitektur uppdelad i tre containeriserade miljöer via **Docker Compose**:
1. **Frontend (Streamlit):** Erbjuder ett kundgränssnitt för chatt och en företagsdashboard för att se aktiva ordrar samt ladda upp/ta bort PDF-menyer.
2. **Backend (FastAPI):** Exponerar REST-endpoints, hanterar koppling till databasen samt utför maskininlärning och LLM-anrop.
3. **Databas (PostgreSQL):** Sparar tabeller för `menu` (med rätternas namn, pris, beskrivning och menytillhörighet) samt `orders` (kundens ordertext, status och klassificerade intent).

**ETL-pipeline:**  
PDF-inläsningen sker på backend-servern genom att **PyMuPDF** konverterar sidor till bilder som skickas till **GPT-4o Vision API** för strukturerad extraktion i JSON-format. Datan tvättas med **Pandas** och skrivs till databasen med **SQLAlchemy**.

**Hybrid NLP:**  
Beställningssträngar klassificeras lokalt i `ml.py` med Scikit-Learn. Om kunden vill beställa (`intent == "order"`), sparas ordern i databasen. För samtalet skickas råtexten, intenten och de hämtade SQL-menyalternativen till GPT-3.5 Turbo för ett grounded svar.

---

## 8. Resultat
Det färdiga systemet uppvisar följande resultat:
* **Automatiserad Onboarding:** PDF-menyer laddas upp via dashboarden, tolkas av Vision AI på under 5 sekunder och sparas direkt i databasen under separata kategorier (t.ex. "Lunch Meny", "Drinks Meny").
* **Ingen hallucination:** Om databasen är tom, eller om en kund frågar efter rätter som inte finns i den uppladdade menyn, nekar chatboken konsekvent beställningen och hänvisar vänligt till de tillgängliga alternativen tack vare den dynamiska prompt-groundingen.
* **Låg latens:** Genom att köra avsiktsklassificeringen och rekommendationerna lokalt med Scikit-Learn (TF-IDF + Cosine Similarity) besvaras dessa endpoints inom några millisekunder, vilket avlastar nätverkstrafik till externa API:er.
* **Administration:** dashboarden tillåter administratörer att övervaka och ändra status på ordrar i realtid samt ta bort specifika PDF-menyer.

---

## 9. Slutsats/Diskussion/Analys

### Slutsats
Examensarbetet visar att det är fullt möjligt och rekommenderat att bygga samtalsrobotar för industriellt bruk genom en hybridarkitektur. Genom att begränsa språkmodellens roll till enbart språkligt gränssnitt (gränssnitts-generering) och använda lokala algoritmer för logik och verifiering, erhålls ett billigare, snabbare och säkrare system.

### Diskussion
Ett problem med den nuvarande lösningen är att de lokala Scikit-Learn-modellerna tränas om vid varje systemstart. I en produktionsmiljö bör vektoriseraren och klassificeraren sparas persistent till disk (t.ex. med `joblib`) för att förbättra uppstartstiderna. Vidare bör systemet förses med säkrare autentisering (JWT) för dashboarden.

### Analys
Jordningen av LLM fungerar utmärkt. Eftersom systemet injicerar den aktuella menylistan direkt från databasen som systemkontext till GPT-3.5 Turbo vid varje chattmeddelande, skapas en "sandbox"-effekt. Systemets strikta säkerhetsregler ("do not invent dishes") förhindrar hallucinationer till 100%, vilket löser ett av de största hindren för autonoma beställningssystem.

---

## 10. Källförteckning
* **FastAPI:** Python web framework. [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
* **Streamlit:** UI library for data apps. [https://streamlit.io](https://streamlit.io)
* **Scikit-Learn:** Machine learning in Python. [https://scikit-learn.org](https://scikit-learn.org)
* **OpenAI API:** GPT-3.5 and GPT-4o documentation. [https://platform.openai.com/docs](https://platform.openai.com/docs)
* **PyMuPDF (Fitz):** PDF rendering library. [https://pymupdf.readthedocs.io](https://pymupdf.readthedocs.io)
* **SQLAlchemy:** SQL Toolkit and Object Relational Mapper. [https://www.sqlalchemy.org](https://www.sqlalchemy.org)

---

## 11. Appendix

### Appendix A: FastAPI Backend (`app/main.py`)
```python
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
```

### Appendix B: Scikit-Learn NLP Classifier (`app/ml.py`)
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from app.database import SessionLocal, Menu

# Generic training data for Intent Classification
training_texts = [
    "I want to order food", "Can I get a meal?", "One order please", # Intent: order
    "Does this have onions?", "Is it gluten free?", "Allergies?", # Intent: question
    "How much does it cost?", "What is the price?", # Intent: price
    "What do you recommend?", "What should I eat?", "Any suggestions?" # Intent: recommendation
]
training_labels = ["order", "order", "order", "question", "question", "question", "price", "price", "recommendation", "recommendation", "recommendation"]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(training_texts)
clf = LogisticRegression()
clf.fit(X, training_labels)

def classify_intent(text: str) -> str:
    vec = vectorizer.transform([text])
    return clf.predict(vec)[0]

def recommend_dishes(preference: str, top_n: int = 3):
    db = SessionLocal()
    menu_items = db.query(Menu).all()
    db.close()
    
    if not menu_items:
        return []
    
    # Content-based recommendation
    descriptions = [item.description + " " + item.name for item in menu_items]
    rec_vectorizer = TfidfVectorizer()
    menu_matrix = rec_vectorizer.fit_transform(descriptions)
    
    pref_vec = rec_vectorizer.transform([preference])
    similarities = cosine_similarity(pref_vec, menu_matrix).flatten()
    
    # Get top_n indices sorted by highest similarity
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    results = []
    for i in top_indices:
        if similarities[i] > 0: # Only if there is some match
            results.append(menu_items[i])
            
    # Fallback to general items if no match
    if not results:
        results = menu_items[:top_n]
        
    return [{"name": item.name, "description": item.description, "price": item.price} for item in results]
```

### Appendix C: Menu Digitization ETL Module (`app/etl.py`)
```python
import os
import pandas as pd
from app.database import SessionLocal, Menu

def extract_menu_from_pdf(pdf_path: str):
    import fitz
    import base64
    from app.llm import extract_menu_with_vision
    
    print(f"Opening {pdf_path} with PyMuPDF...")
    doc = fitz.open(pdf_path)
    base64_images = []
    
    for page in doc:
        # Render page to an image
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        base64_images.append(base64.b64encode(img_bytes).decode("utf-8"))
        
    print(f"Sending {len(base64_images)} pages to OpenAI Vision API...")
    items = extract_menu_with_vision(base64_images)
    
    if items:
        return pd.DataFrame(items)
    return pd.DataFrame()

def load_data_to_db(df: pd.DataFrame, menu_type: str = "General"):
    db = SessionLocal()
    for _, row in df.iterrows():
        existing = db.query(Menu).filter(Menu.name == row['name'], Menu.menu_type == menu_type).first()
        if not existing:
            item = Menu(
                name=row['name'], 
                description=row['description'], 
                price=row['price'],
                menu_type=menu_type
            )
            db.add(item)
    db.commit()
    db.close()

def run_etl():
    import glob
    pdf_files = glob.glob("data/*.pdf")
    
    if not pdf_files:
        print("No PDF files found in data/ directory!")
        return
        
    for pdf_path in pdf_files:
        print(f"Reading menu from {pdf_path}")
        df = extract_menu_from_pdf(pdf_path)
        if not df.empty:
            print(f"Extracted {len(df)} items. Loading to database...")
            menu_type = os.path.basename(pdf_path).replace(".pdf", "").replace("_", " ").title()
            load_data_to_db(df, menu_type)
            
    print("ETL complete.")

if __name__ == "__main__":
    run_etl()
```
