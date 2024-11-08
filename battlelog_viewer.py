import streamlit as st
import re
from datetime import datetime

def extract_players(preparation_text):
    """Extract player names from preparation text"""
    players = []
    for line in preparation_text.split('\n'):
        if 'hat Zahl für den Münzwurf' in line:
            players.append(re.search(r'(\w+) hat Zahl', line).group(1))
        elif 'hat den Münzwurf gewonnen' in line:
            winner = re.search(r'(\w+) hat den', line).group(1)
            if winner not in players:
                players.append(winner)
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
    player = re.search(r'Zug von (\w+)', turn_header).group(1)
    
    # Extract actions
    actions = [line.strip() for line in turn_text.split('\n')[1:] if line.strip()]
    
    return {
        'turn_number': turn_num,
        'player': player,
        'actions': actions
    }

def format_action(action):
    """Format action text with colored player names and appropriate styling"""
    colored_text = color_player_names(action)
    
    if "wurde kampfunfähig gemacht" in action:
        return f"**🔥 {colored_text}**"
    elif "hat gewonnen" in action:
        return f"### 🏆 {colored_text}"
    elif any(key in action.lower() for key in ["ist jetzt in der aktiven position"]):
        return f" 🆕 {action}"
    elif any(key in action.lower() for key in ["schadenspunkte"]):
        return f" 🗡️ {action}"
    elif any(key in action.lower() for key in ["preiskarte"]):
        return f" 🏅 {action}"
    elif any(key in action.lower() for key in ["ablagestapel"]):
        return f" 📥 {action}"
    elif any(key in action.lower() for key in ["gespielt"]):
        return f" 🎫 {action}"
    elif any(key in action.lower() for key in ["gemischt"]):
        return f" 🌀 {action}"
    elif any(key in action.lower() for key in ["hinzugefügt", "gezogen"]):
        return f" ➕ {action}"
    elif any(key in action.lower() for key in ["entwickelt", "energie", "eingesetzt"]):
        return f"- 🎯 {colored_text}"
    else:
        return f"- {colored_text}"

def main():
    st.set_page_config(page_title="Pokemon TCG Game Viewer", layout="wide")
    
    st.title("Pokemon Trading Card Game - Match Viewer")
    
    # Add file uploader for the game log
    uploaded_file = st.file_uploader("Spielprotokoll hochladen", type=['txt'])
    
    if uploaded_file is not None:
        game_log = uploaded_file.getvalue().decode('utf-8')
    else:
        # Sample game log for testing
        st.warning("Bitte laden Sie ein Spielprotokoll hoch.")
        return

    # Parse the game log
    preparation, turns = parse_game_log(game_log)
    
    # Extract players and assign colors
    players = extract_players(preparation)
    player_colors = get_player_colors(players)
    
    # Display player information
    st.markdown("### Spieler")
    cols = st.columns(len(players))
    for i, (player, color) in enumerate(player_colors.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="padding: 10px; border-radius: 5px; border: 2px solid {color};">
                <h4 style="color: {color}">{player}</h4>
            </div>
            """, unsafe_allow_html=True)
    
    # Display preparation phase with colored player names
    with st.expander("📝 Spielvorbereitung", expanded=True):
        for line in preparation.split('\n'):
            if line.strip():
                st.markdown(color_player_names(line, player_colors), unsafe_allow_html=True)
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["🎮 Spielverlauf", "📊 Statistiken"])
    
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
                <h3>Zug {turn_info['turn_number']} - <span style='color: {color}'>{player}</span></h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Display actions with colored player names
            for action in turn_info['actions']:
                st.markdown(format_action(action, player_colors), unsafe_allow_html=True)
    
    with tab2:
        # Calculate statistics
        total_turns = len(turns)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Gesamtzüge", total_turns)
        
        with col2:
            knockout_count = sum(1 for turn in turns for action in turn.split('\n') 
                               if "wurde kampfunfähig gemacht" in action)
            st.metric("Kampfunfähige Pokemon", knockout_count)
        
        with col3:
            energy_count = sum(1 for turn in turns for action in turn.split('\n') 
                             if "Energie" in action)
            st.metric("Energiekarten gespielt", energy_count)
        
        # Add a timeline of major events with colored player names
        st.subheader("Wichtige Ereignisse")
        events = []
        for turn in turns:
            turn_info = extract_turn_info(turn)
            for action in turn_info['actions']:
                if any(key in action for key in ["kampfunfähig", "gewonnen", "entwickelt"]):
                    events.append(f"Zug {turn_info['turn_number']}: {action}")
        
        for event in events:
            st.markdown(color_player_names(event, player_colors), unsafe_allow_html=True)

        # Add player statistics
        st.subheader("Spieler-Statistiken")
        cols = st.columns(len(players))
        
        for i, (player, color) in enumerate(player_colors.items()):
            player_turns = [turn for turn in turns if extract_turn_info(turn)['player'] == player]
            player_knockouts = sum(1 for turn in player_turns 
                                 for action in turn.split('\n') 
                                 if "wurde kampfunfähig gemacht" in action)
            
            with cols[i]:
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; border: 2px solid {color};">
                    <h4 style="color: {color}">{player}</h4>
                    <p>Züge gespielt: {len(player_turns)}</p>
                    <p>Pokemon kampfunfähig gemacht: {player_knockouts}</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()