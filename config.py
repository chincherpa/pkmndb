sBattlelogs_Folder = 'battlelogs_others'

lStandard_regulations = ['G', 'H', 'I']

lColumns_DE = ['Name DE', 'Evolves from DE', 'Ability DE', 'Ability text DE', 'Attack 1 name DE', 'Effect 1 DE', 'Attack 2 name DE', 'Effect 2 DE', 'URL DE']

lImportant_Actions = [
  'kampfunfähig',
  'gewonnen',
  'entwickelt',
  'Befehl vom Boss',
  'Preiskarte',

  'Knocked Out',
  'wins',
  'evolved',
  # "Boss's Orders",
  'Prize card.',
  'Prize cards.',
  'Entering Sudden Death.',
  'conceded.',
  ]

dImportant_Actions_colors = {
  # 'kampfunfähig': 'red',
  # 'gewonnen': 'red',
  # 'entwickelt': 'red',
  # 'Befehl vom Boss': 'red',
  # 'Preiskarte': 'red',

  'Knocked Out': 'red',
  'wins': 'gold',
  # 'evolved': 'red',
  # "Boss's Orders": 'red',
  'Prize card.': 'gold',
  'Prize cards.': 'gold',
  'Entering Sudden Death.': 'black',
}

dTranslations = {
  'deutsch': {
    'file': 'cards_de.csv',
    'encoding': 'cp1252',
    'find_in_names': 'Suche in Namen oder Attacken:',
    'find_in_evolves': "Suche in 'Entwickelt sich aus'",

    # Battlelog Viewer
    'energy': 'Energie',
    'damage': 'Schaden',
    'events': 'Wichtige Ereignisse',
    'gameplay': 'Spielverlauf',
    'knockout_pokemon': 'Verlor',
    'knockout': 'wurde kampfunfähig gemacht!',
    'played_energies': 'Energiekarten gespielt',
    'player_pattern': ' hat für die Starthand',
    'player_stistics': 'Spieler-Statistiken',
    'setup': 'Spielvorbereitung',
    'suddendeath': 'Sudden-Death',
    'statistics': 'Statistiken',
    'total_turns': 'Gesamtzüge',
    'turn_pattern': r'Zug von (\w+)',
    # 'turn_pattern': r'Zug von (.*?)',
    'turn': 'Zug',
    'turns_played': 'Züge gespielt',
    'winner_pattern': r'\b(\w+)\b(?=\s*hat\s*gewonnen)',
    'win': 'gewonnen',
  },
  'english': {
    'file': 'cards_en.csv',
    'encoding': 'utf-8',
    'find_in_names': 'Find in names or attacks:',
    'find_in_evolves': "Find in 'Evolves from'",

    # Battlelog Viewer
    'energy': 'Energy',
    'damage': 'damage',
    'events': 'Important events',
    'gameplay': 'Game play',
    'knockout_pokemon': 'Lost',
    'knockout': 'was Knocked Out!',
    'played_energies': 'Attached energies',
    'player_pattern': ' drew 7 cards for the opening hand',
    'player_stistics': 'Player statistics',
    'setup': 'Preparation',
    'suddendeath': 'Sudden Death',
    'statistics': 'Statistics',
    'total_turns': 'Total turns',
    'turn_pattern': r'Turn # \d+ - (.*?)\'s Turn',  #r"(\w+)'s Turn",
    'turn': 'Turn',
    'turns_played': 'Played',
    'winner_pattern': r'\b(\w+)\b(?=\s*wins)',
    'win': 'wins',
  },
}

lDecklistKeywords = ['Pokémon:', 'Trainer:', 'Energy:', 'Total Cards:', 'Energie:', 'Karten insgesamt:']
# sDecklistEntryPattern = r'(\d+) .+ ([A-Z]{3}) (\d+)' # without cardname
sDecklistEntryPattern = r'(\d+) (.+) ([A-Z]{3}) (\d+)'

# lEnergies = {
#   'Basic {D} Energy': 'Darkness Energy',
#   'Basic {X} Energy': 'Fighting Energy',
#   'Basic {G} Energy': 'Grass Energy',
#   'Basic {L} Energy': 'Lightning Energy',
#   'Basic {M} Energy': 'Metal Energy',
#   'Basic {P} Energy': 'Psychic Energy',
#   'Basic {F} Energy': 'Fire Energy',
#   'Basic {W} Energy': 'Water Energy'
# }