from datetime import datetime, timezone
import logging
from flask import current_app, jsonify
import json
import requests
from app.products import process_order_message
from app.services import gemini_services as AI
# from app.services.openai_service import generate_response
import re

from app.services.crud_services import insert_order, insert_user, user_exists
from app.services.product_service import send_whatsapp_product_list
from app.utils.messages import po_template
from app.utils.validations import is_within_radius
from ..sessions import user_sessions

from app.services.cloud_apis import get_language, request_location_message, send_bsc, send_food_category, send_gbc, send_mfc, send_options, send_po, send_vfc, send_whatsapp_image


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient,text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def generate_response(name,response,session):
    # Return text in uppercase
    print(222)
    return AI.chatGemini(name,response,session)


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }
    
    print(current_app.config['ACCESS_TOKEN'])
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        print("data:",data)
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

       
    
    

        
    if wa_id not in user_sessions:
                user_sessions[wa_id] = {}
                user_sessions[wa_id]['po']=[]
                user_sessions[wa_id]['level']="F1"
                user_sessions[wa_id]['items']=[]
                user_sessions[wa_id]['notes']=""
                user_sessions[wa_id]['language']=""
                user=user_exists(wa_id)[0]
                if  not user["exists"]:
                  get_language(wa_id)
                  
                  return
                user_sessions[wa_id]['language']=user['user']['language']
   

    response = ""  # Default response
    print("Recieved message :",message)
    print("\n \n User Session ----",user_sessions[wa_id])
    print("\n\n")
    try:
        # If it's a regular text message
        ts = int(message['timestamp'])
        if (datetime.now(timezone.utc) - datetime.fromtimestamp(ts, timezone.utc)).total_seconds() > 60: return
        if message["type"] == "text":
            
            message_body = message["text"]["body"]

            
                 #  send_interactive_button_message(wa_id)
            

            if  user_sessions[wa_id]['level']=="M2":
                user_sessions[wa_id]['level']="M3"
                user_sessions[wa_id]['notes']=message_body
                request_location_message(wa_id)
                
                
                return
            if user_sessions[wa_id]['level']=="F2":
                user_sessions[wa_id]['level']="F3"
                user_sessions[wa_id]['notes']=message_body
                request_location_message(wa_id)
            
                return
           

            response,items = generate_response(name, message_body,user_sessions[wa_id])
            if items and isinstance(items[0], dict):
             user_sessions[wa_id]['items'].extend(items)
            
           
            elif 'po' in response.lower() :
                send_po(wa_id,response)
                user_sessions[wa_id]['po'].append(message_body)
                
                
                return 
            
            elif 'hi' in response.lower() or 'ഹായ്' in response.lower() or '?' in response.lower():
                print("-----")
                data = get_text_message_input(wa_id, response)
                send_message(data)
                user=user_exists(wa_id)[0]
                if  not user["exists"]:
                  get_language(wa_id)
                  return
                else:
                 #  send_interactive_button_message(wa_id)
                  user_sessions[wa_id]['language']=user['user']['language']
                 
                  send_options(wa_id,user_sessions[wa_id]['language'])
            
                return None
            
            elif 'searchresult'==response:
                send_whatsapp_product_list(list(items),wa_id)
                return
      
        elif message["type"] == "interactive":
            
            if message["interactive"]['type']=='list_reply':
                button_id = message["interactive"]["list_reply"]["id"]
                print(222)
            else:
                button_id = message["interactive"]["button_reply"]["id"]
            
            
            if button_id in ['food','backfood']:
               print(333)
               send_food_category(wa_id,user_sessions[wa_id]['language'])
               return
            elif button_id=='medicine':

                user_sessions[wa_id]['level']="M1"
                response ="Please send a picture of your valid prescription"  if user_sessions[wa_id]['language']=='en' else "ദയവായി നിങ്ങളുടെ സാധുവായ മരുന്ന് ഷീറ്റിന്റെ ചിത്രം അയയ്ക്കൂ."
                data = get_text_message_input(wa_id, response)
                send_message(data)
                return
            elif button_id =='en':
              new_user = {"id": wa_id, "phone": wa_id, "name": name, "lastlogin": current_time, "language": "en"}
              response_status = insert_user(new_user)
              print(response_status)
              user_sessions[wa_id]['language']='en' 
              send_options(wa_id,user_sessions[wa_id]['language'])
              return   
            elif button_id =='ml':
              new_user = {"id": wa_id, "phone": wa_id, "name": name, "lastlogin": current_time, "language": "ml"}
              response_status = insert_user(new_user)
              print(response_status)
              user_sessions[wa_id]['language']='ml' 
              send_options(wa_id,user_sessions[wa_id]['language'])
              return

            elif button_id == "opt1":
                send_whatsapp_product_list("vegetables",wa_id)
                return
            
            elif button_id == "opt2":
               send_whatsapp_product_list("groceries",wa_id)
               return
            
          
            elif button_id=='opt4':
               send_whatsapp_product_list("fruits",wa_id)
               return
            elif button_id=='opt7':
                send_whatsapp_product_list("meat",wa_id)
                return
            elif button_id=='opt8':
                send_whatsapp_product_list("fish",wa_id)
                return
            elif button_id=='opt10':
                send_whatsapp_product_list("bakeries",wa_id)
                return
            elif button_id=='VFC':
                send_vfc(wa_id,user_sessions[wa_id]['language'])
            elif button_id=='GBC':
                 send_gbc(wa_id,user_sessions[wa_id]['language'])
            elif button_id=='MFC':
                send_mfc(wa_id,user_sessions[wa_id]['language'])
                
            elif button_id=='BFC':
                send_bsc(wa_id, user_sessions[wa_id]['language'])
                return
            
               
            elif button_id=="oc":
                user_sessions[wa_id]['level']="F2"
                response ="Please add your notes  if any, else type any key to move on" if user_sessions[wa_id]['language']=='en' else "ദയവായി നിങ്ങളുടെ കുറിപ്പുകൾ ചേർക്കുക, ഇല്ലെങ്കിൽ തുടരാൻ ഏതെങ്കിലും കീ ടൈപ്പ് ചെയ്യുക."
                data = get_text_message_input(wa_id, response)
                send_message(data)
                
                
                return
            elif button_id=="clear":
                user_sessions[wa_id]['level']=""
                user_sessions[wa_id]['items']=[]
                response ="Now your cart is clear please continue shop with us" if user_sessions[wa_id]['language']=="en" else "നിങ്ങളുടെ കാർട്ട് ഇപ്പോൾ ശൂന്യമാണ്, ദയവായി ഞങ്ങളോടൊപ്പം ഷോപ്പ് ചെയ്യുന്നത് തുടരണം"
                data = get_text_message_input(wa_id, response)
                send_message(data)
                send_options(wa_id,user_sessions[wa_id]['language'])
                return
            
            elif button_id=="add":
                response ="please add your items " if user_sessions[wa_id]['language']=="en" else "ദയവായി നിങ്ങളുടെ ഐറ്റങ്ങൾ ചേർക്കുക"
                data = get_text_message_input(wa_id, response)
                send_message(data)
                send_options(wa_id,user_sessions[wa_id]['language'])
                return
                
  
            else:
        
                # response = "Sorry, I didn't understand your selection."
                pass

        elif message["type"] == "location":
                

                location = body["entry"][0]["changes"][0]["value"]["messages"][0]["location"]
                if (is_within_radius(location["latitude"],location["longitude"])):
                 coordinates=extract_location_link(body)
                 user_sessions[wa_id]['location']=coordinates
                 response ="Your order will be in your doors within 20 minutes.\n Please contact +91 99615 75781 for further queries." if user_sessions[wa_id]['language']=="en" else "നിങ്ങളുടെ ഓർഡർ 20 മിനിറ്റിനകം നിങ്ങളുടെ വാതിലിൽ എത്തിച്ചേരും.കൂടുതൽ വിവരങ്ങൾക്ക് ദയവായി +91 99615 75781 എന്ന നമ്പറിൽ ബന്ധപ്പെടുക."
                else:
                 response ="Sorry for now we are not providing our service in your location" if user_sessions[wa_id]['language']=='en' else "ക്ഷമിക്കണം, ഇപ്പോഴെത്തന്നെ നിങ്ങളുടെ സ്ഥലത്ത് ഞങ്ങൾ സേവനം നൽകുന്നില്ല" 
                 data= get_text_message_input(wa_id,response)
                 send_message(data)
                 return
                
                data = get_text_message_input(wa_id, response)
                send_message(data)
                if user_sessions[wa_id]['level']=="M3":
                    
                    user_sessions[wa_id]['level']="F1"
                    

                    response_status=insert_order({"receipt": user_sessions[wa_id]['notes']+user_sessions[wa_id]['medicineimageid'],"bill_amount":0,"userid":wa_id})
               
                    order_notification_template=response_status[0].get('order_id')+"\n"+user_sessions[wa_id]['notes']+"\n"+user_sessions[wa_id]['location']['google']+"\n"+wa_id
                    
                    send_whatsapp_image("919645846341", user_sessions[wa_id]['medicineimageid'],order_notification_template)
                    return
                order_notification_template = po_template(user_sessions[wa_id])
                response_status=insert_order({"receipt":order_notification_template,"bill_amount":0,"userid":wa_id})
               
                print("order Created",response_status)
                order_id = response_status[0].get('order_id')
           
                order_notification_template = po_template(user_sessions[wa_id],order_id=order_id)

                
                data= get_text_message_input(wa_id,order_notification_template)
                send_message(data)
                user_sessions[wa_id]['level']=="F1"
                user_sessions[wa_id]['items']=[]

                return 
        elif message["type"] == "order":
            product_items = message["order"]["product_items"]
            user_sessions[wa_id]['items'].extend(product_items)
            bill_text,items = process_order_message(user_sessions[wa_id]['items'])
            user_sessions[wa_id]['bill']=bill_text
            
            print("\n\n user session",user_sessions[wa_id])

            
            data = get_text_message_input(wa_id, bill_text)
            print("data",data)
            # send_message(data)
            send_po(wa_id,bill_text,user_sessions[wa_id]['language'])
            # request_location_message(wa_id)
            return
        elif user_sessions[wa_id]['level']=='M1' and  message["type"] == "image":
            user_sessions[wa_id]['level']="M2"
            imageid=message["image"]["id"]
            user_sessions[wa_id]['medicineimageid']=imageid
            response ="Please add your notes to pharmacist 💊 if any, else type anything to move on" if user_sessions[wa_id]['language']=='en' else "നിങ്ങൾ ഫാർമസിസ്റ്റിന് ഇങ്ങനെയുള്ള സന്ദേശങ്ങൾ നൽകാം \n eg:\"മരുന്ന് 5 ദിവസത്തേക്ക് വേണം.\""
            data = get_text_message_input(wa_id, response)
            send_message(data)
            return
       


                

    except Exception as e:
        response = "Please enter a valid input"
        print("xxxxxxxxx",e)

    # Send text message back
    if response:
     data = get_text_message_input(wa_id, response)
     print(data)
     send_message(data)
     send_options(wa_id,user_sessions[wa_id]['language'])
     return

    # Optional: send buttons again for more interaction
    if   user_sessions[wa_id] != {}:
    #  send_interactive_button_message(wa_id)
    #  send_options(wa_id)
     print("session",user_sessions[wa_id])


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )


def extract_location_link(body):
    try:
        location = body["entry"][0]["changes"][0]["value"]["messages"][0]["location"]
        latitude = location["latitude"]
        longitude = location["longitude"]

        gmap_link = f"https://www.google.com/maps?q={latitude},{longitude}"
        apple_map_link = f"https://maps.apple.com/?q={latitude},{longitude}"

        return {
            "google": gmap_link,
            "apple": apple_map_link
        }
    except KeyError:
        return None

    
