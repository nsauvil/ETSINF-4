# AUTORES: Noelia Saugar Villar
#          Kléber Zapata Zambrano
#          Rafael Estellés Tatay

def esDisjunto(s):   #comprobar que no hay cadenas repetidas
    for i in range(0,len(s)):
        aux = s[i]
        s2 = s[i+1:]
        for a in aux:
            for el in s2:
                if a in el:
                    return False
    return True

def mismosElem(univ, s):
    obj = len(univ)
    cont = 0   #para comprobar que tenemos tantos elementos distintos como los del dominio
    for el in s:
        for a in el:
            cont = cont + 1
    return obj == cont
        
def exact_cover(listaConjuntos):
    U = set().union(*listaConjuntos) # para saber qué universo tenemos
    N = len(listaConjuntos)
    solucion = []
    def backtracking(longSol, cjtAcumulado):
        # COMPLETAR
        # consulta los métodos isdisjoint y union de la clase set,
        # podrías necesitarlos
        if longSol == N:  #es terminal
            if esDisjunto(solucion) and mismosElem(U,solucion):  #es factible
                yield solucion.copy()
        else:  #ramificar
            cjt = listaConjuntos[longSol]
            if set().isdisjoint(cjt) and set().isdisjoint(cjtAcumulado):
                solucion.append(cjt) 
                yield from backtracking(longSol + 1, set().union(cjtAcumulado, cjt))
                solucion.pop()
            yield from backtracking(longSol + 1, cjtAcumulado)
    yield from backtracking(0, set())

if __name__ == "__main__":
    cjtdcjts = [{"casa","coche","gato"},
                {"casa","bici"},
                {"bici","perro"},
                {"boli","gato"},
                {"coche","gato","bici"},
                {"casa", "moto"},
                {"perro", "boli"},
                {"coche","moto"},
                {"casa"}]
    for solucion in exact_cover(cjtdcjts):
        print(solucion)
