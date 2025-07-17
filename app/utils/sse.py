import queue
import json
from flask import Response

clients = []

def get_clients():
    return clients

def event_stream(q):
    while True:
        data = q.get()
        yield f"data: {json.dumps(data)}\n\n"

def register_sse_endpoint(app):
    @app.route("/events")
    def sse():
        q = queue.Queue()
        clients.append(q)
        return Response(event_stream(q), mimetype="text/event-stream")
