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
ZAZNAMY_CSV = "zaznamy.csv"
ZAVODY_CSV = "databaze_zavodu.csv"
JIZDY_CSV = "databaze_jizd.csv"


# --- DEFINICE TŘÍD ---
class Trat:
    def __init__(self,jmeno_trati):
        self.jmeno_trati=jmeno_trati


class Osoba:
    def __init__(self,jmeno,prijmeni,id_osoby):
        self.jmeno=jmeno
        self.prijmeni=prijmeni
        self.id_osoby=id_osoby


class Zavodnik(Osoba):
     def __init__(self, jmeno, prijmeni,id_osoby,rok_nar, skupina):
        self.jmeno=jmeno
        self.prijmeni=prijmeni
        self.id_osoby=id_osoby
        self.rok_nar=rok_nar
        self.skupina=skupina

        #rok nar = rok narození
        
        
class Trener(Osoba):
    def __init__ (self, jmeno, prijmeni, email, id_osoby,skupiny):
        self.jmeno=jmeno
        self.prijmeni=prijmeni
        self.email=email
        self.id_osoby=id_osoby
        self.skupiny=skupiny


class zaznam:
    def __init__(self, jmeno, prijmeni, cas, datum, id_zaznamu):
        self.jemno=jmeno
        self.prijmeni=prijmeni
        self.cas=cas
        self.datum = datum
        self.id_zaznamu = id_zaznamu
        self._stav = "Platný"           # Výchozí stav záznamu       


class Testovaci_jizda:
    def __init__(self, zavodnik_obj, trat, cas, datum, id_zaznamu):
        self.zavodnik_obj = zavodnik_obj
        self.trat=trat
        self.cas=cas
        self.datum = datum
        self.id_zaznamu = id_zaznamu
        self._stav = "Platný"           # Výchozí stav nové jizdy
        # self._prirazeny_urednik = None  # Výchozí nepřiřazeno

    # def prirad_urednika(self, urednik_obj):
    #     self._prirazeny_urednik = urednik_obj
    #     self._stav = "V řízení"
    # def zmen_stav(self,novy_stav):
    #     self._stav=novy_stav


class zavod:
    def __init__(self, zavodnik_obj, trat, cas, umisteni, datum, id_zaznamu):
        self.zavodnik_obj = zavodnik_obj
        self.trat=trat
        self.cas=cas
        self.umisteni=umisteni
        self.datum = datum
        self.id_zaznamu = id_zaznamu
        self._stav = "Platný"           # Výchozí stav závodu
        # self._prirazeny_urednik = None  # Výchozí nepřiřazeno
        
# PRACE S DATABAZÍ 

def nacti_a_sluc_zavodniky(databaze_zavodniku):
   
    # Pokud soubor neexistuje, není co načítat
    if not os.path.exists(ZAVODNICI_CSV):
        return databaze_zavodniku

    # Načteme soubor do DataFrame
    df = pd.read_csv(ZAVODNICI_CSV, dtype=str).fillna("")

    # Projdeme každý řádek v CSV
    for _, r in df.iterrows():
        idz = r["id_zavodnika"]

        # Pokud závodník ještě není v databázi -> vytvoříme ho
        if idz not in databaze_zavodniku:
            novy = Zavodnik(
                jmeno=r["jmeno"],
                prijmeni=r["prijmeni"],
                id_osoby=idz,
                rok_nar=r["rok_nar"],
                skupina=r["skupina"]
            )
            databaze_zavodniku[idz] = novy

        # Pokud už v databázi je -> jen mu přepíšeme nové údaje z CSV
        else:
            z = databaze_zavodniku[idz]
            z.jmeno = r["jmeno"]
            z.prijmeni = r["prijmeni"]
            z.rok_nar = r["rok_nar"]
            z.skupina = r["skupina"]

    return databaze_zavodniku


def nacti_zazmamy(zdroj, databaze_zavodniku):
        if not os.path.exists (ZAZNAMY_CSV):
            return zdroj
        
        df = pd.read_csv(ZAZNAMY_CSV, dtype=str).fillna("") 

        for _, r in df.iterrows(): 
            
            Zavodnik = databaze_zavodniku.get(r["id_zavodnika"])
            if Zavodnik is None:
                continue

            trat = Trat(r["trat"])

        # 3c) Podle typu vytvoříme správný objekt
        if r["typ"] == "test":
            j = Testovaci_jizda(trat, Zavodnik, r["datum"], r["id_zaznamu"])
            j.cas = r["cas"]
            j.umisteni = r["umisteni"]
            zdroj.uloz_jizdu(j)

        elif r["typ"] == "zavod":
            z = zavod(trat, Zavodnik, r["datum"], r["id_zaznamu"])
            z.cas = r["cas"]
            z.umisteni = r["umisteni"]
            zdroj.uloz_zavod(z)

    # 4) Vrátíme zdroj naplněný starými záznamy
        return zdroj

# jak je to s class prace s databazi? potrebuju ji a k cemu mi je?

class prace_s_databazi:
    def __init__(self):
        self._databaze_jizd = []
        self._databaze_zavodu = []
    def uloz_jizdu(self,testovaci_jizda):
        
        self._databaze_jizd.append(testovaci_jizda)
        nova_jizda = {
            "id_zaznamu": testovaci_jizda.id_zaznamu,
            "id_zavodnika": testovaci_jizda.zavodnik_obj.id_osoby,
            "jmeno": testovaci_jizda.zavodnik_obj.jmeno,
            "prijmeni": testovaci_jizda.zavodnik_obj.prijmeni,
            "rok_nar": testovaci_jizda.zavodnik_obj.rok_nar,
            "datum": testovaci_jizda.datum,
            "trat": testovaci_jizda.trat.jmeno_trati,
            "cas": testovaci_jizda.cas
        }

        df = pd.DataFrame([nova_jizda])
        df.to_csv("databaze_jizd.csv",
                  mode="a",                     # append
                  header=not os.path.exists("databaze_jizd.csv"),
                  index=False)


    def uloz_zavod(self,zavod):

        self._databaze_zavodu.append(zavod)
        novy_zavod = {
            "id_zaznamu": zavod.id_zaznamu,
            "id_zavodnika": zavod.zavodnik_obj.id_osoby,
            "jmeno": zavod.zavodnik_obj.jmeno,
            "prijmeni": zavod.zavodnik_obj.prijmeni,
            "rok_nar": zavod.zavodnik_obj.rok_nar,
            "datum": zavod.datum,
            "trat": zavod.trat.jmeno_trati,
            "cas": zavod.cas,
            "umisteni": zavod.umisteni
        }

        df = pd.DataFrame([novy_zavod])
        df.to_csv("databaze_zavodu.csv",
                  mode="a",
                  header=not os.path.exists("databaze_zavodu.csv"),
                  index=False)
        

    def deduplikuj_zaznamy(self):
        """
        Odstraní duplicitní záznamy v jízdách i závodech.
        Nechá první výskyt, další shodné smaže.
        """

        def klic(zaznam):

            jmeno = zaznam.zavodnik_obj.jmeno
            prijmeni = zaznam.zavodnik_obj.prijmeni
            skupina = getattr(zaznam.zavodnik_obj, "skupina", "")
            datum = zaznam.datum
            cas = getattr(zaznam, "cas", "")
            trat = getattr(zaznam.trat, "jmeno_trati", "")
            umisteni = getattr(zaznam, "umisteni", "")
            return (jmeno, prijmeni, skupina, datum, cas, trat, umisteni)

        # --- deduplikace jízd ---
        videne = set()
        nove_jizdy = []
        for j in self._databaze_jizd:
            k = klic(j)
            if k not in videne:
                videne.add(k)
                nove_jizdy.append(j)
        self._databaze_jizd = nove_jizdy

        # --- deduplikace závodů ---
        videne = set()
        nove_zavody = []
        for z in self._databaze_zavodu:
            k = klic(z)
            if k not in videne:
                videne.add(k)
                nove_zavody.append(z)
        self._databaze_zavodu = nove_zavody
        
        
    def najdi_dle_jmena(self, jmeno, prijmeni): # najde závody a testovací jízdy daného závodníka
        """Najde zavod/jizdu podle jména a přijímení závodníka"""
        jizdy = []
        zavody = []
        for testovaci_jizda in self._databaze_jizd:
            if testovaci_jizda.zavodnik_obj.jmeno == jmeno and testovaci_jizda.zavodnik_obj.prijmeni == prijmeni:
                jizdy.append(testovaci_jizda)
        
        for zavod in self._databaze_zavodu:
            if zavod.zavodnik_obj.jmeno == jmeno and zavod.zavodnik_obj.prijmeni == prijmeni:
                zavody.append(zavod)
        return zavody, jizdy 
    
    