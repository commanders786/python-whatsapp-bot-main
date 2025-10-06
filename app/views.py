# import logging
# import json
# from .sessions import user_sessions
# from flask import Blueprint, request, jsonify, current_app

# from .decorators.security import signature_required
# from .utils.whatsapp_utils import (
#     process_whatsapp_message,
#     is_valid_whatsapp_message,
# )



# webhook_blueprint = Blueprint("webhook", __name__)


# def handle_message():
#     """
#     Handle incoming webhook events from the WhatsApp API.

#     This function processes incoming WhatsApp messages and other events,
#     such as delivery statuses. If the event is a valid message, it gets
#     processed. If the incoming payload is not a recognized WhatsApp event,
#     an error is returned.

#     Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

#     Returns:
#         response: A tuple containing a JSON response and an HTTP status code.
#     """
#     body = request.get_json()

#     # logging.info(f"request body: {body}")

#     # Check if it's a WhatsApp status update
#     if (
#         body.get("entry", [{}])[0]
#         .get("changes", [{}])[0]
#         .get("value", {})
#         .get("statuses")
#     ):
#         logging.info("Received a WhatsApp status update.")
#         return jsonify({"status": "ok"}), 200

#     try:
#         if is_valid_whatsapp_message(body):
#             print(body)
#             process_whatsapp_message(body)
#             return jsonify({"status": "ok"}), 200
#         else:
#             # if the request is not a WhatsApp API event, return an error
#             return (
#                 jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
#                 404,
#             )
#     except json.JSONDecodeError:
#         logging.error("Failed to decode JSON")
#         return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


# # Required webhook verifictaion for WhatsApp
# def verify():
#     # Parse params from the webhook verification request
#     mode = request.args.get("hub.mode")
#     token = request.args.get("hub.verify_token")
#     challenge = request.args.get("hub.challenge")
#     # Check if a token and mode were sent
#     if mode and token:
#         # Check the mode and token sent are correct
#         if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
#             # Respond with 200 OK and challenge token from the request
#             logging.info("WEBHOOK_VERIFIED")
#             return challenge, 200
#         else:
#             # Responds with '403 Forbidden' if verify tokens do not match
#             logging.info("VERIFICATION_FAILED")
#             return jsonify({"status": "error", "message": "Verification failed"}), 403
#     else:
#         # Responds with '400 Bad Request' if verify tokens do not match
#         logging.info("MISSING_PARAMETER")
#         return jsonify({"status": "error", "message": "Missing parameters"}), 400


# @webhook_blueprint.route("/webhook", methods=["GET"])
# def webhook_get():
#     return verify()

# @webhook_blueprint.route("/webhook", methods=["POST"])
# @signature_required
# def webhook_post():
#     return handle_message()


import logging
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from flask import Blueprint, request, jsonify, current_app

from .sessions import user_sessions
from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

# ----------------------------------------------------------------------
# 🌟 Executor setup — handle WhatsApp messages asynchronously
# ----------------------------------------------------------------------
MAX_WORKERS = 10
QUEUE_LIMIT = 50

executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def monitor_queue_depth():
    """Logs current background task queue depth every 2 seconds."""
    import time
    while True:
        depth = executor._work_queue.qsize()
        if depth > 0:
            logging.warning(f"⚠️ Task queue depth is {depth}")
        time.sleep(2)

# Start monitoring thread (daemon → exits with main app)
threading.Thread(target=monitor_queue_depth, daemon=True).start()

# ----------------------------------------------------------------------
# 🌟 Flask Blueprint
# ----------------------------------------------------------------------
webhook_blueprint = Blueprint("webhook", __name__)

# ----------------------------------------------------------------------
# ✅ Handle WhatsApp webhook POST (main logic)
# ----------------------------------------------------------------------
def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API asynchronously.
    """
    body = request.get_json()

    # 1️⃣ Check for WhatsApp status updates (sent/delivered/read)
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    # 2️⃣ Process actual messages
    try:
        if is_valid_whatsapp_message(body):
            current_depth = executor._work_queue.qsize()

            # Protect against overload
            if current_depth > QUEUE_LIMIT:
                logging.warning(
                    f"⚠️ Queue overloaded ({current_depth}). Rejecting new request temporarily."
                )
                return jsonify({"status": "busy"}), 429

            # Submit task to background thread
            executor.submit(process_whatsapp_message, body)
            logging.info("✅ Message queued for background processing.")

            # Respond instantly to WhatsApp
            return jsonify({"status": "queued"}), 200

        else:
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )

    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


# ----------------------------------------------------------------------
# ✅ Webhook verification (GET)
# ----------------------------------------------------------------------
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            logging.warning("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        logging.warning("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


# ----------------------------------------------------------------------
# 🌟 Routes
# ----------------------------------------------------------------------
@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()


@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()
