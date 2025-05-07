import requests
import json
import os
from dotenv import load_dotenv

from app.utils import messages

load_dotenv()

# Replace with your actual access token and business account ID
access_token = os.getenv("ACCESS_TOKEN")
business_account_id = "579242655280457"

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


def send_mfc(recipient_phone_number,language):
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
                            "id": "opt7",
                            "title":  messages.button_names["mt"][language]
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "opt8",
                            "title":  messages.button_names["fish"][language]
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
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f'''{response} \n '''
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "oc",
                            "title":  "proceed"
                        }
                    },{
                        "type": "reply",
                        "reply": {
                            "id": "add",
                            "title": "Add Items"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "clear",
                            "title": "clear"
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
                "text": "Hi Welcome to അങ്ങാടി 🤗\n Please choose your Language \n ദയവായി നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക "
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
                                "id": "opt8",
                                "title":messages.button_names["fish"][language],
                                "description":"Fresh fish",
                            },
                             {
                                "id": "opt7",
                                "title":messages.button_names["mt"][language],
                                "description":"Beef Mutton Chicken Kaada ",
                            },
                             {
                                "id": "opt2",
                                "title":messages.button_names["gr"][language],
                                "description":"Grains and all masala",
                            },
                            
                            {
                                "id": "medicine",
                                "title":messages.optmsgs["title2"][language],
                                "description": messages.optmsgs["desc2"][language],
                            }
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