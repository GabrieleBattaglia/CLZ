# Collezioni Carica e salva su disco una raccolta di nomi univoci.
# Giugno 2017, inizio il porting a Python3
# giugno 2024, spostato su Github

import pickle
from GBUtils import dgt

print ("Collezioni 1.6 - 5 aprile 2013 / 4 settembre 2023\n-- by Gabriele Battaglia")
print ("\n- Nome della collezione: ",end="")
clz = dgt(smax=40)
clz=str.lower(clz)
clz=str.strip(clz)
clz = "CLZ-" + clz
def Txt():    
    f1=open(clz+".txt","wt")
    for j in range(ins):
        f1.writelines(l[j]+"\n")
    print ("\n- File: "+clz+".txt"+" salvato.")
    f1.close()
    return

def Menu():
    '''Scrive il menu delle scelte'''
    print ("\n----Menu----")
    print ("Inserisci questi comandi per ottenere le azioni corrispondenti.")
    print ("\tNota: i comandi vanno scritti in maiuscolo e preceduti da un punto")
    print (" - .ELI = Elimina un elemento dalla collezione")
    print (" - .UNI = Unisce una seconda collezione a quella aperta")
    print (" - .LST = Lista degli oggetti")
    print (" - .MEN = Visualizza questo menu")
    print (" - .TXT = Salva la lista in testo")
    print (" - Inserisci una riga vuota per concludere.")
    return

def Controllo(n):
    if n == ".TXT":
        Txt()
        return (True)
    if n == ".MEN":
        Menu()
        return (True)
    if n == ".LST":
        i1 = dgt("Da: ","i")
        i1 -= 1
        if i1 < 0: i1=0
        if i1 > len(l)-1: i1=len(l)-1
        i2 = dgt("A: ","i")
        i2 -= 1
        if i2 > len(l)-1: i2 = len(l)-1
        if i2 - i1 > 25: i2 = i1 + 25
        print ("Lista oggetti da",i1+1,"a",i2+1,":\n")
        for j in range(i1, i2+1):
            print (j+1,l[j])
        print ("\n")
        return (True)
    if n == ".ELI":
        j = dgt("Numero oggetto da eliminare? ", "i")
        j -= 1
        if j < 0: j=0
        if j > len(l)-1: j=len(l)-1
        print ("Elimino:", j+1, l[j])
        del l[j]
        return (True)
    if n == ".UNI":
        print ("Nome della collezione da aggiungere?",end="")
        clz0=dgt(smax=40)
        clz0=str.lower(clz0)
        clz0=str.strip(clz0)
        clz0 = "CLZ-" + clz0
        try:
            f=open(clz0+".gbd","rb")
            print ("- Caricamento di "+clz0+".gbd"+"  in corso...")
            l0=pickle.load(f)
            f.close()
        except IOError:
            print ("\a\n\n- La collezione "+clz0+".gbd"+" non esiste... Operazione annullata")
            return (True)
        print (" Caricamento completato con successo.")
        print (" Elementi presenti: %d, nuovi elementi aggiunti: %d. Elementi totali: %d." % (len(l), len(l0), len(l)+len(l0)))
        l.extend(l0)
        l.sort()
        return (True)
    return (False)

#quif
Menu()
try:
    f=open(clz+".gbd","rb")
    print ("\n\n- Caricamento di "+clz+".gbd"+"  in corso...")
    l=pickle.load(f)
    f.close()
except IOError:
    print ("\a\n\n- Creazione di "+clz+".gbd"+" in corso...")
    l=[]
f=open(clz+".gbd","wb")
nome="Gabriele"
while nome != "":
    ins=len(l)
    print ("Oggetto ",ins+1,": ",end="")
    nome=dgt()
    if Controllo(nome): continue
    nome=str.strip(nome)
    nome=str.capitalize(nome)
    if (nome != "" and nome not in l):
        l.append(nome)
        l.sort()
        continue
    if nome == "": continue
    i=l.index(nome)
    if i < 2:
        j1=0
        if i>ins-3:
            j2=ins-1
        else:
            j2=i+2
    elif i>ins-3:
        j2=ins-1
        j1=i-2
    else:
        j1=i-2
        j2=i+2
    print ("Elemento in posizione %d: %2.2f%%" % (i+1, (float(i+1)*100)/ins))
    for j in range(j1, j2+1):
        if i==j: print ("("+l[j]+")"+". ",end="")
        else: print (l[j]+", ",end="")
    print ("\n")
pickle.dump(l, f, protocol=pickle.HIGHEST_PROTOCOL)
f.close()
print("Arrivederci.")