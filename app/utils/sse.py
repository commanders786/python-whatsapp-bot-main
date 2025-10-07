import queue
import json
import time
import logging
from flask import Response, make_response

clients = []
MAX_CLIENTS = 10  # cap concurrent SSE clients to avoid thread exhaustion

def get_clients():
    return clients

def event_stream(q):
    try:
        while True:
            try:
                # Non-blocking wait; send heartbeat on timeout
                data = q.get(timeout=10)
                yield f"data: {json.dumps(data)}\n\n"
            except queue.Empty:
                # Comment line as heartbeat; keeps connection alive without consuming threads forever
                yield ": heartbeat\n\n"
    finally:
        # On client disconnect, remove the queue if present
        try:
            clients.remove(q)
        except ValueError:
            pass

def register_sse_endpoint(app):
    @app.route("/events")
    def sse():
        # Enforce a max-clients limit to prevent thread starvation
        if len(clients) >= MAX_CLIENTS:
            logging.warning("SSE client limit reached: %s", len(clients))
            resp = make_response("Too many SSE clients", 503)
            resp.headers["Retry-After"] = "10"
            return resp

        q = queue.Queue()
        clients.append(q)
        # Recommended headers for SSE
        response = Response(event_stream(q), mimetype="text/event-stream")
        response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Accel-Buffering"] = "no"  # disable proxy buffering if any
        return response
