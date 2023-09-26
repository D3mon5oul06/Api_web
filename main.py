from fastapi import FastAPI, UploadFile, File, HTTPException,Form
from pydantic import BaseModel
import mysql.connector
from mysql.connector import errorcode
from minio import Minio
from typing_extensions import Annotated
import uuid
import io




minio_client = Minio(
    endpoint='127.0.0.1:9000',
    access_key='5gUjDX35x0X2TMBT',
    secret_key='nUwdi0YYljlGOh3jzyb8FhYA2Ri7Vsvl',
    secure=False
)

try:
    cnx = mysql.connector.connect(user='root',password="",database='alpr')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor = cnx.cursor()
  
class Item(BaseModel):
    user: str
    passw: str 
    
app = FastAPI()

@app.post("/login")
def login(user,passw):
    statement = "Select tipo_usuario from users where nombre_usuario = %s and password = %s"
    cursor.execute(statement, (user, passw))
    print(cursor)
    cur=cursor.fetchone()
    if len(cur) == 0:
        return 0
    else:
        return cur[0]


class User(BaseModel):
    curp: str
    nombre_usuario: str
    password: str
    tipo: str
    tipo_usuario: str

@app.post("/users")
def create_user(user: User):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "INSERT INTO users (curp, nombre_usuario, password, tipo, tipo_usuario) " \
                    "VALUES (%s, %s, %s, %s, %s)"
        data = (user.curp, user.nombre_usuario, user.password, user.tipo, user.tipo_usuario)

        cursor.execute(statement, data)
        cnx.commit()

        return {"message": "User created successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.get("/users/{curp}")
def get_user(curp: str):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "SELECT * FROM users WHERE curp = %s"
        data = (curp,)

        cursor.execute(statement, data)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        user = {
            "curp": result[0],
            "nombre_usuario": result[1],
            "password": result[2],
            "tipo": result[3],
            "tipo_usuario": result[4]
        }

        return user
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.put("/users/{curp}")
def update_user(curp: str, user_update: User):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "UPDATE users SET nombre_usuario = %s, password = %s, tipo = %s, tipo_usuario = %s " \
                    "WHERE curp = %s"
        data = (user_update.nombre_usuario, user_update.password, user_update.tipo,
                user_update.tipo_usuario, curp)

        cursor.execute(statement, data)
        cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User updated successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.delete("/users/{curp}")
def delete_user(curp: str):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "DELETE FROM users WHERE curp = %s"
        data = (curp,)

        cursor.execute(statement, data)
        cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

#crud ine
class INE(BaseModel):
    nombre: str
    curp: str
    fecha_nacimiento: str
    vigencia: str
    sexo: str
    domicilio: str
    clave_elector: str
    seccion: str
    localidad: str
    año_registro: int

@app.post("/ine")
def create_ine(ine: INE):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "INSERT INTO ine (nombre, curp, fecha_nacimiento, vigencia, sexo, " \
                    "domicilio, clave_elector, seccion, localidad, año_registro) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (ine.nombre, ine.curp, ine.fecha_nacimiento, ine.vigencia, ine.sexo,
                ine.domicilio, ine.clave_elector, ine.seccion, ine.localidad, ine.año_registro)

        cursor.execute(statement, data)
        cnx.commit()

        return {"message": "INE data created successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.get("/ine/{curp}")
def get_ine(curp: str):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "SELECT * FROM ine WHERE curp = %s"
        data = (curp)

        cursor.execute(statement, data)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="INE data not found")

        ine_data = INE( nombre=result[0], curp=result[1], fecha_nacimiento=result[2],
                    vigencia=result[3], sexo=result[4], domicilio=result[5],
                    clave_elector=result[6], seccion=result[7], localidad=result[8], año_registro=result[9])

        return ine_data
    except mysql.connector.Error as err:
        return {"error": str(err)}

@app.put("/ine/{curp}")
def update_ine(curp: str, ine_update: INE):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "UPDATE ine SET nombre = %s, curp = %s, fecha_nacimiento = %s, vigencia = %s, " \
                    "sexo = %s, foto = %s, domicilio = %s, clave_elector = %s, seccion = %s, " \
                    "localidad = %s, año_registro = %s WHERE id_persona = %s"
        data = (ine_update.nombre, ine_update.curp, ine_update.fecha_nacimiento, ine_update.vigencia,
                ine_update.sexo, ine_update.foto, ine_update.domicilio, ine_update.clave_elector,
                ine_update.seccion, ine_update.localidad, ine_update.año_registro, curp)

        cursor.execute(statement, data)
        cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="INE data not found")

        return {"message": "INE data updated successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.delete("/ine/{curp}")
def delete_ine(curp: str):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "DELETE FROM ine WHERE curp = %s"
        data = (curp,)

        cursor.execute(statement, data)
        cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="INE data not found")

        return {"message": "INE data deleted successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

#crud vehiculo
class Vehiculo(BaseModel):
    placa: str
    modelo: str
    color: str
    año: str
    marca: str
    vin: str
    num_puertas: int
    tipo_motor: str
try:
    cnx = mysql.connector.connect(user='root', password="", database='alpr')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor = cnx.cursor()



@app.post("/vehiculos")
def create_vehiculo(vehiculo: Vehiculo):
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()

        statement = "INSERT INTO vehiculo (placa, modelo, color, año, marca, vin, num_puertas, tipo_motor) " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = (vehiculo.placa, vehiculo.modelo, vehiculo.color, vehiculo.año, vehiculo.marca,
                vehiculo.vin, vehiculo.num_puertas, vehiculo.tipo_motor)

        cursor.execute(statement, data)
        cnx.commit()

        return {"message": "Vehiculo created successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.get("/vehiculos/{placa}")
def get_vehiculo(placa: str):
    try:
        statement = "SELECT * FROM vehiculo WHERE placa = %s"
        data = (placa,)

        cursor.execute(statement, data)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Vehiculo not found")

        vehiculo = {
            "placa": result[0],
            "modelo": result[1],
            "color": result[2],
            "año": result[3],
            "marca": result[4],
            "vin": result[5],
            "num_puertas": result[6],
            "tipo_motor": result[7]
        }

        return vehiculo
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.put("/vehiculos/{placa}")
def update_vehiculo(placa: str, vehiculo_update: Vehiculo):
    try:
        statement = "UPDATE vehiculo SET modelo = %s, color = %s, año = %s, marca = %s, " \
                    "vin = %s, num_puertas = %s, tipo_motor = %s WHERE placa = %s"
        data = (vehiculo_update.modelo, vehiculo_update.color, vehiculo_update.año,
                vehiculo_update.marca, vehiculo_update.vin, vehiculo_update.num_puertas,
                vehiculo_update.tipo_motor, placa)

        cursor.execute(statement, data)
        cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vehiculo not found")

        return {"message": "Vehiculo updated successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

@app.delete("/vehiculos/{placa}")
def delete_vehiculo(placa: str):
    try:
        statement = "DELETE FROM vehiculo WHERE placa = %s"
        data = (placa,)

        cursor.execute(statement, data)
        cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vehiculo not found")

        return {"message": "Vehiculo deleted successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
            
#crud persona
class Personas(BaseModel):
    curp: str
    nombre: str
    edad: int
    email: str
    telefono: int
    vin: str

@app.on_event("startup")
async def startup():
    try:
        cnx = mysql.connector.connect(user='root', password='', database='alpr')
        cursor = cnx.cursor()
        app.state.cnx = cnx
        app.state.cursor = cursor
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

@app.on_event("shutdown")
async def shutdown():
    cursor = app.state.cursor
    cnx = app.state.cnx
    cursor.close()
    cnx.close()

@app.post("/personas")
def create_persona(persona: Personas):
    try:
        statement = "INSERT INTO persona (curp, nombre, edad, email, telefono, vin) " \
                    "VALUES (%s, %s, %s, %s, %s, %s)"
        data = (persona.curp, persona.nombre, persona.edad, persona.email,
                persona.telefono, persona.vin)

        cursor = app.state.cursor
        cursor.execute(statement, data)
        app.state.cnx.commit()

        return {"message": "Persona created successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}

@app.get("/personas/{curp}")
def get_persona(curp: str):
    try:
        statement = "SELECT * FROM persona WHERE curp = %s"
        data = (curp,)

        cursor = app.state.cursor
        cursor.execute(statement, data)
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Persona not found")

        persona = {
            "curp": result[0],
            "nombre": result[1],
            "edad": result[2],
            "email": result[3],
            "telefono": result[4],
            "vin": result[5]
        }

        return persona
    except mysql.connector.Error as err:
        return {"error": str(err)}

@app.put("/personas/{curp}")
def update_persona(curp: str, persona_update: Personas):
    try:
        statement = "UPDATE persona SET nombre = %s, edad = %s, email = %s, " \
                    "telefono = %s, vin = %s WHERE curp = %s"
        data = (persona_update.nombre, persona_update.edad, persona_update.email,
                persona_update.telefono, persona_update.vin, curp)

        cursor = app.state.cursor
        cursor.execute(statement, data)
        app.state.cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Persona not found")

        return {"message": "Persona updated successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}

@app.delete("/personas/{curp}")
def delete_persona(curp: str):
    try:
        statement = "DELETE FROM persona WHERE curp = %s"
        data = (curp,)

        cursor = app.state.cursor
        cursor.execute(statement, data)
        app.state.cnx.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Persona not found")

        return {"message": "Persona deleted successfully"}
    except mysql.connector.Error as err:
        return {"error": str(err)}


mysql_config = {
    'user': 'root',
    'password': '',
    'database': 'alpr',
    'host': 'localhost',
    'port': '3306',
}


@app.post("/ine/", status_code=201)
async def guardar_ine(file: Annotated[bytes, File()],):
    image_uuid = str(uuid.uuid4())
    lenght=len(file)
    stream=io.BytesIO(file)
    print(lenght)
    minio_client.put_object(
        bucket_name='ine',
        object_name=f"{image_uuid}.jpg",
        data=stream,
        length=lenght,
        content_type='image/jpg'
    )



    #statement = "INSERT INTO guardar_ine (uuid, curp_rf) VALUES (%s, %s)"
    #data = (image_uuid, 'curp_rf_value')



@app.get("/ine/{image_uuid}")
async def obtener_ine(image_uuid: str):
    try:
        
        exists = minio_client.bucket_exists(bucket_name='ine')
        if not exists:
            return {"error": "El bucket 'ine' no existe"}

        
        object_exists = minio_client.object_exists(bucket_name='ine', object_name=f"{image_uuid}.jpg")
        if not object_exists:
            return {"error": "La imagen no existe"}

        
        object_info = minio_client.stat_object(bucket_name='ine', object_name=f"{image_uuid}.jpg")
        size = object_info.size
        content_type = object_info.content_type

        return {
            "image_uuid": image_uuid,
            "size": size,
            "content_type": content_type
        }
    except Exception as e:
        return {"error": str(e)}

@app.put("/ine/{image_uuid}", status_code=200)
async def actualizar_ine(image_uuid: str, file: Annotated[bytes, File()]):
    try:

        exists = minio_client.bucket_exists(bucket_name='ine')
        if not exists:
            return {"error": "El bucket 'ine' no existe"}


        object_exists = minio_client.object_exists(bucket_name='ine', object_name=f"{image_uuid}.jpg")
        if not object_exists:
            return {"error": "La imagen no existe"}

        minio_client.remove_object(bucket_name='ine', object_name=f"{image_uuid}.jpg")
        

        lenght = len(file)
        stream = io.BytesIO(file)
        minio_client.put_object(
            bucket_name='ine',
            object_name=f"{image_uuid}.jpg",
            data=stream,
            length=lenght,
            content_type='image/jpg'
        )
        
        return {"message": "Imagen actualizada correctamente"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/ine/{image_uuid}", status_code=204)
async def eliminar_ine(image_uuid: str):
    try:
        exists = minio_client.bucket_exists(bucket_name='ine')
        if not exists:
            return {"error": "El bucket 'ine' no existe"}

        object_exists = minio_client.object_exists(bucket_name='ine', object_name=f"{image_uuid}.jpg")
        if not object_exists:
            return {"error": "La imagen no existe"}


        minio_client.remove_object(bucket_name='ine', object_name=f"{image_uuid}.jpg")

        return None
    except Exception as e:
        return {"error": str(e)}


vin_mysql_config = {
    'user': 'root',
    'password': '',
    'database': 'guardar_vin',
    'host': 'localhost',
    'port': '3306',
}

@app.post("/vin/", status_code=201)
async def guardar_vin(file: Annotated[bytes, File()],):
    image_uuid = str(uuid.uuid4())
    lenght=len(file)
    stream=io.BytesIO(file)
    print(lenght)
    minio_client.put_object(
        bucket_name='vin',
        object_name=f"{image_uuid}.jpg",
        data=stream,
        length=lenght,
        content_type='image/jpg'
    )


    #statement = "INSERT INTO guardar_vin (uuid, vin_nf) VALUES (%s, %s)"
    #data = (image_uuid, count + 1)



@app.get("/vin/{image_uuid}", status_code=200)
async def obtener_vin(image_uuid: str):
    try:
        response = minio_client.get_object(
            bucket_name='vin',
            object_name=f"{image_uuid}.jpg"
        )
        image_data = response.data

        return {
            "image_uuid": image_uuid,
            "image_data": image_data
        }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/vin/{image_uuid}", status_code=200)
async def eliminar_vin(image_uuid: str):
    try:
        exists = minio_client.bucket_exists(bucket_name='vin')
        if not exists:
            return {"error": "El bucket 'vin' no existe"}

        
        object_exists = minio_client.object_exists(bucket_name='vin', object_name=f"{image_uuid}.jpg")
        if not object_exists:
            return {"error": "La imagen no existe"}

        
        minio_client.remove_object(bucket_name='vin', object_name=f"{image_uuid}.jpg")
        
        return {"message": "Imagen eliminada correctamente"}
    except Exception as e:
        return {"error": str(e)}

@app.put("/vin/{image_uuid}", status_code=200)
async def actualizar_vin(image_uuid: str, file: Annotated[bytes, File()]):
    try:
        exists = minio_client.bucket_exists(bucket_name='vin')
        if not exists:
            return {"error": "El bucket 'vin' no existe"}

        object_exists = minio_client.object_exists(bucket_name='vin', object_name=f"{image_uuid}.jpg")
        if not object_exists:
            return {"error": "La imagen no existe"}

        lenght = len(file)
        stream = io.BytesIO(file)
        minio_client.put_object(
            bucket_name='vin',
            object_name=f"{image_uuid}.jpg",
            data=stream,
            length=lenght,
            content_type='image/jpg'
        )
        
        return {"message": "Imagen actualizada correctamente"}
    except Exception as e:
        return {"error": str(e)}

