# Importar paquetes
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests

# 📡 Conexión a Snowflake usando secrets (estructura con [connections.my_example_connection])
conn = st.secrets["connections"]["my_example_connection"]

connection_parameters = {
    "account": conn["account"],
    "user": conn["user"],
    "password": conn["password"],
    "role": conn["role"],
    "warehouse": conn["warehouse"],
    "database": conn["database"],
    "schema": conn["schema"]
}

# Crear la sesión de Snowflake
session = Session.builder.configs(connection_parameters).create()

# 🎨 Título y bienvenida
st.title("🍹 Customize Your Smoothie 🎈")
st.write("Choose the fruits you want in your custom Smoothie!")

# 🧾 Input de nombre para el smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# 📦 Obtener lista de frutas desde Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# 🥝 Selección de ingredientes
ingredients_list = st.multiselect(
    'Elige hasta 5 ingredientes:',
    my_dataframe,
    max_selections=5
)

# Construcción del string de ingredientes seleccionados
ingredients_string = ''
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    st.write("Tu Smoothie llevará:", ingredients_string)

# ✅ Botón para enviar la orden
if st.button('Submit Order'):
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered! ✅')

# -------------------------------
# 🍉 Mostrar info externa de Smoothiefroot API
# -------------------------------
st.markdown("---")
st.subheader("🍉 Info rápida desde Smoothiefroot API")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
