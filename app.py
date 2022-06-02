import altair as alt
import datetime
import folium
import geopandas as gpd
import geopy
import json
import base64
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import plotly_express as px
import plotly.io as pio
import plotly.offline as pyo
import requests
import seaborn as sns
import streamlit as st
import psycopg2

from folium.features import DivIcon
from googletrans import Translator
from PIL import Image
from shapely.geometry import Point, LineString
from spacy import displacy
from spacy_streamlit import visualize_ner
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

from branca.element import Figure
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

ox.config(use_cache=True, log_console=True)
pyo.init_notebook_mode(connected=True)

st.set_page_config(
    page_title="Nakagawa - Safest Path during Earthquakes",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.set_option('deprecation.showPyplotGlobalUse', False)

st.markdown(
    """
    <style>
        .css-hby737, .css-17eq0hr, .css-qbe2hs {
            background-color:    #154360    !important;
            color: black !important;
        }
        div[role="radiogroup"] {
            color:black !important;
            margin-left:8%;
        }
        div[data-baseweb="select"] > div {
            
            color: black;
        }
        div[data-baseweb="base-input"] > div {
            background-color: #aab7b8 !important;
            color: black;
        }
        
        .st-cb, .st-bq, .st-aj, .st-c0{
            color: black !important;
        }
        .st-bs, .st-ez, .st-eq, .st-ep, .st-bd, .st-e2, .st-ea, .st-g9, .st-g8, .st-dh, .st-c0 {
            color: black !important;
        }
        .st-fg, .st-fi {
            background-color: #c6703b !important;
            color: black !important;
        }
       
        
        .st-g0 {
            border-bottom-color: #c6703b !important;
        }
        .st-fz {
            border-top-color: #c6703b !important;
        }
        .st-fy {
            border-right-color: #c6703b !important;
        }
        .st-fx {
            border-left-color: #c6703b !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown('<h1 style="margin-left:8%; color:#FA8072">Nakagawa - Safest Path during Earthquakes </h1>', unsafe_allow_html=True)

add_selectbox = st.sidebar.radio(
    "",
    ("Home", "About", "Features", "Safest Path", "Visualizations", "Conclusion", "Team")
)

if add_selectbox == 'Home':
    
    LOGO_IMAGE = "omdena_japan_logo.jpg"
    
    st.markdown(
          """
          <style>
          .container {
          display: flex;
        }
        .logo-text {
             font-weight:700 !important;
             font-size:50px !important;
             color: #f9a01b !important;
             padding-top: 75px !important;
        }
        .logo-img {
             float:right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
          f"""
          <div class="container">
               <img class="logo-img" src="data:image/jpg;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
          </div>
          """,
          unsafe_allow_html=True
    )
    
    st.subheader('PROBLEM STATEMENT')
    
    st.markdown('Natural Disasters are problems in Japan, with risk of earthquakes, floods and tsunamis. Japan has well-developed \
        disaster response systems, but densely populated cities and narrow roads make managing the response difficult. By giving \
            individuals information about the safest ways from their homes and places of work, it will increase their awareness of \
                the surrounding area and improve their preparedness.', unsafe_allow_html=True)


elif add_selectbox == 'About':
    
    st.subheader('ABOUT THE PROJECT')

    st.markdown('<h4>Project Goals</h4>', unsafe_allow_html=True)
    st.markdown('• collect satellite images and identify road characteristics', unsafe_allow_html=True) 
    st.markdown('• build a model for scoring the roads in terms of their suitability for use in emergency', unsafe_allow_html=True) 
    st.markdown('• build a pathfinding model from A to B, combining it with road characteristics', unsafe_allow_html=True) 
    st.markdown('• suggest safest path from A to B', unsafe_allow_html=True) 
    st.markdown('• publish interactive dashboards to display road characteristics and safest paths', unsafe_allow_html=True) 
    st.markdown('• arrange demonstration and publicise to local audiences', unsafe_allow_html=True) 
    
    st.markdown('<h4>Location Choosen</h4>', unsafe_allow_html=True)
    st.markdown('We had choosen "Nakagawa-Ku as our region of interest, which comes under Aichi prefecture of Nagoya City. It comes under Chubu region and \
        is the 4th densely populated city in Japan with high risk prone to disasters.',
                unsafe_allow_html=True)
    
    st.markdown('<h4>Developments Made</h4>', unsafe_allow_html=True)
    st.markdown('• We had designed a model collecting data about the local roads from satellite images, classify them and indicate the safest \
        route to be taken from point A to point B and an interactive dashboard to display the safest route in a map.',
                unsafe_allow_html=True)
    st.markdown('• By making individuals aware, it will improve their preparedness and it can be used within families to prepare disaster \
        response plans, depending on their circumstances. To be used by individuals, families and groups, and foreign residents who may \
            not understand local information. Further development will be covering more geographical areas and publicising on a local level.'
                , unsafe_allow_html=True)
  

elif add_selectbox == 'Features':

    st.subheader('PROJECT ENDORSEMENTS')

    st.markdown('• Safest route path to take at occurences of japan disasters', unsafe_allow_html=True)
    st.markdown('• Locates shelters in Nakagawa Ward - Earthquakes, Tsunamis and Floods', unsafe_allow_html=True)
    st.markdown('• Visualizations to Check and Differentiate Parameters across the Nakagawa Ward', unsafe_allow_html=True)
    	
	
elif add_selectbox == 'Safest Path':
	
    st.subheader('FIND THE SAFEST PATH')
	
    current_location = st.text_input('Current Location:') 

    if st.button('Search'):
        api_token = "pk.eyJ1IjoicHJhdGhpbWFrYWRhcmkiLCJhIjoiY2t6MmxlaDVvMXAxaDJ2cWtrM3BzMGZuMCJ9.m5BXW9QUs914PCaWkepfHA"
        
        def create_graph(loc, dist, transport_mode, loc_type="address"):
            """Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’"""
            if loc_type == "address":
                G = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)    
            elif loc_type == "points":
                G = ox.graph_from_point(loc, dist=dist, network_type=transport_mode )

            return G
        
        G = create_graph("Nakagawa, Nagoya, Japan", 2500, "drive")
        ox.plot_graph(G)
        
        G = ox.add_edge_speeds(G) #Impute
        G = ox.add_edge_travel_times(G) #Travel time

        # start = (57.715495, 12.004210)
        # end = (57.707166, 11.978388)

        start = (35.1394307, 136.8565519)
        end = (35.1301611, 136.8697751)

        start_node = ox.get_nearest_node(G, start)
        end_node = ox.get_nearest_node(G, end)# Calculate the shortest path
        route = nx.shortest_path(G, start_node, end_node, weight='travel_time')

        #Plot the route and street networks
        ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k')
        
        node_start = []
        node_end = []
        X_to = []
        Y_to = []
        X_from = []
        Y_from = []
        length = []
        travel_time = []

        for u, v in zip(route[:-1], route[1:]):
            node_start.append(u)
            node_end.append(v)
            length.append(round(G.edges[(u, v, 0)]['length']))
            travel_time.append(round(G.edges[(u, v, 0)]['travel_time']))
            X_from.append(G.nodes[u]['x'])
            Y_from.append(G.nodes[u]['y'])
            X_to.append(G.nodes[v]['x'])
            Y_to.append(G.nodes[v]['y'])
            
            
        df = pd.DataFrame(list(zip(node_start, node_end, X_from, Y_from, X_to, Y_to, length, travel_time)),
                  columns =["node_start", "node_end", "X_from", "Y_from", "X_to", "Y_to", "length", 
                            "travel_time"])
        
        def create_line_gdf(df):
            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.X_from, df.Y_from))
            gdf["geometry_to"] = [Point(xy) for xy in zip(gdf.X_to, gdf.Y_to)]
            gdf['line'] = gdf.apply(lambda row: LineString([row['geometry_to'], row['geometry']]), axis=1)

            line_gdf = gdf[["node_start","node_end","length","travel_time", "line"]].set_geometry('line')

            return line_gdf
        
        line_gdf = create_line_gdf(df)
        start = df[df["node_start"] == start_node]
        end = df[df["node_end"] == end_node]
        
        fig = px.scatter_mapbox(df, lon= "X_from", lat="Y_from", zoom=12, width=1000, height=800)
        fig.update_layout(font_size=16,  title={'xanchor': 'center','yanchor': 'top', 'y':0.9, 'x':0.5,}, 
                title_font_size = 24, mapbox_accesstoken=api_token, 
                          mapbox_style = "mapbox://styles/strym/ckhd00st61aum19noz9h8y8kw")
        fig.update_traces(marker=dict(size=6))
        
        st.write(fig)
        
        fig = px.scatter_mapbox(df, lon= "X_from", lat="Y_from", 
                        zoom=13, width=1000, height=800, animation_frame=df.index, mapbox_style="dark")
        fig.data[0].marker = dict(size = 12, color="black")
        fig.add_trace(px.scatter_mapbox(start, lon= "X_from", lat="Y_from").data[0])
        fig.data[1].marker = dict(size = 15, color="red")
        fig.add_trace(px.scatter_mapbox(end, lon= "X_from", lat="Y_from").data[0])
        fig.data[2].marker = dict(size = 15, color="green")
        fig.add_trace(px.line_mapbox(df, lon= "X_from", lat="Y_from").data[0])

        fig.update_layout(font_size=16,  title={'xanchor': 'center','yanchor': 'top', 'y':0.9, 'x':0.5,}, 
                title_font_size = 24, mapbox_accesstoken=api_token)
        st.write(fig)
        

        fig2=Figure(width=550,height=350)
        m2=folium.Map(location=[35.139288, 136.8128218], zoom_start=3)
        fig2.add_child(m2)
        folium.TileLayer('Stamen Terrain').add_to(m2)
        folium.TileLayer('Stamen Toner').add_to(m2)
        folium.TileLayer('Stamen Water Color').add_to(m2)
        folium.TileLayer('cartodbpositron').add_to(m2)
        folium.TileLayer('cartodbdark_matter').add_to(m2)
        folium.LayerControl().add_to(m2)

        
        df = pd.read_csv('nakagawa_shelters.csv')

        df['lon'] = pd.to_numeric(df.lon, errors='coerce')
        df['lat'] = pd.to_numeric(df.lat, errors='coerce')# drop rows with missing lat and lon
        df.dropna(subset=['lat', 'lon'], inplace=True)# convert from string to int

        from streamlit_keplergl import keplergl_static
        from keplergl import KeplerGl

        map_1 = KeplerGl(height=800)
        map_1.add_data(data=df, name="shelters")
        keplergl_static(map_1)

	
elif add_selectbox == 'Visualizations':
    
    st.subheader('PROJECT VISUALIZATIONS')
    st.markdown('<h4>Japan Earthquake Zoning Areas</h4>', unsafe_allow_html=True)
    st.image("Japan_Earthquakes_Zoning.png", width=650)
    st.markdown('<h4>Nakagawa Shelter Maps</h4>', unsafe_allow_html=True)
    st.image("Nakagawa_Shelter_Maps.png", width=650)
    st.markdown('<h4>Nakagawa Building Density Score</h4>', unsafe_allow_html=True)
    st.image("nakagawa_graph_building_density_risk.jpg", width=500)
    st.markdown('<h4>Nakagawa Earthquake Risk Score</h4>', unsafe_allow_html=True)
    st.image("nakagawa_graph_earthquake_risk.jpg", width=500)
 

elif add_selectbox == 'Conclusion':
    
    st.subheader('TECH STACK')

    st.markdown('• Data Gathering - Shelter Details, Latitude, Longitude, Ward Type.', unsafe_allow_html=True)
    st.markdown('• Data Preparation - Merging all the Details, Configuring, Evaluating and Converting it into Readable Format.', unsafe_allow_html=True)
    st.markdown('• Risk Classification - Japan Earthquake Zoning Areas, Nakagawa Evacuation Shelters, Risk Factors of Earthquake and Building Density', unsafe_allow_html=True) 
    st.markdown('• Path Finding Algorithms - Python, Jupyter Notebook (Earthquake Risk Score, Building Density Risk Score, Distance Risk Score and Combined Risk Score.', unsafe_allow_html=True) 
    st.markdown('• Dashboard - Streamlit.', unsafe_allow_html=True) 
    
    st.subheader('PROJECT SUMMARY')

    st.markdown('• Gathering the data about the Shelters (Earthquake, Tsunami and Flood) on Nakagawa Ward with various parameters needed to calculate risk factor and safest path.', unsafe_allow_html=True) 
    st.markdown('• Preparing and pre-processing the data for it to read and determine the risk classification and path finding appropriately.', unsafe_allow_html=True) 
    st.markdown('• Check up, configure and evaluate with the risk factors based on distance, building density and earthquake considerations.', unsafe_allow_html=True) 
    st.markdown('• Devising the safest path using algorithms that gives out the best possible route to take up during emergencies.', unsafe_allow_html=True) 
    st.markdown('• Deploying Safest Path Integrated Web App on Streamlit.', unsafe_allow_html=True) 
    
    st.subheader('CONCLUSION')
    
    st.markdown('An Interactive WebApp to devise safest path in Nakagawa-Ku region, Japan during natural disasters like Earthquakes, Tsunamis and Floods that helps in prioritizing the citizens safety in risk prone zones.', unsafe_allow_html=True)

	
elif add_selectbox == 'Team':
    
    st.subheader('COLLABORATORS')
	
    st.markdown('<a href="https://www.linkedin.com/in/avinash-mahech/">Avinash Mahech</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/prathima-kadari/">Prathima Kadari</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/armielyn-obinguar-9229561b0/">Armielyn Obinguar</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/deepali-bidwai/">Deepali Bidwai</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/shalini-gj-6a006712/">Shalini GJ</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/rhey-ann-magcalas-47541490/">Rhey Ann Magcalas</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/pawan-roy123">Pawan Roy Choudhury</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/ahmedgaal/">Ahmed Gaal</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/mkmanolova/">Monika Manolova</a>',
                unsafe_allow_html=True)
    st.markdown('<a href="https://www.linkedin.com/in/abdulbaaqi/">Abdul Baaqi</a>',
                unsafe_allow_html=True)

    st.subheader('PROJECT MANAGER')

    st.markdown('<a href="https://www.linkedin.com/in/galina-naydenova-msc-fhea-b89856196/">Galina Naydenova</a>', unsafe_allow_html=True)
    
