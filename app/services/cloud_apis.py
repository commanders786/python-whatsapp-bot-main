import logging
from flask import current_app, jsonify
import requests
import json
import os
from dotenv import load_dotenv

from app.services.product_service import load_restaurants
from app.utils import messages

load_dotenv()

# Replace with your actual access token and business account ID
access_token = os.getenv("ACCESS_TOKEN")
business_account_id = "579242655280457"
version=os.getenv("VERSION")
PHONE_NUMBER_ID=os.getenv("PHONE_NUMBER_ID")

if not access_token:
    print("Error: FACEBOOK_ACCESS_TOKEN environment variable not set.")
    exit()

base_url = f"https://graph.facebook.com/v22.0/{business_account_id}/messages"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

def send_vfc(recipient_phone_number,language):
    """Sends an interactive button message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": messages.button_names["mwbody"][language]
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt1",
                            "title": messages.button_names["veg"][language]
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt4",
                            "title":  messages.button_names["fr"][language]
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "backfood",
                            "title":  messages.button_names["back"][language]
                        }
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")

def send_gbc(recipient_phone_number,language):
    """Sends an interactive button message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": messages.button_names["mwbody"][language]
            },
            "action": {
                "buttons": [
                  
                   
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt2",
                            "title": messages.button_names["grains"][language]
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "BFC",
                            "title": messages.button_names["bsc"][language]
                        }
                    },
                     {
                        "type": "reply",
                        "reply": {
                            "id": "backfood",
                            "title":messages.button_names["back"][language]
                        }
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")


def get_notes_pharmacist(recipient_phone_number,language):
    """Sends an interactive button message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text":  "Please add your special notes  if any, else type anything to move on" if language=='en' else "നിങ്ങൾ ഇങ്ങനെയുള്ള സന്ദേശങ്ങൾ നൽകാം \n eg: മരുന്ന് 5 ദിവസത്തേക്ക് വേണം. \n eg: കോഴി -കറി കട്ട് \n ഇല്ലെങ്കിൽ Skip ചെയ്യുക  "
            },
            "action": {
                "buttons": [
                  
                   
                    {
                        "type": "reply",
                        "reply": {
                            "id": "skip",
                            "title":"Skip"
                        }
                    },
                     {
                        "type": "reply",
                        "reply": {
                            "id": "clear",
                            "title":"Retake/Cancel"
                        }
                    }
                    
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")


def get_notes(recipient_phone_number,language):
    """Sends an interactive button message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text":  "Please add your notes if any \n Eg: Additional items" if language=='en' else "ദയവായി കുറിപ്പ്  ചേർക്കുക (ഉണ്ടെങ്കിൽ) \n Eg: "
            },
            "action": {
                "buttons": [
                  
                   
                    {
                        "type": "reply",
                        "reply": {
                            "id": "skip",
                            "title":"Skip"
                        }
                    }
                    
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")

def send_bsc(recipient_phone_number,language):
    """Sends an interactive button message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": messages.button_names["mwbody"][language]
            },
            "action": {
                "buttons": [
                  
                   
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt10",
                            "title": messages.button_names["bkry"][language]
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "opt11",
                            "title": messages.button_names["snks"][language]
                        }
                    },
                     {
                        "type": "reply",
                        "reply": {
                            "id": "backfood",
                            "title": messages.button_names["back"][language]
                        }
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")

def request_location_message(recipient_phone_number):
    """Sends a location request message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "location_request_message",
            "body": {
                "text": "As you confirmed the order pls share your location"
            },
            "action": {
                "name": "send_location"
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Location request message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending location request message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")



def send_po(recipient_phone_number,response,language):
    """Sends an interactive button message."""
    url = base_url
    alert="Please click on proceed to confirm " if language=='en' else 'ഓർഡർ സ്ഥിരീകരിക്കാൻ ദയവായി തുടരുക '
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f'''{response} \n \n {alert} '''
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "oc",
                            "title":  "proceed" if language=='en' else 'തുടരുക '
                        }
                    },{
                        "type": "reply",
                        "reply": {
                            "id": "add",
                            "title": "Add Items" if language=='en' else 'കൂടുതൽ സാധനങ്ങൾ'
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "clear",
                            "title": "clear" if language=='en' else 'ഒഴിവാക്കുക'
                        }
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")



def get_language(recipient_phone_number):
    """Sends an interactive button message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Hi Welcome to AI അങ്ങാടി 57 👋🏻\n Please choose your Language \n ദയവായി നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക "
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "en",
                            "title": "English"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "ml",
                            "title": "മലയാളം "
                        }
                    }
                    
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")


def send_options(recipient_phone_number,language):
  
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": messages.optmsgs["header"][language]
            },
            "body": {
                "text": messages.optmsgs["body"][language]
            },
            "footer": {
                "text":messages.optmsgs["footer"][language]
            },
            "action": {
                "button": messages.optmsgs["button"][language],
                "sections": [
                    {
                        "title": "Food",
                        "rows": [

                             {
                                "id": "medicine",
                                "title":messages.optmsgs["title2"][language],
                                "description": messages.optmsgs["desc2"][language],
                            },
                          
                             {
                                "id": "opt1",
                                "title":messages.button_names["veg"][language],
                                "description":"Fresh vegetables",
                            },
                             {
                                "id": "opt4",
                                "title":messages.button_names["fr"][language],
                                "description":"Fresh fruits",
                            },
                             {
                                "id": "opt2",
                                "title":messages.button_names["gr"][language],
                                "description":"Grains and all masala",
                            },
                            {
                                "id": "rest",
                                "title":messages.button_names["rest"][language],
                                "description":"Tastes of koduvally",
                            },
                            
                             {
                                "id": "snacks",
                                "title":messages.optmsgs["snacks"][language],
                                "description":" Bakeries  Evening snacks ",
                            },
                              {
                                "id": "bakeries",
                                "title":messages.optmsgs["bakeries"][language],
                                "description":" Bakeries  from nice bakes ",
                            },
                            {
                                "id": "opt8",
                                "title":messages.button_names["fish"][language],
                                "description":"Fresh fish",
                            },
                             {
                                "id": "opt7",
                                "title":messages.button_names["mt"][language],
                                "description":"Beef Mutton Chicken Kaada ",
                            },
                            
                            
                           
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")


# def send_restaurants(recipient_phone_number, language):
#     restaurant_keys = sorted(list(load_restaurants().keys()))
#     # Get restaurant names
#     url = base_url

#     # Dynamically generate rows for each restaurant
#     restaurant_rows = [
#         {
#             "id": restaurant_name,           # Unique ID
#             "title": restaurant_name,          # Restaurant name as title
#             "description": f"Tastes of {restaurant_name}"
#         }
#         for i, restaurant_name in enumerate(restaurant_keys)
#     ]

#     payload = {
#         "messaging_product": "whatsapp",
#         "recipient_type": "individual",
#         "to": recipient_phone_number,
#         "type": "interactive",
#         "interactive": {
#             "type": "list",
#             "header": {
#                 "type": "text",
#                 "text": messages.optmsgs["header"][language]
#             },
#             "body": {
#                 "text": messages.optmsgs["food_body"][language]
#             },
#             "footer": {
#                 "text": messages.optmsgs["footer"][language]
#             },
#             "action": {
#                 "button": messages.optmsgs["button"][language],
#                 "sections": [
#                     {
#                         "title": "Restaurants",
#                         "rows": restaurant_rows
#                     }
#                 ]
#             }
#         }
#     }

#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
#         print("Interactive button message sent successfully!")
#         print(response.json())
#     except requests.exceptions.RequestException as e:
#         print(f"Error sending interactive button message: {e}")
#         if response is not None:
#             print(f"Response status code: {response.status_code}")
#             print(f"Response body: {response.text}")
def send_restaurants(recipient_phone_number, language, offset=0):
    restaurant_keys = sorted(list(load_restaurants().keys()))
    url = base_url

    # Take 9 restaurants starting from offset
    restaurants_slice = restaurant_keys[offset:offset + 9]

    # Build restaurant rows
    restaurant_rows = [
        {
            "id": restaurant_name,
            "title": restaurant_name,
            "description": f"Tastes of {restaurant_name}"
        }
        for restaurant_name in restaurants_slice
    ]

    # Sections list (always one for Restaurants)
    sections = [
        {
            "title": messages.optmsgs["rest_title"][language],
            "rows": restaurant_rows
        }
    ]

    # Add "Next" section if more restaurants exist
    if offset + 9 < len(restaurant_keys):
        sections.append({
            "title": "More Options",
            "rows": [
                {
                    "id": offset+9,  # unique ID with new offset
                    "title": "Next ➡️",
                    "description": messages.optmsgs["see_more_rest"][language]
                }
            ]
        })

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": messages.optmsgs["header"][language]
            },
            "body": {
                "text": messages.optmsgs["food_body"][language]
            },
            "footer": {
                "text": messages.optmsgs["footer"][language]
            },
            "action": {
                "button": messages.optmsgs["button_rest"][language],
                "sections": sections
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")



def send_food_category(recipient_phone_number,language):
    """Sends an interactive button message."""
    url = base_url
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": messages.button_names["mwbody"][language]
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "VFC",
                            "title":  messages.button_names["vfc"][language]
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "GBC",
                            "title": messages.button_names["gfc"][language]
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "MFC",
                            "title":  messages.button_names["mfc"][language]
                        }
                    }
                  
                ]
            }
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")



def send_whatsapp_image(recipient_phone_number, image_id, caption):
    url = base_url
   
    
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone_number,
        "type": "image",
        "image": {
            "id": image_id,
            "caption": caption
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Interactive button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending interactive button message: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")



def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    
    
    url = f"https://graph.facebook.com/{version}/{PHONE_NUMBER_ID}/messages"

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
        print(response)
        return response
    
    






def send_template_message(template_name, receipt, phone_number):
    """
    Send a WhatsApp template message with a button component.
    
    Args:
        template_name (str): Name of the template (e.g., 'billorder').
        receipt (str): Receipt text for the button's flow_action_data.
        phone_number (str): Recipient phone number (e.g., '919645846341').
    
    Returns:
        Response object or JSON error response.
    """
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    
    url = f"https://graph.facebook.com/{version}/{PHONE_NUMBER_ID}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "button",
                    "sub_type": "flow",
                    "index": 0,
                    "parameters": [
                        {
                            "type": "action",
                            "action": {
                                "flow_token": "1418732815996814",
                                "flow_action_data": {
                                    "init_values": {
                                        "receipt": receipt
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            url, data=json.dumps(payload), headers=headers, timeout=10
        )
        response.raise_for_status()
        print(f"Response: {response.json()}")
        return response
    except requests.Timeout:
        logging.error("Timeout occurred while sending template message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except requests.RequestException as e:
        logging.error(f"Request failed due to: {e}")
        print(f"Payload: {json.dumps(payload)}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500




def send_feedback_buttons(recipient_phone_number: str, language: str = "en"):
    """
    Sends a WhatsApp interactive button message asking for user feedback.
    Supports English and Malayalam.
    """

    # Localized text
    body_text = (
        "*Please share your experience with us* 📝"
        if language == "en"
        else "*നിങ്ങൾ ഡെലിവറി ലഭിച്ചതായി ഞങ്ങൾ പ്രതീക്ഷിക്കുന്നു. ദയവായി നിങ്ങളുടെ അഭിപ്രായം ഞങ്ങളുമായി പങ്കിടൂ.* 📝"
    )

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {"id": "5", "title": "Excellent 🤩✨"},
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "3", "title": "Okay 😊👌"},
                    },
                    {
                        "type": "reply",
                        "reply": {"id": "0", "title": "Not Satisfied 😞👎"},
                    },
                ]
            },
        },
    }

    try:
        response = requests.post(base_url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Feedback button message sent successfully!")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending interactive button message: {e}")
        if 'response' in locals() and response is not None:
            print(f"Status code: {response.status_code}")
            print(f"Response body: {response.text}")

# if __name__ == "__main__":
#     recipient_number = "919961575781"  # Replace with the actual recipient number
    
#     send_options(recipient_number)
    # Send interactive button message
    # send_interactive_button_message(recipient_number)

    # send_po(,"thakkali 10kg")

    # print("\n" + "="*30 + "\n") # Separator

    # # Send location request message
    # request_location_message(recipient_number)\
    # get_language("919961575781")sss