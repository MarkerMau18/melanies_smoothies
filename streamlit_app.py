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

# Convertir Snowpark DataFrame a Pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df, use_container_width=True)

# 🥝 Selección de ingredientes
ingredients_list = st.multiselect(
    'Elige hasta 5 ingredientes:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Construcción del string de ingredientes seleccionados
ingredients_string = ''
if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Obtener el valor de búsqueda para API
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        # Llamada a la API externa y visualización de info nutricional
        st.subheader(f"{fruit_chosen} Nutrition Information")
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if response.status_code == 200:
            try:
                fruit_info = response.json()
                if isinstance(fruit_info, dict):
                    df_info = pd.DataFrame([fruit_info])
                    st.dataframe(df_info, use_container_width=True)
                else:
                    st.write(fruit_info)
            except Exception as e:
                st.error(f"Error al procesar respuesta de la API: {e}")
        else:
            st.error(f"No se pudo obtener info para {fruit_chosen} 😢")

# ✅ Botón para enviar la orden (sin .strip())
if st.button('Submit Order'):
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered! ✅')

# -------------------------------
# 🍉 Mostrar info externa extra (por default: watermelon)
# -------------------------------
st.markdown("---")
st.subheader("🍉 Ejemplo de API: Watermelon Info")

example_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
if example_response.status_code == 200:
    example_data = example_response.json()
    if isinstance(example_data, dict):
        st.dataframe(pd.DataFrame([example_data]), use_container_width=True)
    else:
        st.write(example_data)
else:
    st.error("No se pudo obtener la info de watermelon 🍉")
