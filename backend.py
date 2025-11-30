"""
Soubor: backend.py (MINIMÁLNÍ VERZE)

Tento soubor obsahuje POUZE definice tříd, aby 
frontend.py prošel importem.

Váš úkol je implementovat VŠECHNY metody (__init__, ...)
a atributy tak, aby frontend.py přestal padat na chyby.
"""

# --- IMPORTY (potřebné pro práci se soubory a CSV) ---
import os
import pandas as pd

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

def nacti_a_sluc_zavodniky(databaze_zavodniku, path: str = None):
    # Zde 'path' může být cesta k externímu exportu (např. "C:/Downloads/export.csv")
    path = path or ZAVODNICI_CSV
    
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, dtype=str).fillna("")
            for _, r in df.iterrows():
                idz = r["id_zavodnika"]
                if idz not in databaze_zavodniku:
                    databaze_zavodniku[idz] = Zavodnik(r["jmeno"], r["prijmeni"], idz, r["rok_nar"], r["skupina"])
                else:
                    z = databaze_zavodniku[idz]
                    z.jmeno, z.prijmeni, z.rok_nar, z.skupina = r["jmeno"], r["prijmeni"], r["rok_nar"], r["skupina"]
        except Exception as e:
            print(f"WARN: {e}")

    # --- OKAMŽITÉ ULOŽENÍ ---
    uloz_zavodniky(databaze_zavodniku)


    return databaze_zavodniku        

# --- DEFINICE UKLÁDACÍ FUNKCE ---
def uloz_skupiny(databaze_skupin, path: str = None):
    path = path or SKUPINY_CSV
    
    rows = []
    for s in databaze_skupin.values():
        # Ukládáme jen název, členové se generují dynamicky
        rows.append({
            "jmeno_skupiny": s.jmeno_skupiny
        })
        
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, mode='w')
    else:
        open(path, 'w').close()

# --- NAČÍTACÍ FUNKCE (S AUTOMATICKÝM ULOŽENÍM) ---
def nacti_a_sluc_skupiny(databaze_skupin, databaze_zavodniku, path: str = None):
    cesta_k_nacteni = path or SKUPINY_CSV
    
    # 1. Načtení existujících skupin
    if os.path.exists(cesta_k_nacteni):
        try:
            df = pd.read_csv(cesta_k_nacteni, dtype=str).fillna("")
            for _, r in df.iterrows():
                js = r["jmeno_skupiny"]
                if js not in databaze_skupin:
                    databaze_skupin[js] = Skupina(jmeno_skupiny=js)
        except Exception: pass

    # 2. Dopočítání členů a chybějících skupin ze závodníků
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

    # --- OKAMŽITÉ ULOŽENÍ ---
    uloz_skupiny(databaze_skupin)

    
    return databaze_skupin

# --- DEFINICE UKLÁDACÍ FUNKCE ---
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

# --- NAČÍTACÍ FUNKCE (S AUTOMATICKÝM ULOŽENÍM) ---
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

    # --- OKAMŽITÉ ULOŽENÍ ---
    # Uložíme aktuální stav do hlavního souboru TRATI_CSV
    uloz_trate(databaze_trati)
    # ------------------------

    return databaze_trati

def nacti_zaznamy(databaze_zavodniku, path_jizdy: str = None, path_zavody: str = None):
    

    databaze_jizd = []
    databaze_zavodu = []

    path_jizdy = path_jizdy or JIZDY_CSV
    path_zavody = path_zavody or ZAVODY_CSV

    # --- 2. ČÁST: Načtení jízd ---
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

    # --- 3. ČÁST: Načtení závodů ---
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
# jak je to s class prace s databazi? potrebuju ji a k cemu mi je?

class PraceSDatabazi:
    def __init__(self, databaze_jizd, databaze_zavodu, databaze_zavodniku):
        

        self._databaze_jizd = databaze_jizd
        self._databaze_zavodu = databaze_zavodu
        self.databaze_zavodniku = databaze_zavodniku

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
            cas = polozka.get("cas", "")         # Může být prázdné
            umisteni = polozka.get("umisteni", "") # Může být prázdné (jen u závodů)
            
            zavodnik = self.databaze_zavodniku.get(idz)
            
            if not zavodnik:
                chyby.append(f"ID {idz}: Závodník nenalezen")
                continue

# --- LOGIKA PRO JÍZDU (TRÉNINK) ---
# U tréninku je ČAS povinný
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

            # --- LOGIKA PRO ZÁVOD ---
            elif typ_zaznamu == "zavod":
                # U závodu stačí BUĎ čas, NEBO umístění (nebo oboje)
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
                "jmeno": j.zavodnik_obj.jmeno,
                "prijmeni": j.zavodnik_obj.prijmeni,
                "rok_nar": j.zavodnik_obj.rok_nar,
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

    # --- ZÁPIS NA DISK (APPEND) ---
    def uloz_data_do_csv(self):
        """Uloží BUFFER (novinky) pomocí mode='a'."""
        
        # Jízdy
        if self._nove_jizdy:
            rows = self._sestav_rows_jizdy(self._nove_jizdy)
            df = pd.DataFrame(rows)
            header_needed = not os.path.exists(JIZDY_CSV)
            df.to_csv(JIZDY_CSV, mode="a", header=header_needed, index=False)
            self._nove_jizdy = [] 

        # Závody
        if self._nove_zavody:
            rows = self._sestav_rows_zavody(self._nove_zavody)
            df = pd.DataFrame(rows)
            header_needed = not os.path.exists(ZAVODY_CSV)
            df.to_csv(ZAVODY_CSV, mode="a", header=header_needed, index=False)
            self._nove_zavody = [] 

        return True

    # --- DEDUPLIKACE ---
    def deduplikuj_zaznamy(self):
        """Vyčistí paměť a PŘEPÍŠE soubory (mode='w')."""
        def klic(zaznam):
            return (
                zaznam.zavodnik_obj.jmeno, 
                zaznam.zavodnik_obj.prijmeni, 
                zaznam.datum, 
                getattr(zaznam, "cas", ""), 
                getattr(zaznam.trat, "jmeno_trati", ""),
                getattr(zaznam, "umisteni", "")
            )

        # 1. Jízdy
        videne = set()
        ciste = []
        for j in self._databaze_jizd:
            k = klic(j)
            if k not in videne:
                videne.add(k)
                ciste.append(j)
        self._databaze_jizd = ciste
        self._nove_jizdy = [] 

        # 2. Závody
        videne = set()
        ciste = []
        for z in self._databaze_zavodu:
            k = klic(z)
            if k not in videne:
                videne.add(k)
                ciste.append(z)
        self._databaze_zavodu = ciste
        self._nove_zavody = []

        # 3. Zápis (REWRITE)
        if self._databaze_jizd:
            rows = self._sestav_rows_jizdy(self._databaze_jizd)
            pd.DataFrame(rows).to_csv(JIZDY_CSV, mode="w", index=False)
        
        if self._databaze_zavodu:
            rows = self._sestav_rows_zavody(self._databaze_zavodu)
            pd.DataFrame(rows).to_csv(ZAVODY_CSV, mode="w", index=False)
        
        return True
    
    
class Vyhledavani:
    def __init__(self, databaze):
        self.db = databaze

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

    def dle_id_zavodnika(self, id_zavodnika):
        zavody = []
        jizdy = []

        for z in self.db._databaze_zavodu:
            if z.zavodnik_obj.id_osoby == id_zavodnika:
                zavody.append(z)

        for j in self.db._databaze_jizd:
            if j.zavodnik_obj.id_osoby == id_zavodnika:
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

    def dle_skupiny(self, skupina):

        zavody = []
        jizdy = []

        for z in self.db._databaze_zavodu:
            if z.zavodnik_obj.skupina == skupina:
                zavody.append(z)

        for j in self.db._databaze_jizd:
            if j.zavodnik_obj.skupina == skupina:
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

    def dle_trate(self, jmeno_trati):

        zavody = []
        jizdy = []

        for z in self.db._databaze_zavodu:
            if z.trat.jmeno_trati == jmeno_trati:
                zavody.append(z)

        for j in self.db._databaze_jizd:
            if j.trat.jmeno_trati == jmeno_trati:
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

    # --------------------------------------------------------
    # 2) VYHLEDÁVÁNÍ PODLE DATA / OBDOBÍ
    # --------------------------------------------------------

    def dle_data(self, datum):

        zavody = []
        jizdy = []

        for z in self.db._databaze_zavodu:
            if z.datum == datum:
                zavody.append(z)

        for j in self.db._databaze_jizd:
            if j.datum == datum:
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

    def za_obdobi(self, datum_od, datum_do):

        zavody = []
        jizdy = []

        for z in self.db._databaze_zavodu:
            if datum_od <= z.datum <= datum_do:
                zavody.append(z)

        for j in self.db._databaze_jizd:
            if datum_od <= j.datum <= datum_do:
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

    # --------------------------------------------------------
    # 3) KOMBINOVANÉ VYHLEDÁVÁNÍ (praktické pro UI)
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

        for z in self.db._databaze_zavodu:
            if id_zavodnika is not None and z.zavodnik_obj.id_osoby != id_zavodnika:
                continue
            if jmeno is not None and z.zavodnik_obj.jmeno != jmeno:
                continue
            if prijmeni is not None and z.zavodnik_obj.prijmeni != prijmeni:
                continue
            if skupina is not None and z.zavodnik_obj.skupina != skupina:
                continue
            if trat is not None and z.trat.jmeno_trati != trat:
                continue
            if datum_od is not None and z.datum < datum_od:
                continue
            if datum_do is not None and z.datum > datum_do:
                continue

            zavody.append(z)

        for j in self.db._databaze_jizd:
            if id_zavodnika is not None and j.zavodnik_obj.id_osoby != id_zavodnika:
                continue
            if jmeno is not None and j.zavodnik_obj.jmeno != jmeno:
                continue
            if prijmeni is not None and j.zavodnik_obj.prijmeni != prijmeni:
                continue
            if skupina is not None and j.zavodnik_obj.skupina != skupina:
                continue
            if trat is not None and j.trat.jmeno_trati != trat:
                continue
            if datum_od is not None and j.datum < datum_od:
                continue
            if datum_do is not None and j.datum > datum_do:
                continue

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
