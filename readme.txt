# Projekt-Zavody
## Popis funkcí
Finální verze aplikace je na branch FINAL
Aplikace slouží k zápisu, vyhodnocení a zobrazení výsledků měření závodů a testovacích jízd ve sportovním klubu.  
(funkcionalita závodů je zatím nedostupná, protože se nevyužívá klub má připravené jen záznamy jízd).  
Těžištěm práce je backend a jeho implementace, frontend byl sestaven převážně pomocí Gemini a slouží k testování funkčnosti backendu.   
Aplikace umí zobrazovat dívějšíí záznamy z csv souborů, a do těchto souborů zapisovat nové záznamy pomocí intuitivního formuláře.  
Záznamy jdou také mazat a upravovat.  
Záložka testovací jízdy slouží především ke kontrole záznamů  
Záložky Trati a skupiny slouží k zobrazení záznamů jedna pro celkové pořadí - vyhodnocení napříč skupinami, druhá pořadí v rámci skupiny.  
Obě umožňují výběr trati a filtrování nejlepších výsledků pro každého závodníka (pokud měl více pokusů)
Záložka Vyhledávání umožňuje najít konkrétní záznam nebo závodníka pro osobní statistiky


## Jazyk a yyužívané knihovny:
Python 3.13.7  
streamlit - tvorba frontend  
pandas - práce s csv soubory  
os - načítání souborů přes path  
shutil - vytváření zálohy při mazání záznamů  

## spuštění 
spuštění virtuálního prostředí  
(v průzkumníku souborůsouborů otevřete složku projekt Zavody do cesty zapište cmd pro otevření comand window   
vložte následující příkazy:
python -m venv venv  
venv\Scripts\activate  
)  
pip install streamlit pandas shutil    (nebo    pip install -r requirements.txt)  
streamlit run frontend.py  
## Ověření funkčnosti  
### Vytvořit/upravoit záznamy  
V horním menu vyberte nový trénink, nastavte datum, zvolte skupinu a trať  
do tabulky níže zapište časy a dejte Uložit trénink. Jméno a příjmení se vyplňují automaticky z databáze a nejdou přepisovat.  
Uloží se pouze vyplněné řádky a zobrazí se zelená hláška úspěšně uloženo (n) záznamů  
Pokud ne, klikněte znovu na Uložit trénink  
V případě že je tabulka prázdná (nezapsali jste časy) se při kliknutní na Uložit trénink zobrazí "Nebyl vyplněn žádný čas k uložení."  
Podobně lze ukládat záznamy i jednotlivě  

V záložce Úpravy a mazání je možné záznamy editovat a odstranit opět s pomocí výběru z dropdown menu, mazání pak pomocí chackboxu na příslušném řádku.  
Úspěšný zápis dat se dá zkontrolovat v tabulce Testovací jízdy, skupiny atd. nebo přímo v csv souboru databaze_jizd.csv  
Pokud uložíte stejné výsledky vícekrát metoda deduplikace je automaticky odstraní po znovunačtení (F5)  
### Testovací jízdy
Slouží především pro kontrolu, obsahují tabulku všech jízd. Data je možno řadit kliknutím do hlavičky tabulky. (platí pro všechny tabulky)   
Checkbox umožňuje zobrazit jen nejlepší výsledek každého závodníka na každé trati  (platí pro všechny tabulky)   

### Trati
Slouží k porovnání napříč skupinami. V dorpdown menu vyberte trať 

### Skupiny
Slouží k porovnání v rámci skupiny. V dorpdown menu vyberte skupinu a trať  

### Vyhledávání
Umožňuje vyhledat konkrétní výsledky např. pro jednoho závodníka. Do všech políček je možné jak přímo psát tak vybírat z možností  

Pro účely testování je možné vkládat nové záznamy buď přes UI nebo přímo do csv souborů zavodnici.csv, databaze_jizd.csv
