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
    "header": {
        "en": "Please pick your Order",
        "ml": "ദയവായി നിങ്ങളുടെ ഓർഡർ തിരഞ്ഞെടുക്കുക"
    },
    "body": {
        "en": "Market items are listed here",
        "ml": "മാർക്കറ്റ് വസ്തുക്കൾ ഇവിടെ പട്ടികപ്പെടുത്തിയിരിക്കുന്നു"
    },
    "footer": {
        "en": "Powered by Aghadi",
        "ml": "അഘാടിയുടെ പിന്തുണയോടെ"
    },
    "button": {
        "en": "Our Services ",
        "ml": "ഞങ്ങളുടെ സേവനങ്ങൾ"
    },
    "title1": {
        "en": "Food",
        "ml": "ഫൂഡ്"
    },
    "title2": {
        "en": "Medicine",
        "ml": "മരുന്ന്"
    },
    "desc1": {
        "en": "Groceries, vegetables, fruits, meat",
        "ml": "Groceries, vegetables, fruits, meat"
    },
    "desc2": {
        "en": "Medicines with valid prescription",
        "ml": "Medicines with valid prescription"
    }
}

button_names = {
    "vfc": {
        "en": "Vegetables & Fruits",
        "ml": "പച്ചക്കറികളും ഫലങ്ങളും"
    },
    "gfc": {
        "en": "Grains and Bakeries",
        "ml": "ധാന്യങ്ങളും ബേക്കറിയുകളും"
    },
    "mfc": {
        "en": "Meat & Fish",
        "ml": "മാംസവും മീനും"
    },
    "veg": {
        "en": "Vegetables",
        "ml": "പച്ചക്കറികൾ"
    },
    "fr": {
        "en": "Fruits",
        "ml": "ഫലങ്ങൾ"
    },
    "back": {
        "en": "Back",
        "ml": "തിരികെ"
    },
    "grains": {
        "en": "Grains",
        "ml": "ധാന്യങ്ങൾ"
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

"""
 return ont2 if order_id else ont2