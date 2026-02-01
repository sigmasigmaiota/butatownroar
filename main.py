import streamlit as st
from branca.element import Element
import leafmap as lm
import leafmap.foliumap as leafmap
import ipywidgets as widgets
from ipyleaflet import Map, basemaps, basemap_to_tiles
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import json
import sys
import io
import os
import branca.colormap as cm

contnet = '''
Data compiled from the American Community Survey for Washington Heights, Inwood, Central Harlem, East Harlem, and the Bronx
'''

st.title('Local Community Snapshot')
st.write('###### U.S. Census Bureau, 2019-2023 ACS 5-Year Estimates, https://data.census.gov/table/, accessed 26 Jan 2026.')
st.markdown(contnet)

# Create two tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Demographics", "Household", "Education", "Health", "Detail", "Economic", "Housing"])

# st.set_page_config(layout="wide")
script_dir = os.path.dirname(__file__)
demo_path = os.path.join(script_dir, 'nta2023acsDemographic.geojson')
socl_path = os.path.join(script_dir, 'nta2023acsSocial.geojson')
econ_path = os.path.join(script_dir, 'nta2023acsEconomic.geojson')
hous_path = os.path.join(script_dir, 'nta2023acsHousing.geojson')

with open(demo_path, 'r') as f:
    geo_dem = gpd.read_file(f, encoding='utf-8', errors='ignore')

with open(socl_path, 'r') as f:
    geo_soc = gpd.read_file(f, encoding='utf-8', errors='ignore')

with open(econ_path, 'r') as f:
    geo_eco = gpd.read_file(f, encoding='utf-8', errors='ignore')

with open(hous_path, 'r') as f:
    geo_hou = gpd.read_file(f, encoding='utf-8', errors='ignore')

# geo_dem = gpd.read_file('nta2023acsDemographic.geojson', 
#                         encoding='utf-8', errors='ignore')
geo_dem = geo_dem.to_crs(epsg=4326)

# geo_eco = gpd.read_file('nta2023acsEconomic.geojson', 
#                         encoding='utf-8', errors='ignore')
geo_eco = geo_eco.to_crs(epsg=4326)

# geo_hou = gpd.read_file('nta2023acsHousing.geojson', 
#                         encoding='utf-8', errors='ignore')
geo_hou = geo_hou.to_crs(epsg=4326)

# geo_soc = gpd.read_file('nta2023acsSocial.geojson', 
#                         encoding='utf-8', errors='ignore')
geo_soc = geo_soc.to_crs(epsg=4326)

def get_dicts(df):
    
    dicts = {}
    
    # List of values to use in calculation
    pcols = list(df.columns[[col.endswith('P') for col in df.columns]])
    
    # Loop to create new columns dynamically
    for i in pcols:
        col_name = f'{i}'
        # Construct the new column name using an f-string
        hex_name = f'{i}_HEX'

        dict_name = f'paint_{i}'

        dicts[dict_name] = dict(zip(df[col_name].dropna(), df[hex_name][df[col_name].notna()]))
        # print(dict_name)
    return dicts

demos = get_dicts(geo_dem)
economic = get_dicts(geo_eco)
social = get_dicts(geo_soc)
housing = get_dicts(geo_hou)

geojsondict_dem = geo_dem.to_geo_dict()
geojsondict_soc = geo_soc.to_geo_dict()
geojsondict_eco = geo_eco.to_geo_dict()
geojsondict_hou = geo_hou.to_geo_dict()
################################################################################################################
################################################################################################################
###############################################################################################     TAB 1
################################################################################################################
################################################################################################################
with tab1:
    st.header("Demographics")
    m1 = leafmap.Map(center=[-73.88, 40.88], 
                     zoom=12,
                     tiles='CartoDB positron-nolabels',
                     min_zoom=12,
                     max_zoom=30,
                     layers_control=True,
                     fullscreen_control=False,
                     height='1200px'
    )

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_less_than_18_yrs'] = geo_dem['PopU181E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_less_than_18_yrs'] = geo_dem['PopU181P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='PopU181P', 
                layer_name='Pct less than 18 yrs',
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                layer_type='fill',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_less_than_18_yrs','Percent_less_than_18_yrs'])
    V1min_val = geo_dem['PopU181P'].min(skipna=True)
    V1max_val = geo_dem['PopU181P'].max(skipna=True)
    V1num_bins = 5
    V1bins = np.linspace(V1min_val, V1max_val, V1num_bins + 1)  # Equal intervals
    V1bins = [round(b, 1) for b in V1bins]  # Round for display
    V1continuous_cmap = cm.linear.viridis.scale(V1min_val, V1max_val)
    V1step_colors = [V1continuous_cmap(x) for x in np.linspace(V1min_val, V1max_val, V1num_bins)]
    V1legend_items = ""
    for i in range(V1num_bins):
        V1label = f"{V1bins[i]}%-{V1bins[i+1]}%"
        V1color = V1step_colors[i]
        V1legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V1color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V1label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V1legend_html = f"""
        <div id="PopU181P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct less than 18 yrs</b><br>
        {V1legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V1legend_html))
    
    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_65_yrs_or_more'] = geo_dem['Pop65pl1E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_65_yrs_or_more'] = geo_dem['Pop65pl1P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='Pop65pl1P', 
                layer_name='Pct 65 yrs or more', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_65_yrs_or_more','Percent_65_yrs_or_more'])
    V2min_val = geo_dem['Pop65pl1P'].min(skipna=True)
    V2max_val = geo_dem['Pop65pl1P'].max(skipna=True)
    V2num_bins = 5
    V2bins = np.linspace(V2min_val, V2max_val, V2num_bins + 1)  # Equal intervals
    V2bins = [round(b, 1) for b in V2bins]  # Round for display
    V2continuous_cmap = cm.linear.viridis.scale(V2min_val, V2max_val)
    V2step_colors = [V2continuous_cmap(x) for x in np.linspace(V2min_val, V2max_val, V2num_bins)]
    V2legend_items = ""
    for i in range(V2num_bins):
        V2label = f"{V2bins[i]}%-{V2bins[i+1]}%"
        V2color = V2step_colors[i]
        V2legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V2color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V2label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V2legend_html = f"""
        <div id="Pop65pl1P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct 65 yrs or more</b><br>
        {V2legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V2legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Males_less_than_18_yrs'] = geo_dem['PopU18ME'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Males_less_than_18_yrs'] = geo_dem['PopU18MP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='PopU18MP', 
                layer_name='Pct Males less than 18 yrs', 
                cmap='viridis', 
                #colors=list(demos['paint_PopU18MP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Males_less_than_18_yrs','Percent_Males_less_than_18_yrs'])
    V3min_val = geo_dem['PopU18MP'].min(skipna=True)
    V3max_val = geo_dem['PopU18MP'].max(skipna=True)
    V3num_bins = 5
    V3bins = np.linspace(V3min_val, V3max_val, V3num_bins + 1)  # Equal intervals
    V3bins = [round(b, 1) for b in V3bins]  # Round for display
    V3continuous_cmap = cm.linear.viridis.scale(V3min_val, V3max_val)
    V3step_colors = [V3continuous_cmap(x) for x in np.linspace(V3min_val, V3max_val, V3num_bins)]
    V3legend_items = ""
    for i in range(V3num_bins):
        V3label = f"{V3bins[i]}%-{V3bins[i+1]}%"
        V3color = V3step_colors[i]
        V3legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V3color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V3label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V3legend_html = f"""
        <div id="PopU18MP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Males less than 18 yrs</b><br>
        {V3legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V3legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Females_less_than_18_yrs'] = geo_dem['PopU18FE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Females_less_than_18_yrs'] = geo_dem['PopU18FP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='PopU18FP', 
                layer_name='Pct Females less than 18 yrs', 
                cmap='viridis', 
                #colors=list(demos['paint_PopU18FP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Females_less_than_18_yrs','Percent_Females_less_than_18_yrs'])
    V4min_val = geo_dem['PopU18FP'].min(skipna=True)
    V4max_val = geo_dem['PopU18FP'].max(skipna=True)
    V4num_bins = 5
    V4bins = np.linspace(V4min_val, V4max_val, V4num_bins + 1)  # Equal intervals
    V4bins = [round(b, 1) for b in V4bins]  # Round for display
    V4continuous_cmap = cm.linear.viridis.scale(V4min_val, V4max_val)
    V4step_colors = [V4continuous_cmap(x) for x in np.linspace(V4min_val, V4max_val, V4num_bins)]
    V4legend_items = ""
    for i in range(V4num_bins):
        V4label = f"{V4bins[i]}%-{V4bins[i+1]}%"
        V4color = V4step_colors[i]
        V4legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V4color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V4label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V4legend_html = f"""
        <div id="PopU18FP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Females less than 18 yrs</b><br>
        {V4legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V4legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Males_65_yrs_or_more'] = geo_dem['Pop65plME'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Males_65_yrs_or_more'] = geo_dem['Pop65plMP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='Pop65plMP', 
                layer_name='Pct Males 65 yrs or more', 
                cmap='viridis', 
                #colors=list(demos['paint_Pop65plMP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Males_65_yrs_or_more','Percent_Males_65_yrs_or_more'])
    V5min_val = geo_dem['Pop65plMP'].min(skipna=True)
    V5max_val = geo_dem['Pop65plMP'].max(skipna=True)
    V5num_bins = 5
    V5bins = np.linspace(V5min_val, V5max_val, V5num_bins + 1)  # Equal intervals
    V5bins = [round(b, 1) for b in V5bins]  # Round for display
    V5continuous_cmap = cm.linear.viridis.scale(V5min_val, V5max_val)
    V5step_colors = [V5continuous_cmap(x) for x in np.linspace(V5min_val, V5max_val, V5num_bins)]
    V5legend_items = ""
    for i in range(V5num_bins):
        V5label = f"{V5bins[i]}%-{V5bins[i+1]}%"
        V5color = V5step_colors[i]
        V5legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V5color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V5label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V5legend_html = f"""
        <div id="Pop65plMP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Males 65 yrs or more</b><br>
        {V5legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V5legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Females_65_yrs_or_more'] = geo_dem['Pop65plFE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Females_65_yrs_or_more'] = geo_dem['Pop65plFP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='Pop65plFP', 
                layer_name='Pct Females 65 yrs or more', 
                cmap='viridis', 
                #colors=list(demos['paint_Pop65plFP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Females_65_yrs_or_more','Percent_Females_65_yrs_or_more'])
    V6min_val = geo_dem['Pop65plFP'].min(skipna=True)
    V6max_val = geo_dem['Pop65plFP'].max(skipna=True)
    V6num_bins = 5
    V6bins = np.linspace(V6min_val, V6max_val, V6num_bins + 1)  # Equal intervals
    V6bins = [round(b, 1) for b in V6bins]  # Round for display
    V6continuous_cmap = cm.linear.viridis.scale(V6min_val, V6max_val)
    V6step_colors = [V6continuous_cmap(x) for x in np.linspace(V6min_val, V6max_val, V6num_bins)]
    V6legend_items = ""
    for i in range(V6num_bins):
        V6label = f"{V4bins[i]}%-{V6bins[i+1]}%"
        V6color = V6step_colors[i]
        V6legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V6color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V6label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V6legend_html = f"""
        <div id="Pop65plFP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Females 65 yrs or more</b><br>
        {V6legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V6legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Hispanic/Latino-a-e_(of_any_race)'] = geo_dem['Hsp1E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Hispanic/Latino-a-e_(of_any_race)'] = geo_dem['Hsp1P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='Hsp1P', 
                layer_name='Pct Hispanic/Latino-a-e (of any race)', 
                cmap='viridis', 
                #colors=list(demos['paint_Hsp1P'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Hispanic/Latino-a-e_(of_any_race)','Percent_Hispanic/Latino-a-e_(of_any_race)'])
    V7min_val = geo_dem['Hsp1P'].min(skipna=True)
    V7max_val = geo_dem['Hsp1P'].max(skipna=True)
    V7num_bins = 5
    V7bins = np.linspace(V7min_val, V7max_val, V7num_bins + 1)  # Equal intervals
    V7bins = [round(b, 1) for b in V7bins]  # Round for display
    V7continuous_cmap = cm.linear.viridis.scale(V7min_val, V7max_val)
    V7step_colors = [V7continuous_cmap(x) for x in np.linspace(V7min_val, V7max_val, V7num_bins)]
    V7legend_items = ""
    for i in range(V7num_bins):
        V7label = f"{V7bins[i]}%-{V7bins[i+1]}%"
        V7color = V7step_colors[i]
        V7legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V7color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V7label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V7legend_html = f"""
        <div id="Hsp1P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Hispanic/Latino-a-e (of any race)</b><br>
        {V7legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V7legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Not_Hispanic/Latino-a-e'] = geo_dem['NHspE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Not_Hispanic/Latino-a-e'] = geo_dem['NHspP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='NHspP', 
                layer_name='Pct Not Hispanic/Latino-a-e', 
                cmap='viridis', 
                #colors=list(demos['paint_NHspP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Not_Hispanic/Latino-a-e','Percent_Not_Hispanic/Latino-a-e'])
    V8min_val = geo_dem['NHspP'].min(skipna=True)
    V8max_val = geo_dem['NHspP'].max(skipna=True)
    V8num_bins = 5
    V8bins = np.linspace(V8min_val, V8max_val, V8num_bins + 1)  # Equal intervals
    V8bins = [round(b, 1) for b in V8bins]  # Round for display
    V8continuous_cmap = cm.linear.viridis.scale(V8min_val, V8max_val)
    V8step_colors = [V8continuous_cmap(x) for x in np.linspace(V8min_val, V8max_val, V8num_bins)]
    V8legend_items = ""
    for i in range(V8num_bins):
        V8label = f"{V8bins[i]}%-{V8bins[i+1]}%"
        V8color = V8step_colors[i]
        V8legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V8color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V8label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V8legend_html = f"""
        <div id="NHspP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Not Hispanic/Latino-a-e</b><br>
        {V8legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V8legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_White_(non-Hispanic)'] = geo_dem['WtNHE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_White_(non-Hispanic)'] = geo_dem['WtNHP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='WtNHP', 
                layer_name='Pct White (non-Hispanic)', 
                cmap='viridis', 
                #colors=list(demos['paint_WtNHP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_White_(non-Hispanic)','Percent_White_(non-Hispanic)'])
    V9min_val = geo_dem['WtNHP'].min(skipna=True)
    V9max_val = geo_dem['WtNHP'].max(skipna=True)
    V9num_bins = 5
    V9bins = np.linspace(V9min_val, V9max_val, V9num_bins + 1)  # Equal intervals
    V9bins = [round(b, 1) for b in V9bins]  # Round for display
    V9continuous_cmap = cm.linear.viridis.scale(V9min_val, V9max_val)
    V9step_colors = [V9continuous_cmap(x) for x in np.linspace(V9min_val, V9max_val, V9num_bins)]
    V9legend_items = ""
    for i in range(V9num_bins):
        V9label = f"{V9bins[i]}%-{V9bins[i+1]}%"
        V9color = V9step_colors[i]
        V9legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V9color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V9label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V9legend_html = f"""
        <div id="WtNHP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct White (non-Hispanic)</b><br>
        {V9legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V9legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Black/African_American_(non-Hispanic)'] = geo_dem['BlNHE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Black/African_American_(non-Hispanic)'] = geo_dem['BlNHP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='BlNHP', 
                layer_name='Pct Black/African American (non-Hispanic)', 
                cmap='viridis', 
                #colors=list(demos['paint_BlNHP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Black/African_American_(non-Hispanic)','Percent_Black/African_American_(non-Hispanic)'])
    V10min_val = geo_dem['BlNHP'].min(skipna=True)
    V10max_val = geo_dem['BlNHP'].max(skipna=True)
    V10num_bins = 5
    V10bins = np.linspace(V10min_val, V10max_val, V10num_bins + 1)  # Equal intervals
    V10bins = [round(b, 1) for b in V10bins]  # Round for display
    V10continuous_cmap = cm.linear.viridis.scale(V10min_val, V10max_val)
    V10step_colors = [V10continuous_cmap(x) for x in np.linspace(V10min_val, V10max_val, V10num_bins)]
    V10legend_items = ""
    for i in range(V10num_bins):
        V10label = f"{V10bins[i]}%-{V10bins[i+1]}%"
        V10color = V10step_colors[i]
        V10legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V10color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V10label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V10legend_html = f"""
        <div id="BlNHP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Black/African American (non-Hispanic)</b><br>
        {V10legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V10legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_American_Indian_and_Alaska_Native_(non-Hispanic)'] = geo_dem['AIANNHE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_American_Indian_and_Alaska_Native_(non-Hispanic)'] = geo_dem['AIANNHP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='AIANNHP', 
                layer_name='Pct American Indian and Alaska Native (non-Hispanic)', 
                cmap='viridis', 
                #colors=list(demos['paint_AIANNHP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_American_Indian_and_Alaska_Native_(non-Hispanic)','Percent_American_Indian_and_Alaska_Native_(non-Hispanic)'])
    V11min_val = geo_dem['AIANNHP'].min(skipna=True)
    V11max_val = geo_dem['AIANNHP'].max(skipna=True)
    V11num_bins = 5
    V11bins = np.linspace(V11min_val, V11max_val, V11num_bins + 1)  # Equal intervals
    V11bins = [round(b, 1) for b in V11bins]  # Round for display
    V11continuous_cmap = cm.linear.viridis.scale(V11min_val, V11max_val)
    V11step_colors = [V11continuous_cmap(x) for x in np.linspace(V11min_val, V11max_val, V11num_bins)]
    V11legend_items = ""
    for i in range(V11num_bins):
        V11label = f"{V11bins[i]}%-{V11bins[i+1]}%"
        V11color = V11step_colors[i]
        V11legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V11color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V11label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V11legend_html = f"""
        <div id="AIANNHP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct American Indian and Alaska Native (non-Hispanic)</b><br>
        {V11legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V11legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Asian_(non-Hispanic)'] = geo_dem['AsnNHE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Asian_(non-Hispanic)'] = geo_dem['AsnNHP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='AsnNHP', 
                layer_name='Pct Asian (non-Hispanic)', 
                cmap='viridis', 
                #colors=list(demos['paint_AsnNHP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Asian_(non-Hispanic)','Percent_Asian_(non-Hispanic)'])
    V12min_val = geo_dem['AsnNHP'].min(skipna=True)
    V12max_val = geo_dem['AsnNHP'].max(skipna=True)
    V12num_bins = 5
    V12bins = np.linspace(V12min_val, V12max_val, V12num_bins + 1)  # Equal intervals
    V12bins = [round(b, 1) for b in V12bins]  # Round for display
    V12continuous_cmap = cm.linear.viridis.scale(V12min_val, V12max_val)
    V12step_colors = [V12continuous_cmap(x) for x in np.linspace(V12min_val, V12max_val, V12num_bins)]
    V12legend_items = ""
    for i in range(V12num_bins):
        V12label = f"{V12bins[i]}%-{V4bins[i+1]}%"
        V12color = V12step_colors[i]
        V12legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V12color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V12label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V12legend_html = f"""
        <div id="AsnNHP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Asian (non-Hispanic)</b><br>
        {V12legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V12legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Other_race_(non-Hispanic)'] = geo_dem['OthNHE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Other_race_(non-Hispanic)'] = geo_dem['OthNHP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='OthNHP', 
                layer_name='Pct Other race (non-Hispanic)', 
                cmap='viridis', 
                #colors=list(demos['paint_OthNHP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Other_race_(non-Hispanic)','Percent_Other_race_(non-Hispanic)'])
    V13min_val = geo_dem['OthNHP'].min(skipna=True)
    V13max_val = geo_dem['OthNHP'].max(skipna=True)
    V13num_bins = 5
    V13bins = np.linspace(V13min_val, V13max_val, V13num_bins + 1)  # Equal intervals
    V13bins = [round(b, 1) for b in V13bins]  # Round for display
    V13continuous_cmap = cm.linear.viridis.scale(V13min_val, V13max_val)
    V13step_colors = [V13continuous_cmap(x) for x in np.linspace(V13min_val, V13max_val, V13num_bins)]
    V13legend_items = ""
    for i in range(V13num_bins):
        V13label = f"{V13bins[i]}%-{V13bins[i+1]}%"
        V13color = V13step_colors[i]
        V13legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V13color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V13label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V13legend_html = f"""
        <div id="OthNHP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Other race (non-Hispanic)</b><br>
        {V13legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V13legend_html))

    geo_dem['Neighborhood'] = geo_dem['ntaname']
    geo_dem['Census_District'] = geo_dem['cdtaname']
    geo_dem['Population_Multiracial_(non-Hispanic)'] = geo_dem['Rc2plNHE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_dem['Percent_Multiracial_(non-Hispanic)'] = geo_dem['Rc2plNHP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m1.add_data(geo_dem, 
                column='Rc2plNHP', 
                # min_zoom=11,
                layer_name='Pct Multiracial (non-Hispanic)', 
                cmap='viridis', 
                #colors=list(demos['paint_Rc2plNHP'].values()), 
                add_legend=False,
                scheme='EqualInterval',
                k=4,
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Multiracial_(non-Hispanic)','Percent_Multiracial_(non-Hispanic)'])
    V14min_val = geo_dem['Rc2plNHP'].min(skipna=True)
    V14max_val = geo_dem['Rc2plNHP'].max(skipna=True)
    V14num_bins = 5
    V14bins = np.linspace(V14min_val, V14max_val, V14num_bins + 1)  # Equal intervals
    V14bins = [round(b, 1) for b in V14bins]  # Round for display
    V14continuous_cmap = cm.linear.viridis.scale(V14min_val, V14max_val)
    V14step_colors = [V14continuous_cmap(x) for x in np.linspace(V14min_val, V14max_val, V14num_bins)]
    V14legend_items = ""
    for i in range(V14num_bins):
        V14label = f"{V14bins[i]}%-{V14bins[i+1]}%"
        V14color = V14step_colors[i]
        V14legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{V14color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{V14label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    V14legend_html = f"""
        <div id="Rc2plNHP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Multiracial (non-Hispanic)</b><br>
        {V14legend_items}
        </div>
        """
    # Add the custom legend to the map
    m1.get_root().html.add_child(Element(V14legend_html))
        
    toggle_js1 = """
            $(document).ready(function(){
                var allPaths = document.querySelectorAll('path');
                // console.log(allPaths);
                var allLabels = document.querySelectorAll('label');
                // console.log(allLabels);
                allLabels[0].textContent = ' Base Map';
                var allDiv = document.querySelectorAll('div[class="leaflet-control-attribution leaflet-control"]');
                // console.log(allDiv);
                allDiv[0].style.display = 'none';
                var allInputs = document.querySelectorAll('input[type="checkbox"]');
                var V1legend = document.getElementById('PopU181P');
                var V2legend = document.getElementById('Pop65pl1P');
                var V3legend = document.getElementById('PopU18MP');
                var V4legend = document.getElementById('PopU18FP');
                var V5legend = document.getElementById('Pop65plMP');
                var V6legend = document.getElementById('Pop65plFP');
                var V7legend = document.getElementById('Hsp1P');
                var V8legend = document.getElementById('NHspP');
                var V9legend = document.getElementById('WtNHP');
                var V10legend = document.getElementById('BlNHP');
                var V11legend = document.getElementById('AIANNHP');
                var V12legend = document.getElementById('AsnNHP');
                var V13legend = document.getElementById('OthNHP');
                var V14legend = document.getElementById('Rc2plNHP');

                const objs1 = [V1legend,V2legend,V3legend,V4legend,V5legend,V6legend,V7legend,V8legend,
                    V9legend,V10legend,V11legend,V12legend,V13legend,V14legend]

                allInputs[0].addEventListener('click', function() {
                    status=allInputs[0].checked;
                    if(status == 'false' & allInputs[0].parentElement.innerText == ' Pct less than 18 yrs'){
                        V1legend.style.zIndex = '0';
                        V1legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[0].parentElement.innerText == ' Pct less than 18 yrs'){
                        V1legend.style.display = 'block';
                        V1legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V1legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[1].addEventListener('click', function() {
                    status=allInputs[1].checked;
                    if(status == 'false' & allInputs[1].parentElement.innerText == ' Pct 65 yrs or more'){
                        V2legend.style.zIndex = '0';
                        V2legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[1].parentElement.innerText == ' Pct 65 yrs or more'){
                        V2legend.style.display = 'block';
                        V2legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V2legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[2].addEventListener('click', function() {
                    status=allInputs[2].checked;
                    if(status == 'false' & allInputs[2].parentElement.innerText == ' Pct Males less than 18 yrs'){
                        V3legend.style.zIndex = '0';
                        V3legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[2].parentElement.innerText == ' Pct Males less than 18 yrs'){
                        V3legend.style.display = 'block';
                        V3legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V3legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[3].addEventListener('click', function() {
                    status=allInputs[3].checked;
                    if(status == 'false' & allInputs[3].parentElement.innerText == ' Pct Females less than 18 yrs'){
                        V4legend.style.zIndex = '0';
                        V4legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[3].parentElement.innerText == ' Pct Females less than 18 yrs'){
                        V4legend.style.display = 'block';
                        V4legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V4legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[4].addEventListener('click', function() {
                    status=allInputs[4].checked;
                    if(status == 'false' & allInputs[4].parentElement.innerText == ' Pct Males 65 yrs or more'){
                        V5legend.style.zIndex = '0';
                        V5legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[4].parentElement.innerText == ' Pct Males 65 yrs or more'){
                        V5legend.style.display = 'block';
                        V5legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V5legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[5].addEventListener('click', function() {
                    status=allInputs[5].checked;
                    if(status == 'false' & allInputs[5].parentElement.innerText == ' Pct Females 65 yrs or more'){
                        V6legend.style.zIndex = '0';
                        V6legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[5].parentElement.innerText == ' Pct Females 65 yrs or more'){
                        V6legend.style.display = 'block';
                        V6legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V6legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[6].addEventListener('click', function() {
                    status=allInputs[6].checked;
                    if(status == 'false' & allInputs[6].parentElement.innerText == ' Pct Hispanic/Latino-a-e (of any race)'){
                        V7legend.style.zIndex = '0';
                        V7legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[6].parentElement.innerText == ' Pct Hispanic/Latino-a-e (of any race)'){
                        V7legend.style.display = 'block';
                        V7legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V7legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[7].addEventListener('click', function() {
                    status=allInputs[7].checked;
                    if(status == 'false' & allInputs[7].parentElement.innerText == ' Pct Not Hispanic/Latino-a-e'){
                        V8legend.style.zIndex = '0';
                        V8legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[7].parentElement.innerText == ' Pct Not Hispanic/Latino-a-e'){
                        V8legend.style.display = 'block';
                        V8legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V8legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[8].addEventListener('click', function() {
                    status=allInputs[8].checked;
                    if(status == 'false' & allInputs[8].parentElement.innerText == ' Pct White (non-Hispanic)'){
                        V9legend.style.zIndex = '0';
                        V9legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[8].parentElement.innerText == ' Pct White (non-Hispanic)'){
                        V9legend.style.display = 'block';
                        V9legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V9legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[9].addEventListener('click', function() {
                    status=allInputs[9].checked;
                    if(status == 'false' & allInputs[9].parentElement.innerText == ' Pct Black/African American (non-Hispanic)'){
                        V10legend.style.zIndex = '0';
                        V10legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[9].parentElement.innerText == ' Pct Black/African American (non-Hispanic)'){
                        V10legend.style.display = 'block';
                        V10legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V10legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[10].addEventListener('click', function() {
                    status=allInputs[10].checked;
                    if(status == 'false' & allInputs[10].parentElement.innerText == ' Pct American Indian and Alaska Native (non-Hispanic)'){
                        V11legend.style.zIndex = '0';
                        V11legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[10].parentElement.innerText == ' Pct American Indian and Alaska Native (non-Hispanic)'){
                        V11legend.style.display = 'block';
                        V11legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V11legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[11].addEventListener('click', function() {
                    status=allInputs[11].checked;
                    if(status == 'false' & allInputs[11].parentElement.innerText == ' Pct Asian (non-Hispanic)'){
                        V12legend.style.zIndex = '0';
                        V12legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[11].parentElement.innerText == ' Pct Asian (non-Hispanic)'){
                        V12legend.style.display = 'block';
                        V12legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V12legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[12].addEventListener('click', function() {
                    status=allInputs[12].checked;
                    if(status == 'false' & allInputs[12].parentElement.innerText == ' Pct Other race (non-Hispanic)'){
                        V13legend.style.zIndex = '0';
                        V13legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[12].parentElement.innerText == ' Pct Other race (non-Hispanic)'){
                        V13legend.style.display = 'block';
                        V13legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V13legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[13].addEventListener('click', function() {
                    status=allInputs[13].checked;
                    if(status == 'false' & allInputs[13].parentElement.innerText == ' Pct Multiracial (non-Hispanic)'){
                        V14legend.style.zIndex = '0';
                        V14legend.style.display = 'none';
                        };
                    if(status == 'true' & allInputs[13].parentElement.innerText == ' Pct Multiracial (non-Hispanic)'){
                        V14legend.style.display = 'block';
                        V14legend.style.zIndex = '1002';
                        objs1.forEach((objs1) => {
                            if (objs1 != V14legend) {
                                objs1.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                
                allInputs[0].click();
                allInputs[1].click();
                allInputs[2].click();
                allInputs[3].click();
                allInputs[4].click();
                allInputs[5].click();
                allInputs[6].click();
                allInputs[7].click();
                allInputs[8].click();
                allInputs[9].click();
                allInputs[10].click();
                allInputs[11].click();
                allInputs[12].click();
                allInputs[13].click();
                
            });
        """
    m1.get_root().script.add_child(Element(toggle_js1))
    
    m1.to_streamlit()
################################################################################################################
################################################################################################################
###############################################################################################     TAB 2
################################################################################################################
################################################################################################################
with tab2:
    st.header("Households")

    m2 = leafmap.Map(center=[-73.88, 40.88], 
                     zoom=12,
                     tiles='CartoDB positron-nolabels',
                     fullscreen_control=False,
                     height='800px',
                     min_zoom=12,
                     max_zoom=30)

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Family_households_(families)'] = geo_soc['Fam1E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Family_households_(families)'] = geo_soc['Fam1P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='Fam1P', 
                layer_name='Pct Family households (families)', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Family_households_(families)','Percent_Family_households_(families)'])
    S1min_val = geo_soc['Fam1P'].min(skipna=True)
    S1max_val = geo_soc['Fam1P'].max(skipna=True)
    S1num_bins = 5
    S1bins = np.linspace(S1min_val, S1max_val, S1num_bins + 1)  # Equal intervals
    S1bins = [round(b, 1) for b in S1bins]  # Round for display
    S1continuous_cmap = cm.linear.viridis.scale(S1min_val, S1max_val)
    S1step_colors = [S1continuous_cmap(x) for x in np.linspace(S1min_val, S1max_val, S1num_bins)]
    S1legend_items = ""
    for i in range(S1num_bins):
        S1label = f"{S1bins[i]}%-{S1bins[i+1]}%"
        S1color = S1step_colors[i]
        S1legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S1color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S1label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S1legend_html = f"""
        <div id="Fam1P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Family households (families)</b><br>
        {S1legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S1legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Householder_living_alone'] = geo_soc['NFamAE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Householder_living_alone'] = geo_soc['NFamAP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='NFamAP', 
                layer_name='Pct Householder living alone', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Householder_living_alone','Percent_Householder_living_alone'])
    S2min_val = geo_soc['NFamAP'].min(skipna=True)
    S2max_val = geo_soc['NFamAP'].max(skipna=True)
    S2num_bins = 5
    S2bins = np.linspace(S2min_val, S2max_val, S2num_bins + 1)  # Equal intervals
    S2bins = [round(b, 1) for b in S2bins]  # Round for display
    S2continuous_cmap = cm.linear.viridis.scale(S2min_val, S2max_val)
    S2step_colors = [S2continuous_cmap(x) for x in np.linspace(S2min_val, S2max_val, S2num_bins)]
    S2legend_items = ""
    for i in range(S2num_bins):
        S2label = f"{S2bins[i]}%-{S2bins[i+1]}%"
        S2color = S2step_colors[i]
        S2legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S2color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S2label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S2legend_html = f"""
        <div id="NFamAP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Householder living alone</b><br>
        {S2legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S2legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_With_own_children_under_18_yrs'] = geo_soc['FamChU18E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_With_own_children_under_18_yrs'] = geo_soc['FamChU18P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='FamChU18P', 
                layer_name='Pct With own children under 18 yrs', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_With_own_children_under_18_yrs','Percent_With_own_children_under_18_yrs'])
    S3min_val = geo_soc['FamChU18P'].min(skipna=True)
    S3max_val = geo_soc['FamChU18P'].max(skipna=True)
    S3num_bins = 5
    S3bins = np.linspace(S3min_val, S3max_val, S3num_bins + 1)  # Equal intervals
    S3bins = [round(b, 1) for b in S3bins]  # Round for display
    S3continuous_cmap = cm.linear.viridis.scale(S3min_val, S3max_val)
    S3step_colors = [S3continuous_cmap(x) for x in np.linspace(S3min_val, S3max_val, S3num_bins)]
    S3legend_items = ""
    for i in range(S3num_bins):
        S3label = f"{S3bins[i]}%-{S3bins[i+1]}%"
        S3color = S3step_colors[i]
        S3legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S3color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S3label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S3legend_html = f"""
        <div id="FamChU18P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct With own children under 18 yrs</b><br>
        {S3legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S3legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Male_householder,_no_spouse_present,_family'] = geo_soc['MHnSE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Male_householder,_no_spouse_present,_family'] = geo_soc['MHnSP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='MHnSP', 
                layer_name='Pct Male householder, no spouse present, family', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Male_householder,_no_spouse_present,_family','Percent_Male_householder,_no_spouse_present,_family'])
    S4min_val = geo_soc['MHnSP'].min(skipna=True)
    S4max_val = geo_soc['MHnSP'].max(skipna=True)
    S4num_bins = 5
    S4bins = np.linspace(S4min_val, S4max_val, S4num_bins + 1)  # Equal intervals
    S4bins = [round(b, 1) for b in S4bins]  # Round for display
    S4continuous_cmap = cm.linear.viridis.scale(S4min_val, S4max_val)
    S4step_colors = [S4continuous_cmap(x) for x in np.linspace(S4min_val, S4max_val, S4num_bins)]
    S4legend_items = ""
    for i in range(S4num_bins):
        S4label = f"{S4bins[i]}%-{S4bins[i+1]}%"
        S4color = S4step_colors[i]
        S4legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S4color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S4label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S4legend_html = f"""
        <div id="MHnSP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Male householder, no spouse present, family</b><br>
        {S4legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S4legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Male_householder,_no_spouse,_with_children_under_18_yrs'] = geo_soc['MHnSChU18E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Male_householder,_no_spouse,_with_children_under_18_yrs'] = geo_soc['MHnSChU18P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='MHnSChU18P', 
                layer_name='Pct Male householder, no spouse, with children under 18 yrs', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Male_householder,_no_spouse,_with_children_under_18_yrs','Percent_Male_householder,_no_spouse,_with_children_under_18_yrs'])
    S5min_val = geo_soc['MHnSChU18P'].min(skipna=True)
    S5max_val = geo_soc['MHnSChU18P'].max(skipna=True)
    S5num_bins = 5
    S5bins = np.linspace(S5min_val, S5max_val, S5num_bins + 1)  # Equal intervals
    S5bins = [round(b, 1) for b in S5bins]  # Round for display
    S5continuous_cmap = cm.linear.viridis.scale(S5min_val, S5max_val)
    S5step_colors = [S5continuous_cmap(x) for x in np.linspace(S5min_val, S5max_val, S5num_bins)]
    S5legend_items = ""
    for i in range(S5num_bins):
        S5label = f"{S5bins[i]}%-{S5bins[i+1]}%"
        S5color = S5step_colors[i]
        S5legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S5color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S5label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S5legend_html = f"""
        <div id="MHnSChU18P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Male householder, no spouse, with children under 18 yrs</b><br>
        {S5legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S5legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Female_householder,_no_spouse_present,_family'] = geo_soc['FHnSE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Female_householder,_no_spouse_present,_family'] = geo_soc['FHnSP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='FHnSP', 
                layer_name='Pct Female householder, no spouse present, family', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Female_householder,_no_spouse_present,_family','Percent_Female_householder,_no_spouse_present,_family'])
    S6min_val = geo_soc['FHnSP'].min(skipna=True)
    S6max_val = geo_soc['FHnSP'].max(skipna=True)
    S6num_bins = 5
    S6bins = np.linspace(S6min_val, S6max_val, S6num_bins + 1)  # Equal intervals
    S6bins = [round(b, 1) for b in S6bins]  # Round for display
    S6continuous_cmap = cm.linear.viridis.scale(S6min_val, S6max_val)
    S6step_colors = [S6continuous_cmap(x) for x in np.linspace(S6min_val, S6max_val, S6num_bins)]
    S6legend_items = ""
    for i in range(S6num_bins):
        S6label = f"{S6bins[i]}%-{S6bins[i+1]}%"
        S6color = S6step_colors[i]
        S6legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S6color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S6label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S6legend_html = f"""
        <div id="FHnSP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Female householder, no spouse present, family</b><br>
        {S6legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S6legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Female_householder,_no_spouse,_with_children_under_18_yrs'] = geo_soc['FHnSChU18E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Female_householder,_no_spouse,_with_children_under_18_yrs'] = geo_soc['FHnSChU18P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='FHnSChU18P', 
                layer_name='Pct Female householder, no spouse, with children under 18 yrs', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Female_householder,_no_spouse,_with_children_under_18_yrs','Percent_Female_householder,_no_spouse,_with_children_under_18_yrs'])
    S7min_val = geo_soc['FHnSChU18P'].min(skipna=True)
    S7max_val = geo_soc['FHnSChU18P'].max(skipna=True)
    S7num_bins = 5
    S7bins = np.linspace(S7min_val, S7max_val, S7num_bins + 1)  # Equal intervals
    S7bins = [round(b, 1) for b in S7bins]  # Round for display
    S7continuous_cmap = cm.linear.viridis.scale(S7min_val, S7max_val)
    S7step_colors = [S7continuous_cmap(x) for x in np.linspace(S7min_val, S7max_val, S7num_bins)]
    S7legend_items = ""
    for i in range(S7num_bins):
        S7label = f"{S7bins[i]}%-{S7bins[i+1]}%"
        S7color = S7step_colors[i]
        S7legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S7color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S7label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S7legend_html = f"""
        <div id="FHnSChU18P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Female householder, no spouse, with children under 18 yrs</b><br>
        {S7legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S7legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Nonfamily_households'] = geo_soc['NFam1E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Nonfamily_households'] = geo_soc['NFam1P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='NFam1P', 
                layer_name='Pct Nonfamily households', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Nonfamily_households','Percent_Nonfamily_households'])
    S8min_val = geo_soc['NFam1P'].min(skipna=True)
    S8max_val = geo_soc['NFam1P'].max(skipna=True)
    S8num_bins = 5
    S8bins = np.linspace(S8min_val, S8max_val, S8num_bins + 1)  # Equal intervals
    S8bins = [round(b, 1) for b in S8bins]  # Round for display
    S8continuous_cmap = cm.linear.viridis.scale(S8min_val, S8max_val)
    S8step_colors = [S8continuous_cmap(x) for x in np.linspace(S8min_val, S8max_val, S8num_bins)]
    S8legend_items = ""
    for i in range(S8num_bins):
        S8label = f"{S8bins[i]}%-{S8bins[i+1]}%"
        S8color = S8step_colors[i]
        S8legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S8color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S8label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S8legend_html = f"""
        <div id="NFam1P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Nonfamily households</b><br>
        {S8legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S8legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Householder_living_alone,_65_yrs_and_over'] = geo_soc['NFamA65plE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Householder_living_alone,_65_yrs_and_over'] = geo_soc['NFamA65plP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='NFamA65plP', 
                layer_name='Pct Householder living alone, 65 yrs and over', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Householder_living_alone,_65_yrs_and_over','Percent_Householder_living_alone,_65_yrs_and_over'])
    S9min_val = geo_soc['NFamA65plP'].min(skipna=True)
    S9max_val = geo_soc['NFamA65plP'].max(skipna=True)
    S9num_bins = 5
    S9bins = np.linspace(S9min_val, S9max_val, S9num_bins + 1)  # Equal intervals
    S9bins = [round(b, 1) for b in S9bins]  # Round for display
    S9continuous_cmap = cm.linear.viridis.scale(S9min_val, S9max_val)
    S9step_colors = [S9continuous_cmap(x) for x in np.linspace(S9min_val, S9max_val, S9num_bins)]
    S9legend_items = ""
    for i in range(S9num_bins):
        S9label = f"{S9bins[i]}%-{S9bins[i+1]}%"
        S9color = S9step_colors[i]
        S9legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S9color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S9label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S9legend_html = f"""
        <div id="NFamA65plP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Householder living alone, 65 yrs and over</b><br>
        {S9legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S9legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Households_with_one_or_more_people_under_18_yrs'] = geo_soc['HH1plU18E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Households_with_one_or_more_people_under_18_yrs'] = geo_soc['HH1plU18P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='HH1plU18P', 
                layer_name='Pct Households with one or more people under 18 yrs', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Households_with_one_or_more_people_under_18_yrs','Percent_Households_with_one_or_more_people_under_18_yrs'])
    S10min_val = geo_soc['HH1plU18P'].min(skipna=True)
    S10max_val = geo_soc['HH1plU18P'].max(skipna=True)
    S10num_bins = 5
    S10bins = np.linspace(S10min_val, S10max_val, S10num_bins + 1)  # Equal intervals
    S10bins = [round(b, 1) for b in S10bins]  # Round for display
    S10continuous_cmap = cm.linear.viridis.scale(S10min_val, S10max_val)
    S10step_colors = [S10continuous_cmap(x) for x in np.linspace(S10min_val, S10max_val, S10num_bins)]
    S10legend_items = ""
    for i in range(S10num_bins):
        S10label = f"{S10bins[i]}%-{S10bins[i+1]}%"
        S10color = S10step_colors[i]
        S10legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S10color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S10label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S10legend_html = f"""
        <div id="HH1plU18P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Households with one or more people under 18 yrs</b><br>
        {S10legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S10legend_html))
    
    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Households_with_one_or_more_people_65_yrs_and_over'] = geo_soc['HH1pl65plE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Households_with_one_or_more_people_65_yrs_and_over'] = geo_soc['HH1pl65plP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='HH1pl65plP', 
                layer_name='Pct Households with one or more people 65 yrs and over', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Households_with_one_or_more_people_65_yrs_and_over','Percent_Households_with_one_or_more_people_65_yrs_and_over'])
    S11min_val = geo_soc['HH1pl65plP'].min(skipna=True)
    S11max_val = geo_soc['HH1pl65plP'].max(skipna=True)
    S11num_bins = 5
    S11bins = np.linspace(S11min_val, S11max_val, S11num_bins + 1)  # Equal intervals
    S11bins = [round(b, 1) for b in S11bins]  # Round for display
    S11continuous_cmap = cm.linear.viridis.scale(S11min_val, S11max_val)
    S11step_colors = [S11continuous_cmap(x) for x in np.linspace(S11min_val, S11max_val, S11num_bins)]
    S11legend_items = ""
    for i in range(S11num_bins):
        S11label = f"{S11bins[i]}%-{S11bins[i+1]}%"
        S11color = S11step_colors[i]
        S11legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S11color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S11label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S11legend_html = f"""
        <div id="HH1pl65plP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Households with one or more people 65 yrs and over</b><br>
        {S11legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S11legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Grandparents_responsible_for_grandchildren'] = geo_soc['GpRGcU18E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Grandparents_responsible_for_grandchildren'] = geo_soc['GpRGcU18P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='GpRGcU18P', 
                layer_name='Pct Grandparents responsible for grandchildren', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Grandparents_responsible_for_grandchildren','Percent_Grandparents_responsible_for_grandchildren'])
    S12min_val = geo_soc['GpRGcU18P'].min(skipna=True)
    S12max_val = geo_soc['GpRGcU18P'].max(skipna=True)
    S12num_bins = 5
    S12bins = np.linspace(S12min_val, S12max_val, S12num_bins + 1)  # Equal intervals
    S12bins = [round(b, 1) for b in S12bins]  # Round for display
    S12continuous_cmap = cm.linear.viridis.scale(S12min_val, S12max_val)
    S12step_colors = [S12continuous_cmap(x) for x in np.linspace(S12min_val, S12max_val, S12num_bins)]
    S12legend_items = ""
    for i in range(S12num_bins):
        S12label = f"{S12bins[i]}%-{S12bins[i+1]}%"
        S12color = S12step_colors[i]
        S12legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S12color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S12label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S12legend_html = f"""
        <div id="GpRGcU18P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Grandparents responsible for grandchildren</b><br>
        {S12legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S12legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Males_15_yrs_and_over,_never_married'] = geo_soc['MS_MNvMrdE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Males_15_yrs_and_over,_never_married'] = geo_soc['MS_MNvMrdP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='MS_MNvMrdP', 
                layer_name='Pct Males 15 yrs and over, never married', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Males_15_yrs_and_over,_never_married','Percent_Males_15_yrs_and_over,_never_married'])
    S13min_val = geo_soc['MS_MNvMrdP'].min(skipna=True)
    S13max_val = geo_soc['MS_MNvMrdP'].max(skipna=True)
    S13num_bins = 5
    S13bins = np.linspace(S13min_val, S13max_val, S13num_bins + 1)  # Equal intervals
    S13bins = [round(b, 1) for b in S13bins]  # Round for display
    S13continuous_cmap = cm.linear.viridis.scale(S13min_val, S13max_val)
    S13step_colors = [S13continuous_cmap(x) for x in np.linspace(S13min_val, S13max_val, S13num_bins)]
    S13legend_items = ""
    for i in range(S13num_bins):
        S13label = f"{S13bins[i]}%-{S13bins[i+1]}%"
        S13color = S13step_colors[i]
        S13legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S13color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S13label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S13legend_html = f"""
        <div id="MS_MNvMrdP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Males 15 yrs and over, never married</b><br>
        {S13legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S13legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Females_15_yrs_and_over,_never_married'] = geo_soc['MS_FNvMrdE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Females_15_yrs_and_over,_never_married'] = geo_soc['MS_FNvMrdP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='MS_FNvMrdP', 
                layer_name='Pct Females 15 yrs and over, never married', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Females_15_yrs_and_over,_never_married','Percent_Females_15_yrs_and_over,_never_married'])
    S14min_val = geo_soc['MS_FNvMrdP'].min(skipna=True)
    S14max_val = geo_soc['MS_FNvMrdP'].max(skipna=True)
    S14num_bins = 5
    S14bins = np.linspace(S14min_val, S14max_val, S14num_bins + 1)  # Equal intervals
    S14bins = [round(b, 1) for b in S14bins]  # Round for display
    S14continuous_cmap = cm.linear.viridis.scale(S14min_val, S14max_val)
    S14step_colors = [S14continuous_cmap(x) for x in np.linspace(S14min_val, S14max_val, S14num_bins)]
    S14legend_items = ""
    for i in range(S14num_bins):
        S14label = f"{S14bins[i]}%-{S14bins[i+1]}%"
        S14color = S14step_colors[i]
        S14legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S14color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S14label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S14legend_html = f"""
        <div id="MS_FNvMrdP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Females 15 yrs and over, never married</b><br>
        {S14legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S14legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Residence_1_yr_ago,_same_house'] = geo_soc['SmHsE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Residence_1_yr_ago,_same_house'] = geo_soc['SmHsP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='SmHsP', 
                layer_name='Pct Residence 1 yr ago, same house', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Residence_1_yr_ago,_same_house','Percent_Residence_1_yr_ago,_same_house'])
    S15min_val = geo_soc['SmHsP'].min(skipna=True)
    S15max_val = geo_soc['SmHsP'].max(skipna=True)
    S15num_bins = 5
    S15bins = np.linspace(S15min_val, S15max_val, S15num_bins + 1)  # Equal intervals
    S15bins = [round(b, 1) for b in S15bins]  # Round for display
    S15continuous_cmap = cm.linear.viridis.scale(S15min_val, S15max_val)
    S15step_colors = [S15continuous_cmap(x) for x in np.linspace(S15min_val, S15max_val, S15num_bins)]
    S15legend_items = ""
    for i in range(S15num_bins):
        S15label = f"{S15bins[i]}%-{S15bins[i+1]}%"
        S15color = S15step_colors[i]
        S15legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S15color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S15label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S15legend_html = f"""
        <div id="SmHsP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Residence 1 yr ago, same house</b><br>
        {S15legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S15legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Residence_1_yr_ago,_different_house'] = geo_soc['DfHs1E'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Residence_1_yr_ago,_different_house'] = geo_soc['DfHs1P'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='DfHs1P', 
                layer_name='Pct Residence 1 yr ago, different house', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Residence_1_yr_ago,_different_house','Percent_Residence_1_yr_ago,_different_house'])
    S16min_val = geo_soc['DfHs1P'].min(skipna=True)
    S16max_val = geo_soc['DfHs1P'].max(skipna=True)
    S16num_bins = 5
    S16bins = np.linspace(S16min_val, S16max_val, S16num_bins + 1)  # Equal intervals
    S16bins = [round(b, 1) for b in S16bins]  # Round for display
    S16continuous_cmap = cm.linear.viridis.scale(S16min_val, S16max_val)
    S16step_colors = [S16continuous_cmap(x) for x in np.linspace(S16min_val, S16max_val, S16num_bins)]
    S16legend_items = ""
    for i in range(S16num_bins):
        S16label = f"{S16bins[i]}%-{S16bins[i+1]}%"
        S16color = S16step_colors[i]
        S16legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S16color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S16label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S16legend_html = f"""
        <div id="DfHs1P" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Residence 1 yr ago, different house</b><br>
        {S16legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S16legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Residence_1_yr_ago_different house,_same_county'] = geo_soc['DfHsSmCntE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Residence_1_yr_ago_different house,_same_county'] = geo_soc['DfHsSmCntP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='DfHsSmCntP', 
                layer_name='Pct Residence 1 yr ago different house, same county', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Residence_1_yr_ago_different house,_same_county','Percent_Residence_1_yr_ago_different house,_same_county'])
    S17min_val = geo_soc['DfHsSmCntP'].min(skipna=True)
    S17max_val = geo_soc['DfHsSmCntP'].max(skipna=True)
    S17num_bins = 5
    S17bins = np.linspace(S17min_val, S17max_val, S17num_bins + 1)  # Equal intervals
    S17bins = [round(b, 1) for b in S17bins]  # Round for display
    S17continuous_cmap = cm.linear.viridis.scale(S17min_val, S17max_val)
    S17step_colors = [S17continuous_cmap(x) for x in np.linspace(S17min_val, S17max_val, S17num_bins)]
    S17legend_items = ""
    for i in range(S17num_bins):
        S17label = f"{S17bins[i]}%-{S17bins[i+1]}%"
        S17color = S17step_colors[i]
        S17legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S17color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S17label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S17legend_html = f"""
        <div id="DfHsSmCntP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Residence 1 yr ago different house, same county</b><br>
        {S17legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S17legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Residence_1_yr_ago_different house,_different_county_within_NYC'] = geo_soc['DHDfCntNYCE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Residence_1_yr_ago_different house,_different_county_within_NYC'] = geo_soc['DHDfCntNYCP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='DHDfCntNYCP', 
                layer_name='Pct Residence 1 yr ago different house, different county within NYC', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Residence_1_yr_ago_different house,_different_county_within_NYC','Percent_Residence_1_yr_ago_different house,_different_county_within_NYC'])
    S18min_val = geo_soc['DHDfCntNYCP'].min(skipna=True)
    S18max_val = geo_soc['DHDfCntNYCP'].max(skipna=True)
    S18num_bins = 5
    S18bins = np.linspace(S18min_val, S18max_val, S18num_bins + 1)  # Equal intervals
    S18bins = [round(b, 1) for b in S18bins]  # Round for display
    S18continuous_cmap = cm.linear.viridis.scale(S18min_val, S18max_val)
    S18step_colors = [S18continuous_cmap(x) for x in np.linspace(S18min_val, S18max_val, S18num_bins)]
    S18legend_items = ""
    for i in range(S18num_bins):
        S18label = f"{S18bins[i]}%-{S18bins[i+1]}%"
        S18color = S18step_colors[i]
        S18legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S18color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S18label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S18legend_html = f"""
        <div id="DHDfCntNYCP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Residence 1 yr ago different house, different county within NYC</b><br>
        {S18legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S18legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Residence_1_yr_ago_different house,_different_county_outside_NYC'] = geo_soc['DHnoNYCE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Residence_1_yr_ago_different house,_different_county_outside_NYC'] = geo_soc['DHnoNYCP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='DHnoNYCP', 
                layer_name='Pct Residence 1 yr ago different house, different county outside NYC', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Residence_1_yr_ago_different house,_different_county_outside_NYC','Percent_Residence_1_yr_ago_different house,_different_county_outside_NYC'])
    S19min_val = geo_soc['DHnoNYCP'].min(skipna=True)
    S19max_val = geo_soc['DHnoNYCP'].max(skipna=True)
    S19num_bins = 5
    S19bins = np.linspace(S19min_val, S19max_val, S19num_bins + 1)  # Equal intervals
    S19bins = [round(b, 1) for b in S19bins]  # Round for display
    S19continuous_cmap = cm.linear.viridis.scale(S19min_val, S19max_val)
    S19step_colors = [S19continuous_cmap(x) for x in np.linspace(S19min_val, S19max_val, S19num_bins)]
    S19legend_items = ""
    for i in range(S19num_bins):
        S19label = f"{S19bins[i]}%-{S19bins[i+1]}%"
        S19color = S19step_colors[i]
        S19legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S19color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S19label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S19legend_html = f"""
        <div id="DHnoNYCP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Residence 1 yr ago different house, different county outside NYC</b><br>
        {S19legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S19legend_html))

    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # geo_soc['Census_District'] = geo_soc['cdtaname']
    geo_soc['Population_Residence_1_yr_ago_different house,_abroad'] = geo_soc['AbroadE'].fillna(0).apply(lambda x: f"{x:,}")
    geo_soc['Percent_Residence_1_yr_ago_different house,_abroad'] = geo_soc['AbroadP'].fillna(0).apply(lambda x: f"{x:.1f}%")
    
    m2.add_data(geo_soc, 
                column='AbroadP', 
                layer_name='Pct Residence 1 yr ago different house, abroad', 
                cmap='viridis', 
                add_legend=False,
                scheme='EqualInterval',
                legend_kwds={'fmt': '{:.1f}',
                             'interval': False},
                fields=['Neighborhood','Population_Residence_1_yr_ago_different house,_abroad','Percent_Residence_1_yr_ago_different house,_abroad'])
    S20min_val = geo_soc['AbroadP'].min(skipna=True)
    S20max_val = geo_soc['AbroadP'].max(skipna=True)
    S20num_bins = 5
    S20bins = np.linspace(S20min_val, S20max_val, S20num_bins + 1)  # Equal intervals
    S20bins = [round(b, 1) for b in S20bins]  # Round for display
    S20continuous_cmap = cm.linear.viridis.scale(S20min_val, S20max_val)
    S20step_colors = [S20continuous_cmap(x) for x in np.linspace(S20min_val, S20max_val, S20num_bins)]
    S20legend_items = ""
    for i in range(S20num_bins):
        S20label = f"{S20bins[i]}%-{S20bins[i+1]}%"
        S20color = S20step_colors[i]
        S20legend_items += f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{S20color}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{S20label}</span>
        </div>
        """
    # Custom HTML/CSS Viridis legend (self-contained)
    S20legend_html = f"""
        <div id="AbroadP" style="
            position: fixed; 
            bottom: 50px; left: 5px; 
            width: 180px; height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 1000; 
            font-size: 14px;
            padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
        <b>Pct Residence 1 yr ago different house, abroad</b><br>
        {S20legend_items}
        </div>
        """
    # Add the custom legend to the map
    m2.get_root().html.add_child(Element(S20legend_html))

    toggle_js2 = """
            $(document).ready(function(){
                var allDiv = document.querySelectorAll('div[class="leaflet-control-attribution leaflet-control"]');

                allDiv[0].style.display = 'none';
                var allInputs = document.querySelectorAll('input[type="checkbox"]');

                var S1legend = document.getElementById('Fam1P');
                var S2legend = document.getElementById('NFamAP');
                var S3legend = document.getElementById('FamChU18P');
                var S4legend = document.getElementById('MHnSP');
                var S5legend = document.getElementById('MHnSChU18P');
                var S6legend = document.getElementById('FHnSP');
                var S7legend = document.getElementById('FHnSChU18P');
                var S8legend = document.getElementById('NFam1P');
                var S9legend = document.getElementById('NFamA65plP');
                var S10legend = document.getElementById('HH1plU18P'); 
                var S11legend = document.getElementById('HH1pl65plP');
                var S12legend = document.getElementById('GpRGcU18P'); 
                var S13legend = document.getElementById('MS_MNvMrdP');
                var S14legend = document.getElementById('MS_FNvMrdP');
                var S15legend = document.getElementById('SmHsP');
                var S16legend = document.getElementById('DfHs1P');
                var S17legend = document.getElementById('DfHsSmCntP');
                var S18legend = document.getElementById('DHDfCntNYCP');
                var S19legend = document.getElementById('DHnoNYCP');
                var S20legend = document.getElementById('AbroadP');
                // var S21legend = document.getElementById('SalesOffP');
                // var S22legend = document.getElementById('NRCnstMntP'); 
                // var S23legend = document.getElementById('PrdTrnsMMP');

                const obj2 = [S1legend,S2legend,S3legend,S4legend,S5legend,S6legend,S7legend,S8legend,S9legend,S10legend,
                    S11legend,S12legend,S13legend,S14legend,S15legend,S16legend,S17legend,S18legend,S19legend,S20legend] 

                allInputs[0].addEventListener('click', function() {
                    status=allInputs[0].checked;
                    if(status == 'false'){
                        S1legend.style.zIndex = '0';
                        S1legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S1legend.style.display = 'block';
                        S1legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S1legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        };
                
                });
                allInputs[1].addEventListener('click', function() {
                    status=allInputs[1].checked;
                    if(status == 'false'){
                        S2legend.style.zIndex = '0';
                        S2legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S2legend.style.display = 'block';
                        S2legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S2legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[2].addEventListener('click', function() {
                    status=allInputs[2].checked;
                    if(status == 'false'){
                        S3legend.style.zIndex = '0';
                        S3legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S3legend.style.display = 'block';
                        S3legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S3legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[3].addEventListener('click', function() {
                    status=allInputs[3].checked;
                    if(status == 'false'){
                        S4legend.style.zIndex = '0';
                        S4legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S4legend.style.display = 'block';
                        S4legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S4legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[4].addEventListener('click', function() {
                    status=allInputs[4].checked;
                    if(status == 'false'){
                        S5legend.style.zIndex = '0';
                        S5legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S5legend.style.display = 'block';
                        S5legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S5legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[5].addEventListener('click', function() {
                    status=allInputs[5].checked;
                    if(status == 'false'){
                        S6legend.style.zIndex = '0';
                        S6legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S6legend.style.display = 'block';
                        S6legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S6legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[6].addEventListener('click', function() {
                    status=allInputs[6].checked;
                    if(status == 'false'){
                        S7legend.style.zIndex = '0';
                        S7legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S7legend.style.display = 'block';
                        S7legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S7legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[7].addEventListener('click', function() {
                    status=allInputs[7].checked;
                    if(status == 'false'){
                        S8legend.style.zIndex = '0';
                        S8legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S8legend.style.display = 'block';
                        S8legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S8legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[8].addEventListener('click', function() {
                    status=allInputs[8].checked;
                    if(status == 'false'){
                        S9legend.style.zIndex = '0';
                        S9legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S9legend.style.display = 'block';
                        S9legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S9legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[9].addEventListener('click', function() {
                    status=allInputs[9].checked;
                    if(status == 'false'){
                        S10legend.style.zIndex = '0';
                        S10legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S10legend.style.display = 'block';
                        S10legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S10legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[10].addEventListener('click', function() {
                    status=allInputs[10].checked;
                    if(status == 'false'){
                        S11legend.style.zIndex = '0';
                        S11legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S11legend.style.display = 'block';
                        S11legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S11legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[11].addEventListener('click', function() {
                    status=allInputs[11].checked;
                    if(status == 'false'){
                        S12legend.style.zIndex = '0';
                        S12legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S12legend.style.display = 'block';
                        S12legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S12legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[12].addEventListener('click', function() {
                    status=allInputs[12].checked;
                    if(status == 'false'){
                        S13legend.style.zIndex = '0';
                        S13legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S13legend.style.display = 'block';
                        S13legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S13legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[13].addEventListener('click', function() {
                    status=allInputs[13].checked;
                    if(status == 'false'){
                        S14legend.style.zIndex = '0';
                        S14legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S14legend.style.display = 'block';
                        S14legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S14legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[14].addEventListener('click', function() {
                    status=allInputs[14].checked;
                    if(status == 'false'){
                        S15legend.style.zIndex = '0';
                        S15legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S15legend.style.display = 'block';
                        S15legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S15legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[15].addEventListener('click', function() {
                    status=allInputs[15].checked;
                    if(status == 'false'){
                        S16legend.style.zIndex = '0';
                        S16legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S16legend.style.display = 'block';
                        S16legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S16legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[16].addEventListener('click', function() {
                    status=allInputs[16].checked;
                    if(status == 'false'){
                        S17legend.style.zIndex = '0';
                        S17legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S17legend.style.display = 'block';
                        S17legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S17legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[17].addEventListener('click', function() {
                    status=allInputs[17].checked;
                    if(status == 'false'){
                        S18legend.style.zIndex = '0';
                        S18legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S18legend.style.display = 'block';
                        S18legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S18legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[18].addEventListener('click', function() {
                    status=allInputs[18].checked;
                    if(status == 'false'){
                        S19legend.style.zIndex = '0';
                        S19legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S19legend.style.display = 'block';
                        S19legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S19legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });
                allInputs[19].addEventListener('click', function() {
                    status=allInputs[19].checked;
                    if(status == 'false'){
                        S20legend.style.zIndex = '0';
                        S20legend.style.display = 'none';
                        };
                    if(status == 'true'){
                        S20legend.style.display = 'block';
                        S20legend.style.zIndex = '1002';
                        obj2.forEach((obj2) => {
                            if (obj2 != S20legend) {
                                obj2.style.zIndex = '1000';
                                }
                            });
                        
                        };
                
                });

                allInputs[0].click();
                allInputs[1].click();
                allInputs[2].click();
                allInputs[3].click();
                allInputs[4].click();
                allInputs[5].click();
                allInputs[6].click();
                allInputs[7].click();
                allInputs[8].click();
                allInputs[9].click();
                allInputs[10].click();
                allInputs[11].click();
                allInputs[12].click();
                allInputs[13].click();
                allInputs[14].click();
                allInputs[15].click();
                allInputs[16].click();
                allInputs[17].click();
                allInputs[18].click();
                allInputs[19].click();
                // allInputs[20].click();
                // allInputs[21].click();
                // allInputs[22].click();
                
            });
        """
    m2.get_root().script.add_child(Element(toggle_js2))

    m2.to_streamlit()
################################################################################################################
################################################################################################################
###############################################################################################     TAB 3
################################################################################################################
################################################################################################################
with tab3:
    st.header("Education")
    m3 = leafmap.Map(center=[-73.88, 40.88], 
                     zoom=12,
                     tiles='CartoDB positron-nolabels',
                     fullscreen_control=False,
                     height='800px',
                     min_zoom=12,
                     max_zoom=30)

    # Create an empty dictionary to store your data
    varlist3 = ['SE_NScPSc','SE_Kndgtn','SE_G1t8','SE_G9t12','SE_ClgGSc','EA_LT9G','EA_9t12ND','EA_HScGrd','EA_SClgND',
                'EA_AscD','EA_BchD','EA_GrdPfD','EA_LTHSGr','EA_BchDH']
    vardesc3 = ['Nursery school, preschool enrolled','Kindergarten enrolled','Elementary school enrolled (grades 1-8)',
                'High school enrolled (grades 9-12)','College or graduate school enrolled','Less than 9th grade, 25 yrs and over',
                '9th to 12th grade, no diploma, 25 yrs and over','High school graduate (includes equivalency), 25 yrs and over',
                'Some college, no degree, 25 yrs and over','Associate degree, 25 yrs and over','Bachelor degree, 25 yrs and over',
                'Graduate or professional degree, 25 yrs and over','Less than high school graduate, 25 yrs and over',
                'Bachelor degree or higher, 25 yrs and over']
    leglist3 = []
    Pvarlist = []
    
    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # Use a for loop to populate the dictionary
    for i in range(len(varlist3)):
        legname = f"SC{i}legend"
        leglist3.append(legname)
        legmin = f"SC{i}min_val"
        legmax = f"SC{i}max_val"
        legnum_bins = f"SC{i}num_bins"
        legbins = f"SC{i}bins"
        legcontinuous_cmap = f"SC{i}continuous_cmap"
        legstep_colors = f"SC{i}step_colors"
        leg_items = f"SC{i}legend_items"
        leglabel = f"SC{i}label"
        legcolor = f"SC{i}color"
        leghtml3 = f"SC{i}legend_html"
        varname = varlist3[i]
        vardesc = vardesc3[i]
        vardescUR = vardesc3[i].replace(" ","_")
        Evarname = varname + 'E'
        Pvarname = varname + 'P'
        Pvarlist.append(Pvarname)
        POPvardesc = 'Population ' + vardesc
        PCTvardesc = 'Pct ' + vardesc
        POPvardescUR = 'Population_' + vardescUR
        PCTvardescUR = 'Pct_' + vardescUR
        
        geo_soc[POPvardescUR] = geo_soc[Evarname].fillna(0).apply(lambda x: f"{x:,}")
        geo_soc[PCTvardescUR] = geo_soc[Pvarname].fillna(0).apply(lambda x: f"{x:.1f}%")
        
        m3.add_data(geo_soc,
                    column=Pvarname,
                    layer_name=PCTvardesc,
                    cmap='viridis',
                    add_legend=False,
                    scheme='EqualInterval',
                    legend_kwds={'fmt': '{:.1f}',
                                 'interval': False},
                    fields=['Neighborhood',POPvardescUR,PCTvardescUR])
        legmin = geo_soc[Pvarname].min(skipna=True)
        legmax = geo_soc[Pvarname].max(skipna=True)
        legnum_bins = 5
        legbins = np.linspace(legmin, legmax, legnum_bins + 1)  # Equal intervals
        legbins = [round(b, 1) for b in legbins]  # Round for display
        legcontinuous_cmap = cm.linear.viridis.scale(legmin, legmax)
        legstep_colors = [legcontinuous_cmap(x) for x in np.linspace(legmin, legmax, legnum_bins)]
        leg_items3 = ""
        for n in range(legnum_bins):
            leglabel = f"{legbins[n]}%-{legbins[n+1]}%"
            legcolor = legstep_colors[n]
            leg_items3 += f"""
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{legcolor}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{leglabel}</span>
            </div>
            """
            # Custom HTML/CSS Viridis legend (self-contained)
        leghtml3 = f"""
        <div id="{Pvarname}" style="position:fixed; bottom:50px; left:5px; width:180px; height:auto; background-color: white; 
        border:2px solid grey; z-index:1000; font-size:14px; padding:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <b>{PCTvardesc}</b><br>{leg_items3}</div>"""
        # Add the custom legend to the map
        m3.get_root().html.add_child(Element(leghtml3))
    javaitems3 = ""
    javachunks3 = ""
    javaclicks3 = ""
    for k in range(len(leglist3)):
        legtitle = leglist3[k]
        Pvartitle = Pvarlist[k]
        
        javaitems3 += f"""
            var {leglist3[k]} = document.getElementById('{Pvarlist[k]}');"""
        
        javachunks3 += f"""
        allInputs[{k}].addEventListener('click', function(){{
            status=allInputs[{k}].checked;
            if(status == 'false'){{
                obj3[{k}].style.zIndex = '0';
                obj3[{k}].style.display = 'none';
                }};
            if(status == 'true'){{
                obj3[{k}].style.display = 'block';
                obj3[{k}].style.zIndex = 1002;
                obj3.forEach((b) => {{if(b != obj3[{k}]){{b.style.zIndex = '1000'}}}});
            }};
        }});
        """
        javaclicks3 += f"""allInputs[{k}].click();"""
        
    toggle_js3 = f"""$(document).ready(function(){{
    var allDiv = document.querySelectorAll('div[class="leaflet-control-attribution leaflet-control"]');
    allDiv[0].style.display = 'none';
    var allInputs = document.querySelectorAll('input[type="checkbox"]');
    {javaitems3}
    const obj3 = {str(leglist3).replace("'","")};
    {javachunks3}
    {javaclicks3}
    }});
    """
    m3.get_root().script.add_child(Element(toggle_js3))
    
    m3.to_streamlit()
    
################################################################################################################
################################################################################################################
###############################################################################################     TAB 4
################################################################################################################
################################################################################################################
with tab4:
    st.header("Health")
    m4 = leafmap.Map(center=[-73.88, 40.88], 
                     zoom=12,
                     tiles='CartoDB positron-nolabels',
                     fullscreen_control=False,
                     height='800px',
                     min_zoom=12,
                     max_zoom=30)

    # Create an empty dictionary to store your data
    varlist4 = ['CvNID','CvNID_Hrg','CvNID_Vsn','CvNID_Cog','CvNID_Amb','CvNID_SCr','CvNID_ILD','CvNIU18D','CU18DHrg','CU18DVsn',
                'CU18DCog','CU18DAmb','CU18DSCr','CNI18t64D','C1864DHrg','C1864DVsn','C1864DCog','C1864DAmb','C1864DSCr','C1864DILD',
                'CvNI65plD','C65plDHrg','C65plDVsn','C65plDCog','C65plDAmb','C65plDSCr','C65plDILD']
    vardesc4 = ['With disability','With hearing difficulty','With vision difficulty','With cognitive difficulty',
                'With an ambulatory difficulty','With a self-care difficulty','With an independent living difficulty',
                'Under 18 yrs, with disability','Under 18 yrs, with hearing difficulty','Under 18 yrs, with vision difficulty',
                'Under 18 yrs, with cognitive difficulty','Under 18 yrs, with ambulatory difficulty',
                'Under 18 yrs, with self-care difficulty','18 to 64 yrs, with disability','18 to 64 yrs, with hearing difficulty',
                '18 to 64 yrs, with vision difficulty','18 to 64 yrs, with cognitive difficulty',
                '18 to 64 yrs, with ambulatory difficulty','18 to 64 yrs, with self-care difficulty',
                '18 to 64 yrs, with independent living difficulty','65 yrs and over, with disability',
                '65 yrs and over, with hearing difficulty','65 yrs and over, with vision difficulty',
                '65 yrs and over, with cognitive difficulty','65 yrs and over, with ambulatory difficulty',
                '65 yrs and over, with self-care difficulty','65 yrs and over, with independent living difficulty']
    leglist4 = []
    Pvarlist = []
    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # Use a for loop to populate the dictionary
    for i in range(len(varlist4)):
        legname = f"SO{i}legend"
        leglist4.append(legname)
        legmin = f"SO{i}min_val"
        legmax = f"SO{i}max_val"
        legnum_bins = f"SO{i}num_bins"
        legbins = f"SO{i}bins"
        legcontinuous_cmap = f"SO{i}continuous_cmap"
        legstep_colors = f"SO{i}step_colors"
        leg_items = f"SO{i}legend_items"
        leglabel = f"SO{i}label"
        legcolor = f"SO{i}color"
        leghtml4 = f"SO{i}legend_html"
        varname = varlist4[i]
        vardesc = vardesc4[i]
        vardescUR = vardesc4[i].replace(" ","_")
        Evarname = varname + 'E'
        Pvarname = varname + 'P'
        Pvarlist.append(Pvarname)
        POPvardesc = 'Population ' + vardesc
        PCTvardesc = 'Pct ' + vardesc
        POPvardescUR = 'Population_' + vardescUR
        PCTvardescUR = 'Pct_' + vardescUR
        
        geo_soc[POPvardescUR] = geo_soc[Evarname].fillna(0).apply(lambda x: f"{x:,}")
        geo_soc[PCTvardescUR] = geo_soc[Pvarname].fillna(0).apply(lambda x: f"{x:.1f}%")
        
        m4.add_data(geo_soc,
                    column=Pvarname,
                    layer_name=PCTvardesc,
                    cmap='viridis',
                    add_legend=False,
                    scheme='EqualInterval',
                    legend_kwds={'fmt': '{:.1f}',
                                 'interval': False},
                    fields=['Neighborhood',POPvardescUR,PCTvardescUR])
        legmin = geo_soc[Pvarname].min(skipna=True)
        legmax = geo_soc[Pvarname].max(skipna=True)
        legnum_bins = 5
        legbins = np.linspace(legmin, legmax, legnum_bins + 1)  # Equal intervals
        legbins = [round(b, 1) for b in legbins]  # Round for display
        legcontinuous_cmap = cm.linear.viridis.scale(legmin, legmax)
        legstep_colors = [legcontinuous_cmap(x) for x in np.linspace(legmin, legmax, legnum_bins)]
        leg_items4 = ""
        for n in range(legnum_bins):
            leglabel = f"{legbins[n]}%-{legbins[n+1]}%"
            legcolor = legstep_colors[n]
            leg_items4 += f"""
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{legcolor}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{leglabel}</span>
            </div>
            """
            # Custom HTML/CSS Viridis legend (self-contained)
        leghtml4 = f"""
        <div id="{Pvarname}" style="position:fixed; bottom:50px; left:5px; width:180px; height:auto; background-color: white; 
        border:2px solid grey; z-index:1000; font-size:14px; padding:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <b>{PCTvardesc}</b><br>{leg_items4}</div>"""
        # Add the custom legend to the map
        m4.get_root().html.add_child(Element(leghtml4))
    javaitems4 = ""
    javachunks4 = ""
    javaclicks4 = ""
    for k in range(len(leglist4)):
        legtitle = leglist4[k]
        Pvartitle = Pvarlist[k]
        
        javaitems4 += f"""
            var {leglist4[k]} = document.getElementById('{Pvarlist[k]}');"""
        
        javachunks4 += f"""
        allInputs[{k}].addEventListener('click', function(){{
            status=allInputs[{k}].checked;
            if(status == 'false'){{
                obj4[{k}].style.zIndex = '0';
                obj4[{k}].style.display = 'none';
                }};
            if(status == 'true'){{
                obj4[{k}].style.display = 'block';
                obj4[{k}].style.zIndex = '1002';
                obj4.forEach((b) => {{if(b != obj4[{k}]){{b.style.zIndex = '1000'}}}});
            }};
        }});
        """
        javaclicks4 += f"""allInputs[{k}].click();"""
        
    toggle_js4 = f"""$(document).ready(function(){{
    var allDiv = document.querySelectorAll('div[class="leaflet-control-attribution leaflet-control"]');

    allDiv[0].style.display = 'none';
    var allInputs = document.querySelectorAll('input[type="checkbox"]');

    {javaitems4}
    const obj4 = {str(leglist4).replace("'","")};

    {javachunks4}
    {javaclicks4}
    }});
    """
    m4.get_root().script.add_child(Element(toggle_js4))
    
    m4.to_streamlit()

################################################################################################################
################################################################################################################
###############################################################################################     TAB 5
################################################################################################################
################################################################################################################
with tab5:
    st.header("Detail")
    m5 = leafmap.Map(center=[-73.88, 40.88], 
                     zoom=12,
                     tiles='CartoDB positron-nolabels',
                     fullscreen_control=False,
                     height='800px',
                     min_zoom=12,
                     max_zoom=30)

    # Create an empty dictionary to store your data
    varlist5 = ['Eur','WEur','EEur','Russia','Asia','EAsia','China','ChNoHKTwn','SCAsia','India','SEAsia','WAsia','Yemen','Afr','EAfr',
                'MAfr','NAfr','WAfr','Ghana','Senegal','OWAfr','Oceania','Carib','DomRep','Jamaica','CAm','Guatmala','Honduras','Mexico',
                'Panama','SAm','Colombia','Guyana','Canada']
    vardesc5 = ['Europe','Western Europe','Eastern Europe','Russia','Asia','Eastern Asia','China','China, excluding Hong Kong and Taiwan',
                'South Central Asia','India','South Eastern Asia','Western Asia','Yemen','Africa','Eastern Africa','Middle Africa',
                'Northern Africa','Western Africa','Ghana','Senegal','Other Western Africa','Oceania','Caribbean','Dominican Republic',
                'Jamaica','Central America','Guatemala','Honduras','Mexico','Panama','South America','Colombia','Guyana','Canada']
    leglist5 = []
    Pvarlist = []
    
    geo_soc['Neighborhood'] = geo_soc['ntaname']
    # Use a for loop to populate the dictionary
    for i in range(len(varlist5)):
        legname = f"ED{i}legend"
        leglist5.append(legname)
        legmin = f"ED{i}min_val"
        legmax = f"ED{i}max_val"
        legnum_bins = f"ED{i}num_bins"
        legbins = f"ED{i}bins"
        legcontinuous_cmap = f"ED{i}continuous_cmap"
        legstep_colors = f"ED{i}step_colors"
        leg_items = f"ED{i}legend_items"
        leglabel = f"ED{i}label"
        legcolor = f"ED{i}color"
        leghtml5 = f"ED{i}legend_html"
        varname = varlist5[i]
        vardesc = vardesc5[i]
        vardescUR = vardesc5[i].replace(" ","_")
        Evarname = varname + 'E'
        Pvarname = varname + 'P'
        Pvarlist.append(Pvarname)
        POPvardesc = 'Population ' + vardesc
        PCTvardesc = 'Pct ' + vardesc
        POPvardescUR = 'Population_' + vardescUR
        PCTvardescUR = 'Pct_' + vardescUR
        
        geo_soc[POPvardescUR] = geo_soc[Evarname].fillna(0).apply(lambda x: f"{x:,}")
        geo_soc[PCTvardescUR] = geo_soc[Pvarname].fillna(0).apply(lambda x: f"{x:.1f}%")
        
        m5.add_data(geo_soc,
                    column=Pvarname,
                    layer_name=PCTvardesc,
                    cmap='viridis',
                    add_legend=False,
                    scheme='EqualInterval',
                    legend_kwds={'fmt': '{:.1f}',
                                 'interval': False},
                    fields=['Neighborhood',POPvardescUR,PCTvardescUR])
        legmin = geo_soc[Pvarname].min(skipna=True)
        legmax = geo_soc[Pvarname].max(skipna=True)
        legnum_bins = 5
        legbins = np.linspace(legmin, legmax, legnum_bins + 1)  # Equal intervals
        legbins = [round(b, 1) for b in legbins]  # Round for display
        legcontinuous_cmap = cm.linear.viridis.scale(legmin, legmax)
        legstep_colors = [legcontinuous_cmap(x) for x in np.linspace(legmin, legmax, legnum_bins)]
        leg_items5 = ""
        for n in range(legnum_bins):
            leglabel = f"{legbins[n]}%-{legbins[n+1]}%"
            legcolor = legstep_colors[n]
            leg_items5 += f"""
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{legcolor}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{leglabel}</span>
            </div>
            """
            # Custom HTML/CSS Viridis legend (self-contained)
        leghtml5 = f"""
        <div id="{Pvarname}" style="position:fixed; bottom:50px; left:5px; width:180px; height:auto; background-color: white; 
        border:2px solid grey; z-index:1000; font-size:14px; padding:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <b>{PCTvardesc}</b><br>{leg_items5}</div>"""
        # Add the custom legend to the map
        m5.get_root().html.add_child(Element(leghtml5))
    javaitems5 = ""
    javachunks5 = ""
    javaclicks5 = ""
    for k in range(len(leglist5)):
        legtitle = leglist5[k]
        Pvartitle = Pvarlist[k]
        
        javaitems5 += f"""
            var {leglist5[k]} = document.getElementById('{Pvarlist[k]}');"""
        
        javachunks5 += f"""
        allInputs[{k}].addEventListener('click', function(){{
            status=allInputs[{k}].checked;
            if(status == 'false'){{
                obj5[{k}].style.zIndex = '0';
                obj5[{k}].style.display = 'none';
                }};
            if(status == 'true'){{
                obj5[{k}].style.display = 'block';
                obj5[{k}].style.zIndex = '1002';
                obj5.forEach((b) => {{if(b != obj5[{k}]){{b.style.zIndex = '1000'}}}});
            }};
        }});
        """
        javaclicks5 += f"""allInputs[{k}].click();"""
    toggle_js5 = f"""$(document).ready(function(){{
    var allDiv = document.querySelectorAll('div[class="leaflet-control-attribution leaflet-control"]');

    allDiv[0].style.display = 'none';
    var allInputs = document.querySelectorAll('input[type="checkbox"]');

    {javaitems5}
    const obj5 = {str(leglist5).replace("'","")};
    {javachunks5}
    {javaclicks5}
    }});
    """
    m5.get_root().script.add_child(Element(toggle_js5))
    
    m5.to_streamlit()

################################################################################################################
################################################################################################################
###############################################################################################     TAB 6
################################################################################################################
################################################################################################################
with tab6:
    st.header("Economic")
    m6 = leafmap.Map(center=[-73.88, 40.88], 
                     zoom=12,
                     tiles='CartoDB positron-nolabels',
                     fullscreen_control=False,
                     height='800px',
                     min_zoom=12,
                     max_zoom=30)

    # Create an empty dictionary to store your data
    varlist6 = ['HHIU10','HHI10t14','HHI15t24','HHI25t34','HHI35t49','HHI50t74','HHI75t99','HI100t149','HI150t199',
                'HHI200pl','PvHIns','PbHIns','NHIns','PBwPv','CvEm16pl1','CvLFUEm2','F16plCLFE','CW_PbTrns','MgBSciArt',
                'Srvc','SalesOff','NRCnstMnt','PrdTrnsMM']
    vardesc6 = ['Income less than 10K','Income 10-14K','Income 15-24K','Income 25-34K','Income 35-49K','Income 50-74K','Income 75-99K',
                'Income 100-149K','Income 150-199K','Income 200K and more','Private insurance','Public insurance',
                'No insurance','Below poverty','Employed',
                'Unemployed','Females employed','Public trans to work','Mgmt, business, science, arts','Service industry',
                'Sales, office work','Construction, maintenance','Production, transportation, moving']
    leglist6 = []
    Pvarlist = []
    geo_eco['Neighborhood'] = geo_eco['ntaname']
    # Use a for loop to populate the dictionary
    for i in range(len(varlist6)):
        legname = f"E{i}legend"
        leglist6.append(legname)
        legmin = f"E{i}min_val"
        legmax = f"E{i}max_val"
        legnum_bins = f"E{i}num_bins"
        legbins = f"E{i}bins"
        legcontinuous_cmap = f"E{i}continuous_cmap"
        legstep_colors = f"E{i}step_colors"
        leg_items = f"E{i}legend_items"
        leglabel = f"E{i}label"
        legcolor = f"E{i}color"
        leghtml6 = f"E{i}legend_html"
        varname = varlist6[i]
        vardesc = vardesc6[i]
        vardescUR = vardesc6[i].replace(" ","_")
        Evarname = varname + 'E'
        Pvarname = varname + 'P'
        Pvarlist.append(Pvarname)
        POPvardesc = 'Population ' + vardesc
        PCTvardesc = 'Pct ' + vardesc
        POPvardescUR = 'Population_' + vardescUR
        PCTvardescUR = 'Pct_' + vardescUR
        
        geo_eco[POPvardescUR] = geo_eco[Evarname].fillna(0).apply(lambda x: f"{x:,}")
        geo_eco[PCTvardescUR] = geo_eco[Pvarname].fillna(0).apply(lambda x: f"{x:.1f}%")
        
        m6.add_data(geo_eco,
                    column=Pvarname,
                    layer_name=PCTvardesc,
                    cmap='viridis',
                    add_legend=False,
                    scheme='EqualInterval',
                    legend_kwds={'fmt': '{:.1f}',
                                 'interval': False},
                    fields=['Neighborhood',POPvardescUR,PCTvardescUR])
        legmin = geo_eco[Pvarname].min(skipna=True)
        legmax = geo_eco[Pvarname].max(skipna=True)
        legnum_bins = 5
        legbins = np.linspace(legmin, legmax, legnum_bins + 1)  # Equal intervals
        legbins = [round(b, 1) for b in legbins]  # Round for display
        legcontinuous_cmap = cm.linear.viridis.scale(legmin, legmax)
        legstep_colors = [legcontinuous_cmap(x) for x in np.linspace(legmin, legmax, legnum_bins)]
        leg_items6 = ""
        for n in range(legnum_bins):
            leglabel = f"{legbins[n]}%-{legbins[n+1]}%"
            legcolor = legstep_colors[n]
            leg_items6 += f"""
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{legcolor}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{leglabel}</span>
            </div>
            """
            # Custom HTML/CSS Viridis legend (self-contained)
        leghtml6 = f"""
        <div id="{Pvarname}" style="position:fixed; bottom:50px; left:5px; width:180px; height:auto; background-color: white; 
        border:2px solid grey; z-index:1000; font-size:14px; padding:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <b>{PCTvardesc}</b><br>{leg_items6}</div>"""
        # Add the custom legend to the map
        m6.get_root().html.add_child(Element(leghtml6))
    javaitems6 = ""
    javachunks6 = ""
    javaclicks6 = ""
    for k in range(len(leglist6)):
        legtitle = leglist6[k]
        Pvartitle = Pvarlist[k]
        
        javaitems6 += f"""
            var {leglist6[k]} = document.getElementById('{Pvarlist[k]}');"""
        
        javachunks6 += f"""
        allInputs[{k}].addEventListener('click', function(){{
            status=allInputs[{k}].checked;
            if(status == 'false'){{
                obj6[{k}].style.zIndex = '0';
                obj6[{k}].style.display = 'none';
                }};
            if(status == 'true'){{
                obj6[{k}].style.display = 'block';
                obj6[{k}].style.zIndex = '1002';
                obj6.forEach((b) => {{if(b != obj6[{k}]){{b.style.zIndex = '1000'}}}});
            }};
        }});
        """
        javaclicks6 += f"""allInputs[{k}].click();"""
        
    toggle_js6 = f"""$(document).ready(function(){{
    var allDiv = document.querySelectorAll('div[class="leaflet-control-attribution leaflet-control"]');

    allDiv[0].style.display = 'none';
    var allInputs = document.querySelectorAll('input[type="checkbox"]');

    {javaitems6}
    const obj6 = {str(leglist6).replace("'","")};

    {javachunks6}
    {javaclicks6}
    }});
    """
    m6.get_root().script.add_child(Element(toggle_js6))
    
    m6.to_streamlit()
################################################################################################################
################################################################################################################
###############################################################################################     TAB 7
################################################################################################################
################################################################################################################
with tab7:
    st.header("Housing")

    m7 = leafmap.Map(center=[-73.88, 40.88], 
                     zoom=12,
                     tiles='CartoDB positron-nolabels',
                     fullscreen_control=False,
                     height='800px',
                     min_zoom=12,
                     max_zoom=30)

    # Create an empty dictionary to store your data
    varlist7 = ['OcHU1','VacHU','Blt10Ltr','Blt00t09','Blt90t99','Blt80t89','Blt70t79','Blt60t69','Blt50t59','Blt40t49','BltBf39','OOcHU1',
                'ROcHU1','Mv10Ltr','Mv00t09','Mv90t99','MvBf89','NoVhclAv','Vhcl1Av','Vhcl2Av','Vhcl3plAv','OcPR0t1','OcPR1pl','OcPR1p5pl',
                'GRU500','GR500t999','GR1kt14k','GR15kt19k','GR20kt24k','GR25kt29k','GR3kpl','GRPIU15','GRPI15t19','GRPI20t24',
                'GRPI25t29','GRPI30pl','GRPI50pl']
    vardesc7 = ['Occupied housing units','Vacant housing units','Built 2010 or later','Built 2000 to 2009','Built 1990 to 1999',
                'Built 1980 to 1989','Built 1970 to 1979','Built 1960 to 1969','Built 1950 to 1959','Built 1940 to 1949',
                'Built 1939 or earlier','Owner-occupied','Renter-occupied','Moved in 2010 or later','Moved in 2000 to 2009',
                'Moved in 1990 to 1999','Moved in 1989 or earlier','No vehicles available','1 vehicle available','2 vehicles available',
                '3 or more vehicles available','Occupants per room, 1.00 or less','Occupants per room, 1.01 or more',
                'Occupants per room, 1.51 or more','Gross rent, Less than $500','Gross rent, $500 to $999','Gross rent, $1,000 to $1499',
                'Gross rent, $1,500 to $1,999','Gross rent, $2,000 to $2,499','Gross rent, $2,500 to $2,999','Gross rent, $3,000 or more',
                'Rent as % of HH income, Less than 15.0%','Rent as % of HH income, 15.0 to 19.9%',
                'Rent as % of HH income, 20.0 to 24.9%','Rent as % of HH income, 25.0 to 29.9%',
                'Rent as % of HH income, 30.0% or more','Rent as % of HH income, 50.0% or more']
    
    leglist7 = []
    Pvarlist = []
    geo_hou['Neighborhood'] = geo_hou['ntaname']
    # Use a for loop to populate the dictionary
    for i in range(len(varlist7)):
        legname = f"H{i}legend"
        leglist7.append(legname)
        legmin = f"H{i}min_val"
        legmax = f"H{i}max_val"
        legnum_bins = f"H{i}num_bins"
        legbins = f"H{i}bins"
        legcontinuous_cmap = f"H{i}continuous_cmap"
        legstep_colors = f"H{i}step_colors"
        leg_items = f"H{i}legend_items"
        leglabel = f"H{i}label"
        legcolor = f"H{i}color"
        leghtml7 = f"H{i}legend_html"
        varname = varlist7[i]
        vardesc = vardesc7[i]
        vardescUR = vardesc7[i].replace(" ","_")
        Evarname = varname + 'E'
        Pvarname = varname + 'P'
        Pvarlist.append(Pvarname)
        POPvardesc = 'Population ' + vardesc
        PCTvardesc = 'Pct ' + vardesc
        POPvardescUR = 'Population_' + vardescUR
        PCTvardescUR = 'Pct_' + vardescUR
        
        geo_hou[POPvardescUR] = geo_hou[Evarname].fillna(0).apply(lambda x: f"{x:,}")
        geo_hou[PCTvardescUR] = geo_hou[Pvarname].fillna(0).apply(lambda x: f"{x:.1f}%")
        
        m7.add_data(geo_hou,
                    column=Pvarname,
                    layer_name=PCTvardesc,
                    cmap='viridis',
                    add_legend=False,
                    scheme='EqualInterval',
                    legend_kwds={'fmt': '{:.1f}',
                                 'interval': False},
                    fields=['Neighborhood',POPvardescUR,PCTvardescUR])
        legmin = geo_hou[Pvarname].min(skipna=True)
        legmax = geo_hou[Pvarname].max(skipna=True)
        legnum_bins = 5
        legbins = np.linspace(legmin, legmax, legnum_bins + 1)  # Equal intervals
        legbins = [round(b, 1) for b in legbins]  # Round for display
        legcontinuous_cmap = cm.linear.viridis.scale(legmin, legmax)
        legstep_colors = [legcontinuous_cmap(x) for x in np.linspace(legmin, legmax, legnum_bins)]
        leg_items7 = ""
        for n in range(legnum_bins):
            leglabel = f"{legbins[n]}%-{legbins[n+1]}%"
            legcolor = legstep_colors[n]
            leg_items7 += f"""
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="width: 18px; height: 18px; background:{legcolor}; border:1px solid #000;"></div>
            <span style="margin-left: 6px;">{leglabel}</span>
            </div>
            """
            # Custom HTML/CSS Viridis legend (self-contained)
        leghtml7 = f"""
        <div id="{Pvarname}" style="position:fixed; bottom:50px; left:5px; width:180px; height:auto; background-color: white; 
        border:2px solid grey; z-index:1000; font-size:14px; padding:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <b>{PCTvardesc}</b><br>{leg_items7}</div>"""
        # Add the custom legend to the map
        m7.get_root().html.add_child(Element(leghtml7))
    javaitems7 = ""
    javachunks7 = ""
    javaclicks7 = ""
    for k in range(len(leglist7)):
        legtitle = leglist7[k]
        Pvartitle = Pvarlist[k]
        
        javaitems7 += f"""
            var {leglist7[k]} = document.getElementById('{Pvarlist[k]}');"""
        
        javachunks7 += f"""
        allInputs[{k}].addEventListener('click', function(){{
            status=allInputs[{k}].checked;
            if(status == 'false'){{
                obj7[{k}].style.zIndex = '0';
                obj7[{k}].style.display = 'none';
                }};
            if(status == 'true'){{
                obj7[{k}].style.display = 'block';
                obj7[{k}].style.zIndex = '1002';
                obj7.forEach((b) => {{if(b != obj7[{k}]){{b.style.zIndex = '1000'}}}});
            }};
        }});
        """
        javaclicks7 += f"""allInputs[{k}].click();"""
        
    toggle_js7 = f"""$(document).ready(function(){{
    var allDiv = document.querySelectorAll('div[class="leaflet-control-attribution leaflet-control"]');

    allDiv[0].style.display = 'none';
    var allInputs = document.querySelectorAll('input[type="checkbox"]');

    {javaitems7}
    const obj7 = {str(leglist7).replace("'","")};

    {javachunks7}
    {javaclicks7}
    }});
    """
    m7.get_root().script.add_child(Element(toggle_js7))

    m7.to_streamlit()
