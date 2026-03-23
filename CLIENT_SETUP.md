# Travel AI App - Installation Guide for Client Laptop

This guide explains how to install and run the Travel AI application on a new laptop.

## Prerequisites
1. Download and install Python from https://www.python.org/downloads/
2. **Important for Windows:** During the Python installation, make sure to check the box that says "Add Python to PATH" before hitting install.

---

## Step-by-Step Installation

### Step 1: Copy the Project
Move or copy the entire `travel_ai_app` folder onto the client's laptop (e.g., via USB drive, Google Drive, or GitHub).

### Step 2: Open the Terminal / Command Prompt
1. Open Command Prompt (Windows) or Terminal (Mac/Linux).
2. Navigate to the folder where you placed the project:
   cd path\to\travel_ai_app

### Step 3: Create a Virtual Environment
This creates an isolated environment for the project's dependencies.
- On Windows:
  python -m venv venv
- On Mac/Linux:
  python3 -m venv venv

### Step 4: Activate the Virtual Environment
- On Windows:
  venv\Scripts\activate
- On Mac/Linux:
  source venv/bin/activate
(You should now see `(venv)` appear at the beginning of your terminal line.)

### Step 5: Install Dependencies
Install all the required Python libraries for the app to work:
- pip install -r requirements.txt

### Step 6: Set Up Environment Variables (API Keys)
1. In the project folder, locate the `.env` file. (If you only see an `.env.example` file, make a copy of it and rename the copy to `.env`).
2. Open the `.env` file in Notepad or another text editor.
3. Ensure the API keys are present and correct:
   GROQ_API_KEY=your_groq_key_here
   UNSPLASH_ACCESS_KEY=your_unsplash_key_here
   UNSPLASH_SECRET_KEY=your_unsplash_secret_here
   SECRET_KEY=some_random_string_here

### Step 7: Run the Application
Start the Flask server with the following command:
- python app.py

### Step 8: Access the App
Open any web browser (Chrome, Edge, Safari) and go to:
http://127.0.0.1:5000

---

## Additional Notes
- **Database Reset:** The app uses an SQLite database (`instance/database.db`) which stores user accounts and saved trips. If you want the client to start with a completely fresh, empty database, delete the `instance/database.db` file from the folder before giving it to them. The app will automatically create a brand new, empty database the first time you run `python app.py`.
