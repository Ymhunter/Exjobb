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
