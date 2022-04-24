
import PySimpleGUI as sg
import gui_utilities

SLIDER_MIN_LINE_FAILURES = 'slider_min_line_failures'
SLIDER_MIN_LINE_FAILURES_TOOLTIP = 'filters the simulation results based on the minimum number of line failures'


def getGUIElement():
    layout = sg.Column([[gui_utilities.make_slider_with_frame('Minimum Line Failures', SLIDER_MIN_LINE_FAILURES, range=(0, 100), resolution=1,)],
                        [sg.Listbox(values=['l1', 'l2', 'l3'],
                                    key='test', enable_events=True, size=(15, 3))]])
    return layout
