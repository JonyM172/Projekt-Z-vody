import streamlit as st
import pandas as pd
import datetime
import uuid
import time
from backend import inicializuj_aplikaci, PraceSDatabazi

# ==============================================================================
# NASTAVENÍ STRÁNKY A DAT
# ==============================================================================
st.title("Správa záznamů")

# 1. ZAJIŠTĚNÍ DAT
inicializuj_aplikaci()

# 2. NAČTENÍ Z PAMĚTI (Alias pro snadnější psaní)
db_zavodnici = st.session_state['databaze_zavodniku']
db_skupiny = st.session_state['databaze_skupin']
db_trate = st.session_state['databaze_trati']
db_jizdy = st.session_state['databaze_jizd']  # Toto je list objektů
db_zavody = st.session_state['databaze_zavodu']

# Inicializace Workera s aktuálními daty v Session State
# DŮLEŽITÉ: Předáváme referenci na list v session_state, aby se změny projevily v backendu
worker = PraceSDatabazi(db_jizdy, db_zavody, db_zavodnici, db_trate, db_skupiny)

# ==============================================================================
# ROZCESTNÍK (ZÁLOŽKY)
# ==============================================================================
tab_novy, tab_upravy = st.tabs(["⏱️ Nový trénink", "✏️ Úpravy a mazání"])

# ==============================================================================
# TAB 1: NOVÝ ZÁZNAM (HROMADNÝ I JEDNOTLIVÝ)
# ==============================================================================
with tab_novy:
    st.subheader("Hromadný zápis (celá skupina)")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        datum = st.date_input("Datum tréninku:", datetime.date.today())

    with col2:
        skupiny_list = sorted(list(db_skupiny.keys()))
        if not skupiny_list: # Fallback pokud nejsou skupiny v CSV
            skupiny_list = sorted(list(set(z.skupina for z in db_zavodnici.values() if z.skupina)))
        vybrana_skupina = st.selectbox("Vyberte skupinu:", skupiny_list)

    with col3:
        trate_list = sorted(list(db_trate.keys()))
        if not trate_list:
            trate_list = sorted(list(set(j.trat.jmeno_trati for j in db_jizdy if j.trat)))
        vybrana_trat = st.selectbox("Vyberte trať:", trate_list)

    # --- TABULKA PRO ZADÁNÍ ---
    if not vybrana_skupina:
        st.info("Nejdříve vyberte skupinu.")
    else:
        zavodnici_ve_skupine = [z for z in db_zavodnici.values() if z.skupina == vybrana_skupina]
        
        if not zavodnici_ve_skupine:
            st.warning(f"Ve skupině '{vybrana_skupina}' nejsou žádní závodníci.")
        else:
            zavodnici_ve_skupine.sort(key=lambda z: z.prijmeni)

            data_pro_tabulku = []
            for z in zavodnici_ve_skupine:
                data_pro_tabulku.append({
                    "id_zavodnika": z.id_osoby,
                    "Příjmení": z.prijmeni,
                    "Jméno": z.jmeno,
                    "Čas": ""
                })

            df_template = pd.DataFrame(data_pro_tabulku)
            st.caption("Zadejte časy (např. `1:23,45` nebo `45,2`). Prázdné řádky se ignorují.")

            edited_df = st.data_editor(
                df_template,
                column_config={
                    "id_zavodnika": None, # Skrytý sloupec
                    "Příjmení": st.column_config.TextColumn(disabled=True),
                    "Jméno": st.column_config.TextColumn(disabled=True),
                    "Čas": st.column_config.TextColumn("Čas", width="medium", required=False)
                },
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )

            if st.button("💾 Uložit trénink", type="primary"):
                seznam_k_ulozeni = []
                for _, row in edited_df.iterrows():
                    cas_str = str(row["Čas"]).strip()
                    # Kontrola, zda není čas prázdný nebo "nan"
                    if cas_str and cas_str.lower() != "nan" and cas_str != "None" and cas_str != "":
                        seznam_k_ulozeni.append({
                            "id_zavodnika": row["id_zavodnika"],
                            "cas": cas_str
                        })
                
                if not seznam_k_ulozeni:
                    st.warning("Nebyl vyplněn žádný čas k uložení.")
                else:
                    batch_id = str(uuid.uuid4())[:8]
                    datum_str = datum.strftime("%Y-%m-%d")

                    pocet, chyby = worker.uloz_hromadne_zaznamy(
                        typ_zaznamu="jizda",
                        seznam_raw_dat=seznam_k_ulozeni,
                        jmeno_trati=vybrana_trat,
                        datum=datum_str,
                        id_zaznamu_spolecne=batch_id
                    )

                    if pocet > 0:
                        st.success(f"✅ Úspěšně uloženo {pocet} záznamů.")
                        time.sleep(1)
                        st.rerun()
                    if chyby:
                        st.error(f"Chyby: {chyby}")

    # --- INDIVIDUÁLNÍ ZÁPIS (EXPANDER) ---
    st.write("")
    with st.expander("➕ Vložit pouze jednotlivce (mimo skupinu)", expanded=False):
        ic1, ic2 = st.columns([1, 2])
        with ic1:
            ind_skupiny = ["Všechny"] + sorted(list(db_skupiny.keys()))
            ind_skupina = st.selectbox("Filtr skupiny:", ind_skupiny, key="ind_grp")
        
        with ic2:
            vsechni = list(db_zavodnici.values())
            filtr_zav = [z for z in vsechni if z.skupina == ind_skupina] if ind_skupina != "Všechny" else vsechni
            filtr_zav.sort(key=lambda z: z.prijmeni)
            
            # Mapa pro selectbox: "Příjmení Jméno" -> ID
            mapa_zav = {f"{z.prijmeni} {z.jmeno} ({z.skupina})": z.id_osoby for z in filtr_zav}
            ind_zavodnik_key = st.selectbox("Závodník:", list(mapa_zav.keys()), index=None, placeholder="Vyberte...", key="ind_sel")

        ic3, ic4, ic5 = st.columns(3)
        with ic3:
            ind_trat = st.selectbox("Trať:", trate_list, key="ind_trt", index=0 if trate_list else None)
        with ic4:
            ind_datum = st.date_input("Datum:", datetime.date.today(), key="ind_date")
        with ic5:
            ind_cas = st.text_input("Čas:", key="ind_time", placeholder="1:23,45")

        if st.button("Uložit jednotlivce", type="secondary"):
            if ind_zavodnik_key and ind_trat and ind_cas:
                worker.uloz_hromadne_zaznamy(
                    "jizda", 
                    [{"id_zavodnika": mapa_zav[ind_zavodnik_key], "cas": ind_cas}],
                    ind_trat, 
                    ind_datum.strftime("%Y-%m-%d"), 
                    str(uuid.uuid4())[:8]
                )
                st.success("✅ Uloženo.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Vyplňte všechna pole.")


# ==============================================================================
# TAB 2: ÚPRAVA A MAZÁNÍ (EDITOR)
# ==============================================================================
with tab_upravy:
    st.subheader("✏️ Úprava uložených časů")
    st.info("Změňte čas nebo datum přímo v tabulce a stiskněte 'Uložit změny'. Pro smazání zaškrtněte políčko 'Smazat'.")

    ec1, ec2 = st.columns(2)
    with ec1:
        edit_skupiny = sorted(list(db_skupiny.keys()))
        filtr_edit_skupina = st.selectbox("Skupina k úpravě:", edit_skupiny, key="edit_grp_sel")

    with ec2:
        edit_trate = sorted(list(db_trate.keys()))
        filtr_edit_trat = st.selectbox("Trať k úpravě:", edit_trate, key="edit_trt_sel")

    if filtr_edit_skupina and filtr_edit_trat:
        
        # 1. PŘÍPRAVA DAT (Získání ID objektů místo indexů)
        data_k_uprave = []
        
        # Procházíme Session State db_jizdy
        for jizda in db_jizdy:
            if (jizda.zavodnik_obj.skupina == filtr_edit_skupina and jizda.trat.jmeno_trati == filtr_edit_trat):
                
                # Převod string data na datetime.date pro editor
                d_date = None
                if jizda.datum:
                    try:
                        d_date = datetime.datetime.strptime(jizda.datum, "%Y-%m-%d").date()
                    except:
                        pass
                
                data_k_uprave.append({
                    "id_zaznamu": jizda.id_zaznamu,  # KLÍČOVÝ IDENTIFIKÁTOR
                    "Datum": d_date,
                    "Příjmení": jizda.zavodnik_obj.prijmeni,
                    "Jméno": jizda.zavodnik_obj.jmeno,
                    "Čas": jizda.cas,
                    "Smazat": False
                })

        if not data_k_uprave:
            st.info("Žádné záznamy pro tuto kombinaci nenalezeny.")
        else:
            # Řazení pro hezčí zobrazení (od nejnovějších)
            df_edit = pd.DataFrame(data_k_uprave).sort_values(by=["Datum", "Příjmení"], ascending=[False, True])
            
            edited_data = st.data_editor(
                df_edit,
                column_config={
                    "id_zaznamu": None, # Skryjeme ID, uživatel ho nepotřebuje vidět
                    "Datum": st.column_config.DateColumn("Datum", format="DD.MM.YYYY", required=True),
                    "Příjmení": st.column_config.TextColumn(disabled=True),
                    "Jméno": st.column_config.TextColumn(disabled=True),
                    "Čas": st.column_config.TextColumn("Čas", required=True),
                    "Smazat": st.column_config.CheckboxColumn("Smazat?", default=False)
                },
                hide_index=True,
                use_container_width=True,
                key="editor_jizdy_final"
            )

            # 2. ULOŽENÍ ZMĚN
            if st.button("💾 Uložit změny v tabulce", type="primary"):
                zmeny_provedeny = False
                ids_to_delete = set()
                updates = {} # {id_zaznamu: {datum: ..., cas: ...}}

                # A) Načtení změn z editoru
                for _, row in edited_data.iterrows():
                    row_id = row["id_zaznamu"]
                    
                    if row["Smazat"]:
                        ids_to_delete.add(row_id)
                        zmeny_provedeny = True
                    else:
                        # Datum zpět na string
                        new_date_str = row["Datum"].strftime("%Y-%m-%d") if row["Datum"] else ""
                        new_cas = str(row["Čas"])
                        updates[row_id] = (new_date_str, new_cas)

                # B) Aplikace změn do session_state (db_jizdy)
                # Musíme iterovat přes kopii nebo chytře, protože budeme mazat
                nove_jizdy = []
                for jizda in db_jizdy:
                    jid = jizda.id_zaznamu
                    
                    # 1. Je určen ke smazání? -> Nepřidáme do nového seznamu
                    if jid in ids_to_delete:
                        continue 
                    
                    # 2. Máme update?
                    if jid in updates:
                        nove_datum, novy_cas = updates[jid]
                        if jizda.datum != nove_datum or jizda.cas != novy_cas:
                            jizda.datum = nove_datum
                            jizda.cas = novy_cas
                            zmeny_provedeny = True
                    
                    # Zachováme jízdu
                    nove_jizdy.append(jizda)

                # C) Provedení aktualizace v paměti a na disku
                if zmeny_provedeny:
                    # Aktualizujeme globální list v session state
                    # (Protože db_jizdy je reference na session state list, musíme ho vyčistit a naplnit, 
                    # nebo nahradit v session state a re-inicalizovat workera, ale nejčistší je clear+extend)
                    db_jizdy.clear()
                    db_jizdy.extend(nove_jizdy)
                    
                    # Voláme backend pro přepis souboru
                    worker.prepis_soubor_jizd()
                    
                    st.success("✅ Změny úspěšně uloženy!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("Nebyly provedeny žádné změny.")