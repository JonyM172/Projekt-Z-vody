# --- IMPORTY (potřebné pro práci se soubory a CSV) ---
import shutil
import os
import pandas as pd
import streamlit as st

# --- NÁZEV SOUBORU SE ZÁVODNÍKY ---
ZAVODNICI_CSV = "zavodnici.csv"
SKUPINY_CSV = "skupiny.csv"
ZAZNAMY_CSV = "zaznamy.csv"
ZAVODY_CSV = "databaze_zavodu.csv"
JIZDY_CSV = "databaze_jizd.csv"
TRATI_CSV = "trati.csv"


# --- DEFINICE TŘÍD ---
class Trat:
    def __init__(self, jmeno_trati):
        self.jmeno_trati = jmeno_trati


class Osoba:
    def __init__(self, jmeno, prijmeni, id_osoby):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.id_osoby = id_osoby


class Zavodnik(Osoba):
     def __init__(self, jmeno, prijmeni, id_osoby, rok_nar, skupina):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.id_osoby = id_osoby
        self.rok_nar = rok_nar
        self.skupina = skupina

        #rok nar = rok narození
        

class Trener(Osoba):
    def __init__ (self, jmeno, prijmeni, email, id_osoby, skupiny):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.email = email
        self.id_osoby = id_osoby
        self.skupiny = skupiny

class Skupina:
    def __init__(self, jmeno_skupiny):
        self.jmeno_skupiny = jmeno_skupiny
        self.clenove = []  # Seznam objektů (závodníků), kteří sem patří

class Zaznam:
    def __init__(self, jmeno, prijmeni, cas, datum, id_zaznamu):
        self.jmeno = jmeno
        self.prijmeni = prijmeni
        self.cas = cas
        self.datum = datum
        self.id_zaznamu = id_zaznamu
        self._stav = "Platný"           # Výchozí stav záznamu       


class TestovaciJizda:
    def __init__(self, zavodnik_obj, trat, cas, datum, id_zaznamu):
        self.zavodnik_obj = zavodnik_obj
        self.trat = trat
        self.cas = cas
        self.datum = datum
        self.id_zaznamu = id_zaznamu
        self._stav = "Platný"           # Výchozí stav nové jizdy
        

class Zavod:
    def __init__(self, zavodnik_obj, trat, cas, umisteni, datum, id_zaznamu):
        self.zavodnik_obj = zavodnik_obj
        self.trat = trat
        self.cas = cas
        self.umisteni = umisteni
        self.datum = datum
        self.id_zaznamu = id_zaznamu
        self._stav = "Platný"           # Výchozí stav závodu
        # self._prirazeny_urednik = None  # Výchozí nepřiřazeno
        
def zkontroluj_soubory():

    soubory = {
        ZAVODNICI_CSV: "Závodníci",
        SKUPINY_CSV: "Skupiny",
        ZAVODY_CSV: "Závody",
        JIZDY_CSV: "Jízdy",
        TRATI_CSV: "Tratě"
    }

    for cesta, popis in soubory.items():
        if not os.path.exists(cesta):
            print(f"WARN: Soubor '{cesta}' ({popis}) nenalezen.")

# Zavolání kontroly souborů při spuštění
zkontroluj_soubory()



def inicializuj_aplikaci():
    """
    Zkontroluje Session State. Pokud data chybí (start aplikace nebo F5), načte je z CSV.
    Pokud data existují, nedělá nic.
    """
    # Kontrolujeme klíčový prvek, např. 'databaze_jizd'
    if 'databaze_jizd' not in st.session_state or 'databaze_zavodniku' not in st.session_state:
        
        # 1. Inicializace prázdných kontejnerů
        db_zavodnici = {}
        db_skupiny = {}
        db_trate = {}
        
        # 2. Načtení dat 
        nacti_a_sluc_zavodniky(db_zavodnici)
        nacti_a_sluc_skupiny(db_skupiny, db_zavodnici)
        nacti_a_sluc_trate(db_trate)
        
        # Načtení jízd a závodů (vrací seznamy)
        db_jizdy, db_zavody = nacti_zaznamy(db_zavodnici)

        # 3. Uložení do Streamlit Session State
        st.session_state['databaze_zavodniku'] = db_zavodnici
        st.session_state['databaze_skupin'] = db_skupiny
        st.session_state['databaze_trati'] = db_trate
        st.session_state['databaze_jizd'] = db_jizdy
        st.session_state['databaze_zavodu'] = db_zavody
        

        st.session_state['data_nactena'] = True
        

# PRACE S DATABAZÍ 

def uloz_zavodniky(databaze_zavodniku, path: str = None):
    # Pokud nezadáme cestu, uloží se to do hlavního souboru ZAVODNICI_CSV
    path = path or ZAVODNICI_CSV
    
    rows = []
    for z in databaze_zavodniku.values():
        rows.append({
            "id_zavodnika": z.id_osoby,
            "jmeno": z.jmeno,
            "prijmeni": z.prijmeni,
            "rok_nar": z.rok_nar,
            "skupina": z.skupina
        })
    
    # Uložíme (přepíšeme soubor čistými daty)
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, mode='w')
    else:
        open(path, 'w').close()

def nacti_a_sluc_zavodniky(databaze_zavodniku, path: str = None, export_path: str = None):
    """
    Načte závodníky z hlavního souboru a exportovaného souboru, sloučí je a uloží zpět.
    """
    path = path or ZAVODNICI_CSV  # Hlavní soubor
    export_path = export_path or "export_zavodnici.csv"  # Exportovaný soubor

    # 1. Načtení existujících závodníků z hlavního souboru
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, dtype=str).fillna("")
            for _, r in df.iterrows():
                idz = r["id_zavodnika"]
                if idz not in databaze_zavodniku:
                    databaze_zavodniku[idz] = Zavodnik(
                        jmeno=r["jmeno"],
                        prijmeni=r["prijmeni"],
                        id_osoby=idz,
                        rok_nar=r["rok_nar"],
                        skupina=r["skupina"]
                    )
        except Exception as e:
            print(f"WARN: Chyba při načítání hlavního souboru: {e}")

    # 2. Načtení nových závodníků z exportovaného souboru
    if os.path.exists(export_path):
        try:
            df = pd.read_csv(export_path, dtype=str).fillna("")
            for _, r in df.iterrows():
                idz = r["id_zavodnika"]
                if idz not in databaze_zavodniku:
                    # Přidání nového závodníka
                    databaze_zavodniku[idz] = Zavodnik(
                        jmeno=r["jmeno"],
                        prijmeni=r["prijmeni"],
                        id_osoby=idz,
                        rok_nar=r["rok_nar"],
                        skupina=r["skupina"]
                    )
                else:
                    # Aktualizace existujícího závodníka
                    z = databaze_zavodniku[idz]
                    z.jmeno = r["jmeno"]
                    z.prijmeni = r["prijmeni"]
                    z.rok_nar = r["rok_nar"]
                    z.skupina = r["skupina"]
        except Exception as e:
            print(f"WARN: Chyba při načítání exportovaného souboru: {e}")
#závodníci se naonec needitují v aplikaci kvůli souladu s klubovým informačním systémem
    # 3. Uložení aktualizované databáze zpět do hlavního souboru
    uloz_zavodniky(databaze_zavodniku)

    return databaze_zavodniku        

# --- DEFINICE UKLÁDACÍ FUNKCE ---
def uloz_skupiny(databaze_skupin, path: str = None):
    path = path or SKUPINY_CSV
    
    rows = []
    for s in databaze_skupin.values():
        # Ukládáme jen název, členové se generují ze souboru zavodnici
        rows.append({
            "jmeno_skupiny": s.jmeno_skupiny
        })
        
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, mode='w')
    else:
        open(path, 'w').close()

# načtení + uložení
def nacti_a_sluc_skupiny(databaze_skupin, databaze_zavodniku, path: str = None, export_path: str = None):
    """
    Načte skupiny z hlavního souboru a exportovaného souboru, sloučí je a uloží zpět.
    """
    cesta_k_nacteni = path or SKUPINY_CSV  # Hlavní soubor
    export_path = export_path or "export_skupiny.csv"  # Exportovaný soubor

    # 1. Načtení existujících skupin z hlavního souboru
    if os.path.exists(cesta_k_nacteni):
        try:
            df = pd.read_csv(cesta_k_nacteni, dtype=str).fillna("")
            for _, r in df.iterrows():
                js = r["jmeno_skupiny"]
                if js not in databaze_skupin:
                    databaze_skupin[js] = Skupina(jmeno_skupiny=js)
        except Exception as e:
            print(f"WARN: Chyba při načítání hlavního souboru: {e}")

    # 2. Načtení nových skupin z exportovaného souboru
    if os.path.exists(export_path):
        try:
            df = pd.read_csv(export_path, dtype=str).fillna("")
            for _, r in df.iterrows():
                js = r["jmeno_skupiny"]
                if js not in databaze_skupin:
                    # Přidání nové skupiny
                    databaze_skupin[js] = Skupina(jmeno_skupiny=js)
        except Exception as e:
            print(f"WARN: Chyba při načítání exportovaného souboru: {e}")

    # 3. Dopočítání členů a chybějících skupin ze závodníků
    # Reset členů, aby se nekupili
    for g in databaze_skupin.values():
        g.clenove = []

    for z in databaze_zavodniku.values():
        if z.skupina:
            if z.skupina not in databaze_skupin:
                # Pokud skupina neexistuje, vytvoříme ji
                databaze_skupin[z.skupina] = Skupina(jmeno_skupiny=z.skupina)
            
            # Přidáme člena
            databaze_skupin[z.skupina].clenove.append(z)

    # 4. Uložení aktualizované databáze zpět do hlavního souboru
    uloz_skupiny(databaze_skupin)

    return databaze_skupin


def uloz_trate(databaze_trati, path: str = None):
    path = path or TRATI_CSV
    
    rows = []
    for t in databaze_trati.values():
        rows.append({
            "jmeno_trati": t.jmeno_trati
        })
        
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, mode='w')
    else:
        open(path, 'w').close()


def nacti_a_sluc_trate(databaze_trati, path: str = None):
    # Path může být externí soubor pro import
    cesta_k_nacteni = path or TRATI_CSV

    if os.path.exists(cesta_k_nacteni):
        try:
            df = pd.read_csv(cesta_k_nacteni, dtype=str).fillna("")
            for _, r in df.iterrows():
                jt = r["jmeno_trati"]
                if jt not in databaze_trati:
                    databaze_trati[jt] = Trat(jmeno_trati=jt)
        except Exception as e:
            print(f"WARN: {e}")

 
    # Uložíme do TRATI_CSV
    uloz_trate(databaze_trati)
    # ------------------------

    return databaze_trati

def nacti_zaznamy(databaze_zavodniku, path_jizdy: str = None, path_zavody: str = None):
    

    databaze_jizd = []
    databaze_zavodu = []

    path_jizdy = path_jizdy or JIZDY_CSV
    path_zavody = path_zavody or ZAVODY_CSV

    #  Načtení jízd 
    if os.path.exists(path_jizdy):
        try:
            df_j = pd.read_csv(path_jizdy, dtype=str).fillna("")
        except Exception as e:
            print(f"WARN: Nepodařilo se načíst '{JIZDY_CSV}': {e}")
            df_j = pd.DataFrame()

        for _, r in df_j.iterrows():
            idz = r.get("id_zavodnika")
            zavodnik_obj = databaze_zavodniku.get(idz)

            # Pokud existuje závodník, vytvoříme objekt a přidáme do seznamu
            if zavodnik_obj:
                j = TestovaciJizda(
                    zavodnik_obj=zavodnik_obj,
                    trat=Trat(r["trat"]),
                    cas=r["cas"],
                    datum=r["datum"],
                    id_zaznamu=r["id_zaznamu"]
                )
                databaze_jizd.append(j)
            else :
                jm = r.get("jmeno", "?")
                pr = r.get("prijmeni", "?")
                print(f"WARN: Závodník {jm} {pr} (ID: {idz}) nenalezen. Závod (ID záznamu: {r.get('id_zaznamu')}) přeskočen.")

    #  Načtení závodů ---
    if os.path.exists(path_zavody):
        try:
            df_z = pd.read_csv(path_zavody, dtype=str).fillna("")
        except Exception as e:
            print(f"WARN: Nepodařilo se načíst '{ZAVODY_CSV}': {e}")
            df_z = pd.DataFrame()

        for _, r in df_z.iterrows():
            idz = r.get("id_zavodnika")
            zavodnik_obj = databaze_zavodniku.get(idz)

            if zavodnik_obj:
                z = Zavod(
                    zavodnik_obj=zavodnik_obj,
                    trat=Trat(r["trat"]),
                    cas=r["cas"],
                    umisteni=r.get("umisteni", ""),
                    datum=r["datum"],
                    id_zaznamu=r["id_zaznamu"]
                )
                databaze_zavodu.append(z)
            else:
                # Závodník nenalezen -> výpis varování a pokračujeme
                jm = r.get("jmeno", "?")
                pr = r.get("prijmeni", "?")
                # ZDE JE PŘIDANÁ HLÁŠKA PRO ZÁVODY
                print(f"WARN: Závodník {jm} {pr} (ID: {idz}) nenalezen. Závod (ID záznamu: {r.get('id_zaznamu')}) přeskočen.")

    # 4. Vrátíme nově vytvořené a naplněné seznamy
    return databaze_jizd, databaze_zavodu
# jak je to s class prace s databazi? potrebuji ji a k cemu mi je?

class PraceSDatabazi:
    def __init__(self, databaze_jizd, databaze_zavodu, databaze_zavodniku, 
                 databaze_trati, databaze_skupin):
        
        self._databaze_jizd = databaze_jizd
        self._databaze_zavodu = databaze_zavodu
        self.databaze_zavodniku = databaze_zavodniku
        self.databaze_trati = databaze_trati
        self.databaze_skupin = databaze_skupin

        self._nove_jizdy = []
        self._nove_zavody = []

    # --- INTERNÍ UKLÁDÁNÍ (JEDEN ZÁZNAM) ---
    def uloz_jizdu(self, testovaci_jizda):
        self._databaze_jizd.append(testovaci_jizda)
        self._nove_jizdy.append(testovaci_jizda)

    def uloz_zavod(self, zavod):
        self._databaze_zavodu.append(zavod)
        self._nove_zavody.append(zavod)

    # --- HROMADNÉ UKLÁDÁNÍ (PRO FRONTEND) ---
    def uloz_hromadne_zaznamy(self, typ_zaznamu, seznam_raw_dat, jmeno_trati, datum, id_zaznamu_spolecne):
        objekt_trati = Trat(jmeno_trati)
        ulozono_pocet = 0
        chyby = []
        
        for polozka in seznam_raw_dat:
            idz = polozka.get("id_zavodnika")
            cas = polozka.get("cas", "")
            umisteni = polozka.get("umisteni", "")
            
            zavodnik = self.databaze_zavodniku.get(idz)
            
            if not zavodnik:
                chyby.append(f"ID {idz}: Závodník nenalezen")
                continue

            if typ_zaznamu == "jizda":
                if cas:
                    nova_jizda = TestovaciJizda(
                        zavodnik_obj=zavodnik,
                        trat=objekt_trati,
                        cas=cas,
                        datum=datum,
                        id_zaznamu=id_zaznamu_spolecne
                    )
                    self.uloz_jizdu(nova_jizda)
                    ulozono_pocet += 1
                else:
                    # Pokud není čas -> ignorujeme řádek
                    continue 

            elif typ_zaznamu == "zavod":
                if cas or umisteni:
                    novy_zavod = Zavod(
                        zavodnik_obj=zavodnik,
                        trat=objekt_trati,
                        cas=cas,
                        umisteni=umisteni,
                        datum=datum,
                        id_zaznamu=id_zaznamu_spolecne
                    )
                    self.uloz_zavod(novy_zavod)
                    ulozono_pocet += 1
                else:
                    # Pokud není ani čas, ani umístění -> ignorujeme řádek
                    continue
        
        if ulozono_pocet > 0:
            self.uloz_data_do_csv()
            
        return ulozono_pocet, chyby
    

    # --- POMOCNÉ METODY PRO CSV ---
    def _sestav_rows_jizdy(self, zdrojovy_seznam):
        rows = []
        for j in zdrojovy_seznam:
            rows.append({
                "id_zaznamu": j.id_zaznamu,
                "id_zavodnika": j.zavodnik_obj.id_osoby,
                "datum": j.datum,
                "trat": j.trat.jmeno_trati,
                "cas": j.cas
            })
        return rows

    def _sestav_rows_zavody(self, zdrojovy_seznam):
        rows = []
        for z in zdrojovy_seznam:
            rows.append({
                "id_zaznamu": z.id_zaznamu,
                "id_zavodnika": z.zavodnik_obj.id_osoby,
                "jmeno": z.zavodnik_obj.jmeno,
                "prijmeni": z.zavodnik_obj.prijmeni,
                "rok_nar": z.zavodnik_obj.rok_nar,
                "datum": z.datum,
                "trat": z.trat.jmeno_trati,
                "cas": z.cas,
                "umisteni": z.umisteni
            })
        return rows

    # --- ZÁPIS NA DISK ---
    def uloz_data_do_csv(self):

        #jizdty
        if self._nove_jizdy:
            rows = self._sestav_rows_jizdy(self._nove_jizdy)
            df = pd.DataFrame(rows)
            header_needed = not os.path.exists(JIZDY_CSV)
            df.to_csv(JIZDY_CSV, mode="a", header=header_needed, index=False)
            self._nove_jizdy = [] 

        # zavody
        if self._nove_zavody:
            rows = self._sestav_rows_zavody(self._nove_zavody)
            df = pd.DataFrame(rows)
            header_needed = not os.path.exists(ZAVODY_CSV)
            df.to_csv(ZAVODY_CSV, mode="a", header=header_needed, index=False)
            self._nove_zavody = [] 
        return True
    
    def prepis_soubor_jizd(self):
        """
        Bezpečně přepíše CSV soubor.
        1. Vytvoří zálohu (.bak) původního souboru.
        2. Zkontroluje, zda nechceme omylem smazat všechna data.
        """
        
        # --- POJISTKA 1: VYTVOŘENÍ ZÁLOHY ---
        if os.path.exists(JIZDY_CSV):
            try:
                # Vytvoří kopii: databaze_jizd.csv -> databaze_jizd.csv.bak
                shutil.copyfile(JIZDY_CSV, JIZDY_CSV + ".bak")
            except Exception as e:
                print(f"WARN: Nepodařilo se vytvořit zálohu: {e}")

        # Příprava dat
        rows = []
        for j in self._databaze_jizd:
            rows.append({
                "id_zaznamu": j.id_zaznamu,
                "id_zavodnika": j.zavodnik_obj.id_osoby,
                "datum": j.datum,
                "trat": j.trat.jmeno_trati,
                "cas": j.cas
            })
        
        # --- POJISTKA 2: OCHRANA PROTI OMYLU (PRÁZDNÝ SEZNAM) ---
        # Pokud je seznam prázdný, je to podezřelé. 
        # Opravdu chceme smazat celou databázi?
        if not rows:
            # Zkontrolujeme, jestli původní soubor nebyl velký
            # Pokud soubor existoval a měl data, a my teď chceme zapsat 0 řádků -> STOP.
            puvodni_velikost = os.path.getsize(JIZDY_CSV) if os.path.exists(JIZDY_CSV) else 0
            
            if puvodni_velikost > 100: # 100 bytů je cca hlavička + 1 řádek
                print("CRITICAL ERROR: Pokus o smazání celé databáze jízd zablokován!")
                return False # Zápis se neprovede, data jsou zachráněna

            # Pokud byl soubor malý nebo neexistoval, asi opravdu mažeme vše (nebo začínáme)
            with open(JIZDY_CSV, 'w') as f:
                f.write("id_zaznamu,id_zavodnika,datum,trat,cas\n")
            return True

        # --- ZÁPIS (pokud máme data) ---
        df = pd.DataFrame(rows)
        df.to_csv(JIZDY_CSV, index=False, mode='w')
        
        return True

    # --- DEDUPLIKACE ZÁZNAMŮ ---
    def deduplikuj_zaznamy(self):
        def klic(zaznam):
            return (
                zaznam.zavodnik_obj.jmeno, 
                zaznam.zavodnik_obj.prijmeni, 
                zaznam.datum, 
                getattr(zaznam, "cas", ""), 
                getattr(zaznam.trat, "jmeno_trati", ""),
                getattr(zaznam, "umisteni", "")
            )

        # Jízdy
        videne = set()
        ciste = []
        for j in self._databaze_jizd:
            k = klic(j)
            if k not in videne:
                videne.add(k)
                ciste.append(j)
        self._databaze_jizd = ciste
        self._nove_jizdy = [] 

        # Závody
        videne = set()
        ciste = []
        for z in self._databaze_zavodu:
            k = klic(z)
            if k not in videne:
                videne.add(k)
                ciste.append(z)
        self._databaze_zavodu = ciste
        self._nove_zavody = []

        # Zápis
        if self._databaze_jizd:
            rows = self._sestav_rows_jizdy(self._databaze_jizd)
            pd.DataFrame(rows).to_csv(JIZDY_CSV, mode="w", index=False)
        
        if self._databaze_zavodu:
            rows = self._sestav_rows_zavody(self._databaze_zavodu)
            pd.DataFrame(rows).to_csv(ZAVODY_CSV, mode="w", index=False)
        return True
    

class Vyhledavani:
    def __init__(self, databaze_jizd, databaze_zavodu, databaze_zavodniku, databaze_trati, databaze_skupin):
        # 1. PŘÍMÝ PŘÍSTUP K DATŮM
        # Zde si data uložíme přímo do instance 'Vyhledavani'
        self._databaze_jizd = databaze_jizd
        self._databaze_zavodu = databaze_zavodu
        self.databaze_zavodniku = databaze_zavodniku
        self.databaze_trati = databaze_trati
        self.databaze_skupin = databaze_skupin

    
    # Metody pro Dropdown menu (Data pro výběry)

    def vrat_seznam_trati(self):
        """Vrátí abecedně seřazený seznam názvů tratí."""
        if self.databaze_trati:
            return sorted(list(self.databaze_trati.keys()))
        return []

    def vrat_seznam_skupin(self):
        """Vrátí abecedně seřazený seznam názvů skupin."""
        if self.databaze_skupin:
            return sorted(list(self.databaze_skupin.keys()))
        return []
    
    def vrat_zavodniky_ve_skupine(self, nazev_skupiny):
        """Vrátí seznam n-tic (Jméno, Příjmení, Rok) pro danou skupinu."""
        vybrani = []
        for zavodnik in self.databaze_zavodniku.values():
            if zavodnik.skupina == nazev_skupiny:
                radek = (zavodnik.jmeno, zavodnik.prijmeni, zavodnik.rok_nar)
                vybrani.append(radek)
        
        vybrani.sort(key=lambda z: z[0]) # Řazení podle jména
        return vybrani

    def get_seznam_zavodniku_formatovany(self):
        """Vrátí seznam 'Příjmení Jméno (ID)' pro výběr konkrétní osoby."""
        seznam = []
        for z in self.databaze_zavodniku.values():
            polozka = f"{z.prijmeni} {z.jmeno} ({z.id_osoby})"
            seznam.append(polozka)
        return sorted(seznam)

 
    #  Pomocné metody (Řazení + Formátování pro Frontend) 

    def _serad_vystup(self, zavody, jizdy):
        """
        Pomocná metoda: Sjednotí řazení na jednom místě.
        Pokud budete chtít změnit priority řazení, změníte to jen zde.
        """
        zavody.sort(key=lambda z: (z.trat.jmeno_trati, z.zavodnik_obj.id_osoby, z.datum))
        jizdy.sort(key=lambda j: (j.trat.jmeno_trati, j.zavodnik_obj.id_osoby, j.datum))
        return zavody, jizdy

    def _formatuj_vystup_pro_tabulku(self, zavody, jizdy):
        """
        Pomocná metoda: Převede objekty na seznam textových řádků pro Treeview.
        Výstup: List n-tic (Datum, Typ, Jméno, Příjmení, Skupina, Trať, Čas, Umístění)
        """
        vystup = []
        
        # 1. Závody
        for z in zavody:
            vystup.append((
                z.datum, "Závod", z.zavodnik_obj.jmeno, z.zavodnik_obj.prijmeni, 
                z.zavodnik_obj.skupina, z.trat.jmeno_trati, z.cas, z.umisteni
            ))
            
        # 2. Jízdy (Tréninky)
        for j in jizdy:
            vystup.append((
                j.datum, "Trénink", j.zavodnik_obj.jmeno, j.zavodnik_obj.prijmeni, 
                j.zavodnik_obj.skupina, j.trat.jmeno_trati, j.cas, "-"
            ))
        
        # Pro tabulku řadíme podle data sestupně (nejnovější nahoře)
        vystup.sort(key=lambda x: x[0], reverse=True)
        return vystup

   

    """ 
    # --------------------------------------------------------
    # 1) VYHLEDÁVÁNÍ PODLE JMEN / ID / SKUPINY / TRATĚ
    # --------------------------------------------------------

    def dle_jmena(self, jmeno, prijmeni):
        zavody = []
        jizdy = []

        for z in self.db._databaze_zavodu:
            if z.zavodnik_obj.jmeno == jmeno and z.zavodnik_obj.prijmeni == prijmeni:
                zavody.append(z)

        for j in self.db._databaze_jizd:
            if j.zavodnik_obj.jmeno == jmeno and j.zavodnik_obj.prijmeni == prijmeni:
                jizdy.append(j)

        zavody.sort(key=lambda z: (
            z.trat.jmeno_trati,
            z.zavodnik_obj.id_osoby,
            z.datum
        ))

        jizdy.sort(key=lambda j: (
            j.trat.jmeno_trati,
            j.zavodnik_obj.id_osoby,
            j.datum
        ))

        return zavody, jizdy
"""

        # následující zápis je totéž zkrácenou formou

    # ========================================================
    # ČÁST D: Logika vyhledávání (Opraveno self.db -> self._databaze...)
    # ========================================================

    def dle_jmena(self, jmeno, prijmeni):
        # OPRAVA: Místo self.db._databaze... voláme self._databaze...
        zavody = [z for z in self._databaze_zavodu if z.zavodnik_obj.jmeno == jmeno and z.zavodnik_obj.prijmeni == prijmeni]
        jizdy = [j for j in self._databaze_jizd if j.zavodnik_obj.jmeno == jmeno and j.zavodnik_obj.prijmeni == prijmeni]
        return self._serad_vystup(zavody, jizdy)

    def dle_id_zavodnika(self, id_zavodnika):
        zavody = [z for z in self._databaze_zavodu if z.zavodnik_obj.id_osoby == id_zavodnika]
        jizdy = [j for j in self._databaze_jizd if j.zavodnik_obj.id_osoby == id_zavodnika]
        return self._serad_vystup(zavody, jizdy)

    def dle_skupiny(self, skupina):
        zavody = [z for z in self._databaze_zavodu if z.zavodnik_obj.skupina == skupina]
        jizdy = [j for j in self._databaze_jizd if j.zavodnik_obj.skupina == skupina]
        return self._serad_vystup(zavody, jizdy)

    def dle_trate(self, jmeno_trati):
        zavody = [z for z in self._databaze_zavodu if z.trat.jmeno_trati == jmeno_trati]
        jizdy = [j for j in self._databaze_jizd if j.trat.jmeno_trati == jmeno_trati]
        return self._serad_vystup(zavody, jizdy)

    def dle_data(self, datum):
        zavody = [z for z in self._databaze_zavodu if z.datum == datum]
        jizdy = [j for j in self._databaze_jizd if j.datum == datum]
        return self._serad_vystup(zavody, jizdy)

    def za_obdobi(self, datum_od, datum_do):
        zavody = [z for z in self._databaze_zavodu if datum_od <= z.datum <= datum_do]
        jizdy = [j for j in self._databaze_jizd if datum_od <= j.datum <= datum_do]
        return self._serad_vystup(zavody, jizdy)

    # --------------------------------------------------------
    # UNIVERZÁLNÍ FILTR
    # --------------------------------------------------------

    def filtruj(self, jmeno=None, prijmeni=None, id_zavodnika=None,
                skupina=None, trat=None, datum_od=None, datum_do=None):
        """
        Univerzální filtr:
        - cokoliv z parametrů může být None = nefiltruje se podle toho
        - vrací (zavody, jizdy)
        """
        zavody = []
        jizdy = []


        for z in self._databaze_zavodu:
            if id_zavodnika is not None and z.zavodnik_obj.id_osoby != id_zavodnika: continue
            if jmeno is not None and z.zavodnik_obj.jmeno != jmeno: continue
            if prijmeni is not None and z.zavodnik_obj.prijmeni != prijmeni: continue
            if skupina is not None and z.zavodnik_obj.skupina != skupina: continue
            if trat is not None and z.trat.jmeno_trati != trat: continue
            if datum_od is not None and z.datum < datum_od: continue
            if datum_do is not None and z.datum > datum_do: continue
            zavody.append(z)

        for j in self._databaze_jizd:
            if id_zavodnika is not None and j.zavodnik_obj.id_osoby != id_zavodnika: continue
            if jmeno is not None and j.zavodnik_obj.jmeno != jmeno: continue
            if prijmeni is not None and j.zavodnik_obj.prijmeni != prijmeni: continue
            if skupina is not None and j.zavodnik_obj.skupina != skupina: continue
            if trat is not None and j.trat.jmeno_trati != trat: continue
            if datum_od is not None and j.datum < datum_od: continue
            if datum_do is not None and j.datum > datum_do: continue
            jizdy.append(j)

        # Použití nové pomocné metody pro řazení 
        return self._serad_vystup(zavody, jizdy)

    def najdi_nejlepsi_vykony(jizdy_df):
        """
        Najde nejlepší výkon každého závodníka na dané trati.

        Args:
            jizdy_df (pd.DataFrame): DataFrame obsahující sloupce 'id_zavodnika', 'trat', a 'cas'.

        Returns:
            pd.DataFrame: DataFrame obsahující pouze nejlepší výkony.
        """
        if not all(col in jizdy_df.columns for col in ['id_zavodnika', 'trat', 'cas']):
            raise ValueError("DataFrame musí obsahovat sloupce 'id_zavodnika', 'trat' a 'cas'.")

        # Převod času na sekundy pro porovnání
        def time_to_seconds(time_str):
            try:
                parts = time_str.split(":")
                minutes = int(parts[0])
                seconds = float(parts[1].replace(",", "."))
                return minutes * 60 + seconds
            except (ValueError, AttributeError):
                return float('inf')

        # Přidání pomocného sloupce pro porovnání
        jizdy_df = jizdy_df.copy()
        jizdy_df['cas_v_sekundach'] = jizdy_df['cas'].apply(time_to_seconds)

        # Výběr nejlepšího výkonu pro každého závodníka na každé trati
        nejlepsi_vykony = jizdy_df.loc[
            jizdy_df.groupby(['id_zavodnika', 'trat'])['cas_v_sekundach'].idxmin()
        ]

        # Odstranění pomocného sloupce
        nejlepsi_vykony = nejlepsi_vykony.drop(columns=['cas_v_sekundach'])

        return nejlepsi_vykony

