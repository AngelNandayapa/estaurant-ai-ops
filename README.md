# 🍽️ Restaurant AI Intelligence System

> An AI-powered operations platform that gives restaurant owners complete financial visibility — from automated expense parsing to predictive inventory management — through a simple Telegram interface.

**Built with Python · Gemini LLM · Google Sheets API · Telegram Bot API**

---

## 📊 Results

| Metric | Before | After |
|---|---|---|
| Manual accounting time per receipt | ~5 min | ~3 sec |
| Overall accounting overhead | Baseline | **↓ 80%** |
| Data entry errors | Manual / error-prone | Near-zero (AI-parsed) |
| Financial visibility | Spreadsheets updated weekly | Real-time, automatic |

---

## 🧠 What This System Does

Most restaurants run on gut instinct and manual spreadsheets. This system replaces that with an always-on AI layer that reads receipts, tracks sales, monitors inventory, and tells the owner exactly what to buy this week — all through Telegram.

```
Owner sends a photo of a receipt
        ↓
Gemini LLM extracts structured data
        ↓
Data injected into Google Sheets in real time
        ↓
System updates inventory, tracks margins, flags anomalies
        ↓
Weekly purchase recommendations generated automatically
```

---

## 🗺️ System Roadmap

### ✅ Phase 1 — Expense Tracker (Complete)
Automated receipt and invoice parsing with real-time Google Sheets injection.

- Send any receipt or invoice photo to the Telegram bot
- Gemini LLM extracts vendor, amount, category, date into structured JSON
- Data injected into Google Sheets via gspread API in real time
- Asynchronous Long Polling with robust error handling and secure credential management
- **Result:** 80% reduction in manual accounting time

### 🔄 Phase 2 — Income Tracker (In Progress)
Record and categorize every sale so the restaurant knows exactly what's coming in.

- Log daily sales by product or category through Telegram
- Automatic revenue summaries by day, week, and month
- Income vs. expense balance tracked in real time
- Gross margin calculation per product

### 🔮 Phase 3 — Inventory Management (Planned)
Real-time stock level tracking tied directly to sales and purchases.

- Inventory levels updated automatically when expenses (purchases) are logged
- Stock depletion tracked against sales velocity
- Low-stock alerts sent via Telegram before items run out
- Full audit trail of inventory movements

### 🔮 Phase 4 — Sales Prediction (Planned)
ML-powered forecasting so the restaurant knows what will sell next week.

- Time-series forecasting per product using historical sales data
- Day-of-week and seasonal pattern recognition
- Demand spike detection for events or promotions
- Confidence intervals on all predictions

### 🔮 Phase 5 — Purchase Optimization (Planned)
Closes the loop: tells the owner exactly what to buy, how much, and when.

- Weekly purchase recommendations generated every Sunday
- Quantities calculated from predicted demand + current inventory
- Cost optimization across suppliers
- Delivered automatically via Telegram — no dashboard needed

---

## 🏗️ Architecture

```
telegram/           # Bot interface and message handlers
  bot.py            # Main bot logic and Long Polling
integrations/       # External service connectors
  sheets.py         # Google Sheets read/write via gspread
  gemini.py         # Gemini LLM prompt pipeline
core/               # Business logic modules
  expense_tracker.py    # Phase 1 ✅
  income_tracker.py     # Phase 2 🔄
  inventory.py          # Phase 3 🔮
ml/                 # Machine learning modules
  sales_prediction.py   # Phase 4 🔮
  purchase_optimizer.py # Phase 5 🔮
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Google Gemini 2.5 Flash |
| Prompt Engineering | Chain-of-Thought, System Prompt Design |
| Backend | Python 3.11+ |
| Async Execution | Long Polling (pyTelegramBotAPI) |
| Data Layer | Google Sheets via gspread + pandas |
| Bot Interface | Telegram Bot API |
| Auth / Security | Service Account JSON, .env credential management |
| ML (Phase 4-5) | pandas, scikit-learn (planned) |

---

## 🚀 Setup

### Prerequisites
- Python 3.11+
- Google Cloud project with Sheets API enabled
- Gemini API key
- Telegram Bot token (via @BotFather)

### Installation

```bash
git clone https://github.com/AngelNandayapa/ai-expense-tracker-bot.git
cd ai-expense-tracker-bot
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

Fill in your `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here
GOOGLE_SHEET_ID=your_sheet_id_here
```

Add your Google service account JSON key as `credentials.json` in the root directory.

### Run

```bash
python bot.py
```

---

## 🔒 Security

- No API keys or credentials are ever committed to this repository
- All secrets managed via `.env` and service account JSON (both in `.gitignore`)
- `.env.example` provided as a safe template

---

## 👤 Author

**Angel Nandayapa**
AI Automation Engineer · Software Developer
Monterrey, NL, Mexico

[LinkedIn](https://linkedin.com/in/angelnandayapa) · [GitHub](https://github.com/AngelNandayapa)

---

## 📄 License

MIT License — feel free to fork and adapt for your own restaurant or SMB use case.
