import sys
from time import sleep

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

lList = ['Null', 'Eins',  'Zwei',  'Drei',  'Vier',  'Fünf']

for idx, x in enumerate(lList):
    progress_bar(idx, len(lList))
    sleep(1)
