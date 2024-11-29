from flask import Flask, render_template, request, url_for, redirect
import pymysql

app = Flask(__name__)

# Configuración de la conexión a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'peps2'

def get_db_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    return connection

@app.route('/')
def home():
    return render_template('registro.html')

@app.route('/prueba')
def prueba():
    return render_template('prueba.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/consulta')
def consulta():
    try:
        conn = get_db_connection()
        cur = conn.cursor() 
        cur.execute("SELECT * FROM contacto")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', contactos=data)
    except Exception:
        return render_template('tabla.html', contactos=[])


@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']

        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # Consulta preparada para prevenir inyección SQL
                sql = "INSERT INTO `contacto` (`nombre`, `telefono`, `correo`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nombre, telefono, correo))
                connection.commit()
            return redirect(url_for('consulta'))
        except pymysql.Error as error:
            print(error)
            return "Error al agregar contacto", 500
        finally:
            connection.close()
            
@app.route('/delete/<string:id>')
def delete_contact(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM contacto WHERE ide = %s", (id,))
            conn.commit()
        return redirect(url_for('consulta'))
    except Exception as e:
        print(f"Error al eliminar contacto: {e}")
        return "Error al eliminar el contacto"
    finally:
        conn.close()


#editar
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_contact(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if request.method == 'POST':
                # Recuperar datos del formulario
                nombre = request.form['nombre']
                telefono = request.form['telefono']
                correo = request.form['correo']

                # Consulta para actualizar el contacto con el ID específico
                sql = "UPDATE `contacto` SET `nombre`=%s, `telefono`=%s, `correo`=%s WHERE `ide`=%s"
                cursor.execute(sql, (nombre, telefono, correo, id))
                conn.commit()

                return redirect(url_for('consulta'))

            # Recuperar el contacto para mostrar en el formulario de edición
            cursor.execute("SELECT * FROM `contacto` WHERE `ide` = %s", (id,))
            contact = cursor.fetchone()

            # Si el contacto no existe, manejar el error
            if not contact:
                return "Contacto no encontrado", 404

            # Renderizar el formulario de edición con los datos del contacto
            return render_template('editar.html', contact=contact)

    except pymysql.Error as error:
        print(f"Error al editar contacto: {error}")
        return "Error al obtener o editar contacto", 500
    finally:
        conn.close()

@app.route('/validar', methods=['GET', 'POST'])
def validar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']

        if not nombre or not correo:
            error = "Por favor, complete todos los campos."
            return render_template('validar.html', error=error)

        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Consulta para verificar usuario
                sql = "SELECT * FROM contacto WHERE nombre = %s AND correo = %s"
                cursor.execute(sql, (nombre, correo))
                contacto = cursor.fetchone()

                if contacto:
                    return redirect(url_for('consulta'))
                else:
                    error = "Nombre o correo no válido. Por favor, inténtelo de nuevo."
                    return render_template('validar.html', error=error)
        except pymysql.Error as e:
            print(f"Error en la consulta: {e}")
            return "Error en el servidor", 500
        finally:
            conn.close()

    return 'usuario invalido'


@app.route('/reserva', methods=['GET', 'POST'])
def gestionar_reservas():
    if request.method == 'POST':
        # Inserción de datos en la tabla `reserva`
        usuario = request.form.get("usuario")
        estado = request.form.get("estado")
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                # Consulta preparada para prevenir inyección SQL
                sql = "INSERT INTO `reserva` (`usuario`, `estado`) VALUES (%s, %s)"
                cursor.execute(sql, (usuario, estado))
                reservas = cursor.fetchone()
                contactos = cursor.fetchone()
                connection.commit()
            return redirect(url_for('gestionar_reservas'))  # Redirige al método GET tras insertar
        except pymysql.Error as error:
            print("Error al insertar datos:", error)
            return "Error al agregar contacto", 500
        finally:
            connection.close()

    # Manejo del método GET: visualizar contactos y reservas
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Obtener contactos
            cursor.execute("SELECT * FROM contacto")
            contactos = cursor.fetchall()

            # Obtener reservas
            cursor.execute("SELECT * FROM reserva")
            reservas = cursor.fetchall()

        # Renderiza la plantilla con los datos combinados
        return render_template('estados.html', contactos=contactos, reservas=reservas)
    except pymysql.Error as error:
        print("Error al consultar datos:", error)
        return render_template('estado.html', contactos=[], reservas=[])  # Renderiza con datos vacíos en caso de error
    finally:
        connection.close()

        
@app.route('/delete2/<string:id>')
def delete_contact2(id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM reserva WHERE usuario = %s", (id))
            conn.commit()
        return redirect(url_for('consulta'))
    except Exception as e:
        print(f"Error al eliminar contacto: {e}")
        return "Error al eliminar el contacto"
    finally:
        conn.close()



if __name__ == '__main__':
    app.run(debug=True)