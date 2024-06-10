import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Material Waste Management Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

.button {
    display: inline-block;
    padding: 10px 20px;
    font-size: 20px;
    cursor: pointer;
    text-align: center;
    text-decoration: none;
    outline: none;
    color: #fff;
    background-color: #4CAF50;
    border: none;
    border-radius: 15px;
    margin: 10px 0;
}

.button:hover {background-color: #3e8e41}

.button:active {
    background-color: #3e8e41;
    box-shadow: 0 5px #666;
    transform: translateY(4px);
}

</style>
""", unsafe_allow_html=True)

# Load data
data_path = 'MaterialsForABusinessGroup_array.json'
geojson_path = 'california-counties.geojson'

# Read data
with open(data_path, 'r') as f:
    data = json.load(f)

# Convert data to DataFrame
df = pd.DataFrame(data)

# Sidebar
with st.sidebar:
    st.title("Material Waste Management Dashboard")
    material_category = st.selectbox("Select Material Category", df['Material Category'].unique())
    
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)
    
    st.markdown("""
    <a href="https://public.tableau.com/app/profile/saish.shinde6411/viz/Group9-Project/Dashboard1?publish=yes" target="_blank">
        <div class="button">Organic Time Series Dashboard</div>
    </a>
    """, unsafe_allow_html=True)

    st.markdown("""
    <a href="https://public.tableau.com/app/profile/saish.shinde6411/viz/Recycle-Dashboard/Dashboard1?publish=yes" target="_blank">
        <div class="button">Recycle Time Series Dashboard</div>
    </a>
    """, unsafe_allow_html=True)

# Filter data based on selected material category
filtered_data = df[df['Material Category'] == material_category]

# Calculate facts
total_disposal = filtered_data['Material Tons Disposed'].sum() / 1000000
total_recycle = filtered_data['Material Tons in Curbside Recycle'].sum() / 1000000
total_organics = filtered_data['Material Tons in Curbside Organics'].sum() / 1000000
total_diversion = filtered_data['Material Tons in Other Diversion'].sum() / 1000000

# Map, Bar Chart, and Data Facts
data_fact_col, map_col, chart_col = st.columns([1, 3, 2])

# Data Facts
with data_fact_col:
    st.subheader("Data Facts (tons)")
    st.metric("Total Disposal", f"{total_disposal:.2f} M")
    st.metric("Total Curbside Recycle", f"{total_recycle:.2f} M")
    st.metric("Total Curbside Organics", f"{total_organics:.2f} M")
    st.metric("Total Other Diversion", f"{total_diversion:.2f} M")

with map_col:
    st.subheader(f'Total Disposal of each County for {material_category}')
    
    # Prepare data for choropleth map
    geojson = json.load(open(geojson_path))
    for feature in geojson['features']:
        feature['id'] = feature['properties']['name']

    # Ensure we have the correct disposal values for each county
    county_disposal = filtered_data.groupby('Jurisdiction(s)')['Material Tons Disposed'].sum().reset_index()
    county_disposal.columns = ['name', 'Material Tons Disposed']
    
    # Merge geojson with the county disposal data
    for feature in geojson['features']:
        county_name = feature['properties']['name']
        if county_name in county_disposal['name'].values:
            feature['properties']['Material Tons Disposed'] = county_disposal[county_disposal['name'] == county_name]['Material Tons Disposed'].values[0]
        else:
            feature['properties']['Material Tons Disposed'] = 0

    # Create a Plotly Express choropleth map
    fig_map = px.choropleth(
        county_disposal,
        geojson=geojson,
        locations='name',
        featureidkey="properties.name",
        color='Material Tons Disposed',
        color_continuous_scale=selected_color_theme,
        labels={'Material Tons Disposed': 'Tons Disposed'},
        title='Total Disposal of each County'
    )
    fig_map.update_geos(
        fitbounds="locations",
        visible=False,
        center={"lat": 37.7749, "lon": -122.4194},  # Centered around California
        projection_scale=5  # Adjust this parameter to zoom in or out
    )
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        height=500,
        geo_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_map, use_container_width=True)

with chart_col:
    st.subheader(f'Material Tons Disposed for {material_category}')
    material_types = filtered_data.groupby('Material Type').sum()[['Material Tons Disposed', 'Material Tons in Curbside Recycle', 'Material Tons in Curbside Organics', 'Material Tons in Other Diversion']].reset_index()
    fig = px.bar(material_types, x='Material Type', y=['Material Tons Disposed', 'Material Tons in Curbside Recycle', 'Material Tons in Curbside Organics', 'Material Tons in Other Diversion'],
                 labels={'value':'Tons', 'variable':'Category'}, barmode='stack', color_discrete_map={
                     'Material Tons Disposed': '#EF553B',  # Muted red
                     'Material Tons in Curbside Recycle': '#636EFA',  # Muted blue
                     'Material Tons in Curbside Organics': '#00CC96',  # Muted green
                     'Material Tons in Other Diversion': '#AB63FA'  # Muted purple
                 })
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=50, b=0), height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# Overall analysis charts
st.markdown("# Overall Analysis of California")
# overall_col1, overall_col2 = st.columns(2)
overall_col1, overall_col2, overall_col3 = st.columns((2, 3, 2), gap='medium')

with overall_col1:
    # st.subheader("Proportion of Material Management")
    overall_data = df.groupby('Material Category').sum().reset_index()
    category_proportions = overall_data.copy()
    category_proportions['Disposed (%)'] = (category_proportions['Material Tons Disposed'] / category_proportions['Material Tons Generated (Sum of all Streams)']) * 100
    category_proportions['Curbside Recycle (%)'] = (category_proportions['Material Tons in Curbside Recycle'] / category_proportions['Material Tons Generated (Sum of all Streams)']) * 100
    category_proportions['Curbside Organics (%)'] = (category_proportions['Material Tons in Curbside Organics'] / category_proportions['Material Tons Generated (Sum of all Streams)']) * 100
    category_proportions['Other Diversion (%)'] = (category_proportions['Material Tons in Other Diversion'] / category_proportions['Material Tons Generated (Sum of all Streams)']) * 100
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatterpolar(
        r=category_proportions['Disposed (%)'],
        theta=category_proportions['Material Category'],
        fill='toself',
        name='Disposed (%)',
        marker=dict(color='#EF553B')  # Muted red
    ))
    fig2.add_trace(go.Scatterpolar(
        r=category_proportions['Curbside Recycle (%)'],
        theta=category_proportions['Material Category'],
        fill='toself',
        name='Curbside Recycle (%)',
        marker=dict(color='#636EFA')  # Muted blue
    ))
    fig2.add_trace(go.Scatterpolar(
        r=category_proportions['Curbside Organics (%)'],
        theta=category_proportions['Material Category'],
        fill='toself',
        name='Curbside Organics (%)',
        marker=dict(color='#00CC96')  # Muted green
    ))
    fig2.add_trace(go.Scatterpolar(
        r=category_proportions['Other Diversion (%)'],
        theta=category_proportions['Material Category'],
        fill='toself',
        name='Other Diversion (%)',
        marker=dict(color='#AB63FA')  # Muted purple
    ))

    fig2.update_layout(
        title = "Proportion of Material Management",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title_font=dict(size=20, color='white', family="Arial"),
    )

    st.plotly_chart(fig2, use_container_width=True)

with overall_col2:
    # st.subheader("Correlation Matrix")
    
    # Extract relevant fields for correlation matrix
    df_relevant = df[['Material Tons Disposed', 'Material Tons in Curbside Recycle', 'Material Tons in Curbside Organics', 'Material Tons in Other Diversion']]
    
    # Calculate the correlation matrix
    correlation_matrix = df_relevant.corr()
    
    # Create an interactive heatmap
    fig_corr = px.imshow(correlation_matrix, 
                         text_auto=True, 
                         aspect="auto", 
                         color_continuous_scale='greens'  # Changed color scale to Viridis
                         )
    fig_corr.update_layout(
        title = "Correlation Matrix",
        autosize=True, 
        margin=dict(l=20, r=20, t=100, b=0), 
        height=350,
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=20, color='white', family="Arial"),
        font=dict(size=14, color='black')
    )
    fig_corr.update_xaxes(side="bottom")

    st.plotly_chart(fig_corr, use_container_width=True)

with overall_col3:
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [CalRecycle](https://www2.calrecycle.ca.gov/WasteCharacterization/MaterialTypeStreams?bg=116).
            ''')


