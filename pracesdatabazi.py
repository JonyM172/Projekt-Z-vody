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