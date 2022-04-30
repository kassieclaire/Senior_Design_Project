
import PySimpleGUI as sg

FONT = 'Helvetica 14'
TEXT_COLOR = '#000000'
BACKGROUND_COLOR = '#FFFFFF'


def make_slider_with_frame(label: str, key: str, range=None, resolution=None, tooltip=None, size=(None, None), default_value=None, enable_events=False) -> sg.Frame:
    return sg.Frame(label, [[sg.Slider(key=key, tooltip=tooltip, size=size, range=range, resolution=resolution, orientation='horizontal', default_value=default_value, enable_events=enable_events)]], border_width=0, relief='flat')


def update_text(window, key, text_format, format_values):
    """
    Updates the text of the text box with the given key based on the format string and values.
    :param window: The window to update the text in.
    :param key: The key of the text box to update.
    :param text_format: The format string to use.
    :param format_values: Tuple of the values to use in the format string.
    """
    window[key].update(text_format %
                       format_values)
