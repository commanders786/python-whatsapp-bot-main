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

def send_vfc(recipient_phone_number):
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
                "text": "Please choose from the list or directly type your order in the chat"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt1",
                            "title": "Vegetables"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt4",
                            "title": "Fruits"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "backfood",
                            "title": "Back"
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

def send_gbc(recipient_phone_number):
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
                "text": "Please choose from the list or directly type your order in the chat"
            },
            "action": {
                "buttons": [
                  
                   
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt2",
                            "title": "Groceries"
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "BFC",
                            "title": "Bakeries and Snacks"
                        }
                    },
                     {
                        "type": "reply",
                        "reply": {
                            "id": "backfood",
                            "title": "Back"
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


def send_mfc(recipient_phone_number):
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
                "text": "Please choose from the list or directly type your order in the chat"
            },
            "action": {
                "buttons": [
                  
                   
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt7",
                            "title": "Meat"
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "opt8",
                            "title": "Fish"
                        }
                    },
                     {
                        "type": "reply",
                        "reply": {
                            "id": "backfood",
                            "title": "Back"
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


def send_bsc(recipient_phone_number):
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
                "text": "Please choose from the list or directly type your order in the chat"
            },
            "action": {
                "buttons": [
                  
                   
                    {
                        "type": "reply",
                        "reply": {
                            "id": "opt10",
                            "title": "Bakeries"
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "opt11",
                            "title": "Snacks"
                        }
                    },
                     {
                        "type": "reply",
                        "reply": {
                            "id": "backfood",
                            "title": "Back"
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



def send_po(recipient_phone_number,response):
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
                "text": f'''{response} \n Confirm your Order'''
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "oc",
                            "title": "Proceed"
                        }
                    },{
                        "type": "reply",
                        "reply": {
                            "id": "add",
                            "title": "Add More Items"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "clear",
                            "title": "Cancel or clear cart"
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
                "text": "Please choose your Language"
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
                                "id": "food",
                                "title": messages.optmsgs["title1"][language],
                                "description": messages.optmsgs["desc1"][language]
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



def send_food_category(recipient_phone_number):
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
                "text": "Please choose from the list or directly type your order in the chat"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "VFC",
                            "title": "Vegetables & Fruits"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "GBC",
                            "title": "Groceries & Bakeries"
                        }
                    },
                      {
                        "type": "reply",
                        "reply": {
                            "id": "MFC",
                            "title": "Meat & Fish"
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