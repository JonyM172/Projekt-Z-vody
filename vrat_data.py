# --- METODY PRO PŘÍPRAVU DAT PRO FRONTEND ---
    # Tyto metody volá grafické rozhraní, aby vědělo, co má zobrazit.

    def vrat_seznam_skupin(self):
        """
        Vrátí seznam všech unikátních skupin (např. ['A', 'B', 'Junioři']),
        aby je frontend mohl dát do vysouvacího menu.
        """
        skupiny = set()
        # Projdeme všechny závodníky a posbíráme názvy skupin
        for zavodnik in self.databaze_zavodniku.values():
            if zavodnik.skupina: # Pokud má vyplněnou skupinu
                skupiny.add(zavodnik.skupina)
        
        # Vrátíme seřazený seznam
        return sorted(list(skupiny))

    def vrat_zavodniky_ve_skupine(self, nazev_skupiny):
        """
        Vrátí seznam objektů závodníků, kteří patří do dané skupiny.
        Frontend podle tohoto seznamu vykreslí řádky tabulky.
        """
        vybrani = []
        for zavodnik in self.databaze_zavodniku.values():
            if zavodnik.skupina == nazev_skupiny:
                vybrani.append(zavodnik)
        
        # Seřadíme je abecedně podle příjmení
        vybrani.sort(key=lambda z: z.prijmeni)
        return vybrani