import streamlit as st
import pandas as pd
from backend import Vyhledavani, inicializuj_aplikaci

# --- POMOCNÁ FUNKCE PRO ŘAZENÍ ---
def parse_time_to_seconds(t):
    """Převede string času na číslo pro správné řazení."""
    try:
        if pd.isna(t) or t in ['', '-', None]: return float('inf')
        m, s = str(t).split(':')
        return int(m) * 60 + float(s.replace(',', '.'))
    except: return float('inf')

st.title("Pokročilé vyhledávání")

# ==============================================================================
# 1. ZAJIŠTĚNÍ DAT
# ==============================================================================
inicializuj_aplikaci()

# Načtení odkazů na data ze session state
databaze_jizd = st.session_state['databaze_jizd']
databaze_zavodu = st.session_state['databaze_zavodu']
databaze_zavodniku = st.session_state['databaze_zavodniku']
databaze_trati = st.session_state['databaze_trati']
databaze_skupin = st.session_state['databaze_skupin']

# Inicializace vyhledávače
vyhledavac = Vyhledavani(databaze_jizd, databaze_zavodu, databaze_zavodniku, databaze_trati, databaze_skupin)

# ==============================================================================
# 2. NASTAVENÍ FILTRŮ (UI)
# ==============================================================================

with st.expander("🔍 Nastavení filtrů", expanded=True):
    col1, col2 = st.columns(2)

    # --------------------------------------------------------------------------
    # KROK 1: SKUPINA (Definujeme jako první, aby ovlivnila seznam závodníků)
    # --------------------------------------------------------------------------
    with col2:
        st.write("###### Skupina")
        seznam_skupin = sorted(list(databaze_skupin.keys()))
        if not seznam_skupin: # Fallback
            seznam_skupin = sorted(list(set(z.skupina for z in databaze_zavodniku.values() if z.skupina)))
        
        vybrana_skupina = st.selectbox("Vyberte skupinu:", ["Všechny"] + seznam_skupin, label_visibility="collapsed")

    # --------------------------------------------------------------------------
    # KROK 2: ZÁVODNÍK (Nyní už známe hodnotu 'vybrana_skupina')
    # --------------------------------------------------------------------------
    with col1:
        st.write("###### Závodník")
        metoda = st.radio("Způsob výběru:", ["Ze seznamu", "Podle textu"], horizontal=True, label_visibility="collapsed")
        
        filtr_id = None
        hledany_text = None

        if metoda == "Ze seznamu":
            # FILTRACE ZÁVODNÍKŮ PODLE VYBRANÉ SKUPINY
            if vybrana_skupina == "Všechny":
                # Pokud jsou všechny skupiny, bereme všechny závodníky
                zdroj_zavodniku = databaze_zavodniku.values()
            else:
                # Jinak jen ty, kteří patří do vybrané skupiny
                zdroj_zavodniku = [z for z in databaze_zavodniku.values() if z.skupina == vybrana_skupina]

            # Vytvoření seznamu pro Selectbox
            seznam = sorted([f"{z.prijmeni} {z.jmeno} ({z.id_osoby})" for z in zdroj_zavodniku])
            
            # Pokud po vyfiltrování nikdo nezbude (prázdná skupina), zobrazíme prázdný list
            if not seznam:
                seznam = []
            
            vyber = st.selectbox("Vyberte jméno:", ["Všichni"] + seznam, label_visibility="collapsed")
            
            if vyber != "Všichni":
                try:
                    filtr_id = vyber.split("(")[-1].replace(")", "")
                except: pass
        else:
            # Textové vyhledávání
            hledany_text = st.text_input("Napište část jména:", placeholder="Např. Novák...", label_visibility="collapsed")

    col3, col4 = st.columns(2)

    # --- C. TRAŤ ---
    with col3:
        st.write("###### Trať")
        seznam_trati = sorted(list(databaze_trati.keys()))
        if not seznam_trati: 
            seznam_trati = sorted(list(set(j.trat.jmeno_trati for j in databaze_jizd if j.trat)))
            
        vybrana_trat = st.selectbox("Vyberte trať:", ["Všechny"] + seznam_trati, label_visibility="collapsed")

    # --- D. DATUM ---
    with col4:
        st.write("###### Datum")
        datum_rozsah = st.date_input("Rozsah data:", value=[], label_visibility="collapsed")

# ==============================================================================
# 3. PŘÍPRAVA FILTRŮ PRO BACKEND
# ==============================================================================

# Skupina a Trať
backend_skupina = vybrana_skupina if vybrana_skupina != "Všechny" else None
backend_trat = vybrana_trat if vybrana_trat != "Všechny" else None

# Datum
backend_datum_od = None
backend_datum_do = None
if len(datum_rozsah) == 2:
    backend_datum_od = datum_rozsah[0].strftime("%Y-%m-%d")
    backend_datum_do = datum_rozsah[1].strftime("%Y-%m-%d")
elif len(datum_rozsah) == 1:
    backend_datum_od = datum_rozsah[0].strftime("%Y-%m-%d")

# ==============================================================================
# 4. VOLÁNÍ BACKENDU A ZPRACOVÁNÍ DAT
# ==============================================================================

vyfiltrovane_zavody, vyfiltrovane_jizdy = vyhledavac.filtruj(
    id_zavodnika=filtr_id,      
    skupina=backend_skupina,
    trat=backend_trat,
    datum_od=backend_datum_od,
    datum_do=backend_datum_do
)

raw_data = vyhledavac._formatuj_vystup_pro_tabulku(vyfiltrovane_zavody, vyfiltrovane_jizdy)

st.write("---")

if not raw_data:
    st.info("Zadaným kritériím neodpovídají žádné záznamy.")
else:
    cols = ["Datum", "Typ", "Jméno", "Příjmení", "Skupina", "Trať", "Čas", "Umístění"]
    df = pd.DataFrame(raw_data, columns=cols)

    # Jemný filtr v Pandasu (pokud hledáme podle textu)
    if hledany_text:
        t = hledany_text.lower()
        mask = df.apply(lambda row: t in str(row['Jméno']).lower() or t in str(row['Příjmení']).lower(), axis=1)
        df = df[mask]

    if df.empty:
        st.warning(f"Závodník odpovídající textu '{hledany_text}' nebyl v tomto výběru nalezen.")
    else:
        df['seconds'] = df['Čas'].apply(parse_time_to_seconds)
        st.caption(f"Nalezeno záznamů: {len(df)}")

        if st.checkbox("Zobrazit pouze nejlepší časy (pro vybraná kritéria)"):
            valid = df[df['seconds'] != float('inf')]
            idx = valid.groupby(['Jméno', 'Příjmení', 'Trať'])['seconds'].idxmin()
            df = df.loc[idx]

        df = df.sort_values(by=['Datum', 'seconds'], ascending=[False, True])
        df = df.reset_index(drop=True)
        df.insert(0, 'Pořadí', range(1, len(df) + 1))

        final_cols = ['Pořadí', 'Datum', 'Typ', 'Jméno', 'Příjmení', 'Skupina', 'Trať', 'Čas', 'Umístění']
        st.dataframe(df[final_cols], hide_index=True, use_container_width=True)