# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests  # ← aquí ya va el import bien ubicado

# Write directly to the app
st.title("🍹 Customize Your Smoothie 🎈")
st.write("""
    Choose the fruits you want in your custom Smoothie!
""")

# Input del nombre
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Conexión con Snowflake y tabla de frutas
session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

# Selector de ingredientes
ingredients_list = st.multiselect(
    'Elige hasta 5 ingredientes:',
    my_dataframe,
    max_selections=5
)

# Construcción del string de ingredientes
ingredients_string = ''
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    st.write("Tu Smoothie llevará:", ingredients_string)

# Inserción del pedido
if st.button('Submit Order'):
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered! ✅')

# -------------------------------
# Llamada sencilla a la API externa
# -------------------------------
st.markdown("---")
st.subheader("🍉 Info rápida desde Smoothiefroot API")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
