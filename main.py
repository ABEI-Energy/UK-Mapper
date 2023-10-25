import datetime as dt
import io
import locale as lc
import pandas as pd
import streamlit as st
import streamlit_toggle as tog
from docx.shared import Cm
import mapper as mp
import coordinates as cd
import functions as fn
import kml
from zipfile import ZipFile

if 'disable_opt' not in st.session_state:
    st.session_state.disable_opt = False

#Set the language for datetime
lc.setlocale(lc.LC_ALL,'es_ES.UTF-8')
month = dt.datetime.now().strftime("%B %Y")
def normalize(string):
    return str(round(float(string.replace(",", ".")),2))

def normalize2(string):
    return str(string.replace(",", "."))

st.set_page_config(layout="wide")

rootShp = "USA Shapefile/USA_SHAPEFILE.shp"

"""
# ENVERUS kml maker
"""


# Time to read the documents

st.divider()

coly, colx = st.columns(2)
with colx:
    uploadedFile = st.file_uploader("Drag here the csv from Enverus. Make sure the file is not filtered.", accept_multiple_files = False)

with coly:
    st.caption("Csv example of unaltered file")
    with open("SAMPLEFILES/ENV_CSV_FILE_EXAMPLE.csv", "rb") as fp:
        btn = st.download_button(
            label="Download csv file type",
            data=fp,
            file_name="ENV_CSV_FILE_EXAMPLE.csv",
            mime='text/csv',
        )

colz, cola = st.columns(2)

if uploadedFile:

    # st.cache_data
    if uploadedFile.name.endswith('csv'):

        df_stateless, df_statefull, df_stateless_countiless, df_full = fn.df_adequacy(uploadedFile)
        #@todo hay algunos que tienen county pero no state, hay que pensar cómo llenarlos.
        df, flag_adequacy = mp.locator_json(df_stateless, df_statefull, df_stateless_countiless, df_full, rootShp)

        df.reset_index(inplace = True, drop = True)

        if flag_adequacy:

            col1, col2, col3, col4 = st.columns(4)
            state = period = ISO = priceType = str()

            with col1:
                select_all_state = st.checkbox('Select all states')
                state_key = 'state_' + str(select_all_state)
                if not select_all_state:
                    state = st.multiselect('Select state:', sorted(df['State'].unique()), key = state_key)
                else:
                    state = df['State'].unique().tolist()

            with col2:
                if state:
                    select_all_ISO = st.checkbox('Select all ISOs')
                    iso_key = 'iso_' + str(select_all_ISO)
                    if not select_all_ISO:
                        ISO = st.multiselect('Select ISO:', df.loc[df['State'].isin(state), 'ISO'].unique(), key = iso_key)
                    else:
                        ISO = df.loc[df['State'].isin(state), 'ISO'].unique().tolist()

            with col3:
                if state:
                    select_all_period = st.checkbox('Select all periods')
                    period_key = 'period_' + str(select_all_period)
                    if not select_all_period:
                        period = st.multiselect('Select period:', df.loc[df['State'].isin(state), 'Period From'].unique(), key = period_key)
                    else:
                        period = df.loc[df['State'].isin(state), 'Period From'].unique().tolist()

            with col4:
                if state:
                    select_all_priceType = st.checkbox('Select all price types')
                    price_key = 'price_' + str(select_all_priceType)
                    if not select_all_priceType:
                        priceType = st.multiselect('Select price type:', df.loc[df['State'].isin(state), 'Price type'].unique(), key = price_key)
                    else:
                        priceType = df.loc[df['State'].isin(state), 'Price type'].unique().tolist()   

        if (len(period)!=0) and (len(ISO)!=0) and (len(state)!=0) and (len(priceType)!=0):

            filtered_df, df_indexed = fn.filter_df(df,period,ISO, state, priceType)

            html_to_show_spread = mp.html_display_spread(filtered_df)
            html_to_show_indexed = mp.html_display_indexed(df_indexed)
            colb, colc = st.columns(2)


            st.caption('LMP Hot Spot heatmap')

            html_to_show_indexed = mp.html_display_indexed(df_indexed)
            st.write(html_to_show_indexed)

            obj_html_io_indexed = io.StringIO()
            html_to_show_indexed.write_html(obj_html_io_indexed)
            obj_html_io_indexed.seek(0)


            st.caption('Average Max - Min Daily LMP Spread heatmap')

            html_to_show_spread = mp.html_display_spread(filtered_df)
            st.write(html_to_show_spread)

            obj_html_io_spread = io.StringIO()
            html_to_show_spread.write_html(obj_html_io_spread)
            obj_html_io_spread.seek(0)

            flag_createFile = st.button("Generate zip file")
            flagZip = False

            if flag_createFile:

                with st.status("Generating file", expanded=True) as status:
                    st.write("Preparing kml")

                    nameZip = 'Enverus ' + str(state) + " " + str(ISO) + " " + str(period) + " " + str(priceType) + " " + ".zip"
                    zip_data = io.BytesIO()

                    # We create the kml file
                    flagKml, kml_string = kml.kmlMaker(filtered_df)
                    obj_kml_io = io.StringIO(kml_string)
                    obj_kml_io.seek(0)      


                    st.write("Preparing xlsx")

                    # We create the xlsx
                    excel_io = io.BytesIO()
                    writer = pd.ExcelWriter(excel_io, engine = 'xlsxwriter')
                    excel_io.seek(0)
                    filtered_df.to_excel(writer, sheet_name = 'Nodes', index = False)
                    writer.close()
                    excel_io.seek(0)


                    st.write("Preparing zip")

                    # Create a ZipFile Object
                    with ZipFile(zip_data, 'w') as zipf:
                       # Adding files that need to be zipped
                        zipf.writestr("Heatmap spread value.html",obj_html_io_spread.getvalue())
                        zipf.writestr("Heatmap indexed.html",obj_html_io_indexed.getvalue())
                        zipf.writestr("Node spread.kml",obj_kml_io.getvalue())
                        zipf.writestr("Node spread.xlsx",excel_io.getvalue())

                        flagZip = True


                    status.update(label="File completed")

                    





            
            if flagZip and flagKml:
                st.success('Download the report file')
                btn = st.download_button(
                    label="Download",
                    data=zip_data.getvalue(),
                    file_name=nameZip,
                    mime="application/zip"
                )                


        pass
