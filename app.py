
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
st.sidebar.header("Visualización")

df = load_data()

show_all = st.sidebar.checkbox("Mostrar todos los filmes")

if show_all:
    st.header("Todos los filmes")
    st.dataframe(df)

st.sidebar.header("Buscar por título")

search_title = st.sidebar.text_input("Título de la película")
search_button = st.sidebar.button("Buscar")

if search_button and search_title:
    filtered = df[df["title"].str.contains(search_title, case=False, na=False)]
    st.header("Resultados de búsqueda")
    st.dataframe(filtered)


st.sidebar.header("Filtrar por director")

director = st.sidebar.selectbox(
    "Selecciona un director",
    df["director"].dropna().unique()
)

filter_button = st.sidebar.button("Filtrar")

if filter_button:
    filtered_director = df[df["director"] == director]
    st.header(f"Películas de {director}")
    st.dataframe(filtered_director)

st.header("Agregar nueva película")

with st.form("new_movie_form"):
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
