import unittest
from backend import *
import os

class TestBackend(unittest.TestCase):

    def setUp(self):
        # Příprava testovacích dat
        self.zavodnik = Zavodnik("Jan", "Novák", "1", "1990", "A")
        self.trat = Trat("Trať 1")
        self.jizda = TestovaciJizda(self.zavodnik, self.trat, "00:30:00", "2025-12-01", "1")
        self.zavod = Zavod(self.zavodnik, self.trat, "00:25:00", "1", "2025-12-01", "2")
        self.databaze_zavodniku = {"1": self.zavodnik}
        self.databaze_jizd = [self.jizda]
        self.databaze_zavodu = [self.zavod]
        self.databaze_trati = {"Trať 1": self.trat}
        self.databaze_skupin = {"A": Skupina("A")}

    # 1. Testy tříd
    def test_classes(self):
        self.assertEqual(self.zavodnik.jmeno, "Jan")
        self.assertEqual(self.trat.jmeno_trati, "Trať 1")
        self.assertEqual(self.jizda.cas, "00:30:00")
        self.assertEqual(self.zavod.umisteni, "1")

    # 2. Test importu z CSV
    def test_csv_import(self):
        try:
            nacti_a_sluc_zavodniky(self.databaze_zavodniku, "zavodnici.csv")
            self.assertIn("1", self.databaze_zavodniku)
        except Exception as e:
            self.fail(f"Import CSV selhal: {e}")

    # 3. Test nacti_a_sluc funkcí
    def test_nacti_a_sluc(self):
        try:
            nacti_a_sluc_skupiny(self.databaze_skupin, self.databaze_zavodniku, "skupiny.csv")
            self.assertIn("A", self.databaze_skupin)
            nacti_a_sluc_trate(self.databaze_trati, "trati.csv")
            self.assertIn("Trať 1", self.databaze_trati)
        except Exception as e:
            self.fail(f"nacti_a_sluc funkce selhaly: {e}")

    # 4. Test uloz_data_do_csv
    def test_uloz_data_do_csv(self):
        try:
            prace = PraceSDatabazi(self.databaze_jizd, self.databaze_zavodu, self.databaze_zavodniku, self.databaze_trati, self.databaze_skupin)
            prace.uloz_data_do_csv()
            self.assertTrue(os.path.exists("databaze_jizd.csv"))
            self.assertTrue(os.path.exists("databaze_zavodu.csv"))
        except Exception as e:
            self.fail(f"uloz_data_do_csv selhalo: {e}")

    # 5. Test deduplikuj_zaznamy
    def test_deduplikuj_zaznamy(self):
        try:
            prace = PraceSDatabazi(self.databaze_jizd, self.databaze_zavodu, self.databaze_zavodniku, self.databaze_trati, self.databaze_skupin)
            prace.deduplikuj_zaznamy()
            self.assertEqual(len(prace._databaze_jizd), 1)
            self.assertEqual(len(prace._databaze_zavodu), 1)
        except Exception as e:
            self.fail(f"deduplikuj_zaznamy selhalo: {e}")

    # 6. Test vrat_seznam funkcí
    def test_vrat_seznam_functions(self):
        try:
            vyhledavani = Vyhledavani(self.databaze_jizd, self.databaze_zavodu, self.databaze_zavodniku, self.databaze_trati, self.databaze_skupin)
            trate = vyhledavani.vrat_seznam_trati()
            skupiny = vyhledavani.vrat_seznam_skupin()
            self.assertIn("Trať 1", trate)
            self.assertIn("A", skupiny)
        except Exception as e:
            self.fail(f"vrat_seznam funkce selhaly: {e}")

if __name__ == "__main__":
    unittest.main()