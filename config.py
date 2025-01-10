sBattlelogs_Folder = 'battlelogs'

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
  'german': {
    'file': 'cards_de.csv',
    'encoding': 'cp1252',
    'hp': 'KP',

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
    'statistics': 'Statistiken',
    'total_turns': 'Gesamtzüge',
    'turn_pattern': r'Zug von (\w+)',
    'turn': 'Zug',
    'turns_played': 'Züge gespielt',
    'winner_pattern': r'\b(\w+)\b(?=\s*hat\s*gewonnen)',
    'win': 'gewonnen',
  },
  'english': {
    'file': 'cards_en.csv',
    'encoding': 'utf-8',
    'hp': 'HP',

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
    'statistics': 'Statistics',
    'total_turns': 'Total turns',
    'turn_pattern': r"(\w+)'s Turn",
    'turn': 'Turn',
    'turns_played': 'Played',
    'winner_pattern': r'\b(\w+)\b(?=\s*wins)',
    'win': 'wins',
  },
}