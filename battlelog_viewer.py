import os
import re

import streamlit as st
from rich import print

from config import lImportant_Actions, dTranslations

def get_language(text):
    global sLanguage
    sLanguage = ['English', 'German'][text.split('\n')[0] == 'Vorbereitung']

def load_saved_battlogs():
    saved_selections = ['']
    saved_selections = saved_selections + [f'{battlelog}.txt' for battlelog in os.listdir('battlelogs') if battlelog.endswith('.txt')]
    return [os.path.splitext(f)[0] for f in saved_selections]

def extract_players(preparation_text):
    players = []
    lines = preparation_text.split('\n')

    for line in lines:
        if dTranslations[sLanguage]['player_pattern'] in line:
            player = line.split(dTranslations[sLanguage]['player_pattern'])[0].strip()
            players.append(player)
    print(f'Found these {players = }')
    return players

def get_player_colors(players):
    """Assign colors to players"""
    colors = ["#FF4B4B", "#4B8BFF"]  # Rot und Blau
    return {player: color for player, color in zip(players, colors)}

def color_player_names(text, player_colors):
    """Replace player names with colored versions"""
    for player, color in player_colors.items():
        text = text.replace(player, f"<span style='color: {color}; font-weight: bold;'>{player}</span>")
    return text

def find_last_item(lst):
    """
    Find the last item in the list.
    """
    true_indices = [x for x in lst if x]
    return true_indices[-1]

def get_winner(text):
    winner = 'not found'
    last_line = find_last_item(text.split('\n'))
    print(f'{last_line = }')
    # Suche nach dem Muster
    match = re.search(dTranslations[sLanguage]['winner_pattern'], text)
    if match:
        winner = match.group(1)
        print(f'{winner = }')
    return winner

def parse_game_log(log_text):
    # Split into preparation and turns
    parts = log_text.split("\n\nTurn #")
    preparation = parts[0]
    turns = ["Turn #" + turn for turn in parts[1:]]

    return preparation, turns

def extract_turn_info(turn_text):
    # Extract turn number and player
    turn_header = turn_text.split('\n')[0]
    turn_num = int(re.search(r'Turn # (\d+)', turn_header).group(1))
    player = re.search(dTranslations[sLanguage]['turn_pattern'], turn_header).group(1)

    # Extract actions
    actions = [line.strip() for line in turn_text.split('\n')[1:] if line.strip()]

    return {
        'turn_number': turn_num,
        'player': player,
        'actions': actions
    }

def format_action(action, player_colors):
    """Format action text with colored player names and appropriate styling"""
    colored_text = color_player_names(action, player_colors)

    if dTranslations[sLanguage]['knockout'] in action:
        return f"**🔥 {colored_text}**"
    elif dTranslations[sLanguage]['win'] in action:
        return f"### 🏆 {colored_text}"
    elif any(key in action.lower() for key in ['ist jetzt in der aktiven position', 'is now in the Active Spot']):
        return f' 🆕 {action}'
    elif any(key in action.lower() for key in ['schadenspunkte', 'damage']):
        return f' 🗡️ {action}'
    elif any(key in action.lower() for key in ['preiskarte', 'prize card']):
        return f' 🏅 {action}'
    elif any(key in action.lower() for key in ['ablagestapel', 'discarded']):
        return f' 📥 {action}'
    elif any(key in action.lower() for key in ['gespielt', 'played']):
        return f' 🎫 {action}'
    elif any(key in action.lower() for key in ['gemischt', 'shuffled']):
        return f' 🌀 {action}'
    elif any(key in action.lower() for key in ['hinzugefügt', 'gezogen', 'drew', 'drawn']):
        return f' ➕ {action}'
    elif any(key in action.lower() for key in ['entwickelt', 'energie', 'eingesetzt', 'evolved', 'energy', 'used']):
        return f'- 🎯 {colored_text}'
    else:
        return f'- {colored_text}'

def main():
    # st.set_page_config(page_title='Pokemon TCG Game Viewer', layout='wide')
    
    st.title('Pokemon Trading Card Game - Match Viewer')
    
    bfile_uploader = st.toggle('Load battlelog from file')
    if bfile_uploader:
        col1, col2 = st.columns(2)
        with col1:
            # File uploader for the game log
            uploaded_file = st.file_uploader("Upload battlelog", type=['txt'])

        with col2:
            saved_battlogs = load_saved_battlogs()
            selected_battlog = st.selectbox("Choose battlelog", saved_battlogs)

        if uploaded_file is not None:
            game_log = uploaded_file.getvalue().decode('utf-8')
        elif selected_battlog:
            battlelogfile = rf'battlelogs\{selected_battlog}'
            print(battlelogfile)
            with open(battlelogfile, 'r', encoding='utf-8') as _battlelog:
                game_log = _battlelog.read()
        else:
            st.warning("Bitte laden Sie ein Spielprotokoll hoch.")
            return
    else:
        game_log = st.text_area('Battlelog here')

    if not game_log:
        return

    get_language(game_log)

    # Parse the game log
    preparation, turns = parse_game_log(game_log)
    winner = get_winner(game_log)

    # Extract players and assign colors
    players = extract_players(preparation)
    print(f'{players = }')
    player_colors = get_player_colors(players)
    print(f'{player_colors = }')

    # Display player information
    st.markdown('### Players')
    cols = st.columns(2)
    for i, (player, color) in enumerate(player_colors.items()):
        with cols[i]:
            if player == winner:
                st.markdown(f'''
                <div style="padding: 10px; border-radius: 5px; border: 2px solid {color};">
                    <h4 style="color: {color}">{player}</h4>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div style="padding: 10px; border-radius: 5px; border: 2px solid {color}; background-color:gold">
                    <h4 style="color: {color}">{player}</h4>
                </div>
                ''', unsafe_allow_html=True)

    # Display preparation phase with colored player names
    with st.expander(f"📝 {dTranslations[sLanguage]['setup']}", expanded=True):
        for line in preparation.split('\n'):
            if line.strip():
                st.markdown(color_player_names(line, player_colors), unsafe_allow_html=True)

    # Create tabs for different views
    tab1, tab2 = st.tabs([f"🎮 {dTranslations[sLanguage]['gameplay']}", f"📊 {dTranslations[sLanguage]['statistics']}"])

    with tab1:
        # Display turns
        for turn in turns:
            turn_info = extract_turn_info(turn)
            player = turn_info['player']
            color = player_colors[player]
            light_color = f"{color}22"  # Add transparency for lighter background
            
            st.markdown(f"""
            <div style="background: linear-gradient(to right, {light_color}, white);
                        padding: 15px; border-radius: 10px; margin: 10px 0;
                        border-left: 5px solid {color};">
                <h3>{dTranslations[sLanguage]['turn']} {turn_info['turn_number']} - <span style='color: {color}'>{player}</span></h3>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f'{dTranslations[sLanguage]['turn']} {turn_info['turn_number']}', True):
                # Display actions with colored player names
                for action in turn_info['actions']:
                    st.markdown(format_action(action, player_colors), unsafe_allow_html=True)

    with tab2:
        # Calculate statistics
        total_turns = len(turns)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(dTranslations[sLanguage]['total_turns'], total_turns)

        with col2:
            knockout_count = sum(1 for turn in turns for action in turn.split('\n') 
                               if dTranslations[sLanguage]['knockout'] in action)
            st.metric(dTranslations[sLanguage]['knockout_pokemon'], knockout_count)

        with col3:
            energy_count = sum(1 for turn in turns for action in turn.split('\n') 
                             if dTranslations[sLanguage]['energy'] in action)
            st.metric(dTranslations[sLanguage]['played_energies'], energy_count)

        # Add a timeline of major events with colored player names
        st.subheader(dTranslations[sLanguage]['events'])
        events = []
        for turn in turns:
            turn_info = extract_turn_info(turn)
            for action in turn_info['actions']:
                if any(key in action for key in lImportant_Actions):
                    events.append(f"{dTranslations[sLanguage]['turn']} {turn_info['turn_number']}: {action}")

        for event in events:
            st.markdown(color_player_names(event, player_colors), unsafe_allow_html=True)

        # Add player statistics
        st.subheader(dTranslations[sLanguage]['player_stistics'])
        cols = st.columns(len(players))

        for i, (player, color) in enumerate(player_colors.items()):
            player_turns = [turn for turn in turns if extract_turn_info(turn)['player'] == player]
            player_knockouts = sum(1 for turn in player_turns
                                 for action in turn.split('\n')
                                 if dTranslations[sLanguage]['knockout'] in action)

            with cols[i]:
                st.markdown(f'''
                <div style="padding: 10px; border-radius: 5px; border: 2px solid {color};">
                    <h4 style="color: {color}">{player}</h4>
                    <p>{dTranslations[sLanguage]['turns_played']}: {len(player_turns)}</p>
                    <p>{dTranslations[sLanguage]['knockout_pokemon']}: {player_knockouts}</p>
                </div>
                ''', unsafe_allow_html=True)

if __name__ == '__main__':
    main()