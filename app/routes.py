from flask import render_template, flash, redirect, session, request, url_for
from app import app, logic
from app.logic import clsSqlInsert, clsSqlDelete, clsSqlUpdate, clsSqlSelect
from app.forms import LoginForm, RegisterForm, ModifyForm, Lugar

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def bienvenido():
    if session.get('logueado'):
        return redirect('/principal')
    else:        
        form = LoginForm()
        if form.validate_on_submit():
            SqlSelect = clsSqlSelect.SqlSelect()
            email=form.email.data
            password=form.password.data
            if SqlSelect.login(email, password):
                session.pop('invalid_user', None)
                session['logueado']=True
                session['id_usuario'] = SqlSelect.userdata['id_usuario']
                session['email'] = SqlSelect.userdata['email']
                session['nombre'] = SqlSelect.userdata['nombre']
                session['tipo'] = SqlSelect.userdata['tipo']
                del SqlSelect
                return redirect('/principal')
            else:
                flash('Usuario y/o contraseña inválidos')                
                session['invalid_user']="true"               
                return redirect('/')                    
    return render_template('bienvenido.html', title='¡Bienvenido a PuntaGuia!', form=form)

#TRY-CATCH APAGADO
@app.route('/index/registro', methods=['GET', 'POST'])
def registro():
    if session.get('logueado'):
        return redirect('/principal')   
    else:
        nuevo = request.args.to_dict()
        form = RegisterForm()
        if form.validate_on_submit():
            #try:
            SqlSelect = clsSqlSelect.SqlSelect()                
            SqlInsert = clsSqlInsert.SqlInsert()
            SqlInsert.crearUsuario(form.email.data,
                                    form.nombre.data,
                                    form.password.data,
                                    nuevo['tipo'],
                                    SqlSelect.conseguir_ultimo_idMasUno(),
                                    form.edad.data,
                                    form.pais.data,
                                    form.nombreEmpresa.data
                                    )
            session.clear()
            return redirect('/index') 
            #except:    
            #    return redirect('/index')
    return render_template('registro.html', title="Registrar un nuevo usuario", form=form, tipo=nuevo['tipo'])

@app.route('/principal')
def index():
    if session.get('logueado'):
        SqlSelect = clsSqlSelect.SqlSelect()
        if session['tipo']=='turista':
            listalugares = SqlSelect.conseguir_categorias()
            pass
        else:
            try:
                listalugares = SqlSelect.listarLugares(session['id_usuario'])
            except:
                listalugares={}      
    else:
        session.clear()
        return redirect('/')
    return render_template('principal.html', title="Página principal", lugares=listalugares)

@app.route("/principal/categoria", methods=['GET', 'POST'])
def categoria():
    if (not session.get('logueado')):
        session.clear()
        return redirect('/')
    elif (not session['tipo']=='turista'):
        return redirect('/principal')
    else:
        #try:
        categoria = request.args.to_dict()
        SqlSelect = clsSqlSelect.SqlSelect()
        lugares = SqlSelect.conseguir_lugares(categoria['categoria'])
        lista = SqlSelect.conseguir_PorVisitar(session['id_usuario'])
        if not bool(lista):
            lista = ['a']
        #except:
        #    return redirect("/principal")        
    return render_template('categoria.html', title='Explorando', lugares=lugares, lista=lista, cat=categoria['categoria'])

#TRY-CATCH APAGADO
@app.route("/principal/categoria/agregar", methods=['GET', 'POST'])
def logicaAgregarAPorVisitar():
    if (not session.get('logueado')):
        session.clear()
        return redirect('/')
    elif (not session['tipo']=='turista'):
        return redirect('/principal')
    else:
        #try:
        datos = request.args.to_dict()
        SqlSelect = clsSqlSelect.SqlSelect()
        SqlInsert = clsSqlInsert.SqlInsert()
        orden = SqlSelect.conseguir_orden(session['id_usuario'])
        SqlInsert.insertarAPorVisitar(session['id_usuario'], datos['ide'], str(orden))
        return redirect(url_for("categoria", categoria=datos['categoria']))
        #except:
        #    return redirect('/principal')

#TRY-CATCH APAGADO
@app.route("/principal/categoria/eliminar", methods=['GET', 'POST'])
def logicaEliminarDePorVisitar():
    if (not session.get('logueado')):
        session.clear()
        return redirect('/')
    elif (not session['tipo']=='turista'):
        return redirect('/principal')
    else:
        #try:
        datos = request.args.to_dict()
        SqlDelete = clsSqlDelete.SqlDelete()
        SqlDelete.borrarDePorVisitar(session['id_usuario'], datos['ide'])
        if len(datos) > 2:
            return redirect(url_for("por_visitar"))
        else:
            return redirect(url_for("categoria", categoria=datos['categoria']))
        #except:
        #    return redirect('/principal')

@app.route('/principal/usuario')
def usuario():
    if not session.get('logueado'):
        session.clear()
        return redirect('/')
    return render_template('usuario.html', title='Datos de la cuenta')

#TRY-CATCH APAGADO
@app.route('/principal/usuario/modificar', methods=['GET','POST'])
def modificarUsuario():
    if not session.get('logueado'):
        session.clear()
        return redirect('/')
    else:
        form=ModifyForm()
        #try:
        if form.validate_on_submit():
            nombre = form.nombre.data
            password = form.password.data
            edad = form.edad.data
            pais = form.pais.data
            nombreEmpresa = form.nombreEmpresa.data
            SqlUpdate = clsSqlUpdate.SqlUpdate()
            SqlUpdate.actualizarUsuario(nombre, password, session['id_usuario'], session['tipo'], edad, pais, nombreEmpresa)
            session['nombre'] = nombre
            return redirect("/principal/usuario")
        SqlSelect = clsSqlSelect.SqlSelect()
        userdata = SqlSelect.listarDatosUsuario(session['id_usuario'], session['tipo'])
        #except:
        #    return redirect('/')
    return render_template('modificar_usuario.html', title="Modificar datos de la cuenta", form=form, contrasena=userdata['contrasena'], edad=userdata['edad'], pais=userdata['pais_origen'], nombreEmpresa=userdata['nombre']) 

#TRY-CATCH APAGADO
@app.route('/principal/agregar_lugar', methods=['GET','POST'])
def agregar_lugar():
    if (not session.get('logueado')):
        session.clear()
        return redirect('/')
    elif (not session['tipo']=='empresa'):
        return redirect('/principal')
    else:
        form=Lugar()
        SqlSelect = clsSqlSelect.SqlSelect()
        categorias = SqlSelect.conseguir_categorias()
        form.categoria.choices = [(categoria['idc'], categoria['nombre']) for categoria in categorias]
        #try:
        if request.method=='POST':
            nombre = form.nombre.data
            descripcion = form.descripcion.data
            ubicacion = form.ubicacion.data
            categoria = form.categoria.data
            tipo = form.tipo.data
            horario = form.horario.data
            fecha = form.fecha.data
            
            #INSERTA EN lugar
            SqlInsert = clsSqlInsert.SqlInsert()
            SqlInsert.insertarLugar(nombre, descripcion, ubicacion, tipo, horario, fecha)
            
            #CONSIGUE ide DE lugar
            ide = SqlSelect.conseguir_ide(nombre)

            #INSERTA EN pertenece_a BASANDOSE EN EL ide
            SqlInsert.insertar_pertenece_a(ide,categoria)

            #INSERTA EN tiene
            SqlInsert.insertar_tiene(ide,session['id_usuario'])

            return redirect("/principal")
        #except:
        #    return redirect('/')      
    return render_template('agregar_lugar.html', title="Registrar un establecimiento o evento", form=form)

#TRY-CATCH APAGADO
@app.route('/principal/eliminar_lugar', methods=['GET','POST'])
def eliminar_lugar():
    if (not session.get('logueado')):
        session.clear()
        return redirect('/')
    elif (not session['tipo']=='empresa'):
        return redirect('/principal')
    else:
        #try:
        lugar = request.args.to_dict()
        nombreLugar=lugar['nombre']
        SqlSelect = clsSqlSelect.SqlSelect()
        ide = SqlSelect.conseguir_ide(nombreLugar)
        tiene = SqlSelect.conseguir_tabla_tiene(ide, session['id_usuario'])
        datos = SqlSelect.conseguir_datos_lugar(nombreLugar)
        if request.method=='POST':
            SqlDelete = clsSqlDelete.SqlDelete()
            SqlDelete.borrarLugar(ide)
            return redirect('/principal')
        if not bool(tiene):
            return redirect('/principal')
        #except:
        #    print('Algo malo ocurrió')
        #    return redirect('/principal')
    return render_template('eliminar_lugar.html', title="Eliminar establecimiento/evento", ide=ide, lugar=datos) 

#TRY-CATCH APAGADO
@app.route('/principal/modificar_lugar', methods=['GET','POST'])
def modificar_lugar():
    if (not session.get('logueado')):
        session.clear()
        return redirect('/')
    elif (not session['tipo']=='empresa'):
        return redirect('/principal')
    else:
        #try:
        nom = request.args.to_dict()
        SqlSelect = clsSqlSelect.SqlSelect()
        lugar = SqlSelect.conseguir_datos_lugar(nom['nombre'])
        pertenece_a = SqlSelect.conseguir_datos_pertenece_a(lugar['ide'])
        form = Lugar(categoria=pertenece_a['idc'], tipo=lugar['tipo'], descripcion=lugar['descripcion'])
        categorias = SqlSelect.conseguir_categorias()
        form.categoria.choices = [(categoria['idc'], categoria['nombre']) for categoria in categorias]
        if request.method=='POST':
            SqlUpdate = clsSqlUpdate.SqlUpdate()
            SqlUpdate.actualizarLugarYpertenece_a(form.nombre.data,
                                                    form.descripcion.data,
                                                    form.ubicacion.data,
                                                    form.tipo.data,
                                                    form.horario.data,
                                                    form.fecha.data,
                                                    form.categoria.data,
                                                    pertenece_a['ide'])
            return redirect('/principal')
        #except:
        #    print('Error')
        #    return redirect('/principal')
    return render_template('modificar_lugar.html', title='Modificar establecimiento/evento', form=form, lugar=lugar, pertenece_a=pertenece_a) 

#TRY-CATCH APAGADO
@app.route('/principal/por_visitar', methods=['GET','POST'])
def por_visitar():
    if (not session.get('logueado')):
        session.clear()
        return redirect('/')
    elif (not session['tipo']=='turista'):
        return redirect('/principal')
    else:
        #try:
        SqlSelect = clsSqlSelect.SqlSelect()
        lista = SqlSelect.conseguir_listado_PorVisitar(session['id_usuario'])
        if not bool(lista):
            lista = []
        #except:
        #    return redirect("/principal")        
    return render_template('por_visitar.html', title='Por visitar', lista=lista)

@app.route('/logout')
def logout():
    try:
        idu = request.args.to_dict()
        iduINT = int(idu['id_usuario'])
        ses = int(session['id_usuario'])
        if iduINT==ses:
            SqlDelete = clsSqlDelete.SqlDelete()
            SqlSelect = clsSqlSelect.SqlSelect()
            lugaresABorrar = SqlSelect.listarLugaresDeEmpresa(session['id_usuario'])
            #Si true, es una empresa y tiene lugares creados que hay que borrar, sino es turista
            if bool(lugaresABorrar):
                SqlDelete.borrarUsuario(ses,session['tipo'],lugaresABorrar)
            else:
                SqlDelete.borrarUsuario(ses,session['tipo'])
            
    except:
        print("Logout")           
    session.clear()        
    return redirect('/')

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500

