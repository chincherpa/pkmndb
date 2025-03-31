import pandas as pd

import config as c


def load_more():
  st.session_state.num_images += 20

# Load data function (unchanged)
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

search_term = 'ferm'
mask = df['Name DE'].str.contains(search_term, case=False, na=False) | \
  df['Name'].str.contains(search_term, case=False, na=False)

df = df[mask]

print(df.Name)
print(df.shape)
