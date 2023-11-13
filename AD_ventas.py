from datetime import datetime
import glob
from pathlib import Path

from IPython.display import HTML, display
import pandas as pd
import altair as alt
import streamlit as st
import numpy as np
import locale

st.title('''Analisis de datos de las ventas en moneda nacional de empresa de tecnologias.''')
st.write('''
            Estos datos son tomados de la facturacón entre enero del 2020
            hasta el mes de Octubre del año 2023.
            Se consideran significativos
            ''')
st.sidebar.title('Indicadores importantes')

 #Importando y realizado limpieza y asignación de subdataframes a partir de archvivos .csv
route = "./Data"
files = [ Path(i) for i in glob.glob(f'{route}/*.csv') ]

dfs = []
for csv in files:
    df = pd.read_csv(csv, delimiter= ',')
    dfs.append(df)

data = pd.concat(dfs, ignore_index= True)

data = data[['Fecha','Razón Social', 'Total', 'Cancelado', 'Nombre de la Moneda', 'Nombre del agente']]

data.Fecha = pd.to_datetime(data.Fecha,format = 'mixed')

data_mxn = data[(data['Nombre de la Moneda'] == "Peso Mexicano") & (data['Cancelado'] == 0)]
data_mxn.Total = data.Total.astype(float)

grupo_Clientes_Venta = data_mxn.groupby('Razón Social')['Total'].sum()
clientes_venta_sorting = grupo_Clientes_Venta.sort_values(ascending= False).reset_index().head(30)



# Grafica 1
ventas_anuales = data_mxn.groupby(data_mxn.Fecha.dt.year)['Total'].sum().reset_index()
grafica_1 = alt.Chart(ventas_anuales).mark_line(point = alt.OverlayMarkDef(filled = False, fill = "white", color = "#d62728"), color = "#d62728").encode(
    x = alt.X("Fecha:N").scale(zero = False),
    y = alt.Y("Total:Q").scale(zero = False),
).properties(
    width = 600,
    height = 400
)

st.title("Crecimiento a la fecha.")
st.write('''\n\n Se muestra que se ha tenido un crecimiento exponensial
            En cuanto al consumo de los servicios ofrecidos por la empresa.
            \n\n 
           
        ''')

grafica_1
pElemento = ventas_anuales.Total.iloc[0]
uElemento = ventas_anuales.Total.iloc[-1]
crecimiento_total = round(((uElemento - pElemento) / pElemento ) * 100,2)
st.sidebar.write('<span style=" color: black; font-size: 25px; "> ' 
                 f'''¿Cuanto ha crecido la empresa en 4 años? ''' '</span>', unsafe_allow_html =True)
st.sidebar.write('<span style=" color: green; font-size: 25px; "> ' 
                 f''':chart_with_upwards_trend:   : {crecimiento_total} %''' '</span>', unsafe_allow_html =True)

años_disponibles =  data_mxn['Fecha'].dt.year.unique()
año_inicio = st.sidebar.selectbox("Selecciona el año de inicio: ", np.sort(años_disponibles))
año_fin = st.sidebar.selectbox("Selecciona el año de fin: ", np.sort(años_disponibles))

meses = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre'
}
color_palette = alt.Scale(
    domain=[2020, 2021, 2022, 2023],  # Valores únicos en la columna 'Año'
    range=['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']  # Colores de la paleta
)

contraste_mensual = data_mxn.groupby(data_mxn.Fecha.dt.to_period('M'))['Total'].sum().reset_index()
contraste_mensual = contraste_mensual.iloc[:-2]
contraste_mensual['Fecha'] = contraste_mensual['Fecha'].apply(lambda x: x.to_timestamp()).sort_values(ascending= False)
contraste_mensual['Fecha'] = pd.to_datetime(contraste_mensual['Fecha'], format='%Y-%m')

contraste_mensual['Año'] = contraste_mensual['Fecha'].dt.year
contraste_mensual['Mes'] = contraste_mensual['Fecha'].dt.month

contraste_mensual['Mes'] = contraste_mensual['Mes'].map(meses)


highlight = alt.selection_point(
    on="mouseover", fields=["Año"], nearest=True
)


base = alt.Chart(contraste_mensual).encode(
    x= alt.X('Mes:O', title='Mes',  sort=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo',
                                           'Junio', 'Julio', 'Agosto', 'Septiembre', 
                                           'Octubre', 'Noviembre', 'Diciembre']),
    y= alt.Y('Total:Q', title='Total'),
    color= alt.Color('Año:N', scale = color_palette),
).properties(
    width=600
).interactive()

points = base.mark_circle().encode(
    opacity=alt.value(0)
).add_params(
    highlight
).properties(
    width=600
)

lines = base.mark_line( point=alt.OverlayMarkDef(filled=False, fill="white")).encode(
    size=alt.condition(~highlight, alt.value(1), alt.value(3))
)
points + lines




clientesprincipales_y  = data_mxn[['Fecha', 'Razón Social', 'Total']].reset_index(drop = True)

clientesprincipales_y['Fecha'] = pd.to_datetime(clientesprincipales_y['Fecha'])
clientesprincipales_y['Fecha'] = clientesprincipales_y['Fecha'].dt.year

clientesprincipales_y = clientesprincipales_y.groupby(['Fecha', 'Razón Social'])['Total'].sum().reset_index()
clientesprincipales_y = clientesprincipales_y.sort_values(by='Total', ascending=False)





datos_años_seleccionados = clientesprincipales_y[(clientesprincipales_y['Fecha'] >= int(año_inicio)) & (clientesprincipales_y['Fecha'] <= int(año_fin))].sort_values(by ='Total', ascending= False)

total_facturacion = clientesprincipales_y[(clientesprincipales_y['Fecha'] >= int(año_inicio)) & (clientesprincipales_y['Fecha'] <= int(año_fin))]
total_facturacion = total_facturacion['Total'].sum()
total_facturacion_del_periodo = clientesprincipales_y.Total.sum()


datos_años_seleccionados['PorcentajeTotal_Facturacion'] = round((datos_años_seleccionados['Total']  / total_facturacion) *100,2)
datos_años_seleccionados_table = datos_años_seleccionados.head()
datos_años_seleccionados_table.columns = ['Año', 'Cliente', 'Total', 'Porcentaje Representativo en la Facturación Total']
datos_años_seleccionados_table = datos_años_seleccionados_table.to_html(index=False)

tabla_html = f"""
<table border="1">
    <tr>
        <th style="text-align: center; color: black; font-size: 15px;">Total Facturación Anual</th>
        <th style="text-align: center; color: black; font-size: 15px;">Total Facturación del Periodo</th>
        <th style="text-align: center; color: black; font-size: 15px;">Porcentaje total de las ventas realizadas</th>
    </tr>
    <tr>
        <td style="text-align: center; color: green; font-size: 20px;">${round(total_facturacion, 2)}</td>
        <td style="text-align: center; color: green; font-size: 20px;">${round(total_facturacion_del_periodo, 2)}</td>
        <td style="text-align: center; color: blue; font-size: 20px;">{round((total_facturacion / total_facturacion_del_periodo)* 100,2)  } %</td>
    </tr>
</table>
"""


st.sidebar.write(tabla_html, unsafe_allow_html=True)
st.sidebar.markdown("")





st.sidebar.write( datos_años_seleccionados_table, unsafe_allow_html =True)
grupo_clientes_principales = datos_años_seleccionados.groupby('Razón Social')['Total'].sum().reset_index()
grupo_clientes_principales = grupo_clientes_principales.sort_values(by='Total', ascending=False)
st.title("¿Quienes han sido nuestro cliente con más consumo durante el periodo seleccionado?")
grafica_2 = alt.Chart(grupo_clientes_principales.head(20)).encode(
    y = alt.X('Razón Social:O', title = "Clientes"),
    x = alt.Y('Total', title = "Ventas Totales")
).properties(
    width = 700
)

porcentaje =  clientes_venta_sorting['Total'].sum() / data_mxn['Total'].sum() * 100
cliente = clientes_venta_sorting[clientes_venta_sorting['Total'] == max(clientes_venta_sorting['Total'])]

st.altair_chart(grafica_2.mark_bar() + grafica_2.mark_text(align =  'left', dx = 0))

