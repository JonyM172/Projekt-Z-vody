import git_filter_repo as fr
import os

# --- NASTAVENÍ ---
# Název souboru v historii, který chceme přepsat
# Musí mít před uvozovkami 'b' (bytes)
TARGET_FILENAME = b"databaze_jizd.csv"

# Název souboru na disku, který slouží jako správný vzor
SOURCE_FILE_ON_DISK = "databaze_jizd.csv"
# -----------------

print(f"Načítám vzorový soubor: {SOURCE_FILE_ON_DISK}...")

# 1. Načtení nového obsahu
if not os.path.exists(SOURCE_FILE_ON_DISK):
    print(f"CHYBA: Soubor '{SOURCE_FILE_ON_DISK}' nebyl nalezen!")
    exit(1)

with open(SOURCE_FILE_ON_DISK, 'rb') as f:
    new_content = f.read()

print(f"Načteno {len(new_content)} bytů. Jdu přepisovat historii...")

# 2. Funkce pro nahrazení (upravená pro vaši verzi)
def my_blob_callback(blob, metadata):
    # Pokud jméno souboru v commitu odpovídá našemu cíli
    if metadata.filename == TARGET_FILENAME:
        # Nahradíme obsah
        blob.data = new_content

# 3. Spuštění procesu
try:
    # --force je nutné, aby to běželo i když to není čistý klon
    args = fr.FilteringOptions.parse_args(['--force'])
    
    fr.RepoFilter(args, blob_callback=my_blob_callback).run()
    
    print("\n------------------------------------------------")
    print("HOTOVO! Historie byla přepsána.")
    print("Nyní musíte změny odeslat na server příkazem:")
    print("git push origin --force --all")
    print("------------------------------------------------")

except Exception as e:
    print(f"\nNastala chyba: {e}")