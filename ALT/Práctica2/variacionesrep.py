# AUTORES: Noelia Saugar Villar
#          Kléber Zapata Zambrano
#          Rafael Estellés Tatay

def variacionesRepeticion(elementos, cantidad):
    sol = [None]*cantidad
    def backtracking(longSol):
        if longSol == cantidad:
            yield sol.copy()
        else:
            for child in elementos:
                sol[longSol] = child
                yield from backtracking(longSol+1)
    yield from backtracking(0)

def permutaciones(elementos, cantidad):
    sol = [None]*cantidad
    def prometedor(child, longSol):
        return child not in sol[:longSol] 
    def backtracking(longSol):
        if longSol == cantidad:
            yield sol.copy()
        else:
            for child in elementos:
                if prometedor(child,longSol): #No permite que se repitan elementos en la solución
                    sol[longSol] = child
                    yield from backtracking(longSol+1)
    yield from backtracking(0)

def combinaciones(elementos, cantidad):
    sol = [None]*cantidad
    def prometedor(child, longSol):
        return child not in sol[:longSol]
    def backtracking(longSol, newl):
        if longSol == cantidad:
            yield sol.copy()
        else:
            for child in newl:
                if prometedor(child, longSol): #No permite que se repitan elementos en la solución
                    newl = elementos[elementos.index(child)+1:] #Copia de elementos[] pero sin child ni todos sus elementos anteriores
                    sol[longSol] = child
                    yield from backtracking(longSol+1, newl) #Pasa esa nueva lista para obligar a que se siga el orden
    yield from backtracking(0,elementos) #la primera llamada es con la lista completa

if __name__ == "__main__":    
    print("Variaciones con repeticion: " + "\n")
    for x in variacionesRepeticion(['tomate','queso','anchoas'],3):
        print(x)
    print("\nActividad 1: Permutaciones: " + "\n")
    for x in permutaciones(['tomate','queso','anchoas'],3):
        print(x)
    print("\nActividad 2: Combinaciones: " + "\n")
    for x in combinaciones(["tomate","queso","anchoas","aceitunas"],3):
        print(x)

