import json


multilingual_messages = {

    "language_selection": {
        "en": "Please choose your Language",
        "ml": "ദയവായി നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക"
    },

    "order_confirmation":{ "en":"Please confirm your Order",
                          "ml":"ദയവായി നിങ്ങളുടെ ഓർഡർ സ്ഥിരീകരിക്കുക"},


    "location_request":  {
        "en": "Please share your location",
        "ml": "ദയവായി നിങ്ങളുടെ ലൊക്കേഷൻ പങ്കുവെക്കൂ"
    },


    "price_list_intro": { 
        "en": "Please check our price list.\n"
        "You may type  your order or choose from the store \n\n"
        "eg :thakkali 1kg \n"
        ,
        "ml": "ദയവായി വിലപ്പട്ടിക പരിശോധിക്കൂ. \n"
        "ഓർഡർ ടൈപ്പ് ചെയ്യുകയോ സ്റ്റോറിൽ നിന്ന് തിരഞ്ഞെടുക്കുകയോ ചെയ്യാം \n\n"
        "eg : savala 1kg "
    }
        
    ,
    "ordersuccess":{"en": "Your order will be in your doors within 20 minutes.",
                    "ml":"നിങ്ങളുടെ ഓർഡർ 20 മിനിറ്റിനകം നിങ്ങൾക്ക് ലഭിക്കും."}
}

optmsgs = {
   
   "rest_title":{
       "en": "Have a yummy day 🍟🍔🍗😄",
        "ml": "Have a yummy day 🍟🍔🍗😄"
   },
   "see_more_rest":{
       "en": "See more restaurants",
        "ml": "കൂടുതൽ ഹോട്ടലുകൾ കാണുക"
   },
    "header": {
        "en": "🛒 Please pick your Order 🔎",
        "ml": "🛒 ദയവായി നിങ്ങളുടെ ഓർഡർ തിരഞ്ഞെടുക്കുക🔎"
    },
    "body": {
        "en": "Market items are listed here",
        "ml": "മാർക്കറ്റ് വസ്തുക്കൾ ഇവിടെ ലിസ്റ്റ് ചെയ്‌തിരിക്കുന്നു"
    },"food_body": {
        "en": "Restaurants are listed here 🍽   \n ",
        "ml": "റെസ്റ്റോറന്റ്സ്  ഇവിടെ ലിസ്റ്റ് ചെയ്‌തിരിക്കുന്നു  🍽 "
    },
    "footer": {
        "en": "Powered by അങ്ങാടി",
        "ml": "Powered by അങ്ങാടി"
    },
    "button": {
        "en": "Our Services ",
        "ml": "ഞങ്ങളുടെ സേവനങ്ങൾ"
    },

     "button_rest": {
        "en": "Our 🍔🍕🍟 ",
        "ml": "ഞങ്ങളുടെ 🍔🍕🍟"
    },
    "title1": {
        "en": "Food🍔🍕🍟",
        "ml": "ഫൂഡ്🍔🍕🍟"
    },
    "title2": {
        "en": "Medicine💊🏥",
        "ml": "മരുന്ന്💊🏥"
    },
    "desc1": {
        "en": "Groceries, vegetables, fruits, meat",
        "ml": "Groceries, vegetables, fruits, meat"
    },
    "desc2": {
        "en": "Medicines with valid prescription",
        "ml": "Medicines with valid prescription"
    },"snacks": {
        "en": "Snacks  🥯",
        "ml": "കടികൾ  🥯"
    },
    "bakeries": {
        "en": " Bakeries 🥯🧁",
        "ml": "ബേക്കറി 🥯🧁"
    }
}

button_names = {"mwbody": {
        "en": "Please choose from the list or directly type your order in the chat",
        "ml": "ദയവായി പട്ടികയിൽ നിന്നെന്തെങ്കിലും തിരഞ്ഞെടുക്കുക അല്ലെങ്കിൽ നിങ്ങളുടെ ഓർഡർ നേരിട്ട് ചാറ്റിൽ ടൈപ്പ് ചെയ്യുക"
    },"conforder": {
        "en": "Confirm your Order",
        "ml": "നിങ്ങളുടെ ഓർഡർ സ്ഥിരീകരിക്കുക"
    },
    "vfc": {
        "en": "Vegetables & Fruits",
        "ml": "പച്ചക്കറികളും ഫലങ്ങളും"
    },
    "gfc": {
        "en": "Grains and Bakeries",
        "ml": "ധാന്യങ്ങളും ബേക്കറിയുകളും"
    },
    "mfc": {
        "en": "Meat🥩🍖",
        "ml": "ഇറച്ചി🥩🍖"
    },
    "veg": {
        "en": "Vegetables🍅🫑🥒",
        "ml": "പച്ചക്കറികൾ🍅🫑🥒"
    },
    "fr": {
        "en": "Fruits🍍🥑🍇🥭",
        "ml": "ഫലങ്ങൾ🍍🥑🍇🥭"
    },
    "back": {
        "en": "Back",
        "ml": "തിരികെ"
    },
    "gr": {
        "en": "Masala Shop🛒",
        "ml": "മസാല പീടിക🛒"
    },
    "bsc": {
        "en": "Bakeries & Snacks",
        "ml": "ബേക്കറിയുകളും സ്നാക്കുകളും"
    },
    "bkry": {
        "en": "Bakeries",
        "ml": "ബേക്കറികൾ"
    },
    "snks": {
        "en": "Snacks",
        "ml": "കടികൾ "
    },
     "mt": {
        "en": "Chickem Beef Mutton🥩🍖",
        "ml": "ചിക്കൻ ബീഫ് മട്ടൻ🥩🍖"
    },
     "fish": {
        "en": "Fish🦈🐟",
        "ml": "മീൻ 🦈🐟 "
    },

"prcd": {
    "en": "Proceed",
    "ml": "മുന്നോട്ട് പോകുക"
},

"additem": {
    "en": "Add more items",
    "ml": "കൂടുതൽ  ചേർക്കുക"
},

"clr": {
    "en": "ff",
    "ml": "ff"
},

"rest": {
    "en": "Food🍔🍕🍟",
    "ml": "ഫുഡ്🍔🍕🍟"
}

}

othrs={
 "notes":{
  "en":"Please add your notes if any else type anything to move on",
  "ml":"ഒരു കുറിപ്പുണ്ടെങ്കിൽ ദയവായി ചേർക്കുക, അല്ലെങ്കിൽ മുന്നോട്ടുപോക کچھെനെങ്കിലും ടൈപ്പ് ചെയ്യുക"
 }
}

location = {
    "title": {
        "en": "As you confirmed the order pls share your location",
        "ml": "നിങ്ങളുടെ ഓർഡർ സ്ഥിരീകരിച്ചതിനാൽ ദയവായി നിങ്ങളുടെ ലൊക്കേഷൻ ഷെയർ ചെയ്യൂ"
    }
}


def po_template(user_session,order_id=None):
 ont1=f""" Order No:{order_id}  
  {user_session['bill']}

📍 *Location Links:*
🔗 [Google Maps]({user_session['location']['google']})

"""
 ont2=f""" Order No:{order_id}  
  {user_session['bill']}

📍 *Location Links:*
🔗 [Google Maps]({user_session['location']['google']})

Phone number: {user_session.get('number')[2:]}
Special Notes: {user_session['notes']}

"""
 return ont2 if order_id else ont2


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