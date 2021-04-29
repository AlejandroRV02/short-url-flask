from flask import Flask, render_template, url_for, flash, request, redirect, jsonify

from flask_mysql_connector import MySQL

import shortuuid

#Inicializar app
app  = Flask(__name__)

#Endpoint
endpoint = 'http://www.short.url'

#Conexion a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'short_url'

#Iniciar DB
mysql = MySQL(app)

##Llave para flash
app.secret_key = 'C1v3S3cr3t'

#Rutas
@app.route('/', methods=['GET'])
def inicio():
    try:
        return render_template('index.html'),200
    except:
        return render_template('404.html'), 404

#Ruta enlace corto
@app.route('/short_url', methods=['POST'])
def short_url():
    try:
        if request.method == 'POST':
            #Capturamos la url
            url = request.form['url']
            
            #Cursor
            cursor = mysql.connection.cursor()

            while True:
                #Enlace corto 
                short_url = shortuuid.ShortUUID().random(length=7)

                #Verificamos si existe en la base de datos
                cursor.execute('SELECT * FROM urls WHERE short_url = BINARY %s', (short_url,))

                if not cursor.fetchone():
                    break
            
            cursor.execute('SELECT short_url FROM urls WHERE url = BINARY %s', (url,)) 
            data = cursor.fetchone()
            if data:
                flash(endpoint + '/' + data[0])
                return redirect(url_for('inicio')), 302
            
            #Ingresamos en la BD la url
            cursor.execute('INSERT INTO urls(url, short_url) VALUES (%s, %s)', (url, short_url))

            #Guardamos los cambios en Bd
            mysql.connection.commit()

            #Cerrar conexion
            cursor.close()

            new_url = endpoint + '/' + short_url

            flash(new_url)
            return redirect(url_for('inicio')), 302
    except:
        return render_template('404.html'), 404


#Ruta para redireccionar a pagina original
@app.route('/<id>')
def get_url(id):
    try:
        cursor = mysql.connection.cursor()

        cursor.execute('SELECT url FROM urls WHERE short_url = BINARY %s', (id,))

        data = cursor.fetchone()

        cursor.close()

        return render_template('ads.html', url=data[0]), 200


    except:
        return render_template('404.html'), 404


#Levantar app
if __name__ == '__main__':
    app.run(port=80, debug=True)