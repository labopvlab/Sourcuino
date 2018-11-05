#! python3

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import *
from tkinter.ttk import Treeview
from tkinter import Tk, Label, Button, Frame, Entry, Scrollbar, OptionMenu, StringVar
from tkinter import filedialog
from scipy.interpolate import UnivariateSpline
from scipy import stats
from tkinter import font as tkFont
from PIL import ImageTk
import serial
import serial.tools.list_ports
from time import time, sleep
from datetime import datetime
import math
import numpy as np

from DegradDataPostTreatment import DegradDatatreatment

"""
TODOLIST


- export all data (mpp and JV param) when stopping degrad to avoid having to treat all the files

- put some try except in the data extraction to avoid exception convertion string to float and graphing strings...


- dump the data after saving so the memory is not overloaded => means cannot get automatically the graph with everything!


- units issue

"""


#topmpp = []
#bottommpp =[]
#timempp = []
DATA=[]
minx=0
maxx=0.5
miny=-5
maxy=5

timetoSave = 10 #min

def center(win):
    
    #centers a tkinter window
    #:param win: the root or Toplevel window to center
   
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

class Sourcuino(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.title("Sourcuino")
        
        
        
        for r in range(60):
            master.rowconfigure(r, weight=1)    
        for c in range(100):
            master.columnconfigure(c, weight=1)

        self.superframe=master
        
        self.Frame1 = Frame(master, bg="black")#title black frame
        self.Frame1.grid(row = 0, column = 5, rowspan = 3, columnspan = 85, sticky = W+E+N+S) 
        self.Frame2 = Frame(master, bg="gray")#frame on left for connection and calib
        self.Frame2.grid(row = 3, column = 0, rowspan = 30, columnspan = 5, sticky = W+E+N+S)
        self.Frame3 = Frame(master, bg="red")#frame on bottom left for info display
        self.Frame3.grid(row = 33, column = 0, rowspan = 20, columnspan = 5, sticky = W+E+N+S)
        self.Frame5 = Frame(master, bg="white")#frame of the graphs
        self.Frame5.grid(row = 3, column = 5, rowspan = 15, columnspan = 95, sticky = W+E+N+S)
        
        self.Frame41 = Frame(master, bg="gray")#frame at bottom for parameters entries
        self.Frame41.grid(row = 33, column = 5, rowspan = 20, columnspan = 32, sticky = W+E+N+S)
        self.Frame42 = Frame(master, bg="gray")#frame at bottom for parameters entries
        self.Frame42.grid(row = 33, column = 37, rowspan = 20, columnspan = 27, sticky = W+E+N+S)
        self.Frame43 = Frame(master, bg="gray")#frame at bottom for parameters entries
        self.Frame43.grid(row = 33, column = 64, rowspan = 20, columnspan = 36, sticky = W+E+N+S)
        
        ##########################################################################################################
        #title frame
        ############
        
        label = tk.Label(self.Frame1, text="                  ")
        label.config(font=("Courier", 30),fg='black',background='black')
        label.grid(row=0, column=0,columnspan=10)
        label = tk.Label(self.Frame1, text="Sourcuino")
        label.config(font=("Courier", 30),fg='white',background='black')
        label.grid(row=0, column=10,columnspan=30)
        label = tk.Label(self.Frame1, text="developed by Jonas Geissbuehler and Jeremie Werner")
        label.config(font=("Courier", 10),fg='white',background='black')
        label.grid(row=1, column=10,columnspan=30)
        
        ##########################################################################################################

        
        
        ##########################################################################################################
        label = tk.Label(self.Frame2, text="  ")
        label.config(font=("Courier", 15),fg='black',background='gray')
        label.grid(row=0, column=0,columnspan=5,rowspan=2)
        label = tk.Label(self.Frame2, text="Connection")
        label.config(font=("Courier", 15),fg='black',background='gray')
        label.grid(row=2, column=0,columnspan=5)
        self.connectioncheck = Button(self.Frame2, text="Connect",
                            command = self.ConnectArduino)
        self.connectioncheck.grid(row=3, column=0, columnspan=5)
        #portlist = ["COM3","COM4"]#to be replaced by function that looks what port are available and propose those to the user, then user choose which one to connect the arduino
        #self.port=StringVar()
        #self.port.set("COM4") # default choice
        #self.dropMenuPort = OptionMenu(self.Frame2, self.port, *portlist, command=())
        #self.dropMenuPort.grid(row=4, column=0, columnspan=5)
        self.connectlabel = tk.StringVar()
        self.conlabel = Label(self.Frame3, textvariable=self.connectlabel)
        self.conlabel.config(font=("Courier", 15),fg='black',background='red')
        self.conlabel.grid(row=1, column=0, columnspan=5)
        
        
        label = tk.Label(self.Frame2, text="  ")
        label.config(font=("Courier", 15),fg='black',background='gray')
        label.grid(row=12, column=0,columnspan=5,rowspan=1)

        label = tk.Label(self.Frame2, text="  ")
        label.config(font=("Courier", 15),fg='black',background='gray')
        label.grid(row=13, column=0,columnspan=5,rowspan=1)
        
        
        FrameChoicelist = ["JV scan","MPPT","Degradation","DataStitchingAnalysis"]
        self.FrameChoice=StringVar()
        self.FrameChoice.set("JV scan") # default choice
        self.dropMenuFrame = OptionMenu(self.Frame2, self.FrameChoice, *FrameChoicelist, command=self.FrameTypeChoice)
        self.dropMenuFrame.grid(row=15, column=0, columnspan=5)
        self.FrameTypeChoice(1)
        
        ##########################################################################################################

        label = tk.Label(self.Frame41, text="              ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=0, column=0,columnspan=95)
        label = tk.Label(self.Frame41, text="              ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=1, column=0,columnspan=95)
        label = tk.Label(self.Frame41, text="       ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=0, column=0,rowspan=20)
        
        label = tk.Label(self.Frame42, text="              ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=0, column=0,columnspan=95)
        label = tk.Label(self.Frame42, text="              ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=1, column=0,columnspan=95)
        label = tk.Label(self.Frame42, text="       ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=0, column=0,rowspan=20)
        
        label = tk.Label(self.Frame43, text="              ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=0, column=0,columnspan=95)
        label = tk.Label(self.Frame43, text="              ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=1, column=0,columnspan=95)
        label = tk.Label(self.Frame43, text="       ")
        label.config(font=("Courier", 5),fg='white',background='gray')
        label.grid(row=0, column=0,rowspan=20)
        
        colpos=2
        rowpos=2

        label = tk.Label(self.Frame41, text="J-V scan  ")
        label.config(font=("Courier", 15),fg='black',background='gray')
        label.grid(row=rowpos, column=colpos,columnspan=2)
        jvcelllist = ["Top cell","Bottom cell"]
        self.jvcell=StringVar()
        self.jvcell.set("Bottom cell") # default choice
        self.dropMenuJV = OptionMenu(self.Frame41, self.jvcell, *jvcelllist, command=())
        self.dropMenuJV.grid(row=rowpos, column=colpos+2, columnspan=6)
        
        self.VstartJV = tk.DoubleVar()
        Entry(self.Frame41, textvariable=self.VstartJV,width=5).grid(row=rowpos+1,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame41, text="Vstart (V)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+1,column=colpos,columnspan=2)
        self.VstartJV.set(1.8)
        self.VendJV = tk.DoubleVar()
        Entry(self.Frame41, textvariable=self.VendJV,width=5).grid(row=rowpos+2,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame41, text="Vend (V)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+2,column=colpos,columnspan=2)
        self.VendJV.set(-0.2)
        self.DelayJV = tk.DoubleVar()
        Entry(self.Frame41, textvariable=self.DelayJV,width=5).grid(row=rowpos+3,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame41, text="Delay (s)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+3,column=colpos,columnspan=2)
        self.DelayJV.set(0.1)
        #self.IntegtJV = tk.DoubleVar()
        #Entry(self.Frame4, textvariable=self.IntegtJV,width=5).grid(row=rowpos+5,column=colpos+2,columnspan=2)
        #label=tk.Label(self.Frame4, text="Integ. time (s)")
        #label.config(font=("Courier", 10),fg='black',background='gray')
        #label.grid(row=rowpos+5,column=colpos,columnspan=2)
        #self.IntegtJV.set(0.1)
        self.NbPtsJV = tk.DoubleVar()
        Entry(self.Frame41, textvariable=self.NbPtsJV,width=5).grid(row=rowpos+4,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame41, text="Nb Points")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+4,column=colpos,columnspan=2)
        self.NbPtsJV.set(100)
        self.CellArea = tk.DoubleVar()
        Entry(self.Frame41, textvariable=self.CellArea,width=5).grid(row=rowpos+5,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame41, text="Area (cm2)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+5,column=colpos,columnspan=2)
        self.CellArea.set(1)
        self.PowerCheck = tk.IntVar()
        PowerCheckButton = tk.Checkbutton(self.Frame41,text="PowerCurve",
            variable=self.PowerCheck)
        PowerCheckButton.grid(row=rowpos+5, column=colpos+4, columnspan=4)
        self.PowerCheck.set(1)
        
        self.StartJVscan = Button(self.Frame41, text="Start Scan",fg='green',
                            command = self.IVsweepDyn)
        self.StartJVscan.grid(row=rowpos+1, column=colpos+4, columnspan=4)
        self.saveJVgraph = Button(self.Frame41, text="Save graph",
                            command = self.ExportGraph)
        self.saveJVgraph.grid(row=rowpos+3, column=colpos+4, columnspan=4)
        self.ClearJVgraph = Button(self.Frame41, text="Clear graph",
                            command = self.ClearGraph)
        self.ClearJVgraph.grid(row=rowpos+4, column=colpos+4, columnspan=4)
        self.curvename = tk.StringVar()
        entry=Entry(self.Frame41, textvariable=self.curvename,width=10)
        entry.grid(row=rowpos+2, column=colpos+4, columnspan=4)

        self.SaveJVpath = tk.StringVar()
        Entry(self.Frame41, textvariable=self.SaveJVpath,width=45).grid(row=rowpos+7,column=colpos,columnspan=8)
        self.SaveJVpath.set("C:\\Users\\jwerner\\switchdrive\\arduino\\degradationdata")

        
        colpos=2
        rowpos=2
        label = tk.Label(self.Frame42, text="MPPT")
        label.config(font=("Courier", 15),fg='black',background='gray')
        label.grid(row=rowpos, column=colpos,columnspan=2)
        mpplist = ["Top cell","Bottom cell", "Both cells"]
        self.mppcell=StringVar()
        self.mppcell.set("Bottom cell") # default choice
        self.dropMenumpp = OptionMenu(self.Frame42, self.mppcell, *mpplist, command=())
        self.dropMenumpp.grid(row=rowpos, column=colpos+2, columnspan=7)
        
        self.Vstarttop = tk.DoubleVar()
        Entry(self.Frame42, textvariable=self.Vstarttop,width=5).grid(row=rowpos+1,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame42, text="Vstart top (V)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+1,column=colpos,columnspan=2)
        self.Vstarttop.set(1)
        self.Vstartbottom = tk.DoubleVar()
        Entry(self.Frame42, textvariable=self.Vstartbottom,width=5).grid(row=rowpos+2,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame42, text="Vstart bottom (V)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+2,column=colpos,columnspan=2)
        self.Vstartbottom.set(1)
        self.Duration = tk.DoubleVar()
        Entry(self.Frame42, textvariable=self.Duration,width=5).grid(row=rowpos+3,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame42, text="Duration (s)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+3,column=colpos,columnspan=2)
        self.Duration.set(30)
        self.Vstep = tk.DoubleVar()
        Entry(self.Frame42, textvariable=self.Vstep,width=5).grid(row=rowpos+4,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame42, text="Vstep (mV)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+4,column=colpos,columnspan=2)
        self.Vstep.set(10)
        
        
        self.StartMPP = Button(self.Frame42, text="Start MPPT",fg='green', 
                            command = self.MPPT)
        self.StartMPP.grid(row=rowpos+1, column=colpos+4, columnspan=5)
        self.stopmppcheck=1
        self.StopMPP = Button(self.Frame42, text="Stop MPPT",fg='red',
                            command = self.stopmppt)
        self.StopMPP.grid(row=rowpos+2, column=colpos+4, columnspan=5)
        self.saveMPPgraph = Button(self.Frame42, text="Save graph",
                            command = self.ExportGraph)
        self.saveMPPgraph.grid(row=rowpos+3, column=colpos+4, columnspan=5)
        self.ClearMPPgraph = Button(self.Frame42, text="Save data txt",
                            command = self.ExportMPPTdat)
        self.ClearMPPgraph.grid(row=rowpos+4, column=colpos+4, columnspan=5)
        
        
        colpos=2
        rowpos=2
        label = tk.Label(self.Frame43, text="Degradation")
        label.config(font=("Courier", 15),fg='black',background='gray')
        label.grid(row=rowpos, column=colpos,columnspan=2)
        deglist = ["Top cell","Bottom cell", "Both cells"]
        self.degcell=StringVar()
        self.degcell.set("Bottom cell") # default choice
        self.dropMenumpp = OptionMenu(self.Frame43, self.degcell, *deglist, command=())
        self.dropMenumpp.grid(row=rowpos, column=colpos+2, columnspan=7)
        
        self.VstartJVdeg = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.VstartJVdeg,width=5).grid(row=rowpos+1,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Vstart (V)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+1,column=colpos,columnspan=2)
        self.VstartJVdeg.set(1.8)
        self.VendJVdeg = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.VendJVdeg,width=5).grid(row=rowpos+2,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Vend (V)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+2,column=colpos,columnspan=2)
        self.VendJVdeg.set(-0.2)
        self.DelayJVdeg = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.DelayJVdeg,width=5).grid(row=rowpos+3,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Delay (s)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+3,column=colpos,columnspan=2)
        self.DelayJVdeg.set(0.1)
        self.NbPtsJVdeg = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.NbPtsJVdeg,width=5).grid(row=rowpos+4,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Nb Points")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+4,column=colpos,columnspan=2)
        self.NbPtsJVdeg.set(100)
        self.CellAreadeg = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.CellAreadeg,width=5).grid(row=rowpos+5,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Areatop (cm2)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+5,column=colpos,columnspan=2)
        self.CellAreadeg.set(1)
        self.CellAreadeg1 = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.CellAreadeg1,width=5).grid(row=rowpos+6,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Areabot (cm2)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+6,column=colpos,columnspan=2)
        self.CellAreadeg1.set(1)
        self.Durationdeg = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.Durationdeg,width=5).grid(row=rowpos+7,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Duration mppt (s)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+7,column=colpos,columnspan=2)
        self.Durationdeg.set(200)
        self.Vstepdeg = tk.DoubleVar()
        Entry(self.Frame43, textvariable=self.Vstepdeg,width=5).grid(row=rowpos+8,column=colpos+2,columnspan=2)
        label=tk.Label(self.Frame43, text="Vstep (mV)")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+8,column=colpos,columnspan=2)
        self.Vstepdeg.set(10)
        
        
        self.StartDeg = Button(self.Frame43, text="Start Degr",fg='green', 
                            command = self.Degradation)
        self.StartDeg.grid(row=rowpos+1, column=colpos+4, columnspan=2)
        self.stopdegcheck=1
        self.StopDeg = Button(self.Frame43, text="Stop Degr",fg='red',
                            command = self.stopdegradation)
        self.StopDeg.grid(row=rowpos+2, column=colpos+4, columnspan=2)
        self.savedeggraph = Button(self.Frame43, text="Save graph",
                            command = self.ExportGraph)
        self.savedeggraph.grid(row=rowpos+3, column=colpos+4, columnspan=2)
        self.Cleardeggraph = Button(self.Frame43, text="Clear graph",
                            command = self.ClearDegGraph)
        self.Cleardeggraph.grid(row=rowpos+4, column=colpos+4, columnspan=2)
        
        self.Savepath = tk.StringVar()
        Entry(self.Frame43, textvariable=self.Savepath,width=25).grid(row=rowpos+6,column=colpos+4,columnspan=4)
        label=tk.Label(self.Frame43, text="Auto-saving path")
        label.config(font=("Courier", 10),fg='black',background='gray')
        label.grid(row=rowpos+5,column=colpos+4,columnspan=4)
        self.Savepath.set("C:\\Users\\jwerner\\switchdrive\\arduino\\degradationdata")
        
        self.namedeg = tk.StringVar()
        Entry(self.Frame43, textvariable=self.namedeg,width=25).grid(row=rowpos+7,column=colpos+4,columnspan=4)
        self.namedeg.set("top")
        self.namedeg2 = tk.StringVar()
        Entry(self.Frame43, textvariable=self.namedeg2,width=25).grid(row=rowpos+8,column=colpos+4,columnspan=4)
        self.namedeg2.set("bot")
        
        self.VoctrackCheck = tk.IntVar()
        VocCheckButton = tk.Checkbutton(self.Frame43,text="VocTracking",
            variable=self.VoctrackCheck)
        VocCheckButton.grid(row=rowpos+1, column=colpos+6, columnspan=2)
        self.VoctrackCheck.set(0)
        
        ##########################################################################################################
    def FrameTypeChoice(self,a):
        global DATA
        
        if self.FrameChoice.get()=="DataStitchingAnalysis":
            plt.close() 
            #add here the data analysis. stitch together the mppt files generated during degrad protocol
            #seconds or hours in x-axis, pmpp, jmpp, vmpp
            #stitch together multiple session on same cell, according to start date&time. order the files by file name, then check if count restarts from zero, if so add the previous time mpp + interval from filenametime
            
            DegradDatatreatment()
        
        if self.FrameChoice.get()=="JV scan":
            plt.close()            
            self.fig = plt.figure(figsize=(15, 5.5))
            self.fig.patch.set_facecolor('white')
            canvas = FigureCanvasTkAgg(self.fig, self.Frame5)
            canvas.get_tk_widget().grid(row=0,column=0,rowspan=5,columnspan=95)
            self.IVsubfig = self.fig.add_subplot(121)
            #self.mppsubfig = self.fig.add_subplot(122)
            
            self.Frame6 = Frame(self.superframe, bg="white")
            self.Frame6.grid(row = 3, column = 53, rowspan = 15, columnspan = 45, sticky = W+E+N+S)
    
            self.IVsubfig.set_xlabel('Voltage (V)',fontsize=15)
            self.IVsubfig.set_ylabel('Current density (mA/cm$^2$)',fontsize=15)
            self.IVsubfig.axhline(y=0, color='k')
            self.IVsubfig.axvline(x=0, color='k')
            self.IVsubfig.tick_params(labelsize=15)
            self.fig.subplots_adjust(wspace=0.3)
            self.TableBuilder(self.Frame6)
        
        if self.FrameChoice.get()=="MPPT":
            plt.close()
            DATA=[]
            self.TableBuilder(self.Frame6)
            
        
            self.Frame5 = Frame(self.superframe, bg="white")
            self.Frame5.grid(row = 3, column = 5, rowspan = 15, columnspan = 95, sticky = W+E+N+S)
            
            self.start_time = time()
            self.timepointsmpp = []
            self.mppdata = []
            
            #self.ser = serial.Serial('COM4', 115200)

            self.fig1 = plt.figure(figsize=(15, 5.5))
            self.fig1.patch.set_facecolor('white')
            canvas = FigureCanvasTkAgg(self.fig1, self.Frame5)
            canvas.get_tk_widget().grid(row=0,column=0,rowspan=15,columnspan=95)
            self.mppfig=self.fig1.add_subplot(111)
            self.mppfig.set_xlabel('Time (s)',fontsize=15)
            self.mppfig.set_ylabel('Power (W/m$^2$)',fontsize=15) #to be checked for the units
            plt.axes().grid(True)
            plt.axes().grid(True)
            #plt.xlabel('Time (s)',fontsize=15)
            #plt.ylabel('Power (W/m$^2$)',fontsize=15)
            #plt.axes().grid(True)
            #plt.axes().grid(True)
            #self.line1, = plt.plot(self.mppdata,marker='o',markersize=3,linestyle='none',markerfacecolor='red')
      
        if self.FrameChoice.get()=="Degradation":
            plt.close()
            DATA=[]
            self.TableBuilder(self.Frame6)
            self.Frame5 = Frame(self.superframe, bg="white")
            self.Frame5.grid(row = 3, column = 5, rowspan = 15, columnspan = 95, sticky = W+E+N+S)
            
            self.fig = plt.figure(figsize=(15, 5.5))
            self.fig.patch.set_facecolor('white')
            canvas = FigureCanvasTkAgg(self.fig, self.Frame5)
            canvas.get_tk_widget().grid(row=0,column=0,rowspan=15,columnspan=95)
            self.VocsubfigTop = self.fig.add_subplot(232)
            self.JscsubfigTop = self.fig.add_subplot(233)
            self.VocsubfigBot = self.fig.add_subplot(235)
            self.JscsubfigBot = self.fig.add_subplot(236)
            self.mppdegsubfig = self.fig.add_subplot(231)
            self.IVdegsubfig = self.fig.add_subplot(234)
    
            
            self.VocsubfigTop.set_xlabel("Time (s)",fontsize=8)
            self.VocsubfigTop.set_ylabel("Voc topcell (V)",fontsize=8)
            self.VocsubfigTop.tick_params(labelsize=8)
            
            self.JscsubfigTop.set_xlabel("Time (s)",fontsize=8)
            self.JscsubfigTop.set_ylabel("Jsc topcell (mA/cm$^2$)",fontsize=8)
            self.JscsubfigTop.tick_params(labelsize=8)
            
            self.VocsubfigBot.set_xlabel("Time (s)",fontsize=8)
            self.VocsubfigBot.set_ylabel("Voc botcell (V)",fontsize=8)
            self.VocsubfigBot.tick_params(labelsize=8)
            
            self.JscsubfigBot.set_xlabel("Time (s)",fontsize=8)
            self.JscsubfigBot.set_ylabel("Jsc botcell (mA/cm$^2$)",fontsize=8)
            self.JscsubfigBot.tick_params(labelsize=8)
            
            
            self.mppdegsubfig.set_xlabel('Time (s)',fontsize=8)
            self.mppdegsubfig.set_ylabel('Power (mW/cm$^2$)',fontsize=8)  #to be checked for the units
            self.mppdegsubfig.tick_params(labelsize=8)
            
            self.IVdegsubfig.set_xlabel('Voltage (V)',fontsize=8)
            self.IVdegsubfig.set_ylabel('Current density (mA/cm$^2$)',fontsize=8)
            self.IVdegsubfig.axhline(y=0, color='k')
            self.IVdegsubfig.axvline(x=0, color='k')
            self.IVdegsubfig.tick_params(labelsize=8)
            
            self.fig.subplots_adjust(wspace=0.2)
    
    def stopdegradation(self):
        self.stopdeg=0     
    
    def stopmppt(self):
        self.stopmppt=0 
        
                
    def Degradation(self):
        ###########parameters definition###################
        global minx, maxx, miny, maxy
        global timetoSave
        
        self.stopdeg=1
        
        whichcell=self.degcell.get() #define which channel to probe
        
        SampleNametop=self.namedeg.get() #give a name to the measurement
        SampleNamebot=self.namedeg2.get() #give a name to the measurement
        #duration = 500 # total seconds to collect data
        Vstart=1000*self.VstartJVdeg.get() #voltage to start JV sweep
        Vend=1000*self.VendJVdeg.get() #voltage to end JV sweep
        CellArea=self.CellAreadeg.get() #cm2, aperture area
        Nbpoints=self.NbPtsJVdeg.get() #nb of points in the JV curve
        DurationMpp=self.Durationdeg.get() #nb of seconds of tracking between each JV curve
        Vstep=self.Vstepdeg.get() #voltage step to be used for mppt
        
        
        #where to save the generated data
        #filename = self.Savepath.get()
        
        ###########################################
        
        timepointsJVtop=[]
        Vocdatatop = []
        Jscdatatop = []
        FFdatatop = []
        Effdatatop = []
        #DATAtop=[]
        mppdatatop = []
        timepointsJVbot=[]
        Vocdatabot = []
        Jscdatabot = []
        FFdatabot = []
        Effdatabot = []
        #DATAbot=[]
        mppdatabot = []
        timepointsmpp = []
        ########################################################################################
        #ser = serial.Serial('COM5', 115200)
        #sleep(2)
        self.ser.flushInput()
        start_time = time()
        
        
        #run = True
        #savingtime=time()
        #savelist=[0]
        #k=0
        x=[]
        y=[]
        plt.ion()
        self.lineIV,=self.IVdegsubfig.plot(x,y,marker='o',markersize=2)
        #self.linempp,=self.mppdegsubfig.plot(x,y,marker='o',markersize=2)
        self.linempp,=self.mppdegsubfig.plot(x,y,marker='o',markersize=1)
        self.linempptop,=self.mppdegsubfig.plot(mppdatatop,marker='o',markersize=1,c='r')
        self.linemppbot,=self.mppdegsubfig.plot(mppdatabot,marker='o',markersize=1,c='b')
        
        #self.linevoc,=self.VocsubfigTop.plot(x,y,marker='o')
        self.linevoctop,=self.VocsubfigTop.plot(Vocdatatop,marker='o',c='r')
        #self.linevoc,=self.VocsubfigBot.plot(x,y,marker='o')
        self.linevocbot,=self.VocsubfigBot.plot(Vocdatabot,marker='o',c='b')
        
        #self.linejsc,=self.JscsubfigTop.plot(x,y,marker='o')
        self.linejsctop,=self.JscsubfigTop.plot(Jscdatatop,marker='o',c='r')
        #self.linejsc,=self.JscsubfigBot.plot(x,y,marker='o')
        self.linejscbot,=self.JscsubfigBot.plot(Jscdatabot,marker='o',c='b')
        
        
        
        
        while True:
        
        #############################JVscan##############################################
            try:
                if self.stopdeg==0:
                    break
                
                cellschoice=[]
                if whichcell=="Top cell":
                    cellschoice=["Top cell"]
                elif whichcell=="Bottom cell":
                    cellschoice=["Bottom cell"]
                elif whichcell=="Both cells":
                    cellschoice=["Top cell","Bottom cell"]
                Vocdatatopint = []
                Jscdatatopint = []
                FFdatatopint = []
                Effdatatopint = []
                Vocdatabotint = []
                Jscdatabotint = []
                FFdatabotint = []
                Effdatabotint = []
                for item in cellschoice:
                    cell=item
                    timestart=time()
                    timepointsJV=[]
                    datainterm={}
                    #DATA=[]
                    command=""
                    if cell=="Top cell":
                        command+="sweeptop"
                        SampleName=SampleNametop
                        datainterm["CellSurface"]=self.CellAreadeg.get()
                    elif cell=="Bottom cell":
                        command+="sweepbot"
                        SampleName=SampleNamebot
                        datainterm["CellSurface"]=self.CellAreadeg1.get()
                    
                    command+="="+str(Vstart)+":"+str(Vend)+";"+str(Nbpoints)+","+str(0)
                    
                    self.ser.write(command.encode())
                    x=[]
                    y=[]
        
                    stop=0
                    start=0
                    while stop!=1:
                        line=str(self.ser.readline().strip().decode())
                        #print(line)
                        if line=="sweepending":
                            stop=1
                        if stop!=1 and line == "sweepstarting":
                            start=1
                        if stop!=1 and start and line != "sweepstarting":
                            #print(line)
                            x.append(float(line.split(",")[0])/1000) #volt
                            #print(float(line.split(",")[0])/1000)
                            y.append(float(line.split(",")[1])/datainterm["CellSurface"]) #mA/cm2
                            self.lineIV.set_xdata(x)
                            self.lineIV.set_ydata(y)
                            if min(x)<minx:
                                minx=min(x)
                            if max(x)>maxx:
                                maxx=max(x)
                            if 1.2*min(y)<miny:
                                miny=1.2*min(y)
                            if max(y)>maxy:
                                maxy=max(y)
                            self.IVdegsubfig.axis([minx,maxx,miny,maxy])
                            
                            try:
                                self.fig.canvas.draw()
                                self.fig.canvas.flush_events()
                            except:
                                print("exception with draw")
                    
                            
                    
                    datainterm["x"]=x
                    datainterm["y"]=y
                    
                    #calculate JV parameters
                    testfind=0
                    for i in range(len(x)-1):
                        if np.sign(x[i])!=np.sign(x[i+1]):
                            #datainterm["Jsc"]=-(y[i]-x[i]*(y[i+1]-y[i])/(x[i+1]-x[i]))/datainterm["CellSurface"]
                            testfind=1
                            try:
                                xregress=[x[i+2],x[i+1],x[i],x[i-1]]
                                yregress=[y[i+2],y[i+1],y[i],y[i-1]]
                                slope, intercept, r_value, p_value, std_err = stats.linregress(xregress,yregress)
                                #print(datainterm["Jsc"])
                                #print(-intercept/datainterm["CellSurface"])
                                datainterm["Jsc"]=-intercept #mA/cm2
                            except:
                                datainterm["Jsc"]=0
                                print("xregress problem")
                            break
                        else:
                            datainterm["Jsc"]=0
                    if testfind==0:
                        print("could not find Jsc")
                    testfind=0
                    for i in range(len(y)-1):
                        if np.sign(y[i+1])!=np.sign(y[i]):
                            #datainterm["Voc"]=(x[i]-y[i]*(x[i]-x[i+1])/(y[i]-y[i+1]))
                            testfind=1
                            xregress=[x[i+2], x[i+1],x[i],x[i-1],x[i-2]]
                            yregress=[y[i+2], y[i+1],y[i],y[i-1], y[i-2]]
                            slope, intercept, r_value, p_value, std_err = stats.linregress(xregress,yregress)
                            datainterm["Voc"]=-1000*intercept/slope #mV
                            break
                        else:
                            datainterm["Voc"]=0
                    if testfind==0:
                        print("could not find Voc") 
                        print(datainterm["Voc"])
                    #print(x)
                    try:
                        a=list(zip(*sorted(zip(x, y))))#need to verify that x is increasing order!
                        x=list(a[0])
                        y=list(a[1])
                        
                        spl = UnivariateSpline(x, y, s=0)
                        #print(datainterm["Jsc"])
                        #print(-spl(0)/datainterm["CellSurface"])
                        power = [x[i]*y[i] for i in range(len(x))]
                        powerspl=UnivariateSpline(x, power, s=0)
                        #plt.plot(x,powerspl(x))
                        powersplder=powerspl.derivative(n=1)
                        powersplderdiscret=[powersplder(xi) for xi in x]
                    
                        #print(powersplderdiscret)
                        for i in range(len(powersplderdiscret)-1):
                            if np.sign(powersplderdiscret[i+1])!=np.sign(powersplderdiscret[i]):
                                try:
                                    xregress=[x[i+2], x[i+1],x[i],x[i-1]]
                                    yregress=[powersplderdiscret[i+2], powersplderdiscret[i+1], powersplderdiscret[i], powersplderdiscret[i-1]]
                                    slope, intercept, r_value, p_value, std_err = stats.linregress(xregress,yregress)
                                except:
                                    print("regression problem")
                                try:
                                    datainterm["Vmpp"]=-1000*intercept/slope  #mV
                                    #print(datainterm["Vmpp"])
                                    datainterm["Jmpp"]=abs(spl(datainterm["Vmpp"]/1000))
                                    #print(datainterm["Jmpp"])
                                    datainterm["FF"]=datainterm["Jmpp"]*datainterm["Vmpp"]/(datainterm["Voc"]*datainterm["Jsc"])
                                    datainterm["Eff"]=abs(datainterm["Jsc"]*datainterm["Voc"]*datainterm["FF"]/1000)
                                except:
                                    datainterm["Vmpp"]=0
                                    datainterm["Jmpp"]=0
                                    datainterm["FF"]=0
                                    datainterm["Eff"]=0
                                break
                    except:
                        print("problem with powerspl")
                        datainterm["Vmpp"]=0
                        datainterm["Jmpp"]=0
                        datainterm["FF"]=0
                        datainterm["Eff"]=0
                    
                    """    
                    try:
                        datainterm["Vmpp"]=fsolve(powersplder,0.8*datainterm["Voc"])[0]*1000
                        print(datainterm["Vmpp"])
                        datainterm["Jmpp"]=abs(spl(datainterm["Vmpp"]/1000))
                        #print(datainterm["Jmpp"])
                        datainterm["FF"]=datainterm["Jmpp"]*datainterm["Vmpp"]/(datainterm["Voc"]*datainterm["Jsc"])/10
                        #print(datainterm["FF"])
                        datainterm["Eff"]=abs(datainterm["Jsc"]*datainterm["Voc"]*datainterm["FF"]/100)
                    except:
                        print("could not calculate FF")
                    """
                    try:
                        if math.isnan(datainterm["Vmpp"]):
                            #print("this is it")
                            datainterm["Vmpp"]=0
                        if math.isnan(datainterm["Jmpp"]):
                            #print("this is it")
                            datainterm["Jmpp"]=0
                        if math.isnan(datainterm["FF"]):
                            #print("this is it")
                            datainterm["FF"]=0 
                            datainterm["Eff"]=0
                    except KeyError:
                        print("keyerror... all set to 0")
                        datainterm["Vmpp"]=0
                        datainterm["Jmpp"]=0
                        datainterm["FF"]=0
                        datainterm["Eff"]=0
                        
                    """
                    datainterm["Vmpp"]=0
                    datainterm["Jmpp"]=0
                    datainterm["FF"]=0 
                    datainterm["Eff"]=0
                    """
                    
                    datainterm["SampleName"]=SampleName+"_"+str(datetime.now().strftime('%Y.%m.%d-%H.%M.%S'))
        
                    
                    if Vstart<Vend:
                        datainterm["ScanDirection"]="Forward"
                    else:
                        datainterm["ScanDirection"]="Reverse"
                    #DATA.append(datainterm)
                    
                    timeend=time()
                    elapsed=timeend-timestart
                    contenttxtfile=["Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_"+SampleName+"\n",
                            "Vstart=\t"+str(Vstart)+"\n",
                            "Vend=\t"+str(Vend)+"\n",
                            "Nb of points=\t"+str(Nbpoints)+"\n",
                            "Total scan fct time (s)=\t"+'%.2f' % float(elapsed)+"\n\n",
                            "Voc=\t"+str(datainterm["Voc"])+"\n","Jsc=\t"+str(datainterm["Jsc"])+"\n","FF=\t"+str(datainterm["FF"])+"\n","Eff.=\t"+str(datainterm["Eff"])+"\n",
                            "Vmpp=\t"+str(datainterm["Vmpp"])+"\n","Jmpp=\t"+str(datainterm["Jmpp"])+"\n","\n\n","DATA:\n"]
                    
                    
                    for item in range(len(x)):
                        contenttxtfile.append(str(x[item])+"\t"+str(y[item])+"\n")
                    
                    file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_"+SampleName+".txt",'w')
                    
                    file.writelines("%s" % item for item in contenttxtfile)
                    file.close()
                    
                    if cell=="Top cell":
                        Vocdatatopint.append(datainterm["Voc"])
                        Jscdatatopint.append(datainterm["Jsc"])
                        FFdatatopint.append(datainterm["FF"])
                        Effdatatopint.append(datainterm["Eff"])
                        
                    elif cell=="Bottom cell":
                        Vocdatabotint.append(datainterm["Voc"])
                        Jscdatabotint.append(datainterm["Jsc"])
                        FFdatabotint.append(datainterm["FF"])
                        Effdatabotint.append(datainterm["Eff"])
                    
                    timepointsJV.append(time()-start_time)
    
                if whichcell=="Top cell":
                    timepointsJVtop+=timepointsJV
                    Vocdatatop+=Vocdatatopint
                    Jscdatatop+=Jscdatatopint
                    FFdatatop+=FFdatatopint
                    Effdatatop+=Effdatatopint
                    #DATAtop+=DATA
                    self.linevoctop.set_xdata(timepointsJVtop)
                    self.linevoctop.set_ydata(Vocdatatop)
                    self.VocsubfigTop.set_ylim([0.8*min(Vocdatatop),1.2*max(Vocdatatop)])
                    self.VocsubfigTop.set_xlim([min(timepointsJVtop),max(timepointsJVtop)])
                                
                    self.linejsctop.set_xdata(timepointsJVtop)
                    self.linejsctop.set_ydata(Jscdatatop)
                    self.JscsubfigTop.set_ylim([0.8*min(Jscdatatop),1.2*max(Jscdatatop)])
                    self.JscsubfigTop.set_xlim([min(timepointsJVtop),max(timepointsJVtop)])
    
                    if mppdatatop!=[]:
                        self.linempp.set_xdata(timepointsmpp)
                        self.linempp.set_ydata(mppdatatop)
                        self.mppdegsubfig.set_ylim([0.8*min(mppdatatop),1.2*max(mppdatatop)])
                        self.mppdegsubfig.set_xlim([min(timepointsmpp),max(timepointsmpp)])
                    
                    try:
                        self.fig.canvas.draw()
                        self.fig.canvas.flush_events()
                        self.fig.savefig(self.Savepath.get()+"\\"+"JVparamTop_"+SampleNametop+"_"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+".png",dpi=300)
                    except:
                        print("exception with draw")
        
                elif whichcell=="Bottom cell":
                    timepointsJVbot+=timepointsJV
                    Vocdatabot+=Vocdatabotint
                    Jscdatabot+=Jscdatabotint
                    FFdatabot+=FFdatabotint
                    Effdatabot+=Effdatabotint
                    #DATAbot+=DATA
                    
                    self.linevocbot.set_xdata(timepointsJVbot)
                    self.linevocbot.set_ydata(Vocdatabot)
                    self.VocsubfigBot.set_ylim([0.8*min(Vocdatabot),1.2*max(Vocdatabot)])
                    self.VocsubfigBot.set_xlim([min(timepointsJVbot),max(timepointsJVbot)])
                                
                    self.linejscbot.set_xdata(timepointsJVbot)
                    self.linejscbot.set_ydata(Jscdatabot)
                    self.JscsubfigBot.set_ylim([0.8*min(Jscdatabot),1.2*max(Jscdatabot)])
                    self.JscsubfigBot.set_xlim([min(timepointsJVbot),max(timepointsJVbot)])
    
                    if mppdatabot!=[]:
                        self.linempp.set_xdata(timepointsmpp)
                        self.linempp.set_ydata(mppdatabot)
                        self.mppdegsubfig.set_ylim([0.8*min(mppdatabot),1.2*max(mppdatabot)])
                        self.mppdegsubfig.set_xlim([min(timepointsmpp),max(timepointsmpp)])
                    try:
                        self.fig.canvas.draw()
                        self.fig.canvas.flush_events()
                        self.fig.savefig(self.Savepath.get()+"\\"+"JVparamBot_"+SampleNamebot+"_"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+".png",dpi=300)
                    except:
                        print("exception with draw")
    
                elif whichcell=="Both cells":
                    
                    timepointsJVtop+=timepointsJV
                    Vocdatatop+=Vocdatatopint
                    Jscdatatop+=Jscdatatopint
                    FFdatatop+=FFdatatopint
                    Effdatatop+=Effdatatopint
                    #DATAtop+=DATA
                    timepointsJVbot+=timepointsJV
                    Vocdatabot+=Vocdatabotint
                    Jscdatabot+=Jscdatabotint
                    FFdatabot+=FFdatabotint
                    Effdatabot+=Effdatabotint
                    #DATAbot+=DATA
                    
                    self.linevoctop.set_xdata(timepointsJVtop)
                    self.linevoctop.set_ydata(Vocdatatop)
                    self.VocsubfigTop.set_ylim([0.8*min(Vocdatatop),1.2*max(Vocdatatop)])
                    self.VocsubfigTop.set_xlim([min(timepointsJVtop),max(timepointsJVtop)])
                    self.linevocbot.set_xdata(timepointsJVbot)
                    self.linevocbot.set_ydata(Vocdatabot)
                    self.VocsubfigBot.set_ylim([0.8*min(Vocdatabot),1.2*max(Vocdatabot)])
                    self.VocsubfigBot.set_xlim([min(timepointsJVbot),max(timepointsJVbot)])
                    self.linejsctop.set_xdata(timepointsJVtop)
                    self.linejsctop.set_ydata(Jscdatatop)
                    self.JscsubfigTop.set_ylim([0.8*min(Jscdatatop),1.2*max(Jscdatatop)])
                    self.JscsubfigTop.set_xlim([min(timepointsJVtop),max(timepointsJVtop)])
                    self.linejscbot.set_xdata(timepointsJVbot)
                    self.linejscbot.set_ydata(Jscdatabot)
                    self.JscsubfigBot.set_ylim([0.8*min(Jscdatabot),1.2*max(Jscdatabot)])
                    self.JscsubfigBot.set_xlim([min(timepointsJVbot),max(timepointsJVbot)])     
                    
                    if mppdatabot!=[] and mppdatatop!=[]:
                        #self.mppdegsubfig.clear()
                        
                        self.linemppbot.set_xdata(timepointsmpp)
                        self.linemppbot.set_ydata(mppdatabot)
                        self.linempptop.set_xdata(timepointsmpp)
                        self.linempptop.set_ydata(mppdatatop)
                        self.mppdegsubfig.set_ylim([0.8*min(mppdatabot+mppdatatop),1.2*max(mppdatabot+mppdatatop)])
                        self.mppdegsubfig.set_xlim([min(timepointsmpp),max(timepointsmpp)])
                        
                    try:
                        self.fig.canvas.draw()
                        self.fig.canvas.flush_events()
                        self.fig.savefig(self.Savepath.get()+"\\"+"JVparamBoth_"+SampleNametop+"_"+SampleNamebot+"_"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+".png",dpi=300)
                    except:
                        print("exception with draw")
            except:
                print("exception in jv scan")
            #k+=1           
        ###################################MPPT###################################################33
            try:
                mppstarttime=time()
                
                if self.VoctrackCheck.get()==0:
                    mpporvoc="mpp"
                else:
                    mpporvoc="voc"
                    
                command=""
                if whichcell=="Top cell":
                    command=mpporvoc+"top="+str(1000*float(self.Vstarttop.get()))+","+str(Vstep)+";"+str(DurationMpp)
                    self.ser.write(command.encode())
                    SampleName=SampleNametop
                elif whichcell=="Bottom cell":
                    command=mpporvoc+"bot="+str(1000*float(self.Vstartbottom.get()))+","+str(Vstep)+";"+str(DurationMpp)
                    self.ser.write(command.encode())
                    SampleName=SampleNamebot
                elif whichcell=="Both cells":
                    command=mpporvoc+"two="+str(1000*float(self.Vstarttop.get()))+":"+str(1000*float(self.Vstartbottom.get()))+","+str(Vstep)+";"+str(DurationMpp)
                    self.ser.write(command.encode())
                
                if whichcell!="Both cells":
                    
                    contenttxtfile=[mpporvoc+"tracking\n",
                                "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_"+SampleName+"\n",
                                "\n","Time\tPower\tVoltage\tCurrent\n"]
                    stop=0
                    start=0
                    #savelist=[0]
                    if whichcell=="Top cell":
                        timepointsmpp=timepointsmpp
                        mppdata=mppdatatop
                        cellarea=self.CellAreadeg.get()
    #                    print("top")
                    elif whichcell=="Bottom cell":
                        timepointsmpp=timepointsmpp
                        mppdata=mppdatabot
                        cellarea=self.CellAreadeg1.get()
    
                    
                    j=0
                    while stop!=1:
                        line=str(self.ser.readline().strip().decode())
                        #print(line)
                        if self.stopdeg==0:
                            self.ser.write("STOP".encode())
                            print("STOPpython")
                            print(str(self.ser.readline().decode()))
                            print(str(self.ser.readline().decode()))
                            print(str(self.ser.readline().decode()))
                            self.ser.flush()
                            break
                        if line=="trackingending":
                            stop=1
                        if stop!=1 and line == "trackingstarting":
                            start=1
                        if stop!=1 and start and line != "trackingstarting" and line!="invalid!" and line!="":
    #                        print(line)
                            try:
                                readtime=float(line.split(",")[3])
                                #print(readtime)
                                timepointsmpp.append((mppstarttime-start_time)+readtime)
                                
                                #print(self.VoctrackCheck.get())
                                
                                if self.VoctrackCheck.get()==0:
                                    mppdata.append(float(line.split(",")[2])/cellarea/1000) #to put power in W/cm2
                                else:
                                    mppdata.append(float(line.split(",")[0])) #voltage
                                    #print("here")
        
                                contenttxtfile.append(str(timepointsmpp[-1])+"\t"+str(float(line.split(",")[2])/cellarea/1000)+"\t"+str(line.split(",")[0])+"\t"+str(float(line.split(",")[1])/cellarea)+"\n")
                                
                                i=int(math.floor(readtime))
                                
                                #update a live plot
                                if len(mppdata)>100:
                                    self.mppdatatoplot=mppdata[-100:-1]
                                    self.timepointsmpptoplot=timepointsmpp[-100:-1]
                                else:
                                    self.mppdatatoplot=mppdata
                                    self.timepointsmpptoplot=timepointsmpp
                                
    
                                self.mppdegsubfig.set_ylim([0.8*min(self.mppdatatoplot),1.2*max(self.mppdatatoplot)])
                                self.mppdegsubfig.set_xlim([min(self.timepointsmpptoplot),max(self.timepointsmpptoplot)])
                                self.linempp.set_xdata(self.timepointsmpptoplot)
                                self.linempp.set_ydata(self.mppdatatoplot)
                                
                                try:
                                    self.fig.canvas.draw()
                                    self.fig.canvas.flush_events()
                                except:
                                    print("exception with draw")
                                    
                                if i//(timetoSave*120) >j:
                                    j=i//(timetoSave*120)
                                    file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_mpp.txt",'w')
                                    file.writelines("%s" % item for item in contenttxtfile)
                                    file.close()
                                    contenttxtfile=["MPPtracking\n",
                                            "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_"+SampleName+"\n",
                                            "\n","Time\tPower\tVoltage\tCurrent\n"]
                            except: 
                                print(line)
                    #self.mpptxtfile1=contenttxtfile
                    file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_mpp.txt",'w')
                    file.writelines("%s" % item for item in contenttxtfile)
                    file.close()
                    
                else:
                    contenttxtfiletop=["MPPtracking topcell\n",
                            "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_top"+SampleNametop+"\n",
                                            "\n","Time\tPower\tVoltage\tCurrent\n"]
                    contenttxtfilebot=["MPPtracking botcell\n",
                            "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_bot"+SampleNamebot+"\n",
                                            "\n","Time\tPower\tVoltage\tCurrent\n"]
                    
                    stop=0
                    start=0
                    #savelist=[0]
                    j=0
                    while stop!=1:
                            line=str(self.ser.readline().strip().decode())
                            #print(line)
                            if self.stopdeg==0:
                                self.ser.write("STOP".encode())
                                print("STOPpython")
                                print(str(self.ser.readline().decode()))
                                print(str(self.ser.readline().decode()))
                                print(str(self.ser.readline().decode()))
                                self.ser.flush()
                                break
                            if line=="trackingending":
                                stop=1
                            if stop!=1 and line == "trackingstarting":
                                start=1
                            if stop!=1 and start and line != "trackingstarting" and line!="invalid!" and line!="":
                                try:
                                    readtime=float(line.split(",")[6])
                                    #timepointsmpp.append(readtime)
                                    timepointsmpp.append((mppstarttime-start_time)+readtime)    
                                    
                                    if self.VoctrackCheck.get()==0:
                                        mppdatabot.append(float(line.split(",")[2])/self.CellAreadeg1.get()/1000) #to put power in W/cm2
                                        mppdatatop.append(float(line.split(",")[5])/self.CellAreadeg.get()/1000) #to put power in W/cm2
                                    else:
                                        mppdatabot.append(float(line.split(",")[0])) #voltage
                                        mppdatatop.append(float(line.split(",")[3])) #voltage
                                    
                                                                
                                    contenttxtfilebot.append(str(timepointsmpp[-1])+"\t"+str(float(line.split(",")[2])/self.CellAreadeg1.get()/1000)+"\t"+str(line.split(",")[0])+"\t"+str(float(line.split(",")[1])/self.CellAreadeg1.get())+"\n")
                                    contenttxtfiletop.append(str(timepointsmpp[-1])+"\t"+str(float(line.split(",")[5])/self.CellAreadeg.get()/1000)+"\t"+str(line.split(",")[3])+"\t"+str(float(line.split(",")[4])/self.CellAreadeg.get())+"\n")
            
                                    i=int(math.floor(readtime))
                                    #update a live plot
                                    if len(mppdatabot)>100:
                                        self.mppdatatoplotbot=mppdatabot[-100:-1]
                                        self.mppdatatoplottop=mppdatatop[-100:-1]
                                        self.timepointsmpptoplot=timepointsmpp[-100:-1]
                                    else:
                                        self.mppdatatoplotbot=mppdatabot
                                        self.mppdatatoplottop=mppdatatop
                                        self.timepointsmpptoplot=timepointsmpp
                                        
                                    datarange=self.mppdatatoplotbot + self.mppdatatoplottop
                                    
                                    self.mppdegsubfig.set_ylim([0.8*min(datarange),1.2*max(datarange)])
                                    self.mppdegsubfig.set_xlim([min(self.timepointsmpptoplot),max(self.timepointsmpptoplot)])
            
                                    #self.mppfig.set_ylim([0.5*min(min(self.mppdatatoplotbot),min(self.mppdatatoplottop)),1.5*max(max(self.mppdatatoplottop),max(self.mppdatatoplotbot))])
                                    #self.mppfig.set_xlim([min(self.timepointsmpptoplot),max(self.timepointsmpptoplot)])
                             
                                    self.linemppbot.set_xdata(self.timepointsmpptoplot)
                                    self.linemppbot.set_ydata(self.mppdatatoplotbot)
                                    self.linempptop.set_xdata(self.timepointsmpptoplot)
                                    self.linempptop.set_ydata(self.mppdatatoplottop)
                                    
                                    try:
                                        self.fig.canvas.draw()
                                        self.fig.canvas.flush_events()
                                    except:
                                        print("exception with draw")
                                    
                                    if i//(timetoSave*120) >j:
                                        j=i//(timetoSave*120)
                                        file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_topmpp.txt",'w')
                                        file.writelines("%s" % item for item in contenttxtfiletop)
                                        file.close()
                                        contenttxtfiletop=["MPPtracking topcell\n",
                                                           "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_top"+SampleNametop+"\n",
                                                           "\n","Time\tPower\tVoltage\tCurrent\n"]
                                        file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_botmpp.txt",'w')
                                        file.writelines("%s" % item for item in contenttxtfilebot)
                                        file.close()
                                        contenttxtfilebot=["MPPtracking botcell\n",
                                                           "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_bot"+SampleNamebot+"\n",
                                                           "\n","Time\tPower\tVoltage\tCurrent\n"]
                                except: 
                                    print(line)
                    #self.mpptxtfile1=contenttxtfilebot
                    #self.mpptxtfile2=contenttxtfiletop
                    file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_topmpp.txt",'w')
                    file.writelines("%s" % item for item in contenttxtfiletop)
                    file.close()
                    file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_botmpp.txt",'w')
                    file.writelines("%s" % item for item in contenttxtfilebot)
                    file.close()
            except:
                print("exception in mpp tracking")
            
        print("Degradation has been ended")
        
        #add here the export all data when user has stopped the programm
        
            
    def MPPT(self):
        #filename = self.Savepath.get()
        self.start_time = time()
        self.timepointsmpp = []
        self.mppdata = []
        self.mppdatatop = []
        self.mppdatabot = []
        self.stopmppt=1
        #self.mpptxtfile1=[]
        #self.mpptxtfile2=[]
        plt.close()
        
        plt.ion()
        
        
        self.Frame5 = Frame(self.superframe, bg="white")
        self.Frame5.grid(row = 3, column = 5, rowspan = 15, columnspan = 95, sticky = W+E+N+S)
        
        self.fig1 = plt.figure(figsize=(15, 5.5))
        self.fig1.patch.set_facecolor('white')
        canvas = FigureCanvasTkAgg(self.fig1, self.Frame5)
        canvas.get_tk_widget().grid(row=0,column=0,rowspan=15,columnspan=95)
        self.mppfig=self.fig1.add_subplot(111)
        self.mppfig.set_xlabel('Time (s)',fontsize=15)
        self.mppfig.set_ylabel('Power (W/cm$^2$)',fontsize=15)
        plt.axes().grid(True)
        plt.axes().grid(True)
        #self.line1, = self.mppfig.plot(self.mppdata,marker='o',markersize=3,linestyle='none',markerfacecolor='red')
        self.line1, = self.mppfig.plot(self.mppdata,marker='o',markersize=2)
        self.line2, = self.mppfig.plot(self.mppdatatop,marker='o',markersize=2, label="Bottom Cell")
        self.line3, = self.mppfig.plot(self.mppdatabot,marker='o',markersize=2, label="Top Cell")

        plt.show(block=False)
        
        command=""
        if self.mppcell.get()=="Top cell":
            command="mpptop="+str(1000*float(self.Vstarttop.get()))+","+str(self.Vstep.get())+";"+str(self.Duration.get())
            self.ser.write(command.encode())
        elif self.mppcell.get()=="Bottom cell":
            command="mppbot="+str(1000*float(self.Vstartbottom.get()))+","+str(self.Vstep.get())+";"+str(self.Duration.get())
            self.ser.write(command.encode())
        elif self.mppcell.get()=="Both cells":
            command="mpptwo="+str(1000*float(self.Vstarttop.get()))+":"+str(1000*float(self.Vstartbottom.get()))+","+str(self.Vstep.get())+";"+str(self.Duration.get())
            self.ser.write(command.encode())
        
        if self.mppcell.get()!="Both cells":
            contenttxtfile=["MPPtracking\n",
                        "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"\n",
                        "\n","Time\tPower\tVoltage\tCurrent\n"]
            stop=0
            start=0
            savelist=[0]
            j=0
            while stop!=1:
                try:
                    line=str(self.ser.readline().strip().decode())
                    #print(line)
                    if self.stopmppt==0:
                        self.ser.write("STOP".encode())
                        print("STOPpython")
                        print(str(self.ser.readline().decode()))
                        print(str(self.ser.readline().decode()))
                        print(str(self.ser.readline().decode()))
                        self.ser.flush()
                        break
                    if line=="trackingending":
                        stop=1
                    if stop!=1 and line == "trackingstarting":
                        start=1
                    if stop!=1 and start and line != "trackingstarting" and line!="invalid!":
                        #print(line)
                        readtime=float(line.split(",")[3])
                        #print(readtime)
                        self.timepointsmpp.append(readtime)
                        self.mppdata.append(float(line.split(",")[2])/self.CellArea.get()/1000) #to put power in W/cm2
                        contenttxtfile.append(str(self.timepointsmpp[-1])+"\t"+str(self.mppdata[-1])+"\t"+str(line.split(",")[0])+"\t"+str(line.split(",")[1])+"\n")
                        
                        i=int(math.floor(readtime))
                        
                        #update a live plot
                        
                        if len(self.mppdata)>100:
                            self.mppdatatoplot=self.mppdata[-100:-1]
                            self.timepointsmpptoplot=self.timepointsmpp[-100:-1]
                        else:
                            self.mppdatatoplot=self.mppdata
                            self.timepointsmpptoplot=self.timepointsmpp
                        
                        self.mppfig.set_ylim([0.5*min(self.mppdatatoplot),1.5*max(self.mppdatatoplot)])
                        self.mppfig.set_xlim([min(self.timepointsmpptoplot),max(self.timepointsmpptoplot)])
                        self.line1.set_xdata(self.timepointsmpptoplot)
                        self.line1.set_ydata(self.mppdatatoplot)
                        
                        self.fig1.canvas.draw()
                        self.fig1.canvas.flush_events()
                        
                        if i//120 >j:
                            j=i//120
                            file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_mpp.txt",'w')
                            file.writelines("%s" % item for item in contenttxtfile)
                            file.close()
                            contenttxtfile=["MPPtracking\n",
                                        "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"\n",
                                        "\n","Time\tPower\tVoltage\tCurrent\n"]
                    


                            
                except: pass
            #self.mpptxtfile1=contenttxtfile
            file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_mpp.txt",'w')
            file.writelines("%s" % item for item in contenttxtfile)
            file.close()
            
        else:
            contenttxtfiletop=["MPPtracking topcell\n",
                    "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"\n",
                    "\n","Time\tPower\tVoltage\tCurrent\n"]
            contenttxtfilebot=["MPPtracking topcell\n",
                    "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"\n",
                    "\n","Time\tPower\tVoltage\tCurrent\n"]
            
            stop=0
            start=0
            #savelist=[0]
            j=0
            while stop!=1:
                try:
                    line=str(self.ser.readline().strip().decode())
                    print(line)
                    if self.stopmppt==0:
                        self.ser.write("STOP".encode())
                        print("STOPpython")
                        print(str(self.ser.readline().decode()))
                        print(str(self.ser.readline().decode()))
                        print(str(self.ser.readline().decode()))
                        self.ser.flush()
                        break
                    if line=="trackingending":
                        stop=1
                    if stop!=1 and line == "trackingstarting":
                        start=1
                    if stop!=1 and start and line != "trackingstarting" and line!="invalid!":
                        
                        readtime=float(line.split(",")[6])
                        self.timepointsmpp.append(readtime)
                                                
                        self.mppdatabot.append(float(line.split(",")[2])/self.CellArea.get()/1000) #to put power in W/cm2
                        self.mppdatatop.append(float(line.split(",")[5])/self.CellArea.get()/1000) #to put power in W/cm2
                        
                        contenttxtfilebot.append(str(self.timepointsmpp[-1])+"\t"+str(self.mppdatabot[-1])+"\t"+str(line.split(",")[0])+"\t"+str(line.split(",")[1])+"\n")
                        contenttxtfiletop.append(str(self.timepointsmpp[-1])+"\t"+str(self.mppdatatop[-1])+"\t"+str(line.split(",")[3])+"\t"+str(line.split(",")[4])+"\n")

                        i=int(math.floor(readtime))
                        #update a live plot
                        if len(self.mppdatabot)>100:
                            self.mppdatatoplotbot=self.mppdatabot[-100:-1]
                            self.mppdatatoplottop=self.mppdatatop[-100:-1]
                            self.timepointsmpptoplot=self.timepointsmpp[-100:-1]
                        else:
                            self.mppdatatoplotbot=self.mppdatabot
                            self.mppdatatoplottop=self.mppdatatop
                            self.timepointsmpptoplot=self.timepointsmpp
                            
                        datarange=self.mppdatatoplotbot + self.mppdatatoplottop
                        
                        self.mppfig.set_ylim([0.5*min(datarange),1.5*max(datarange)])
                        self.mppfig.set_xlim([min(self.timepointsmpptoplot),max(self.timepointsmpptoplot)])

                        #self.mppfig.set_ylim([0.5*min(min(self.mppdatatoplotbot),min(self.mppdatatoplottop)),1.5*max(max(self.mppdatatoplottop),max(self.mppdatatoplotbot))])
                        #self.mppfig.set_xlim([min(self.timepointsmpptoplot),max(self.timepointsmpptoplot)])
                 
                        self.line2.set_xdata(self.timepointsmpptoplot)
                        self.line2.set_ydata(self.mppdatatoplotbot)
                        self.line3.set_xdata(self.timepointsmpptoplot)
                        self.line3.set_ydata(self.mppdatatoplottop)
                        
                        self.mppfig.legend()
                        
                        self.fig1.canvas.draw()
                        self.fig1.canvas.flush_events()
                        
                        if i//60 >j:
                            j=i//60
                            file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_topmpp.txt",'w')
                            file.writelines("%s" % item for item in contenttxtfiletop)
                            file.close()
                            contenttxtfiletop=["MPPtracking topcell\n",
                                            "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"\n",
                                            "\n","Time\tPower\tVoltage\tCurrent\n"]
                            file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_botmpp.txt",'w')
                            file.writelines("%s" % item for item in contenttxtfilebot)
                            file.close()
                            contenttxtfilebot=["MPPtracking topcell\n",
                                            "Sample name:\t"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"\n",
                                            "\n","Time\tPower\tVoltage\tCurrent\n"]
 
                except: pass
            #self.mpptxtfile1=contenttxtfilebot
            #self.mpptxtfile2=contenttxtfiletop
            file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_topmpp.txt",'w')
            file.writelines("%s" % item for item in contenttxtfiletop)
            file.close()
            file = open(self.Savepath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_botmpp.txt",'w')
            file.writelines("%s" % item for item in contenttxtfilebot)
            file.close()
    
                
    def ConnectArduino(self):
        if self.connectlabel.get()=="":
            i=5
            connected=1
            while i:
                arduino_ports = [
                    p.device
                    for p in serial.tools.list_ports.comports()
                    if 'Arduino' in p.description
                ]
                
                if not arduino_ports:
                    print("No Arduino found")
                    break
                    connected=0
                elif len(arduino_ports) > 1:
                    print('Multiple Arduinos found - using the first')
                    break
                    connected=0
                else:
                    self.ser = serial.Serial(str(arduino_ports[0]),115200, timeout=.1)
                    sleep(2)
                    print("startsendingtoarduino")
                    self.IVsweepatconnect()
                    print("Arduino is connected on ",arduino_ports[0])
                    self.ser.write('L'.encode())
                    self.connectlabel.set("Connected")
                    self.Frame3.configure(bg="forestgreen")
                    self.conlabel.config(font=("Courier", 15),fg='black',background='forestgreen')
                    break
                    connected=1

            if connected==0:
                print("Connection failed after 5 attempts on all ports")
                    
        elif self.connectlabel.get()=="Connected":
            print("the arduino is already connected")

            
    def IVsweepatconnect(self):
        global minx, maxx, miny, maxy
        
        command="sweeptop"
        
        command+="="+str(1000*(-0.1))+":"+str(1000+0.1)+";"+str(1)+","+str(0.2)
        
        #print(command)
        self.ser.write(command.encode())
        stop=0
        start=0
        while stop!=1:
            line=str(self.ser.readline().strip().decode())
            print(line)
            if line=="sweepending":
                stop=1
            if stop!=1 and line == "sweepstarting":
                start=1
            if stop!=1 and start and line != "sweepstarting":
                print(line)
                
        command="sweepbot"
        command+="="+str(1000*(-0.1))+":"+str(1000*0.1)+";"+str(1)+","+str(0.2)
            
        self.ser.write(command.encode())
        stop=0
        start=0
        while stop!=1:
            line=str(self.ser.readline().strip().decode())
            print(line)
            if line=="sweepending":
                stop=1
            if stop!=1 and line == "sweepstarting":
                start=1
            if stop!=1 and start and line != "sweepstarting":
                print(line)
    
    def IVsweepDyn(self):
        global minx, maxx, miny, maxy
        timestart=time()
        command=""
        if self.jvcell.get()=="Top cell":
            command+="sweeptop"
        else:
            command+="sweepbot"
        
        command+="="+str(1000*float(self.VstartJV.get()))+":"+str(1000.0*float(self.VendJV.get()))+";"+str(self.NbPtsJV.get())+","+str(self.DelayJV.get())
        
        print(command)
        
        self.ser.write(command.encode())
        x=[]
        y=[]
        stop=0
        start=0
        plt.ion()
        self.line,=self.IVsubfig.plot(x,y,marker='o',markersize=2)
        
        while stop!=1:
            line=str(self.ser.readline().strip().decode())
            #print(line)
            if line=="sweepending":
                stop=1
            if stop!=1 and line == "sweepstarting":
                start=1
            if stop!=1 and start and line != "sweepstarting":
                x.append(float(line.split(",")[0])/1000) #to volt
                y.append(float(line.split(",")[1])/self.CellArea.get()) #mA/cm2
                self.line.set_xdata(x)
                self.line.set_ydata(y)
                if min(x)<minx:
                    minx=min(x)
                if max(x)>maxx:
                    maxx=max(x)
                if 1.2*min(y)<miny:
                    miny=1.2*min(y)
                if max(y)>maxy:
                    maxy=max(y)
                self.IVsubfig.axis([minx,maxx,miny,maxy])
                
                try:
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                except:
                    print("exception with draw")
                
        power = [x[i]*y[i] for i in range(len(x))]
        if self.curvename.get()!="":
            self.IVsubfig.plot(x,y,label=self.curvename.get())
            if self.PowerCheck.get():
                self.IVsubfig.plot(x,power,label=self.curvename.get()+"_power")
        else:
            self.IVsubfig.plot(x,y,label=self.jvcell.get())
            if self.PowerCheck.get():
                self.IVsubfig.plot(x,power,label=self.jvcell.get()+"_power")
        self.leg=self.IVsubfig.legend(loc=0)
        
        if min(x)<minx:
            minx=min(x)
        if max(x)>maxx:
            maxx=max(x)
        if 1.2*min(y)<miny:
            miny=1.2*min(y)
        if max(y)>maxy:
            maxy=max(y)
        #print(x)
        #print(y)
        self.IVsubfig.axis([minx,maxx,miny,maxy])
        plt.gcf().canvas.draw()
        
        datainterm={}
        datainterm["x"]=x
        datainterm["y"]=y
        datainterm["CellSurface"]=self.CellArea.get()
        #calculate JV parameters
        
        testfind=0
        datainterm["Jsc"]=0
        for i in range(len(x)-1):
            if np.sign(x[i+1])!=np.sign(x[i]):
                #datainterm["Jsc"]=-(y[i]-x[i]*(y[i]-y[i+1])/(x[i]-x[i+1]))
                testfind=1
                xregress=[x[i+2],x[i+1],x[i],x[i-1]]
                yregress=[y[i+2],y[i+1],y[i],y[i-1]]
                slope, intercept, r_value, p_value, std_err = stats.linregress(xregress,yregress)
                #print(datainterm["Jsc"])
                #print(-intercept/datainterm["CellSurface"])
                datainterm["Jsc"]=-intercept #/datainterm["CellSurface"]
                break
            else:
                datainterm["Jsc"]=0
        if testfind==0:
            print("could not find Jsc")
        #datainterm["Voc"]=fsolve(spl,0.7)[0]*1000
        testfind=0
        for i in range(len(y)-1):
            if np.sign(y[i+1])!=np.sign(y[i]):
                #datainterm["Voc"]=(x[i]-y[i]*(x[i]-x[i+1])/(y[i]-y[i+1]))
                testfind=1
                xregress=[x[i+2], x[i+1],x[i],x[i-1],x[i-2]]
                yregress=[y[i+2], y[i+1],y[i],y[i-1], y[i-2]]
                slope, intercept, r_value, p_value, std_err = stats.linregress(xregress,yregress)
                datainterm["Voc"]=-1000*intercept/slope
                break
            else:
                datainterm["Voc"]=0
        if testfind==0:
            print("could not find Voc")                 
        
        a=list(zip(*sorted(zip(x, y))))#need to verify that x is increasing order!
        x=list(a[0])
        y=list(a[1])
        
#        if x[0]>x[1]:
#            x=x[::-1]
#            y=y[::-1]
        spl = UnivariateSpline(x, y, s=0)
        power = [x[i]*y[i] for i in range(len(x))]
        powerspl=UnivariateSpline(x, power, s=0)
        powersplder=powerspl.derivative(n=1)
        powersplderdiscret=[powersplder(xi) for xi in x]
        for i in range(len(powersplderdiscret)-1):
            if np.sign(powersplderdiscret[i+1])!=np.sign(powersplderdiscret[i]):
                xregress=[x[i+2], x[i+1],x[i],x[i-1]]
                yregress=[powersplderdiscret[i+2], powersplderdiscret[i+1], powersplderdiscret[i], powersplderdiscret[i-1]]
                slope, intercept, r_value, p_value, std_err = stats.linregress(xregress,yregress)
                datainterm["Vmpp"]=-1000*intercept/slope 
                #print(datainterm["Vmpp"])
                datainterm["Jmpp"]=abs(spl(datainterm["Vmpp"]/1000))
                #print(datainterm["Jmpp"])
                datainterm["FF"]=datainterm["Jmpp"]*datainterm["Vmpp"]/(datainterm["Voc"]*datainterm["Jsc"])
                datainterm["Eff"]=abs(datainterm["Jsc"]*datainterm["Voc"]*datainterm["FF"]/1000)
                break

        if math.isnan(datainterm["Vmpp"]):
            datainterm["Vmpp"]=0
        if math.isnan(datainterm["Jmpp"]):
            datainterm["Jmpp"]=0
        if math.isnan(datainterm["FF"]):
            datainterm["FF"]=0 
            datainterm["Eff"]=0
                      
        if self.curvename.get()!="":
            datainterm["SampleName"]=self.curvename.get()
        else:
            datainterm["SampleName"]=self.jvcell.get()

        if self.VstartJV.get()<self.VendJV.get():
            datainterm["ScanDirection"]="Forward"
        else:
            datainterm["ScanDirection"]="Reverse"
        DATA.append(datainterm)
        
        timeend=time()
        elapsed=timeend-timestart
        
        contenttxtfile=["Sample name:\t"+datainterm["SampleName"]+"\n",
                "Time&Date:\t"+str(datetime.now().strftime('%Y.%m.%d-%H.%M.%S'))+"\n",
                "Vstart=\t"+str(1000*self.VstartJV.get())+"\n",
                "Vend=\t"+str(1000*self.VendJV.get())+"\n",
                "Nb of points=\t"+str(self.NbPtsJV.get())+"\n",
                "Total scan fct time (s)=\t"+'%.2f' % float(elapsed)+"\n\n",
                "Voc=\t"+str(datainterm["Voc"])+"\n","Jsc=\t"+str(datainterm["Jsc"])+"\n","FF=\t"+str(datainterm["FF"])+"\n","Eff.=\t"+str(datainterm["Eff"])+"\n",
                "Vmpp=\t"+str(datainterm["Vmpp"])+"\n","Jmpp=\t"+str(datainterm["Jmpp"])+"\n","\n\n","DATA:\n"]
        for item in range(len(x)):
            contenttxtfile.append(str(x[item])+"\t"+str(y[item])+"\n")

        #file = open("C:\Users\jwerner\switchdrive\arduino\sourcuino\BackupRawDATA\\"+datetime.now().strftime('%Y%m%d-%Hh%M-%S')+"_"+datainterm["SampleName"]+".txt",'w')
        
        file = open(self.SaveJVpath.get()+"\\"+datetime.now().strftime('%Y.%m.%d-%H.%M.%S')+"_"+datainterm["SampleName"]+".txt",'w')

        file.writelines("%s" % item for item in contenttxtfile)
        file.close()
        
        if self.FrameChoice.get()=="JV scan":
            self.TableBuilder(self.Frame6)
            
            
    
        
    def ClearGraph(self):
        global DATA, minx, maxx, miny, maxy
        
        self.IVsubfig.clear()
        self.IVsubfig.set_xlabel('Voltage (V)',fontsize=15)
        self.IVsubfig.set_ylabel('Current density (mA/cm$^2$)',fontsize=15)
        self.IVsubfig.axhline(y=0, color='k')
        self.IVsubfig.axvline(x=0, color='k')
        self.IVsubfig.tick_params(labelsize=15)
        plt.gcf().canvas.draw()
        
        DATA=[]
        minx=0
        maxx=0.5
        miny=-5
        maxy=5
        self.TableBuilder(self.Frame6)
                
    def ClearMPPGraph(self):
        global DATA, minx, maxx, miny, maxy
        
        self.mppfig.clear()
        self.mppfig.set_xlabel('Time (s)',fontsize=15)
        self.mppfig.set_ylabel('Power (W/m$^2$)',fontsize=15)
        plt.axes().grid(True)
        plt.axes().grid(True)
        plt.gcf().canvas.draw()
        
        DATA=[]
        minx=0
        maxx=1
        miny=0
        maxy=1
    
    def ClearDegGraph(self):
        global DATA, minx, maxx, miny, maxy
        
        self.mppdegsubfig.clear()
        self.mppdegsubfig.set_xlabel('Time (s)',fontsize=8)
        self.mppdegsubfig.set_ylabel('Power (mW/cm$^2$)',fontsize=8)
        
        self.IVdegsubfig.clear()
        self.IVdegsubfig.set_xlabel('Voltage (V)',fontsize=8)
        self.IVdegsubfig.set_ylabel('Current density (mA/cm$^2$)',fontsize=8)
        
        self.VocsubfigTop.clear()
        self.VocsubfigTop.set_xlabel("Time (s)",fontsize=8)
        self.VocsubfigTop.set_ylabel("Voc topcell (V)",fontsize=8)
        
        self.JscsubfigTop.clear()
        self.JscsubfigTop.set_xlabel("Time (s)",fontsize=8)
        self.JscsubfigTop.set_ylabel("Jsc topcell (mA/cm$^2$)",fontsize=8)
        
        self.VocsubfigBot.clear()
        self.VocsubfigBot.set_xlabel("Time (s)",fontsize=8)
        self.VocsubfigBot.set_ylabel("Voc botcell (V)",fontsize=8)
        
        self.JscsubfigBot.clear()
        self.JscsubfigBot.set_xlabel("Time (s)",fontsize=8)
        self.JscsubfigBot.set_ylabel("Jsc botcell (mA/cm$^2$)",fontsize=8)
        
        
        self.FrameTypeChoice(1)
        
        
        
             
    def ExportGraph(self):
        if self.FrameChoice.get()=="JV scan":
            try:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.IVsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                #self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.3, 1.3),bbox_extra_artists=(self.leg,), transparent=True)
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.3, 1.3), transparent=True)
            except:
                print("there is an exception...check legend maybe...")

        elif self.FrameChoice.get()=="MPPT":
            try:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                self.fig1.savefig(f, dpi=300, transparent=True)
            except:
                print("there is an exception...check legend maybe...")

        elif self.FrameChoice.get()=="Degradation":
            try:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                self.fig.savefig(f, dpi=300, transparent=True)
            except:
                print("there is an exception...check legend maybe...")

    def ExportMPPTdat(self):
        if self.mppcell.get()!="Both cells":
            try:
                f = filedialog.asksaveasfilename()
                file = open(f +".txt",'w')
                file.writelines("%s" % item for item in self.mpptxtfile1)
                file.close()
            except:
                print("there is an exception...")
        else:
            #try:
                f = filedialog.asksaveasfilename()
                print(f)
                file = open(f +"_bot.txt",'w')
                file.writelines("%s" % item for item in self.mpptxtfile1)
                file.close()
                file = open(f +"_top.txt",'w')
                file.writelines("%s" % item for item in self.mpptxtfile2)
                file.close()
            #except:
             #   print("there is an exception...")
        

            
    class TableBuilder(tk.Frame):
        def __init__(self, parent):
            tk.Frame.__init__(self, parent)
            self.parent=parent
            self.initialize_user_interface()
    
        def initialize_user_interface(self):
            global DATA
            testdata=[]
            self.parent.grid_rowconfigure(0,weight=1)
            self.parent.grid_columnconfigure(0,weight=1)
            
            for r in range(15):
                self.parent.rowconfigure(r, weight=1)    
            for c in range(45):
                self.parent.columnconfigure(c, weight=1)
            #self.parent.config(background="white")

            for item in range(len(DATA)):
                testdata.append([DATA[item]["SampleName"],DATA[item]["ScanDirection"],float('%.2f' % float(DATA[item]["Jsc"])),float('%.2f' % float(DATA[item]["Voc"])),float('%.2f' % float(DATA[item]["FF"])),float('%.2f' % float(DATA[item]["Eff"])),float('%.2f' % float(DATA[item]["Vmpp"])),float('%.2f' % float(DATA[item]["Jmpp"]))])
           
            self.tableheaders=('Sample','Scan direct.','Jsc','Voc','FF','Eff.','Vmpp','Jmpp')
                        
            # Set the treeview
            self.tree = Treeview( self.parent, columns=self.tableheaders, show="headings")
            
            for col in self.tableheaders:
                self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
                #self.tree.column(col,stretch=tk.YES)
                self.tree.column(col, width=int(round(1*tkFont.Font().measure(col.title()))), anchor='n')   
            
            vsb = Scrollbar(orient="vertical", command=self.tree.yview)
            #hsb = Scrollbar(orient="horizontal",command=self.tree.xview)
            self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=())
            self.tree.grid(row=5,column=0, columnspan=45,rowspan=3, sticky='nsew', in_=self.parent)
            #vsb.grid(column=11, row=1,rowspan=10, sticky='ns', in_=self.parent)
            #hsb.grid(column=0, row=11, sticky='ew', in_=self.parent)
            self.treeview = self.tree
            
            self.insert_data(testdata)

        def insert_data(self, testdata):
            for item in testdata:
                self.treeview.insert('', 'end', values=item)
                
        def sortby(self, tree, col, descending):
            data = [(tree.set(child, col), child) for child in tree.get_children('')]
            try:
                data.sort(key=lambda t: float(t[0]), reverse=descending)
            except ValueError:
                data.sort(reverse=descending)
            for ix, item in enumerate(data):
                tree.move(item[1], '', ix)
            # switch the heading so it will sort in the opposite direction
            tree.heading(col,text=col.capitalize(), command=lambda _col_=col: self.sortby(tree, _col_, int(not descending)))
                
            
            
        
if __name__ == '__main__':
    root = Tk()
    
    
    background_image=ImageTk.PhotoImage(file="csem1.png")
    #background_image=ImageTk.PhotoImage(file="csem1.png")

    background_label = tk.Label(root, image=background_image)
    background_label.grid(row=0,column=0,columnspan=5, rowspan=3)
    background_image2=ImageTk.PhotoImage(file="pvlab.png")
    background_label2 = tk.Label(root, image=background_image2)
    background_label2.grid(row=0,column=90,columnspan=10, rowspan=3)

    root.config(background="white")
    
    app = Sourcuino(master=root)
    root.geometry("1630x940")
    root.resizable(width=True, height=True)
    center(root)
    app.mainloop()
