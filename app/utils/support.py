# from app.services.gemini_services import call_gemini  # import your working Gemini wrapper

# CATEGORIES = [
#     "vegetables", "fruits", "meat", "fish",
#     "snacks", "bakeries", "food", "nuts", "general", "oth"
# ]

# def detect_category_with_gemini(query):
#     """
#     Use Gemini (via your working call_gemini) to detect product category
#     """
#     prompt = f"""
# You are a classification assistant for a grocery shopping bot.

# Your task:
# Given a user query, identify which product category it belongs to.
# Choose ONLY from these categories:
# {', '.join(CATEGORIES)}.

# Examples:
# - "chicken" -> meat
# - "കോഴി" -> meat
# - "beef" -> meat
# - "apple" -> fruits
# - "garlic" -> vegetables
# - "biryani" -> food
# - "bread" -> bakeries
# - "fish" -> fish
# - "cashew" -> nuts
# - "soap" -> oth
# - "detergent" -> oth

# Now, classify the following query:
# "{query}"

# Return only the category name, nothing else.
#     """

#     response = call_gemini(prompt, model_name="gemini-2.0-flash", temperature=0.2, max_tokens=10)
#     category = response.strip().lower()

#     # normalize and validate
#     if category not in CATEGORIES:
#         print(f"⚠️ Gemini returned invalid category '{category}', defaulting to None")
#         return None
    
#     print(f"✅ Gemini detected category: {category}")
#     return category
