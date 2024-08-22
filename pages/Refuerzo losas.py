import streamlit as st 
import numpy as np
import pandas as pd 
import json
import itertools
import random 
import ezdxf
import io

st.title('Refuerzo longitudinal losas') 

path1 = st.file_uploader("Cargar informacion refuerzo horizontal", type=["txt"], key="uploaded_file")
path2 = st.file_uploader("Cargar informacion refuerzo Vertical", type=["txt"], key="uploaded_file2")

doc = ezdxf.new()
msp = doc.modelspace()


if st.button("Procesar"):
    Datos           = pd.read_csv(st.session_state['uploaded_file'], sep="\\t", engine='python')
    Datos['Inicio'] = Datos['Location (feet)'].apply(lambda X: [(float(val2.split(',')[0].replace('(','').replace(')',''))*12,float(val2.split(',')[1].replace('(','').replace(')',''))*12)  for val2 in X.split(')(')])

    Datos2          = pd.read_csv(st.session_state['uploaded_file2'], sep="\\t", engine='python')
    Datos2['Inicio'] = Datos2['Location (feet)'].apply(lambda X: [(float(val2.split(',')[0].replace('(','').replace(')',''))*12,float(val2.split(',')[1].replace('(','').replace(')',''))*12)  for val2 in X.split(')(')])

    ## DETALLADO REFUERZO VERTICAL 
    Datos_top = Datos2[Datos2['Face']=='Top']
    for index, row in Datos_top.iterrows(): 
        Inicio   = row['Inicio']
        X        = np.mean([val[0] for val in Inicio])
        Y        = np.mean([val[1] for val in Inicio])
        L        = row['Length (feet)']
        Barra    = row['Bar Size']
        Cantidad = row['Bars']
        Espacio  = row['Spacing (inches)']
        msp.add_line((X, Y-L*12/2), (X, Y+L*12/2), dxfattribs={"color": 10})
        Etiqueta   = str(Cantidad)  + Barra + "L" + str(L)+ "@" + str(Espacio) + "T"
        msp.add_text(Etiqueta, height=5,  dxfattribs={'rotation':90, "color": 10}).set_placement((X, Y))

    traslacion = 10000
    Datos_bottom = Datos2[Datos2['Face']=='Bottom']
    for index, row in Datos_bottom.iterrows():
        Inicio   = row['Inicio']
        X        = np.mean([val[0] for val in Inicio]) + traslacion
        Y        = np.mean([val[1] for val in Inicio])
        L        = row['Length (feet)']
        Barra    = row['Bar Size']
        Cantidad = row['Bars']
        Espacio  = row['Spacing (inches)']
        msp.add_line((X, Y-L*12/2), (X, Y+L*12/2), dxfattribs={"color": 10})
        Etiqueta   = str(Cantidad)  + Barra + "L" + str(L)+ "@" + str(Espacio) + "B"
        msp.add_text(Etiqueta, height=5,  dxfattribs={'rotation':90,"color": 10}).set_placement((X, Y))


    circle  = msp.add_circle((0, 0), radius=50)
    circle2 = msp.add_circle((traslacion, 0), radius=50)

    ## DETALLADO REFUERZO HORIZONTAL 
    Datos_top = Datos[Datos['Face']=='Top']
    for index, row in Datos_top.iterrows(): 
        Inicio   = row['Inicio']
        X        = np.mean([val[0] for val in Inicio])
        Y        = np.mean([val[1] for val in Inicio])
        L        = row['Length (feet)']
        Barra    = row['Bar Size']
        Cantidad = row['Bars']
        Espacio  = row['Spacing (inches)']
        msp.add_line((X-L*12/2, Y), (X+L*12/2, Y), dxfattribs={"color": 50})
        Etiqueta   = str(Cantidad)  + Barra + "L" + str(L)+ "@" + str(Espacio) + "T"
        msp.add_text(Etiqueta, height=5,  dxfattribs={'rotation':0, "color": 50}).set_placement((X, Y))

    traslacion = 10000
    Datos_bottom = Datos[Datos['Face']=='Bottom']
    for index, row in Datos_bottom.iterrows():
        Inicio   = row['Inicio']
        X        = np.mean([val[0] for val in Inicio]) + traslacion
        Y        = np.mean([val[1] for val in Inicio])
        L        = row['Length (feet)']
        Barra    = row['Bar Size']
        Cantidad = row['Bars']
        Espacio  = row['Spacing (inches)']
        msp.add_line((X-L*12/2, Y), (X+L*12/2, Y), dxfattribs={"color": 50})
        Etiqueta   = str(Cantidad)  + Barra + "L" + str(L)+ "@" + str(Espacio) + "B"
        msp.add_text(Etiqueta, height=5,  dxfattribs={'rotation':0,"color": 50}).set_placement((X, Y))
    
    stream_obj = io.StringIO()
    doc.write(stream_obj)
    dxf_text_string = stream_obj.getvalue()
    stream_obj.close()

    st.download_button(
        label     = "Descargar DXF",
        data      =  dxf_text_string,
        file_name = "Refuerzo_losa.dxf",
        mime      = "text/csv",)
