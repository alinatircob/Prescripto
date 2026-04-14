import streamlit as st
import pandas as pd
from services.ai_service import ai_service
from services.data_service import DataService

def apply_custom_css():
    """Aplică stilizarea CSS"""
    st.markdown("""
        <style>
        .main-title { 
            font-size: 4rem !important; 
            font-weight: 800 !important; 
            color: #1E88E5 !important;
            text-align: center !important; 
            margin-top: -20px !important; 
            margin-bottom: 5px !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1) !important; 
        }
        .sub-title { 
            font-size: 1.2rem !important; 
            color: var(--text-color) !important;
            opacity: 0.7; 
            text-align: center !important; 
            margin-bottom: 40px !important; 
            font-weight: 400;
        }
        div[data-testid="stForm"] { 
            border-radius: 12px; 
            border: 1px solid rgba(128, 128, 128, 0.2); 
            background-color: transparent; 
        }
        .sidebar-step { 
            background-color: rgba(128, 128, 128, 0.05); 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 4px solid #1E88E5; 
            margin-bottom: 15px; 
        }
        .sidebar-step-title { 
            font-weight: 600; 
            font-size: 1.05rem; 
            color: var(--text-color); 
            margin-bottom: 5px; 
        }
        .sidebar-step-text { 
            font-size: 0.9rem; 
            color: var(--text-color); 
            opacity: 0.8;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Afișează titlul principal și subtitlul."""
    st.markdown('<p class="main-title">💊 Prescripto</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Traducătorul tău de rețete. Din mâna medicului, direct în calendarul tău.</p>', unsafe_allow_html=True)
    st.divider()

# CACHE & OPTIMIZARE
@st.cache_data
def incarca_date():
    df = DataService.load_meds_database()
    if df is not None:
        df.columns = df.columns.str.strip()
        coloana_gramaj = None
        posibile_nume = ['Concentratia', 'Concentratie', 'Gramaj', 'Doza', 'Concentrație', 'concentratia']

        for nume in posibile_nume:
            if nume in df.columns:
                coloana_gramaj = nume
                break

        df.attrs['coloana_gramaj'] = coloana_gramaj
        if coloana_gramaj:
            df['Nume_Afisare'] = df['Denumire comerciala'].astype(str) + " - " + df[coloana_gramaj].astype(str)
        else:
            df['Nume_Afisare'] = df['Denumire comerciala'].astype(str)
    return df

@st.cache_data(show_spinner=False)
def traducere_diagnostic_salvata(text_medical):
    return ai_service.explain_diagnosis(text_medical)

@st.cache_data(show_spinner=False)
def prospect_salvat(nume_medicament):
    return ai_service.get_medication_prospectus(nume_medicament)