import backend

print("--- ZAČÍNÁ TEST BACKENDU ---")

# 1. NAČTENÍ DAT
# Připravíme prázdné slovníky
zavodnici = {}
trate = {}
skupiny = {}

print("\n>>> 1. Načítám číselníky...")
# Načteme závodníky, tratě a skupiny
backend.nacti_a_sluc_zavodniky(zavodnici)
backend.nacti_a_sluc_trate(trate)
backend.nacti_a_sluc_skupiny(skupiny, zavodnici)

print(f"   -> Načteno {len(zavodnici)} závodníků.")
print(f"   -> Načteno {len(trate)} tratí.")
print(f"   -> Načteno {len(skupiny)} skupin.")

print("\n>>> 2. Načítám záznamy (jízdy a závody)...")
print("(Zde očekávejte výpis WARN hlášek - to je správně, testujeme chyby v datech!)")
print("-" * 40)

# Toto je klíčový moment - zde se projeví, zda program spadne na špatných datech
jizdy_list, zavody_list = backend.nacti_zaznamy(zavodnici)

print("-" * 40)
print(f"   -> Úspěšně načteno {len(jizdy_list)} platných jízd.")
print(f"   -> Úspěšně načteno {len(zavody_list)} platných závodů.")

# 2. INICIALIZACE TŘÍD
# Propojení dat s logikou
vyhledavac = backend.Vyhledavani(jizdy_list, zavody_list, zavodnici, trate, skupiny)

# 3. TEST VYHLEDÁVÁNÍ
print("\n>>> 3. Test vyhledávání (Filtry)...")

# A) Hledáme podle jména (Test diakritiky)
print("   A) Hledám: 'Jiří Vašek'")
data_vasek = vyhledavac.vrat_data_pro_tabulku_filtrovana(prijmeni="Vašek")
for radek in data_vasek:
    print(f"      Nalezeno: {radek}")

# B) Hledáme ELITE jezdce (Test nových dat)
print("\n   B) Hledám skupinu: 'Elite'")
data_elite = vyhledavac.vrat_data_pro_tabulku_filtrovana(skupina="Elite")
for radek in data_elite:
    print(f"      Nalezeno: {radek}")

# C) Hledáme podle tratě (Test Comboboxu)
print("\n   C) Test seznamu tratí pro menu:")
seznam_trati = vyhledavac.vrat_seznam_trati()
print(f"      {seznam_trati}")
# Zde bychom měli vidět i tu "překlepovou" trať 'neexistujici_trat_překlep', 
# pokud ji backend načetl z chybné jízdy (což je validní chování).

print("\n--- TEST ÚSPĚŠNĚ DOKONČEN ---")
if len(jizdy_list) > 0 and len(data_elite) > 0:
    print("✅ VŠE FUNGUJE JAK MÁ!")
else:
    print("❌ NĚCO JE ŠPATNĚ (žádná data?)")