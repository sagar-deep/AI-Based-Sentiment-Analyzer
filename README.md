# Sentiment AI (AI-Based Sentiment Analyzer)

> **Internship Project** | Flask · HuggingFace Transformers · MongoDB · Matplotlib

Analyzes social media posts and product reviews using a fine-tuned RoBERTa model to
predict **Positive**, **Negative**, or **Neutral** sentiment with a confidence score.
All results are persisted to MongoDB and visualized with interactive charts.

---

## 📸 Features

| Feature | Details |
|---|---|
| **Sentiment Prediction** | POSITIVE / NEGATIVE / NEUTRAL via RoBERTa |
| **Confidence Score** | Per-class probability scores (0–100%) |
| **Source Tagging** | Tag texts as Manual / Social Media / Product Review |
| **MongoDB Storage** | Every analysis persisted with timestamp |
| **Pie Chart** | Sentiment distribution across all analyses |
| **Bar Chart** | Daily analysis volume (last 7 days) |
| **History Page** | Filterable table of all past analyses |
| **Delete Records** | Remove individual records from the DB |
| **Responsive UI** | Mobile-first dark theme |

---

## Project Structure

```
sentiment_analyzer/
│
├── app.py                  # Flask application — routes & startup
│
├── models/
│   ├── __init__.py
│   └── sentiment_model.py  # HuggingFace inference wrapper
│
├── utils/
│   ├── __init__.py
│   ├── db.py               # MongoDB CRUD operations
│   ├── chart_generator.py  # Matplotlib → base64 PNG charts
│   └── helpers.py          # Sanitization, formatting utilities
│
├── templates/
│   ├── index.html          # Analyzer page
│   └── history.html        # History & reports page
│
├── static/
│   ├── css/style.css       # Dark-theme responsive stylesheet
│   └── js/
│       ├── main.js         # Analyzer page interactions
│       └── history.js      # History filtering & delete
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # This file
```

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- MongoDB 6.0+ (local or Atlas)
- pip (Python package manager)
- Git

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/sentiment-analyzer.git
cd sentiment-analyzer
```

---

### Step 2 — Create a Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (Linux / macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> This will download the HuggingFace model (~500 MB) on first run.
> Subsequent runs use the local cache.

---

### Step 4 — Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed:

```env
MONGO_URI=mongodb://localhost:27017/   # your MongoDB URI
MONGO_DB=sentiment_db                  # database name
SECRET_KEY=change_me_in_production
```

> If MongoDB is unavailable, the app falls back to an **in-memory store** automatically.
> Data will not persist between restarts in fallback mode.

---

### Step 5 — Start MongoDB

```bash
# Linux / macOS (if installed via package manager)
sudo systemctl start mongod

# macOS (Homebrew)
brew services start mongodb-community

# Windows — start MongoDB service from Services panel or:
net start MongoDB
```

Or use **MongoDB Atlas** — just set your `MONGO_URI` to the connection string.

---

### Step 6 — Run the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Usage

### Analyze Text

1. Open **http://localhost:5000**
2. Select a source tab: Manual Input, Social Media, or Product Review
3. Type or paste any text (up to 1000 characters)
4. Click **Analyze Sentiment** or press `Ctrl+Enter`
5. View the result — label, confidence, and per-class breakdown

### View History

1. Click **History** in the navigation bar
2. Browse all stored analyses in the table
3. Filter by text or sentiment label
4. View the Sentiment Distribution (pie) and Daily Volume (bar) charts

---

## Model Details

| Property | Value |
|---|---|
| **Model** | `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| **Architecture** | RoBERTa-base fine-tuned on Twitter data |
| **Classes** | POSITIVE, NEGATIVE, NEUTRAL |
| **Max Input** | 512 tokens (truncated) |
| **Fallback** | `distilbert-base-uncased-finetuned-sst-2-english` |

---

## MongoDB Schema

Each document in the `analyses` collection:

```json
{
  "_id":        "ObjectId",
  "text":       "string — input text",
  "label":      "POSITIVE | NEGATIVE | NEUTRAL",
  "confidence": 0.9731,
  "all_scores": {
    "POSITIVE": 0.9731,
    "NEGATIVE": 0.0142,
    "NEUTRAL":  0.0127
  },
  "timestamp":  "2024-11-15T10:30:00.000Z",
  "source":     "manual | twitter | amazon"
}
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET`  | `/`              | Analyzer page |
| `POST` | `/analyze`       | Run inference; store & return result |
| `GET`  | `/history`       | History page with charts |
| `GET`  | `/api/history`   | JSON list of recent analyses |
| `GET`  | `/api/stats`     | JSON aggregate stats |
| `DELETE` | `/delete/<id>` | Delete a record by MongoDB `_id` |

**POST /analyze — Request:**
```json
{ "text": "This product is amazing!", "source": "amazon" }
```

**POST /analyze — Response:**
```json
{
  "id":         "673abc123def",
  "text":       "This product is amazing!",
  "label":      "POSITIVE",
  "confidence": "97.31%",
  "all_scores": { "POSITIVE": 97.31, "NEGATIVE": 1.42, "NEUTRAL":  1.27 }
}
```

---

## Technologies Used

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| NLP Model | HuggingFace Transformers, PyTorch |
| Database | MongoDB 6, PyMongo |
| Charts | Matplotlib |
| Frontend | HTML5, CSS3, Vanilla JS |
| Fonts | Google Fonts (Inter, Space Grotesk) |

---

## Internship Notes

This project was developed as part of an internship program to demonstrate:

- Integration of pre-trained NLP models into a production web app
- RESTful API design with Flask
- NoSQL database operations with MongoDB
- Data visualization and reporting
- Responsive UI/UX design without a frontend framework
- Clean project structure with documentation and comments

---
