import streamlit as st 
import numpy as np
import pandas as pd 
import json
import itertools
import random 
import ezdxf
import io
import shutil
from io import BytesIO
from io import StringIO

def crear_tabla_ssr(Datos, Nombre, coordenadas_dxf):
    Numeracion    = []
    Angulo        = []
    Etiqueta_stud = []
    for index, row in Datos.iterrows(): 
        Coordenadas    = row['Coordenadas']
        Stud           = row['SSR System']
        Cantidad       = row['Stud Count']	
        Primer_espacio = row['1st Stud Spacing (inches)']
        espaciamiento  = row['Typ Stud Spacing (inches)']
        try:
            Altura         = row['Approx. Rail Height (inches)']
        except:
            Altura = 6.375
        Etiqueta  = str(Cantidad) + "*" + Stud + "*" + " 1st spacing:"+ "*" + str(Primer_espacio) + "*" +" Spacing:" + "*" + str(espaciamiento) + "*" + str(Altura)
        Etiqueta_stud.append(Etiqueta)
        X1 = Coordenadas[0][0]*12
        Y1 = Coordenadas[0][1]*12
        X2 = Coordenadas[1][0]*12
        Y2 = Coordenadas[1][1]*12
        rotacion = np.arctan2(Y2-Y1,X2-X1)
        if rotacion<0: 
            rotacion+= 2*np.pi
        Angulo.append(rotacion*180/np.pi)
        col        = Nombre[np.argmin([np.linalg.norm(np.array([X1,Y1]) - np.array(coord)) for coord in coordenadas_dxf])]
        Numeracion.append(col)
    Datos['Columna']       = Numeracion
    Datos['Angulo']        = Angulo
    Datos['Etiqueta_stud'] = Etiqueta_stud
    Datos['Etiqueta_stud_angulo'] = Datos['Etiqueta_stud'] + "*" +Datos['Angulo'].astype(str)
    Tabla = Datos.groupby(['Columna','Etiqueta_stud_angulo'])['Etiqueta_stud'].count().reset_index()
    Tabla[["Cantidad","Stud","First spacing","spacing","Height","Angulo"]] = Tabla['Etiqueta_stud_angulo'].str.split("*", expand=True).drop(columns=[2,4])
    Tabla["Angulo"] = Tabla["Angulo"].astype(float)
    Columnas = Tabla["Columna"].unique()

    Nombre_columnas = []
    Narrow_Face     = []
    Long_Face       = []
    Diameter        = []
    Stud_Height     = []
    First_spacing   = []
    Stud_spacing    = []
    Number_studs_rail = []
    Detail            = []
    Tipo6             = []

    for columna in Columnas: 
        tabla_col = Tabla[Tabla['Columna'] == columna]
        Stud_spacing.append(tabla_col['spacing'].astype(float).min())
        Number_studs_rail.append(tabla_col['Cantidad'].astype(float).min())
        #Narrow_Face.append(tabla_col['Etiqueta_stud'].astype(int).min())
        try:
            Narrow_Face.append(np.sort(tabla_col['Etiqueta_stud'].astype(int).unique())[::-1][1])
        except: 
            Narrow_Face.append(tabla_col['Etiqueta_stud'].astype(int).min())
        
        try: 
            Long_Face.append(np.sort(tabla_col['Etiqueta_stud'].astype(int).unique())[::-1][0])
        except: 
            Long_Face.append(tabla_col['Etiqueta_stud'].astype(int).max())

        #Long_Face.append(tabla_col['Etiqueta_stud'].astype(int).max())
        First_spacing.append(tabla_col["First spacing"].astype(float).min())
        Diameter.append(tabla_col['Stud'].values[0])
        Stud_Height.append(float(tabla_col['Height'].values[0]))
        Etiqueta = tabla_col['Etiqueta_stud']
        Angulos  = tabla_col['Angulo']
        try:
            Cantidad_0   = Etiqueta[np.isclose(Angulos,0.0)].values[0]
        except:
            Cantidad_0 = False

        try:
            Cantidad_90  = Etiqueta[np.isclose(Angulos,90.0)].values[0]
        except:
            Cantidad_90 = False

        try:
            Cantidad_180 = Etiqueta[np.isclose(Angulos,180.0)].values[0]
        except:
            Cantidad_180 = False

        try:
            Cantidad_270 = Etiqueta[np.isclose(Angulos,270.0)].values[0]
        except:
            Cantidad_270 = False

        if (len(tabla_col) == 3) and (Cantidad_0 == Cantidad_180):
            Detail.append('1')
        elif (len(tabla_col) == 3) and (Cantidad_90 == Cantidad_270) and (Cantidad_0 == 0 or Cantidad_180==0):
            Detail.append('2')
        elif (len(tabla_col) == 3) and (Cantidad_0 == Cantidad_180) and (Cantidad_90 == 0 or Cantidad_270==0):
            Detail.append('2')
        elif (len(tabla_col) == 4) and (Cantidad_90 == Cantidad_270) and (Cantidad_0 == Cantidad_180):
            Detail.append('3')
        elif (len(tabla_col) == 2):
            Detail.append('4')
        elif (len(tabla_col) == 4) and (Cantidad_90 != Cantidad_270) and (Cantidad_0 == Cantidad_180):
            Detail.append('6')
        elif (len(tabla_col) == 4) and (Cantidad_90 == Cantidad_270) and (Cantidad_0 != Cantidad_180):
            Detail.append('6')
        elif (len(tabla_col) == 3) and (Cantidad_90 == Cantidad_270) and (Cantidad_0 != Cantidad_180):
            Detail.append('7')
        elif (len(tabla_col) == 3) and (Cantidad_90 != Cantidad_270) and (Cantidad_0 == Cantidad_180):
            Detail.append('7')
        elif (len(tabla_col) == 3) and (Cantidad_90 != Cantidad_270) and (Cantidad_0 != Cantidad_180):
            Detail.append('7')
        elif (len(tabla_col) == 5) and (Cantidad_90 != Cantidad_270) and (Cantidad_0 == Cantidad_180):
            Detail.append('6')
        elif (len(tabla_col) == 5) and (Cantidad_90 == Cantidad_270) and (Cantidad_0 != Cantidad_180):
            Detail.append('6')
        else: 
            Detail.append('')

    Tabla_studs = pd.DataFrame({"Col No":Columnas, 'Narrow Face':Narrow_Face, 'Long Face':Long_Face, 'Number studs rail':Number_studs_rail, 'Diameter':Diameter, 'Stud Height':Stud_Height, 'First stud spacing':First_spacing, 'Stud spacing':Stud_spacing,'Detail':Detail})
    return Tabla_studs





st.title('Refuerzo a cortante SSR') 

path1 = st.file_uploader("Cargar archivo SSR txt", type=["txt"], key="uploaded_file", accept_multiple_files=True)
path2 = st.file_uploader("Cargar plano dxf", type=["dxf"], key="uploaded_file2")

#st.write(st.session_state['uploaded_file'][0])

if st.button("Procesar"):
    Tablas = []
    with open("ssr.dxf", "wb") as buffer:
        shutil.copyfileobj(path2, buffer)
    
     # Se carga planos dxf
    doc             = ezdxf.readfile("ssr.dxf")
    msp             = doc.modelspace()
    coordenadas_dxf = []
    Nombre          = []

    for insert in msp.query('INSERT'): 
        atributos   = {atributo.dxf.tag : atributo.dxf.text for atributo in insert.attribs}
        coordenadas_dxf.append([insert.dxf.insert[0], insert.dxf.insert[1]])
        etiqueta = list(atributos.values())[0]
        NombreAtributo = atributos.keys()
        try:
            Nombre.append(atributos['XXX'])
        except:
            try:
                Nombre.append('P'+atributos['XX'])
            except:
                Nombre.append('P'+atributos['00'])
    for file in path1: 
        #Datos                = pd.read_csv(file, sep="\\t", engine='python')
        bytes_data  = file.getvalue()
        string_data = StringIO(bytes_data.decode("utf-16"))
        #Datos           = pd.read_csv(st.session_state['uploaded_file'], sep="\\t", engine='python')
        Datos            = pd.read_csv(string_data, sep="\\t", engine='python')
        #Datos                = pd.read_csv(file,sep='\\t'.encode('utf-16-le'), encoding='utf-16-le', engine='python')
        #Datos                 = pd.read_csv(BytesIO(file.read().decode('UTF-16').encode('UTF-s8')), sep='\t', header=0)
        
        Datos['Coordenadas'] = Datos['Location (feet)'].apply(lambda X: [(float(val2.split(',')[0].replace('(','').replace(')','')),float(val2.split(',')[1].replace('(','').replace(')','')))  for val2 in X.split(')(')])
        tabla                = crear_tabla_ssr(Datos, Nombre, coordenadas_dxf)
        tabla['Nivel']       = file.name.split(".")[0]
        Tablas.append(tabla)
    #Datos                = pd.read_csv(st.session_state['uploaded_file'], sep="\\t", engine='python')
    #Datos['Coordenadas'] = Datos['Location (feet)'].apply(lambda X: [(float(val2.split(',')[0].replace('(','').replace(')','')),float(val2.split(',')[1].replace('(','').replace(')','')))  for val2 in X.split(')(')])
    
    #Tabla_studs = crear_tabla_ssr(Datos, Nombre, coordenadas_dxf)
    #st.session_state['uploaded_file'].name.split('.')[0]
    Tabla_studs         = pd.concat(Tablas, axis=0)
    Tabla_studs['Tipo'] = Tabla_studs['Narrow Face'].astype(str) +'-'+ Tabla_studs['Long Face'].astype(str) +'-'+ Tabla_studs['Number studs rail'].astype(str) +'-'+ Tabla_studs['Diameter'].astype(str) +'-'+ Tabla_studs['Diameter'].astype(str) +'-'+ Tabla_studs['Stud Height'].astype(str) +'-'+ Tabla_studs['First stud spacing'].astype(str) +'-'+ Tabla_studs['Stud spacing'].astype(str) +'-'+ Tabla_studs['Detail'].astype(str)
    st.write(Tabla_studs)
    st.download_button(
        label     = "Descargar Tabla",
        data      =  Tabla_studs.to_csv(index=False),
        file_name = "Refuerzo_SSR.csv",
        mime      = "text/csv",)

    
