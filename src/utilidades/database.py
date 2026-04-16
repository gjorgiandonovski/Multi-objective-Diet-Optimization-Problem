import os
from dotenv import load_dotenv
import mysql.connector  # MySQL library

# Load environment variables
load_dotenv()

def conexion_basedatos():
    """Create and return the database connection."""
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'raise_on_warnings': True
    }
    return mysql.connector.connect(**config)


def comida_basedatos():
    """Fetch food rows from the `comida` table as a list of dictionaries."""

    cnx = conexion_basedatos()
    cursor = cnx.cursor(dictionary=True)

    query = "SELECT nombre, grupo, calorias, grasas, proteinas, carbohidratos FROM comida"
    cursor.execute(query)
    comida_basedatos = cursor.fetchall()

    cursor.close()
    cnx.close()
    
    return comida_basedatos


def sujetos_basedatos():
    """Fetch subjects together with their likes, dislikes, and allergies."""

    cnx = conexion_basedatos()
    cursor = cnx.cursor(dictionary=True)

    # Fetch the basic subject information
    query_sujetos = """
    SELECT sp.id AS sujeto_id, sp.edad, sc.calorias 
    FROM sujetos sp
    JOIN sujetos_calorias sc ON sp.id = sc.id
    """
    cursor.execute(query_sujetos)
    sujetos = cursor.fetchall()

    # Fetch likes, dislikes, and allergies
    query_gustos = "SELECT sujeto_id, grupo FROM sujetos_gustos"
    query_disgustos = "SELECT sujeto_id, grupo FROM sujetos_disgustos"
    query_alergias = "SELECT sujeto_id, grupo FROM sujetos_alergias"

    cursor.execute(query_gustos)
    gustos = cursor.fetchall()

    cursor.execute(query_disgustos)
    disgustos = cursor.fetchall()

    cursor.execute(query_alergias)
    alergias = cursor.fetchall()

    # Build the output structure
    sujetos_dict = {}
    for sujeto in sujetos:
        sujeto_id = sujeto["sujeto_id"]
        sujetos_dict[sujeto_id] = {
            "calorias": sujeto["calorias"],
            "edad": sujeto["edad"],
            "gustos": [],
            "disgustos": [],
            "alergias": []
        }

    # Attach likes to each subject
    for gusto in gustos:
        sujetos_dict[gusto["sujeto_id"]]["gustos"].append(gusto["grupo"])

    # Attach dislikes to each subject
    for disgusto in disgustos:
        sujetos_dict[disgusto["sujeto_id"]]["disgustos"].append(disgusto["grupo"])

    # Attach allergies to each subject
    for alergia in alergias:
        sujetos_dict[alergia["sujeto_id"]]["alergias"].append(alergia["grupo"])

    cursor.close()
    cnx.close()

    return list(sujetos_dict.values())
