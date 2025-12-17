import streamlit as st
import pandas as pd
from backend import Vyhledavani, inicializuj_aplikaci

def parse_time_to_seconds(t):
    try:
        if pd.isna(t) or t in ['', '-', None]: return float('inf')
        m, s = str(t).split(':')
        return int(m) * 60 + float(s.replace(',', '.'))
    except: return float('inf')

st.title("Skupiny")

# 1. ZAJIŠTĚNÍ DAT
inicializuj_aplikaci()

# 2. NAČTENÍ Z PAMĚTI
databaze_jizd = st.session_state['databaze_jizd']
databaze_zavodniku = st.session_state['databaze_zavodniku']
databaze_skupin = st.session_state['databaze_skupin']

# Získáme seznam skupin (buď z klíčů DB skupin, nebo unikátní skupiny závodníků)
skupiny_list = sorted(list(databaze_skupin.keys()))
if not skupiny_list:
    # Fallback, kdyby DB skupin byla prázdná
    skupiny_list = sorted(list(set(z.skupina for z in databaze_zavodniku.values() if z.skupina)))

if not skupiny_list:
    st.warning("Nejsou definovány žádné skupiny.")
else:
    # 3. VÝBĚR SKUPINY
    selected_group = st.selectbox("Vyberte skupinu:", skupiny_list)
    
    # Filtrace jízd podle skupiny (pomocí backendu)
    vyhledavac = Vyhledavani(databaze_jizd, [], databaze_zavodniku, {}, databaze_skupin)
    _, jizdy_skupiny = vyhledavac.dle_skupiny(selected_group)
    
    if not jizdy_skupiny:
        st.info(f"Skupina {selected_group} nemá žádné jízdy.")
    else:
        # 4. VÝBĚR TRATĚ (Jen ty, které skupina jela)
        trate_skupiny = sorted(list(set(j.trat.jmeno_trati for j in jizdy_skupiny)))
        
        if not trate_skupiny:
            st.warning("Skupina sice má jízdy, ale bez názvu tratě.")
        else:
            selected_track = st.selectbox("Vyberte trať:", trate_skupiny)
            
            # Filtrace podle tratě (Python list comprehension nad už vyfiltrovanou skupinou)
            finalni_jizdy = [j for j in jizdy_skupiny if j.trat.jmeno_trati == selected_track]
            
            # Formátování
            raw_data = vyhledavac._formatuj_vystup_pro_tabulku([], finalni_jizdy)
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
            
            st.write(f"### Výsledky: {selected_group} - {selected_track}")
            st.dataframe(df[['Pořadí', 'Jméno', 'Příjmení', 'Datum', 'Čas']], hide_index=True, use_container_width=True)