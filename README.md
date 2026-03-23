
# 🌍 Travel_Reco - AI-Powered Travel Planning Assistant

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-lightgrey.svg)](https://flask.palletsprojects.com/)
[![AI](https://img.shields.io/badge/AI-LLM%20Integration-orange.svg)]()
[![API](https://img.shields.io/badge/API-Unsplash-green.svg)](https://unsplash.com/)

**Travel_Reco** is an intelligent travel planning platform that uses AI to recommend destinations, generate itineraries, and provide personalized travel insights based on user preferences like budget, group size, and travel style.

It simplifies trip planning by turning complex decisions into **smart, AI-driven suggestions**.

---

## ✨ Core Capabilities

Travel_Reco transforms user input into actionable travel plans through intelligent AI workflows:

| Feature | Description | Powered By |
| :--- | :--- | :--- |
| **📍 State Recommendation** | Suggests best Indian states based on user preferences | LLM |
| **🏝️ Place Discovery** | Recommends tourist destinations with descriptions | LLM |
| **🧾 Smart Itinerary** | Generates day-wise travel plans | LLM |
| **💸 Budget Estimation** | Provides approximate trip cost breakdown | AI Logic |
| **🖼️ Image Integration** | Fetches destination visuals dynamically | Unsplash API |
| **🗺️ Map Navigation** | Direct Google Maps access for locations | Google Maps |

---

## 🧠 AI System Overview

The AI engine handles:

- Context-based travel recommendations  
- Natural language description generation  
- Itinerary creation  
- Budget estimation  

### Sample Prompt


Travel_Reco is an intelligent travel planning platform that uses AI to
recommend destinations, generate itineraries, and provide personalized
travel insights based on user preferences like budget, group size, and
travel style.

It simplifies trip planning by turning complex decisions into smart,
AI-driven suggestions.

User Details:
Budget: {budget}
Members: {members}
Travel Type: {type}
Duration: {days}

Suggest 3 best Indian states with reasons.

------------------------------------------------------------------------

## ✨ Core Capabilities
Travel_Reco transforms user input into actionable travel plans through intelligent AI workflows:

| Feature | Description | Powered By |
| :--- | :--- | :--- |
| **📍 State Recommendation** | Suggests best Indian states based on user preferences | LLM |
| **🏝️ Place Discovery** | Recommends tourist destinations with descriptions | LLM |
| **🧾 Smart Itinerary** | Generates day-wise travel plans | LLM |
| **💸 Budget Estimation** | Provides approximate trip cost breakdown | AI Logic |
| **🖼️ Image Integration** | Fetches destination visuals dynamically | Unsplash API |
| **🗺️ Map Navigation** | Direct Google Maps access for locations | Google Maps |


------------------------------------------------------------------------


## 🛠️ Technology Stack

| Layer        | Technology              | Description |
|-------------|------------------------|-------------|
| **Backend**  | Python, Flask          | Handles server logic, routing, and API integration |
| **Frontend** | HTML5, CSS3, Bootstrap | Builds responsive and user-friendly interface |
| **AI Engine**| LLM APIs (Grok/Gemini) | Generates recommendations, itineraries, and insights |
| **Database** | SQLite                 | Stores user data and session information |
| **Images**   | Unsplash API           | Fetches dynamic travel images |
| **Maps**     | Google Maps            | Provides location navigation and map integration |

------------------------------------------------------------------------

## 📂 Project Structure

```text
Travel_Reco/
├── app.py              # Main Flask application
├── models.py           # Database models
├── database.db         # SQLite database
│
├── templates/          # HTML pages
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── recommendations.html
│   ├── place.html
│
├── static/             # CSS, JS, Images
│
├── utils/              # AI & API logic
│   ├── ai.py
│   ├── image_api.py
│
└── README.md
```
-----------------------------------------------------------------------


## Prerequisites

- Python 3.x  
- API Keys
     -Groq API key
     -Unplash Access key
     -Unplash Secret key
     -Secret key  

-----------------------------------------------------------------------


### Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SAQIB-dev7447/Travel_Reco.git
   cd Travel_Reco
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3.**Configure Environment Variables**:
Create a `.env` file in the root dirctory:
```env
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key (optional)
UNSPLASH_API_KEY=your_key
```

4.**Run the Application**
```bash
python app.py
```
Open: http://127.0.0.1:5000
---
