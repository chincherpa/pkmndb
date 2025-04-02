from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import sys

from rich import print

sDateTime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
print(sDateTime)

r'''
Sub GetPic()
Dim fNameAndPath As Variant
Dim img As Picture

Dim aktiveZeile As Long
Dim wert1 As String
Dim wert5 As String
Dim wert10 As String
Dim zusammengesetzterWert As String


aktiveZeile = ActiveCell.Row
If aktiveZeile = 1 Then
    Exit Sub
End If
Name = Left(Cells(aktiveZeile, 1).Value, 31)
expansion = Cells(aktiveZeile, 22).Value
Number = Cells(aktiveZeile, 23).Value

zusammengesetzterWert = expansion & " " & Number & " " & Name

ActiveSheet.Pictures.Delete
fNameAndPath = "C:\Users\fv4tjay\Downloads\pkmn imgs\" & expansion & "\" & zusammengesetzterWert & ".png"
Set img = ActiveSheet.Pictures.Insert(fNameAndPath)

iRow = WorksheetFunction.Max(aktiveZeile - 10, 1)

With img
  .Left = ActiveSheet.Cells(aktiveZeile, 23).Left
  .Top = ActiveSheet.Cells(iRow, 23).Top
  .Height = ActiveSheet.Range("W2:W20").Height
  .Placement = 1
  .PrintObject = True
End With

With img
   .Left = ActiveSheet.Range("A3812").Left
   .Top = ActiveSheet.Range("A3812").Top
   .Height = ActiveSheet.Range("A3812:A3830").Height
   .Placement = 1
   .PrintObject = True
End With

End Sub

Private Sub Worksheet_SelectionChange(ByVal Target As Range)
GetPic
End Sub

Sub MehrereZeichenErsetzenImGesamtenBlatt()
Dim ws As Worksheet
Dim cell As Range
Dim replacements As Variant
Dim i As Integer

' Definiere die Zeichen, die ersetzt werden sollen, und ihre Entsprechungen
replacements = Array( _
    Array("Ã©", "e"), _
    Array("Ã—", "*"), _
    Array("Ã¼", "ü"), _
    Array("Ãœ", "Ü"), _
    Array("Ã¤", "ä"), _
    Array("Ã„", "Ä"), _
    Array("Ã¶", "ö"), _
    Array("Ã–", "Ö"), _
    Array("ÃŸ", "ß"), _
    Array("â™€", "male"), _
    Array("â™‚", "female") _
)

' Setze das aktive Arbeitsblatt
Set ws = ActiveSheet

' Durchlaufe jede Zelle im gesamten Blatt
For Each cell In ws.UsedRange
    If Not IsEmpty(cell.Value) Then
        For i = LBound(replacements) To UBound(replacements)
            cell.Value = Replace(cell.Value, replacements(i)(0), replacements(i)(1))
        Next i
    End If
Next cell

MsgBox "Ersetzen im gesamten Blatt abgeschlossen!"
End Sub

Sub WertAlsHyperlink()

Dim ws As Worksheet
Dim cell As Range
Dim cellvalue As String

For Each cell In Selection
    cellvalue = cell.Value
    ActiveSheet.Hyperlinks.Add Anchor:=cell, Address:=cellvalue, TextToDisplay:=cellvalue
Next cell

MsgBox "Ersetzen im gesamten Blatt abgeschlossen!"

End Sub
'''

def download_image(url, cardname, expansion, number):
  pass
  # file_name = f'{expansion} {number} {cardname}.png'
  # file_path = rf"C:/Users/fv4tjay/Downloads/pkmn imgs/{expansion}/{file_name}"
  # if not os.path.isfile(file_path):
  #   print(f'Downloading: expansion = |{expansion}| number = |{number}| card_name = |{card_name}|')
  #   # print(f'Downloading: {file_name}')
  #   response = requests.get(url)
  #   if response.status_code == 200:
  #     image_data = response.content

  #     with open(file_path, 'wb') as file:
  #       file.write(image_data)

def progress_bar(current, total, filename="", bar_length=40):
  """Eine Fortschrittsanzeige mit aktuellem Dateinamen."""
  fraction = current / total
  arrow = int(fraction * bar_length) * '█'
  padding = (bar_length - len(arrow)) * '░'
  percent = int(fraction * 100)
  # Dateianzeige auf maximale Länge begrenzen
  max_filename_length = 40
  if len(filename) > max_filename_length:
    display_filename = filename[:max_filename_length-3] + "..."
  else:
    display_filename = filename
  sys.stdout.write(f'\r[{arrow}{padding}] {percent}% ({current}/{total}) | {display_filename} ')
  sys.stdout.flush()
  if current == total:
    print("\n")

def split_attack(sAttack):
  # pattern = r"^(\w+)\s+([A-Za-zÄÖÜäöüß ]+)\s*(\d*\+??)$"
  pattern = r"^(\w+)\s+([A-Za-zÄÖÜäöüß \-]+)\s*(\d+[+×]?)?$"

  # Verarbeitung der Strings
  match = re.match(pattern, sAttack)
  if match:
    color, name, damage = match.groups()
    damage = damage if damage else ''
  else:
    color, name, damage = '', '', ''

  return color, name, damage

def translate_text(dReplacements, text):
  
  # Sort replacements by length (longest first) to avoid partial matches
  sorted_replacements = sorted(dReplacements.items(), key=lambda x: len(x[0]), reverse=True)
  
  for old_text, new_text in sorted_replacements:
    # Use word boundaries \b for whole words only where appropriate
    if old_text.isalpha():
      text = re.sub(r'\b' + re.escape(old_text) + r'\b', new_text, text)
    else:
      text = text.replace(old_text, new_text)
  
  return text

DOWNLOAD_ONLY = False

dReplacements = {
  # 'de':{
    'Drache': 'Dragon',
    'Elektro': 'Lightning',
    'Farblos': 'Colorless',
    'Feuer': 'Fire',
    'Finsternis': 'Darkness',
    'Kampf': 'Fighting',
    'Metall': 'Metal',
    'Pflanze': 'Grass',
    'Psycho': 'Psychic',
    'Wasser': 'Water',
    '[C]': 'Colorless',
    '[D]': 'Darkness',
    '[F]': 'Fighting',
    '[G]': 'Grass',
    '[L]': 'Lightning',
    '[M]': 'Metal',
    '[P]': 'Psychic',
    '[R]': 'Fire',
    '[W]': 'Water',
    'Schwäche:': '',
    'Weakness:': '',
    'Resistenz:': '',
    'Resistance:': '',
    'Rückzug:': '',
    'Retreat:': '',
    'keine': '',
    'none': '',
    'Basis': 'Basic',
    'Phase 1': 'Stage 1',
    'Phase 2': 'Stage 2',
    '(SP': 'PR-SW',
  # },
  # 'en':{
  #   'Weakness:': '',
  #   'Resistance:': '',
  #   'Retreat:': '',
  #   'none': '',
  # },
}

lAceSpecs = [
  'Dowsing Machine',
  'Scramble Switch',
  'Victory Piece',
  'Life Dew',
  'Rock Guard',
  'G Booster',
  'G Scope',
  'Master Ball',
  'Scoop Up Cyclone',
  'Awakening Drum',
  "Hero's Cape",
  'Master Ball',
  'Maximum Belt',
  'Prime Catcher',
  'Reboot Pod',
  'Hyper Aroma',
  'Scoop Up Cyclone',
  'Secret Box',
  'Survival Brace',
  'Unfair Stamp',
  'Dangerous Laser',
  'Neutralization Zone',
  'Poké Vital A',
  'Deluxe Bomb',
  'Grand Tree',
  'Sparkling Crystal',
  'Amulet of Hope',
  'Brilliant Blender',
  'Energy Search Pro',
  'Megaton Blower',
  'Miracle Headset',
  'Precious Trolley',
  'Scramble Switch',
  'Max Rod',
  'Maximum Belt',
  'Prime Catcher',
  'Scoop Up Cyclone',
  'Sparkling Crystal',
  'Treasure Tracker',
]

langs = ['de', 'en']
lHeader = [
  'Name DE',
  'Name',
  'Cardtype',
  'Type',
  'Tera',
  'HP',
  'Evolves from DE',
  'Evolves from',
  'Ability DE',
  'Ability',
  'Ability text DE',
  'Ability text',
  'Attack 1 cost',
  'Attack 1 name DE',
  'Attack 1 name',
  'Attack 1 damage',
  'Effect Attack 1 DE',
  'Effect Attack 1',
  'Attack 2 cost',
  'Attack 2 name DE',
  'Attack 2 name',
  'Attack 2 damage',
  'Effect Attack 2 DE',
  'Effect Attack 2',
  'Weakness',
  'Resistance',
  'Retreat cost',
  'Set',
  '#',
  'Regulation',
  'Set Name',
  'URL DE',
  'URL',
]

lFiles = [
      'ASR_DE.html',
      'BRS_DE.html',
      'CRZ_DE.html',
      'JTG_DE.html',
      'LOR_DE.html',
      'MEW_DE.html',
      'OBF_DE.html',
      'PAF_DE.html',
      'PAL_DE.html',
      'PAR_DE.html',
      'PGO_DE.html',
      'PR-SW_DE.html',
      'PRE_DE.html',
      'SCR_DE.html',
      'SFA_DE.html',
      'SIT_DE.html',
      'SSP_DE.html',
      'SVI_DE.html',
      'SVP_DE.html',
      'TEF_DE.html',
      'TWM_DE.html',
    ]

dCards_EN = {}

sEncoding = 'utf-8-sig'# if lang == 'de' else 'utf-8'
with open(f'cards_{sDateTime}.csv', mode='w', newline='', encoding=sEncoding) as file_csv:
  writer = csv.writer(file_csv, delimiter=';', )
  writer.writerow(lHeader)
# if 1:
  for idx, file_path in enumerate(lFiles):
    progress_bar(idx + 1, len(lFiles), file_path.split('_')[0])

    file_path = f'html/{file_path}'
    with open(file_path, 'r', encoding='utf-8') as file:
      html = file.read()

    # Englische
    file_path_en = f"{file_path.replace('_DE', '_EN')}"
    with open(file_path_en, 'r', encoding='utf-8') as file_en:
      html_en = file_en.read()

    soup_en = BeautifulSoup(html_en, 'html.parser')
    cards_en = soup_en.find_all('div', class_='card-page-main')
    dCards_EN = {}

    for card_en in cards_en:
      set_info_en = card_en.find('div', class_='prints-current-details').text.strip()
      expansion, _, _, number_rarity = set_info_en.split("\n")
      expansion_long = expansion.strip()
      expansion = expansion_long[-4:-1]
      expansion = translate_text(dReplacements, expansion)
      try:
        number, rarity = number_rarity.split(' · ')
        set_info_en = f'{expansion} {number.strip()}'
        number = number.strip().replace('#', '')
        rarity = rarity.strip()
      except ValueError:
        rarity = ''
        set_info_en = f'{expansion} {number_rarity.strip()}'
        number = number_rarity.replace('#', '').strip()
      # Kartentitel, Typ und KP
      name_section_en = card_en.find('p', class_='card-text-title').text.strip()
      s_clean_en = name_section_en.strip().split(' - ')

      sCard_name_en = s_clean_en[0].strip()

      # Angriffe und Effekte
      attacks_en = card_en.find_all('div', class_='card-text-attack')
      if attacks_en:
        attack1_en = attacks_en[0].find('p', class_='card-text-attack-info').text.strip()
        s_clean_en = ' '.join(attack1_en.split())
        attack1_en = ' '.join(s_clean_en.split(' ', 1))
        _, name_attack1_en, _ = split_attack(attack1_en)
        effect1_en = attacks_en[0].find('p', class_='card-text-attack-effect').text.strip()
        attack2_en = attacks_en[1].find('p', class_='card-text-attack-info').text.strip() if len(attacks_en) > 1 else ''
        s_clean_en = ' '.join(attack2_en.split())
        attack2_en = ' '.join(s_clean_en.split(' ', 1))
        _, name_attack2_en, _ = split_attack(attack2_en)
        effect2_en = attacks_en[1].find('p', class_='card-text-attack-effect').text.strip() if len(attacks_en) > 1 else ''
      else:
        name_attack1_en, effect1_en = '', ''
        name_attack2_en, effect2_en = '', ''

      # Type
      card_type_en = card_en.find('p', class_='card-text-type').text.strip()
      s_clean = ' '.join(card_type_en.split())

      card_type_en = ' '.join(s_clean.split(' ', 1)).replace('Pokémon - ', '')
      lCard_type_parts = card_type_en.split(' - Evolves from ')
      if len(lCard_type_parts) == 1:
        lCard_type_parts = card_type_en.split(' - Evolves from')

      sEvolves_from_en = ''
      if len(lCard_type_parts) == 1:
        card_type = lCard_type_parts[0]
      elif len(lCard_type_parts) == 2:
        card_type, sEvolves_from_en = lCard_type_parts
      else:
        print(f'Hier is komisch {set_info_en}')

      if sCard_name_en in lAceSpecs:
        card_type = f'{card_type} Ace Spec'

      abilities_en = card_en.find_all('div', class_='card-text-ability')
      if abilities_en:
        if len(abilities_en) >= 2:
          icap_num = 1
        else:
          icap_num = 0
        ability_en = abilities_en[icap_num].find('p', class_='card-text-ability-info').text.replace('Ability: ', '').replace('Δ', 'Mega').strip()
        ability_text_en = abilities_en[icap_num].find('p', class_='card-text-ability-effect').text.replace('Ability: ', '').strip()
      else:
        ability_en, ability_text_en = '', ''

      if 'Trainer' in card_type_en or 'Special Energy' in card_type_en:
        sections_en = card_en.find_all('div', class_='card-text-section')
        ability_text_en = sections_en[1].text.strip()
        ability_text_en = ability_text_en.split()
        ability_text_en = ' '.join(ability_text_en)

      img_tag_en = card_en.select_one('div.card-image img')
      img_url_en = img_tag_en.get('src')

      dCards_EN[set_info_en] = {
        'sCard_name_en': sCard_name_en,
        'ability_en': ability_en,
        'ability_text_en': ability_text_en,
        'name_attack1_en': name_attack1_en,
        'effect1_en': effect1_en,
        'name_attack2_en': name_attack2_en,
        'effect2_en': effect2_en,
        'card_type': card_type,
        'evolves_from_en': sEvolves_from_en,
        'img_url_en': img_url_en,
      }

    soup = BeautifulSoup(html, 'html.parser')
    sTitle = soup.title.string.replace(' – Limitless', '')
    cards = soup.find_all('div', class_='card-page-main')

    for card in cards:
      set_info = card.find('div', class_='prints-current-details').text.strip()
      expansion, _, _, number_rarity = set_info.split("\n")
      expansion_long = expansion.strip()
      expansion = expansion_long[-4:-1]
      expansion = translate_text(dReplacements, expansion)
      try:
        number, rarity = number_rarity.split(' · ')
        set_info = f'{expansion} {number.strip()}'
        number = number.strip().replace('#', '')
        rarity = rarity.strip()
      except ValueError:
        rarity = ''
        set_info = f'{expansion} {number_rarity.strip()}'
        number = number_rarity.replace('#', '').strip()

  ####### Image Download
      card_name = card.find('span', class_='card-text-name').text.strip()
      img_tag = card.select_one('div.card-image img')
      img_url = img_tag.get('src')
      if DOWNLOAD_ONLY:
        download_image(img_url, card_name, expansion, number)
        continue

  ####### Daten in CSV-Datei speichern
      # Kartentitel, Typ und KP
      name_section = card.find('p', class_='card-text-title').text.strip()
      s_clean = name_section.strip().split(' - ')

      if len(s_clean) == 3:
        # Name, Typ und KP extrahieren und bereinigen
        sCard_name = s_clean[0].strip()
        sTyp = s_clean[1].strip()
        sKP = s_clean[2].strip().replace(' KP', '').replace(' HP', '')
      elif len(s_clean) == 2:
        sCard_name = s_clean[0].strip() 
        sTyp = s_clean[1].strip()
        sKP = ''
      else:
        sCard_name = s_clean[0]
        sTyp = ''
        sKP = ''

      # Type
      card_type = card.find('p', class_='card-text-type').text.strip()
      s_clean = ' '.join(card_type.split())

      card_type = ' '.join(s_clean.split(' ', 1)).replace('Pokémon - ', '')
      lCard_type_parts = card_type.split(' - Entwickelt sich aus ')
      if len(lCard_type_parts) == 1:
        lCard_type_parts = card_type.split(' - Entwickelt sich aus')
      if len(lCard_type_parts) == 1:
        lCard_type_parts = card_type.split(' - Evolves from ')
      if len(lCard_type_parts) == 1:
        lCard_type_parts = card_type.split(' - Evolves from')

      sEvolves_from = ''
      if len(lCard_type_parts) == 1:
        card_type = lCard_type_parts[0]
      elif len(lCard_type_parts) == 2:
        card_type, sEvolves_from = lCard_type_parts
      else:
        print(f'Hier is komisch {set_info}')

      if sCard_name in lAceSpecs:
        card_type = f'{card_type} Ace Spec'

      # Ability
      abilities = card.find_all('div', class_='card-text-ability')
      sTera = ''
      if abilities:
        if len(abilities) >= 2:
          icap_num = 1
          if abilities[0].find('p', class_='card-text-ability-info').text.replace('Fähigkeit: ', '').replace('Ability: ', '').replace('Δ', 'Mega').strip() == 'Terakristall':
            sTera = 'Tera'
        else:
          icap_num = 0
        ability = abilities[icap_num].find('p', class_='card-text-ability-info').text.replace('Fähigkeit: ', '').replace('Ability: ', '').replace('Δ', 'Mega').strip()
        ability_text = abilities[icap_num].find('p', class_='card-text-ability-effect').text.replace('Fähigkeit: ', '').replace('Ability: ', '').strip()
      else:
        ability, ability_text = '', ''

      if 'Trainer' in card_type or 'Spezial-Energie' in card_type:
        sections = card.find_all('div', class_='card-text-section')
        ability_text = sections[1].text.strip()

      # Attacks and effects DE
      attacks = card.find_all('div', class_='card-text-attack')
      if attacks:
        attack1 = attacks[0].find('p', class_='card-text-attack-info').text.strip()
        # if number == '257':
        #   print(f'{attack1 = }')
        s_clean = ' '.join(attack1.split())
        attack1 = ' '.join(s_clean.split(' ', 1))
        color_attack1, name_attack1, damage_attack1 = split_attack(attack1)
        # if number == '257':
        #   print(f'{attack1 = }')
        #   print(f'{s_clean = }')
        #   print(split_attack(attack1))
        effect1 = attacks[0].find('p', class_='card-text-attack-effect').text.strip()
        attack2 = attacks[1].find('p', class_='card-text-attack-info').text.strip() if len(attacks) > 1 else ''
        s_clean = ' '.join(attack2.split())
        attack2 = ' '.join(s_clean.split(' ', 1))
        color_attack2, name_attack2, damage_attack2 = split_attack(attack2)
        effect2 = attacks[1].find('p', class_='card-text-attack-effect').text.strip() if len(attacks) > 1 else ''
      else:
        attack1, effect1, color_attack1, name_attack1, damage_attack1 = '', '', '', '', ''
        attack2, effect2, color_attack2, name_attack2, damage_attack2 = '', '', '', '', ''

      # Schwäche, Resistenz und Rückzug
      weakness, resistance, retreat = '', '', ''
      if txt_wrr := card.find('p', class_='card-text-wrr'):
        wrr_section = txt_wrr.text.strip().split('\n')
        weakness = translate_text(dReplacements, wrr_section[0]).strip()
        resistance = translate_text(dReplacements, wrr_section[1]).strip()
        retreat = translate_text(dReplacements, wrr_section[2]).strip()

      regulation_mark_div = card.find('div', class_='regulation-mark')
      regulation_text = regulation_mark_div.get_text(strip=True)
      sRegulation = regulation_text.split('•')[0].strip().replace(' Regelzeichen', '').replace(' Regulation Mark', '')

      # In die CSV-Datei schreiben
      # if lang == 'de':
      lResult_str = [
          "sCard_name",
          "dCards_EN[set_info]['sCard_name_en']",
          "dCards_EN[set_info]['card_type']",
          "# translate_text(dReplacements, card_type)",
          "# sTyp",
          "translate_text(dReplacements, sTyp)",
          "sTera",
          "sKP",
          "sEvolves_from",
          "dCards_EN[set_info]['evolves_from_en']",
          "ability",
          "dCards_EN[set_info]['ability_en']",
          "ability_text",
          "dCards_EN[set_info]['ability_text_en']",
          "color_attack1",
          "name_attack1",
          "dCards_EN[set_info]['name_attack1_en']",
          "damage_attack1",
          "effect1",
          "dCards_EN[set_info]['effect1_en']",
          "color_attack2",
          "name_attack2",
          "dCards_EN[set_info]['name_attack2_en']",
          "damage_attack2",
          "effect2",
          "dCards_EN[set_info]['effect2_en']",
          "# weakness",
          "translate_text(dReplacements, weakness)",
          "# resistance",
          "translate_text(dReplacements, resistance)",
          "retreat",
          "# expansion",
          "translate_text(dReplacements, expansion)",
          "number",
          "sRegulation",
          "sTitle",
          "img_url",
          "dCards_EN[set_info]['img_url_en']",
        ]

      lResult = [
          sCard_name,
          dCards_EN[set_info]['sCard_name_en'],
          dCards_EN[set_info]['card_type'],
          # translate_text(dReplacements, card_type),
          # sTyp,
          translate_text(dReplacements, sTyp),
          sTera,
          sKP,
          sEvolves_from,
          dCards_EN[set_info]['evolves_from_en'],
          ability,
          dCards_EN[set_info]['ability_en'],
          ability_text,
          dCards_EN[set_info]['ability_text_en'],
          color_attack1,
          name_attack1,
          dCards_EN[set_info]['name_attack1_en'],
          damage_attack1,
          effect1,
          dCards_EN[set_info]['effect1_en'],
          color_attack2,
          name_attack2,
          dCards_EN[set_info]['name_attack2_en'],
          damage_attack2,
          effect2,
          dCards_EN[set_info]['effect2_en'],
          # weakness,
          translate_text(dReplacements, weakness),
          # resistance,
          translate_text(dReplacements, resistance),
          retreat,
          # expansion,
          translate_text(dReplacements, expansion),
          number,
          sRegulation,
          sTitle,
          img_url,
          dCards_EN[set_info]['img_url_en'],
        ]

      # if number == '159':
      #   print(dict(zip(lHeader, lResult)))

      # else:
      #   lResult = [
      #     sCard_name,
      #     card_type,
      #     sTyp,
      #     sTera,
      #     sKP,
      #     sEvolves_from,
      #     ability,
      #     ability_text,
      #     color_attack1,
      #     name_attack1,
      #     damage_attack1,
      #     effect1,
      #     color_attack2,
      #     name_attack2,
      #     damage_attack2,
      #     effect2,
      #     weakness,
      #     resistance,
      #     retreat,
      #     expansion,
      #     number,
      #     sRegulation,
      #     sTitle,
      #     img_url
      #     ]

      # print(f'{sCard_name} {card_type} {expansion} {number}')

      # if not WRITE_TO_CSV:
      #   print(f'{sCard_name = }')
      #   print(f'{card_type = }')
      #   print(f'{sTyp = }')
      #   print(f'{sKP = }')
      #   print(f'{color_attack1 = }')
      #   print(f'{name_attack1 = }')
      #   print(f'{damage_attack1 = }')
      #   print(f'{effect1 = }')
      #   print(f'{color_attack2 = }')
      #   print(f'{name_attack2 = }')
      #   print(f'{damage_attack2 = }')
      #   print(f'{effect2 = }')
      #   print(f'{weakness = }')
      #   print(f'{resistance = }')
      #   print(f'{retreat = }')
      #   print(f'{expansion = }')
      #   print(f'{number = }')
      #   print('-' * 40)

      writer.writerow(lResult)
      # print(*lResult, sep='\n')
      # input('next')

print('DONE')
