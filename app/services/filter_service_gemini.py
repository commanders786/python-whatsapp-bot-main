import os
import pickle
import json
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai

# Constants
PICKLE_FILE = "product_embeddings_gemini.pkl"
JSON_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "result.json")
ALWAYS_CREATE = True
GEMINI_API_KEY = "AIzaSyCdjhXYHSQCThh2GF7UNB8pYTYXhy5vajQ"  # 🔁 Replace with your actual API key
GEMINI_MODEL_NAME = "models/gemini-embedding-exp-03-07"

# ✅ Setup Gemini Client
genai.configure(api_key=GEMINI_API_KEY)
embedding_model = genai.get_model(GEMINI_MODEL_NAME)

# ✅ Load products from result.json
def load_products_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat_products = []
    for category, retailers in data.items():
        for retailer_id, product in retailers.items():
            product["fb_product_category"] = category
            flat_products.append(product)
    return flat_products

# ✅ Build a clean product text for embedding
def build_product_text(product):
    name = product.get("name", "")
    pattern = product.get("pattern") or ""
    description = product.get("description") or ""
    category = product.get("fb_product_category", "")
    return f"{name} {pattern} {description} {category}".lower().strip()

# ✅ Call Gemini API to get embedding
def get_gemini_embedding(text):
    try:
        response = genai.embed_content(
            model="models/embedding-001",  # or "embedding-001"
            content=text,
            task_type="retrieval_document"
        )
        return response['embedding']
    except Exception as e:
        print(f"❌ Error embedding '{text}': {e}")
        return [0.0] * 768  # fallback dummy vector

# ✅ Load or create embeddings
if os.path.exists(PICKLE_FILE) and not ALWAYS_CREATE:
    print("✅ Loading Gemini embeddings from file...")
    with open(PICKLE_FILE, "rb") as f:
        data = pickle.load(f)
        product_embeddings = data["embeddings"]
        products = data["products"]
else:
    print("⚡ Gemini embeddings not found — generating now...")
    products = load_products_from_json(JSON_FILE)
    product_texts = [build_product_text(p) for p in products]
    product_embeddings = [get_gemini_embedding(text) for text in product_texts]

    with open(PICKLE_FILE, "wb") as f:
        pickle.dump({
            "products": products,
            "embeddings": product_embeddings
        }, f)

# ✅ Search function
def search_products(query, top_k=5, threshold=0.5):
    query_embedding = get_gemini_embedding(query.lower().strip())
    similarities = cosine_similarity([query_embedding], product_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    print(f"\n🔍 Search Results for: '{query}'")
    results_found = False

    for idx in top_indices:
        score = similarities[idx]
        if score < threshold:
            continue  # skip low-match results

        product = products[idx]
        print(f"\n🛒 {product['name']}")
        print(f"🆔 Item ID: {product['retailer_id']}")
        print(f"💰 Price: {product.get('price', '-')}")
        print(f"📏 Unit: {product.get('unit', '-')}")
        print(f"🧾 Pattern: {product.get('pattern', '-')}")
        print(f"📊 Score: {score:.2f}")
        results_found = True

    if not results_found:
        print("⚠️ No good matches found. Try another term!")

# ✅ Input loop
if __name__ == "__main__":
    while True:
        user_input = input("\n🔍 Enter a product to search (or type 'exit' to quit): ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting search. Have a great day!")
            break
        elif user_input == "":
            print("⚠️ Please enter something!")
            continue
        else:
            search_products(user_input)
