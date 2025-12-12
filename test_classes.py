import unittest
from backend import *

class TestBackendClasses(unittest.TestCase):

    def test_trat_init(self):
        trat = Trat("Trať 1")
        self.assertEqual(trat.jmeno_trati, "Trať 1")

    def test_osoba_init(self):
        osoba = Osoba("Jan", "Novák", "1")
        self.assertEqual(osoba.jmeno, "Jan")
        self.assertEqual(osoba.prijmeni, "Novák")
        self.assertEqual(osoba.id_osoby, "1")

    def test_zavodnik_init(self):
        zavodnik = Zavodnik("Jan", "Novák", "1", "1990", "A")
        self.assertEqual(zavodnik.jmeno, "Jan")
        self.assertEqual(zavodnik.prijmeni, "Novák")
        self.assertEqual(zavodnik.id_osoby, "1")
        self.assertEqual(zavodnik.rok_nar, "1990")
        self.assertEqual(zavodnik.skupina, "A")

    def test_trener_init(self):
        trener = Trener("Petr", "Svoboda", "petr@svoboda.cz", "2", ["A", "B"])
        self.assertEqual(trener.jmeno, "Petr")
        self.assertEqual(trener.prijmeni, "Svoboda")
        self.assertEqual(trener.email, "petr@svoboda.cz")
        self.assertEqual(trener.id_osoby, "2")
        self.assertEqual(trener.skupiny, ["A", "B"])

    def test_skupina_init(self):
        skupina = Skupina("Skupina A")
        self.assertEqual(skupina.jmeno_skupiny, "Skupina A")
        self.assertEqual(skupina.clenove, [])

    def test_zaznam_init(self):
        zaznam = Zaznam("Jan", "Novák", "00:30:00", "2025-12-01", "1")
        self.assertEqual(zaznam.jmeno, "Jan")
        self.assertEqual(zaznam.prijmeni, "Novák")
        self.assertEqual(zaznam.cas, "00:30:00")
        self.assertEqual(zaznam.datum, "2025-12-01")
        self.assertEqual(zaznam.id_zaznamu, "1")
        self.assertEqual(zaznam._stav, "Platný")

    def test_testovaci_jizda_init(self):
        zavodnik = Zavodnik("Jan", "Novák", "1", "1990", "A")
        trat = Trat("Trať 1")
        jizda = TestovaciJizda(zavodnik, trat, "00:30:00", "2025-12-01", "1")
        self.assertEqual(jizda.zavodnik_obj, zavodnik)
        self.assertEqual(jizda.trat, trat)
        self.assertEqual(jizda.cas, "00:30:00")
        self.assertEqual(jizda.datum, "2025-12-01")
        self.assertEqual(jizda.id_zaznamu, "1")
        self.assertEqual(jizda._stav, "Platný")

    def test_zavod_init(self):
        zavodnik = Zavodnik("Jan", "Novák", "1", "1990", "A")
        trat = Trat("Trať 1")
        zavod = Zavod(zavodnik, trat, "00:25:00", "1", "2025-12-01", "2")
        self.assertEqual(zavod.zavodnik_obj, zavodnik)
        self.assertEqual(zavod.trat, trat)
        self.assertEqual(zavod.cas, "00:25:00")
        self.assertEqual(zavod.umisteni, "1")
        self.assertEqual(zavod.datum, "2025-12-01")
        self.assertEqual(zavod.id_zaznamu, "2")
        self.assertEqual(zavod._stav, "Platný")

if __name__ == "__main__":
    unittest.main()