import os
import pickle
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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
def search_products(query, top_k=15):
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
        output += f"\n\n🛒 {product['name']}"
        output += f"\n💰 itemId: {product['retailer_id']}"
        output += f"\n💰 Price: {product['price']}"
        output += f"\n💰 Unit: {product['unit']}"
        output += f"\n💰 Other names: {product['pattern']}"
        output += f"\n🔗 Match Score: {score:.2f}"
    return output





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



#Audio filter

# import requests

# def download_audio_and_save_as_wav(audio_id):
#     # Step 1: First API call to get audio URL
#     first_api_url = "https://graph.facebook.com/v22.0/{audio_id}"
#     headers = {
#         'Authorization': 'Bearer EAAQKF56ZAbJQBOyWTBZAEQdGBL18R3HcRF1gyo6rQ6XV1uMTrT7ANBWvrSly6TSiUaXESTgPlXBFAfBVJ9c62piJHuNUqtA0Jbsgp2LACMIrfNffq2ZAW6qrQlObtlpSZCZBTQGpYh6KtxiZBkDWXPlbBCIb5emVVB2zf9mPM7ZAgV8XdDwrlxgzJD68ZBWvV4W98VNDb5gXykkQJgGjYBnBGo13Md7HumDaZC5IS'
#     }

#     try:
#         # Making the first API call
#         response = requests.get(first_api_url, headers=headers)
        
#         if response.status_code == 200:
#             # Extract the audio URL from the response
#             audio_url = response.json()['url']
#             print(f"Audio URL: {audio_url}")
#         else:
#             print(f"Failed to retrieve audio URL. Status Code: {response.status_code}")
#             print(response.text)
#             return

#         # Step 2: Second API call to download the audio file
#         audio_response = requests.get(audio_url, headers=headers)

#         if audio_response.status_code == 200:
#             # Save the audio file as .wav
#             with open('downloaded_audio.wav', 'wb') as f:
#                 f.write(audio_response.content)
#             print("Audio file has been saved as 'downloaded_audio.wav'")
#         else:
#             print(f"Failed to download audio. Status Code: {audio_response.status_code}")
#             print(audio_response.text)
#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")

# # Call the function to download and save audio
# download_audio_and_save_as_wav()
