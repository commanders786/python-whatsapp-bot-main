import os
import pickle
import json
import threading
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import fuzz
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

def search_products(query, session=None, top_k=40):
    global products, product_embeddings
    
    model = get_model()
    if products is None or product_embeddings is None:
        products, product_embeddings = get_product_embeddings()
    
    query = query.strip()

    # 🧠 Use Gemini to detect category
    detected_category = detect_category_with_gemini(query)
    print(f"🧭 Gemini-detected category: {detected_category}")

    # 🔍 Filter based on category
    filtered_indices = []
    if detected_category:
        filtered_indices = [
            i for i, p in enumerate(products)
            if p.get("fb_product_category") == detected_category
        ]
    else:
        filtered_indices = list(range(len(products)))

    if not filtered_indices:
        return f"No products found in category {detected_category or 'all'}", 0

    query_embedding = model.encode([query])
    subset_embeddings = [product_embeddings[i] for i in filtered_indices]
    similarities = cosine_similarity(query_embedding, subset_embeddings)[0]

    top_indices = similarities.argsort()[-top_k:][::-1]
    output = f"\n🔍 Search Results for: '{query}'"
    found_any = 0

    print("top_indices:", top_indices)

    for idx in top_indices:
        product = products[filtered_indices[idx]]
        score = similarities[idx]
        

        # Replace the original condition with this fuzzy match version
        if fuzz.ratio(query.lower(), (product.get('name') or '').lower()) > 30 or fuzz.ratio(query.lower(), (product.get('pattern') or '').lower()) > 30:
             score += 0.5
        print(product['name'], score)
        if score < 0.45:
            continue

        found_any = 1
        output += f"\n\n🛒 {product['name']}"
        output += f"\n💰 itemId: {product['retailer_id']}"
        output += f"\n💰 Price: {product['price']}"
        output += f"\n💰 Unit: {product['unit']}"
        output += f"\n💰 Other names: {product['pattern']}"
        output += f"\n🔗 Match Score: {score:.2f}"

    if found_any and session:
        response = (
            "Anghadi AI ⚡ may take few seconds (5–10) to process your request"
            if session.get('language') == 'en'
            else "അങ്ങാടി AI ⚡ താങ്കളുടെ അഭ്യർത്ഥന പ്രോസസ്സ് ചെയ്യാൻ കുറച്ച് സെക്കന്റുകൾ (5–10) എടുത്തേക്കാം"
        )
        data = get_text_message_input(session.get('number'), response)
        send_message(data)


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
    "snacks", "bakeries", "food", "nuts", "general", "oth"
]

def detect_category_with_gemini(query):
    """
    Use Gemini API directly (without importing from gemini_service)
    to classify grocery item category.
    """
    try:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""
You are a classification assistant for a grocery shopping bot.

Your task:
Given a user query, identify which product category it belongs to.
Choose ONLY from these categories:
{', '.join(CATEGORIES)}.

Examples:
- "chicken" -> meat
- "കോഴി" -> meat
- "beef" -> meat
- "apple" -> fruits
- "garlic" -> vegetables
- "biryani" -> food
- "bread" -> bakeries
- "fish" -> fish
- "cashew" -> nuts
- "soap" -> oth
- "detergent" -> oth
-coke ,pepsi,fanta,sprite etc -> oth

NB:just dont adhere to only thease examples if any item comes out of thease check it is in which category
   meat inclues only raw meat not ready to cook items

   food inclues lot of items arabian ,chinease so please understand query and map it corectly

Now, classify the following query:
"{query}"

Return only the category name, nothing else.
"""

        response = model.generate_content(
            contents=prompt,
            generation_config={
                "max_output_tokens": 10,
                "temperature": 0.2,
                "top_p": 0.95
            }
        )

        category = response.text.strip().lower()

        # Validate
        if category not in CATEGORIES:
            print(f"⚠️ Gemini returned invalid category '{category}', defaulting to None")
            return None

        print(f"✅ Gemini detected category: {category}")
        return category

    except Exception as e:
        print(f"❌ Error detecting category with Gemini: {e}")
        return None
