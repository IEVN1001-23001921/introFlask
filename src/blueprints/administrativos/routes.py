
from flask import Blueprint, jsonify, request
from database import mysql

administrativos_bp = Blueprint(
    'administrativos',
    __name__,
    url_prefix='/api/administrativos'
)


def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))


# GET: consultar todos los administrativos
@administrativos_bp.route('', methods=['GET'])
def lista_administrativos():
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT numempleado, nombre, apellidos,
                   telefono, correo, departamento
            FROM administrativos
        """)

        datos = cursor.fetchall()

        administrativos = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]

        return jsonify({
            'administrativos': administrativos,
            'mensaje': 'Lista de administrativos',
            'exito': True
        }), 200

    except Exception as e:
        print("ERROR AL CONSULTAR ADMINISTRATIVOS:", e)

        return jsonify({
            'mensaje': 'Error al consultar los administrativos',
            'detalle': str(e),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# Función: buscar un administrativo por número de empleado
def leer_administrativo_bd(numempleado):
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT numempleado, nombre, apellidos,
                   telefono, correo, departamento
            FROM administrativos
            WHERE numempleado = %s
        """, (numempleado,))

        datos = cursor.fetchone()

        if datos is not None:
            return fila_a_diccionario(cursor, datos)

        return None

    finally:
        if cursor is not None:
            cursor.close()


# GET: consultar un administrativo por número de empleado
@administrativos_bp.route('/<numempleado>', methods=['GET'])
def leer_administrativo(numempleado):
    try:
        administrativo = leer_administrativo_bd(numempleado)

        if administrativo is not None:
            return jsonify({
                'administrativo': administrativo,
                'mensaje': 'Administrativo encontrado',
                'exito': True
            }), 200

        return jsonify({
            'administrativo': None,
            'mensaje': 'Administrativo no encontrado',
            'exito': False
        }), 404

    except Exception as e:
        print("ERROR AL BUSCAR ADMINISTRATIVO:", e)

        return jsonify({
            'mensaje': 'Error al consultar el administrativo',
            'exito': False
        }), 500


# POST: registrar un administrativo
@administrativos_bp.route('', methods=['POST'])
def registrar_administrativo():
    cursor = None

    try:
        datos = request.get_json()

        if not isinstance(datos, dict):
            return jsonify({
                'mensaje': 'Debes enviar los datos en formato JSON',
                'exito': False
            }), 400

        campos = [
            'numempleado', 'nombre', 'apellidos',
            'telefono', 'correo', 'departamento'
        ]

        for campo in campos:
            if campo not in datos or datos[campo] is None:
                return jsonify({
                    'mensaje': 'Falta el campo {}'.format(campo),
                    'exito': False
                }), 400

        administrativo = leer_administrativo_bd(
            datos['numempleado']
        )

        if administrativo is not None:
            return jsonify({
                'mensaje': 'El número de empleado ya existe',
                'exito': False
            }), 409

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO administrativos
            (numempleado, nombre, apellidos, telefono,
             correo, departamento)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datos['numempleado'],
            datos['nombre'],
            datos['apellidos'],
            datos['telefono'],
            datos['correo'],
            datos['departamento']
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Administrativo registrado correctamente',
            'exito': True
        }), 201

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL REGISTRAR ADMINISTRATIVO:", e)

        return jsonify({
            'mensaje': 'Error al registrar el administrativo',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# PUT: actualizar un administrativo
@administrativos_bp.route('/<numempleado>', methods=['PUT'])
def actualizar_administrativo(numempleado):
    cursor = None

    try:
        administrativo = leer_administrativo_bd(numempleado)

        if administrativo is None:
            return jsonify({
                'mensaje': 'Administrativo no encontrado',
                'exito': False
            }), 404

        datos = request.get_json()

        if not isinstance(datos, dict):
            return jsonify({
                'mensaje': 'Debes enviar los datos en formato JSON',
                'exito': False
            }), 400

        campos = [
            'nombre', 'apellidos', 'telefono',
            'correo', 'departamento'
        ]

        for campo in campos:
            if campo not in datos or datos[campo] is None:
                return jsonify({
                    'mensaje': 'Falta el campo {}'.format(campo),
                    'exito': False
                }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE administrativos
            SET nombre = %s,
                apellidos = %s,
                telefono = %s,
                correo = %s,
                departamento = %s
            WHERE numempleado = %s
        """, (
            datos['nombre'],
            datos['apellidos'],
            datos['telefono'],
            datos['correo'],
            datos['departamento'],
            numempleado
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Administrativo actualizado correctamente',
            'exito': True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL ACTUALIZAR ADMINISTRATIVO:", e)

        return jsonify({
            'mensaje': 'Error al actualizar el administrativo',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# DELETE: eliminar un administrativo
@administrativos_bp.route('/<numempleado>', methods=['DELETE'])
def eliminar_administrativo(numempleado):
    cursor = None

    try:
        administrativo = leer_administrativo_bd(numempleado)

        if administrativo is None:
            return jsonify({
                'mensaje': 'Administrativo no encontrado',
                'exito': False
            }), 404

        cursor = mysql.connection.cursor()

        cursor.execute("""
            DELETE FROM administrativos
            WHERE numempleado = %s
        """, (numempleado,))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Administrativo eliminado correctamente',
            'exito': True
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        print("ERROR AL ELIMINAR ADMINISTRATIVO:", e)

        return jsonify({
            'mensaje': 'Error al eliminar el administrativo',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
