import streamlit as st
import pandas as pd
import time
from PIL import Image

from services.ai_service import ai_service
from services.data_service import DataService
from services.calendar_service import calendar_service
from models.patient import Patient
from models.prescription import ConfirmedMedication

from ui.components import incarca_date, traducere_diagnostic_salvata, prospect_salvat


def render_main_view():
    """Randează zona principală de lucru a aplicației."""
    df_meds = incarca_date()
    coloana_gramaj = df_meds.attrs.get('coloana_gramaj') if df_meds is not None else None

    st.markdown("### 1️⃣ Încarcă Rețeta")
    with st.container(border=True):
        uploaded_file = st.file_uploader("Fă o poză sau alege un fișier din galerie (JPG, PNG)",
                                         type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file is not None:
        if 'ultimul_fisier_incarcat' not in st.session_state or st.session_state[
            'ultimul_fisier_incarcat'] != uploaded_file.name:
            st.toast("📸 Rețetă încărcată cu succes!", icon="✅")
            st.session_state['ultimul_fisier_incarcat'] = uploaded_file.name

        st.markdown("<br>", unsafe_allow_html=True)

        col_img, col_ai = st.columns([1, 1.4], gap="large")

        with col_img:
            st.markdown("#### 📄 Documentul tău")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True, caption="Previzualizare rețetă")

        with col_ai:
            st.markdown("#### 2️⃣ Analiza Asistentului")
            st.info("Sistemul este pregătit. Apasă butonul pentru a iniția extracția de date.")

            if st.button("✨ Procesează Rețeta cu AI", type="primary", use_container_width=True):
                with st.status("🤖 Inițializare motor AI...", expanded=True) as status:
                    st.write("🔍 Scanez imaginea cu Google Vision...")
                    time.sleep(1)
                    st.write("🧠 Interpretez scrisul de mână prin rețele neuronale...")
                    rezultat_ai = ai_service.analyze_prescription(uploaded_file)
                    st.write("📚 Caut medicamentele în Nomenclatorul Oficial...")
                    time.sleep(1)
                    status.update(label="Analiză finalizată!", state="complete", expanded=False)

                st.session_state['date_reteta'] = rezultat_ai
                st.rerun()

            if 'date_reteta' in st.session_state:
                datele = st.session_state['date_reteta']

                if datele.eroare:
                    st.error(f"Eroare: {datele.eroare}")
                else:
                    st.markdown("<br>", unsafe_allow_html=True)
                    tab_diag, tab_trat = st.tabs(["🩺 Diagnosticul Tău", "💊 Tratamentul Prescris"])

                    with tab_diag:
                        st.markdown("<br>", unsafe_allow_html=True)
                        valoare_initiala_cod = str(datele.cod_diagnostic) if datele.cod_diagnostic else ""
                        if valoare_initiala_cod.lower() in ["none", "null"]:
                            valoare_initiala_cod = ""

                        cod_boala_editat = st.text_input("Cod Diagnostic Oficial:", value=valoare_initiala_cod)

                        if cod_boala_editat:
                            coduri_individuale = [c.strip() for c in cod_boala_editat.split(",")]
                            for cod in coduri_individuale:
                                if cod:
                                    text_brut_boala = DataService.get_disease_from_pdf(cod)
                                    if text_brut_boala:
                                        with st.spinner("Traducem diagnosticul..."):
                                            explicatie_simpla = traducere_diagnostic_salvata(text_brut_boala)
                                            st.success(
                                                f"**{text_brut_boala.strip()}**\n\n💡 *Doctorul AI explică:* {explicatie_simpla}")
                                    else:
                                        st.warning(f"Codul '{cod}' nu a fost găsit.")

                    with tab_trat:
                        st.markdown("<br>", unsafe_allow_html=True)
                        with st.form("formular_validare", border=False):
                            medicamente_confirmate = []

                            for i, med in enumerate(datele.medicamente):
                                with st.container(border=True):
                                    st.markdown(f"**🔹 Medicament {i + 1}**")
                                    nume_citit_ai = med.nume_brand_citit

                                    c1, c2 = st.columns(2, gap="medium")
                                    with c1:
                                        termen_cautare = st.text_input("Prescris (Modifică dacă e necesar):",
                                                                       value=nume_citit_ai, key=f"cautare_{i}")
                                        doza = st.text_input("Dozaj prescris:", value=med.doza, key=f"doza_{i}")

                                    if df_meds is not None:
                                        match_df = df_meds[
                                            df_meds['Nume_Afisare'].str.contains(termen_cautare, case=False, na=False)]
                                    else:
                                        match_df = pd.DataFrame()

                                    medicament_final = termen_cautare

                                    with c2:
                                        if not match_df.empty and len(termen_cautare) >= 3:
                                            best_match = match_df.iloc[0]
                                            dci_tinta = best_match.get('DCI', None)

                                            if dci_tinta:
                                                if coloana_gramaj and pd.notna(best_match.get(coloana_gramaj)):
                                                    conc_tinta = best_match[coloana_gramaj]
                                                    alternative_df = df_meds[(df_meds['DCI'] == dci_tinta) & (
                                                                df_meds[coloana_gramaj] == conc_tinta)]
                                                else:
                                                    alternative_df = df_meds[df_meds['DCI'] == dci_tinta]

                                                optiuni = alternative_df['Nume_Afisare'].unique().tolist()
                                                if best_match['Nume_Afisare'] in optiuni:
                                                    optiuni.remove(best_match['Nume_Afisare'])
                                                    optiuni.insert(0, best_match['Nume_Afisare'])

                                                medicament_final = st.selectbox("Achiziționat de la farmacie:",
                                                                                options=optiuni, key=f"select_{i}")
                                        else:
                                            medicament_final = st.text_input("Medicament ales:", value=termen_cautare,
                                                                             disabled=True, key=f"fallback_{i}")

                                    instructiuni = st.text_area("Instrucțiuni Pacient:", value=med.instructiuni_pacient,
                                                                key=f"inst_{i}", height=80)

                                    with st.expander(f"📖 Prospect AI: Află cum te ajută {medicament_final}"):
                                        with st.spinner("Caut informații..."):
                                            st.write(prospect_salvat(medicament_final))
                                    st.markdown("<br>", unsafe_allow_html=True)

                                # Creăm obiectul Pydantic validat
                                medicamente_confirmate.append(ConfirmedMedication(
                                    nume=medicament_final,
                                    doza=doza,
                                    instructiuni=instructiuni,
                                    ore=med.ore_sugerate
                                ))

                            st.markdown("<br>", unsafe_allow_html=True)
                            with st.container(border=True):
                                st.markdown("### 3️⃣ Sincronizare Google Calendar")
                                st.info(
                                    "Introdu adresa cu care ai pre-aprobat asistentul pentru a primi schemele de tratament pe telefon.")

                                email_pacient = st.text_input("📧 Adresa ta de Gmail:",
                                                              placeholder="ion.popescu@gmail.com")

                                submit = st.form_submit_button("📅 Adaugă Alarmele în Calendar!",
                                                               use_container_width=True)

                                if submit:
                                    if not email_pacient:
                                        st.error("⚠️ Te rugăm să introduci o adresă de email validă!")
                                    else:
                                        with st.spinner("Conectare la serverele Google..."):
                                            pacient = Patient(email=email_pacient)
                                            rezultat_calendar = calendar_service.adauga_tratament_in_calendar(
                                                medicamente_confirmate, pacient)

                                            if rezultat_calendar.success:
                                                st.balloons()
                                                st.success("🎉 Succes! Tratamentul tău a fost programat.")
                                                st.toast("Verifică telefonul! Alarmele au fost setate.", icon="📱")

                                                with st.expander("🔗 Vezi evenimentele create"):
                                                    for link in rezultat_calendar.linkuri:
                                                        st.markdown(f"- [Deschide în Browser]({link})")
                                            else:
                                                st.error(f"❌ Eroare Google Calendar: {rezultat_calendar.eroare}")