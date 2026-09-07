# Changelog di CLZ, Collezioni

Il formato segue il versionamento x.y.z: x per le grosse novita' o i
refactoring profondi, y per ogni nuova funzionalita', z per ogni
correzione o cambiamento minore.

## 2.0.0 del 7 settembre 2026

Revisione 1 dell'analisi del codice. Tutti e ventiquattro i rilievi sono
stati chiusi. La versione passa da 1.9 a 2.0.0 perche' cambia il formato
dell'archivio e il programma e' stato riscritto nella struttura.

### Formato dell'archivio
- Le collezioni sono in JSON, un elemento per riga. Il pickle e' stato
  abbandonato: aprire un pickle significa eseguire il codice che il file
  contiene, e il comando .UNI invita a caricare file che possono venire
  da chiunque.
- Le vecchie collezioni .gbd vengono convertite alla prima apertura, una
  volta sola, e i file originali restano dove sono, intatti.
- Le quattro collezioni del repository sono gia' state convertite:
  words con 297855 elementi, Cognomi con 2619, Femminili con 774,
  Maschili con 628. Il contenuto e l'ordine sono stati verificati
  identici agli originali.

### Sicurezza dell'archivio
- Una collezione che esiste ma non si riesce a leggere non viene piu'
  sostituita da una collezione vuota: il programma lo dice e si ferma
  senza scrivere niente. Prima il salvataggio finale cancellava per
  sempre l'archivio danneggiato.
- Il salvataggio e' atomico: passa da un file temporaneo e sostituisce
  con os.replace, conservando la versione precedente come .json.bak.
- Si salva dopo ogni aggiunta, eliminazione e unione, non piu' soltanto
  all'uscita. Chiudere la finestra non perde piu' il lavoro fatto.
- Cio' che si legge dal disco viene verificato: se non e' un elenco di
  parole il programma lo dice e non prosegue.
- I percorsi sono ancorati alla cartella del programma e non piu' alla
  directory di lavoro.
- Le eccezioni catturate sono quelle che si sanno nominare. Le altre
  risalgono, invece di diventare in silenzio una collezione vuota.

### Correttezza d'uso
- Un comando scritto male non viene piu' aggiunto alla collezione. Prima
  .ELIM, .TX o .eli con un refuso finivano dentro come se fossero
  parole, e il programma diceva anzi che erano stati aggiunti.
- Gli estremi dell'elenco vengono chiesti dentro i limiti veri. Prima si
  poteva ottenere l'elemento numero zero, che non esiste, e cancellarlo
  con .ELI significava cancellarne un altro.
- Il nome della collezione non puo' essere vuoto e viene ripulito dai
  caratteri che Windows non ammette nei nomi di file.

### Struttura
- Il programma ha una funzione main e la guardia __name__: prima
  caricamento e ciclo principale stavano a livello di modulo.
- La collezione viene passata alle funzioni invece di essere una
  variabile globale modificata da tre punti diversi.
- L'elenco dei comandi e' una tabella sola, mostrata con menu di
  GBUtils, e la guida e' affidata a manuale.
- Il calcolo degli elementi attorno a un duplicato occupava diciannove
  righe con quattro rami annidati: adesso sono due righe. Tolti tre rami
  che non potevano scattare.

### Accessibilita'
- Tolto il separatore grafico fatto di trattini attorno alla parola
  Menu, e tolte le righe vuote di separazione.
- Le stringhe informative sono spezzate in blocchi di circa quaranta
  caratteri, utili sul display braille. Le voci del menu arrivavano a
  settantacinque caratteri, i riepiloghi dell'unione a novanta.
- Il campanello del terminale, che su Windows spesso non suona, e' stato
  sostituito dai suoni condivisi di Acusticator: errore, avviso e
  conferma adesso si distinguono a orecchio. Se la scheda audio non c'e'
  il programma prosegue in silenzio.
- Versione e data di rilascio sono due costanti separate, l'intestazione
  ha la riga degli autori e le tre date che si contraddicevano sono
  state riconciliate.

### Rimasto com'era, per scelta
- Il comando .UNI continua a riordinare alfabeticamente tutta la
  collezione. Adesso pero' lo dice, e il risultato viene salvato subito.
- Gli elementi continuano a essere normalizzati con l'iniziale maiuscola
  e il resto minuscolo.

### Pulizia
- Il .gitignore, che era di una riga sola, adesso esclude cio' che la
  compilazione produce e le copie di sicurezza.
- Il sorgente passa ruff senza rilievi.
- Il commento che annunciava una divisione del testo in frasi e' stato
  allineato a cio' che il codice fa davvero, cioe' estrarre parole.

## 1.9 e precedenti
- Giugno 2017, porting a Python 3.
- Giugno 2024, spostato su GitHub.
- Aprile 2025, caricamento da file di testo, gestione dei file e
  conservazione dell'ordine di inserimento.
