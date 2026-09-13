"""最小可运行的匹配 API 原型。正式版需替换为数据库、鉴权和 WebSocket。"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

queue = []
rooms = {}

class Api(BaseHTTPRequestHandler):
    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/match/queue":
            queue.append(data)
            play = data.get("play", "刚枪")
            matched = [p for p in queue if p.get("play") == play]
            self.send_json({"queued": True, "matches": matched[:4]})
        elif self.path == "/rooms":
            room_id = str(len(rooms) + 1)
            rooms[room_id] = {"id": room_id, "members": [data]}
            self.send_json(rooms[room_id], 201)
        else:
            self.send_json({"error": "not found"}, 404)

    def do_GET(self):
        if self.path == "/match/results":
            self.send_json({"matches": queue[-4:]})
        elif self.path.startswith("/rooms/"):
            self.send_json(rooms.get(self.path.rsplit("/", 1)[-1], {}))
        else:
            self.send_json({"error": "not found"}, 404)

if __name__ == "__main__":
    print("吃鸡搭子 API running at http://localhost:8787")
    HTTPServer(("0.0.0.0", 8787), Api).serve_forever()
