import os
from openai import OpenAI
from typing import List
from app.database import Menu

# The API key is automatically picked up from the OPENAI_API_KEY environment variable
client = OpenAI()

def generate_chat_response(prompt: str, intent: str, menu_items: List[Menu]) -> str:
    # 1. Check if the menu is empty
    if not menu_items:
        system_message = (
            "You are a friendly, helpful AI Waiter. "
            "CRITICAL: The restaurant currently has no items on the menu. "
            "If the customer says hello or asks general questions, reply politely. "
            "However, if they ask about food, try to order, or ask for recommendations, politely explain "
            "that the menu is currently empty and you cannot recommend or take orders for any dishes at this time."
        )
        user_message = f"User Message: {prompt}"
    else:
        # 2. Format the menu so the LLM knows what we serve
        menu_context = "Current Restaurant Menu:\n"
        for item in menu_items:
            menu_context += f"- {item.name} (${item.price}): {item.description}\n"
            
        # 3. Define the bot's persona and rules
        system_message = (
            "You are a friendly, helpful AI Waiter at a restaurant. "
            "Use the provided menu to answer questions, recommend dishes, and confirm orders. "
            "If the user is ordering, confirm their order. "
            "Do not invent dishes that are not on the menu. Keep your responses concise, conversational, and polite."
        )
        user_message = f"System Context - User Intent detected: {intent}\n\n{menu_context}\n\nUser Message: {prompt}"
    
    try:
        # 4. Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I'm sorry, I am having trouble thinking right now! Error: {str(e)}"

def extract_menu_with_vision(base64_images: list):
    import json
    
    prompt = """
    You are an expert menu digitizer.
    Look at the provided images of a restaurant menu and extract all the dishes.
    Return a raw JSON list of dictionaries, where each dictionary represents a dish and has EXACTLY these keys:
    - "name": string
    - "description": string (if none, empty string)
    - "price": float (only the number, e.g. 100.0)
    
    Do NOT return markdown blocks like ```json. ONLY return the raw JSON array starting with [ and ending with ].
    """
    
    content = [{"type": "text", "text": prompt}]
    for img in base64_images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}"}
        })
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            temperature=0.0
        )
        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
        return json.loads(raw_output.strip())
    except Exception as e:
        print(f"Vision API error: {e}")
        return []
