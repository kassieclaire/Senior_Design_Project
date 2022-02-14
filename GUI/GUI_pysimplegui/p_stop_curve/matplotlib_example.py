from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
import os
from PIL import Image, ImageTk
from urllib import request
matplotlib.use('TkAgg')
from p_stop_curve import cascading_failure_function
"""
    Simultaneous PySimpleGUI Window AND a Matplotlib Interactive Window
    A number of people have requested the ability to run a normal PySimpleGUI window that
    launches a MatplotLib window that is interactive with the usual Matplotlib controls.
    It turns out to be a rather simple thing to do.  The secret is to add parameter block=False to plt.show()
"""
#define values here
cap_loss = 1500
delivery_loss_percent = 8
worst_cluster = 4
num_lines = 186
#end defines
def draw_plot():
    p_stop_df = cascading_failure_function() #
    fig = plt.figure()
    plt.plot('x_values', 'cascade_stop', data=p_stop_df, color='skyblue', linewidth=1)
    plt.xlabel('Number of Failed Lines')
    plt.ylabel('Cascade-Stop Probability')
    plt.title('Cascade-Stop Probability vs Number of Line Failures')
    # show legend
    plt.legend()
    #set title
    plt.title = "Cascade-Stop Probability vs Number of Line Failures"
    #plt.plot([0.1, 0.2, 0.5, 0.7])
    #plt.show(block=False)
    return fig
# ------------------------------- Beginning of Matplotlib helper code -----------------------

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# layout = [[sg.Text('Plot test')],
#           [sg.Text('Load: '), sg.InputText(), sg.Canvas(key='-CANVAS-')],
#           [sg.Text('Line Failures: '), sg.InputText()],
#           [sg.Text('Load Shed Control: '), sg.InputText()],
#           [sg.Text('Cap Est. Err.: '), sg.InputText()],
#           [sg.Button('Run'), sg.Button('More Options')],
#           [sg.Button('Cancel')]]
#create column
#fill in column
description = " This is a Graphical User Interface \n for the SACE lab's cascading failure simulator, \n which simulates line failures in a grid \n after a number of initial failures"
load_tooltip = "This is the load-generation ratio for the grid. \n" + \
    "1.0 represents the sum of the loads being equivalant to the max generation capacity\n" + \
    "and 0.0 represents no load"
input_column = [[sg.Frame('Cascading Failure Simulation', [[sg.Text(description)]], border_width=10)],
                [sg.Frame('Load', [[sg.Slider(orientation ='horizontal', key='stSlider', range=(0.0,1.0), resolution=.01, tooltip=load_tooltip)]], border_width=10)],
                [sg.Frame('Initial Line Failures', [[sg.Slider(orientation ='horizontal', key='stSlider', range=(0.0,1.0), resolution=.01)]], border_width=10)],
                [sg.Frame('Flexibility', [[sg.Slider(orientation ='horizontal', key='stSlider', range=(0.0,1.0), resolution=.01)]], border_width=10)],
                [sg.Frame('Line Capacity Uncertainty', [[sg.Slider(orientation ='horizontal', key='stSlider', range=(0.0,1.0), resolution=.01)]], border_width=10)],
                [sg.Button('More Options'), sg.Button('Run')]
                ]
filename = os.getcwd() + "/graph_png.png" #TODO: get rid of this, make it display the pstop instead
# Resize PNG file to size (300, 300)
#size = (300, 300)
# im = Image.open(filename)
# im = im.resize(size, resample=Image.BICUBIC)
# image = ImageTk.PhotoImage(image=im)
#output_column = [[sg.Canvas(key='-CANVAS-')],
output_column = [[sg.Image(filename=filename)],
                [sg.Text('Loss of Delivery Capacity: '), sg.Text(str(delivery_loss_percent) + "%")],
                [sg.Text('Max Line Capacity: '), sg.Text(str(cap_loss) + " MW")],
                [sg.Text('Worst-off Cluster: '), sg.Text(str(worst_cluster))],
                [sg.Text('Probability of failure: '), sg.Text('Click on Line')],
                ]
layout = [[sg.Text('Cascading failure Simulator GUI')],
          [sg.Column(input_column, element_justification='c'), sg.Column(output_column, element_justification='c')]]
# create the form and show it without the plot
window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI', layout, finalize=True, element_justification='center', font='Helvetica 18')

# add the plot to the window
#fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, draw_plot())

event, values = window.read()

window.close()
