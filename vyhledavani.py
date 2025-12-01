class Vyhledavani:
    def __init__(self, databaze_jizd, databaze_zavodu, databaze_zavodniku, databaze_trati, databaze_skupin):
        # 1. PŘÍMÝ PŘÍSTUP K DATŮM (už žádné self.db)
        self._databaze_jizd = databaze_jizd
        self._databaze_zavodu = databaze_zavodu
        self.databaze_zavodniku = databaze_zavodniku
        self.databaze_trati = databaze_trati
        self.databaze_skupin = databaze_skupin

    # ========================================================
    # ČÁST A: Metody pro Dropdown menu (Přesunuto z PraceSDatabazi)
    # ========================================================

    def vrat_seznam_trati(self):
        """Vrátí seznam názvů tratí pro Combobox."""
        if self.databaze_trati:
            return sorted(list(self.databaze_trati.keys()))
        return []

    def vrat_seznam_skupin(self):
        """Vrátí seznam názvů skupin pro Combobox."""
        if self.databaze_skupin:
            return sorted(list(self.databaze_skupin.keys()))
        return []
    
    def vrat_zavodniky_ve_skupine(self, nazev_skupiny):
        """Původní metoda pro získání seznamu objektů/tuple."""
        vybrani = []
        for zavodnik in self.databaze_zavodniku.values():
            if zavodnik.skupina == nazev_skupiny:
                radek = (zavodnik.jmeno, zavodnik.prijmeni, zavodnik.rok_nar)
                vybrani.append(radek)
        
        vybrani.sort(key=lambda z: z[0]) # Řazení podle jména
        return vybrani

    def get_seznam_zavodniku_formatovany(self):
        """NOVÉ: Vrátí 'Příjmení Jméno (ID)' pro výběr v GUI."""
        seznam = []
        for z in self.databaze_zavodniku.values():
            polozka = f"{z.prijmeni} {z.jmeno} ({z.id_osoby})"
            seznam.append(polozka)
        return sorted(seznam)

    # ========================================================
    # ČÁST B: Vaše PŮVODNÍ filtrovací logika (Zachováno 100%)
    # (Jen upraveno self.db -> self)
    # ========================================================

    def dle_jmena(self, jmeno, prijmeni):
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

    def filtruj(self, jmeno=None, prijmeni=None, id_zavodnika=None,
                skupina=None, trat=None, datum_od=None, datum_do=None):
        """Univerzální filtr (zachovaný z vašeho kódu)."""
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

        return self._serad_vystup(zavody, jizdy)

    # ========================================================
    # ČÁST C: Pomocné metody (Řazení + Formátování pro GUI)
    # ========================================================

    def _serad_vystup(self, zavody, jizdy):
        """Interní metoda pro seřazení výsledků (jak jste měl v původním kódu)."""
        zavody.sort(key=lambda z: (z.trat.jmeno_trati, z.zavodnik_obj.id_osoby, z.datum))
        jizdy.sort(key=lambda j: (j.trat.jmeno_trati, j.zavodnik_obj.id_osoby, j.datum))
        return zavody, jizdy

    def _formatuj_vystup_pro_tabulku(self, zavody, jizdy):
        """Převede objekty na textové řádky pro Treeview."""
        vystup = []
        # Závody
        for z in zavody:
            vystup.append((z.datum, "Závod", z.zavodnik_obj.jmeno, z.zavodnik_obj.prijmeni, 
                           z.zavodnik_obj.skupina, z.trat.jmeno_trati, z.cas, z.umisteni))
        # Jízdy
        for j in jizdy:
            vystup.append((j.datum, "Trénink", j.zavodnik_obj.jmeno, j.zavodnik_obj.prijmeni, 
                           j.zavodnik_obj.skupina, j.trat.jmeno_trati, j.cas, "-"))
        
        # Řadíme primárně podle data sestupně pro přehlednost v tabulce
        vystup.sort(key=lambda x: x[0], reverse=True)
        return vystup

    # ========================================================
    # ČÁST D: "Wrapper" metody pro Frontend (Vrátí hotová data)
    # ========================================================

    def vrat_data_pro_tabulku_filtrovana(self, **kwargs):
        """
        Zavolá 'filtruj' s parametry a rovnou vrátí naformátovaná data pro tabulku.
        Použití: vyhledavac.vrat_data_pro_tabulku_filtrovana(trat="Brno", skupina="A")
        """
        z, j = self.filtruj(**kwargs)
        return self._formatuj_vystup_pro_tabulku(z, j)

    def vrat_vsechna_data_pro_tabulku(self):
        """Vrátí úplně vše."""
        return self._formatuj_vystup_pro_tabulku(self._databaze_zavodu, self._databaze_jizd)