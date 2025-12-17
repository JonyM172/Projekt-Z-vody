import streamlit as st
import pandas as pd
# import numpy as np
from backend import (
    Zavodnik, Skupina, Trat, TestovaciJizda, Zavod,
    zkontroluj_soubory, inicializuj_aplikaci,
    uloz_zavodniky, nacti_a_sluc_zavodniky, uloz_skupiny, nacti_a_sluc_skupiny,
    uloz_trate, nacti_a_sluc_trate, nacti_zaznamy,
    PraceSDatabazi,  # Import the class containing deduplication logic
)

# 1. Kontrola souborů a inicializace dat do paměti
zkontroluj_soubory()
inicializuj_aplikaci()

# ==============================================================================
# OPRAVA: Vytažení dat ze Session State
# Musíme definovat proměnné databaze_..., jinak je PraceSDatabazi neuvidí.
# ==============================================================================
databaze_jizd = st.session_state['databaze_jizd']
databaze_zavodu = st.session_state['databaze_zavodu']
databaze_zavodniku = st.session_state['databaze_zavodniku']
databaze_trati = st.session_state['databaze_trati']
databaze_skupin = st.session_state['databaze_skupin']

# 2. Vytvoření instance pro práci s databází
# Teď už proměnné existují, takže tento řádek proběhne bez chyby
prace_s_databazi = PraceSDatabazi(databaze_jizd, databaze_zavodu, databaze_zavodniku, databaze_trati, databaze_skupin)

# 3. Deduplikace záznamů
prace_s_databazi.deduplikuj_zaznamy()


# PAGES SETUP
Vytvoř_záznam = st.Page(
    page="pages/Vytvoř_záznam.py",
    title="Vytvořit/upravit záznamy",  
    )
Homepage = st.Page(
    page="pages/Homepage.py",
    title="Homepage",  
    )
TestovaciJizdy = st.Page(
    page="pages/Testovací jízdy.py",
    title="Testovací jízdy",  
    )
Závody = st.Page(
    page="pages/Závody.py",
    title="Závody",
    )
Trati = st.Page(
    page="pages/Trati.py",
    title="Trati",  
    )
Skupiny = st.Page(
    page="pages/Skupiny.py",
    title="Skupiny",  
    )
Vyhledávání = st.Page(
    page="pages/Vyhledavani.py",
    title="Vyhledávání",  
    )

# NAVIGATION SETUP
PG = st.navigation(pages=[Homepage, Vytvoř_záznam, TestovaciJizdy, Závody, Trati, Skupiny, Vyhledávání])

# RUN NAVIGATION
PG.run()
