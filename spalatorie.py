import streamlit as st
import pandas as pd
import datetime
import requests

# Linkul tău de la SheetDB (modifică aici)
SHEETDB_API_URL = "https://sheetdb.io/api/v1/lflhp2opnih56"

# Îlecarcă datele existente din Google Sheets
@st.cache_data
def load_data():
    response = requests.get(SHEETDB_API_URL)
    if response.status_code == 200:
        data = pd.DataFrame(response.json())
        if data.empty:
            return pd.DataFrame(columns=["Data", "Client", "Cantitate", "Comentarii"])
        if "Comentarii" not in data.columns:
            data["Comentarii"] = ""
        return data
    else:
        return pd.DataFrame(columns=["Data", "Client", "Cantitate", "Comentarii"])

# Salvează datele noi sau actualizate în Google Sheets
def save_data(df):
    payload = {
        "data": [{
            "Data": df.iloc[-1]["Data"],
            "Client": df.iloc[-1]["Client"],
            "Cantitate": df.iloc[-1]["Cantitate"],
            "Comentarii": df.iloc[-1]["Comentarii"]
        }]
    }
    requests.post(SHEETDB_API_URL, json=payload)

# Obține data curentă
today = datetime.date.today().strftime("%Y-%m-%d")

# Încarcă datele existente
data = load_data()

# Titlul aplicației
st.title("Înregistrare Cantitate Zilnică")

# Lista de clienți disponibili pentru selecție
clients = [
    "C. REGALA", "MELISS", "DEVESELU", "Portughezi", "BUCOVAT",
    "LICEUL MILITAR - INFIR", "LICEUL MILITAR - Stănus", "LICEUL MILITAR - Rojistean", "LICEUL MILITAR - Dincă",
    "VOILA", "Cârcea Grad.", "Helin", "Catalin", "Albesti", "Evelina", "Casablanca", "Coliseum"
]

# Selectează clientul din lista disponibilă
client = st.selectbox("Selectează Clientul", sorted(clients))

# Introdu cantitatea pentru clientul selectat
quantity = st.number_input("Introdu Cantitatea", min_value=0, step=1)

# Introdu comentarii opționale
comments = st.text_input("Comentarii (opțional)")

# Buton pentru salvare sau actualizare a cantității
if st.button("Trimite/Actualizează"):
    # Verifică dacă există deja o înregistrare pentru clientul selectat în ziua curentă
    existing = (data["Data"] == today) & (data["Client"] == client)
    if existing.any():
        # Actualizează cantitatea și comentariile existente
        data.loc[existing, "Cantitate"] = quantity
        data.loc[existing, "Comentarii"] = comments
    else:
        # Creează o nouă înregistrare
        new_row = {"Data": today, "Client": client, "Cantitate": quantity, "Comentarii": comments}
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
    # Salvează modificările în Google Sheets
    save_data(data)
    st.success("Salvat cu succes!")

# Afișează tabelul cu toate înregistrările de astăzi
st.subheader("Înregistrări pentru Azi")
st.dataframe(data[data["Data"] == today].reset_index(drop=True))
