import streamlit as st
import pandas as pd
import pickle
import os

st.set_page_config(page_title='pkmndb', page_icon='🐲', layout="wide")

# Existing initializations
if 'num_images' not in st.session_state:
    st.session_state.num_images = 20

# Modified initialization for selected cards
if 'selected_cards' not in st.session_state:
    st.session_state.selected_cards = {}

# Function to load more images
def load_more():
    st.session_state.num_images += 20

# Load data function (unchanged)
@st.cache_data
def load_data():
    df = pd.read_csv('pokemon_karten.csv', sep=';', encoding='utf-8')
    df['KP'] = pd.to_numeric(df['KP'], errors='coerce')
    numeric_columns = ['KP', 'Angriff 1 Schaden', 'Angriff 2 Schaden']
    df[numeric_columns] = df[numeric_columns].fillna(0)
    object_columns = df.select_dtypes(include=['object']).columns
    df[object_columns] = df[object_columns].astype(str)
    return df

# Modified function for saving selections
def save_selection():
    selection_name = st.session_state.selection_name
    if selection_name and st.session_state.selected_cards:
        with open(f"{selection_name}.pkl", "wb") as f:
            pickle.dump(st.session_state.selected_cards, f)
        st.success(f"Selection '{selection_name}' saved successfully!")
    else:
        st.error("Please enter a name for your selection and select at least one card.")

def load_saved_selections():
    saved_selections = [f for f in os.listdir() if f.endswith('.pkl')]
    return [os.path.splitext(f)[0] for f in saved_selections]

# New function to update card quantity
def update_card_quantity(card_name, quantity):
    if quantity > 0:
        st.session_state.selected_cards[card_name] = quantity
    elif card_name in st.session_state.selected_cards:
        del st.session_state.selected_cards[card_name]

# Load data
df_orig = load_data()
df = df_orig

# Create tabs
tab1, tab2 = st.tabs(["Kartenauswahl", "Gespeicherte Auswahlen"])

with tab1:
  # Existing search functionality
  col_search, _ = st.columns([2,3])
  search_term = col_search.text_input('Suche nach Namen oder Angriffen:')
  if search_term:
    mask = df['Name'].str.contains(search_term, case=False, na=False) | \
      df['Name EN'].str.contains(search_term, case=False, na=False) | \
      df['Angriff 1 Name'].str.contains(search_term, case=False, na=False) | \
      df['Angriff 1 Name EN'].str.contains(search_term, case=False, na=False) | \
      df['Angriff 2 Name'].str.contains(search_term, case=False, na=False) | \
      df['Angriff 2 Name EN'].str.contains(search_term, case=False, na=False)
    df = df[mask]

  # Filter
  col1, col2, col3 = st.columns(3)

  with col1:
    kartentyp_options = ['Alle'] + sorted(df['Kartentyp'].unique().tolist())
    kartentyp = st.selectbox('Kartentyp', kartentyp_options)
    # print(f'{kartentyp = }')
    angriff1_kosten_options = sorted(df['Angriff 1 Kosten'].unique().tolist())  # ['Alle'] + 
    angriff1_kosten = st.multiselect('Angriff 1 Kosten', angriff1_kosten_options)
    # print(f'{angriff1_kosten = }')
    angriff1_schaden_options = sorted(df['Angriff 1 Schaden'].unique().tolist())  # ['Alle'] + 
    angriff1_schaden = st.multiselect('Angriff 1 Schaden', angriff1_schaden_options)
    # print(f'{angriff1_schaden = }')

  with col2:
    typ_options = ['Alle'] + sorted(df['Typ'].unique().tolist())
    typ = st.selectbox('Typ', typ_options)
    # print(f'{typ = }')
    angriff2_kosten_options = sorted(df['Angriff 2 Kosten'].unique().tolist())  # ['Alle'] + 
    angriff2_kosten = st.multiselect('Angriff 2 Kosten', angriff2_kosten_options)
    # print(f'{angriff2_kosten = }')
    angriff2_schaden_options = sorted(df['Angriff 2 Schaden'].unique().tolist())  # ['Alle'] + 
    angriff2_schaden = st.multiselect('Angriff 2 Schaden', angriff2_schaden_options)
    # print(f'{angriff2_schaden = }')

  with col3:
    kp_min = int(df['KP'].min())
    kp_max = int(df['KP'].max()
    iStep = 10
    if kp_min == kp_max:
      kp_max += iStep
    kp_range = st.slider('KP', kp_min, kp_max, (kp_min, kp_max), step=iStep)
    # print(f'{kp_range = }')
    set_filter = st.multiselect('Set', sorted(df['Set'].unique()))
    # print(f'{set_filter = }')
    regulation = st.multiselect('Regulation', df['Regulation'].unique())
    # print(f'{regulation = }')

  # Anwenden der Filter
  if kartentyp != 'Alle':
    df = df[df['Kartentyp'] == kartentyp]
  if typ != 'Alle':
    df = df[df['Typ'] == typ]
  df = df[(df['KP'] >= kp_range[0]) & (df['KP'] <= kp_range[1])]
  if angriff1_kosten:
    # df = df[df['Angriff 1 Kosten'] == angriff1_kosten]
    df = df[df['Angriff 1 Kosten'].isin(angriff1_kosten)]
  if angriff1_schaden:
    # df = df[df['Angriff 1 Schaden'] == float(angriff1_schaden)]
    df = df[df['Angriff 1 Schaden'].isin(angriff1_schaden)]
  if angriff2_kosten:
    # df = df[df['Angriff 2 Kosten'] == angriff2_kosten]
    df = df[df['Angriff 2 Kosten'].isin(angriff2_kosten)]
  if angriff2_schaden:
    # df = df[df['Angriff 2 Schaden'] == float(angriff2_schaden)]
    df = df[df['Angriff 1 Schaden'].isin(angriff2_schaden)]
  if set_filter:
    df = df[df['Set'].isin(set_filter)]
  if regulation:
    df = df[df['Regulation'].isin(regulation)]

  st.metric('Karten', len(df))
  col, _ = st.columns([2,3])
  search_term_cap = col.text_input('Suche in Fähigkeit:')
  if search_term_cap:
    mask = df['Fähigkeit'].str.contains(search_term_cap, case=False, na=False) | \
      df['Fähigkeit Text'].str.contains(search_term_cap, case=False, na=False)
    df = df[mask]

    col2, _ = st.columns([2,3])
    search_term_cap_2 = col2.text_input('Suche in Fähigkeit 2:')
    if search_term_cap_2:
      mask = df['Fähigkeit'].str.contains(search_term_cap_2, case=False, na=False) | \
        df['Fähigkeit Text'].str.contains(search_term_cap_2, case=False, na=False)
      df = df[mask]

  st.dataframe(df)

  if not df.empty:
    on = st.checkbox("zeige Karten")
    if on:
      st.write(f"Anzeigen von {min(st.session_state.num_images, len(df))} Karten:")
      cols = st.columns(4)
      for i in range(min(st.session_state.num_images, len(df))):
        card = df.iloc[i]
        with cols[i % 4]:
          quantity = st.number_input(f"{card['Name']} '{card['Name EN']}' {card['Set']} {card['#']}", min_value=0, value=st.session_state.selected_cards.get(f"{card['Name']} {card['Set']} {card['#']}", 0), key=f"quantity_{i}", max_value=4)
          st.image(card['URL'], width=400)
          update_card_quantity(f"{card['Name']}|{card['Set']}|{card['#']}", quantity)

      if st.session_state.num_images < len(df):
        if st.button('Mehr laden'):
          load_more()
        st.write(f"Angezeigt: {min(st.session_state.num_images, len(df))} von {len(df)} Karten")

    # Save selection
    st.subheader("Auswahl speichern")
    col_save, _ = st.columns([2,3])
    col_save.text_input("Geben Sie einen Namen für Ihre Auswahl ein:", key="selection_name")
    st.button("Auswahl speichern", on_click=save_selection)

    # Display current selection
    st.subheader("Aktuelle Auswahl")
    for card, quantity in st.session_state.selected_cards.items():
      st.write(f"{card}: {quantity}")
    st.write('ende')

  else:
    st.write('Keine Karten gefunden, die den Filterkriterien entsprechen.')

with tab2:
  st.header("Gespeicherte Auswahlen anzeigen")
  saved_selections = load_saved_selections()
  col_saved, _ = st.columns([2,3])
  selected_save = col_saved.selectbox("Wählen Sie eine gespeicherte Auswahl:", saved_selections)
  print(f'\n{"#"*10}\n{"#"*10} {selected_save = }\n{"#"*10}\n')

  if selected_save:
    with open(f"{selected_save}.pkl", "rb") as f:
      loaded_selection = pickle.load(f)
    st.write(f"Karten in '{selected_save}':")
    for card, quantity in loaded_selection.items():
      st.write(f"{card}: {quantity}")

    # Display the selected cards
    cols = st.columns(4)
    for i, (card_id, quantity) in enumerate(loaded_selection.items()):
      print(f'{card_id = }')
      card_name, card_set, card_num = card_id.split('|')
      mask = df_orig['Name'].str.contains(card_name, case=False, na=False) & \
        df_orig['Set'].str.contains(card_set, case=False, na=False) & \
        df_orig['#'].str.contains(card_num, case=False, na=False)

      card = df_orig[mask].iloc[0]
      with cols[i % 4]:
        st.write(f"{card['Name']} '{card['Name EN']}' {card['Set']} {card['#']}")
        st.write(f"Anzahl: {quantity}")
        st.image(card['URL'], width=300)