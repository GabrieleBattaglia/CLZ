# Collezioni Carica e salva su disco una raccolta di nomi univoci.
# Giugno 2017, inizio il porting a Python3
# giugno 2024, spostato su Github
# Aprile 2025, modifiche per caricamento .txt, gestione file, ordine memoria

import pickle
import os # Importato per verificare l'esistenza dei file
from GBUtils import dgt # Assumiamo che dgt gestisca l'input utente

print ("Collezioni 1.8 - 5 aprile 2013 / 17 aprile 2025\n-- by Gabriele Battaglia")
print ("\n- Nome della collezione: ", end="")
collection_name_input = dgt(smax=40)
collection_name_input = collection_name_input.lower()
collection_name_input = collection_name_input.strip()
collection_prefix = "CLZ-" + collection_name_input
gbd_file_path = collection_prefix + ".gbd"
txt_file_path = collection_prefix + ".txt"

collection_items = [] # Inizializza la lista vuota

# --- Blocco di Caricamento Modificato ---
# Priorità al file .gbd, poi al .txt
print(f"\n- Ricerca collezione '{collection_prefix}'...")
loaded_from = None
try:
    # Prova a caricare dal file .gbd (pickle)
    if os.path.exists(gbd_file_path):
        print(f"- Caricamento di {gbd_file_path} (pickle) in corso...")
        with open(gbd_file_path, "rb") as f_pickle_in:
            # Carica la lista così com'è (ordine preservato da salvataggi precedenti)
            collection_items = pickle.load(f_pickle_in)
        print(f"- Caricamento da {gbd_file_path} completato ({len(collection_items)} elementi).")
        loaded_from = 'gbd'
    # Se .gbd non esiste, prova a caricare dal file .txt
    elif os.path.exists(txt_file_path):
        print(f"- File {gbd_file_path} non trovato.")
        print(f"- Caricamento di {txt_file_path} (testo) in corso...")
        temp_items = set() # Usiamo un set per gestire duplicati iniziali
        try:
            # Apre il file txt in lettura con encoding utf-8
            with open(txt_file_path, "rt", encoding='utf-8') as f_text_in:
                for line in f_text_in:
                    # Processa ogni riga come un nuovo oggetto
                    item = line.strip()
                    if item: # Ignora righe vuote
                         item = item.capitalize()
                         temp_items.add(item)
            # Converte il set in lista e ORDINA dopo caricamento da TXT
            collection_items = sorted(list(temp_items))
            print(f"- Caricamento da {txt_file_path} completato. {len(collection_items)} elementi unici caricati e ordinati.")
            loaded_from = 'txt'
        except Exception as e:
            print(f"\a\n- Errore durante la lettura di {txt_file_path}: {e}")
            collection_items = []
    else:
        # Nessun file trovato, si crea una nuova collezione
        print(f"\a\n- Nessuna collezione ({gbd_file_path} o {txt_file_path}) trovata.")
        print(f"- Creazione di una nuova collezione '{collection_prefix}' in corso...")
        collection_items = []
except (pickle.UnpicklingError, IOError, EOFError) as e:
    print(f"\a\n\n- Errore durante il caricamento di {gbd_file_path}: {e}")
    print("- Potrebbe essere corrotto. Verrà creata una nuova collezione.")
    collection_items = []
except Exception as e: # Cattura altre eccezioni impreviste
    print(f"\a\n\n- Errore imprevisto durante il caricamento: {e}")
    collection_items = []

# --- Funzioni ---

def save_to_txt():
    """Salva la collezione corrente ORDINATA in un file .txt con encoding UTF-8."""
    if not collection_items:
        print("\n- La collezione è vuota, nessun file .txt salvato.")
        return
    # Crea una COPIA ORDINATA della lista per il salvataggio
    sorted_items_for_txt = sorted(collection_items)
    try:
        with open(txt_file_path, "wt", encoding='utf-8') as f_text_out:
            for item in sorted_items_for_txt:
                f_text_out.write(item + "\n")
        print(f"\n- File: {txt_file_path} salvato ({len(sorted_items_for_txt)} elementi, ordinati).")
    except IOError as e:
        print(f"\a\n- Errore durante il salvataggio di {txt_file_path}: {e}")
    except Exception as e:
        print(f"\a\n- Errore imprevisto durante il salvataggio TXT: {e}")

def show_menu():
    '''Scrive il menu delle scelte'''
    print ("\n----Menu----")
    print ("Inserisci questi comandi per ottenere le azioni corrispondenti.")
    print ("\tNota: i comandi vanno scritti in maiuscolo e preceduti da un punto")
    print (" - .ELI = Elimina un elemento dalla collezione (in base alla posizione attuale)")
    print (" - .UNI = Unisce una seconda collezione a quella aperta (risultato ordinato)")
    print (" - .LST = Lista degli oggetti (nell'ordine attuale)")
    print (" - .MEN = Visualizza questo menu")
    print (" - .TXT = Salva la lista ordinata in testo")
    print (" - Inserisci una riga vuota per concludere.")

def process_command(command):
    """Processa i comandi speciali inseriti dall'utente."""
    global collection_items # Necessario per modificare la lista globale

    if command == ".TXT":
        save_to_txt()
        return True
    if command == ".MEN":
        show_menu()
        return True
    if command == ".LST":
        list_items()
        return True
    if command == ".ELI":
        delete_item()
        return True
    if command == ".UNI":
        unite_collection()
        # Nota: unite_collection ora ordina collection_items
        return True
    return False # Non era un comando riconosciuto

def list_items():
    """Mostra una porzione della lista di elementi nell'ordine corrente."""
    if not collection_items:
        print("- La collezione è vuota.")
        return

    total_items = len(collection_items)
    print(f"- La collezione contiene {total_items} elementi (ordine attuale).")

    # Gestione input con valori di default sensati
    try:
        start_index = dgt(f"Elemento iniziale (1-{total_items}, default 1): ", "i", default=1)
        end_index = dgt(f"Elemento finale ({start_index}-{total_items}, default {min(start_index + 24, total_items)}): ", "i", default=min(start_index + 24, total_items))
    except ValueError:
        print("\a- Input numerico non valido.")
        return

    # Validazione e correzione indici (base 0 internamente)
    start_index = max(0, start_index - 1)
    end_index = min(total_items - 1, end_index - 1)
    start_index = min(start_index, end_index) # Assicura start <= end

    # Limita il numero di elementi visualizzati a 25 per volta
    if end_index - start_index > 24:
        end_index = start_index + 24
        print("- Visualizzazione limitata a 25 elementi.")

    print (f"\nLista oggetti da {start_index + 1} a {end_index + 1} (ordine attuale):")
    for j in range(start_index, end_index + 1):
        # Gestisce possibile errore se la lista viene modificata concorrentemente (improbabile qui)
        try:
            print (f"{j + 1}. {collection_items[j]}")
        except IndexError:
            print(f"{j+1}. Errore: indice fuori range")
            break # Interrompe se l'indice non è più valido
    print ("\n")


def delete_item():
    """Elimina un elemento dalla collezione specificando il numero (posizione attuale)."""
    global collection_items
    if not collection_items:
        print("- La collezione è vuota, impossibile eliminare.")
        return

    total_items = len(collection_items)
    try:
        item_number = dgt(f"Numero oggetto da eliminare (1-{total_items}, posizione attuale)? ", "i")
    except ValueError:
        print("\a- Input numerico non valido.")
        return

    # Validazione indice (base 0 internamente)
    index_to_delete = item_number - 1
    if 0 <= index_to_delete < total_items:
        item_to_delete = collection_items[index_to_delete]
        print(f"Elimino: {item_number}. {item_to_delete}")
        del collection_items[index_to_delete]
        # La lista mantiene il nuovo ordine dopo 'del'
    else:
        print(f"\a- Numero oggetto non valido. Deve essere tra 1 e {total_items}.")

def unite_collection():
    """Unisce un'altra collezione (da file .gbd) e ORDINA il risultato."""
    global collection_items
    print ("Nome della collezione da aggiungere?", end="")
    other_collection_name = dgt(smax=40)
    other_collection_name = other_collection_name.lower().strip()
    other_collection_prefix = "CLZ-" + other_collection_name
    other_gbd_path = other_collection_prefix + ".gbd"

    if not os.path.exists(other_gbd_path):
        print(f"\a\n\n- La collezione {other_gbd_path} non esiste... Operazione annullata")
        return

    try:
        print(f"- Caricamento di {other_gbd_path} in corso...")
        with open(other_gbd_path, "rb") as f_other_pickle:
            other_items = pickle.load(f_other_pickle)
        print("- Caricamento completato con successo.")

        original_count = len(collection_items)
        new_items_count = len(other_items)

        # Unione efficiente usando set per rimuovere duplicati
        combined_set = set(collection_items)
        combined_set.update(other_items)

        # Aggiorna la lista globale e la ORDINA
        collection_items = sorted(list(combined_set))

        added_count = len(collection_items) - original_count
        final_count = len(collection_items)

        print(f"Elementi presenti prima: {original_count}, elementi da collezione unita: {new_items_count}.")
        print(f"Elementi unici aggiunti: {added_count}. Elementi totali ora (ordinati): {final_count}.")

    except (pickle.UnpicklingError, IOError, EOFError) as e:
        print(f"\a\n- Errore durante il caricamento di {other_gbd_path}: {e}")
    except Exception as e:
        print(f"\a\n- Errore imprevisto durante l'unione: {e}")


# --- Ciclo Principale ---
show_menu()

while True: # Ciclo principale
    current_count = len(collection_items)
    # --- Prompt Ripristinato ---
    print (f"Oggetto {current_count + 1}: ", end="")
    user_input = dgt() # Legge l'input utente

    # Controlla se è un comando
    if user_input.startswith('.'):
        if process_command(user_input.upper()):
            continue # Se era un comando valido, ricomincia il ciclo

    # Se l'input è vuoto, termina il ciclo
    if not user_input:
        break

    # Processa l'input come un nuovo elemento
    new_item = user_input.strip().capitalize()

    if new_item == "": # Se dopo strip/capitalize è vuoto, ignora
         # Non stampo nulla per input vuoto processato
         continue

    # Controlla duplicati nella lista attuale (non ordinata)
    if new_item in collection_items:
        try:
            # Trova l'indice della prima occorrenza nella lista attuale
            item_index = collection_items.index(new_item)
            ins = len(collection_items) # Dimensione attuale

            # --- Logica Duplicati Ripristinata ---
            i = item_index # Rinomino per usare la logica originale
            if i < 2:
                j1 = 0
                if i > ins - 3: # Verifica se l'indice è vicino alla fine
                    j2 = ins - 1
                else:
                    j2 = i + 2
            elif i > ins - 3:
                j2 = ins - 1
                j1 = i - 2
            else:
                j1 = i - 2
                j2 = i + 2

            # Correzione per assicurare che j2 non superi l'indice massimo
            j2 = min(j2, ins - 1)
            # Correzione per assicurare che j1 non sia negativo
            j1 = max(0, j1)

            print(f"Elemento già presente in posizione {i + 1} ({float(i + 1) * 100 / ins:.2f}%)")
            output_parts = []
            for j in range(j1, j2 + 1):
                 # Assicurati che j sia un indice valido prima di accedere a collection_items[j]
                 if 0 <= j < len(collection_items):
                     if i == j:
                         output_parts.append(f"({collection_items[j]}).")
                     else:
                         output_parts.append(f"{collection_items[j]}")
                 else:
                     # Questo non dovrebbe accadere con le correzioni j1/j2, ma per sicurezza
                     print(f"Errore indice j={j} fuori range")

            print(", ".join(output_parts))
            print("\n")
            # --- Fine Logica Duplicati Ripristinata ---

        except ValueError:
             print(f"- '{new_item}' trovato con 'in' ma non con 'index'. Raro.")
        except Exception as e:
             print(f"- Errore nella gestione duplicato: {e}")
        continue # Passa alla prossima iterazione senza aggiungere

    # Aggiunge il nuovo elemento alla FINE della lista (ordine di inserimento)
    collection_items.append(new_item)
    # --- Rimosso collection_items.sort() ---
    print(f"- '{new_item}' aggiunto in posizione {len(collection_items)}. Totale: {len(collection_items)}")
    # Non serve 'continue' qui, il ciclo riparte

# --- Salvataggio Finale ---
# Salva la lista nell'ordine in cui si trova in memoria (ordine inserimento / post-UNI)
print(f"\n- Salvataggio finale della collezione in {gbd_file_path}...")
try:
    with open(gbd_file_path, "wb") as f_pickle_out:
        pickle.dump(collection_items, f_pickle_out, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"- Salvataggio completato ({len(collection_items)} elementi, ordine attuale).")
except IOError as e:
    print(f"\a\n- Errore durante il salvataggio finale di {gbd_file_path}: {e}")
except Exception as e:
    print(f"\a\n- Errore imprevisto durante il salvataggio finale: {e}")

print("\nArrivederci.")