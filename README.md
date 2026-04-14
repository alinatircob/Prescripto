# 💊 Prescripto - Asistent Medical & Traducător de Rețete 

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange)
![Google Cloud Vision](https://img.shields.io/badge/Google%20Cloud-Vision%20API-blue)
![Google Calendar](https://img.shields.io/badge/Google%20Calendar-API-success)
![Pydantic](https://img.shields.io/badge/Pydantic-Data%20Validation-blueviolet)

**Prescripto** este o aplicație web inovatoare concepută pentru a traduce, valida și programa schemele de tratament medical. Pornește de la o simplă fotografie a unei rețete (indiferent cât de ilizibil este scrisul medicului), extrage datele folosind un sistem AI hibrid, le validează cu baze de date oficiale și sincronizează automat alarmele de administrare direct în Google Calendar-ul pacientului.

> 🏆 **Contextul Proiectului:** Acest proiect a luat naștere în cadrul **AI Ideation Hackathon (Innovation Labs Cluj)**. Ulterior, codul de tip prototip (MVP) a fost complet refactorizat într-o arhitectură robustă de producție, orientată pe obiect (OOP), fiind pregătit pentru scalabilitate.

---

## 📑 Cuprins
1. [Funcționalități Principale](#-funcționalități-principale)
2. [Arhitectură și Tehnologii](#-arhitectură-și-tehnologii)
3. [Materiale de Test și Documentație Business](#-materiale-de-test-și-documentație-business)
4. [Ghid Complet de Instalare și Setare](#-ghid-complet-de-instalare-și-setare)
5. [Mod de Utilizare (User Flow)](#-mod-de-utilizare-user-flow)
6. [Structura Proiectului](#-structura-proiectului)
7. [Roadmap și Îmbunătățiri Viitoare](#-roadmap-și-îmbunătățiri-viitoare)

---

## ✨ Funcționalități Principale

* **📸 Scanare și OCR Hibrid:** Folosește Google Cloud Vision pentru a extrage cu acuratețe maximă textul brut de pe rețete medicale, chitanțe sau bilete de ieșire din spital.
* **🤖 Analiză AI cu Validare Încrucișată (RAG):** Motorul Google Gemini 1.5 analizează textul brut și îl corelează inteligent cu:
  * Nomenclatorul Oficial de Boli (PDF)
  * Lista completă a Medicamentelor (CSV)
  * *Rezultat: Elimină halucinațiile AI-ului și returnează doar medicamente care există fizic în farmacii.*
* **💊 Prospecte Simplificate (Pe înțelesul tuturor):** Generează explicații clare, lipsite de jargon medical excesiv, despre scopul tratamentului, efecte adverse și sfaturi de administrare.
* **✅ Interfață de Validare:** Utilizatorul menține controlul absolut. Poate edita concentrațiile și poate alege manual alternativele generice disponibile în farmacie, bazate pe DCI (Denumirea Comună Internațională).
* **📅 Sincronizare Google Calendar:** Creează automat evenimente recurente și alarme (remindere pop-up cu 10 minute înainte) trimițând invitații directe pe telefonul pacientului (prin intermediul unui Service Account).

---

## 🏗️ Arhitectură și Tehnologii

Aplicația respectă principiile **Clean Architecture**, **Separation of Concerns** și **SOLID**, fiind divizată logic pentru o testare și mentenanță ușoară:

* **Modele (`models/`):** Utilizăm **Pydantic** pentru definirea strictă a schemelor de date (ex: `PrescriptionData`, `ConfirmedMedication`). Asigură *Type Safety* și validarea automată a JSON-urilor returnate de AI.
* **Servicii (`services/`):** Izolează complet logica de business:
    * `ai_service.py`: Gestionează prompturile și comunicarea cu Google Vision și Gemini.
    * `data_service.py`: Gestionează interogările în fișierele locale (Pandas pentru CSV, PyPDF2 pentru PDF).
    * `calendar_service.py`: Gestionează autentificarea și payload-urile pentru Google Calendar API.
* **Interfață UI (`ui/`):** Componente Streamlit modulare (`sidebar.py`, `views.py`, `components.py`) care transformă `main.py` într-un simplu dirijor

---

## 📊 Materiale de Test și Documentație Business

Pentru o evaluare completă a proiectului, în folderul `/docs` (sau direct în repository) veți găsi:
1. **Lean Canvas (`LeanCanvas.jpeg`):** Modelul de business creat la Hackathon, care detaliază problema, soluția, segmentul de clienți și modelul de monetizare.
2. **Prezentarea pentru Pitch(`prezentare_prescripto_pitch.pdf`):** Prezentarea (Pitch) susținută în fața juriului la Innovation Labs. Conține problema identificată, soluția propusă, analiza pieței și strategia de dezvoltare a produsului
3. **Imagine de Test (`RetetaTest.jpg`):** O rețetă medicală completă pregătită pentru a fi încărcată în aplicație pentru testarea flow-ului OCR + AI.
4. **Baze de Date:**
   * Nomenclatorul de coduri de boală (în `/data`).
   * Baza de date cu medicamente DCI (în `/data`).

---

## 🚀 Ghid Complet de Instalare și Setare

### Precondiții
* **Python 3.9** sau o versiune mai nouă instalată pe sistemul tău.
* Un cont **Google Cloud Console** cu următoarele API-uri activate:
    * *Google Cloud Vision API*
    * *Google Calendar API*
* O cheie API **Google Gemini** validă (obținută de pe [Google AI Studio](https://aistudio.google.com/)).

### Pasul 1: Clonarea și pregătirea mediului
1. Clonează acest repository local:
   ```bash
   git clone [https://github.com/username-ul-tau/prescripto.git](https://github.com/username-ul-tau/prescripto.git)
   cd prescripto
2. Creează și activează un mediu virtual Python izolat:
    ```bash
   # Pentru Windows
    python -m venv .venv
    .venv\Scripts\activate

    # Pentru macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
3. Instalează pachetele necesare:
    ```bash
   python -m pip install --upgrade pip
    pip install -r requirements.txt
   
### Pasul 2: Configurarea Variabilelor de Mediu (Secrets)
1. Creează un fișier numit exact .env în rădăcina proiectului.
2. Adaugă cheia ta Gemini:
    ```python
   GEMINI_API_KEY="AIzaSy...cheia-ta-aici..."

### Pasul 3: Configurarea Google Calendar (Service Account)
1. În Google Cloud Console, creează un Service Account (Cont de Serviciu).
2. Generează o cheie privată pentru acest cont și descarc-o sub formă de fișier JSON.
3. Redenumește fișierul descărcat în credentials.json și plasează-l în folderul rădăcină al proiectului (lângă main.py și .env).

### Pasul 4: Pornirea Aplicației
1. Rulează comanda de mai jos în terminalul tău pentru a porni serverul web:
    ```bash
   streamlit run main.py
2. Aplicația va fi disponibilă în browser la adresa: http://localhost:8501.

---

## 🎯 Mod de Utilizare (User Flow)
1. Scanează (Upload): Trage imaginea de test (RetetaTest.jpeg) peste zona de upload din interfață.
2. Procesează (AI Magic): Apasă butonul „Procesează Rețeta cu AI”. Urmărește statusul în timp real: Vision citește textul, Gemini extrage logica medicală, iar Pandas caută alternativele în baza de date.
3. Validează (Human in the Loop): Revizuiește tab-urile generate. Dacă AI-ul a identificat Noliprel 5mg, dar tu ai cumpărat Noliprel 10mg, folosește meniul drop-down pentru a selecta alternativa achiziționată de la farmacie. Poți citi pe loc un prospect rezumat de AI.
4. Programează (Sincronizare Calendar): Introdu adresa ta de email (ex: ion.popescu@gmail.com) în secțiunea finală și apasă „Adaugă Alarmele”.
5. Finalizare: Verifică adresa de email introdusă. Vei primi invitații oficiale de la asistentul robot. Odată acceptate, alarmele se activează pe telefonul tău.

