import re

import streamlit as st
import pandas as pd
import os

from st_keyup import st_keyup
# import pyperclip

import config as c

# FIXME Search results with 0 HP
# FIXME Search results when no card is found
# TODO entry

st.set_page_config(page_title='pkmndb', page_icon='🐲', layout='wide')

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
def load_data(language):
  df = pd.read_csv(c.dTranslations[language]['file'], sep=';', encoding=c.dTranslations[language]['encoding'])
  df['HP'] = pd.to_numeric(df['HP'], errors='coerce')
  numeric_columns = ['HP', 'Attack 1 damage', 'Attack 2 damage']

  df[numeric_columns] = df[numeric_columns].fillna(0)
  object_columns = df.select_dtypes(include=['object']).columns
  df[object_columns] = df[object_columns].astype(str)
  return df

def save_selection():
    selection_name = st.session_state.selection_name
    print(f'{selection_name = }')
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

def reset():
  print('reseting')
  st.session_state.selected_cards = {}
  st.session_state.search_term = ''
  st.session_state.search_term_evolves_from = ''
  st.session_state.search_term_cap = ''
  st.session_state.search_term_att_eff = ''
  st.session_state.cardtype = 'All'
  st.session_state.att_eff = None
  st.session_state.evolves = None
  st.session_state.wertzu = False
  st.session_state.bAdded_Card = False
  st.session_state.num_images = 20
  st.session_state.name_decklist = ''
  st.session_state.not_found = []
  st.session_state.names = None

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
        'amount': amount,
        'name': name,
        'set': set_code,
        'number': card_number
      }

    else:
      st.write(f'Could not parse: {sLine}')
      lNotFound.append(sLine)

    iCounter += 1
  # st.write(dOutput)

  return dOutput, lNotFound

def display_decklist(decklist_dict, not_found_cards, num_columns):
  st.divider()
  # Display not found cards if any exist
  if not_found_cards:
    st.write("Cards not found")
    for card in not_found_cards:
      st.write(card)

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
        st.write(f"{dCard['amount']} {dCard['name']}")
        st.image(image_url, use_column_width=True)
      except Exception as e:
        st.error(f"Error displaying card: {dCard['name']}")
        st.write(f"Error details: {str(e)}")

def add_card_to_decklist(dDecklist, name, set_, num):
  # print('Decklist IN')
  # print(dDecklist)
  iNew_key = max(list(dDecklist.keys())) + 1
  print(f'{iNew_key}: {name} {set_} {num}')
  dDecklist[iNew_key] = {
    'amount': '1',
    'name': name,
    'set': set_,
    'number': num
  }
  # print('Decklist OUT')
  # print(dDecklist)
  return dDecklist

def export_decklist(dDecklist):
  # print(dDecklist)
  text = f"\n{'\n'.join(f"{card['amount']} {card['name']} {card['set']} {card['number']}" for card in dDecklist.values())}\n"
  st.code(text)
  # pyperclip.copy(text)

col_lang, col_reset = st.columns([1,5])
# language_cards = col_lang.selectbox('Language', ['english', 'deutsch'])
language_cards = col_lang.selectbox('Language of cards', ['english', 'deutsch'])

# Load data
df_orig = load_data(language_cards)
df = df_orig

lUniqueNames = df['Name'].unique().tolist()

# Reset Button
bReset = col_reset.button('Reset', key='reset', on_click=reset)

# Create tabs
# saved for later
# tab1, tab2, tab3, tab4 = st.tabs(['Card selection', 'Saved selections', 'Import', 'Battle log viewer'])
tab1, tab2, tab3 = st.tabs(['Card selection', 'Battlelog viewer', 'Decklist Viewer'])

# Card search
with tab1:
  col_search_names, col_search_evo = st.columns(2)
  with col_search_names:
    search_term = st_keyup(c.dTranslations[language_cards]['find_in_names'], key='names')
  with col_search_evo:
    search_term_evolves_from = st_keyup(c.dTranslations[language_cards]['find_in_evolves'], key='evolves')

  if search_term_evolves_from:
    mask = df['Evolves from'].str.contains(search_term_evolves_from, case=False, na=False)
    df = df[mask]
  elif search_term:
    if language_cards == 'english':
      mask = df['Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 1 Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 2 Name'].str.contains(search_term, case=False, na=False)
    elif language_cards == 'deutsch':
      mask = df['Name'].str.contains(search_term, case=False, na=False) | \
        df['Name EN'].str.contains(search_term, case=False, na=False) | \
        df['Attack 1 Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 1 Name EN'].str.contains(search_term, case=False, na=False) | \
        df['Attack 2 Name'].str.contains(search_term, case=False, na=False) | \
        df['Attack 2 Name EN'].str.contains(search_term, case=False, na=False)
    df = df[mask]

  if not df.empty:
    with st.expander('Filter'):
      # Filter
      col1, col2, col3 = st.columns(3)
    
      with col1:
        lCardtype_options = ['All', 'Pokemon'] + sorted(df['Cardtype'].unique().tolist())
        cardtype = st.selectbox('Cardtype', lCardtype_options)
        attack1_cost_options = sorted(df['Attack 1 cost'].unique().tolist())
        attack1_cost = st.multiselect('Attack 1 cost', attack1_cost_options)
        attack1_damage_options = sorted(df['Attack 1 damage'].unique().tolist())
        attack1_damage = st.multiselect('Attack 1 damage', attack1_damage_options)
        lWeakness_options = ['Choose an option'] + sorted(df['Weakness'].unique().tolist())
        weakness_filter = st.selectbox('Weakness', lWeakness_options)

      with col2:
        typ_options = ['All'] + sorted(df['Type'].unique().tolist())
        type_filter = st.selectbox('Type', typ_options)
        attack2_cost_options = sorted(df['Attack 2 cost'].unique().tolist())
        attack2_cost = st.multiselect('Attack 2 cost', attack2_cost_options)
        attack2_damage_options = sorted(df['Attack 2 damage'].unique().tolist())
        attack2_damage = st.multiselect('Attack 2 damage', attack2_damage_options)
    
      with col3:
        set_filter = st.multiselect('Set', sorted(df['Set'].unique()))
        regulation_filter = st.multiselect('Regulation', df['Regulation'].unique())
        kp_min = int(df['HP'].min())
        kp_max = int(df['HP'].max())
        iStep = 10
        if kp_min == kp_max:
          kp_max += iStep
        kp_range = st.slider('HP', kp_min, kp_max, (kp_min, kp_max), step=iStep)

      # Applying the filters
      dFilters = {
        'cardtype': cardtype,
        'attack1_cost': attack1_cost,
        'attack1_damage': attack1_damage,
        'weakness_filter': weakness_filter,
        'type_filter': type_filter,
        'attack2_cost': attack2_cost,
        'attack2_damage': attack2_damage,
        'set_filter': set_filter,
        'regulation_filter': regulation_filter,
        'kp_range': kp_range
      }
      if st.checkbox('Show filter'):
        st.write(dFilters)

      # cardtype == 'Pokemon' = Show all Pokemon crads
      if cardtype == 'Pokemon':
        df = df[df['Cardtype'].isin(['Basic', 'Stage 1', 'Stage 2'])]
      elif cardtype != 'All':
        df = df[df['Cardtype'] == cardtype]
      if type_filter != 'All':
        df = df[df['Type'] == type_filter]
      df = df[(df['HP'] >= kp_range[0]) & (df['HP'] <= kp_range[1])]
      if attack1_cost:
        df = df[df['Attack 1 cost'].isin(attack1_cost)]
      if attack1_damage:
        df = df[df['Attack 1 damage'].isin(attack1_damage)]
      if attack2_cost:
        df = df[df['Attack 2 cost'].isin(attack2_cost)]
      if attack2_damage:
        df = df[df['Attack 1 damage'].isin(attack2_damage)]
      if set_filter:
        df = df[df['Set'].isin(set_filter)]
      if regulation_filter:
        df = df[df['Regulation'].isin(regulation_filter)]
      if weakness_filter != 'Choose an option':
        df = df[df['Weakness'] == weakness_filter]

    st.metric('Found cards', len(df))
    col, col2 = st.columns([2,3])
    with col:
      search_term_cap = st_keyup('Find in Ability:')
      search_term_att_eff = st_keyup('Find in attack effect:', key='att_eff')

    if search_term_cap:
      mask = df['Ability'].str.contains(search_term_cap, case=False, na=False) | \
        df['Ability text'].str.contains(search_term_cap, case=False, na=False)
      df = df[mask]
      with col2:
        search_term_cap_2 = st_keyup('and...')
      if search_term_cap_2:
        mask = df['Ability'].str.contains(search_term_cap_2, case=False, na=False) | \
          df['Ability text'].str.contains(search_term_cap_2, case=False, na=False)
        df = df[mask]

    if search_term_att_eff:
      mask = df['Effect 1'].str.contains(search_term_att_eff, case=False, na=False) | \
        df['Effect 2'].str.contains(search_term_att_eff, case=False, na=False)
      df = df[mask]

    event = st.dataframe(
      df,
      # column_config=column_configuration,
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

    if not df_selected_cards.empty:
      st.write(f'Show {min(st.session_state.num_images, len(df_selected_cards))} cards:')
      iWidth = 400  # st.slider('size', 100, 600, 400, 50)
      cols = st.columns(4)
      for i in range(min(st.session_state.num_images, len(df_selected_cards))):
        card = df_selected_cards.iloc[i]
        with cols[i % 4]:
          col_num, col_link = st.columns(2)
          if language_cards == 'english':
            quantity = col_num.number_input(f"{card['Name']} {card['Set']} {card['#']}", min_value=0, value=st.session_state.selected_cards.get(f"{card['Name']} {card['Set']} {card['#']}", 0), key=f"quantity_{i}", max_value=4)
          elif language_cards == 'deutsch':
            quantity = col_num.number_input(f"{card['Name']} '{card['Name EN']}' {card['Set']} {card['#']}", min_value=0, value=st.session_state.selected_cards.get(f"{card['Name']} {card['Set']} {card['#']}", 0), key=f"quantity_{i}", max_value=4)

          # url = f'https://limitlesstcg.com/cards/de/{card['Set']}/{card['#']}'
          url = card['URL']
          col_link.link_button('go to card on limitlessTCG', url)
          st.image(url, width=iWidth)
          update_card_quantity(f"{card['Name']}|{card['Set']}|{card['#']}", quantity)

      if st.session_state.num_images < len(df_selected_cards):
        if st.button('load more'):
          load_more()
        st.write(f'Angezeigt: {min(st.session_state.num_images, len(df_selected_cards))} von {len(df_selected_cards)} Karten')
  else:
    st.write('No card found')

# Battlelog viewer
with tab2:
  st.title('Pokemon Trading Card Game - Battlelog Viewer')

  game_log = ''

  bfile_uploader = st.toggle('Load battlelog from textfile')
  if bfile_uploader:
    col1, col2 = st.columns(2)
    with col1:
      # File uploader for the game log
      uploaded_file = st.file_uploader('Upload battlelog', type=['txt'])

    with col2:
      saved_battlogs = load_saved_battlogs()
      selected_battlog = st.selectbox('Choose battlelog', saved_battlogs)

    if uploaded_file is not None:
      game_log = uploaded_file.getvalue().decode('utf-8')
    elif selected_battlog:
      battlelogfile = rf'{c.sBattlelogs_Folder}\{selected_battlog}'
      print(battlelogfile)
      with open(battlelogfile, 'r', encoding='utf-8') as _battlelog:
        game_log = _battlelog.read()
  else:
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
      print(player, color)
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
              for sName in lUniqueNames:
                if sName in sLine:
                  sName_final = sName
                  if f'{sName} ex' in sLine:
                    sName_final = f'{sName} ex'
                  elif f'{sName} VSTAR' in sLine:
                    sName_final = f'{sName} VSTAR'
                  elif f'{sName} V' in sLine:
                    sName_final = f'{sName} V'
                  sLine = sLine.replace(sName_final, f'**:blue-background[{sName_final}]**')
                  break
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
  # sDecklist = st.text_area('Paste decklist here')
  sDecklist = """Pokémon: 9
1 Rotom V LOR 177
  """
  """
2 Hisuian Braviary SIT 149
2 Munkidori TWM 95
4 Froslass TWM 53
2 Rufflet ASR 131 PH
1 Munkidori SFA 72
1 Bloodmoon Ursaluna ex TWM 222
4 Snorunt SIT 41
1 Mimikyu PR-SV 75
Trainer: 24
3 Irida ASR 147
1 Arven SVI 235
2 Switch Cart ASR 154
2 Nest Ball PAF 84 PH
1 Earthen Vessel SFA 96
1 Calamitous Wasteland PAL 175 PH
2 Arven PAF 235
1 Super Rod PAL 276
3 Iono PAF 237
1 Iono PAL 269
1 Penny PAF 239
1 Technical Machine: Devolution PAR 177
2 Night Stretcher SFA 61
1 Pokémon League Headquarters OBF 192 PH
1 Technical Machine: Evolution PAR 178
1 Artazon OBF 229
1 Lost Vacuum LOR 217
4 Buddy-Buddy Poffin TWM 223
1 Forest Seal Stone SIT 156
1 Nest Ball SVI 181
1 Rescue Board TEF 159
2 Counter Catcher PAR 264
1 Neutralization Zone SFA 60
1 Nest Ball SVI 255

Energy: 2
4 Basic {D} Energy SFA 98
2 Luminous Energy PAL 191

Total Cards: 60

  """

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

    col_decklist1, col_decklist2 = st.columns([5, 1])
    with col_decklist1:
      col_temp1, col_search_term_name = st.columns([1, 3])
      with col_temp1:
        search_term_name = st_keyup('Find card by name', key='name_decklist')
        print(f'{search_term_name = }')
      with col_search_term_name:
        search_term_name

      if search_term_name:
        df_result = df_orig[df_orig['Name'].str.contains(search_term_name, case=False, na=False)]

        event_2 = st.dataframe(
          df_result,
          use_container_width=True,
          hide_index=True,
          on_select='rerun',
          selection_mode='single-row',
        )

        with col_decklist2:
          if selected_card := event_2.selection.rows:
            df_selected_card = df_result.iloc[selected_card]
            name = df_selected_card['Name'].iloc[0]
            set = df_selected_card['Set'].iloc[0]
            num = df_selected_card['#'].iloc[0]
            url = df_selected_card['URL'].iloc[0]
            st.write(f'{name} {set} {num}')
            st.image(url, width=200)

            # st.write('vor Button')
            # st.write(dDecklist)
            if st.button('Add card to decklist'):
              dDecklist = add_card_to_decklist(dDecklist, name, set, num)
              st.session_state['bAdded_Card'] = True
              st.session_state['decklist'] = dDecklist
              # st.write('nach Button')
              # st.write(dDecklist)

    # Display the decklist
    display_decklist(dDecklist, not_found, num_columns)
    # st.write('vor Export')
    # st.write(dDecklist)
    # if st.button('print session state decklist'):
    #   st.write(st.session_state['decklist'])
    if st.button('Export decklist'):
      # st.write(st.session_state['decklist'])
      export_decklist(dDecklist)

print('st.session_state')
for k, v in st.session_state.items():
  print(k, f"'{v}'")
# print('\n\ndecklist', st.session_state['decklist'])
# print(st.session_state.selected_cards)
# st.write(st.session_state)
# st.write(st.session_state.selected_cards)







####################################### TESTS #######################################

# # Function to display the image on hover
# def display_image_on_hover(image_url, i):
#     # Generate unique class names for each image
#     hover_class = f'hoverable_{i}'
#     tooltip_class = f'tooltip_{i}'
#     image_popup_class = f'image-popup_{i}'

#     # Define the unique CSS for each image
#     hover_css = f'''
#         .{hover_class} {{
#             position: relative;
#             display: inline-block;
#             cursor: pointer;
#         }}
#         .{hover_class} .{tooltip_class} {{
#             opacity: 0;
#             position: absolute;
#             bottom: 100%;
#             left: 50%;
#             transform: translateX(-50%);
#             transition: opacity 0.5s;
#             background-color: rgba(0, 0, 0, 0.8);
#             color: #fff;
#             padding: 4px;
#             border-radius: 4px;
#             text-align: center;
#             white-space: nowrap;
#         }}
#         .{hover_class}:hover .{tooltip_class} {{
#             opacity: 1;
#         }}
#         .{image_popup_class} {{
#             position: absolute;
#             display: none;
#             background-image: none;
#             width: 200px;
#             height: 200px;
#         }}
#         .{hover_class}:hover .{image_popup_class} {{
#             display: block;
#             background-image: url({image_url});
#             background-size: cover;
#             z-index: 999;
#         }}
#     '''
#     tooltip_css = f"<style>{hover_css}</style>"

#     # Define the html for each image
#     image_hover = f'''
#         <div class="{hover_class}">
#             <a href="{image_url}">{image_url}</a>
#             <div class="{tooltip_class}">Image {i}</div>
#             <div class="{image_popup_class}"></div>
#         </div>
#     '''
    
#     # Write the dynamic HTML and CSS to the content container
#     st.markdown(f'<p>{image_hover}{tooltip_css}</p>', unsafe_allow_html=True)

# st.image("https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/ASR/ASR_018_R_EN_XS.png")
# st.markdown(
#     """
#     <style>
#     img {
#         cursor: pointer;
#         transition: all 5s ease-in-out;
#     }
#     img:hover {
#         transform: scale(2);
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# st.markdown("*Streamlit* is **really** ***cool***.")
# st.markdown('''
#     :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
#     :gray[pretty] :rainbow[colors] and :blue-background[highlight] text.''')
# st.markdown("Here's a bouquet &mdash;\
#             :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

# multi = '''If you end a line with two spaces,
# a soft return is used for the next line.

# Two (or more) newline characters in a row will result in a hard return.
# '''
# st.markdown(multi)

