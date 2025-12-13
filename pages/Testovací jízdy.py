import streamlit as st
import pandas as pd
from backend import Vyhledavani, inicializuj_aplikaci

# Pomocná funkce pro převod času (čistě frontendová záležitost)
def parse_time_to_seconds(t):
    try:
        if pd.isna(t) or t in ['', '-', None]: return float('inf')
        m, s = str(t).split(':')
        return int(m) * 60 + float(s.replace(',', '.'))
    except: return float('inf')

st.title("Testovací jízdy")

# --- KROK 1: ZÁCHRANNÁ SÍŤ PROTI F5 ---
inicializuj_aplikaci()

# --- KROK 2: VYTAŽENÍ DAT Z PAMĚTI ---
db_jizdy = st.session_state['databaze_jizd']
db_zavodnici = st.session_state['databaze_zavodniku']

# --- KROK 3: LOGIKA STRÁNKY ---
if not db_jizdy:
    st.info("Zatím nejsou k dispozici žádné záznamy.")
else:
    # Inicializace vyhledávače (pouze pro formátování výstupu)
    # Posíláme jen to, co potřebujeme, zbytek {} nebo []
    vyhledavac = Vyhledavani(db_jizdy, [], db_zavodnici, {}, {})
    
    # Získání dat v textové podobě pro tabulku
    raw_data = vyhledavac._formatuj_vystup_pro_tabulku([], db_jizdy)
    
    # Převod na DataFrame
    cols = ["Datum", "Typ", "Jméno", "Příjmení", "Skupina", "Trať", "Čas", "Umístění"]
    df = pd.DataFrame(raw_data, columns=cols)
    
    # Pomocný sloupec pro řazení
    df['seconds'] = df['Čas'].apply(parse_time_to_seconds)

    # UI: Checkbox
    st.write("### Možnosti zobrazení")
    if st.checkbox("Zobrazit pouze nejlepší pokusy závodníků na každé trati"):
        # Logika filtrace
        valid = df[df['seconds'] != float('inf')]
        # Najdi indexy řádků s nejmenším časem pro (Jméno+Trať)
        idx = valid.groupby(['Jméno', 'Příjmení', 'Trať'])['seconds'].idxmin()
        df = df.loc[idx]

    # Finální úprava a zobrazení
    df = df.sort_values(by=['seconds', 'Datum'])
    df.insert(0, 'Pořadí', range(1, len(df) + 1))
    
    final_cols = ['Pořadí', 'Jméno', 'Příjmení', 'Skupina', 'Trať', 'Datum', 'Čas']
    st.dataframe(df[final_cols], hide_index=True, use_container_width=True)