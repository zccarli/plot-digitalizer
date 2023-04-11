'''
sys: library associated with system process
csv: processing csv file
'''

import sys
import csv
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from matplotlib.widgets import Button

from tkinter import simpledialog
from tkinter import filedialog

# Abbreviations for long functions name
ms = simpledialog.messagebox.showwarning
qs = simpledialog.askstring
sf = filedialog.asksaveasfile

class Click():

    def __init__(self, ax, ROOT):
        '''
        Initial settings for the variables:
        ax.figure.canvas.mpl_connect links the matplotlib event to a specific funtion
        Setup personal settings for cursor and annotation, e.g., color
        '''
        self.ROOT = ROOT
        self.ax = ax
        self.button = 1
        self.press = False
        self.move = False
        self.press_event = self.ax.figure.canvas.mpl_connect('button_press_event', self.onpress)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.onrelease)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.onmove)
        self.ax.figure.canvas.mpl_connect('close_event', self.handle_close)

        self.cursor = Cursor(ax, horizOn=True, vertOn=True, useblit=True,
                             color='r', linewidth=1)
        # Creating an annotating box
        self.annot = ax.annotate("", xy=(0, 0), xytext=(-40, 40), textcoords="offset points",
                                 bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                                 arrowprops=dict(arrowstyle='-|>'))
        self.annot.set_visible(False)

        self.cal_pressed = False
        self.activated = False
        self.showscatter_pressed = False

        self._add_buttons()
        self._b_connect(True)

        self.scale_x = 1
        self.scale_y = 1

        self.calpoint = []
        self.labelpoint = []
        self.output = []
        self.x_before = []
        self.y_before = []
        self.x_after = []
        self.y_after = []
        self.counter = 0
        self.x_cache = 9999
        self.y_cache = 9999

        self.xdir = 1  # direction of calibrated x axis, default 1 indicates from left (negative) to right (positive)
        self.ydir = 1  # direction of calibrated y axis, default 1 indicates from bottom (negative) to top (positive)

        # print('press calibration to start!!!')
        ms(title='Info', message='Press calibration to start ! ! !')

    def handle_close(self, event):
        '''
        Close GUI and end the system process
        '''
        self.ROOT.destroy()  # close all pop up windows
        sys.exit(0)  # exit from python
        # print('close a11')

    def onclick(self, event):
        '''
        Increase counter by 1 for each click, the first two clicks generates calibration points
        The third click (counter = 2) transform the matplotlib coordinate system to the expected coordinate system in the plot
        The rest of clicks allow the user to draw labels
        '''
        if event.inaxes == self.ax:
            if event.button == self.button:
                if self.cal_pressed and self.counter < 2 and self.activated:
                    self.cal(event, self.ax)
                elif self.cal_pressed and self.counter == 2 and self.activated:
                    # print('scaling...')
                    self.scaling(self.x_before, self.y_before, self.x_after, self.y_after)
                    ms(title='Info', message='Now you can start labeling...')
                elif self.cal_pressed and self.counter > 2 and self.activated:
                    # print('labeling...')
                    self.label(event, self.ax)

        plt.pause(0.01) # avoid clicking too fast that causes crash

    def onpress(self, event):
        '''
        If the user presses mouse button, set press = True
        '''
        self.press = True

    def onmove(self, event):
        '''
        If the user holds and drags mouse button, set move = True
        If the user places the cursor upon a label point, show the coordinate of the points
        '''
        if self.press:
            self.move = True

        if event.inaxes == self.ax:  # hovering
            for p in self.labelpoint:
                boo = p.contains(event)[0]
                if boo:
                    self.hover(p)

    def onrelease(self, event):
        '''
        Only enable onclick() if the user click and release the mouse button at the same positiion
        '''
        if self.press and not self.move:
            self.onclick(event)
        self.press = False; self.move = False

    def cal(self, event, ax):
        '''
        Start drawing calibration points if self.calpressed = True and self.activated = True
        Store the coordinate of calibration points in self.x_before and self.y_before list for matplotlib coordinate system
        Store the coordinate of calibration points in self.x_after and self.y_after list for new coordinate system
        Store the calibration points as events in self.calpoint list, which can be removed by event.remove()
        '''
        self.press = False
        self.ax.figure.canvas.mpl_disconnect(self.press_event)  # disable the press event when input
        self._b_connect(False)  # disable the buttons when input

        x, y = event.xdata, event.ydata
        sc = ax.scatter(x, y, marker='x')
        ax.figure.canvas.draw()
        print(x, y)
        self.annot.xy = (x, y)
        text = 'Calpoint {:d}'.format(self.counter + 1)
        self.annot.set_text(text)
        self.annot.set_visible(True)

        while True:
            try:
                # x_in = input('enter the calibrated x value for calibration point %d: ' % self.counter)
                x_in = qs(title=None,
                          prompt='Enter the calibrated X value for calibration point %d: ' % (self.counter + 1))
                if float(x_in) == self.x_cache:
                    # print('must enter a different x value!!!')
                    ms(title='Warning', message='Must enter a different X value ! ! !')
                else:
                    self.x_cache = float(x_in)
                    self.x_after.append(float(x_in))
                    # print(self.x_cache)
                    break
            except ValueError:
                # print('invalid input')
                ms(title='Warning', message='Invalid input ! ! !')
                pass
            except TypeError:  # if cancel is pressed, a TypeError is raised. Then jump out of the cal and do nothing
                sc.remove() # remove the last calpoint drawn in the graph
                if self.x_before != []:
                    self.annot.xy = (self.x_before[-1], self.y_before[-1]) # re-annotate calpoint 1 to give a clear view
                    text = 'Calpoint {:d}'.format(self.counter) # counter = 1
                    self.annot.set_text(text)
                else:
                    self.annot.set_visible(False)

                self.press = True
                self.press_event = self.ax.figure.canvas.mpl_connect('button_press_event',
                                                                     self.onpress)  # re-enable the press event
                self._b_connect(True)
                return ''

        while True:
            try:
                # y_in = input('enter the calibrated y value for calibration point %d: ' % self.counter)
                y_in = qs(title=None,
                          prompt='Enter the calibrated Y value for calibration point %d: ' % (self.counter + 1))
                if float(y_in) == self.y_cache:
                    # print('must enter a different y value!!!')
                    ms(title='Warning', message='Must enter a different Y value ! ! !')
                else:
                    self.y_cache = float(y_in)
                    self.y_after.append(float(y_in))
                    # print(self.y_cache)
                    break
            except ValueError:
                # print('invalid input')
                ms(title='Warning', message='Invalid input ! ! !')
                pass
            except TypeError:
                self.x_cache = 9999
                del self.x_after[-1]  # remove the last x_after value from the list
                sc.remove()
                if self.x_before != []:
                    self.annot.xy = (self.x_before[-1], self.y_before[-1]) # re-annotate calpoint 1 to give a clear view
                    text = 'Calpoint {:d}'.format(self.counter) # counter = 1
                    self.annot.set_text(text)
                else:
                    self.annot.set_visible(False)

                self.press = True
                self.press_event = self.ax.figure.canvas.mpl_connect('button_press_event',
                                                                     self.onpress)  # re-enable the press event
                self._b_connect(True)
                return ''

        self.calpoint.append(sc)
        self.x_before.append(x)
        self.y_before.append(y)

        self.counter += 1

        self.press = True
        self.press_event = self.ax.figure.canvas.mpl_connect('button_press_event',
                                                             self.onpress)  # re-enable the press event
        self._b_connect(True)  # enable the buttons

    def _add_buttons(self):
        '''
        Add buttons to the matplotlib GUI
        '''
        self.button_cal = Button(plt.axes([0.18, 0.05, 0.12, 0.075]), 'Cal/Recal')
        self.button_showscatter = Button(plt.axes([0.375, 0.05, 0.1, 0.075]), 'Show')
        self.button_delscatter = Button(plt.axes([0.55, 0.05, 0.1, 0.075]), 'Delete')
        self.button_save = Button(plt.axes([0.725, 0.05, 0.1, 0.075]), 'Save')

    def _b_connect(self, con):
        '''
        If con = True, connect the buttons to the corresponding functions, otherwise disconnect the buttons
        '''
        if con:
            self.bc = self.button_cal.on_clicked(self.activate_cal)
            self.bss = self.button_showscatter.on_clicked(self.show_scatter)
            self.bds = self.button_delscatter.on_clicked(self.del_scatter)
            self.bs = self.button_save.on_clicked(self.save)

        else:
            self.button_cal.disconnect(self.bc)
            self.button_showscatter.disconnect(self.bss)
            self.button_delscatter.disconnect(self.bds)
            self.button_save.disconnect(self.bs)

    def del_scatter(self, event):
        '''
        Delete label points by iterating the self.labelpoint list
        '''
        self.annot.set_visible(False)
        try:
            for p in self.labelpoint:
                p.remove()
        except ValueError:
            pass

        self.labelpoint = []
        self.output = []

    def show_scatter(self, event):
        '''
        Hide label points by iterating the self.labelpoint list
        '''
        if self.showscatter_pressed:
            self.annot.set_visible(True)
            for p in self.calpoint:
                p.set_visible(True)
            for p in self.labelpoint:
                p.set_visible(True)
            self.showscatter_pressed = False
        else:
            self.annot.set_visible(False)
            for p in self.calpoint:
                p.set_visible(False)
            for p in self.labelpoint:
                p.set_visible(False)
            self.showscatter_pressed = True

    def activate_cal(self, event):
        '''
        Setting self.activated to True.
        Activate the calibration by two inputs which indicates whether the x and y axis is inverted in the plot
        '''
        self.ax.figure.canvas.mpl_disconnect(self.press_event)  # disable the press event when input
        self._b_connect(False)  # disable the buttons when input

        if self.cal_pressed:
            ms(title='Info', message='Now recalibration starts...')

        self.activated = False
        self.counter = 0
        self.x_before = []
        self.y_before = []
        self.x_after = []
        self.y_after = []
        self.x_cache = 9999
        self.y_cache = 9999

        self.annot.set_visible(False)

        try:  # try/except used here because calpoint has been removed after scaling, remove twice will cause ValueError
            for p in self.calpoint:
                p.remove()

        except ValueError:
            pass

        for p in self.labelpoint:

            p.remove()

        self.calpoint = []
        self.labelpoint = []
        self.cal_pressed = True

        x_dir = qs(title='Enter the direction of calibrated X axis',
                   prompt='    Standard axis press 1, inverted axis press 2    ')

        while True:
            if x_dir == str(1):
                self.xdir = 1
                break
            elif x_dir == str(2):
                self.xdir = -1
                break
            elif x_dir == None:  # it is tested by print(x_dir) that None will be returned when the cancel button is pressed
                self.press_event = self.ax.figure.canvas.mpl_connect('button_press_event',
                                                                     self.onpress)  # re-enable the press event
                self._b_connect(True)
                ms(title='Warning', message='Calibration paused !')
                return ''  # Then jump out of activate_cal and do nothing
            else:
                # print(x_dir)
                x_dir = qs(title='Enter the direction of calibrated X axis',
                           prompt='Invalid input ! Standard axis press 1, inverted axis press 2')
                # x_dir = input('invalid input, enter the direction of calibrated x axis, from left (negative) to right (postive) press 1, otherwise press 2: ')

        # y_dir = input('enter the direction of calibrated y axis, from bottom (negative) to top (postive) press 1, otherwise press 2: ')

        y_dir = qs(title='Enter the direction of calibrated Y axis',
                   prompt='    Standard axis press 1, inverted axis press 2    ')

        while True:
            if y_dir == str(1):
                self.ydir = -1  # the origin of matplotlib axis for import image is at the top left corner
                break
            elif y_dir == str(2):
                self.ydir = 1
                break
            elif y_dir == None:
                self.press_event = self.ax.figure.canvas.mpl_connect('button_press_event',
                                                                     self.onpress)  # re-enable the press event
                self._b_connect(True)
                ms(title='Warning', message='Calibration paused !')
                return ''
            else:
                y_dir = qs(title='Enter the direction of calibrated Y axis',
                           prompt='Invalid input ! Standard axis press 1, inverted axis press 2')

        # print('continue plotting two points and their calibrated coordinates to finish calibration...')
        ms(title='Info',
           message='Continue plotting two points and enter their calibrated coordinates to finish calibration...')
        self.press_event = self.ax.figure.canvas.mpl_connect('button_press_event',
                                                             self.onpress)  # re-enable the press event
        self._b_connect(True)

        self.activated = True

    def scaling(self, x_before, y_before, x_after, y_after):
        '''
        Calculate the ratio of scale between the matplotlib coordinate system and the expected coordinate system in the plot
        Calculate the origin of the new coordinate system
        '''
        print(self.x_before, self.x_after)

        upper_x = x_after[1] - x_after[0]
        lower_x = x_before[1] - x_before[0]
        self.scale_x = abs(upper_x / lower_x)  # ratio of displacement between matplotlib axis and image axis
        print('scale x:', self.scale_x)

        upper_y = y_after[1] - y_after[0]
        lower_y = y_before[1] - y_before[0]
        self.scale_y = abs(upper_y / lower_y)
        print('scale y:', self.scale_y)

        self.origin_x = x_before[1] - self.xdir * x_after[1] / self.scale_x
        self.origin_y = y_before[1] - self.ydir * y_after[1] / self.scale_y

        print('new origin:', self.origin_x, self.origin_y)

        self.counter += 1

        self.annot.set_visible(False)

        for p in self.calpoint:
            p.remove()

    def label(self, event, ax):
        '''
        After the third click on the plot, start labeling with matplotlib scatters.
        Calculate the coordinate of novel label points in the new coordinate system and display it in the screen
        Store the label points as events in self.labelpoint list, which can be removed by event.remove()
        or set invisible by event.set_invisible()
        '''
        x, y = event.xdata, event.ydata
        self.labelpoint.append(ax.scatter(x, y, marker='x'))
        for p in self.labelpoint:
            p.set_visible(True)
        # plt.pause(1)
        ax.figure.canvas.draw()
        # plt.draw()
        new_x = (x - self.origin_x) * self.scale_x * self.xdir
        new_y = (y - self.origin_y) * self.scale_y * self.ydir
        print(new_x, new_y)
        self.output.append([new_x, new_y])
        self.annot.xy = (x, y)
        text = "({:.2g}, {:.2g})".format(new_x, new_y)
        self.annot.set_text(text)
        self.annot.set_visible(True)

    def hover(self, p):
        '''
        calculate the coordinate of old label points and display it in the screen
        '''
        [[x, y]] = p.get_offsets()

        new_x = (x - self.origin_x) * self.scale_x * self.xdir
        new_y = (y - self.origin_y) * self.scale_y * self.ydir

        try:
            self.annot.xy = (x, y)
            text = '({:.2g}, {:.2g})'.format(new_x, new_y)
            self.annot.set_text(text)
            self.annot.set_visible(True)
            self.ax.figure.canvas.draw()

        except ValueError:
            pass

    def save(self, event):
        '''
        save the coordinate of label points in a csv file
        '''
        # sc = open('scatter.txt', 'w')
        file = sf(initialfile='Untitled.csv',
                defaultextension='.csv',
                title='Save as',
                filetypes=[("All Files", "*.*"), ("Comma-Separated Values File", "*.csv")])

        f = csv.writer(file)

        try:
            for p in self.output:
                f.writerow(p)
            file.close()
            ms(title='Info', message='Data saved !')
            
        except AttributeError:# when cancel is pressed
            pass






