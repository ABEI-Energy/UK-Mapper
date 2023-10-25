import pandas as pd
import simplekml as ks

def kmlMaker(df):
    
    # Create a KML object
    kml = ks.Kml()


    df_copy = df.copy()

    df_copy[['Average Max - Min Daily LMP Spread', 'Average Min Daily LMP', 'Average Max Daily LMP', 'Average LMP']] = df_copy[['Average Max - Min Daily LMP Spread', 'Average Min Daily LMP', 'Average Max Daily LMP', 'Average LMP']].astype(str) + ' $/MWh'


    unique_types = df_copy['ISO'].unique()

    for t in unique_types:
        type_folder = kml.newfolder(name=t)
        type_points = df_copy[df_copy['ISO'] == t]
        for index, row in type_points.iterrows():
            point = type_folder.newpoint(name=row['Node'], coords=[(row['Longitude'], row['Latitude'])])
            description = '<table>'
            for column_name, column_value in row.items():
                description += '<tr><td>{}</td><td>{}</td></tr>'.format(column_name, column_value)
            description += '</table>'
            point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'

            try:
                if 'pjm' in row['ISO'].lower():
                    point.style.iconstyle.color = ks.Color.white
                elif 'caiso' in row['ISO'].lower():
                    point.style.iconstyle.color = ks.Color.blue
                elif 'ercot' in row['ISO'].lower():
                    point.style.iconstyle.color = ks.Color.red
                elif 'neiso' in row['ISO'].lower():
                    point.style.iconstyle.color = ks.Color.yellow
                elif 'spp' in row['ISO'].lower():
                    point.style.iconstyle.color = ks.Color.orange
                elif 'nyiso' in row['ISO'].lower():
                    point.style.iconstyle.color = ks.Color.greenyellow   
                elif 'nyiso' in row['ISO'].lower():
                    point.style.iconstyle.color = ks.Color.purple   

                point.description = description
                point.style.iconstyle.scale = 1
                point.style.labelstyle.scale = 1  # Adjust this value as needed

            except Exception as e:
                point.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'
                point.style.iconstyle.color = ks.Color.black
                point.description = description
                point.style.iconstyle.scale = 1
                point.style.labelstyle.scale = 1 # Adjust this value as needed

    kml_file = kml.kml(format = True)

    flagKml = True

    return flagKml, kml_file

