import streamlit as st
import pandas as pd
import numpy as np

# Load skupiny from a CSV file
skupiny_data = pd.read_csv('skupiny.csv')
# Correct column name to match the CSV file
skupiny_list = skupiny_data['jmeno_skupiny'].unique()

st.title("Skupiny")

# Dropdown menu for selecting a group
selected_skupina = st.selectbox("Vyberte skupinu:", skupiny_list)

# Load the CSV files
jizdy_csv_path = 'databaze_jizd.csv'
zavodnici_csv_path = 'zavodnici.csv'

try:
    # Load data from both CSV files with explicit handling of missing values
    jizdy_data = pd.read_csv(jizdy_csv_path, dtype={"id_zavodnika": str, "trat": str, "datum": str, "cas": str})
    zavodnici_data = pd.read_csv(zavodnici_csv_path, dtype={"id_zavodnika": str, "jmeno": str, "prijmeni": str, "rok_nar": str, "skupina": str})

    # Merge data based on racer ID
    merged_data = pd.merge(jizdy_data, zavodnici_data, how='left', on='id_zavodnika')

      
    # Filter and rename columns for display
    filtered_data = merged_data[["id_zavodnika", "trat", "datum", "cas"]]
    filtered_data.insert(0, "Pořadí", range(1, len(filtered_data) + 1))

    # Merge data to include additional racer details for display only
    display_data = pd.merge(filtered_data, zavodnici_data[["id_zavodnika", "jmeno", "prijmeni", "rok_nar", "skupina"]], how='left', on='id_zavodnika')

    # Reorder columns for display
    display_data = display_data[["Pořadí", "jmeno", "prijmeni", "rok_nar", "skupina", "trat", "datum", "cas"]]

    # Filter the data to show only the selected group
    filtered_display_data = display_data[display_data['skupina'] == selected_skupina]

    # Dropdown menu for selecting a track within the selected group
    available_tracks = filtered_display_data['trat'].unique()
    selected_track = st.selectbox("Vyberte trať:", available_tracks)

    # Filter the data to show only the selected track
    final_filtered_data = filtered_display_data[filtered_display_data['trat'] == selected_track]

    # Drop the existing 'Pořadí' column if it exists
    if 'Pořadí' in final_filtered_data.columns:
        final_filtered_data = final_filtered_data.drop(columns=['Pořadí'])

    # Recalculate the order for the filtered data
    final_filtered_data = final_filtered_data.reset_index(drop=True)
    final_filtered_data.insert(0, "Pořadí", range(1, len(final_filtered_data) + 1))

    # Display the filtered table
    st.write("### Přehled jízd pro vybranou skupinu a trať")
    st.dataframe(final_filtered_data, use_container_width=True, hide_index=True)

except FileNotFoundError as e:
    st.error(f"File not found: {e.filename}. Please ensure all required files are in the correct directory.")
except KeyError as e:
    st.error(f"Missing column: {e}. Please ensure the CSV files have the correct structure.")
except ValueError as e:
    st.error(f"Data loading error: {e}. Please check the CSV file format.")
