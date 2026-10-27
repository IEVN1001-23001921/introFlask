
from flask import Blueprint, jsonify, request
from database import mysql

alumnos_bp = Blueprint(
    'alumnos',
    __name__,
    url_prefix='/api/alumnos'
)


def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))


# GET: consultar todos los alumnos
@alumnos_bp.route('', methods=['GET'])
def lista_alumnos():
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT matricula, nombre, apaterno, amaterno, correo
            FROM alumnos
        """)

        datos = cursor.fetchall()

        alumnos = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]

        return jsonify({
            'alumnos': alumnos,
            'mensaje': 'Lista de alumnos',
            'exito': True
        }), 200

    except Exception as e:
        print("ERROR REAL:", e)

        return jsonify({
            'mensaje': 'Error al consultar los alumnos',
            'detalle': str(e),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# Función: buscar un alumno por matrícula
def leer_alumno_bd(matricula):
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        sql = """
            SELECT matricula, nombre, apaterno, amaterno, correo
            FROM alumnos
            WHERE matricula = %s
        """

        cursor.execute(sql, (matricula,))
        datos = cursor.fetchone()

        if datos is not None:
            return fila_a_diccionario(cursor, datos)

        return None

    finally:
        if cursor is not None:
            cursor.close()


# GET: consultar un alumno por matrícula
@alumnos_bp.route('/<mat>', methods=['GET'])
def leer_alumno(mat):
    try:
        alumno = leer_alumno_bd(mat)

        if alumno is not None:
            return jsonify({
                'alumno': alumno,
                'mensaje': 'Alumno encontrado',
                'exito': True
            }), 200

        return jsonify({
            'alumno': None,
            'mensaje': 'Alumno no encontrado',
            'exito': False
        }), 404

    except Exception as e:
        print("ERROR AL BUSCAR:", e)

        return jsonify({
            'mensaje': 'Error al consultar el alumno',
            'exito': False
        }), 500


# POST: registrar un alumno
@alumnos_bp.route('', methods=['POST'])
def registrar_alumno():
    cursor = None

    try:
        datos = request.get_json()

        if not isinstance(datos, dict):
            return jsonify({
                'mensaje': 'Debes enviar los datos en formato JSON',
                'exito': False
            }), 400

        campos = [
            'matricula', 'nombre', 'apaterno',
            'amaterno', 'correo'
        ]

        for campo in campos:
            if campo not in datos or datos[campo] is None:
                return jsonify({
                    'mensaje': 'Falta el campo {}'.format(campo),
                    'exito': False
                }), 400

        alumno = leer_alumno_bd(datos['matricula'])

        if alumno is not None:
            return jsonify({
                'mensaje': 'Alumno ya existe, no se permiten duplicados',
                'exito': False
            }), 409

        cursor = mysql.connection.cursor()

        sql = """
            INSERT INTO alumnos
            (matricula, nombre, apaterno, amaterno, correo)
            VALUES (%s, %s, %s, %s, %s)
        """

        valores = (
            datos['matricula'],
            datos['nombre'],
            datos['apaterno'],
            datos['amaterno'],
            datos['correo']
        )

        cursor.execute(sql, valores)
        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Alumno registrado',
            'exito': True
        }), 201

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL REGISTRAR:", e)

        return jsonify({
            'mensaje': 'Error al registrar el alumno',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# PUT: actualizar un alumno por matrícula
@alumnos_bp.route('/<mat>', methods=['PUT'])
def actualizar_alumno(mat):
    cursor = None

    try:
        alumno = leer_alumno_bd(mat)

        if alumno is None:
            return jsonify({
                'mensaje': 'Alumno no encontrado',
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

        sql = """
            UPDATE alumnos
            SET nombre = %s,
                apaterno = %s,
                amaterno = %s,
                correo = %s
            WHERE matricula = %s
        """

        valores = (
            datos['nombre'],
            datos['apaterno'],
            datos['amaterno'],
            datos['correo'],
            mat
        )

        cursor.execute(sql, valores)
        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Alumno actualizado',
            'exito': True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL ACTUALIZAR:", e)

        return jsonify({
            'mensaje': 'Error al actualizar el alumno',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# DELETE: eliminar un alumno por matrícula
@alumnos_bp.route('/<mat>', methods=['DELETE'])
def eliminar_alumno(mat):
    cursor = None

    try:
        alumno = leer_alumno_bd(mat)

        if alumno is None:
            return jsonify({
                'mensaje': 'Alumno no encontrado',
                'exito': False
            }), 404

        cursor = mysql.connection.cursor()

        sql = "DELETE FROM alumnos WHERE matricula = %s"
        cursor.execute(sql, (mat,))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Alumno eliminado',
            'exito': True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL ELIMINAR:", e)

        return jsonify({
            'mensaje': 'Error al eliminar el alumno',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
