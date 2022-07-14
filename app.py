from unicodedata import name
from flask import Flask
from flask import render_template,request,redirect,url_for,flash
from flask import send_from_directory
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from datetime import datetime #Nos permitirá darle el nombre a la foto
import os #modulo del SO - permite entrar en carpeta

app = Flask(__name__)
app.secret_key="ClaveSecreta"

#conexion
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_BD']='Sistema'
mysql.init_app(app)

CARPETA = os.path.join('uploads') #referencia a la carpeta uploads
print(CARPETA)
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():
    sql = "SELECT * FROM `Sistema`.`empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor(cursor=DictCursor)
    cursor.execute(sql)
    empleados=cursor.fetchall()
    print(empleados)
    conn.commit()    
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor(cursor=DictCursor)
    cursor.execute("SELECT foto FROM `Sistema`.`empleados` WHERE id=%s",id)
    fila= cursor.fetchall()
 
    try:
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
    except:
        pass

    cursor.execute("DELETE FROM `Sistema`.`empleados` WHERE id=%s", (id))
    conn.commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor(cursor=DictCursor)
    cursor.execute("SELECT * FROM `Sistema`.`empleados` WHERE id=%s", (id))
    empleados=cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados=empleados)    

@app.route('/update', methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE `Sistema`.`empleados` SET nombre=%s, correo=%s WHERE id=%s;"
    datos=(_nombre,_correo,id)

    conn = mysql.connect()
    cursor = conn.cursor(cursor=DictCursor)
    now= datetime.now()
    tiempo= now.strftime("%Y%H%M%S")   

    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        print(nuevoNombreFoto)
        cursor.execute("SELECT foto FROM `Sistema`.`empleados` WHERE id=%s", id)
        fila= cursor.fetchall()

        try:
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        except:
            pass
                
        cursor.execute("UPDATE `Sistema`.`empleados` SET foto=%s WHERE id=%s;", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')    

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    if _nombre == '' or _correo == '' or _foto =='':
        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
    sql = "INSERT INTO `Sistema`.`empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos=(_nombre, _correo,nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor(cursor=DictCursor)
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')  
    

if __name__ == '__main__':
    app.run(debug=True)
