import os
import shutil
import time
import curses
import zipfile
import requests
from tqdm import tqdm

USER_DIR = os.environ['USERPROFILE'] 
BASE_DIR = os.path.join(USER_DIR, "AppData", "LocalLow", "semiwork", "REPO", "saves")
DOWNLOAD_DIR = os.path.join(USER_DIR, "Downloads")

idioma = "español" 

texts = {
    "español": {
        "ascii": """
                           _____ 
    ____                  | ____|
   / __ \__   ____ _   ___| |__  
  / / _` \ \ / / _` | |_  /___ \ 
 | | (_| |\ V / (_| |_ / / ___) |
  \ \__,_| \_/ \__, (_)___|____/ 
   \____/       __/ |            
               |___/             
""",
        "menu_options": [
            "Clonar partida desde carpeta", 
            "Descargar partida nivel 5", 
            "Cambiar idioma", 
            "Salir"
        ],
        "change_language": "Selecciona un idioma:",
        "espanol": "Español",
        "ingles": "Inglés",
        "select_folder": "Selecciona una carpeta para clonar:",
        "enter_quantity": "¿Cuántas copias quieres hacer? (1-99): ",
        "cloning": "Clonando {0} veces la partida {1}...",
        "process_completed": "[✓] Proceso completado. Todos los archivos se han eliminado correctamente.",
        "zip_removed": "[✓] El archivo ZIP ha sido eliminado después de la extracción.",
    },
    "ingles": {
        "ascii": """
                           _____ 
    ____                  | ____|
   / __ \__   ____ _   ___| |__  
  / / _` \ \ / / _` | |_  /___ \ 
 | | (_| |\ V / (_| |_ / / ___) |
  \ \__,_| \_/ \__, (_)___|____/ 
   \____/       __/ |            
               |___/             
""",
        "menu_options": [
            "Clone save from folder", 
            "Download save level 5", 
            "Change language", 
            "Exit"
        ],
        "change_language": "Select a language:",
        "espanol": "Spanish",
        "ingles": "English",
        "select_folder": "Select a folder to clone:",
        "enter_quantity": "How many copies do you want to make? (1-99): ",
        "cloning": "Cloning {0} times the save {1}...",
        "process_completed": "[✓] Process completed. All files have been deleted successfully.",
        "zip_removed": "[✓] The ZIP file has been removed after extraction.",
    }
}

def mostrar_ascii(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.clear()
    for i, line in enumerate(texts[idioma]["ascii"].split("\n")):
        stdscr.addstr(i + 1, 5, line, curses.color_pair(1))
        stdscr.refresh()
        time.sleep(0.1)

def obtener_siguiente_numero():
    """Encuentra el número más alto usado en carpetas y devuelve el siguiente disponible"""
    existentes = {int(f) for f in os.listdir(BASE_DIR) if f.isdigit()}
    nuevo_num = 1
    while nuevo_num in existentes:
        nuevo_num += 1
    return nuevo_num

def listar_carpetas():
    """Lista todas las carpetas en el directorio BASE_DIR que contienen las partidas"""
    return [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

def clonar_y_renombrar(stdscr, origen, cantidad):
    """Clona la carpeta 'cantidad' de veces y renombra archivos internos acorde al nombre de la carpeta"""
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    origen_path = os.path.join(BASE_DIR, origen)
    siguiente_num = obtener_siguiente_numero()
    
    for _ in tqdm(range(cantidad), desc="Clonando partidas", unit=" clon", ascii=True):
        nueva_carpeta = os.path.join(BASE_DIR, str(siguiente_num))
        shutil.copytree(origen_path, nueva_carpeta)
        stdscr.addstr(10, 5, f"[+] Clonada partida: {siguiente_num}", curses.color_pair(2))
        stdscr.refresh()
        time.sleep(0.3)

        for archivo in os.listdir(nueva_carpeta):
            archivo_path = os.path.join(nueva_carpeta, archivo)

            if "BACKUP" in archivo.upper():
                os.remove(archivo_path)
                stdscr.addstr(12, 5, f"[-] Eliminado backup: {archivo}", curses.color_pair(2))
                stdscr.refresh()
                time.sleep(0.3)
                continue

            extension = os.path.splitext(archivo)[1]
            nuevo_nombre = f"{siguiente_num}{extension}"
            nuevo_path = os.path.join(nueva_carpeta, nuevo_nombre)
            os.rename(archivo_path, nuevo_path)
            stdscr.addstr(14, 5, f"[*] Renombrado: {archivo} -> {nuevo_nombre}", curses.color_pair(2))
            stdscr.refresh()
            time.sleep(0.3)
        
        siguiente_num += 1

def descargar_partida(url):
    """Descarga una partida desde una URL y la descomprime"""
    nombre_archivo = os.path.join(DOWNLOAD_DIR, "partida_lvl5.zip")
    
    response = requests.get(url)
    with open(nombre_archivo, 'wb') as f:
        f.write(response.content)
    
    with zipfile.ZipFile(nombre_archivo, 'r') as zip_ref:
        zip_ref.extractall(BASE_DIR)
    
    os.remove(nombre_archivo)

    return os.path.basename(url).split(".")[0]  

def cambiar_idioma(stdscr):
    """Permite cambiar el idioma entre español e inglés"""
    global idioma
    opciones_idioma = [texts[idioma]["espanol"], texts[idioma]["ingles"]]
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(2, 5, texts[idioma]["change_language"], curses.A_BOLD)
        
        for i, opcion in enumerate(opciones_idioma):
            if i == idx:
                stdscr.addstr(4 + i, 7, f"> {opcion}", curses.A_REVERSE)
            else:
                stdscr.addstr(4 + i, 7, f"  {opcion}")
        
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(opciones_idioma) - 1:
            idx += 1
        elif key == 10: 
            idioma = "español" if idx == 0 else "ingles"
            break

    menu(stdscr)  


def menu(stdscr):
    curses.curs_set(0)
    mostrar_ascii(stdscr)
    time.sleep(1)
    stdscr.clear()
    stdscr.refresh()
    
    opciones = texts[idioma]["menu_options"]
    idx = 0
    
    while True:
        stdscr.clear()
        stdscr.addstr(2, 5, "Selecciona una opción:", curses.A_BOLD)
        
        for i, opcion in enumerate(opciones):
            if i == idx:
                stdscr.addstr(4 + i, 7, f"> {opcion}", curses.A_REVERSE)
            else:
                stdscr.addstr(4 + i, 7, f"  {opcion}")
        
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(opciones) - 1:
            idx += 1
        elif key == 10:  
            if idx == 0:
                stdscr.clear()
                stdscr.addstr(2, 5, texts[idioma]["select_folder"], curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                
                carpetas = listar_carpetas()
                idx_carpeta = 0  
                while True:
                    for i, carpeta in enumerate(carpetas):
                        if i == idx_carpeta:
                            stdscr.addstr(4 + i, 5, f"> {carpeta}", curses.A_REVERSE)
                        else:
                            stdscr.addstr(4 + i, 5, f"  {carpeta}")
                    stdscr.refresh()
                    
                    key = stdscr.getch()
                    if key == curses.KEY_UP and idx_carpeta > 0:
                        idx_carpeta -= 1
                    elif key == curses.KEY_DOWN and idx_carpeta < len(carpetas) - 1:
                        idx_carpeta += 1
                    elif key == 10:  
                        origen = carpetas[idx_carpeta]
                        break
                
                stdscr.addstr(6 + len(carpetas), 5, texts[idioma]["enter_quantity"], curses.A_BOLD)
                stdscr.refresh()
                curses.echo()
                cantidad = int(stdscr.getstr(7 + len(carpetas), 5, 2).decode("utf-8"))
                cantidad = max(1, min(cantidad, 99))
                curses.noecho()
                
                stdscr.clear()
                stdscr.addstr(5, 10, texts[idioma]["cloning"].format(cantidad, origen), curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                clonar_y_renombrar(stdscr, origen, cantidad)
                
                stdscr.clear()
                stdscr.addstr(5, 10, texts[idioma]["process_completed"], curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                stdscr.getch()
            elif idx == 1:
                url = "https://github.com/lamenteturbia/R.E.P.O-SAVE-DATA-CLONER/raw/main/REPO_SAVE_2025_03_16_18_49_50.zip"  
                nombre_carpeta = descargar_partida(url)
                
                stdscr.clear()
                stdscr.addstr(2, 5, texts[idioma]["enter_quantity"], curses.A_BOLD)
                stdscr.refresh()
                curses.echo()
                cantidad = int(stdscr.getstr(3, 5, 2).decode("utf-8"))
                cantidad = max(1, min(cantidad, 99))
                curses.noecho()
                
                stdscr.clear()
                stdscr.addstr(5, 10, texts[idioma]["cloning"].format(cantidad, nombre_carpeta), curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                clonar_y_renombrar(stdscr, nombre_carpeta, cantidad)
                
                stdscr.clear()
                stdscr.addstr(5, 10, texts[idioma]["process_completed"], curses.A_BOLD)
                stdscr.refresh()
                time.sleep(1)
                stdscr.addstr(6, 10, texts[idioma]["zip_removed"], curses.A_BOLD)
                stdscr.refresh()
                stdscr.getch()
            elif idx == 2:
                cambiar_idioma(stdscr)
            elif idx == 3:
                break

if __name__ == "__main__":
    curses.wrapper(menu)
