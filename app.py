from salles_data import salles_data
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inscriptions Sportives OCP", layout="wide")
st.title("Formulaire d'inscription - Activités sportives OCP")

# Session state for beneficiaries
if "beneficiaries" not in st.session_state:
    st.session_state.beneficiaries = []

st.header("Informations du Collaborateur")
nom_collab = st.text_input("Nom et prénom du collaborateur")
selected_salle = st.selectbox(
    "Salle choisie",
    salles_data,
    format_func=lambda x: f"{x['Nom']} ({x['Code']})"
)

st.write(f"Discipline : {selected_salle['Discipline']}")
st.write(f"Catégorie : {selected_salle['Catégorie']}")
st.write(f"Tarif plein : {selected_salle['Tarif']} DHS")

# Gestion des bénéficiaires
st.subheader("Bénéficiaires")
nb_benef = st.number_input("Nombre de bénéficiaires", min_value=0, max_value=6, step=1)

beneficiaries_data = []
for i in range(nb_benef):
    with st.expander(f"Bénéficiaire {i+1}"):
        categorie = st.selectbox(f"Catégorie {i+1}", ["Conjoint(e)", "Enfant"], key=f"cat_{i}")
        nom = st.text_input(f"Nom & Prénom", key=f"nom_{i}")
        date_naissance = st.date_input(f"Date de naissance", key=f"date_{i}")
        cnie = st.text_input(f"N° CNIE (si adulte)", key=f"cnie_{i}")
        tarif_total = st.number_input(f"Tarif total (DHS TTC)", min_value=0.0, step=1.0, key=f"tarif_{i}")
        quote_part = round(tarif_total * 0.5, 2)
        st.write(f"Quote-part à payer (50%) : {quote_part} DHS")
        beneficiaries_data.append({
            "Catégorie": categorie,
            "Nom Prénom": nom,
            "Date de naissance": date_naissance,
            "CNIE": cnie,
            "Tarif total": tarif_total,
            "Quote-part": quote_part
        })

# Mode de paiement
st.subheader("Paiement")
moyen_paiement = st.selectbox("Mode de paiement", ["TPE", "Virement"])
preuve_virement = ""
if moyen_paiement == "Virement":
    preuve_virement = st.text_input("Justificatif du virement (ex: numéro de virement ou fichier PDF transmis)")
    # Optionnel : st.file_uploader("Joindre la preuve (PDF)", type=["pdf"])

if st.button("Valider l'inscription"):
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dossier_num = int(datetime.now().timestamp())
    total_quote = sum(b["Quote-part"] for b in beneficiaries_data)

    entry = {
        "Date": date_now,
        "Dossier n°": dossier_num,
        "Collaborateur": nom_collab,
        "Salle": selected_salle["Nom"],
        "Code Salle": selected_salle["Code"],
        "Total Quote-part": total_quote,
        "Nombre bénéficiaires": nb_benef,
        "Mode de paiement": moyen_paiement,
        "Justificatif virement": preuve_virement
    }

    df_main = pd.DataFrame([entry])
    df_benef = pd.DataFrame(beneficiaries_data)

    df_main.to_csv("data/inscriptions.csv", mode="a", header=not os.path.exists("data/inscriptions.csv"), index=False)
    df_benef.to_csv(f"data/beneficiaires_{dossier_num}.csv", index=False)

    st.success(f"Inscriptions sauvegardées pour le dossier n° {dossier_num}")
