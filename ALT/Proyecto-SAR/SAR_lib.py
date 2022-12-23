import json
from lib2to3.pgen2.tokenize import tokenize
from nltk.stem.snowball import SnowballStemmer
import os
import re
import numpy as np
#import distancias

# ALGORITMICA
from spellsuggester import SpellSuggester
from distancias import *

#Participantes: Kléber Zapata Zambrano, Rafael Estellés Tatay, Noelia Saugar Villar.

class SAR_Project:
    """
    Prototipo de la clase para realizar la indexacion y la grecuperacion de noticias
        
        Preparada para todas las ampliaciones:
          parentesis + multiples indices + posicionales + stemming + permuterm + ranking de resultado

    Se deben completar los metodos que se indica.
    Se pueden aÃ±adir nuevas variables y nuevos metodos
    Los metodos que se aÃ±adan se deberan documentar en el codigo y explicar en la memoria
    """

    # lista de campos, el booleano indica si se debe tokenizar el campo
    # NECESARIO PARA LA AMPLIACION MULTIFIELD
    fields = [("title", True), ("date", False),
              ("keywords", True), ("article", True),
              ("summary", True)]
    
    
    # numero maximo de documento a mostrar cuando self.show_all es False
    SHOW_MAX = 10
    
    


    def __init__(self):
        """
        Constructor de la classe SAR_Indexer.
        NECESARIO PARA LA VERSION MINIMA

        Incluye todas las variables necesaria para todas las ampliaciones.
        Puedes aÃ±adir mÃ¡s variables si las necesitas 

        """
        #posting list= lista de documetnos(meterlso como números) que contiene una palabra
        self.index = {'title': {},
                      'date': {},
                      'keywords': {},
                      'article': {},
                      'summary': {}} # hash para el indice invertido de terminos --> clave: termino, valor: posting list.
                        # Si se hace la implementacion multifield, se pude hacer un segundo nivel de hashing de tal forma que:
                        # self.index['title'] seria el indice invertido del campo 'title'.
        #Cojo la palabra le hago stema (casas, cas) y busco con un or en el índice invertido
        self.sindex = {'title': {},
                      'date': {},
                      'keywords': {},
                      'article': {},
                      'summary': {}} # hash para el indice invertido de stems --> clave: stem, valor: lista con los terminos que tienen ese stem
        self.ptindex = {'title': {},
                      'date': {},
                      'keywords': {},
                      'article': {},
                      'summary': {}} # hash para el indice permuterm.
        self.docs = {} # diccionario de documentos --> clave: entero(docid),  valor: ruta del fichero.
        self.weight = {} # hash de terminos para el pesado, ranking de resultados. puede no utilizarse
        self.news = {} # hash de noticias --> clave entero (newid), valor: la info necesaria para diferenciar la noticia dentro de su fichero (doc_id y posiciÃ³n dentro del documento)
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()
        self.docid = 0
        self.newid = 0

        #Algoritmica
        self.use_spelling = False
        self.distance = None
        self.threshold = None

        self.speller = SpellSuggester(dist_functions = opcionesSpell)
        
        

   


    ###############################
    ###                         ###
    ###      CONFIGURACION      ###
    ###                         ###
    ###############################
        self.doc_cont = 0
        self.new_cont = 0
     #Búsqueda con tolerancia
    def set_spelling(self, use_spelling, distance, threshold): 
        """ 
        self.use_spelling a True se activa la corrección ortográfica
        EN LAS PALABRAS NO ENCONTRADAS, en caso contrario NO utilizará
        correción ortográfica  
        """
        self.use_spelling = use_spelling
        self.distance = distance
        self.threshold = threshold
    def set_showall(self, v):
        """

        Cambia el modo de mostrar los resultados.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_all es True se mostraran todos los resultados el lugar de un maximo de self.SHOW_MAX, no aplicable a la opcion -C

        """
        self.show_all = v


    def set_snippet(self, v):
        """

        Cambia el modo de mostrar snippet.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_snippet es True se mostrara un snippet de cada noticia, no aplicable a la opcion -C

        """
        self.show_snippet = v


    def set_stemming(self, v):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v


    def set_ranking(self, v):
        """

        Cambia el modo de ranking por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON RANKING DE NOTICIAS

        si self.use_ranking es True las consultas se mostraran ordenadas, no aplicable a la opcion -C

        """
        self.use_ranking = v




    ###############################
    ###                         ###
    ###   PARTE 1: INDEXACION   ###
    ###                         ###
    ###############################


    def index_dir(self, root, **args):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        
        Recorre recursivamente el directorio "root" e indexa su contenido
        los argumentos adicionales "**args" solo son necesarios para las funcionalidades ampliadas

        """

        self.multifield = args['multifield']
        self.positional = args['positional']
        self.stemming = args['stem']
        self.permuterm = args['permuterm']

        for dir, subdirs, files in os.walk(root):
            for filename in files:
                if filename.endswith('.json'):
                    fullname = os.path.join(dir, filename)
                    self.index_file(fullname)

        ##########################################
        ## COMPLETAR PARA FUNCIONALIDADES EXTRA ##
        ##########################################

        # Activamos funcion permuterm
        if self.permuterm:
            self.make_permuterm()
        # Activamos funcion stemming
        if self.stemming:
            self.make_stemming()
        
        #ALGORÍTMICA   
        self.speller.set_vocabulary(list(self.index['article'].keys()))
        
        
        
        

    def index_file(self, filename):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Indexa el contenido de un fichero.

        Para tokenizar la noticia se debe llamar a "self.tokenize"

        Dependiendo del valor de "self.multifield" y "self.positional" se debe ampliar el indexado.
        En estos casos, se recomienda crear nuevos metodos para hacer mas sencilla la implementacion

        input: "filename" es el nombre de un fichero en formato JSON Arrays (https://www.w3schools.com/js/js_json_arrays.asp).
                Una vez parseado con json.load tendremos una lista de diccionarios, cada diccionario se corresponde a una noticia

        """
        
        with open(filename) as fh:
            jlist = json.load(fh)

        #
        # "jlist" es una lista con tantos elementos como noticias hay en el fichero,
        # cada noticia es un diccionario con los campos:
        #      "title", "date", "keywords", "article", "summary"
        #
        # En la version basica solo se debe indexar el contenido "article"
        #
        #
        #
        #################
        ### COMPLETAR ###
        #################
           # docid = len(self.docs)  #al agregar nuevo documento su id sera 1+ el ultimo id, es decir, la longitud del hash de documentos
            self.docs[self.docid] = filename #agregamos al hash de documentos el documento que nos han pasado en su correspondiente id
           # newid = len(self.news) #conseguimos el id posterior al de la ultima noticia agregada
            posicion_not = 0 #posicion de la noticia en el documento
            
            for new in jlist: #recorremos la lista de noticias que hay en el fichero
                
                self.news[self.newid] = {
                    'docid':self.docid,
                    'posicion':posicion_not
                }   #guardamos de la noticia actual en la tabla hash de news, su docid y su posicion en la lista de noticias
                
                if self.multifield:  #Extensión multifield
                    multifield = ['title', 'date', 'keywords', 'article', 'summary']  
                else:
                    multifield = ['article'] 
                for f in multifield:  
                    if f == 'date':  #las fechas no se tokenizan 
                        tokens = [new['date']] #guardamos el contenido de la parte de la fecha de la noticia
                    else:
                        content = new[f] 
                       # posicion = 0
                        tokens = self.tokenize(content) #mediante el metodo tokenize nos devuelve una lista de tokens del articulo/titulo/...
                    pos_token = 0
                    for t in tokens: #recorremos los tokens

                        if not self.index[f].get(t,0): #si el token no está en el índice  
                            if not self.positional:
                                self.index[f][t] = {self.newid: 1}
                        #Implementar para el positional 
                            else: self.index[f][t] = {self.newid: [pos_token]}
                        else:  
                            if not self.index[f][t].get(self.newid,0): #añadir la noticia si no está en el token 
                                if not self.positional:
                                    self.index[f][t][self.newid] = 1
                                #IMPLEMENTAR para POSITIONAL 
                                else:
                                    self.index[f][t][self.newid] = [pos_token] 
                                
                            else:
                                if not self.positional:
                                    self.index[f][t][self.newid] += 1
                                #IMPLEMENTAR PARA POSITIONAL 
                                else:
                                    self.index[f][t][self.newid] += [pos_token]
                        pos_token = pos_token + 1
                                

                posicion_not = posicion_not + 1 #la posicion crece en uno ya que vamos a pasar a la siguiente noticia
                self.newid = self.newid + 1 #newid tambien suma uno porque pasa a la siguiente noticia
            self.docid = self.docid + 1
        
        
        
            
        



    def tokenize(self, text):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Tokeniza la cadena "texto" eliminando simbolos no alfanumericos y dividientola por espacios.
        Puedes utilizar la expresion regular 'self.tokenizer'.

        params: 'text': texto a tokenizar

        return: lista de tokens

        """
        return self.tokenizer.sub(' ', text.lower()).split()



    def make_stemming(self):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING.

        Crea el indice de stemming (self.sindex) para los terminos de todos los indices.

        self.stemmer.stem(token) devuelve el stem del token

        """
        #for f in self.index:
        #    for t in self.index[f]:
        #        stem = self.stemmer.stem(t)
        #        self.sindex[f][stem] = self.sindex[f].get(stem, [])
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################
        # Si se activa la función multifield
        if self.multifield:
            multifield = ['title', 'date', 'keywords', 'article', 'summary']
        else:
            multifield = ['article']
        for field in multifield:
            # Se aplica stemming a cada token del self.index[field] y se añade al indice de stems
            # En este caso solo se guarda la noticia, no la posición
            for token in self.index[field].keys():
                token_s = self.stemmer.stem(token)
                if token_s not in self.sindex[field]:
                    self.sindex[field][token_s] = [token]
                else:
                    if token not in self.sindex[field][token_s]:
                        self.sindex[field][token_s] += [token]


    
    def make_permuterm(self):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        """
        
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################
        #Si multifield está activo
        if self.multifield: 
            multifield = ['title', 'date', 'keywords', 'article', 'summary']
        else: 
            multifield = ['article']
        for field in multifield:
            for token in self.index[field].keys():
                #Lista donde almacenar la permutación de cada token
                permutation = []
                #Añadimos el $ al final para hacer permuterm
                tokenA = token + '$'
                for i in range(len(tokenA)):
                    #Guardo el token menos el primer caracter que la pongo al final
                    tokenA = tokenA[1:] + tokenA[0]
                    permutation += [tokenA] 
                for p in permutation:
                    #p no esta en indice de permuterm 
                    if p not in self.ptindex:
                        #añadimos el primer token a esa permutación
                        self.ptindex[field][p] = [token]
                    else:
                        #Si el token NO esta en el indice de permuterm para esa permutacion
                        if token not in self.ptindex[field][p]:
                            #Añadimos el token a esa permutación
                            self.ptindex[field][p] += token


    def show_stats(self):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        
        Muestra estadisticas de los indices
        
        """
       # pass
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################

        print("========================================")
        print("Number of indexed days: " + str(len(self.docs))) #La longitud del hash de documentos es el número de documentos indexados
        print("----------------------------------------")
        print("Number of indexed news: " + str(len(self.news))) #La longitud del hash de noticias es el número de noticias indexadas
        print("----------------------------------------")
        print("TOKENS:")

        if self.multifield:
            print("\t# of tokens in 'title': " + str(len(self.index['title']))) #Se busca en 'title' .
            print("\t# of tokens in 'date': " + str(len(self.index['date']))) #Se busca en 'date' 
            print("\t# of tokens in 'keywords': " + str(len(self.index['keywords']))) #Se busca en 'keywords' 
            print("\t# of tokens in 'article': " + str(len(self.index['article']))) #Se busca en 'article' 
            print("\t# of tokens in 'summary': " + str(len(self.index['summary']))) #Se busca en 'summary' 
        else:
            print("\t# of tokens in 'article': " + str(len(self.index['article']))) #Se busca en 'article' porque por ahora sólo se indexa el contenido del campo 'article' del diccionario de la noticia.
        print("----------------------------------------")
        if self.permuterm:
            print("PERMUTERMS:")
            if self.multifield:
                print("\t# of permuterms in 'title': " + str(len(self.ptindex['title']))) #Se busca en 'title' .
                print("\t# of permuterms in 'date': " + str(len(self.ptindex['date']))) #Se busca en 'date' 
                print("\t# of permuterms in 'keywords': " + str(len(self.ptindex['keywords']))) #Se busca en 'keywords' 
                print("\t# of permuterms in 'article': " + str(len(self.ptindex['article']))) #Se busca en 'article' 
                print("\t# of permuterms in 'summary': " + str(len(self.ptindex['summary']))) #Se busca en 'summary' 
            else:
                print('\t# of permuterms in \'{}\': {}'.format("article", len(self.ptindex["article"])))
            print("----------------------------------------")
        if self.stemming:
            print("STEMS:")
            if self.multifield:
                print("\t# of stems in 'title': " + str(len(self.sindex['title']))) #Se busca en 'title' .
                print("\t# of stems in 'date': " + str(len(self.sindex['date']))) #Se busca en 'date' 
                print("\t# of stems in 'keywords': " + str(len(self.sindex['keywords']))) #Se busca en 'keywords' 
                print("\t# of stems in 'article': " + str(len(self.sindex['article']))) #Se busca en 'article' 
                print("\t# of stems in 'summary': " + str(len(self.sindex['summary']))) #Se busca en 'summary' 
            else:
                print("\t# of stems in 'article': " + str(len(self.sindex['article'])))
            print("----------------------------------------")
        if self.positional:print("Positional queries are allowed.")
        else: print("Positional queries are NOT allowed.")
        print("========================================")


    ###################################
    ###                             ###
    ###   PARTE 2.1: RECUPERACION   ###
    ###                             ###
    ###################################


    def solve_query(self, query, prev={}):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una query.
        Debe realizar el parsing de consulta que sera mas o menos complicado en funcion de la ampliacion que se implementen


        param:  "query": cadena con la query
                "prev": incluido por si se quiere hacer una version recursiva. No es necesario utilizarlo.


        return: posting list con el resultado de la query

        """
        aux =[] 

        if query is None or len(query) == 0:
            return []

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################

        #arreglamos los paréntesis para que se queden aislados en el split 
        query = query.replace('"', '')
        query = query.replace('(', ' ( ')
        query = query.replace(')', ' ) ')
        query = query.replace(':', ' : ')
        q=query.split()
        postinglist_a =[] 
        postinglist_b =[] 
        #si la primera palabra debe NO APARECER, aplicamos ese not
        i=0
        if ':' in q: #MULTIFIELD
            nm = q.count(':') #contar cuántos fields hay
            while nm > 0: #analizar todos los campos
                pos = q.index(':') #posición de : en la query
                q[pos] = self.get_posting(q[pos+1].lower(), q[pos-1] )  #posting (term,field)   field : term
                q.pop(pos - 1)
                q.pop(pos) #pos era pos+1 antes 
                nm = nm - 1
        # print(self.sindex)
        while i < len(q): 
            term = q[i] 
                  
            if term == '(':
                position=i            
                o=i+1
                q2 = ''
                aux = 0
                contador=0
                while aux >= 0:
                    if q[o] == '(':
                         aux += 1
                    if q[o] == ')':
                        aux -= 1
                    q2 += q[o] + ' '
                    o += 1
                    contador+=1                   
                q2 = q2.strip()
                q2 = q2[0:len(q2) - 1]  
                qx=self.solve_query(q2)
                q[position]=qx
                for num in range(contador):
                    q.pop(position+1)
            if self.stemming and q[i] != 'AND'and q[i] != 'OR'and q[i] != 'NOT' and not isinstance(q[i], list) :
                
                if q[0]=='NOT':
                    b = q[1] 
                    q[1] =  self.get_stemming(q[1])
                    q[0] =self.reverse_posting(self.get_posting(b))
                    q.pop(1)
                    i -= 1
                else: q[i]=self.get_stemming(q[i])
                
            i += 1
        if q[0]=='NOT':
            q[0]=self.reverse_posting(self.get_posting(q[1]))
            q.pop(1)
        
            

        while len(q) > 1:
            if q[1]=='AND':
                if q[2]=='NOT':
                    if 4<len(q):
                        if isinstance(q[4],str) and q[4] != 'AND' and q[4] != 'OR' and q[4] != 'NOT':
                            i=5
                            terms = [q[3],q[4]]
                            while i<len(q) and isinstance(q[i],str) and q[i] != 'AND' and q[i] != 'OR' and q[i] != 'NOT':
                                terms.append(q[i])
                                i+=1
                            i-=1
                            while i > 3:
                                q.pop(i)
                                i-=1
                        # print(terms)
                            q[3] = self.get_positionals(terms)
                        # print(q[0]) 
                    if isinstance(q[0], str): postinglist_a = self.get_posting(q[0])
                    elif(isinstance(q[0], list)): postinglist_a = q[0] 
                    if isinstance(q[3], str): postinglist_b = self.get_posting(q[3])
                    elif(isinstance(q[3], list)): postinglist_b = q[3]
                    postinglist_b = self.reverse_posting(postinglist_b)
                    q[0]=self.and_posting(postinglist_a, postinglist_b)
                    postinglist_a = q[0]
                    q.pop(3)
                    q.pop(2)
                    q.pop(1)
                else:
                    if 3<len(q):
                        if isinstance(q[3],str) and q[3] != 'AND' and q[3] != 'OR' and q[3] != 'NOT':
                            i=4
                            terms = [q[2],q[3]]
                            while i<len(q) and isinstance(q[i],str) and q[i] != 'AND' and q[i] != 'OR' and q[i] != 'NOT':
                                terms.append(q[i])
                                i+=1
                            i-=1
                            while i > 2:
                                q.pop(i)
                                i-=1
                        # print(terms)
                            q[2] = self.get_positionals(terms)
                        # print(q[0]) 
                    if isinstance(q[0], str): postinglist_a = self.get_posting(q[0])
                    elif(isinstance(q[0], list)): postinglist_a = q[0]
                    if isinstance(q[2], str): postinglist_b = self.get_posting(q[2])
                    elif(isinstance(q[2], list)): postinglist_b = q[2]
                    q[0] = self.and_posting(postinglist_a, postinglist_b)
                    postinglist_a = q[0]
                    q.pop(2)
                    q.pop(1)
            elif q[1]=='OR':
                if q[2]=='NOT':
                    if 4<len(q):
                        if isinstance(q[4],str) and q[4] != 'AND' and q[4] != 'OR' and q[4] != 'NOT':
                            i=5
                            terms = [q[3],q[4]]
                            while i<len(q) and isinstance(q[i],str) and q[i] != 'AND' and q[i] != 'OR' and q[i] != 'NOT':
                                terms.append(q[i])
                                i+=1
                            i-=1
                            while i > 3:
                                q.pop(i)
                                i-=1
                        # print(terms)
                            q[3] = self.get_positionals(terms)
                        # print(q[0]) 
                    if isinstance(q[0], str): postinglist_a = self.get_posting(q[0])
                    elif(isinstance(q[0], list)): postinglist_a = q[0]
                    if isinstance(q[3], str): postinglist_b = self.get_posting(q[3])
                    elif(isinstance(q[3], list)): postinglist_b = q[3]
                    postinglist_b = self.reverse_posting(postinglist_b)
                    # print(postinglist_a)
                    # print(postinglist_b)
                    q[0]=self.or_posting(postinglist_a, postinglist_b)
                     # print(q[0])
                    postinglist_a = q[0]
                    q.pop(3)
                    q.pop(2)
                    q.pop(1)
                else:
                    if 3<len(q):
                        if isinstance(q[3],str) and q[3] != 'AND' and q[3] != 'OR' and q[3] != 'NOT':
                            i=4
                            terms = [q[2],q[3]]
                            while i<len(q) and isinstance(q[i],str) and q[i] != 'AND' and q[i] != 'OR' and q[i] != 'NOT':
                                terms.append(q[i])
                                i+=1
                            i-=1
                            while i > 2:
                                q.pop(i)
                                i-=1
                        # print(terms)
                            q[2] = self.get_positionals(terms)
                        # print(q[0]) 
                    if isinstance(q[0], str): postinglist_a = self.get_posting(q[0])
                    elif(isinstance(q[0], list)): postinglist_a = q[0] 
                    if isinstance(q[2], str): postinglist_b = self.get_posting(q[2])
                    elif(isinstance(q[2], list)): postinglist_b = q[2]
                    q[0]=self.or_posting(postinglist_a, postinglist_b)
                    postinglist_a = q[0] 
                    q.pop(2)
                    q.pop(1)
            elif isinstance(q[1],str):
                i=2
                terms = [q[0],q[1]]
                while i<len(q) and isinstance(q[i],str) and q[i] != 'AND' and q[i] != 'OR' and q[i] != 'NOT':
                    terms.append(q[i])
                    i+=1
                i-=1
                while i > 0:
                    q.pop(i)
                    i-=1
               # print(terms)
                q[0] = self.get_positionals(terms)
               # print(q[0])
                 
        if isinstance(q[0], str):
            q[0] = self.get_posting(q[0])

        return q[0] 
 


    def get_posting(self, term, field='article', wildcard='False'):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve la posting list asociada a un termino. 
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales
            - self.get_permuterm: para la ampliacion de permuterms
            - self.get_stemming: para la amplaicion de stemming


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario si se hace la ampliacion de multiples indices

        return: posting list

        """
        
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        posting = []
        #lista = []
        if self.stemming and not wildcard:
            posting = self.get_stemming(term,field)
           # print(posting)
        elif '*' in term or '?' in term:  
            posting = self.get_permuterm(term,field)
            return posting
       #FALTA EL DE POSICIONALES 
        else:
            if term in self.index[field]:
                posting = self.index[field].get(term, []) #implementación para la entrega obligatoria
                #for key, value in posting.items():
                        #entry = (key, value)
                        #lista.append(entry)
                return list(posting.keys())
        #ALGORITMICA
        if self.use_spelling and posting == []:
            #aux = []  #para guardar las palabras sugeridas
            aux = self.speller.suggest(term, self.distance, self.threshold, flatten=True)
            #if aux == []: return []
           # else: 
               # res = ""   #para agrupar la consulta OR
                #count = 1
                #for a in aux:
                   # if len(aux) < count:
                        #res += a +  " OR "
                    #else:
                        #res += a
                    #count = count + 1  #evitar un OR extra
                #return self.solve_query(res)
            for a in aux:
                posting = self.or_posting(posting, self.get_posting(a))
        #else:
           # return []
        return posting
       # return list(posting.keys())
                        
            
        

    def set_spelling(self, use_spelling, distance, threshold):
        """
        self.use_spelling a True se activa la corrección ortográfica
        EN LAS PALABRAS NO ENCONTRADAS, en caso contrario NO utilizará
        corrección ortográfica
        """
        self.use_spelling = use_spelling
        self.distance = distance
        self.threshold = threshold


    def get_positionals(self, terms, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        
        ########################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE POSICIONALES ##
        ########################################################
        res = []
        corrido = True
        if terms[0] in self.index[field]: #si el primer termino se encuentra indexado 
            for posting_list in self.index[field][terms[0]].items(): #recorre las posting_list de noticias del primer termino
                noticia = posting_list[0] #guarda el indice de la noticia actual de la posting_list 
                lista_posiciones = posting_list[1] #guarda la lista de posiciones del termino actual en la noticia actual de la posting_list 
                for posicion in lista_posiciones: #recorre las posiciones del termino en la noticia actual 
                    i=1
                    corrido = True
                    while i<len(terms) and corrido: #recorremos el resto de terminos comprobando que están de seguido 
                        
                        if self.index[field].get(terms[i],0): #comprueba si el termino actual se encuentra indexado 
                            #print(res)
                            if self.index[field][terms[i]].get(noticia,0): #comprueba si el termino actual contiene la noticia actual del primer termino 
                               # print(self.index[field][terms[i]][noticia])
                                if (posicion+1) in self.index[field][terms[i]][noticia]: #comprueba si el termino se encuentra en la posicion inmediatamente siguiente a la del termino anterior en la noticia actual
                                  #  print(res)
                                    posicion += 1 #pasa a comprobar la siguiente posicion
                                else:
                                   # print('bloop')
                                    corrido = False
                            else:
                                corrido = False
                        else: 
                            corrido = False
                        i+=1
                    if corrido: #si han estado todos los terminos de corrido se añade la noticia a la solucion 
                       # print(noticia)
                        res += [noticia]
                        break #pasa a comprobar la siguiente noticia
                   # print(noticia)
        return res
            
            


    def get_stemming(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE STEMMING

        Devuelve la posting list asociada al stem de un termino.

        param:  "term": termino para recuperar la posting list de su stem.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        
        stem = self.stemmer.stem(term)

        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################
        res = []
        if (stem in self.sindex[field]):
            for token in self.sindex[field][stem]:
                res = self.or_posting(res, list(self.index[field][token].keys()))
        return res

    def get_permuterm(self, term, field='article'):
        """
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        Devuelve la posting list asociada a un termino utilizando el indice permuterm.

        param:  "term": termino para recuperar la posting list, "term" incluye un comodin (* o ?).
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """

        ##################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA PERMUTERM ##
        ##################################################
        res = []
        term = term + '$'
        #Recorremos el termino para crear la query 
        while term[-1] != '*' and term[-1] != '?': 
            term = term[1:] + term[0]
        #Nos guardamos si lo que hemos encontrado es un '*' o '?'
        comodin = term[-1]
        #Alamcenamos el termino a buscar en la query
        term = term[:-1]

        #Si el comodin = '*' : buscamos TODOS sus permutaciones que comiencen por query
        #Si comodin = '?': buscamos TODAS sus permutaciones que comiencen por query + longitud = al de term
        for perm in (x for x in list(self.ptindex[field].keys()) if x.startswith(term) and (comodin == '*' or len(x) == len(term) + 1)):
            #Buscamos para cada token en ptindex
            for token in self.ptindex[field][perm]:
                res = self.or_posting(res, self.get_posting(token, field, wildcard=True))

        return res




    def reverse_posting(self, p):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.


        param:  "p": posting list


        return: posting list con todos los newid exceptos los contenidos en p

        """
        # Extraemos las noticias
        news = list(self.news.keys())
        #Recorremos la lista p
        for i in p:
            #Eliminamos de las noticas las que aparecen en p
            news.remove(i)
        #Devolvemos las noticias sin las que tenía p
        return news


    def and_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos en p1 y p2

        """
        #Estructura vista en clase: ALGORITMO INTERSECCION (Tema 1. Diap.39)
        res = []
        i = 0
        j = 0
        while i < len(p1) and j < len(p2):
            if p1[i]  == p2[j]:
                res.append(p1[i])
                i += 1
                j += 1
            elif p1[i] <= p2[j]:
                i += 1
            elif p1[i] >= p2[j]:
                j += 1
        return res

    def not_and_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el NOT(AND) de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos en p1 y p2

        """
        aux = self.and_posting(p1, p2)
        #i = 0
        #j = 0
        #Extraemos todos los id de las noticias
        #news = list(self.news.keys())
        #Si un elemento esta en las dos lista lo eliminamos del resultado
        #while i < len(p1) and j < len(p2):
            #if p1[i] == p2[j]:
                #news.remove(p1[i])
                #i += 1
                #j += 1
            #elif p1[i] <= p2[j]:
                #i += 1
            #elif p1[i] >= p2[j]:
                #j += 1
        return self.reverse_posting(aux)
                

    def or_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los new id incluidos de p1 o p2

        """
        #añadimos todos los terminos a la lista
        res = []
        i = 0
        j = 0
        #Recorremos las listas y eliminamos los elementos de la lista news
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                res.append(p1[i])
                i += 1
                j += 1
            elif p1[i] <= p2[j]:
                res.append(p1[i])
                i += 1
            elif p1[i] >= p2[j]:
                res.append(p2[j])
                j += 1
        #Terminos que no han sido eliminados aun del resultado
        for k in range(i, len(p1)):
            res.append(p1[k])
        for l in range(j, len(p2)):
            res.append(p2[l])
        return list(np.unique(res))

    def not_or_posting(self, p1, p2):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el OR de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los new id incluidos de p1 o p2

        """
        aux = self.or_posting(p1, p2)
        #añadimos todos los terminos a la lista
        #news = list(self.news.keys())
        #i = 0
        #j = 0

        #while i < len(p1) and j < len(p2):
            #if p1[i] == p2[j]:
                #i += 1
                #j += 1
                #news.remove(p1[i])
            #elif p1[i] <= p2[j]:
                #i += 1
                #news.remove(p1[i])
            #elif p1[i] >= p2[j]:
                #j += 1
                #news.remove(p1[i])
        #Terminos que no han sido añadidos aun al resultado
        #for k in range(i, len(p1)):
            #news.remove(p1[i])
        #for l in range(j, len(p2[l])):
            #news.remove(p1[i])
        return list(self.reverse_posting(aux))
        

    def minus_posting(self, p1, p2):
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se propone por si os es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los newid incluidos de p1 y no en p2

        """

        
        pass
        ########################################################
        ## COMPLETAR PARA TODAS LAS VERSIONES SI ES NECESARIO ##
        ########################################################





    #####################################
    ###                               ###
    ### PARTE 2.2: MOSTRAR RESULTADOS ###
    ###                               ###
    #####################################


    def solve_and_count(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra junto al numero de resultados 

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T

        """
        result = self.solve_query(query)
        print("%s\t%d" % (query, len(result)))
        return len(result)  # para verificar los resultados (op: -T)


    def solve_and_show(self, query):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra informacion de las noticias recuperadas.
        Consideraciones:

        - En funcion del valor de "self.show_snippet" se mostrara una informacion u otra.
        - Si se implementa la opcion de ranking y en funcion del valor de self.use_ranking debera llamar a self.rank_result

        param:  "query": query que se debe resolver.

        return: el numero de noticias recuperadas, para la opcion -T
        
        """
        result = self.solve_query(query) 
        if self.use_ranking:
            result = self.rank_result(result, query)   

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        separadores = "=" * 38
        # print(separadores)
        print('Query: {}'.format(query))
        print('Number of results: {}'.format(len(result)))
       
        #mostrar cada una de las noticias recuperadas 
        i=1
        for noticia in result:
            n = self.news[noticia] 
            idDoc = n['docid'] #documento donde se encuentra la noticia 
            pos = n['posicion']  #posición de la noticia dentro del documento
            fh = open(self.docs[idDoc])
            n = json.load(fh)[pos] #carga la noticia 
            if self.use_ranking:
               #si usa ranking, obtener score de la noticia
               score = self.jaccard(n,query) #COMPLETAR 
            else:
                score = 0 

            #comprobar si la función snippets está activada
            if self.show_snippet:
                print('#{}'.format(i))  #orden recuperación noticia
                print('Score: {}'.format(score)) 
                print(noticia)  #id noticia
                print('Date: {}'.format(n['date'])) 
                print('Title: {}'.format(n['title']))
                print('Keywords: {}'.format(n['keywords']))
                print('{}\n'.format(self.snippet(n,query)))
               
            
            else: 
               #si no se activa el snippet, mostrar una línea por noticia 
                print('#{} \t ({}) ({}) ({}) {} ({}) '.format(i,score,noticia,n['date'], n['title'], n['keywords']))
            
            i = i+1
            if not self.show_all and i > self.SHOW_MAX:
               #si no está activada la función show_all y ya se han mostrado todas las noticias permitidas(max), detener el bucle 
                break

        return result


    def jaccard(self, doc, query):
        """
        jaccard(A,B) =|A intersección B| / |A unión B| 
        param:  "doc": noticia
                "query": query procesada


        return: el peso documento-consulta (score)
         """
        #Primero, tokenizar la query
        query = query.replace('AND', '') 
        #AND y OR se eliminan ya que usaremos las funciones intersection y union 
        query = query.replace('OR', '')
        #NOT se une con la palabra para que no haga matching en el texto
        query = query.replace('NOT ', 'NOT')  
        query = set(self.tokenize(query))
        peso = 0

        #con MULTIFIELD se analizan: 'title, article, summary, keywords y date' 
         #en el Indexer básico solo se analiza el campo 'article' 
        d = doc['article']
        d = set(self.tokenize(d)) 
        peso = len(query.intersection(d)) / len(query.union(d))
        peso = round(peso, 5) #redondear para evitar problemas en el ranking
        return peso 

    def snippet(self,n,query):
        '''
       param:  'n': noticia cargada, con todos sus campos
               'query': query sin procesar
       return: parte de la noticia que contiene las palabras buscadas en la query
       '''
        
        pal = self.tokenize(n['article'])  #palabras noticia
        snippet = '' #el snippet que devolveremos al final 
        cont = 0 #contar las palabras de la query encontradas

        #Quitar todos los símbolos no necesarios en la query 
        query = query.replace('"', '') 
        query = query.replace('?', '')
        query = query.replace('*', '')
        query = query.replace('NOT ', 'NOT') #para que detecte el NOT 
        query = query.replace('(', '')
        query = query.replace(')', '')
       #MULTIFIELD: igual que con el NOT, modificar la query para que se note
        query = query.replace(':', 'AAABBBCCC')
        query = self.tokenize(query)


        for p in query:  #recorrer las palabras de la query 
            local = pal #por si es MULTIFIELD 
            if 'AAABBBCCC' in p:  #MULTIFIELD, consultar el field indicado 
                field, p = p.split('AAABBBCCC')   
                # No hay que tokenizar la fecha
                if field != 'date':
                    local = self.tokenize(n[field])

            if p in local:
                snippet_aux = ''
                pos = local.index(p) #posicion de la palabra en la noticia 
               # Mostrar (si se puede) la frase donde se encuentra la palabra buscada
                pos_i = pos - 3  #a la izquierda de la palabra 
                if pos_i < 0:  #revisar que la palabra no está al comienzo de la noticia 
                    pos_i = 0
                pos_d = pos + 6 #a la derecha de la palabra 
                if pos_d > len(local) - 1: #revisar que la palabra no está al final de la noticia
                    pos_d = len(local) - 1

               #Comprobar que no está al principio 
                if pos_i > 0:
                    snippet_aux = snippet_aux + '...'  #los puntos indican que no es la frase completa 

                snippet_aux += " ".join(local[pos_i:pos_d + 1])

                #Comprobar que no está al final
                if pos_d < len(local) - 1:
                    snippet_aux += '...'

                cont += 1
                #Comprobar que no hemos revisado todas las palabras de query aún
                if cont != len(query) - 1 and len(query) > 1 and len(snippet_aux.lstrip()) > 0:
                    snippet_aux += '\n'

                snippet += snippet_aux

        return snippet 

    
       


    def rank_result(self, result, query):
        """
        NECESARIO PARA LA AMPLIACION DE RANKING

        Ordena los resultados de una query.

        param:  "result": lista de resultados sin ordenar
                "query": query, puede ser la query original, la query procesada o una lista de terminos


        return: la lista de resultados ordenada

        """

        pass
        
        ###################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE RANKING ##
        ###################################################
        query = query.replace('AND', '')
        query = query.replace('OR', '')
        query = query.replace('NOT ', 'NOT')
        query = query.replace(':', ' ')
        res = []
        resul = [] 

        for n in result:
            ntc = self.news[n] 
            idDoc = ntc['docid'] #documento donde se encuentra la noticia 
            pos = ntc['posicion']  #posición de la noticia dentro del documento
            fh = open(self.docs[idDoc])
            aux = json.load(fh)[pos] #carga la noticia 

            res.append([n, self.jaccard(aux, query)])

        res.sort(key=lambda tup: tup[1], reverse=True)
        for i in res:
            resul.append(i[0]) 
        return resul