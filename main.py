import re

import streamlit as st
import pandas as pd
import os

from st_keyup import st_keyup
# import pyperclip

import config as c

# TODO filter Tera

st.set_page_config(page_title='pkmndb', page_icon='🐲', layout='wide')

# Existing initializations
if 'num_images' not in st.session_state:
  st.session_state.num_images = 20

# Modified initialization for selected cards
if 'selected_cards' not in st.session_state:
  st.session_state.selected_cards = {}

if 'card_set' not in st.session_state:
  st.session_state.card_set = set()

# Function to load more images
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

def save_selection():
    selection_name = st.session_state.selection_name
    if selection_name and st.session_state.selected_cards:
        with open(f'{selection_name}.txt', 'w') as f:
    #with open('readme.txt', 'w') as f:
    #  f.write('readme')
            for card, quantity in st.session_state.selected_cards.items():
                f.write(f'{quantity} {card}\n')
        st.success(f"Selection '{selection_name}' saved successfully!")
    elif selection_name:
        st.error('Please select at least one card.')
    elif st.session_state.selected_cards:
        st.error('Please enter a name.')

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

def format_pokemon_card_line(line):
    # Teile die Zeile in Wörter auf
    words = line.split()
    
    # Finde die Position der letzten beiden Wörter
    last_word = words[-1]
    second_last_word = words[-2]
    
    # Erstelle den neuen String mit | als Trenner für die letzten beiden Elemente
    new_line = ' '.join(words[:-2]) + f'|{second_last_word}|{last_word}'
    
    return new_line

def parse_card_entries(text):
  r"""
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

def reset_fields():
  for k, v in st.session_state.items():
  st.session_state.seg_ctrl_lang = 'english'
  st.session_state.seg_ctrl_format = 'standard'
  st.session_state.search_term_name = None
  st.session_state.search_term_evolves_from_key = ''
  st.session_state.search_term_ability = ''
  st.session_state.search_term_att_eff = ''
  st.session_state.cardtype = 'All'
  st.session_state.att_eff = None
  st.session_state.evolves = None
  st.session_state.selected_cards = {}
  st.session_state.bAdded_Card = False
  st.session_state.num_images = 20
  st.session_state.name_decklist = ''
  st.session_state.not_found = []
  for k, v in st.session_state.items():

# Initialisiere das Set
if 'card_set' not in st.session_state:
  st.session_state.card_set = set()

def update_quantity(old_item, new_quantity):
  """Aktualisiert die Anzahl eines Elements im Set"""
  # Entferne das alte Element
  st.session_state.card_set.remove(old_item)

  # Erstelle das neue Element mit aktualisierter Anzahl
  pattern = r'^\d+'
  new_item = re.sub(pattern, str(new_quantity), old_item)

  # Füge das neue Element hinzu
  st.session_state.card_set.add(new_item)

# Battlelog viewer START
def get_language(text):
    global language_battlelog
    language_battlelog = ['english', 'deutsch'][text.split('\n')[0] == 'Vorbereitung']

def load_saved_battlogs():
    saved_selections = ['']
    saved_selections = saved_selections + [f'{battlelog}.txt' for battlelog in os.listdir(c.sBattlelogs_Folder) if battlelog.endswith('.txt')]
    return [os.path.splitext(f)[0] for f in saved_selections]

def extract_players(preparation_text):
    players = []
    lines = preparation_text.split('\n')

    for line in lines:
        if c.dTranslations[language_battlelog]['player_pattern'] in line:
            player = line.split(c.dTranslations[language_battlelog]['player_pattern'])[0].strip()
            players.append(player)
    return players

def get_player_colors(players):
    """Assign colors to players"""
    colors = ['#FF4B00', '#4B8BFF']  # Rot und Blau
    return {player: color for player, color in zip(players, colors)}

def color_player_names(text, player_colors):
    """Replace player names with colored versions"""
    for player, color in player_colors.items():
        text = text.replace(player, f"<span style='color: {color}; font-weight: bold;'>{player}</span>")
    return text

def color_player_names_events(text, player_colors, sKey=None):
  """Replace player names with colored versions"""
  if ':' not in text:
    return text

  text_turn, text_text = text.split(':')
  if sKey is not None:
    color = c.dImportant_Actions_colors[sKey]
    text_text = text_text.replace(sKey, f"<span style='color: {color}; font-weight: bold;'>{sKey}</span>")

  for player, player_color in player_colors.items():
    text_text = text_text.replace(player, f"<span style='color: {player_color}; font-weight: bold;'>{player}</span>")

  return f'<p><u>{text_turn}:</u> {text_text}</p>'

def find_last_item(lst):
    """
    Find the last item in the list.
    """
    true_indices = [x for x in lst if x]
    return true_indices[-1]

def get_winner(text):
    winner = 'not found'
    last_line = find_last_item(text.split('\n'))
    # Suche nach dem Muster
    match = re.search(c.dTranslations[language_battlelog]['winner_pattern'], text)
    if match:
        winner = match.group(1)
    return winner, last_line

def parse_game_log(log_text):
    # Split into preparation and turns
    parts = log_text.split('\n\nTurn #')
    preparation = parts[0]
    turns = ['Turn #' + turn for turn in parts[1:]]

    return preparation, turns

def extract_turn_info(turn_text):
    # Extract turn number and player
    turn_header = turn_text.split('\n')[0]
    turn_num = int(re.search(r'Turn # (\d+)', turn_header).group(1))
    player = re.search(c.dTranslations[language_battlelog]['turn_pattern'], turn_header).group(1)

    # Extract actions
    actions = [line.strip() for line in turn_text.split('\n')[1:] if line.strip()]

    return {
        'turn_number': turn_num,
        'player': player,
        'actions': actions
    }

def format_action(action, player_colors):
  """Format action text with colored player names and appropriate styling"""
  formatted_text = color_player_names(action, player_colors)
  action_lower = action.lower()

  # Define action patterns and their corresponding emojis/formats
  patterns = {
    'knockout': '🪦',
    'win': '🏆',
    'damage': '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;⚡',
    ('ist jetzt in der aktiven position', 'is now in the Active Spot'): '🆕',
    ('XXX', 'breakdown'): '💥',
    ('schadenspunkte', 'damage'): '🗡️',
    ('preiskarte', 'prize card'): '🏅',
    ('ablagestapel', 'discarded'): '📥',
    ('gespielt', 'played'): '🃏',
    ('gemischt', 'shuffled'): '🌀',
    ('hinzugefügt', 'gezogen', 'drew', 'drawn', 'added'): '➕',
    ('entwickelt', 'energie', 'evolved', 'energy'): '🎯',
    ('eingesetzt', 'used'): '⚙️',
    ('XXX', "didn't take an action in time"): '⏳',
    ('XXX', 'ended their turn'): '🔚',
  }

  # Check for special cases first
  if '• ' in action and c.dTranslations[language_battlelog]['damage'] in action:
    pattern = patterns['damage']
  elif c.dTranslations[language_battlelog]['knockout'] in action:
    pattern = patterns['knockout']
  elif c.dTranslations[language_battlelog]['win'] in action:
    pattern = patterns['win']
  else:
    # Check other patterns
    for keys, pattern in patterns.items():
      if isinstance(keys, str):
        continue  # Skip the special cases we handled above
      if any(key in action_lower for key in keys):
        break
    else:
      # Default pattern if no match found
      return formatted_text

  return f'{pattern} {formatted_text}'
# Battlelog viewer END

# Decklist viewer
def parse_decklist(decklist_text):
  dOutput = {}
  lNotFound = []
  iCounter = 0
  # Process each non-empty line
  for sLine in (line.strip() for line in decklist_text.splitlines() if line.strip()):
    # Skip section headers and empty lines
    if any(keyword in sLine for keyword in c.lDecklistKeywords):
      continue

    # Parse card entry
    if matches := re.match(c.sDecklistEntryPattern, sLine):
      amount, name, set_code, card_number = matches.groups()
      st.write(f'{sLine} => Amount: {amount}, Name: {name}, Set: {set_code}, Number: {card_number}')
      dOutput[iCounter] = {
        'amount': int(amount),
        'name': name,
        'set': set_code,
        'number': card_number
      }
      iCounter += 1

    else:
      st.error(f'Could not parse: {sLine}')
      lNotFound.append(sLine)

  # st.write(dOutput)

  return dOutput, lNotFound

def display_decklist(decklist_dict, not_found_cards, num_columns):
  st.divider()
  # Display not found cards if any exist
  if not_found_cards:
    st.write("Cards not found")
    for card in not_found_cards:
      st.error(card)

  # Create grid layout
  cols = st.columns(num_columns)

  # Display cards in grid
  for idx, dCard in decklist_dict.items():
    with cols[idx % num_columns]:
      try:
        image_url = (
          f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/"
          f"tpci/{dCard['set']}/{dCard['set']}_{dCard['number']:0>3}_R_EN_LG.png"
        )
        st.write(dCard['name'])
        if 'Basic' in dCard['name'] and 'Energy' in dCard['name']:
          iMaxValue = 59
        else:
          iMaxValue = 4
        dCard['amount'] = st.number_input(dCard['name'], min_value=0, value=int(dCard['amount']), max_value=iMaxValue, key=f"decklist_card_{idx}", label_visibility='collapsed')
        st.image(image_url, use_container_width=True)
      except Exception as e:
        st.error(f"Error displaying card: {dCard['name']}")
        st.write(f"Error details: {str(e)}")
  for idx, dCard in decklist_dict.items():
    # for key, aCard in dCard.items():
    #   if key == 'name':
    #   else:
  return decklist_dict

def add_card_to_decklist(dDecklist, name, set_, num):
  iNew_key = max(list(dDecklist.keys())) + 1
  dDecklist[iNew_key] = {
    'amount': 1,
    'name': name,
    'set': set_,
    'number': num
  }
  return dDecklist

def export_decklist(dDecklist):
  text = f"\n{'\n'.join(f"{card['amount']} {card['name']} {card['set']} {card['number']}" for card in dDecklist.values())}\n"
  with st.popover('popover', icon="🚨"):
    st.code(text)
  # pyperclip.copy(text)

col_lang, col_format, col_reset = st.columns(3)
with col_lang:
  language_cards = st.segmented_control('Cards language', ['english', 'deutsch'], default='english', key='seg_ctrl_lang')
with col_format:
  sCards_format = st.segmented_control('Cards format', ['standard', 'all'], default='standard', key='seg_ctrl_format')
with col_reset:
  # Reset Button
  st.write('')
  bReset = st.button('Reset - not working as expected', key='reset', on_click=reset_fields)

# Load data
df_orig = load_data()
lIndices = [47, 48 , 49]
if sCards_format == 'standard':
  df_orig = df_orig[df_orig['Regulation'].isin(c.lStandard_regulations)] # lStandard_regulations
df = df_orig.reset_index(drop=True)

lUniqueNames = df['Name'].unique().tolist()

# saved for later
# tab1, tab2, tab3, tab4 = st.tabs(['Card selection', 'Saved selections', 'Import', 'Battle log viewer'])
tab1, tab2, tab3 = st.tabs(['Card selection', 'Battlelog viewer', 'Decklist Viewer'])

# Card search
with tab1:
  with st.expander('Filter'):
    # Filter
    col1, col2, col3 = st.columns(3)
  
    with col1:
      lCardtype_options = ['All', 'Ace Spec', 'Pokemon'] + sorted(df['Cardtype'].unique().tolist())
      cardtype = st.selectbox('Cardtype', lCardtype_options)
      if cardtype == 'Pokemon':
        df = df[df['Cardtype'].isin(['Basic', 'Stage 1', 'Stage 2'])]
      elif cardtype == 'Ace Spec':
        df = df[df['Cardtype'].str.contains('Ace Spec')]
      elif cardtype != 'All':
        df = df[df['Cardtype'] == cardtype]
      typ_options = ['All'] + sorted(df['Type'].unique().tolist())
      type_filter = st.selectbox('Type', typ_options)
      if type_filter != 'All':
        df = df[df['Type'] == type_filter]
      lWeakness_options = ['Choose an option'] + sorted(df['Weakness'].unique().tolist())
      weakness_filter = st.selectbox('Weakness', lWeakness_options)
      if weakness_filter != 'Choose an option':
        df = df[df['Weakness'] == weakness_filter]

    with col2:
      attack_cost_options = sorted(set(df['Attack 1 cost'].unique().tolist() + df['Attack 2 cost'].unique().tolist()))
      attack_cost = st.multiselect('Attack cost', attack_cost_options, key='multiselect_key_attack_cost')
      if attack_cost:
        df = df[df['Attack 1 cost'].isin(attack_cost) | df['Attack 2 cost'].isin(attack_cost)]
      attack_damage_options = sorted(set(df['Attack 1 damage'].unique().tolist() + df['Attack 2 damage'].unique().tolist()))
      attack_damage = st.multiselect('Attack damage', attack_damage_options, key='multiselect_key_attack_damage')
      if attack_damage:
        df = df[df['Attack 1 damage'].isin(attack_damage) | df['Attack 2 damage'].isin(attack_damage)]
      hp_min = int(df['HP'].min())
      hp_max = int(df['HP'].max())
      iStep = 10
      if hp_min == hp_max:
        hp_max += iStep
      hp_range = st.slider('HP', hp_min, hp_max, (hp_min, hp_max), step=iStep)
      df = df[(df['HP'] >= hp_range[0]) & (df['HP'] <= hp_range[1])]

    with col3:
      col_set, col_num = st.columns(2)
      with col_set:
        set_filter = st.multiselect('Set', sorted(df['Set'].unique()), key='multiselect_key_set_filter')
        if set_filter:
          df = df[df['Set'].isin(set_filter)]
      with col_num:
        num_filter = st.multiselect('Number', sorted(df['#'].unique()), key='multiselect_key_num_filter')
        if num_filter:
          df = df[df['#'].isin(num_filter)]
      regulation_filter = st.multiselect('Regulation', df['Regulation'].unique(), key='multiselect_key_regulation_filter')
      if regulation_filter:
        df = df[df['Regulation'].isin(regulation_filter)]
      sToggle_ex = st.segmented_control('Pokemon ex', ["include 'ex'", "exclude 'ex'", "only 'ex'"], default="include 'ex'", key='sToggle_ex', label_visibility='hidden')
      if sToggle_ex == "exclude 'ex'":
        df = df[~df['Name'].str.endswith(' ex')]
      if sToggle_ex == "only 'ex'":
        df = df[df['Name'].str.endswith(' ex')]
      sToggle_V = st.segmented_control('Pokemon V', ["include 'V(STAR)'", "exclude 'V(STAR)'", "only 'V(STAR)'"], default="include 'V(STAR)'", key='sToggle_V', label_visibility='hidden')
      if sToggle_V == "exclude 'V(STAR)'":
        df = df[~df['Name'].str.endswith(('V', 'VSTAR'))]
      if sToggle_V == "only 'V(STAR)'":
        df = df[df['Name'].str.endswith(('V', 'VSTAR'))]
      if language_cards == 'deutsch':
        sSame_name = st.segmented_control('Same name in english and german only', ['no', 'yes'], default='no', key='same_name_key')
        if sSame_name == 'yes':
          df = df[df['Name DE'] == df['Name']]

  col_search_left1, col_search_right1 = st.columns(2)
  with col_search_left1:
    search_term_name = st_keyup('Find in Pokemon name:', key='search_term_name_key')
    if search_term_name:
      if language_cards == 'english':
        mask = df['Name'].str.contains(search_term_name, case=False, na=False)
      elif language_cards == 'deutsch':
        mask = df['Name DE'].str.contains(search_term_name, case=False, na=False) | \
          df['Name'].str.contains(search_term_name, case=False, na=False)
      df = df[mask]
  with col_search_right1:
    search_term_evolves_from = st_keyup("Find in 'Evolves from'", key='search_term_evolves_from_key')
    if search_term_evolves_from:
      mask = df['Evolves from'].str.contains(search_term_evolves_from, case=False, na=False) | \
          df['Evolves from DE'].str.contains(search_term_evolves_from, case=False, na=False)
      df = df[mask]

  col_search_left2, col_search_right2 = st.columns(2)
  with col_search_left2:
    search_term_ability = st_keyup('Find in ability (name or text):', key='search_term_ability_key')
    if search_term_ability:
      mask = df['Ability'].str.contains(search_term_ability, case=False, na=False) | \
        df['Ability text'].str.contains(search_term_ability, case=False, na=False)
      df = df[mask]
  with col_search_right2:
    search_term_ability_2 = st_keyup('and...', key='search_term_ability_2_key')
    if search_term_ability_2:
      mask = df['Ability'].str.contains(search_term_ability_2, case=False, na=False) | \
        df['Ability text'].str.contains(search_term_ability_2, case=False, na=False)
      df = df[mask]

  col_search_left3, col_search_right3 = st.columns(2)
  with col_search_left3:
    search_term_attack = st_keyup('Find in name of attack:', key='search_term_attack_key')
    if search_term_attack:
      if language_cards == 'english':
        mask = df['Attack 1 name'].str.contains(search_term_attack, case=False, na=False) | \
          df['Attack 2 name'].str.contains(search_term_attack, case=False, na=False)
      elif language_cards == 'deutsch':
        mask = df['Attack 1 name DE'].str.contains(search_term_attack, case=False, na=False) | \
          df['Attack 1 name'].str.contains(search_term_attack, case=False, na=False) | \
          df['Attack 2 name DE'].str.contains(search_term_attack, case=False, na=False) | \
          df['Attack 2 name'].str.contains(search_term_attack, case=False, na=False)
      df = df[mask]
  with col_search_right3:
    search_term_att_eff = st_keyup('Find in effect of attack:', key='search_term_att_eff_key')
    if search_term_att_eff:
      if language_cards == 'english':
        mask = df['Effect 1'].str.contains(search_term_att_eff, case=False, na=False) | \
          df['Effect 2'].str.contains(search_term_att_eff, case=False, na=False)
      elif language_cards == 'deutsch':
        mask = df['Effect 1 DE'].str.contains(search_term_att_eff, case=False, na=False) | \
          df['Effect 1'].str.contains(search_term_att_eff, case=False, na=False) | \
          df['Effect 2 DE'].str.contains(search_term_att_eff, case=False, na=False) | \
          df['Effect 2'].str.contains(search_term_att_eff, case=False, na=False)
      df = df[mask]

  # Show filters
  dFilters = {
    'sCards_format': sCards_format,
    'search_term_name': search_term_name,
    'search_term_attack': search_term_attack,
    'search_term_evolves_from': search_term_evolves_from,
    'cardtype': cardtype,
    'attack_cost': attack_cost,
    'attack_damage': attack_damage,
    'weakness_filter': weakness_filter,
    'type_filter': type_filter,
    'set_filter': set_filter,
    'num_filter': num_filter,
    'regulation_filter': regulation_filter,
    'hp_range': hp_range,
    'sToggle_ex': sToggle_ex,
    'sToggle_V': sToggle_V,
  }
  with st.expander(f'Found cards {len(df)} - Show filter'):
    st.write(dFilters)

  if not df.empty:
    df_with_urls = df.reset_index(drop=True)
    if language_cards == 'english':
      df = df.drop(c.lColumns_DE, axis=1)
    lColumns_to_show = st.multiselect('Show only these columns', list(df.columns), key='multiselect_key_lColumns_to_show')
    if lColumns_to_show:
      df = df[lColumns_to_show]

    st.write('⬇️ Select cards here')
    event = st.dataframe(
      df,
      use_container_width=True,
      hide_index=True,
      on_select='rerun',
      selection_mode='multi-row',
    )

    st.header('Selected cards')
    selected_cards = event.selection.rows
    df_selected_cards = df.iloc[selected_cards]

    st.dataframe(
      df_selected_cards,
      use_container_width=True,
    )
    if 'URL' not in lColumns_to_show:
      if language_cards == 'deutsch':
        df_selected_cards['URL'] = df_with_urls.iloc[selected_cards]['URL DE']
    if 'Set' not in lColumns_to_show:
      df_selected_cards['Set'] = df_with_urls.iloc[selected_cards]['Set']
    if 'num' not in lColumns_to_show:
      # df_selected_cards['num'] = df_with_urls.iloc[selected_cards]['#']
      df_selected_cards['num'] = df_with_urls.loc[selected_cards, '#'].values

    if not df_selected_cards.empty:
      st.write(f'Show {min(st.session_state.num_images, len(df_selected_cards))} cards:')
      iWidth = 400  # st.slider('size', 100, 600, 400, 50)
      cols = st.columns(4)
      for i in range(min(st.session_state.num_images, len(df_selected_cards))):
        card = df_selected_cards.iloc[i]
        with cols[i % 4]:
          col_num, col_link = st.columns(2)
          card_id = f"1 {card['Name']} {card['Set']} {card['num']}"
          pin = col_num.toggle('add card', key=card_id)
          if pin:
            st.session_state.card_set.add(card_id)
          else:
            if card_id in st.session_state.card_set:
              st.session_state.card_set.remove(card_id)

          url = card['URL']
          col_link.link_button('go to card on limitlessTCG', url)
          st.image(url, width=iWidth)

      if st.session_state.num_images < len(df_selected_cards):
        if st.button('load more'):
          load_more()
        st.write(f'Show: {min(st.session_state.num_images, len(df_selected_cards))} von {len(df_selected_cards)} Karten')
  else:
    st.write('No card found')

  # App-Titel
  st.header('Card set administration - TBD')

  # Zeige alle Elemente mit Bearbeitungsmöglichkeiten

  for item in sorted(list(st.session_state.card_set), key=lambda x: x[2:-8]):
    col1, col2 = st.columns([3, 1])

    with col1:
      st.text(item)

    with col2:
      # Extrahiere die aktuelle Anzahl
      current_quantity = int(re.match(r'^\d+', item).group())

      # Erstelle einen eindeutigen Schlüssel für den Zahleneingabebereich
      key = f'quantity_{item}'

      # Eingabefeld für die neue Anzahl
      if 'Basic' in item and 'Energy' in item:
        iMaxValue = 59
      else:
        iMaxValue = 4
  #     new_quantity = st.number_input(
  #       'Anzahl', 
  #       min_value=0,
  #       max_value=iMaxValue,
  #       value=current_quantity,
  #       step=1,
  #       key=key,
  #       label_visibility='collapsed'
  #     )

  #     # Wenn sich die Anzahl geändert hat und der Benutzer die Änderung bestätigt
  #     if new_quantity != current_quantity:# and st.button('Aktualisieren', key=f'update_{item}'):
  #       update_quantity(item, new_quantity)
  #       st.rerun()

  st.subheader('Decklist')
  for card in sorted(list(st.session_state.card_set), key=lambda x: x[2:-8]):
    st.write(card)

# Battlelog viewer
with tab2:
  st.title('Pokemon Trading Card Game - Battlelog Viewer')

  # game_log = ''

  # bfile_uploader = st.toggle('Load battlelog from textfile')
  # if bfile_uploader:
  #   col1, col2 = st.columns(2)
  #   with col1:
  #     # File uploader for the game log
  #     uploaded_file = st.file_uploader('Upload battlelog', type=['txt'])

  #   with col2:
  #     saved_battlogs = load_saved_battlogs()
  #     selected_battlog = st.selectbox('Choose battlelog', saved_battlogs)

  #   if uploaded_file is not None:
  #     game_log = uploaded_file.getvalue().decode('utf-8')
  #   elif selected_battlog:
  #     battlelogfile = rf'{c.sBattlelogs_Folder}\{selected_battlog}'
  #     with open(battlelogfile, 'r', encoding='utf-8') as _battlelog:
  #       game_log = _battlelog.read()
  # else:
  game_log = st.text_area('Paste battlelog here')

  if game_log:
    get_language(game_log)

    # Parse the game log
    preparation, turns = parse_game_log(game_log)
    winner, last_line = get_winner(game_log)

    # Extract players and assign colors
    players = extract_players(preparation)
    player_colors = get_player_colors(players)

    # Display player information
    st.markdown('### Players')
    cols = st.columns(2)
    for i, (player, color) in enumerate(player_colors.items()):
      with cols[i]:
        if player == winner:
          st.markdown(f'''<div style="text-align: center; padding: 10px; border-radius: 5px; border: 2px solid {color}; background-color:gold;">
                      <h4 style="color: {color}">{player}</h4>
                      <p>{last_line}</p>
                      </div>''',
                      unsafe_allow_html=True)
        else:
          st.markdown(f'''<div style="text-align: center; padding: 10px; border-radius: 5px; border: 2px solid {color}">
                      <h4 style="color: {color}">{player}</h4></div>''',
                      unsafe_allow_html=True)

    # Create tabs for different views
    tab1, tab2 = st.tabs([f"🎮 {c.dTranslations[language_battlelog]['gameplay']}", f"📊 {c.dTranslations[language_battlelog]['statistics']}"])

    with tab1:
      # Display preparation phase with colored player names
      with st.expander(f"📝 {c.dTranslations[language_battlelog]['setup']}", expanded=False):
        for line in preparation.split('\n'):
          if line.strip():
            st.markdown(color_player_names(line, player_colors), unsafe_allow_html=True)

      # Display turns
      for turn in turns:
        turn_info = extract_turn_info(turn)
        player = turn_info['player']
        color = player_colors[player]
        light_color = f'{color}22'  # Add transparency for lighter background

        st.markdown(f"""
        <div style="background: linear-gradient(to right, {light_color}, white);
              padding: 15px; border-radius: 10px; margin: 10px 0;
              border-left: 5px solid {color};">
          <h3>{c.dTranslations[language_battlelog]['turn']} {turn_info['turn_number']} - <span style='color: {color}'>{player}</span></h3>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f'{c.dTranslations[language_battlelog]['turn']} {turn_info['turn_number']}', True):
          # Display actions with colored player names
          for action in turn_info['actions']:
            if last_line in action:
              st.markdown(f'''<div style="text-align: center; border-radius: 5px; background-color: gold;">
                    <h4 style="color: black">{action}</h4></div>''',
                    unsafe_allow_html=True)
            elif c.dTranslations[language_battlelog]['suddendeath'] in action or c.dTranslations[language_battlelog]['suddendeath'] in action:
              st.markdown(f'''<div style="text-align: center; border-radius: 5px; background-color:black;">
                    <h4 style="color: white">{action}</h4></div>''',
                    unsafe_allow_html=True)
            else:
              sLine = format_action(action, player_colors)
              lFound = []
              for sName in lUniqueNames:
                if sName in sLine and sName not in lFound:
                  lFound.append(sName)
                  sName_final = sName
                  if f'{sName} ex' in sLine:
                    sName_final = f'{sName} ex'
                  elif f'{sName} VSTAR' in sLine:
                    sName_final = f'{sName} VSTAR'
                  elif f'{sName} V' in sLine:
                    sName_final = f'{sName} V'
                  sLine = sLine.replace(sName_final, f'**:blue-background[{sName_final}]**')
                  continue
              st.markdown(sLine, unsafe_allow_html=True)

    with tab2:
      # Calculate statistics

      total_turns = len(turns)

      col1, col2, col3 = st.columns(3)
      with col1:
        st.metric(c.dTranslations[language_battlelog]['total_turns'], total_turns)

      with col2:
        knockout_count = sum(1 for turn in turns for action in turn.split('\n')
                  if c.dTranslations[language_battlelog]['knockout'] in action)
        st.metric('Knocked out Pokemons', knockout_count)

      with col3:
        st.metric('x', 0)

      # Add a timeline of major events with colored player names
      st.header(c.dTranslations[language_battlelog]['events'])
      events = []
      for turn in turns:
        turn_info = extract_turn_info(turn)
        for action in turn_info['actions']:
          if any(key in action for key in c.lImportant_Actions):
            events.append(f"{c.dTranslations[language_battlelog]['turn']} {turn_info['turn_number']}: {action}")

      # Add player statistics
      st.subheader(c.dTranslations[language_battlelog]['player_stistics'])
      cols = st.columns(len(players))

      for i, (player, color) in enumerate(player_colors.items()):
        player_turns = [turn for turn in turns if extract_turn_info(turn)['player'] == player]
        player_knockouts = sum(1 for turn in turns
                  for action in turn.split('\n')
                  if player in action and c.dTranslations[language_battlelog]['knockout'] in action)

        with cols[i]:
          st.markdown(f'''
          <div style="padding: 10px; border-radius: 5px; border: 2px solid {color};">
            <h4 style="color: {color}">{player}</h4>
            <p>{c.dTranslations[language_battlelog]['turns_played']} {len(player_turns)} turns</p>
            <p>{c.dTranslations[language_battlelog]['knockout_pokemon']} {player_knockouts} Pokemons</p>
          </div>
          <p></p>''', unsafe_allow_html=True)

      st.subheader('events')
      for event in events:
        for sKey in c.dImportant_Actions_colors.keys():
          if sKey in event:
            st.markdown(color_player_names_events(event, player_colors, sKey), unsafe_allow_html=True)
            break
        else:
          st.markdown(f'{color_player_names_events(event, player_colors)}', unsafe_allow_html=True)

# Decklist viewer
with tab3:
  if 'bAdded_Card' not in st.session_state:
    st.session_state['bAdded_Card'] = False
  sDecklist = st.text_area('Paste decklist here')

  if sDecklist:
    with st.expander('Decklist'):
      if not st.session_state['bAdded_Card']:
        dDecklist, not_found = parse_decklist(sDecklist)
        if 'decklist' not in st.session_state:
          st.write("Adding key 'decklist' to sessionState")
          st.session_state['decklist'] = dDecklist
          st.write("Adding key 'not_found' to sessionState")
          st.session_state['not_found'] = not_found
      else:
        dDecklist = st.session_state['decklist']
        not_found = st.session_state['not_found']
        st.session_state['bAdded_Card'] = False

    num_columns = st.slider('Number of columns:', min_value=1, max_value=20, value=8)

    col_search_term_name, _ = st.columns([1, 3])
    with col_search_term_name:
      search_term_name = st_keyup('Find card by name', key='name_decklist')

    col_found_cards, col_image_selected_card = st.columns([5, 1])
    with col_found_cards:
      if search_term_name:
        df_result = df_orig[df_orig['Name'].str.contains(search_term_name, case=False, na=False)]

        if not df_result.empty:
          event_2 = st.dataframe(
            df_result,
            use_container_width=True,
            hide_index=True,
            on_select='rerun',
            selection_mode='single-row',
          )

          with col_image_selected_card:
            if selected_card := event_2.selection.rows:
              df_selected_card = df_result.iloc[selected_card]
              name = df_selected_card['Name'].iloc[0]
              set = df_selected_card['Set'].iloc[0]
              num = df_selected_card['#'].iloc[0]
              url = df_selected_card['URL'].iloc[0]
              st.write(f'{name} {set} {num}')
              st.image(url, width=200)

              if st.button('Add card to decklist'):
                dDecklist = add_card_to_decklist(dDecklist, name, set, num)
                st.session_state['bAdded_Card'] = True
                st.session_state['decklist'] = dDecklist
        else:
          st.error('No cards found')

    # Display the decklist
    dDecklist = display_decklist(dDecklist, not_found, num_columns)
    text = f"\n{'\n'.join(f"{card['amount']} {card['name']} {card['set']} {card['number']}" for card in dDecklist.values())}\n"
    with st.popover('Show decklist', icon="📄"):
      st.code(text)
