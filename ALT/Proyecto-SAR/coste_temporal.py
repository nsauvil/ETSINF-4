from distancias import *
from spellsuggester import SpellSuggester
import os
import time
import re

def calcular_coste():
    bateria_test = [
        "casa",
        "uqijoext",
    ]
    levenshtein_test = [
        'levenshtein_m',
        'levenshtein_r',
        'levenshtein',
        'levenshtein_o',
    ]
    v =["./corpora/miniquijote.txt", "./corpora/2015/01/2015-01-03.json",
        "./corpora/2015/01/2015-01-02.json"]   #vocabularios
    for i in range(0,len(v)):    #para cada vocabulario
        spellsuggester = SpellSuggester(
            dist_functions = opcionesSpell,
            vocab = v[i])
        
        tokenizer=re.compile("\W+")  #Calcular tamaño vocab
        with open(v[i], "r", encoding="utf-8") as fr:
            vocab = set(tokenizer.split(fr.read().lower()))
            vocab.discard("")  
            tamaño = len(vocab)
            
        for dstname in levenshtein_test:   #para cada distancia levenshtein
            for palabra in bateria_test:
                for threshold in range(1, 4+1):
                    t0 = time.time()
                    newresul = spellsuggester.suggest(palabra, distance=dstname,
                                                   threshold=threshold, flatten=False)
                    t1 = time.time()
                    print('Longitud vocab: ' + str(tamaño) + '    Metodo: ' + str(dstname) + 
                          '    Threshold: ' + str(threshold) + 
                          '    Palabra: ' + str(palabra) +
                          '    Time suggest: %2.5fs.' % (t1 - t0) + '\n')
                    
                
                
if __name__ == "__main__":
    calcular_coste()
