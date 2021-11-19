from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
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
    p_stop_df = cascading_failure_function()
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
input_column = [[sg.Text('Load')],
                [sg.Slider(orientation ='horizontal', key='stSlider', range=(0.0,1.0), resolution=.01)],
                [sg.Text('Initial Line Failures: ')],
                [sg.Slider(orientation ='horizontal', key='stSlider', range=(1,num_lines), resolution=1)],
                [sg.Text('Load Shed Control')],
                [sg.Slider(orientation ='horizontal', key='stSlider', range=(0.0,1.0), resolution=.01)],
                [sg.Text('Cap Est. Err.')],
                [sg.Slider(orientation ='horizontal', key='stSlider', range=(0.0,1.0), resolution=.01)],
                [sg.Button('More Options'), sg.Button('Run')],
                ]
output_column = [[sg.Canvas(key='-CANVAS-')],
                [sg.Text('Loss of Delivery Capacity: '), sg.Text(str(delivery_loss_percent) + "%")],
                [sg.Text('Max Line Capacity: '), sg.Text(str(cap_loss) + " MW")],
                [sg.Text('Worst-off Cluster: '), sg.Text(str(worst_cluster))],
                [sg.Text('Probability of failure: '), sg.Text('Click on Line')],
                ]
layout = [[sg.Text('Cascading failure sim')],
          [sg.Column(input_column, element_justification='c'), sg.Column(output_column, element_justification='c')]]
# create the form and show it without the plot
window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI', layout, finalize=True, element_justification='center', font='Helvetica 18')

# add the plot to the window
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, draw_plot())

event, values = window.read()

window.close()
