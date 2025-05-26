import os
import pickle
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.cloud_apis import send_message
from app.utils.messages import get_text_message_input

# File paths
PICKLE_FILE = "product_embeddings.pkl"
JSON_FILE = "result.json"
ALWAYS_CREATE=True

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

model = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ Load the model ONCE


 # ✅ Load or generate embeddings
if os.path.exists(PICKLE_FILE) and not ALWAYS_CREATE:
    
    print("✅ Loading embeddings from file...")
    with open(PICKLE_FILE, "rb") as f:
        data = pickle.load(f)
        product_embeddings = data["embeddings"]
        products = data["products"]
else:
    print("⚡ Embeddings not found — generating now...")
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
   

# ✅ Product search function
def search_products(query,session, top_k=15):
    nothing=0
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, product_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    output = f"\n🔍 Search Results for: '{query}'"
    print(f"\n🔍 Search Results for: '{query}'")
    for idx in top_indices:
        product = products[idx]
        score = similarities[idx]
        if score<0.4:
            continue
        nothing=1
        output += f"\n\n🛒 {product['name']}"
        output += f"\n💰 itemId: {product['retailer_id']}"
        output += f"\n💰 Price: {product['price']}"
        output += f"\n💰 Unit: {product['unit']}"
        output += f"\n💰 Other names: {product['pattern']}"
        output += f"\n🔗 Match Score: {score:.2f}"
        print(score)
    if nothing:
     response ="Anghadi AI ⚡ may take take few seconds  (5-10) to process your request" if session.get('language')=='en' else "അങ്ങാടി AI ⚡ താങ്കളുടെ അഭ്യർത്ഥന പ്രോസസ്സ് ചെയ്യാൻ കുറച്ച് സെക്കന്റുകൾ (5-10) എടുത്തേക്കാം"
     data = get_text_message_input(session.get('number'), response)
     send_message(data)
    return output,nothing





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

