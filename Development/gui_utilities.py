
import PySimpleGUI as sg

FONT = 'Helvetica 14'


def make_slider_with_frame(label: str, key: str, range=None, resolution=None, tooltip=None, size=(None, None)) -> sg.Frame:
    return sg.Frame(label, [[sg.Slider(key=key, tooltip=tooltip, size=size, range=range, resolution=resolution, orientation='horizontal')]], border_width=10, relief='flat')
