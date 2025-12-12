import streamlit as st
import pandas as pd
import numpy as np

# Load the CSV files
jizdy_csv_path = 'databaze_jizd.csv'
zavodnici_csv_path = 'zavodnici.csv'

try:
    # Load data from both CSV files with explicit handling of missing values
    jizdy_data = pd.read_csv(jizdy_csv_path, dtype={"id_zavodnika": str, "trat": str, "datum": str, "cas": str})
    zavodnici_data = pd.read_csv(zavodnici_csv_path, dtype={"id_zavodnika": str, "jmeno": str, "prijmeni": str, "rok_nar": int, "skupina": str})

    # Merge data based on racer ID
    merged_data = pd.merge(jizdy_data, zavodnici_data, how='left', left_on='id_zavodnika', right_on='id_zavodnika')

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
    filtered_data = merged_data[["jmeno", "prijmeni", "rok_nar", "trat", "datum", "cas"]]
    filtered_data.insert(0, "Pořadí", range(1, len(filtered_data) + 1))

    st.title("Testovací jízdy")
    st.write("### Přehled jízd se závodníky")
    st.dataframe(filtered_data, use_container_width=True)

except FileNotFoundError as e:
    st.error(f"File not found: {e.filename}. Please ensure all required files are in the correct directory.")
except KeyError as e:
    st.error(f"Missing column: {e}. Please ensure the CSV files have the correct structure.")
except ValueError as e:
    st.error(f"Data loading error: {e}. Please check the CSV file format.")
