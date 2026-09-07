# CLZ

Collection, collezione. Crea un elenco di parole uniche e lo salva su disco, conservando l'ordine in cui e' stato costruito. Interfaccia a riga di comando, pensata per la lettura con screen reader.

Versione 2.0.0 del 7 settembre 2026.

## Come si usa
Avvia CLZ.py, dai un nome alla collezione e comincia a digitare elementi: ognuno viene aggiunto in fondo, e se e' gia' presente il programma dice dove si trova e cosa gli sta attorno. Una riga vuota chiude il programma.

I comandi cominciano con un punto: .ELI elimina, .LST elenca, .MEN rilegge il menu, .TXT salva in testo, .UNI unisce un'altra collezione, .GUI mostra la guida.

## Dove finiscono i dati
Ogni collezione sta in un file CLZ-nome.json accanto al programma. Si salva dopo ogni modifica, e della versione precedente resta sempre una copia con estensione .json.bak.

Le collezioni delle versioni fino alla 1.9 erano file .gbd in formato pickle. Alla prima apertura vengono convertite in JSON una volta sola, e i file originali restano dove sono senza essere toccati. Quelle di questo repository sono gia' convertite.

## Requisiti
Serve GBUtils.py nella stessa cartella, oppure nella path. Puoi scaricarlo dall'omonimo progetto su GitHub. Le altre dipendenze sono in requirements.txt.

## Cronologia
Le novita' di ogni versione sono in CHANGELOG.md.
