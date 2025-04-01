# Importar paquetes
import streamlit as st
import pandas as pd
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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
st.stop()

# Convert the snowpark dataframe to pandas dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

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
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        # st.text(smoothiefroot_response.json())
        st_df= st.dataframe (data=smoothiefroot_response.json(), use_container_width=True)
    # st.write("Tu Smoothie llevará:", ingredients_string)

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
# st.text(smoothiefroot_response.json())
st_df= st.dataframe (data=smoothiefroot_response.json(), use_container_width=True)
