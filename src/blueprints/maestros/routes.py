from flask import Blueprint, jsonify, request
from database import mysql

maestros_bp = Blueprint('maestros', __name__, url_prefix='/api/maestros')



#GET : consultar todos los alumnos
@maestros_bp.route('', methods=['GET'])
def lista_maestros():
    cursor=None

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""SELECT idmaestro, nombre, apaterno, amaterno, correo FROM maestros""")
        datos = cursor.fetchall()
        maestros = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]

        return jsonify({
            'maestros':maestros,
            'mensaje':'lista de maestros'
            'exito': True
        }), 200

    except Exception:
        return jsonify({
            'mensaje': 'Error al consultar los maestros',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()