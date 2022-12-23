@echo off
echo SAR_Indexer.py corpora/2015 index2015.bin

FOR %%x IN (levenshtein_o damerau_r damerau_i) DO (
    FOR %%y in (1 2 3) DO (
        SAR_Searcher.py index2015.bin -L referenciasSAR/queries.txt -C -t %%y -d %%x > referenciasSAR/resul_%%x_%%y.txt
    )
) 
