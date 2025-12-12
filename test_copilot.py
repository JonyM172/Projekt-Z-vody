import unittest
from backend import *

class TestBackend(unittest.TestCase):

    def setUp(self):
        # Příprava testovacích dat
        self.zavodnik = Zavodnik("Jan", "Novák", "1", "1990", "A")
        self.trat = Trat("Trať 1")
        self.jizda = TestovaciJizda(self.zavodnik, self.trat, "00:30:00", "2025-12-01", "1")
        self.zavod = Zavod(self.zavodnik, self.trat, "00:25:00", "1", "2025-12-01", "2")

    def test_zavodnik_init(self):
        # Test inicializace závodníka
        self.assertEqual(self.zavodnik.jmeno, "Jan")
        self.assertEqual(self.zavodnik.prijmeni, "Novák")
        self.assertEqual(self.zavodnik.id_osoby, "1")
        self.assertEqual(self.zavodnik.rok_nar, "1990")
        self.assertEqual(self.zavodnik.skupina, "A")

    def test_uloz_zavodniky(self):
        # Test ukládání závodníků
        databaze_zavodniku = {"1": self.zavodnik}
        uloz_zavodniky(databaze_zavodniku, "test_zavodnici.csv")
        with open("test_zavodnici.csv", "r") as f:
            obsah = f.read()
        self.assertIn("Jan", obsah)
        self.assertIn("Novák", obsah)

    def test_nacti_a_sluc_zavodniky(self):
        # Test načítání závodníků
        databaze_zavodniku = {}
        nacti_a_sluc_zavodniky(databaze_zavodniku, "test_zavodnici.csv")
        self.assertIn("1", databaze_zavodniku)
        self.assertEqual(databaze_zavodniku["1"].jmeno, "Jan")

    def test_vyhledavani_dle_jmena(self):
        # Test vyhledávání podle jména
        databaze_zavodniku = {"1": self.zavodnik}
        databaze_jizd = [self.jizda]
        databaze_zavodu = [self.zavod]
        vyhledavani = Vyhledavani(databaze_jizd, databaze_zavodu, databaze_zavodniku, {}, {})
        zavody, jizdy = vyhledavani.dle_jmena("Jan", "Novák")
        self.assertEqual(len(zavody), 1)
        self.assertEqual(len(jizdy), 1)

if __name__ == "__main__":
    unittest.main()