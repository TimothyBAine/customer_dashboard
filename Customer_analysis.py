import streamlit as st
import pandas as pd 
import altair as alt
import numpy as np 
import pydeck as pdk 
import datetime

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Customer Analysis", page_icon=":dollar:")

pd.options.display.float_format = '{:, .2f}'.format

# Loading the data
@st.cache
def load_data(file):
    df = pd.read_csv(file, dtype={'order_id': 'str'}, parse_dates=['order_date', 'Customer Since'])
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['Customer Since'] = pd.to_datetime(df['Customer Since'])
    return df


def donut_chart (data, slider, states):
    df2 = data[(data['order_date'] <= slider[1]) & (data['order_date'] >= slider[0])]
    df2 = df2.loc[df2['State'].isin(states)]
    df_group = df2.groupby(['Region'])['total'].sum()
    df_grouped = df_group.reset_index()
    df_grouped['percentage'] = df_grouped['total']/df_grouped['total'].sum()
    df_grouped.loc[:, "Percentage"] = df_grouped["percentage"].map('{:,.2%}'.format)
    chart=alt.Chart(df_grouped).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="percentage", type="quantitative"),
        color=alt.Color(field="Region", type="nominal"),
        tooltip=('Region','Percentage')
        ).properties(width=400,height=250)
    return chart

def line_graph(data, slider, states):
    df2 = data[(data['order_date'] <= slider[1]) & (data['order_date'] >= slider[0])]
    df2 = df2.loc[df2['State'].isin(states)]
    df1 = pd.DataFrame(list(zip(df2['month'], df2['total'])), columns=['Month', 'revenue'])
    df_group = df1.groupby(['Month'])['revenue'].sum()
    df_group = df_group.reset_index()
    df_grouped = df_group.reindex([10,9,2,4,3,7,0,8,6,5,1,11])
    df_grouped.loc[:, "Revenue"] = '$'+df_grouped["revenue"].map('{:,.2f}'.format)
    chart = alt.Chart(df_grouped).mark_area(
        line={'color':'darkgreen'},
        color=alt.Gradient(gradient='linear',stops=[alt.GradientStop(color='white', offset=0),
        alt.GradientStop(color='darkgreen', offset=1)],
        x1=1,x2=1,y1=1,y2=0)
        ).encode(
            alt.X('Month:O'),
            alt.Y('revenue:Q'),
            tooltip=('Month', 'Revenue')
            ).properties(width=400,height=250)
    return chart


def butterfly_graph(data, slider, states):
    df2 = data[(data['order_date'] <= slider[1]) & (data['order_date'] >= slider[0])]
    df2 = df2.loc[df2['State'].isin(states)]
    df_grouped = df2.groupby(['category', 'Gender'])['total'].sum()
    df_grouped = df_grouped.reset_index()
    df_grouped.loc[:, "Revenue"] = '$'+df_grouped["total"].map('{:,.2f}'.format)
    female = df_grouped[df_grouped['Gender']=='F']
    male = df_grouped[df_grouped['Gender']=='M']
    #color_scale = alt.Scale(domain=['Male', 'Female'],range=['#1f77b4', '#e377c2'])
    left = alt.Chart(female).encode(
            y=alt.Y('category:N', axis=None),
            x=alt.X('total:Q',
            title='Revenue',
            sort=alt.SortOrder('descending')),
            tooltip=('category', 'Revenue')
            ).mark_bar(color='firebrick').properties(title='Female').properties(width=150,height=250)

    middle = alt.Chart(df_grouped).encode(
        y=alt.Y('category:N', axis=None),
        text=alt.Text('category:N'),).mark_text().properties(width=40
        )

    right = alt.Chart(male).encode(
        y=alt.Y('category:N', axis=None),
        x=alt.X('total:Q', title='Revenue'),
        tooltip=('category', 'Revenue')
        ).mark_bar().properties(title='Male').properties(width=150,height=250)

    # alt.concat(left, middle, right, spacing=5)
    return alt.concat(left, middle, right, spacing=5)

def scatter_graph(data, slider, states):
    df2 = data[(data['order_date'] <= slider[1]) & (data['order_date'] >= slider[0])]
    df2 = df2.loc[df2['State'].isin(states)]
    df2['Customer Lifetime'] = (df2['order_date'].max()-df2['Customer Since'])/np.timedelta64(1, 'Y')
    df1 = pd.DataFrame(list(zip(df2['Customer Lifetime'], df2['Discount_Percent'], df2['total'])), columns=['Customer Lifetime', 'Discount Percentage', 'Revenue'])
    df1 = df1.round(2)
    chart = alt.Chart(df1).mark_point().encode(
        x = 'Revenue',
        y = 'Discount Percentage',
        size = 'Customer Lifetime',
    ).properties(width=400,height=250)
    return chart


def age_band(data, slider, states):
    bins = [0, 20, 30, 40, 50, 60, 70, np.inf]
    df2 = data[(data['order_date'] <= slider[1]) & (data['order_date'] >= slider[0])]
    df2 = df2.loc[df2['State'].isin(states)]
    age_groups = pd.cut(df2['age'], bins=bins)
    df = df2.groupby(age_groups)['total'].sum()
    df1 = pd.DataFrame(list(zip(['0-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70>'],df)), columns = ['age band', 'revenue'])
    df1.loc[:, "Revenue"] ='$'+df1["revenue"].map('{:,.2f}'.format)
    chart = alt.Chart(df1).mark_bar().encode(
        alt.Y('revenue', type='quantitative', title=''),
        alt.X('age band', type='nominal', title='Age Band'),
        tooltip=['age band', 'Revenue']
    ).properties(width=400,height=250)

    return chart


file = "https://raw.githubusercontent.com/TimothyBAine/customer_dashboard/main/sales_06_FY2020-21.csv"
df = load_data(file)

states = df['State'].unique()

# PAGE LAYOUT
st.title('Customer Analysis')
with st.expander('About:'):
    st.markdown("""
    * An analysis of Customer revenue in the **Greater America** region
    * The Data is gotten and duplicated from the Stanley George Joseph's [Youtube](https://youtu.be/_qReGTOrKTk)
    * Data Controls like the Year slider and State selector can be found in the sidebar to the right.
    """)

column2, padding, column3 = st.columns((10,2,10))
with st.sidebar:
    st.write("\n\n")
    year_range = st.slider(
        "Select date", 
        datetime.datetime(2020, 10,1,0,0), datetime.datetime(2021, 10,1, 0, 0), (datetime.datetime(2020, 10,1,0,0), datetime.datetime(2021, 10,1,0,0)),
        )

    container = st.container()
    all = st.checkbox(label='Select All')
    if all:
        selected_options = container.multiselect('Choose the State:', states, states)
    else:
        selected_options = st.multiselect(label='Choose the State:', options=states)

with column2:
    st.altair_chart(age_band(df, slider= year_range, states=selected_options))
    st.altair_chart(scatter_graph(df, slider= year_range, states=selected_options))
    #st.altair_chart(geo_chart(df,slider= year_range, states=selected_options))

with column3:
    st.altair_chart(donut_chart(df, slider= year_range, states=selected_options))
    st.altair_chart(line_graph(df, slider= year_range, states=selected_options))
    st.altair_chart(butterfly_graph(df, slider= year_range, states=selected_options))
