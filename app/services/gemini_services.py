import ast
import asyncio
from datetime import datetime
import json
import os
import re
from venv import logger
from dotenv import load_dotenv
import google.generativeai as genai

from app.services.filter_service import search_products
from app.utils.whatsapp_utils import process_order_message
from .promptTemplate import prompt_template

def call_gemini(prompt, model_name="gemini-2.0-flash", max_tokens=500, temperature=0.7):
    """
    Call Google's Gemini API (or similar generative AI API) with a prompt.
    
    Args:
        prompt (str): The input text prompt
        model_name (str): The model to use (e.g., 'gemini-pro')
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Controls randomness (0.0 to 1.0)
    
    Returns:
        str: Generated response or error message
    """
    try:

        load_dotenv()
        # Configure API key (set this in your environment or directly here)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Set up the model
        model = genai.GenerativeModel(model_name)
        
        # Configure generation parameters
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
        }
        
        # Generate content
        response = model.generate_content(
    contents=prompt,
    generation_config=generation_config
)

        
        # Return the generated text
        return response.text.replace("```text","")
        
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def chatGemini(name,query,session):

    # prompt=f'''System query :You are a AI Shopping bot named Sana,i will be giving you user query from my users 
    # so kindly talk to them in a polite way in max 10 words.if their message looks like a starting of the conversation like hi hello just treat them 
    # by indroducing your self and calling their name if they ask anything outside of our shopping context tell them that you are not aware of it.User query{query} and user name is {name}
    # now generate output in a way that you talk to the user if the user query is something like a purchase order like tomoto 1kg onion 20rs you need to generate a sample po to send to the user to confirm the op
    # by the user just make it simple slno item quantity unit price total and grand total atlast hey always add emart  our company name in the header and po (just po in the generated po header) and always remember just create the po dont tell anything else
    # '''

    filtered_items=search_products(query)
    print(filtered_items)
    print(query)
    print('items',session.get('items'))
    try:
     formatted_prompt = prompt_template.format(
        query=query,
        name=name,
        session=session.get('items'),
        filtered_items=filtered_items,
        language=session.get('language')
    )
    except KeyError as e:
     print(f"⚠️ Missing key in prompt template: {e}")
    except Exception as e:
     print(f"❌ Error formatting prompt: {e}")

    items=[]
    def clean_gemini_response(response):
     """
    Cleans Gemini output by removing markdown fences and extra whitespace.
    Returns cleaned string.
    """
    # Remove any ```json ... ``` or ``` ... ``` completely
     response = re.sub(r"```(?:json)?", "", response)
     response = re.sub(r"```", "", response)
     
    
    # Also strip any leading/trailing spaces or newlines
     return response.strip()
    try:
     response = call_gemini(formatted_prompt)
     print("🧠 Raw response from Gemini:", repr(response))

    # Clean response for safe JSON parsing
     cleaned_response = clean_gemini_response(response)
     print("🧠 Cleaned response from  Gemini:", repr(cleaned_response))
     print("clean",cleaned_response)
    # Try parsing if it looks like JSON
     if cleaned_response.startswith("["):
        parsed = json.loads(cleaned_response)
       
        print("✅ Parsed JSON:", parsed)
        response,items=process_order_message(parsed)

     if cleaned_response.startswith("("):
           parsed = ast.literal_eval(cleaned_response)
           print("tuple",parsed)
           return 'searchresult',list(parsed)
     else:
        print("💬 Plain text response:", cleaned_response)
        # Handle greeting or other text cases here

    except Exception as e:
       print(f"❌ Error during Gemini call: {e}")
   
    print("from gemini",response)
    print(type(response))
    return response,items


# import asyncio
# from datetime import datetime
# import json
# import os
# from venv import logger
# from dotenv import load_dotenv
# # import google.generativeai as genai
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI

# # Initialize Langchain components with Gemini
# load_dotenv()
# google_api_key = os.getenv("GOOGLE_API_KEY")

# if not google_api_key:
#     print("Error: GOOGLE_API_KEY environment variable not set. Langchain with Gemini will not be available.")

# else:
#     try:
#         llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key)
#         memory_gemini = ConversationBufferMemory(memory_key="history")
#         prompt_template = PromptTemplate(
#             input_variables=["history", "name", "query"],
#             template="""System query :You are a AI Shopping bot named Sana,i will be giving you user query from my users
#         so kindly talk to them in a polite way in max 10 words.if their message looks like a starting of the conversation like hi hello just treat them
#         by introducing yourself and calling their name if they ask anything outside of our shopping context tell them that you are not aware of it.
#         Current chat history: {history}
#         User query: {query} and user name is {name}
#         Now generate output in a way that you talk to the user."""
#         )
#         conversation_gemini = LLMChain(llm=llm_gemini, prompt=prompt_template, memory=memory_gemini)
       
#     except Exception as e:
#         print(f"Error initializing Langchain with Gemini: {e}")
       

# def chatGemini(name, query):
   
#         try:
#             response = conversation_gemini.predict(name=name, query=query)
#             response_text = response.strip()
#             print(f"{name}: {query}")
#             print(f"Sana (Langchain - Gemini): {response_text}")
#             return response_text
#         except Exception as le:
#             print(f"Error using Langchain with Gemini: {le}")
#             use_langchain_gemini = False
#             return f"Error processing your request."
    
