from simple_gui import simple_gui
from complex_gui import complex_gui

action = simple_gui()
while action != 'quit':
    if action == 'more':
        action = complex_gui()
    else:
        #action is less -- move to less-complex GUI
        action = simple_gui()
    