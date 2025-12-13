import streamlit as st
import pandas as pd
from backend import Vyhledavani, nacti_a_sluc_zavodniky, nacti_zaznamy

# --- POMOCNÁ FUNKCE PRO ŘAZENÍ (UI LOGIKA) ---
def parse_time_to_seconds(t):
    """Převede string času (MM:SS,ms) na float sekundy pro správné řazení."""
    try:
        if pd.isna(t) or t == '' or t == '-' or t is None: return float('inf')
        parts = str(t).split(':')
        minutes = int(parts[0])
        seconds = float(parts[1].replace(',', '.'))
        return minutes * 60 + seconds
    except (ValueError, IndexError, AttributeError):
        return float('inf')

# --- HLAVNÍ APLIKACE ---
st.title("Testovací jízdy")

#NActeni dat 

if 'databaze_zavodniku' not in st.session_state or 'databaze_jizd' not in st.session_state:
    databaze_zavodniku = {}
    nacti_a_sluc_zavodniky(databaze_zavodniku)
    databaze_jizd, _ = nacti_zaznamy(databaze_zavodniku)
    st.session_state['databaze_zavodniku'] = databaze_zavodniku
    st.session_state['databaze_jizd'] = databaze_jizd
else:
    databaze_zavodniku = st.session_state['databaze_zavodniku']
    databaze_jizd = st.session_state['databaze_jizd']

# 2. PŘÍPRAVA A ZOBRAZENÍ DAT
if databaze_jizd:
    vyhledavac = Vyhledavani(databaze_jizd, [], databaze_zavodniku, {}, {})
    # Získání surových dat pro tabulku a prevod na dataframe
    raw_data = vyhledavac._formatuj_vystup_pro_tabulku([], databaze_jizd)

    cols = ["Datum", "Typ", "Jméno", "Příjmení", "Skupina", "Trať", "Čas", "Umístění"]
    df = pd.DataFrame(raw_data, columns=cols)


    df['seconds'] = df['Čas'].apply(parse_time_to_seconds)

    # Ovládací prvek: Checkbox
    st.write("### Možnosti zobrazení")
    jen_nejlepsi = st.checkbox("Zobrazit pouze nejlepší pokusy závodníků na každé trati")

    # Logika filtrování "Nejlepší pokus"
    if jen_nejlepsi:
        # 1. Zahodíme neplatné časy (DNF, prázdné...)
        valid_df = df[df['seconds'] != float('inf')]
        
        # 2. Najdeme indexy řádků s minimálním časem pro každou skupinu (Jméno + Trať)
        idx_nejlepsi = valid_df.groupby(['Jméno', 'Příjmení', 'Trať'])['seconds'].idxmin()
        
        # 3. Vyfiltrujeme původní tabulku podle těchto indexů
        df = df.loc[idx_nejlepsi]

    # KROK D: Finální úprava tabulky
    # Seřadíme podle času (nejlepší nahoře) a data
    df = df.sort_values(by=['seconds', 'Datum'])
    
    # Resetujeme index a vytvoříme sloupec "Pořadí" (1, 2, 3...)
    df = df.reset_index(drop=True)
    df.insert(0, 'Pořadí', range(1, len(df) + 1))

    # Vybereme jen ty sloupce, které má uživatel vidět
    final_cols = ['Pořadí', 'Jméno', 'Příjmení', 'Skupina', 'Trať', 'Datum', 'Čas']
    
    st.write("### Přehled jízd")
    st.dataframe(df[final_cols], hide_index=True, use_container_width=True)

else:
    # Pokud v databázi nejsou žádné jízdy
    st.warning("Žádná data k zobrazení. Nahrajte prosím jízdy.")