import pandas as pd
import streamlit as st
from groq import Groq

#===CONFIGURAR PAGINA ==============================
st.set_page_config(layout='wide')
st.title('Informe Ejecutivo - Api Groq')

#===CONFIGURAR API KEY==============================
api_key = st.secrets["GROQ_API_KEY"]
cliente = Groq(api_key=api_key)

#===CARGAR DATA===================================
archivo = st.file_uploader('Cargar archivo Excel (.xlsx)', type=['xlsx'])

if archivo:
    df = pd.read_excel(archivo)
    # st.dataframe(df.head(5))

    #===GENERAR RESUMEN=================================
    filas, columnas = df.shape
    nums = df.select_dtypes(include='number').columns.tolist()
    cats = df.select_dtypes(include='object').columns.tolist()

    resumen = [f'Filas: {filas}', f'Columnas: {columnas}']

    for col in nums:
        s =df[col].dropna()
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers = (s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]).count()
        resumen.append(f'{col}: media={s.mean():.2f}, mediana={s.median():.2f}, std={s.std():.2f}, outliers={outliers}')
        
    for col in cats:
        top = df[col].value_counts().head(5)
        resumen.append(f'{col}: {dict(top)}')

    texto_resumen = '\n'.join(resumen)

    with st.expander('Resumen para Enviar al Modelo'):
        st.text(texto_resumen)

    #===GENERAR INFORME=================================
    if st.button('Generar Informe'):
        with st.spinner('Generando informe...'):
            prompt = f'''
            Analiza estos datos y redacta un informe ejecutivo

            Datos:
            {texto_resumen}
            '''
            respuesta = cliente.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
            )
            informe = respuesta.choices[0].message.content
            st.markdown(informe)
