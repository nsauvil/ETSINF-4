from audioop import reverse
import numpy as np

def levenshtein_matriz(x, y, threshold=None):
    # esta versión no utiliza threshold, se pone porque se puede
    # invocar con él, en cuyo caso se ignora
    lenX, lenY = len(x), len(y)
    
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    return D[lenX, lenY]


def levenshtein_edicion(x, y, threshold=None):
    # a partir de la versión levenshtein_matriz
    lenX, lenY = len(x), len(y)
    
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    distancia_leven = D[lenX, lenY]

    i = lenX
    j = lenY
    res = []
    
    while i != 0 or j != 0:
        #Posiciones alrededor
        valAtual = D[i][j]
        valLeft  = D[i][j-1]        
        valUp  = D[i-1][j]
        valDiagonal  = D[i-1][j-1]

        if valDiagonal <= valUp and valDiagonal <= valLeft and valDiagonal <= valAtual:
            aux = (x[i-1],y[j-1])
            res.append(aux)
            i -= 1
            j -= 1
        elif valLeft <= valDiagonal and valLeft == valAtual - 1:
            aux = ("", y[j-1])
            res.append(aux)
            j -= 1
        elif valUp <= valDiagonal and valUp == valAtual - 1:
            aux = (x[i-1], "")
            res.append(aux)
            i -= 1
        
    res = list(reversed(res))
    return distancia_leven, res

def levenshtein_reduccion(x, y, threshold=None):
    # completar versión con reducción coste espacial
    lenX, lenY = len(x), len(y)
    '''
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    return D[lenX, lenY]
    '''
    X = np.zeros(lenX + 1, dtype=np.int)
    Y = np.zeros(lenX + 1, dtype=np.int)
    for i in range(1, lenX + 1):
        X[i] = X[i-1] + 1

    for j in range(1, lenY + 1):
        Y[0] = j
        for i in range(1, lenX + 1):
            Y[i] = min(
                Y[i-1] + 1,
                X[i] + 1,
                X[i-1] + (x[i - 1] != y[j - 1]),
            )
        X,Y = Y,X

    return X[lenX]

def levenshtein(x, y, threshold):
    # completar versión reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y)
    X = np.zeros(lenX + 1, dtype=np.int)
    Y = np.zeros(lenX + 1, dtype=np.int)
    for i in range(1, lenX + 1):
        X[i] = X[i-1] + 1

    for j in range(1, lenY + 1):
        Y[0] = j
        for i in range(1, lenX + 1):
            Y[i] = min(
                Y[i-1] + 1,
                X[i] + 1,
                X[i-1] + (x[i - 1] != y[j - 1]),
            )
        if np.min(Y) > threshold:
            return threshold+1
        X,Y = Y,X
    return min(X[lenX],threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def levenshtein_cota_optimista(x, y, threshold): #AMPLIACIÓN
    aux = set(x)
    aux.update(set(y))

    res = {
        -1:0,
        1:0
    }

    for a in aux:
        dif = x.count(a) -y.count(a)
        if dif < 0:
            res[-1] += abs(dif)
        else: res[1] += dif

    maximum = max(res[-1], res[1])

    if maximum > threshold: return threshold +1

    return levenshtein(x,y,threshold)

def damerau_restricted_matriz(x, y, threshold=None): #AMPLIACIÓN
    # completar versión Damerau-Levenstein restringida con matriz
    lenX, lenY = len(x), len(y)
    
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
            if(i > 0 and j > 0 and (x[i - 1] == y[j - 2]) and (x[i - 2] == y[j - 1])):
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
    return D[lenX, lenY]

def damerau_restricted_edicion(x, y, threshold=None):
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición
    lenX, lenY = len(x), len(y)
    
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
            if(i > 0 and j > 0 and (x[i - 1] == y[j - 2]) and (x[i - 2] == y[j - 1])):
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)

    distancia_damerau_restricted = D[lenX, lenY]

    i = lenX
    j = lenY
    res = []

    while i != 0 or j != 0:
        #Posiciones alrededor
        valAtual = D[i][j]
        valLeft  = D[i][j-1]        
        valUp  = D[i-1][j]
        valDiagonal  = D[i-1][j-1]

        if i >= 2 and j >= 2:
            x1 =  x[i-2]
            x2 =  x[i-1]
            y1 =  y[j-2]
            y2 =  y[j-1]
            if x1 == y2 and y1 == x2:
                aux = (x1 + x2, y1 + y2)
                res.append(aux)
                i -= 2
                j -= 2
                continue   
        
        if valDiagonal <= valUp  and valDiagonal <= valLeft and valDiagonal <= valAtual :
            aux = (x[i-1],y[j-1])
            res.append(aux)
            i -= 1
            j -= 1
        elif valLeft <= valDiagonal and valLeft == valAtual - 1:
            aux = ("", y[j-1])
            res.append(aux)
            j -= 1
        elif valUp <= valDiagonal and valUp == valAtual - 1:
            aux = (x[i-1], "")
            res.append(aux)
            i -= 1
        # else:
        #     aux = (x[i-2]+x[i-1], y[i-2]+y[i-1])
        #     res.append(aux)
        #     i -= 2
        #     j -= 2
    res = list(reversed(res))
    return distancia_damerau_restricted, res

def damerau_restricted(x, y, threshold):
    # versión con reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y)
    X = np.zeros(lenX + 1, dtype=np.int)
    Y = np.zeros(lenX + 1, dtype=np.int)
    Z = np.zeros(lenX + 1, dtype=np.int)
    for i in range(1, lenX + 1):
        X[i] = X[i-1] + 1

    for j in range(1, lenY + 1):
        Y[0] = j 
        Y[1] = min(
                j + 1,
                X[1] + 1
        )
        for i in range(1, lenX + 1):
            Y[i] = min(
                Y[i-1] + 1,
                X[i] + 1,
                X[i-1] + (x[i - 1] != y[j - 1])
            )
            if(i > 1 and j > 1 and (x[i - 1] == y[j - 2]) and (x[i - 2] == y[j - 1])):
                Y[i] = min(Y[i], Z[i - 2] + 1)
        if np.min(Y) > threshold:
            return threshold+1
        X,Y = Y,X
        Z,Y = Y,Z
    return min(X[lenX],threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein intermedia con matriz

    lenX, lenY = len(x), len(y)
    
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1])
            )
            if(i > 1 and j > 1 and (x[i - 1] == y[j - 2]) and (x[i - 2] == y[j - 1])):
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
            if(i > 2 and j > 1 and (x[i - 3] == y[j - 1]) and (x[i - 1] == y[j - 2])):
                D[i][j] = min(D[i][j], D[i - 3][j - 2] + 2)
            if(i > 1 and j > 2 and (x[i - 2] == y[j - 1]) and (x[i - 1] == y[j - 3])):
                D[i][j] = min(D[i][j], D[i -2][j - 3] + 2)
    return D[lenX, lenY]

def damerau_intermediate_edicion(x, y, threshold=None):
    # partiendo de matrix_intermediate_damerau añadir recuperar
    # secuencia de operaciones de edición
    # completar versión Damerau-Levenstein intermedia con matriz
    lenX, lenY = len(x), len(y)
    
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1])
            )
            if(i > 1 and j > 1 and (x[i - 1] == y[j - 2]) and (x[i - 2] == y[j - 1])):
                D[i][j] = min(D[i][j], D[i - 2][j - 2] + 1)
            if(i > 2 and j > 1 and (x[i - 3] == y[j - 1]) and (x[i - 1] == y[j - 2])):
                D[i][j] = min(D[i][j], D[i - 3][j - 2] + 2)
            if(i > 1 and j > 2 and (x[i - 2] == y[j - 1]) and (x[i - 1] == y[j - 3])):
                D[i][j] = min(D[i][j], D[i -2][j - 3] + 2)

    distancia_damerau_inter = D[lenX, lenY]

    i = lenX
    j = lenY
    res = []

    while i != 0 or j != 0:
        #Posiciones alrededor
        valAtual = D[i][j]
        valLeft  = D[i][j-1]        
        valUp  = D[i-1][j]
        valDiagonal  = D[i-1][j-1]

        if i >= 2 and j >= 2:
            x1 =  x[i-2]
            x2 =  x[i-1]
            y1 =  y[j-2]
            y2 =  y[j-1]
            if x1 == y2 and y1 == x2:
                aux = (x1 + x2, y1 + y2)
                res.append(aux)
                i -= 2
                j -= 2
                continue 

        if i >=3 and j>=2: 
            x1 =  x[i-3]
            x2 =  x[i-2]
            x3 =  x[i-1]
            y1 =  y[j-2]
            y2 =  y[j-1]

            if y1 == x3 and y2 == x1:
                aux = (x1+x2+x3, y1+y2)
                res.append(aux)
                i-=3
                j-=2
                continue
       
        if  i >= 2 and j >= 3:
            x1 =  x[i-2]
            x2 =  x[i-1]
            y1 =  y[j-3]
            y2 =  y[j-2]
            y3 =  y[j-1]
            if x2 == y1 and x1 == y3:
                aux = (x1+x2, y1+y2+y3)
                res.append(aux)
                i-=2
                j-=3
                continue

        if valDiagonal <= valUp  and valDiagonal <= valLeft and valDiagonal <= valAtual :
            aux = (x[i-1],y[j-1])
            res.append(aux)
            i -= 1
            j -= 1
        elif valLeft <= valDiagonal and valLeft == valAtual - 1:
            aux = ("", y[j-1])
            res.append(aux)
            j -= 1
        elif valUp <= valDiagonal and valUp == valAtual - 1:
            aux = (x[i-1], "")
            res.append(aux)
            i -= 1
        # else:
        #     aux = (x[i-2]+x[i-1], y[i-2]+y[i-1])
        #     res.append(aux)
        #     i -= 2
        #     j -= 2
    res = list(reversed(res))
    return distancia_damerau_inter, res

    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE
    
def damerau_intermediate(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y)
    X = np.zeros(lenX + 1, dtype=np.int)
    Y = np.zeros(lenX + 1, dtype=np.int)
    Z = np.zeros(lenX + 1, dtype=np.int)
    Z_2 = np.zeros(lenX + 1, dtype=np.int)
    for i in range(1, lenX + 1):
        X[i] = X[i-1] + 1

    for j in range(1, lenY + 1):
        Y[0] = j
        Y[1] = min(
                j + 1,
                X[1] + 1
        ) 
        for i in range(1, lenX + 1):
            Y[i] = min(
                Y[i-1] + 1,
                X[i] + 1,
                X[i-1] + (x[i - 1] != y[j - 1])
            )
            if(i > 1 and j > 1 and (x[i - 1] == y[j - 2]) and (x[i - 2] == y[j - 1])):
                Y[i] = min(Y[i], Z[i - 2] + 1)
            if(i > 2 and j > 1 and (x[i - 3] == y[j - 1]) and (x[i - 1] == y[j - 2])):
                Y[i] = min(Y[i], Z[i - 3] + 2)
            if(i > 1 and j > 2 and (x[i - 2] == y[j - 1]) and (x[i - 1] == y[j - 3])):
                Y[i] = min(Y[i], Z_2[i - 2] + 2)
        if np.min(Y) > threshold:
            return threshold+1
        X,Y = Y,X
        Z,Z_2 = Z_2,Z
        Z,Y = Y,Z
    return min(X[lenX],threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

opcionesSpell = {
    'levenshtein_m': levenshtein_matriz,
    'levenshtein_r': levenshtein_reduccion,
    'levenshtein':   levenshtein,
    'levenshtein_o': levenshtein_cota_optimista,
    'damerau_rm':    damerau_restricted_matriz,
    'damerau_r':     damerau_restricted,
    'damerau_im':    damerau_intermediate_matriz,
    'damerau_i':     damerau_intermediate
}


opcionesEdicion = {
    'levenshtein': levenshtein_edicion,
    'damerau_r':   damerau_restricted_edicion,
    'damerau_i':   damerau_intermediate_edicion
}