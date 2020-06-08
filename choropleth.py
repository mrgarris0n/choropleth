'''
How I learned to stop worrying and love the choropleth
or: data visualization with Folium
by Gergely Karacsonyi (https://www.linkedin.com/in/gergelyk/)
'''

import time
import json
import folium
import pandas as pd
import requests
from geopy.geocoders import Nominatim

# Utilizing an empty geoJSON template here
geojson = \
    {
        "type": "FeatureCollection",
        "features": []
    }


# Helper functions
def get_polygon(address):
    '''
    This function returns the bounding polygon of a given address, in geoJSON format by
    calling the Nominatim API of OpenStreetMap.

    :param address: the address query in string format
    :return: a geojson of the given address, containing name, coordinates and
             other OpenStreetMap-related props
    '''

    url = 'https://nominatim.openstreetmap.org/search?q={}&format=geojson' \
          '&polygon_geojson=1&addressdetails=1'.format(address)
    results = requests.get(url).json()
    return results


def scrape_geojson_data(address_list):
    '''
    This function requests geoJSON data of multiple addresses and merges them
    into one large geoJSON file. Drops everything but the name and the polygon of the
    addresses.

    :param addressList: list of address queries
    :return: geoJSON of multiple polygons
    '''

    for address in address_list:
        temp = {
            "type": "Feature",
            "properties": {},
        }

        geo_json = get_polygon(address)
        time.sleep(.5)
        name = list(geo_json['features'][0]['properties']['address'].values())[0]
        poly = geo_json['features'][0]['geometry']

        temp["properties"]["name"] = name
        temp["geometry"] = poly

        geojson["features"].append(temp)

    return geojson


def get_gcoor(name):
    '''
    This function requests the geographical coordinates of a given address using
    the Nominatim library of GeoPY.

    :param name: the address in string
    :return: latitude and longitude of the input address
    '''

    geolocator = Nominatim(user_agent="geojson_creator")
    location = geolocator.geocode(name)
    latitude = location.latitude
    longitude = location.longitude

    return latitude, longitude


def create_geojson_file(name_list):
    '''
    This function creates and writes a json file from scraped geoJSON data.
    Use this if you want to create a different geoJSON file than in this example.

    :param name_list: the addresses to get geoJSON data for
    '''

    geo_data = scrape_geojson_data(name_list)
    with open('geodata.json', 'w') as outfile:
        json.dump(geo_data, outfile)


def create_folium_map(geojson_file, name, data, columns, legend):
    '''
    This function draws a Choropleth Folium map from given data and geoJSON.

    :param geojson_file: geoJSON file with geometry for the map
    :param name: name of the map
    :param data: data for choropleth segments
    :param columns: data fields for choropleth segments
    :param legend: text of the legend
    :return: returns the map instance
    '''

    bp_lat, bp_lon = get_gcoor('Budapest')
    new_map = folium.Map(location=[bp_lat, bp_lon], zoom_start=8)

    # Creating the Choropleth
    folium.Choropleth(
        geo_data=geojson_file,
        name=name,
        data=data,
        columns=columns,
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend,
    ).add_to(new_map)

    folium.LayerControl().add_to(new_map)

    new_map.save('index.html')  # use this line if you want to view your map in a browser
#   new_map # use this line if you are using this code in a Jupyter notebook

    return new_map

def main():
    '''
    The main function.
    '''
    county_data = pd.read_csv('hun_county.csv', sep=';')
    geodata = 'geodata.json'

    create_folium_map(geodata, 'Population by county', county_data,
                      ['County', 'Population'], 'Population')

if __name__ == "__main__":
    main()
