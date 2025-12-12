class PraceSDatabazi:
    def __init__(self):
        # ✅ BUFFER — trvalý v paměti
        self._databaze_jizd = []
        self._databaze_zavodu = []
        
        # ✅ NOVÉ: STAGING — dočasný pro "na uložení"
        self._nove_jizdy_k_ulozeni = []
        self._nove_zavody_k_ulozeni = []
    
    def uloz_jizdu(self, testovaci_jizda):
        # ✅ ZMĚNA: Teď přidává do BUFFERU i do STAGING
        self._databaze_jizd.append(testovaci_jizda)          # ← BUFFER
        self._nove_jizdy_k_ulozeni.append(testovaci_jizda)   # ← STAGING (NOVÉ)

    def uloz_zavod(self, zavod):
        # ✅ ZMĚNA: Teď přidává do BUFFERU i do STAGING
        self._databaze_zavodu.append(zavod)                  # ← BUFFER
        self._nove_zavody_k_ulozeni.append(zavod)            # ← STAGING (NOVÉ)

    # ✅ NOVÉ METODY: Pomocné pro staging
    def _sestav_rows_jizdy_staging(self):
        """Sestaví řádky POUZE z nových dat (staging)."""
        rows = []
        for j in self._nove_jizdy_k_ulozeni:  # ← STAGING (NOVÉ)
            rows.append({
                "id_zaznamu": j.id_zaznamu,
                "id_zavodnika": j.zavodnik_obj.id_osoby,
                "datum": j.datum,
                "trat": j.trat.jmeno_trati,
                "cas": j.cas
            })
        return rows

    def _sestav_rows_zavody_staging(self):
        """Sestaví řádky POUZE z nových dat (staging)."""
        rows = []
        for z in self._nove_zavody_k_ulozeni:  # ← STAGING (NOVÉ)
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

    # ✅ NOVÉ METODY: Pomocné pro buffer (deduplikaci)
    def _sestav_rows_jizdy_buffer(self):
        """Sestaví řádky ze VŠECH dat v bufferu."""
        rows = []
        for j in self._databaze_jizd:  # ← BUFFER (všechno)
            rows.append({
                "id_zaznamu": j.id_zaznamu,
                "id_zavodnika": j.zavodnik_obj.id_osoby,
                "datum": j.datum,
                "trat": j.trat.jmeno_trati,
                "cas": j.cas
            })
        return rows

    def _sestav_rows_zavody_buffer(self):
        """Sestaví řádky ze VŠECH dat v bufferu."""
        rows = []
        for z in self._databaze_zavodu:  # ← BUFFER (všechno)
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

    def uloz_data_do_csv(self):
        # ✅ ZMĚNA: Uloží POUZE NOVÁ data ze staging (ne vše!)
        if self._nove_jizdy_k_ulozeni:  # ← STAGING (NOVÉ)
            rows_jizdy = self._sestav_rows_jizdy_staging()  # ← STAGING metoda (NOVÁ)
            df_jizdy = pd.DataFrame(rows_jizdy)
            df_jizdy.to_csv(JIZDY_CSV, mode="a", header=not os.path.exists(JIZDY_CSV), index=False)

        if self._nove_zavody_k_ulozeni:  # ← STAGING (NOVÉ)
            rows_zavody = self._sestav_rows_zavody_staging()  # ← STAGING metoda (NOVÁ)
            df_zavody = pd.DataFrame(rows_zavody)
            df_zavody.to_csv(ZAVODY_CSV, mode="a", header=not os.path.exists(ZAVODY_CSV), index=False)

        # ✅ ZMĚNA: Vyčistit POUZE staging (buffer zůstane!)
        self._nove_jizdy_k_ulozeni = []      # ← STAGING (NOVÉ)
        self._nove_zavody_k_ulozeni = []     # ← STAGING (NOVÉ)

        return True

    def deduplikuj_zaznamy(self):
        """
        Odstraní duplicitní záznamy v jízdách i závodech.
        Nechá první výskyt, další shodné smaže.
        Poté uloží data do CSV s mode="w" (PŘEPÍŠE).
        """
        # ... (deduplikace zůstává stejná) ...

        # ✅ ZMĚNA: Uloží VEŠKERÁ data z bufferu (ne jen nová!)
        if self._databaze_jizd:
            rows_jizdy = self._sestav_rows_jizdy_buffer()  # ← BUFFER metoda (NOVÁ)
            df_jizdy = pd.DataFrame(rows_jizdy)
            df_jizdy.to_csv(JIZDY_CSV, mode="w", index=False)

        if self._databaze_zavodu:
            rows_zavody = self._sestav_rows_zavody_buffer()  # ← BUFFER metoda (NOVÁ)
            df_zavody = pd.DataFrame(rows_zavody)
            df_zavody.to_csv(ZAVODY_CSV, mode="w", index=False)

        # ✅ NOVÉ: Vyčistit i staging
        self._nove_jizdy_k_ulozeni = []      # ← (NOVÉ)
        self._nove_zavody_k_ulozeni = []     # ← (NOVÉ)

        return True