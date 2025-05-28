from neo4j import GraphDatabase


#Importacion de librerias
from neo4j import GraphDatabase
#Datos de conexión
URI="neo4j+ssc://86ebfe37.databases.neo4j.io"
AUTH=("neo4j","vtzbcvao9ALFrF2J6QlGtDKt5cl-r7KY5-9Oh80r7LY")
AURA_INSTANCEID="f955a66e"
AURA_INSTANCENAME="Instance01"
#Conexión


driver = GraphDatabase.driver(URI, auth=AUTH)

# Test the connection with a simple query
def test_connection(driver):
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful' AS message")
        print(result.single()["message"])


#test_connection(driver)


def returnId(driver, pieza, rompecabezas):
    result = driver.execute_query(
        """
        MATCH (p:PIEZA {id: $pieza})-[per:pertenece_a]-(r:ROMPECABEZAS {descripcion: $rompecabezas})
        RETURN elementId(p) AS id
        """, pieza = pieza, rompecabezas = rompecabezas
    )
    return result[0][0]['id'] if result else None

#print(returnId(driver, 1, "avioncito"))

def getPiezasConectadas(driver, pieza):

    def format(record):
        return {"pieza_ini":record["pieza_id"], "conector_ini":record["conector_in"], "pieza_fin":record["pieza_conectada"], "conector_fin":record["conector_out"]}
            
        
    result = driver.execute_query(
        """
        MATCH (p:PIEZA)-[r:conecta_a]-(p2:PIEZA)
        WHERE elementId(p) = $pieza
        RETURN p.id AS pieza_id, r.conectorIn AS conector_in, r.conectorFin AS conector_out, p2.id AS pieza_conectada, elementId(p2) AS pieza_conectada_id
        """, pieza=pieza
    )
    return [format(record) for record in result[0]] if result else []


def getNumPiezas(driver, rompecabezas):
    result = driver.execute_query(
        """
        MATCH (r:ROMPECABEZAS {descripcion: $rompecabezas})
        RETURN r.numPiezas as numPiezas
        """, rompecabezas=rompecabezas
    )
    return result[0][0]['numPiezas'] if result else 0

#print(getNumPiezas(driver, "avioncito"))

def resolver(driver, rompecabezas, piezaIni):
    """p
    
    """
    numPiezas = getNumPiezas(driver, rompecabezas)
    piezas_puestas = []
    stack = getPiezasConectadas(driver, returnId(driver, piezaIni, rompecabezas))
    ruta = []
    notFound = True
    connectionsLeft = True
   

    while notFound and connectionsLeft:
        propuesta = stack[0] if stack else None

        if not propuesta:
            connectionsLeft = False
            break

        # Ordenar: primero los que NO tienen None en los conectores
        stack.sort(key=lambda x: (x["conector_ini"] is None or x["conector_fin"] is None))
        #print(propuesta)
        pieza_propuesta = propuesta["pieza_fin"]

        if pieza_propuesta not in piezas_puestas:
            ruta.append(propuesta)
            piezas_puestas.append(pieza_propuesta)
            nuevos_vecinos = getPiezasConectadas(driver, returnId(driver, pieza_propuesta, rompecabezas))
            stack += nuevos_vecinos

            # Comprobación de finalización
            if len(piezas_puestas) == numPiezas:
                notFound = False
        else:
            stack.remove(propuesta)
            if not stack:
                connectionsLeft = False

    return ruta 

def rutaPrinter(ruta):
    """Imprime la ruta de forma legible"""
    for paso in ruta:
        if paso["conector_ini"] is None or paso["conector_fin"] is None:
            print(f"Encaje la pieza '{paso['pieza_fin']}' en la pieza '{paso['pieza_ini']}' sin conectores.")
        else:
            print(f"Conecte el conector '{paso['conector_ini']}' de la pieza '{paso['pieza_ini']}' con el conector '{paso['conector_fin']}' de la pieza '{paso['pieza_fin']}'.")

# Example usage

ruta = resolver(driver, "2 delfines y una ballena", 1)

rutaPrinter(ruta)