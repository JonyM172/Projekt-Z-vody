import streamlit as st
import pandas as pd
from backend import Vyhledavani, inicializuj_aplikaci

def parse_time_to_seconds(t):
    try:
        if pd.isna(t) or t in ['', '-', None]: return float('inf')
        m, s = str(t).split(':')
        return int(m) * 60 + float(s.replace(',', '.'))
    except: return float('inf')

st.title("Trati")

# 1. ZAJIŠTĚNÍ DAT
inicializuj_aplikaci()

# 2. NAČTENÍ Z PAMĚTI
databaze_jizd = st.session_state['databaze_jizd']
databaze_zavodniku = st.session_state['databaze_zavodniku']

if not databaze_jizd:
    st.info("Zatím nejsou k dispozici žádné jízdy.")
else:
    # 3. ZÍSKÁNÍ SEZNAMU TRATÍ
    # Projdeme načtené jízdy a vytáhneme unikátní názvy tratí
    trate_list = sorted(list(set(j.trat.jmeno_trati for j in databaze_jizd if j.trat)))

    if not trate_list:
        st.warning("Jízdy nemají přiřazené žádné tratě.")
    else:
        # 4. VÝBĚR A FILTRACE
        selected_track = st.selectbox("Vyberte trať:", trate_list)
        
        # Použijeme backend třídu pro pohodlné filtrování objektů
        vyhledavac = Vyhledavani(databaze_jizd, [], databaze_zavodniku, {}, {})
        _, vyfiltrovane_jizdy = vyhledavac.dle_trate(selected_track)
        
        if not vyfiltrovane_jizdy:
             st.info("Pro tuto trať nejsou záznamy.")
        else:
            # Formátování výstupu
            raw_data = vyhledavac._formatuj_vystup_pro_tabulku([], vyfiltrovane_jizdy)
            
            # Pandas tabulka
            df = pd.DataFrame(raw_data, columns=["Datum", "Typ", "Jméno", "Příjmení", "Skupina", "Trať", "Čas", "Umístění"])
            df['seconds'] = df['Čas'].apply(parse_time_to_seconds)

            # Checkbox Nejlepší
            st.write("### Možnosti zobrazení")
            if st.checkbox("Zobrazit pouze nejlepší pokusy závodníků"):
                valid = df[df['seconds'] != float('inf')]
                idx = valid.groupby(['Jméno', 'Příjmení'])['seconds'].idxmin()
                df = df.loc[idx]

            # Zobrazení
            df = df.sort_values(by=['seconds', 'Datum'])
            df = df.reset_index(drop=True)
            df.insert(0, 'Pořadí', range(1, len(df) + 1))
            
            st.write(f"### Výsledky: {selected_track}")
            st.dataframe(df[['Pořadí', 'Jméno', 'Příjmení', 'Datum', 'Čas']], hide_index=True, use_container_width=True)