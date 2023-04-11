'''
os, stat, subprocess: libraries associated with files, e.g., file opening
matplotlib: image processing and labelling
PIL: used in error parsing when PIL.UnidentifiedImageError is raised
tkinter: building graphical user interface
mpl_interactions: provides additional functions in matplotlib, e.g., zooming and panning
'''
import os, stat, subprocess
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import PIL

from plot_digitizer import Click

from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox

from mpl_interactions import panhandler, zoom_factory

matplotlib.use('TKAgg') # backend
matplotlib.rcParams['toolbar'] = 'None' # remove matplotlib toolbar

ROOT = Tk()
ROOT.geometry('300x150+300+150')
ROOT.title('plot digitizer')
ROOT.resizable(width=False, height=False) # fix tkinter window

def exit():
    '''
    Standard function of exiting tkinter GUI
    '''
    if messagebox.askokcancel(title='Quit', message='Do you want to quit?'): # simpledialog is not useful here
        ROOT.destroy()
        #plt.close('all')

ROOT.protocol('WM_DELETE_WINDOW', exit)

def read_me():
    '''
    Search a file by os module and run the file by subprocess
    '''
    name = 'README.txt'

    path = os.path.dirname(os.path.abspath(__file__)) # return the absolute directory of the running script

    for root, dirs, files in os.walk(path, topdown=True): # open the first README topdown
        if name in files:
            file = os.path.join(root, name)
            os.chmod(file, stat.S_IREAD) # stat.S_IREAD read only for owner
            subprocess.run(['open', file], check=True)
            return ''

    simpledialog.messagebox.showwarning(title='Warning', message='No README.txt found')

def open_img():
    '''
    Open an image by tkinter.filedialog and create a canvas for the image by plt.subplot,
    finally display the image by plt.show
    '''
    while True:
        try:
            filename = filedialog.askopenfilename(title='Open')
            ROOT.withdraw() # hide GUI
            img = mpimg.imread(filename)

            break

        except PIL.UnidentifiedImageError:
            simpledialog.messagebox.showwarning(title='Warning', message='Cannot identify image file')

            pass

        except AttributeError: # in the case of pressing cancel
            ROOT.deiconify() # reveal GUI
            return '' # jump out of def

    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.imshow(img)
    ax1.axis('off')

    zoom = zoom_factory(ax1) # scroll to zoom
    pan_handler = panhandler(fig) # hold the right mouse button to pan the plot

    mng = plt.get_current_fig_manager()
    mng.window.resizable(width=False, height=False) # matplotlib becomes lagging when the window size gets larger, so fix the size

    Click(ax1, ROOT)

    plt.show()

    ROOT.destroy()

Button(ROOT, text='OPEN', command=open_img, width=10, height=2).place(relx=0.5, rely=0.3, anchor=CENTER)

Button(ROOT, text='README', command=read_me, width=10, height=2).place(relx=0.5, rely=0.7, anchor=CENTER)

ROOT.mainloop()





