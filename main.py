import re

import streamlit as st
import pandas as pd
import os

from st_keyup import st_keyup

from config import dConfig

st.set_page_config(page_title='pkmndb', page_icon='🐲', layout="wide")

# st.markdown("""
#   div.stButton > button:first-child {
#     background-color: #00cc00;
#     color:white;
#     font-size:20px;
#     height:3em;
#     width:30em;
#     border-radius:10px 10px 10px 10px;
#   }
# """, unsafe_allow_html=True)

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
def load_data(lang):
  df = pd.read_csv(dConfig[lang]['file'], sep=';', encoding=dConfig[lang]['encoding'])
  df[dConfig[lang]['hp']] = pd.to_numeric(df[dConfig[lang]['hp']], errors='coerce')
  numeric_columns = [dConfig[lang]['hp'], 'Attack 1 damage', 'Attack 2 damage']

  df[numeric_columns] = df[numeric_columns].fillna(0)
  object_columns = df.select_dtypes(include=['object']).columns
  df[object_columns] = df[object_columns].astype(str)
  return df

def save_selection():
    selection_name = st.session_state.selection_name
    print(f'{selection_name = }')
    if selection_name and st.session_state.selected_cards:
        with open(f"{selection_name}.txt", "w") as f:
    #with open('readme.txt', 'w') as f:
    #  f.write('readme')
            for card, quantity in st.session_state.selected_cards.items():
                f.write(f'{quantity} {card}\n')
        st.success(f"Selection '{selection_name}' saved successfully!")
    elif selection_name:
        st.error("Please select at least one card.")
    elif st.session_state.selected_cards:
        st.error("Please enter a name.")

def load_saved_selection(textfile):
    with open(f'saved_selections/{textfile}', 'r') as f:
        lines = f.readlines()

    dResult = {}
    for line in lines:
        quantity = line.split(' ')[0]
        card = line[len(quantity) + 1:].strip()
        dResult[card] = quantity

    return dResult

# Modified function for loading saved selections
def load_saved_selections():
    saved_selections = ['']
    saved_selections = saved_selections + [f for f in os.listdir('saved_selections') if f.endswith('.txt')]
    return [os.path.splitext(f)[0] for f in saved_selections]

# New function to update card quantity
def update_card_quantity(card_name, quantity):
  if quantity > 0:
    st.session_state.selected_cards[card_name] = quantity
  elif card_name in st.session_state.selected_cards:
    del st.session_state.selected_cards[card_name]

def format_pokemon_card_line(line):
    # Teile die Zeile in Wörter auf
    words = line.split()
    
    # Finde die Position der letzten beiden Wörter
    last_word = words[-1]
    second_last_word = words[-2]
    
    # Erstelle den neuen String mit | als Trenner für die letzten beiden Elemente
    new_line = ' '.join(words[:-2]) + f"|{second_last_word}|{last_word}"
    
    return new_line

def parse_card_entries(text):
  """
  Parse card entries to extract quantity, name, set, and card number.
  
  Pattern explanation:
  ^(\d+)\s+       # Start of line, capture quantity (1 or more digits), followed by whitespace
  (.+?)\s+      # Capture name (non-greedy match), followed by whitespace
  ([A-Z]{3})\s+    # Capture 3-letter set code, followed by whitespace
  (\d+)$       # Capture card number at end of line
  """
  pattern = r'^(\d+)\s+(.+?)\s+([A-Z]{3})\s+(\d+)$'
  # Compile the regex pattern
  regex = re.compile(pattern)
  results = []
  for line in text.strip().split('\n'):
    match = regex.match(line)
    if match:
      quantity, name, set_code, number = match.groups()
      results.append([quantity, name.strip(), set_code, number])

  return results

lang = st.selectbox('Language', ['english', 'deutsch'])

# Load data
df_orig = load_data(lang)
df = df_orig

# Reset Button
bReset = st.button('Reset')
if bReset:
  # del st.session_state['selected_cards']
  st.session_state.selected_cards = {}

# Create tabs
tab1, tab2, tab3 = st.tabs(['Card selection', 'Saved selections', 'Import'])

with tab1:
  # Existing search functionality
  col_search, _ = st.columns([2,3])
  search_term_evolves_from = st_keyup("Find in: 'Evolves from'")
  search_term = st_keyup('Find in names or attacks:')
  if search_term_evolves_from:
    mask = df['Evolves from'].str.contains(search_term_evolves_from, case=False, na=False)
    df = df[mask]
  elif search_term:
    if lang == 'english':
      mask = df['Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 1 Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 2 Name'].str.contains(search_term, case=False, na=False)
    elif lang == 'deutsch':
      mask = df['Name'].str.contains(search_term, case=False, na=False) | \
        df['Name EN'].str.contains(search_term, case=False, na=False) | \
        df['Attack 1 Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 1 Name EN'].str.contains(search_term, case=False, na=False) | \
        df['Attack 2 Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 2 Name EN'].str.contains(search_term, case=False, na=False)
    df = df[mask]

#  st.divider()
  with st.expander('Filter'):
    # Filter
    col1, col2, col3 = st.columns(3)
  
    with col1:
      Cardtype_options = ['All'] + sorted(df['Cardtype'].unique().tolist())
      cardtype = st.selectbox('Cardtype', Cardtype_options)
      # print(f'{Cardtype = }')
      attack1_cost_options = sorted(df['Attack 1 cost'].unique().tolist())
      attack1_cost = st.multiselect('Attack 1 cost', attack1_cost_options)
      # print(f'{attack1_cost = }')
      attack1_damage_options = sorted(df['Attack 1 damage'].unique().tolist())
      attack1_damage = st.multiselect('Attack 1 damage', attack1_damage_options)
      # print(f'{attack1_damage = }')
  
    with col2:
      typ_options = ['All'] + sorted(df['Typ'].unique().tolist())
      typ = st.selectbox('Typ', typ_options)
      # print(f'{typ = }')
      attack2_cost_options = sorted(df['Attack 2 cost'].unique().tolist())
      attack2_cost = st.multiselect('Attack 2 cost', attack2_cost_options)
      # print(f'{attack2_cost = }')
      attack2_damage_options = sorted(df['Attack 2 damage'].unique().tolist())
      attack2_damage = st.multiselect('Attack 2 damage', attack2_damage_options)
      # print(f'{attack2_damage = }')
  
    with col3:
      kp_min = int(df[dConfig[lang]['hp']].min())
      kp_max = int(df[dConfig[lang]['hp']].max())
      iStep = 10
      if kp_min == kp_max:
        kp_max += iStep
      kp_range = st.slider(dConfig[lang]['hp'], kp_min, kp_max, (kp_min, kp_max), step=iStep)
      # print(f'{kp_range = }')
      set_filter = st.multiselect('Set', sorted(df['Set'].unique()))
      # print(f'{set_filter = }')
      regulation = st.multiselect('Regulation', df['Regulation'].unique())
      # print(f'{regulation = }')

    # Anwenden der Filter
    if cardtype != 'All':
      df = df[df['Cardtype'] == cardtype]
    if typ != 'All':
      df = df[df['Typ'] == typ]
    df = df[(df[dConfig[lang]['hp']] >= kp_range[0]) & (df[dConfig[lang]['hp']] <= kp_range[1])]
    if attack1_cost:
      # df = df[df['Attack 1 cost'] == attack1_cost]
      df = df[df['Attack 1 cost'].isin(attack1_cost)]
    if attack1_damage:
      # df = df[df['Attack 1 damage'] == float(attack1_damage)]
      df = df[df['Attack 1 damage'].isin(attack1_damage)]
    if attack2_cost:
      # df = df[df['Attack 2 cost'] == attack2_cost]
      df = df[df['Attack 2 cost'].isin(attack2_cost)]
    if attack2_damage:
      # df = df[df['Attack 2 damage'] == float(attack2_damage)]
      df = df[df['Attack 1 damage'].isin(attack2_damage)]
    if set_filter:
      df = df[df['Set'].isin(set_filter)]
    if regulation:
      df = df[df['Regulation'].isin(regulation)]

  st.metric('Karten', len(df))
  col, _ = st.columns([2,3])
  search_term_cap = col.text_input('Find in Ability:')
  if search_term_cap:
    mask = df['Ability'].str.contains(search_term_cap, case=False, na=False) | \
      df['Ability Text'].str.contains(search_term_cap, case=False, na=False)
    df = df[mask]

    col2, _ = st.columns([2,3])
    search_term_cap_2 = col2.text_input('Find in Ability 2:')
    if search_term_cap_2:
      mask = df['Ability'].str.contains(search_term_cap_2, case=False, na=False) | \
        df['Ability Text'].str.contains(search_term_cap_2, case=False, na=False)
      df = df[mask]

  # st.dataframe(df)
  event = st.dataframe(
    df,
    # column_config=column_configuration,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
  )

  st.header("Selected cards")
  selected_cards = event.selection.rows
  filtered_df = df.iloc[selected_cards]
  st.dataframe(
    filtered_df,
    # column_config=column_configuration,
    use_container_width=True,
  )

  # Reset Button
  # bReset = st.button('Reset2')
  # if bReset:
  #   # del st.session_state['selected_cards']
  #   st.session_state.selected_cards = {}

  if not filtered_df.empty:
    st.write(f"Show {min(st.session_state.num_images, len(filtered_df))} cards:")
    cols = st.columns(4)
    for i in range(min(st.session_state.num_images, len(filtered_df))):
      card = filtered_df.iloc[i]
      with cols[i % 4]:
        col_num, col_link = st.columns(2)
        if lang == 'english':
          quantity = col_num.number_input(f"{card['Name']} {card['Set']} {card['#']}", min_value=0, value=st.session_state.selected_cards.get(f"{card['Name']} {card['Set']} {card['#']}", 0), key=f"quantity_{i}", max_value=4)
        if lang == 'deutsch':
          quantity = col_num.number_input(f"{card['Name']} '{card['Name EN']}' {card['Set']} {card['#']}", min_value=0, value=st.session_state.selected_cards.get(f"{card['Name']} {card['Set']} {card['#']}", 0), key=f"quantity_{i}", max_value=4)

        url = f'https://limitlesstcg.com/cards/de/{card['Set']}/{card['#']}'
        col_link.link_button('go to card on limitlessTCG', url)
        st.image(card['URL'], width=400)
        # st.link_button('go to card on limitlessTCG', url)
        update_card_quantity(f"{card['Name']}|{card['Set']}|{card['#']}", quantity)

    if st.session_state.num_images < len(filtered_df):
      if st.button('load more'):
        load_more()
      st.write(f"Angezeigt: {min(st.session_state.num_images, len(filtered_df))} von {len(filtered_df)} Karten")

    # Save selection
    st.subheader("Auswahl speichern")
    col_save, _ = st.columns([2,3])
    print(col_save.text_input("Name für die Auswahl:", key="selection_name"))
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
  # saved_selections = load_saved_selections()  # list of files
  # col_saved, _ = st.columns([2,3])
  # selected_save = col_saved.selectbox("Wählen Sie eine gespeicherte Auswahl:", saved_selections)
  # print(f'|{selected_save}|', 'selected_save bool', bool(selected_save), type(selected_save))

  # if selected_save:
  #   loaded_selection = load_saved_selection(f"{selected_save}.txt")
  #   st.write(f"Karten in '{selected_save}':")
  #   for card, quantity in loaded_selection.items():
  #     st.write(f"{card}: {quantity}")

  #   # Display the selected cards
  #   cols = st.columns(4)
  #   for i, (card_id, quantity) in enumerate(loaded_selection.items()):
  #     print(f'{card_id = }')
  #     card_name, card_set, card_num = card_id.split('|')
  #     mask = df_orig['Name'].str.contains(card_name, case=False, na=False) & \
  #       df_orig['Set'].str.contains(card_set, case=False, na=False) & \
  #       df_orig['#'].str.contains(card_num, case=False, na=False)

  #     card = df_orig[mask].iloc[0]
  #     with cols[i % 4]:
  #       st.write(f"{card['Name']} '{card['Name EN']}' {card['Set']} {card['#']}")
  #       # col_quan, col_del = cols = st.columns(2)
  #       st.write(f"Anzahl: {quantity}")
  #       st.image(card['URL'], width=300)
  #       bDelete = st.button(f'remove {card_id}')
  #       if bDelete:
  #         print('removing this card')

with tab3:
    input_text = st.text_area('input import')
    parsed_cards = parse_card_entries(input_text)

    iCounter = 0
    cols = st.columns(4)
    for lCard in parsed_cards:
      # Display the selected cards
      # for i, (card_id, quantity) in enumerate(loaded_selection.items()):
      print(f'{lCard = }')
      quan, card_name, card_set, card_num = lCard
      print(quan, card_name, card_set, card_num)
      mask = df_orig['Name EN'].str.contains(card_name, case=False, na=False) & \
        df_orig['Set'].str.contains(card_set, case=False, na=False) & \
        df_orig['#'].str.contains(card_num, case=False, na=False)

      card = df_orig[mask].iloc[0]
      with cols[iCounter % 4]:
        st.text(f"{quan}\t{card['Name']}\n{card['Name EN']} {card['Set']} {card['#']}")
        # col_quan, col_del = cols = st.columns(2)
        # st.text(f"Anzahl: {quan}")
        st.image(card['URL'], width=300)
        bDelete = st.button(f'remove {card_name} {card_set} {card_num}')
        if bDelete:
          print('removing this card')
      iCounter += 1

# print('st.session_state')
# print(st.session_state)
# print(st.session_state.selected_cards)
# st.write(st.session_state)
# st.write(st.session_state.selected_cards)
