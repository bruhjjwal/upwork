# E-Commerce AI Shopping Assistant

An AI-powered chatbot that helps customers find products from an e-commerce catalog. Built with Python (Gemini 2.5 Flash) and deployed on Vercel.

## Demo Questions

Try asking:
- "Do you have red shoes under $50?"
- "What sizes are available for sneakers?"
- "Show me women's accessories"
- "What's the cheapest jacket you have?"

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Google Gemini 2.5 Flash |
| Backend | Python (Vercel Serverless Function) |
| Frontend | HTML / CSS / JavaScript |
| Data | JSON file (20 products) |
| Hosting | Vercel (free tier) |

## Project Structure

```
├── api/
│   └── chat.py          # Backend — handles chat via Gemini API
├── products.json         # Product catalog (20 items)
├── index.html            # Chatbot UI
├── style.css             # Styling (minimal B&W theme)
├── script.js             # Frontend logic
├── vercel.json           # Vercel deployment config
├── requirements.txt      # Python dependencies
└── README.md
```

## Setup Instructions

### 1. Prerequisites
- A [Vercel](https://vercel.com) account (free)
- A Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### 2. Deploy to Vercel

**Option A: Via Vercel CLI**
```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to project directory
cd upwork2

# Deploy
vercel

# Set the Gemini API key as an environment variable
vercel env add GEMINI_API_KEY
# Paste your API key when prompted

# Redeploy with the env variable
vercel --prod
```

**Option B: Via GitHub**
1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project → select the repo
3. In Settings → Environment Variables, add:
   - Key: `GEMINI_API_KEY`
   - Value: your Gemini API key
4. Click Deploy

### 3. Test Locally (Optional)

To test the frontend locally without the backend:
```bash
# Simple HTTP server
python3 -m http.server 3000
```
Then open `http://localhost:3000` (API calls won't work locally without Vercel dev).

To test with full backend:
```bash
vercel dev
```

## How It Works

1. User types a question in the chat interface
2. Frontend sends the message + conversation history to `/api/chat`
3. Backend loads the product catalog from `products.json`
4. The full catalog is included in the system prompt sent to Gemini
5. Gemini analyzes the question against the catalog and returns a relevant answer
6. The response is displayed in the chat interface

## Product Catalog

The catalog includes 20 products across 3 categories:
- **Shoes** (7): Sneakers, formal, athletic, boots, casual, sandals
- **Clothing** (7): Jeans, t-shirts, outerwear, dresses, shirts, activewear
- **Accessories** (6): Bags, eyewear, scarves, watches, hats

Each product has: title, category, brand, colors, sizes, price, description, material, and gender.

## Extending the Catalog

To add products, simply edit `products.json` following the existing format:
```json
{
  "id": 21,
  "title": "Product Name",
  "category": "shoes",
  "subcategory": "sneakers",
  "brand": "BrandName",
  "colors": ["red", "blue"],
  "sizes": ["S", "M", "L"],
  "price": 49.99,
  "description": "Product description here.",
  "in_stock": true,
  "material": "cotton",
  "gender": "unisex"
}
```
