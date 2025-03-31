import streamlit as st
import pandas as pd

from st_keyup import st_keyup

import config as c

st.set_page_config(page_title='pkmndb TEST', page_icon='🐲', layout='wide')

def load_more():
  st.session_state.num_images += 20

# Load data function (unchanged)
@st.cache_data
def load_data():
  df = pd.read_csv('cards.csv', sep=';')
  df=df.fillna('')
  df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
  numeric_columns = ['HP', 'Attack 1 damage', 'Attack 2 damage']

  df[numeric_columns] = df[numeric_columns].fillna(0)
  object_columns = df.select_dtypes(include=['object']).columns
  df[object_columns] = df[object_columns].astype(str)
  return df

# Load data
df = load_data()
df = df[df['Regulation'].isin(c.lStandard_regulations)]
df = df.reset_index(drop=True)
st.dataframe(df)

search_term_att_eff = 'sch' # st_keyup('Find in effect of attack:', key='search_term_att_eff_key')
mask = df['Effect Attack 1 DE'].str.contains(search_term_att_eff, case=False, na=False) | \
  df['Effect Attack 1'].str.contains(search_term_att_eff, case=False, na=False) | \
  df['Effect Attack 2 DE'].str.contains(search_term_att_eff, case=False, na=False) | \
  df['Effect Attack 2'].str.contains(search_term_att_eff, case=False, na=False)
df = df[mask]

st.header('Result')
st.dataframe(df)
