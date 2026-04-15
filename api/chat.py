from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

# Load products once at module level (cold start)
PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'products.json')
with open(PRODUCTS_PATH, 'r') as f:
    PRODUCTS = json.load(f)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = 'gemini-2.5-flash'
GEMINI_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}'

# Build product catalog string for the prompt
def build_catalog_context():
    lines = []
    for p in PRODUCTS:
        lines.append(
            f"- ID:{p['id']} | {p['title']} | Category: {p['category']}/{p['subcategory']} | "
            f"Brand: {p['brand']} | Colors: {', '.join(p['colors'])} | "
            f"Sizes: {', '.join(p['sizes'])} | Price: ${p['price']} | "
            f"Material: {p['material']} | Gender: {p['gender']} | "
            f"In Stock: {p['in_stock']} | {p['description']}"
        )
    return "\n".join(lines)

CATALOG = build_catalog_context()

SYSTEM_PROMPT = f"""You are a helpful e-commerce shopping assistant. You help customers find products from our catalog.

Here is our complete product catalog:
{CATALOG}

Instructions:
- Answer questions about products based ONLY on the catalog above.
- When customers ask about products, search through the catalog and provide relevant matches.
- Include product details like price, available colors, sizes, and description when recommending products.
- If no products match the customer's query, politely let them know and suggest alternatives from the catalog.
- Be concise, friendly, and helpful.
- Format prices with $ sign.
- If asked about something outside of product questions, politely redirect to how you can help them shop.
- When listing multiple products, format them in a clear, readable way.
- Do NOT invent products that are not in the catalog."""


def call_gemini(user_message, conversation_history):
    """Call Gemini API with conversation history."""
    
    contents = []
    
    # Add conversation history
    for msg in conversation_history:
        contents.append({
            "role": msg["role"],
            "parts": [{"text": msg["content"]}]
        })
    
    # Add current user message
    contents.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    
    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1024
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        GEMINI_URL,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    # Extract text from Gemini response
    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError):
        return "I'm sorry, I couldn't process that request. Could you try rephrasing your question?"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            user_message = data.get('message', '')
            conversation_history = data.get('history', [])
            
            if not user_message.strip():
                self._send_json(400, {"error": "Message cannot be empty"})
                return
            
            if not GEMINI_API_KEY:
                self._send_json(500, {"error": "Gemini API key not configured"})
                return
            
            reply = call_gemini(user_message, conversation_history)
            self._send_json(200, {"reply": reply})
            
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON in request body"})
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            self._send_json(502, {"error": f"Gemini API error: {error_body}"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
