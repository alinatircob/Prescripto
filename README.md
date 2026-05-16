# 💊 Prescripto - Medical Assistant & Prescription Translator 

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange)
![Google Cloud Vision](https://img.shields.io/badge/Google%20Cloud-Vision%20API-blue)
![Google Calendar](https://img.shields.io/badge/Google%20Calendar-API-success)
![Pydantic](https://img.shields.io/badge/Pydantic-Data%20Validation-blueviolet)

**Prescripto** is an innovative web application designed to translate, validate, and schedule medical treatment plans. Starting from a simple photo of a prescription (no matter how illegible the doctor's handwriting is), it extracts data using a hybrid AI system, validates it against official databases, and automatically synchronizes administration alarms directly into the patient's Google Calendar.

> 🏆 **Project Context:** This project was born within the **AI Ideation Hackathon (Innovation Labs Cluj)**. Subsequently, the prototype (MVP) code was completely refactorized into a robust production architecture, object-oriented (OOP), being prepared for scalability.

---

## 📑 Table of Contents
1. [Main Features](#-main-features)
2. [Architecture and Technologies](#-architecture-and-technologies)
3. [Test Materials and Business Documentation](#-test-materials-and-business-documentation)
4. [Complete Installation and Setup Guide](#-complete-installation-and-setup-guide)
5. [How to Use (User Flow)](#-how-to-use-user-flow)
6. [Project Structure](#-project-structure)
7. [Roadmap and Future Improvements](#-roadmap-and-future-improvements)

---

## ✨ Main Features

* **📸 Hybrid OCR and Scanning:** Uses Google Cloud Vision to extract raw text from medical prescriptions, receipts, or hospital discharge summaries with maximum accuracy.
* **🤖 AI Analysis with Cross-Validation (RAG):** The Google Gemini 1.5 engine analyzes raw text and intelligently correlates it with:
  * The Official Disease Nomenclature (PDF)
  * The complete Medications List (CSV)
  * *Result: Eliminates AI hallucinations and returns only medications that physically exist in pharmacies.*
* **💊 Simplified Leaflets (For Everyone):** Generates clear explanations, free of excessive medical jargon, regarding the purpose of the treatment, side effects, and administration advice.
* **✅ Validation Interface:** The user maintains absolute control. They can edit concentrations and manually choose generic alternatives available in pharmacies, based on INN (International Nonproprietary Name) / DCI.
* **📅 Google Calendar Synchronization:** Automatically creates recurring events and alarms (pop-up reminders 10 minutes before), sending direct invitations to the patient's phone (via a Service Account).

---

## 🏗️ Architecture and Technologies

The application complies with **Clean Architecture**, **Separation of Concerns**, and **SOLID** principles, being logically divided for easy testing and maintenance:

* **Models (`models/`):** We use **Pydantic** for the strict definition of data schemas (e.g., `PrescriptionData`, `ConfirmedMedication`). It ensures *Type Safety* and automatic validation of the JSON structures returned by the AI.
* **Services (`services/`):** Completely isolates the business logic:
    * `ai_service.py`: Manages prompts and communication with Google Vision and Gemini.
    * `data_service.py`: Manages queries in local files (Pandas for CSV, PyPDF2 for PDF).
    * `calendar_service.py`: Manages authentication and payloads for the Google Calendar API.
* **UI Interface (`ui/`):** Modular Streamlit components (`sidebar.py`, `views.py`, `components.py`) that turn `main.py` into a simple traffic controller.

---

## 📊 Test Materials and Business Documentation

For a complete evaluation of the project, in the `/docs` folder (or directly in the repository) you will find:
1. **Lean Canvas (`LeanCanvas.jpeg`):** The business model created at the Hackathon, detailing the problem, solution, customer segment, and monetization model.
2. **Pitch Presentation (`prezentare_prescripto_pitch.pdf`):** The presentation (Pitch) delivered to the jury at Innovation Labs. It contains the identified problem, proposed solution, market analysis, and product development strategy.
3. **Test Image (`RetetaTest.jpg`):** A complete medical prescription ready to be uploaded into the application to test the OCR + AI flow.
4. **Databases:**
   * Disease codes nomenclature (in `/data`).
   * INN/DCI medications database (in `/data`).

---

## 🚀 Complete Installation and Setup Guide

### Prerequisites
* **Python 3.9** or a newer version installed on your system.
* A **Google Cloud Console** account with the following APIs enabled:
    * *Google Cloud Vision API*
    * *Google Calendar API*
* O cheie API **Google Gemini** validă (obținută de pe [Google AI Studio](https://aistudio.google.com/)).

### Step 1: Cloning and environment preparation
1. Clone this repository locally:
   ```bash
   git clone [https://github.com/username-ul-tau/prescripto.git](https://github.com/username-ul-tau/prescripto.git)
   cd prescripto
2. Create and activate an isolated Python virtual environment:
    ```bash
   # For Windows
    python -m venv .venv
    .venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
3. Install the required packages:
    ```bash
   python -m pip install --upgrade pip
    pip install -r requirements.txt
   
### Step 2: Configuring Environment Variables (Secrets)
1. Create a file named exactly .env in the root of the project.
2. Add your Gemini key:
    ```python
   GEMINI_API_KEY="AIzaSy...your-key..."

### Step 3: Configuring Google Calendar (Service Account)
1. In the Google Cloud Console, create a Service Account.
2. Generate a private key for this account and download it as a JSON file.
3. Rename the downloaded file to credentials.json and place it in the root folder of the project (next to main.py and .env).

### Step 4: Starting the Application
1. Run the command below in your terminal to start the web server:
    ```bash
   streamlit run main.py
2. The application will be available in the browser at: http://localhost:8501.

---

## 🎯 How to Use (User Flow)
1. Scan (Upload): Drag and drop the test image (RetetaTest.jpeg) over the upload area in the interface.
2. Process (AI Magic): Press the "Process Prescription with AI" button. Track the status in real time: Vision reads the text, Gemini extracts the medical logic, and Pandas searches for alternatives in the database.
3. Validate (Human in the Loop): Review the generated tabs. If the AI identified Noliprel 5mg, but you bought Noliprel 10mg, use the drop-down menu to select the alternative purchased from the pharmacy. You can read a summary of the leaflet generated by the AI on the spot.
4. Schedule (Calendar Synchronization): Enter your email address (e.g., ion.popescu@gmail.com) in the final section and press "Add Alarms".
5. Completion: Verify the entered email address. You will receive official invitations from the assistant robot. Once accepted, the alarms will activate on your phone.

