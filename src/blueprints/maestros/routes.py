
from flask import Blueprint, jsonify, request
from database import mysql

maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)


def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))


# GET: consultar todos los maestros
@maestros_bp.route('', methods=['GET'])
def lista_maestros():
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT idmaestro, nombre, apaterno, amaterno, correo
            FROM maestros
        """)

        datos = cursor.fetchall()

        maestros = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]

        return jsonify({
            'maestros': maestros,
            'mensaje': 'Lista de maestros',
            'exito': True
        }), 200

    except Exception as e:
        print("ERROR AL CONSULTAR MAESTROS:", e)

        return jsonify({
            'mensaje': 'Error al consultar los maestros',
            'detalle': str(e),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# Función: buscar un maestro por idmaestro
def leer_maestro_bd(idmaestro):
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT idmaestro, nombre, apaterno, amaterno, correo
            FROM maestros
            WHERE idmaestro = %s
        """, (idmaestro,))

        datos = cursor.fetchone()

        if datos is not None:
            return fila_a_diccionario(cursor, datos)

        return None

    finally:
        if cursor is not None:
            cursor.close()


# GET: consultar un maestro por idmaestro
@maestros_bp.route('/<int:idmaestro>', methods=['GET'])
def leer_maestro(idmaestro):
    try:
        maestro = leer_maestro_bd(idmaestro)

        if maestro is not None:
            return jsonify({
                'maestro': maestro,
                'mensaje': 'Maestro encontrado',
                'exito': True
            }), 200

        return jsonify({
            'maestro': None,
            'mensaje': 'Maestro no encontrado',
            'exito': False
        }), 404

    except Exception as e:
        print("ERROR AL BUSCAR MAESTRO:", e)

        return jsonify({
            'mensaje': 'Error al consultar el maestro',
            'exito': False
        }), 500


# POST: registrar un maestro
@maestros_bp.route('', methods=['POST'])
def registrar_maestro():
    cursor = None

    try:
        datos = request.get_json()

        if not isinstance(datos, dict):
            return jsonify({
                'mensaje': 'Debes enviar los datos en formato JSON',
                'exito': False
            }), 400

        campos = [
            'idmaestro', 'nombre', 'apaterno',
            'amaterno', 'correo'
        ]

        for campo in campos:
            if campo not in datos or datos[campo] is None:
                return jsonify({
                    'mensaje': 'Falta el campo {}'.format(campo),
                    'exito': False
                }), 400

        maestro = leer_maestro_bd(datos['idmaestro'])

        if maestro is not None:
            return jsonify({
                'mensaje': 'El maestro ya existe',
                'exito': False
            }), 409

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO maestros
            (idmaestro, nombre, apaterno, amaterno, correo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datos['idmaestro'],
            datos['nombre'],
            datos['apaterno'],
            datos['amaterno'],
            datos['correo']
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro registrado correctamente',
            'exito': True
        }), 201

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL REGISTRAR MAESTRO:", e)

        return jsonify({
            'mensaje': 'Error al registrar el maestro',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# PUT: actualizar un maestro por idmaestro
@maestros_bp.route('/<int:idmaestro>', methods=['PUT'])
def actualizar_maestro(idmaestro):
    cursor = None

    try:
        maestro = leer_maestro_bd(idmaestro)

        if maestro is None:
            return jsonify({
                'mensaje': 'Maestro no encontrado',
                'exito': False
            }), 404

        datos = request.get_json()

        if not isinstance(datos, dict):
            return jsonify({
                'mensaje': 'Debes enviar los datos en formato JSON',
                'exito': False
            }), 400

        campos = ['nombre', 'apaterno', 'amaterno', 'correo']

        for campo in campos:
            if campo not in datos or datos[campo] is None:
                return jsonify({
                    'mensaje': 'Falta el campo {}'.format(campo),
                    'exito': False
                }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE maestros
            SET nombre = %s,
                apaterno = %s,
                amaterno = %s,
                correo = %s
            WHERE idmaestro = %s
        """, (
            datos['nombre'],
            datos['apaterno'],
            datos['amaterno'],
            datos['correo'],
            idmaestro
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro actualizado correctamente',
            'exito': True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL ACTUALIZAR MAESTRO:", e)

        return jsonify({
            'mensaje': 'Error al actualizar el maestro',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# DELETE: eliminar un maestro por idmaestro
@maestros_bp.route('/<int:idmaestro>', methods=['DELETE'])
def eliminar_maestro(idmaestro):
    cursor = None

    try:
        maestro = leer_maestro_bd(idmaestro)

        if maestro is None:
            return jsonify({
                'mensaje': 'Maestro no encontrado',
                'exito': False
            }), 404

        cursor = mysql.connection.cursor()

        cursor.execute("""
            DELETE FROM maestros
            WHERE idmaestro = %s
        """, (idmaestro,))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro eliminado correctamente',
            'exito': True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL ELIMINAR MAESTRO:", e)

        return jsonify({
            'mensaje': 'Error al eliminar el maestro',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
