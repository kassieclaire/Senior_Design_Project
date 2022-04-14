
from matplotlib import container
import remi.gui as gui
import remi


class MyApp(remi.App):
    def __init__(self, *args) -> None:
        super(MyApp, self).__init__(*args)

    def main(self):
        container = gui.VBox()
        # container = gui.VBox(width=120, height=100)
        self.lbl = gui.Label('Hello World!')
        self.bt = gui.Button('Click me!')

        # setting the listener for the onclick event of the button
        self.bt.onclick.do(self.on_button_pressed)

        # append a widget to another, first arg is a string key
        container.append(self.lbl)
        container.append(self.bt)

        # return the root widget
        return container

    # listener function
    def on_button_pressed(self, widget):
        self.lbl.set_text('Button Pressed!')
        self.bt.set_text('Hi!')


# start the web server
if __name__ == "__main__":
    remi.start(MyApp, address='127.0.0.1',
               start_browser=True, multiple_instance=True)
