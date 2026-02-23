
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="Movies Dashboard", layout="wide")

@st.cache_resource
def init_firestore():
    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firestore()

@st.cache_data
def load_data():
    docs = db.collection("movies").stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)


df = load_data()

if st.sidebar.checkbox("Mostrar todos los filmes"):
    st.header("Listado completo de filmes")
    st.dataframe(df)

search_text = st.sidebar.text_input("Título del filme")

if st.sidebar.button("Buscar filmes"):
    if search_text:
        filtered_df = df[df["title"].str.contains(search_text, case=False, na=False)]
        
        st.header("Resultados de búsqueda")
        st.write(f"Total encontrados: {len(filtered_df)}")
        st.dataframe(filtered_df)
    else:
        st.warning("Por favor escribe un título para buscar")


st.sidebar.header("Seleccionar director")

director = st.sidebar.selectbox(
    "Seleccionar director",
    df["director"].dropna().unique()
)

if st.sidebar.button("Filtrar director"):
    filtered_df = df[df["director"] == director]
    st.write(f"Total encontrados: {len(filtered_df)}")
    st.dataframe(filtered_df)

st.sidebar.header("Nuevo filme")

with st.sidebar.form("new_movie_form"):
    title = st.text_input("Título")
    genre = st.text_input("Género")
    director = st.text_input("Director")
    rating = st.number_input("Rating", min_value=0.0, max_value=10.0)

    submit = st.form_submit_button("Agregar")

    if submit:
        new_movie = {
            "title": title,
            "genre": genre,
            "director": director,
            "rating": rating
        }

        db.collection("movies").add(new_movie)
        st.success("Película agregada correctamente")
        st.cache_data.clear()
        st.return()
