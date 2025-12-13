import streamlit as st
import pandas as pd
import numpy as np

# Load the CSV files
jizdy_csv_path = 'databaze_jizd.csv'
zavodnici_csv_path = 'zavodnici.csv'

try:
    # Load data from both CSV files with explicit handling of missing values
    jizdy_data = pd.read_csv(jizdy_csv_path, dtype={"id_zavodnika": str, "trat": str, "datum": str, "cas": str})
    zavodnici_data = pd.read_csv(zavodnici_csv_path, dtype={"id_zavodnika": str, "jmeno": str, "prijmeni": str, "rok_nar": str, "skupina": str})

    # Merge data based on racer ID
    merged_data = pd.merge(jizdy_data, zavodnici_data, how='left', on='id_zavodnika')

    # Replace empty or NaN times with a high placeholder value for sorting
    merged_data['cas'] = merged_data['cas'].replace('', np.nan)

    # Convert time to seconds for sorting
    def time_to_seconds(time_str):
        if pd.isna(time_str):
            return float('inf')
        try:
            parts = time_str.split(":")
            minutes = int(parts[0])
            seconds = float(parts[1].replace(",", "."))
            return minutes * 60 + seconds
        except ValueError:
            return float('inf')

    merged_data['cas_sort'] = merged_data['cas'].apply(time_to_seconds)

    # Sort data by time (ascending)
    merged_data = merged_data.sort_values(by=["cas_sort", "datum"]).drop(columns=['cas_sort'])

   
    # Filter and rename columns for display
    filtered_data = merged_data[["id_zavodnika", "trat", "datum", "cas"]]
    filtered_data.insert(0, "Pořadí", range(1, len(filtered_data) + 1))

    # Merge data to include additional racer details for display only
    display_data = pd.merge(filtered_data, zavodnici_data[["id_zavodnika", "jmeno", "prijmeni", "rok_nar", "skupina"]], how='left', on='id_zavodnika')

    # Reorder columns for display
    display_data = display_data[["Pořadí", "jmeno", "prijmeni", "rok_nar", "skupina", "trat", "datum", "cas"]]

    # Přidání přepínače pro zobrazení nejlepších pokusů
    st.write("### Možnosti zobrazení")
    zobrazit_nejlepsi = st.checkbox("Zobrazit pouze nejlepší pokusy závodníků na každé trati")

    if zobrazit_nejlepsi:
        # Ošetření chybějících nebo prázdných hodnot v 'cas'
        merged_data = merged_data.dropna(subset=['cas'])
        merged_data = merged_data[merged_data['cas'] != '']

        # Filtrace pro nejlepší pokusy každého závodníka na každé trati
        try:
            nejlepsi_pokusy = (
                merged_data.loc[
                    merged_data.groupby(['id_zavodnika', 'trat'])['cas'].idxmin()
                ]
            )

            filtered_data = nejlepsi_pokusy[["id_zavodnika", "trat", "datum", "cas"]]
            filtered_data.insert(0, "Pořadí", range(1, len(filtered_data) + 1))

            # Sloučení dat pro zobrazení detailů závodníků
            display_data = pd.merge(filtered_data, zavodnici_data[["id_zavodnika", "jmeno", "prijmeni", "rok_nar", "skupina"]], how='left', on='id_zavodnika')

            # Přeuspořádání sloupců pro zobrazení
            display_data = display_data[["Pořadí", "jmeno", "prijmeni", "rok_nar", "skupina", "trat", "datum", "cas"]]
        except KeyError as e:
            st.error(f"Chybí sloupec: {e}. Zkontrolujte strukturu CSV souborů.")
        except ValueError as e:
            st.error(f"Chyba při zpracování dat: {e}. Zkontrolujte hodnoty v CSV souborech.")

    # Debugging: Display the contents of merged_data and display_data
    st.write("Merged Data:", merged_data)
    st.write("Display Data:", display_data)

    # Zobrazení tabulky
    st.title("Testovací jízdy")
    st.write("### Přehled jízd se závodníky")
    st.dataframe(display_data, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"File not found: {e.filename}. Please ensure all required files are in the correct directory.")
except KeyError as e:
    st.error(f"Missing column: {e}. Please ensure the CSV files have the correct structure.")
except ValueError as e:
    st.error(f"Data loading error: {e}. Please check the CSV file format.")
