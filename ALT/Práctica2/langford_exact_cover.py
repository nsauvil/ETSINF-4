# -*- coding: utf-8 -*-
# AUTORES: Noelia Saugar Villar
#          Kléber Zapata Zambrano
#          Rafael Estellés Tatay
import sys
from exactcover import exact_cover

# AUTORES: Noelia Saugar Villar
#          Kléber Zapata Zambrano
#          Rafael Estellés Tatay

def langford_data_structure(N):
    # n1,n2,... means that the value has been used
    # p0,p1,... means that the position has been used
    def value(i):
        return sys.intern(f'n{i}')   #al generar varias veces la cadena, se usa una sola referencia
    def position(i):
        return sys.intern(f'p{i}')
    # crear la lista de conjuntos que resuelva la
    # secuencia de Langford con exact_cover
    # COMPLETAR
    U = []     
    N2 = 2*N
    pos2 = 0
    aux = {}
    for i in range(1,N+1):
        for i2 in range(0,N2):
            pos2 = i2 + i + 1
            if pos2 <= N2-1:
                aux = {position(i2), position(pos2), value(i)}  #posiciones en las que puede estar ni
                if aux not in U:
                    U.append(aux)
    
    return U

def langford_exact_cover(N):
    if N%4 in (0,3):
        U = langford_data_structure(N)
        sol = [None]*2*N
        for coversol in exact_cover(U):
            for item in coversol:
                elems = sorted(item)
                n = int(elems[0][1:])
                p = int(elems[1][1:])
                sol[p]=n
                p = int(elems[2][1:])
                sol[p]=n
            yield "-".join(map(str,sol))

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
    for sol in langford_exact_cover(N):
        if numSolutions is not None and i>=numSolutions:
            break
        i += 1
        print(f'sol {i:4} ->',sol)
