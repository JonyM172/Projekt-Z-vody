import git_filter_repo as fr
import os

# --- NASTAVENÍ ---
# Cesta k souboru v repozitáři (musí být bytes = písmeno b před uvozovkami)
TARGET_FILENAME = b"databaze_jizd.csv"

# Cesta k souboru na disku (název souboru, jak ho máte ve složce)
SOURCE_FILE_ON_DISK = "databaze_jizd.csv"
# -----------------

print(f"Načítám obsah souboru: {SOURCE_FILE_ON_DISK}...")

if not os.path.exists(SOURCE_FILE_ON_DISK):
    print(f"CHYBA: Soubor '{SOURCE_FILE_ON_DISK}' nebyl nalezen!")
    exit(1)

with open(SOURCE_FILE_ON_DISK, 'rb') as f:
    new_content = f.read()

print(f"Velikost nového obsahu: {len(new_content)} bytů.")

# --- OPRAVENÁ FUNKCE ---
# Zde byla chyba: odstranil jsem argument 'commit', nyní jsou jen dva.
def my_blob_callback(blob, metadata):
    # OPRAVA: Cesta se nachází v metadata.filename
    if metadata.filename == TARGET_FILENAME:
        blob.data = new_content

print("Spouštím přepisování historie git repozitáře...")

try:
    # --force povolí běh i na repozitáři, který není čerstvým klonem
    args = fr.FilteringOptions.parse_args(['--force'])
    fr.RepoFilter(args, blob_callback=my_blob_callback).run()
    print("Hotovo. Soubor v historii byl nahrazen.")
except Exception as e:
    print(f"\nNastala chyba: {e}")
    print("Tip: Ujistěte se, že nemáte otevřené soubory v jiném programu.")