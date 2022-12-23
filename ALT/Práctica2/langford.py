# -*- coding: utf-8 -*-

# AUTORES: Noelia Saugar Villar
#          Kléber Zapata Zambrano
#          Rafael Estellés Tatay

import sys

def langford(N):
    N2   = 2*N
    seq  = [0]*N2
    def backtracking(num):
        if num<=0: #es terminal
            yield "-".join(map(str, seq))
        else: #No es terminal
            # buscamos una posicion para situar una pareja num 
            for i in range(0,len(seq) - num - 1): #Ramificamos
                j = i + num + 1
                if seq[i] == seq[j] == 0 and j <= 2*N-1: #Si es prometedor
                    seq[i] = seq[j] = num #Modificaciones (cambair valor seq)
                    yield from backtracking(num-1) #bracktracking
                    #No sirve la rama: Deshacemos las modificaciones (seq a 0)
                    seq[i] = seq[j] = 0 #Deshacemos (Ponemos a 0 los huecos usados)

    if N%4 in (0,3):
        yield from backtracking(N)

if __name__ == "__main__":
    if len(sys.argv) not in (2,3):
        print('\nUsage: %s N [maxsoluciones]\n' % (sys.argv[0],))
        sys.exit()
    try:
        N = int(sys.argv[1])
    except ValueError:
        print('First argument must be an integer')
        sys.exit()
    numSolutions = None
    if len(sys.argv) == 3:
        try:
            numSolutions = int(sys.argv[2])
        except ValueError:
            print('Second (optional) argument must be an integer')
            sys.exit()

    i = 0
    for sol in langford(N):
        if numSolutions is not None and i>=numSolutions:
            break
        i += 1
        print(f'sol {i:4} ->',sol)
