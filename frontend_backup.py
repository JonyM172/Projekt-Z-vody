import streamlit as st
import pandas as pd
import numpy as np
from backend import (
    Zavodnik, Skupina, Trat, TestovaciJizda, Zavod,
    zkontroluj_soubory, inicializuj_aplikaci,
    uloz_zavodniky, nacti_a_sluc_zavodniky, uloz_skupiny, nacti_a_sluc_skupiny,
    uloz_trate, nacti_a_sluc_trate, nacti_zaznamy,
    PraceSDatabazi,  # Import the class containing deduplication logic
)
zkontroluj_soubory()
inicializuj_aplikaci()

# Initialize databases

databaze_zavodniku = {}
databaze_skupin = {}
databaze_trati = {}
databaze_jizd = []
databaze_zavodu = []

zkontroluj_soubory()

# Load initial data
databaze_zavodniku = nacti_a_sluc_zavodniky(databaze_zavodniku)
databaze_skupin = nacti_a_sluc_skupiny(databaze_skupin, databaze_zavodniku)
databaze_trati = nacti_a_sluc_trate(databaze_trati)
databaze_jizd, databaze_zavodu = nacti_zaznamy(databaze_zavodniku)

# Debugging: Display the contents of loaded databases
#st.write("Databáze závodníků:", databaze_zavodniku)
#st.write("Databáze jízd:", databaze_jizd)

# Create an instance of PraceSDatabazi
prace_s_databazi = PraceSDatabazi(databaze_jizd, databaze_zavodu, databaze_zavodniku, databaze_trati, databaze_skupin)

# Deduplicate records using the backend method
prace_s_databazi.deduplikuj_zaznamy()

# PAGES SETUP

Vytvoř_záznam = st.Page(
    page="pages/Vytvoř_záznam.py",
    title="Vytvořit záznam",  
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

# NAVIGATION SETUP
PG = st.navigation(pages=[Homepage, Vytvoř_záznam, TestovaciJizdy, Závody, Trati, Skupiny])

# RUN NAVIGATION
PG.run()

zkontroluj_soubory()
