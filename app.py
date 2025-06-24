from salles_data import salles_data
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuration Streamlit
st.set_page_config(page_title="Inscriptions Sportives OCP", layout="wide")

# Logo + Titre
col1, col2 = st.columns([1, 10])
with col1:
    st.image("ocp_logo.png", width=100)
with col2:
    st.markdown("## <span style='color:#1a8d1a'>Formulaire d'inscription - Activités sportives OCP</span>", unsafe_allow_html=True)

st.markdown("---")

# Initialisation session
if "beneficiaries" not in st.session_state:
    st.session_state.beneficiaries = []

# Informations collaborateur
st.markdown("### 👤 Informations du Collaborateur")
nom_collab = st.text_input("Nom et prénom du collaborateur")

# Bénéficiaires
st.markdown("### 👨‍👩‍👧‍👦 Bénéficiaires")
nb_benef = st.number_input("Nombre de bénéficiaires", min_value=0, max_value=6, step=1)

beneficiaries_data = []
noms_salles_uniques = sorted(set([s["Nom"] for s in salles_data]))

for i in range(nb_benef):
    with st.expander(f"Bénéficiaire {i+1}"):
        categorie = st.selectbox(f"Catégorie {i+1}", ["Conjoint(e)", "Enfant"], key=f"cat_{i}")
        nom = st.text_input(f"Nom & Prénom", key=f"nom_{i}")
        date_naissance = st.date_input(f"Date de naissance", key=f"date_{i}")
        cnie = st.text_input(f"N° CNIE (si adulte)", key=f"cnie_{i}")
        salle_choisie = st.selectbox(f"Salle souhaitée", noms_salles_uniques, key=f"salle_{i}")

        cat_recherche = "E" if categorie == "Enfant" else "H & F"
        salle_finale = next((s for s in salles_data if s["Nom"] == salle_choisie and s["Catégorie"] == cat_recherche), None)

        if salle_finale:
            st.success(f"Code : {salle_finale['Code']} | Discipline : {salle_finale['Discipline']}")
            st.write(f"💰 Tarif plein : {salle_finale['Tarif']} DHS")
            quote_part = round(salle_finale['Tarif'] * 0.5, 2)
            st.write(f"✅ Quote-part (50%) : {quote_part} DHS")

            beneficiaries_data.append({
                "Catégorie": categorie,
                "Nom Prénom": nom,
                "Date de naissance": date_naissance,
                "CNIE": cnie,
                "Nom Salle": salle_finale["Nom"],
                "Code Salle": salle_finale["Code"],
                "Discipline": salle_finale["Discipline"],
                "Tarif total": salle_finale["Tarif"],
                "Quote-part": quote_part
            })

# Paiement
st.markdown("### 💳 Paiement")
moyen_paiement = st.selectbox("Mode de paiement", ["TPE", "Virement"])
preuve_virement = ""
if moyen_paiement == "Virement":
    preuve_virement = st.text_input("Justificatif du virement (ex: numéro de virement ou fichier PDF transmis)")

# Validation
if st.button("✅ Valider l'inscription"):
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dossier_num = int(datetime.now().timestamp())
    total_quote = sum(b["Quote-part"] for b in beneficiaries_data)

    entry = {
        "Date": date_now,
        "Dossier n°": dossier_num,
        "Collaborateur": nom_collab,
        "Total Quote-part": total_quote,
        "Nombre bénéficiaires": nb_benef,
        "Mode de paiement": moyen_paiement,
        "Justificatif virement": preuve_virement
    }

    df_main = pd.DataFrame([entry])
    df_benef = pd.DataFrame(beneficiaries_data)

    os.makedirs("data", exist_ok=True)
    df_main.to_csv("data/inscriptions.csv", mode="a", header=not os.path.exists("data/inscriptions.csv"), index=False)
    df_benef.to_csv(f"data/beneficiaires_{dossier_num}.csv", index=False)

    st.success(f"Inscriptions sauvegardées pour le dossier n° {dossier_num}")
