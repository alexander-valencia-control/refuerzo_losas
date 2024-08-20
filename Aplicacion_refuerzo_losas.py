import streamlit as st 
import numpy as np
import pandas as pd 
import json
import itertools
import random 
import ezdxf
import io

st.set_page_config(page_title="Aplicacion refuerzo losas")

st.title('Refuerzo losas') 
#st.sidebar.success("Seleccionar pagina")

st.header("Datos de entrada")

st.subheader("Datos de entrada refuerzo losas")
st.markdown("Los datos de entrada para generar el plano de refuerzo longitudinal de las losas son dos tablas que se pueden ver en las imagenes siguientes. El usuario debe determinar cuales son verticales y cuales las horizontales y guardarlo como archivo de texto (codificacion UTF-8) con el respectivo nombre")

st.image("Screenshot 2024-08-20 103736.jpg", caption="Tablas para refuerzo longitudinal")
st.image("Screenshot 2024-08-20 103736.jpg", caption="Tablas para refuerzo longitudinal")


st.subheader("Datos de entrada ssr")
st.markdown("Los datos de entrada para generar la tabla de refuerzo a cortante se pueden ver en las imagenes. Se pueden procesar multiples archivos de texto al tiempo (texto en formato UTF-8). Se requiere un plano en formato dxf con la numeracion de las columnas. El numero de la columna debe estar centrado en la columna respectiva.")

st.image("Screenshot 2024-08-20 104657.jpg", caption="Tablas para refuerzo ssr")
st.image("Screenshot 2024-08-20 104807.jpg", caption="Plano dxf")
