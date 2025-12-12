import unittest
from backend import *

class TestBackendDetailed(unittest.TestCase):

    def setUp(self):
        # Příprava testovacích dat
        self.zavodnik = Zavodnik("Jan", "Novák", "1", "1990", "A")

    def test_nacti_a_sluc_zavodniky(self):
        try:
            # Simulace načítání závodníků z CSV
            databaze_zavodniku = {}
            nacti_a_sluc_zavodniky(databaze_zavodniku, "test_zavodnici.csv")
            self.assertIn("1", databaze_zavodniku)
            self.assertEqual(databaze_zavodniku["1"].jmeno, "Jan")
        except Exception as e:
            print("Chyba při načítání a slučování závodníků:", e)
            raise

if __name__ == "__main__":
    unittest.main()