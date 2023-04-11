
CONTENTS OF THIS FILE
---------------------

 * Introduction
 * Starting the PlotDigitizer
 * Using the PlotDigitizer


INTRODUCTION
------------

Producer: Ruiyang Liu <ruiyang.liu.19@ucl.ac.uk>

PlotDigitizer is an application that is designed to calibrate a 2D plot with new axes for academic usages.

Journal plots are the fruit of those academic researchers. Whilst the digital data of the plots are lost due to the loss of disc memory and the lack of cloud services, PlotDigitizer is intended to recover the data.


STARTING THE PlotDigitizer
--------------------------

To start the PlotDigitizer as .app in MacOS: 

   Free online download: 
   
   https://liveuclac-my.sharepoint.com/:u:/g/personal/zccarli_ucl_ac_uk/
   Ecc850WYIbBJpY5_jqSdEN8BmWvpa8092f37UaTmriBHsw?e=zMYshF

   Unzip the file and double click the PlotDigitizer.app to start

To start the PlotDigitizer as .py (strongly suggested to run in MacOS, some modifications in .py files may be required to adapt WindowsOS): 

   The libraries that you need:

   os, sys, stat, subprocesses, matplotlib, PIL, tkinter, mpl_interactions, csv, numpy

   Place main.py and plot_digitizer.py in the same folder and run main.py in IDE

To run the main.py in command line interface:

   Open the command line interface as administrator, enter <cd /the/working/directory>
   in the next line enter <python main.py>


USING THE PlotDigitizer
-----------------------

PlotDigitizer is now started and two options are displayed:

   <OPEN> 

   Browse image files in your computer, formats such as png, jpg, gif are accepted

   <README> 
   
   Open README.txt to help

After an image file is opened, it will be displayed by the matplotlib module using TkAgg backend which is compatible with the Tkinter GUI. Then you will see 4 buttons and the
built-in scrolling, zooming and panning functions provided by mpl-interactions:

   <Cal/Recal> 
    
   Start calibrating the axis, press again at any moment (unless a pop up input
   dialog is displayed) to recalibrate

   <Show>

   Show/hide the scatter points and annotations

   <Del>

   Only available after calibration is complete. Delete all label points

   <Save>

   Print out all label points (exclude calibration points), save as a csv file in your
   computer

   <Scrolling, zooming and panning> 

   Scroll to zoom the plot and hold right mouse button to pan


Please follow the instructions of the pop up messages.

After calibration is complete, click any place in the plot to start labelling. 



--------------------------------------- THE END -----------------------------------------

If you have any questions and advices, please email the producer. Thank you and enjoy!!!

-----------------------------------------------------------------------------------------