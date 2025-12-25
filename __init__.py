from .src import gui

try:
    from importlib import reload
except:
    pass

reload(gui)

def editable():
    gui.main(True)

    
def main():
    gui.main(False)