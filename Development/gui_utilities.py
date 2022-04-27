
import PySimpleGUI as sg

FONT = 'Helvetica 14'
TEXT_COLOR = '#000000'
BACKGROUND_COLOR = '#FFFFFF'


def make_slider_with_frame(label: str, key: str, range=None, resolution=None, tooltip=None, size=(None, None), default_value=None, enable_events=False) -> sg.Frame:
    return sg.Frame(label, [[sg.Slider(key=key, tooltip=tooltip, size=size, range=range, resolution=resolution, orientation='horizontal', default_value=default_value, enable_events=enable_events)]], border_width=10, relief='flat')
