# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Elige hasta 5 ingredientes:',
    my_dataframe
)

ingredients_string = ''

if ingredients_list:
    ingredients_string=''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)


my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
            values ('""" + ingredients_string + """')"""

time_to_insert =st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
