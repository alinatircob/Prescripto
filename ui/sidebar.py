import streamlit as st

def render_sidebar():
    """Randează meniul lateral cu pașii de funcționare."""
    with st.sidebar:
        st.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=70)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center; color: #1E88E5; margin-bottom: 30px;'>Cum funcționează?</h3>", unsafe_allow_html=True)

        st.markdown("""
            <div class="sidebar-step">
                <div class="sidebar-step-title">📸 1. Scanează</div>
                <div class="sidebar-step-text">Încarcă poza clară cu rețeta ta medicală.</div>
            </div>
            <div class="sidebar-step">
                <div class="sidebar-step-title">🤖 2. Analizează</div>
                <div class="sidebar-step-text">AI-ul descifrează scrisul de mână și identifică tratamentul.</div>
            </div>
            <div class="sidebar-step">
                <div class="sidebar-step-title">💊 3. Validează</div>
                <div class="sidebar-step-text">Alege alternativele din farmacie și citește prospectul.</div>
            </div>
            <div class="sidebar-step">
                <div class="sidebar-step-title">📅 4. Programează</div>
                <div class="sidebar-step-text">Sincronizează totul în telefon pentru alarme automate.</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.divider()
        st.caption("🚀 Construit cu Gemini AI & Google Calendar")