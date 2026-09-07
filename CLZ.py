# CLZ, Collezioni. Raccolta di nomi univoci salvata su disco.
# Giugno 2017, inizio del porting a Python 3.
# Giugno 2024, spostato su GitHub.
# Aprile 2025, caricamento da testo, gestione file, ordine di memoria.
# 7 settembre 2026, versione 2.0.0: archivio in JSON, salvataggio atomico
#   dopo ogni modifica, comandi sicuri e messaggi accessibili.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto)

import json
import os
import pickle
import string
import sys

from GBUtils import Acusticator, dgt, manuale, menu

VERSIONE = "2.0.0"
RELEASE_DATE = "7 settembre 2026"

# I percorsi sono ancorati alla cartella del programma, non a quella di
# lavoro, cosi' le collezioni sono le stesse da qualunque cartella si parta.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caratteri che Windows non ammette nei nomi di file.
VIETATI = '<>:"/\\|?*'

# Quanti elementi si elencano per volta e quanti se ne mostrano
# attorno a un duplicato.
PAGINA = 25
CONTORNO = 2

COMANDI = {
    ".eli": "Elimina un elemento",
    ".lst": "Elenca gli elementi",
    ".men": "Rilegge questo menu",
    ".txt": "Salva la lista ordinata in testo",
    ".uni": "Unisce un'altra collezione",
    ".gui": "Guida di CLZ",
}

GUIDA = """Guida di CLZ, Collezioni.

Che cosa fa
CLZ tiene una raccolta di nomi univoci: parole,
cognomi, sigle, quello che vuoi. Ogni elemento
compare una volta sola, e la collezione conserva
l'ordine in cui l'hai costruita.

Come si usa
Al prompt digiti un elemento e premi INVIO: se
non c'e' viene aggiunto in fondo, se c'e' gia'
CLZ te lo dice, con la posizione e gli elementi
che gli stanno attorno.
Una riga vuota chiude il programma.

I comandi cominciano con un punto e sono:
.ELI elimina un elemento indicando la sua
     posizione attuale;
.LST elenca gli elementi, venticinque per volta;
.MEN rilegge l'elenco dei comandi;
.TXT salva la collezione ordinata in un file di
     testo, accanto a quello della collezione;
.UNI unisce un'altra collezione a questa. Il
     risultato viene riordinato alfabeticamente,
     quindi l'ordine di inserimento va perduto;
.GUI mostra questa guida.
Un comando scritto male non viene mai aggiunto
alla collezione: CLZ lo segnala e basta.

Dove finiscono i dati
Ogni collezione vive in un file CLZ-nome.json
accanto al programma. Il salvataggio avviene
dopo ogni modifica, quindi non c'e' niente da
perdere chiudendo la finestra.
Della versione precedente resta sempre una copia
con estensione .bak.

Le vecchie collezioni
I file .gbd delle versioni fino alla 1.9 erano in
formato pickle, che all'apertura esegue il codice
contenuto nel file. Alla prima apertura CLZ li
converte in JSON una volta sola e li lascia dove
sono, senza toccarli.
"""


def suona(nome):
    """Fa sentire un preset della collezione condivisa.
    Se la scheda audio non c'e' o non risponde, il programma prosegue in
    silenzio: un suono mancato non e' una ragione per fermare il lavoro.
    """
    try:
        Acusticator.play(nome)
    except (OSError, RuntimeError, ImportError) as e:
        print(f"Audio non disponibile: {e}", file=sys.stderr)


def nome_valido(nome):
    """Ripulisce il nome della collezione dai caratteri vietati"""
    pulito = "".join(c for c in nome if c not in VIETATI).strip()
    return pulito


def percorsi(nome):
    """Restituisce i quattro percorsi della collezione che ha quel nome"""
    prefisso = os.path.join(BASE_DIR, "CLZ-" + nome)
    return {
        "json": prefisso + ".json",
        "bak": prefisso + ".json.bak",
        "tmp": prefisso + ".json.tmp",
        "gbd": prefisso + ".gbd",
        "txt": prefisso + ".txt",
    }


def lista_di_stringhe(dati):
    """Dice se cio' che si e' letto e' davvero una lista di stringhe"""
    return isinstance(dati, list) and all(isinstance(x, str) for x in dati)


def leggi_json(percorso):
    """Legge una collezione in JSON.
    Restituisce la lista, oppure None se il file c'e' ma non si legge.
    """
    try:
        with open(percorso, "r", encoding="utf-8") as f:
            dati = json.load(f)
    except (OSError, ValueError) as e:
        print("Non riesco a leggere la collezione.")
        print(f"Motivo: {e}")
        return None
    if not lista_di_stringhe(dati):
        print("Il file non contiene una collezione:")
        print("dentro non c'e' un elenco di parole.")
        return None
    return dati


def leggi_gbd(percorso):
    """Legge una vecchia collezione in formato pickle.
    Restituisce la lista, oppure None se non si riesce a leggerla.
    """
    try:
        with open(percorso, "rb") as f:
            dati = pickle.load(f)
    except (OSError, ValueError, pickle.UnpicklingError, EOFError, AttributeError) as e:
        print("Non riesco a leggere la vecchia collezione.")
        print(f"Motivo: {e}")
        return None
    if not lista_di_stringhe(dati):
        print("Il vecchio file non contiene un elenco")
        print("di parole.")
        return None
    return dati


def leggi_txt(percorso):
    """Estrae le parole da un file di testo, una per ogni sequenza di
    caratteri separata da spazi, ripulita dalla punteggiatura ai bordi.
    Restituisce la lista ordinata, oppure None se il file non si legge.
    """
    trovate = set()
    try:
        with open(percorso, "r", encoding="utf-8") as f:
            for riga in f:
                for parola in riga.split():
                    pulita = parola.strip(string.punctuation)
                    if pulita:
                        trovate.add(pulita.capitalize())
    except (OSError, UnicodeDecodeError) as e:
        print("Non riesco a leggere il file di testo.")
        print(f"Motivo: {e}")
        return None
    return sorted(trovate)


def salva(elementi, vie):
    """Scrive la collezione in JSON.
    Passa da un file temporaneo e poi lo mette al posto dell'archivio con
    os.replace, che e' atomico: se qualcosa va storto la versione
    precedente resta intatta, e viene comunque conservata come .bak.
    Restituisce True se il salvataggio e' riuscito.
    """
    try:
        with open(vie["tmp"], "w", encoding="utf-8") as f:
            json.dump(elementi, f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(vie["json"]):
            os.replace(vie["json"], vie["bak"])
        os.replace(vie["tmp"], vie["json"])
    except OSError as e:
        suona("ronzio_di_errore_di_sistema")
        print(f"Errore nel salvataggio: {e}")
        print("La collezione precedente non e' stata")
        print("toccata.")
        return False
    return True


def carica(vie):
    """Trova e carica la collezione.
    Prova nell'ordine il JSON, la vecchia collezione pickle da convertire e
    il file di testo. Se un file esiste ma non si legge, si ferma e
    restituisce None: cosi' nessun archivio illeggibile viene sostituito da
    una collezione vuota.
    """
    if os.path.exists(vie["json"]):
        print("Carico la collezione.")
        return leggi_json(vie["json"])
    if os.path.exists(vie["gbd"]):
        print("Trovata una collezione vecchia.")
        print("La converto nel nuovo formato.")
        elementi = leggi_gbd(vie["gbd"])
        if elementi is None:
            return None
        if not salva(elementi, vie):
            return None
        print(f"Convertiti {len(elementi)} elementi.")
        print("Il vecchio file resta dov'e', intatto.")
        return elementi
    if os.path.exists(vie["txt"]):
        print("Trovato un file di testo.")
        print("Ne estraggo le parole.")
        elementi = leggi_txt(vie["txt"])
        if elementi is None:
            return None
        print(f"Estratte {len(elementi)} parole diverse,")
        print("in ordine alfabetico.")
        return elementi
    print("Nessuna collezione con questo nome.")
    print("Ne comincio una nuova.")
    return []


def elenca(elementi):
    """Mostra una porzione della collezione, nell'ordine attuale"""
    if not elementi:
        print("La collezione e' vuota.")
        return
    totale = len(elementi)
    print(f"La collezione contiene {totale} elementi.")
    primo = dgt(f"Primo elemento, da 1 a {totale}: ", kind="i", imin=1, imax=totale, default=1)
    ultimo_pre = min(primo + PAGINA - 1, totale)
    ultimo = dgt(f"Ultimo elemento, da {primo} a {totale}: ", kind="i", imin=primo, imax=totale, default=ultimo_pre)
    if ultimo - primo + 1 > PAGINA:
        ultimo = primo + PAGINA - 1
        print(f"Ne mostro {PAGINA} per volta.")
    print(f"Elementi da {primo} a {ultimo}:")
    for j in range(primo - 1, ultimo):
        print(f"{j + 1}. {elementi[j]}")


def elimina(elementi, vie):
    """Toglie un elemento indicato per posizione attuale"""
    if not elementi:
        print("La collezione e' vuota.")
        return
    totale = len(elementi)
    n = dgt(f"Quale elimino, da 1 a {totale}? ", kind="i", imin=1, imax=totale)
    tolto = elementi.pop(n - 1)
    print(f"Eliminato {n}, {tolto}.")
    print(f"Restano {len(elementi)} elementi.")
    suona("timbratura")
    salva(elementi, vie)


def unisci(elementi, vie):
    """Aggiunge a questa collezione il contenuto di un'altra.
    Il risultato viene riordinato alfabeticamente, come nelle versioni
    precedenti: l'ordine di inserimento della collezione aperta va perduto.
    """
    nome = nome_valido(dgt("Nome della collezione da unire: ", kind="s", smin=1, smax=40).lower())
    if not nome:
        print("Nome non valido, non faccio nulla.")
        return elementi
    altre_vie = percorsi(nome)
    if os.path.exists(altre_vie["json"]):
        altri = leggi_json(altre_vie["json"])
    elif os.path.exists(altre_vie["gbd"]):
        altri = leggi_gbd(altre_vie["gbd"])
    else:
        suona("avviso_di_sistema")
        print(f"La collezione {nome} non esiste.")
        return elementi
    if altri is None:
        suona("ronzio_di_errore_di_sistema")
        print("Unione annullata.")
        return elementi
    prima = len(elementi)
    insieme = set(elementi)
    insieme.update(altri)
    uniti = sorted(insieme)
    aggiunti = len(uniti) - prima
    print(f"Elementi prima: {prima}.")
    print(f"Nella collezione unita: {len(altri)}.")
    print(f"Aggiunti perche' nuovi: {aggiunti}.")
    print(f"Totale adesso: {len(uniti)}.")
    print("La collezione e' stata riordinata in")
    print("ordine alfabetico.")
    suona("conferma")
    salva(uniti, vie)
    return uniti


def salva_testo(elementi, vie):
    """Scrive la collezione ordinata in un file di testo"""
    if not elementi:
        print("La collezione e' vuota, non salvo nulla.")
        return
    try:
        with open(vie["txt"], "w", encoding="utf-8") as f:
            f.writelines(x + "\n" for x in sorted(elementi))
    except OSError as e:
        suona("ronzio_di_errore_di_sistema")
        print(f"Errore nel salvataggio del testo: {e}")
        return
    print(f"Salvati {len(elementi)} elementi in testo,")
    print("in ordine alfabetico.")
    suona("conferma")


def mostra_duplicato(elementi, posizione):
    """Dice dove si trova un elemento gia' presente e cosa gli sta attorno"""
    totale = len(elementi)
    da = max(0, posizione - CONTORNO)
    a = min(totale - 1, posizione + CONTORNO)
    percento = (posizione + 1) * 100 / totale
    print(f"Gia' presente alla posizione {posizione + 1}")
    print(f"su {totale}, cioe' al {percento:.1f} per cento.")
    intorno = []
    for j in range(da, a + 1):
        if j == posizione:
            intorno.append(f"({elementi[j]})")
        else:
            intorno.append(elementi[j])
    print(", ".join(intorno) + ".")


def esegui_comando(comando, elementi, vie):
    """Esegue un comando che comincia per punto.
    Restituisce la collezione, che i comandi possono avere cambiato, e
    True se il comando era riconosciuto.
    """
    if comando == ".txt":
        salva_testo(elementi, vie)
    elif comando == ".men":
        menu(d=COMANDI, show_only=True)
    elif comando == ".gui":
        manuale(testo=GUIDA, nome="Guida di CLZ")
    elif comando == ".lst":
        elenca(elementi)
    elif comando == ".eli":
        elimina(elementi, vie)
    elif comando == ".uni":
        elementi = unisci(elementi, vie)
    else:
        return elementi, False
    return elementi, True


def chiedi_nome():
    """Chiede il nome della collezione e lo restituisce ripulito"""
    while True:
        nome = nome_valido(dgt("Nome della collezione: ", kind="s", smin=1, smax=40).lower())
        if nome:
            return nome
        suona("avviso_di_sistema")
        print("Il nome non puo' essere vuoto e non puo'")
        print("contenere questi caratteri:")
        print(VIETATI)


def main():
    print(f"CLZ, Collezioni, versione {VERSIONE}")
    print(f"del {RELEASE_DATE}.")
    print("di Gabriele Battaglia.")
    print("Raccoglie nomi univoci e li tiene su disco.")
    suona("partenza")
    nome = chiedi_nome()
    vie = percorsi(nome)
    elementi = carica(vie)
    if elementi is None:
        suona("ronzio_di_errore_di_sistema")
        print("CLZ si ferma qui per non rischiare di")
        print("rovinare la collezione. Non ho scritto")
        print("niente.")
        print(f"Il file e': {vie['json']}")
        if os.path.exists(vie["bak"]):
            print("C'e' una copia precedente con estensione")
            print("punto bak: per usarla, rinominala dopo")
            print("aver messo al sicuro quella rotta.")
        return
    print(f"Elementi in collezione: {len(elementi)}.")
    menu(d=COMANDI, show_only=True)
    print("Una riga vuota chiude il programma.")
    while True:
        voce = dgt(f"Elemento {len(elementi) + 1}: ", kind="s", smin=0, smax=256).strip()
        if not voce:
            break
        if voce.startswith("."):
            elementi, riconosciuto = esegui_comando(voce.lower(), elementi, vie)
            if not riconosciuto:
                suona("avviso_di_sistema")
                print(f"{voce} non e' un comando.")
                print("Punto MEN per rileggere l'elenco.")
            continue
        nuovo = voce.capitalize()
        if nuovo in elementi:
            suona("avviso_di_sistema")
            mostra_duplicato(elementi, elementi.index(nuovo))
            continue
        elementi.append(nuovo)
        print(f"{nuovo}, aggiunto alla posizione {len(elementi)}.")
        suona("timbratura")
        salva(elementi, vie)
    print(f"Collezione {nome} chiusa.")
    print(f"Elementi salvati: {len(elementi)}.")
    suona("conferma")


if __name__ == "__main__":
    main()
