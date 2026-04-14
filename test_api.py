
import google.generativeai as genai

from utils.config import settings


def test_gemini_connection():
    """Testează conexiunea la API-ul Google Gemini și listează modelele disponibile."""
    print("🔄 Se verifică cheia API din configurație...")

    # Validăm dacă cheia a fost încărcată corect din .env
    if not settings.GEMINI_API_KEY:
        print("❌ Eroare: Cheia API lipsește sau nu a putut fi citită din fișierul .env.")
        return

    # Folosim cheia din clasa settings
    genai.configure(api_key=settings.GEMINI_API_KEY)

    try:
        print("\n✅ Conexiune stabilită! Modelele disponibile pentru generare sunt:")
        modele_gasite = False

        for m in genai.list_models():
            # Filtrăm doar modelele capabile să genereze conținut (text/imagini)
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
                modele_gasite = True

        if not modele_gasite:
            print("\n⚠️ Atenție: Cheia ta API este validă, dar nu are acces la niciun model de generare text/imagini!")

    except Exception as e:
        print(f"\n❌ Eroare la conectarea cu serverele Google: {e}")


if __name__ == "__main__":
    test_gemini_connection()