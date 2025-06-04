import os #Para interactuar con el sistema operativo 
import ast #Para convertir cadenas de texto en algo que Python pueda leer 
from datetime import datetime #Para obtener fecha y hora 
from API import chat_con_php #Conecta a main.py con el asistente virtual 
import shutil #Para obtener el tamaño de la termian
import textwrap #Para ajustar tectos largos en varias lineas
print("lo que sea")


CARPETA_ARCHIVOS = "archivos"

if not os.path.exists(CARPETA_ARCHIVOS): #si no existe un archivo con el nombre "archivos" entonces lo crea y si existe entonce no hace nada
    os.makedirs(CARPETA_ARCHIVOS)

usuarios = {}
usuario_actual = None

def mostrarMenuPrincipal():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Iniciar sesión")
    print("2. Crear cuenta")
    print("3. Salir")

def obtenerRutaArchivo(nombre): #Obtiene el archivo txt basandose en el nombre de usuario 
    return os.path.join(CARPETA_ARCHIVOS, f"{nombre}_conversaciones.txt")

def cargar_conversaciones(nombre):
    archivo = obtenerRutaArchivo(nombre) 
    if os.path.exists(archivo): #Verifica si el archivo existe 
        with open(archivo, "r", encoding="utf-8") as f: # Abre el archivo en modo lectura 'r' y el UTF-8 hace que soporte caracteres especiales como tilds o eñes 
        #with hacen que el archivo se cierre al termianr  
            contenido = f.read() #Lee el contenido del archivo y lo guarda como una cadena en la variable contenido
            if contenido: #Si contenido no esta vacio avanza sino retorna []
                return ast.literal_eval(contenido) #convierte a contenido en una lista 
    return []

def guardar_conversaciones(nombre):
    archivo = obtenerRutaArchivo(nombre)
    with open(archivo, "w", encoding="utf-8") as f: #abre el archivo en modo escritura 'w' 
        f.write(str(usuarios[nombre])) #Convierte el historial de conversaciones a texto usando STR y luego lo guarda en el archivo
        
def registrar_conversacion(nombre):
    conversacion = []
    print("Escriba los mensajes. Escriba 'salir' para terminar la conversación.")
    ancho_consola = shutil.get_terminal_size().columns
    ancho_mensaje = int(ancho_consola * 0.8) #El 80% del ancho de la terminal

    while True: #Bucle infinito que solo se detiene al escribir salir 
        mensaje_usuario = input("Tú: ")
        if mensaje_usuario.lower() == "salir": # El .lower() convierte todo el mensaje en minuscula 
            break
        conversacion.append({"role": "usuario", "content": mensaje_usuario}) #cada vez que se escribe algo se guarda en conversacion como un diccionario 

        lineas_usuario = textwrap.wrap(mensaje_usuario, width=ancho_mensaje)
        for i, linea in enumerate(lineas_usuario):
            if i == 0:
                print("Tú:".rjust(ancho_consola))
            print(linea.rjust(ancho_consola))

        mensaje_asistente = chat_con_php(mensaje_usuario) #Manda lo que escribiste a la ia y retorna lo que esta responde  
        conversacion.append({"role": "asistente", "content": mensaje_asistente})#Guarda la respuesta de la ia en conversacion 

        lineas_asistente = textwrap.wrap(mensaje_asistente, width=ancho_mensaje)
        print("Asistente:")
        for linea in lineas_asistente:
            print(linea)

    registro = { #se crea un registro completo de la conversacion con fecha y lista de mensajes 
        "fecha": fecha(), #llama a fecha que retorna el dia-mes-año
        "mensajes": conversacion
    }

    usuarios[nombre].append(registro) #Agrega el registro al usuario actual 
    guardar_conversaciones(nombre)
    print("Conversación guardada con éxito.")

def ver_historial(nombre):
    historial = usuarios[nombre] #Accede al historial del usuario 
    ancho_consola = shutil.get_terminal_size().columns
    ancho_mensaje = int(ancho_consola * 0.6) #Tira que tan largo puede ser un mensaje antes de dividirse en otras lineas 
    lado_user = int(ancho_consola * 0.8) #Para alinear el mensaje del usuario al otro lado
    if not historial: #Verifica si esta vacio 
        print("No hay conversaciones registradas.")
        return

    historial_ordenado = sorted(historial, key=lambda x: x["fecha"]) #Ordena las conversaciones por fecha (Por si acaso)

    for i, registro in enumerate(historial_ordenado): #Bucle de cada conversacion
        print(f"\n--- Conversación {i + 1} ({registro['fecha']}) ---") #Imprime el numero de la conversacion y la fecha del registro
        for mensaje in registro["mensajes"]: #Bucle de cada mensaje
            lineas = textwrap.wrap(mensaje['content'], width = ancho_mensaje) #Divide el mensaje en varias lineas
            if mensaje["role"] == "asistente":                           #Hace print y las acomoda de lado dependiedo de quien es el mensaje 
                for i, linea in enumerate(lineas):
                    if i == 0:
                        print (f"Asistente:  {linea}")
                    else:
                        print(" " * (len("Asistente")+2) + linea)
            else:
                print("Tú:".rjust(lado_user))
                for i, linea in enumerate(lineas):
                    texto = f"{linea}" if i < len(lineas) - 1 else f"{linea}"
                    print(texto.rjust(lado_user))

def buscar_palabra(nombre):
    palabra = input("Ingrese la palabra clave a buscar: ").lower()
    historial = usuarios[nombre] #Carga las conversaciones del usuario 
    encontrados = []

    for i, registro in enumerate(historial): #Recorre cada conversacion
        for mensaje in registro["mensajes"]: #Luego cada mensaje
            if palabra in mensaje["content"].lower(): #Si la palabra esta en el mensaje lo guarda en encontrados 
                encontrados.append((i + 1, registro["fecha"], mensaje))

    if encontrados:
        print(f"\nSe encontró la palabra '{palabra}' en:")
        for numero, fecha, mensaje in encontrados:
            print(f"- Conversación {numero} ({fecha}), {mensaje['role']}: {mensaje['content']}") #Hace print a lo que encontro
    else:
        print("No se encontró esa palabra en ninguna conversación.")

def generar_resumen(nombre):
    historial = usuarios[nombre] #Carga las convesaciones del usuario
    if not historial:
        print("No hay conversaciones para resumir.")
        return

    ver_historial(nombre)
    try:
        num = int(input("Seleccione el número de la conversación a resumir: ")) - 1
        if 0 <= num < len(historial): #Revisa que el numero ingresado este dentro del rango valido 
            mensajes = historial[num]["mensajes"]
            print("\nResumen (máx 50 palabras):")

            resumen = chat_con_php("Genera un resumen de maximo50 mensajes de la siguiente conversacion" + str(mensajes))
            print(resumen) #Manda la convesacion seleccionada al Bot con una instruccion clara 
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada no válida.")

def menu_usuario(nombre): #Menu de usuario, bucle infinito que solo termina si el usuario escoge cerrar sesion 
    while True: 
        print(f"\n--- MENÚ DE USUARIO ({nombre}) ---")
        print("1. Registrar nueva conversación")
        print("2. Ver historial de conversaciones")
        print("3. Buscar palabra clave")
        print("4. Generar resumen de una conversación")
        print("5. Cerrar sesión")

        opcion = input("Seleccione una opción: ")

        match opcion:
            case "1":
                registrar_conversacion(nombre)
            case "2":
                ver_historial(nombre)
            case "3":
                buscar_palabra(nombre)
            case "4":
                generar_resumen(nombre)
            case "5":
                print("Cerrando sesión...")
                break
            case _:
                print("Opción no válida. Intente de nuevo.")

def menuInicioSesion():
    global usuario_actual
    nombre = input("Ingrese su nombre de Usuario: ")
    archivo = obtenerRutaArchivo(nombre)
    if os.path.exists(archivo): #Busca el nombre en la carpeta archivos, si existe entrara al menu de usuario con su nombre 
        usuario_actual = nombre #Sino le pedira que cree una cuenta 
        usuarios[nombre] = cargar_conversaciones(nombre)
        print(f"Bienvenido de nuevo, {nombre}!")
        menu_usuario(nombre)
    else:
        print("Usuario no encontrado. Por favor, cree una cuenta primero.")

def menuCrearCuenta():
    nombre = input("Ingrese un nombre de Usuario nuevo: ")
    if nombre in usuarios or os.path.exists(obtenerRutaArchivo(nombre)): #Busca el nombre en Archivos si existe le pedira que intente con otro nombre
        print("Este nombre de usuario ya existe. Intente con otro.")
    else: #Si no existe entonces manda el nombre a guardar conversaciones 
        usuarios[nombre] = []
        guardar_conversaciones(nombre)
        print(f"Felicidades {nombre}, su usuario ha sido creado exitosamente.")

def main():
    while True:
        mostrarMenuPrincipal()
        opcion = input("Seleccione una opción: ")

        match opcion:
            case "1":
                menuInicioSesion()
            case "2":
                menuCrearCuenta()
            case "3":
                print("Saliendo del programa...")
                break
            case _:
                print("Opción no válida. Intente de nuevo.")

def fecha(): #Toma la fecha actual para cuando se ocupe guardar en una converssacion 
    fecha_actual = datetime.now()
    fecha_actual = fecha_actual.strftime('%d-%m-%Y')
    return fecha_actual

if __name__ == "__main__":
    main()
