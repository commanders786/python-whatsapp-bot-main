import os
import pickle
import json
import threading
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
from app.services.cloud_apis import send_message
from app.utils.messages import get_text_message_input


# File paths
PICKLE_FILE = "product_embeddings.pkl"
JSON_FILE = "result.json"
ALWAYS_CREATE=True

# Global variables for lazy loading
model = None
products = None
product_embeddings = None
_model_lock = threading.Lock()

# ✅ Load and flatten product data from result.json
def load_products_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    flat_products = []
    for category, retailers in data.items():
        for retailer_id, product in retailers.items():
            product["fb_product_category"] = category  # Add category info for context
            flat_products.append(product)
    return flat_products

def get_model():
    """Lazy load the model with thread safety"""
    global model
    if model is None:
        with _model_lock:
            if model is None:
                print("Loading SentenceTransformer model...")
                model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Model loaded successfully")
    return model



 # ✅ Load or generate embeddings


def get_product_embeddings():
    global products, product_embeddings
    
    if os.path.exists(PICKLE_FILE) and not ALWAYS_CREATE:
        print("✅ Loading embeddings from file...")
        with open(PICKLE_FILE, "rb") as f:
            data = pickle.load(f)
            product_embeddings = data["embeddings"]
            products = data["products"]
        return products, product_embeddings
    else:
        print("⚡ Embeddings not found — generating now...")
        # Ensure model is loaded before using it
        model = get_model()
        products = load_products_from_json(JSON_FILE)
        product_texts = [
            f"{p['retailer_id']} {p['name']} {p['description']}   {p['pattern']}"
            for p in products
        ]
        product_embeddings = model.encode(product_texts)
        with open(PICKLE_FILE, "wb") as f:
            pickle.dump({
                "products": products,
                "embeddings": product_embeddings
            }, f)
        return products, product_embeddings
        

# # ✅ Product search function
# def search_products(query,session=None, top_k=20):
#     global products, product_embeddings
    
#     # Ensure model and data are loaded
#     model = get_model()
#     if products is None or product_embeddings is None:
#         products, product_embeddings = get_product_embeddings()
    
#     query=query.strip()
#     nothing=0
#     query_embedding = model.encode([query])
#     similarities = cosine_similarity(query_embedding, product_embeddings)[0]
#     top_indices = similarities.argsort()[-top_k:][::-1]
#     output = f"\n🔍 Search Results for: '{query}'"
#     print(f"\n🔍 Search Results for: '{query}'")
#     for idx in top_indices:
      
#         product = products[idx]
        
#         score = similarities[idx]
      
#         # if query.lower() in (product.get('name') or '').lower() or query.lower() in (product.get('pattern') or '').lower():

#         #   score += 0.5


#                 # Install with: pip install thefuzz[speedup]
#         # from thefuzz import fuzz

#         # # Replace the original condition with this fuzzy match version
#         # if fuzz.ratio(query.lower(), (product.get('name') or '').lower()) > 80 or \
#         # fuzz.ratio(query.lower(), (product.get('pattern') or '').lower()) > 80:
#         #     score += 0.5
                
#         if score<0.4:
#             continue
#         nothing=1
#         output += f"\n\n🛒 {product['name']}"
#         output += f"\n💰 itemId: {product['retailer_id']}"
#         output += f"\n💰 Price: {product['price']}"
#         output += f"\n💰 Unit: {product['unit']}"
#         output += f"\n💰 Other names: {product['pattern']}"
#         output += f"\n🔗 Match Score: {score:.2f}"
#         print(product['name'],score)
      
       
#     if nothing:
#      response ="Anghadi AI ⚡ may take take few seconds  (5-10) to process your request" if session.get('language')=='en' else "അങ്ങാടി AI ⚡ താങ്കളുടെ അഭ്യർത്ഥന പ്രോസസ്സ് ചെയ്യാൻ കുറച്ച് സെക്കന്റുകൾ (5-10) എടുത്തേക്കാം"
#      data = get_text_message_input(session.get('number'), response)
#      send_message(data)
#     return output,nothing
model = get_model()
def search_products(query, session=None, top_k=40):
    response = (
            "Anghadi AI ⚡ may take few seconds (5–10) to process your request"
            if session.get('language') == 'en'
            else "അങ്ങാടി AI ⚡ താങ്കളുടെ അഭ്യർത്ഥന പ്രോസസ്സ് ചെയ്യാൻ കുറച്ച് സെക്കന്റുകൾ (5–10) എടുത്തേക്കാം"
        )
    data = get_text_message_input(session.get('number'), response)
    send_message(data)
    global products, product_embeddings

   
    if products is None or product_embeddings is None:
        products, product_embeddings = get_product_embeddings()

    query = query.strip()

    # 🧠 Detect one or more likely categories using Gemini
    detected_categories = detect_category_with_gemini(query)
    print(f"🧭 Gemini-detected categories: {detected_categories}")

    # 🔍 Filter indices based on one or more categories
    if detected_categories:
        filtered_indices = [
            i for i, p in enumerate(products)
            if p.get("fb_product_category") in detected_categories
        ]
        
    else:
        filtered_indices = list(range(len(products)))

    if not filtered_indices:
        return f"No products found in categories {detected_categories or 'all'}", 0

    query_embedding = model.encode([query])
    subset_embeddings = [product_embeddings[i] for i in filtered_indices]
    similarities = cosine_similarity(query_embedding, subset_embeddings)[0]

    top_indices = similarities.argsort()[-top_k:][::-1]
    output = f"\n🔍 Search Results for: '{query}'"
    found_any = 0

    for idx in top_indices:
        product = products[filtered_indices[idx]]
        
        score = similarities[idx]
        

        # ⚡ Use RapidFuzz for substring-like fuzzy matching
        if fuzz.partial_ratio(query.lower(), (product.get('name') or '').lower()) > 50 or fuzz.partial_ratio(query.lower(), (product.get('pattern') or '').lower()) > 50 or query.lower() in (product.get('pattern') or '').lower() :
            score += 0.5

        if score < 0.45:
            continue

        found_any = 1
        output += f"\n\n🛒 {product['name']}"
        output += f"\n💰 itemId: {product['retailer_id']}"
        output += f"\n💰 Price: {product['price']}"
        output += f"\n💰 Other names: {product['pattern']}"
        output += f"\n🔗 Match Score: {score:.2f}"

    # if found_any and session:
    #     response = (
    #         "Anghadi AI ⚡ may take few seconds (5–10) to process your request"
    #         if session.get('language') == 'en'
    #         else "അങ്ങാടി AI ⚡ താങ്കളുടെ അഭ്യർത്ഥന പ്രോസസ്സ് ചെയ്യാൻ കുറച്ച് സെക്കന്റുകൾ (5–10) എടുത്തേക്കാം"
    #     )
    #     data = get_text_message_input(session.get('number'), response)
    #     send_message(data)

    return output, found_any




def main():
 global products, product_embeddings
 products, product_embeddings = get_product_embeddings()
if __name__ == "__main__":
    main()

# ✅ Search loop
# while True:
#     user_input = input("\n🔍 Enter a product to search (or type 'exit' to quit): ").strip()
#     if user_input.lower() in ["exit", "quit"]:
#         print("👋 Exiting search. Have a great day!")
#         break
#     elif user_input == "":
#         print("⚠️ Please enter something!")
#         continue
#     else:
#         search_products(user_input)



# Audio filter


import os
from dotenv import load_dotenv
import google.generativeai as genai

CATEGORIES = [
    "vegetables", "fruits", "meat", "fish",
    "snacks", "bakeries", "food", "nuts", "general", "oth","childcare"
]
def detect_category_with_gemini(query):
    """
    Use Gemini API directly (without importing from gemini_service)
    to classify grocery item category or multiple likely categories.
    """
    try:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
You are a classification assistant for a grocery shopping bot.

Given a product query, identify which grocery product categories it could belong to.
Return 1–3 **most likely** categories separated by commas.

Choose only from:
{', '.join(CATEGORIES)}.

Guidelines and examples:
- "cutlet","unnkaaya","samoosa" etc -> snacks
- "chicken" -> meat
- "bread" -> bakeries, oth
- "fish masala" -> food, fish
- "biryani" -> food
- "cashew" -> nuts
- "soap" -> oth
- "apple" -> fruits
- "beef" -> meat
- "cake", "diwali" -> bakeries
- "pepsi", "coke" etc -> oth
- "eggs" -> oth
- "juice", "juices", "milkshake", "falooda", "avil milk" etc -> bakeries, food
- "kunafa" and other sweets or cakes -> bakeries, snacks
- "rice","grains","pulses" -> oth
- Kids toys and study materials -> childcare; all others like diapers, baby food etc -> oth
- If the query is related to snacks, also include bakeries because some products are shared.
-porotta /poratta ->snacks,oth,food
-breakfast->snacks,food
Restaurant names like "AFC Chicken", "Kothiyanz", "Biryani Souk" etc -> food

Now classify the following query:
"{query}"

Note:
- Diwali-related items are added in bakeries.
- "food" mainly includes restaurant meals, not supermarket items.
- Supermarket items usually belong to "oth".
- For juices, shakes, milk-based drinks, sweets, or bakery-related beverages, always include "bakeries" along with "food".
- If unsure, return all possible categories.
Return only the category names, comma separated. No explanation.
"""

        response = model.generate_content(
            contents=prompt,
            generation_config={
                "max_output_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.9,
            
            },stream=True
        )

        final_text = ""

        # ✅ STREAM CORRECTLY
        for chunk in response:
            if not chunk.candidates:
                continue

            candidate = chunk.candidates[0]

            if not candidate.content or not candidate.content.parts:
                continue

            for part in candidate.content.parts:
                if hasattr(part, "text"):
                    final_text += part.text

        if not final_text.strip():
            print("⚠️ Gemini returned no text (blocked or empty)")
            return None

        raw_text = final_text.lower().strip()

        categories = [c.strip() for c in raw_text.split(",") if c.strip() in CATEGORIES]

        if not categories:
            print(f"⚠️ Gemini returned invalid category list '{raw_text}', defaulting to None")
            return None

        print(f"✅ Gemini detected categories: {categories}")
        return categories

    except Exception as e:
        print(f"❌ Error detecting category with Gemini: {e}")
        return None
