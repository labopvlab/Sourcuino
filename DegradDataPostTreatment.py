#! python3

import os


from tkinter import Button, Label, Frame, Entry, Checkbutton, IntVar, Toplevel, Scrollbar, Canvas, OptionMenu, StringVar

from tkinter import filedialog
from pathlib import Path
from operator import itemgetter

from datetime import datetime

"""todolist:
- stitching function: append data files and get the time continuing

"""


#assume all data is for the same sample that we know
#also assume we load only text files, either mpp or jv


#can have 1 or 2 or n different cells in the folder: automatize for n
#



#load all in dictionary: samplename, starttime indicated in the file, time saving indicated on the file name, data (normalize the time to )
#clasify by samplename
#clasify by starttime, ascending (individually for each samplename)
#extract data and put to one file, check if time gaps by comparing startime and saving time, in case add the time. 

#average on 5 or 10 points

def DegradDatatreatment():
    txtfileJVparam=["Samplename\tdate\tHours\tVoc\tJsc\tFF\tEff\tVmpp\tJmpp\n"]
    timeJVcurve=[]
    #JVcurrentList=[]
    #JVvoltageList=[]
    VocList=[]
    JscList=[]
    FFList=[]
    EffList=[]
    VmppList=[]
    JmppList=[]
    
    firstfile=1
    
    DATAinitialTOP=[]
    DATAinitialBOT=[]
    DATAinitial=[]
    
    #file_pathnew=[]
    file_path =filedialog.askopenfilenames(title="Please select the mpp files")
    directory = str(Path(file_path[0]).parent.parent)+'\\resultFilesDegrad'
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chdir(directory)
    else :
        os.chdir(directory)
    
    
                            
    for i in range(len(file_path)):
        
        #print(os.path.split(file_path[i])[-1])
        #print(os.path.split(file_path[i])[-1][-4:])
        print(i)
        
        if os.path.split(file_path[i])[-1][-4:] != ".png":
        
            name=os.path.split(file_path[i])[-1][:-4]
            #print(name)
            
            
            
            if name[-7:]=="_topmpp" or name[-7:]=="_botmpp" or name[-4:]=="_mpp":
                filetoread = open(file_path[i],"r")
                filerawdata = filetoread.readlines()
                
                partdat=[]
                mpptime=[]
                mpppower=[]
                mppvoltage=[]
                mppcurrent=[]
                
                thestring=filerawdata[1].split("\t")[1]
                partdat.append(thestring[thestring.find("_")+4:-1])#samplename
                #print(partdat[0])
                
                partdat.append(datetime.strptime(filerawdata[1].split("\t")[1].split("_")[0], '%Y.%m.%d-%H.%M.%S'))
                #print(partdat[1])#time in the file, when the tracking starts
                
                partdat.append(datetime.strptime(os.path.split(file_path[i])[-1].split("_")[0], '%Y.%m.%d-%H.%M.%S'))
                #print(partdat[2])#time of the file name, when the file is saved
                
                for j in range(4,len(filerawdata)):
                    try:
                        mpptime.append(float(filerawdata[j].split("\t")[0]))
                    except:
                        mpptime.append(9999)
                    try:
                        mpppower.append(float(filerawdata[j].split("\t")[1]))
                    except:
                        mpppower.append(999)
                    try:
                        mppvoltage.append(float(filerawdata[j].split("\t")[2]))
                    except:
                        mppvoltage.append(999)
                    try:
                        mppcurrent.append(float(filerawdata[j].split("\t")[3]))
                    except:
                        mppcurrent.append(999)
                        
                partdat.append(mpptime[0])#[3]
                partdat.append([i-mpptime[0] for i in mpptime])#[4]
                partdat.append(mpppower)#[5]
                partdat.append(mppvoltage)#[6]
                partdat.append(mppcurrent)#[7]
                
                if name[-7:]=="_topmpp":
                    DATAinitialTOP.append(tuple(partdat))
                elif name[-7:]=="_botmpp":
                    DATAinitialBOT.append(tuple(partdat))
                elif name[-4:]=="_mpp":
                    DATAinitial.append(tuple(partdat))
            
            else:
                #print("JV")
                filetoread = open(file_path[i],"r")
                filerawdata = filetoread.readlines()
                
                if firstfile:
                    initialDateTime=datetime.strptime(filerawdata[0].split("\t")[1].split("_")[0], '%Y.%m.%d-%H.%M.%S')
                    filetime=initialDateTime
                    firstfile=0
                    elapsedHours=0
                else:
                    filetime=datetime.strptime(filerawdata[0].split("\t")[1].split("_")[0], '%Y.%m.%d-%H.%M.%S')
                    elapsedtime=filetime-initialDateTime
                            
                    elapsedHours=elapsedtime.total_seconds()/3600
                    
                timeJVcurve.append(elapsedHours)
                VocList.append(float(filerawdata[6].split("\t")[1]))
                JscList.append(float(filerawdata[7].split("\t")[1]))
                FFList.append(float(filerawdata[8].split("\t")[1]))
                EffList.append(float(filerawdata[9].split("\t")[1]))
                VmppList.append(float(filerawdata[10].split("\t")[1]))
                JmppList.append(float(filerawdata[11].split("\t")[1]))
                
                thestring=filerawdata[0].split("\t")[1]
                name=thestring[thestring.find("_")+1:-1]#samplename
    
                txtfileJVparam.append(name+"\t"+str(filetime)+"\t"+str(elapsedHours)+"\t"+
                                      str(VocList[-1])+"\t"+str(JscList[-1])+"\t"+str(FFList[-1])+"\t"+str(EffList[-1])+"\t"+str(VmppList[-1])+"\t"+str(JmppList[-1])+"\n")
    
    if len(txtfileJVparam)>1:
        file = open('JVparam.txt','w')
        file.writelines("%s" % item for item in txtfileJVparam)
        file.close()
    
           
    if DATAinitialTOP!=[]:
        DATAinitialTOP=sorted(DATAinitialTOP,key=itemgetter(1))
        DATAtop=[]
        initialtime=DATAinitialTOP[0][3]
        bigspace=0
        mpptime=[i+initialtime for i in DATAinitialTOP[0][4]]
        mpppower=DATAinitialTOP[0][5]
        mppvoltage=DATAinitialTOP[0][6]
        mppcurrent=DATAinitialTOP[0][7]
        
        for i in range(1,len(DATAinitialTOP)):
            if (DATAinitialTOP[i][1]-DATAinitialTOP[i-1][2]).seconds>50 and DATAinitialTOP[i][3]<50:
                #print("largespace")
                #print((DATAinitialTOP[i][1]-DATAinitialTOP[i-1][2]).seconds)
                timetoaddfromprevious2=(DATAinitialTOP[i][1]-DATAinitialTOP[i-1][2]).seconds-DATAinitialTOP[i][3]+mpptime[-1]
                bigspace=1
            if bigspace==0:
                timetoaddfromprevious=DATAinitialTOP[i][3] #need to keep using the actual first time used in the file because loses 1.9s after JV scan compared to file dates
            else:
                timetoaddfromprevious=DATAinitialTOP[i][3]+timetoaddfromprevious2
            #print(timetoaddfromprevious)
            mpptime+=[j+timetoaddfromprevious for j in DATAinitialTOP[i][4]]
            #print(mpptime[-1])
            mpppower+=DATAinitialTOP[i][5]
            mppvoltage+=DATAinitialTOP[i][6]
            mppcurrent+=DATAinitialTOP[i][7]
            
        txtfile=[]        
        
        for i in range(0, len(mpptime),10):#take only 1/10 data point
            txtfile.append(str(mpptime[i]/3600)+'\t'+str(mpppower[i])+'\t'+str(mppvoltage[i])+'\t'+str(mppcurrent[i])+'\n')    
        
        file = open(DATAinitialTOP[0][0]+'_topcell_mpp.txt','w')
        file.writelines("%s" % item for item in txtfile)
        file.close()
        
    if DATAinitialBOT!=[]:
        DATAinitialBOT=sorted(DATAinitialBOT,key=itemgetter(1))
        DATAbot=[]
        initialtime=DATAinitialBOT[0][3]
        bigspace=0
        mpptime=[i+initialtime for i in DATAinitialBOT[0][4]]
        mpppower=DATAinitialBOT[0][5]
        mppvoltage=DATAinitialBOT[0][6]
        mppcurrent=DATAinitialBOT[0][7]
        
        for i in range(1,len(DATAinitialBOT)):
            if (DATAinitialBOT[i][1]-DATAinitialBOT[i-1][2]).seconds>50 and DATAinitialBOT[i][3]<50:
                timetoaddfromprevious2=(DATAinitialBOT[i][1]-DATAinitialBOT[i-1][2]).seconds-DATAinitialBOT[i][3]+mpptime[-1]
                bigspace=1
            if bigspace==0:
                timetoaddfromprevious=DATAinitialBOT[i][3] #need to keep using the actual first time used in the file because loses 1.9s after JV scan compared to file dates
            else:
                timetoaddfromprevious=DATAinitialBOT[i][3]+timetoaddfromprevious2
            mpptime+=[j+timetoaddfromprevious for j in DATAinitialBOT[i][4]]
            mpppower+=DATAinitialBOT[i][5]
            mppvoltage+=DATAinitialBOT[i][6]
            mppcurrent+=DATAinitialBOT[i][7]
        
        txtfile=[]        
        
        for i in range(0, len(mpptime),10):#take only 1/10 data point
            txtfile.append(str(mpptime[i]/3600)+'\t'+str(mpppower[i])+'\t'+str(mppvoltage[i])+'\t'+str(mppcurrent[i])+'\n')    
        
        file = open(DATAinitialBOT[0][0]+'_botcell_mpp.txt','w')
        file.writelines("%s" % item for item in txtfile)
        file.close()
        
    if DATAinitial!=[]:
        DATAinitial=sorted(DATAinitial,key=itemgetter(1))
        DATA=[]
        initialtime=DATAinitial[0][3]
        
        mpptime=[i+initialtime for i in DATAinitial[0][4]]
        mpppower=DATAinitial[0][5]
        mppvoltage=DATAinitial[0][6]
        mppcurrent=DATAinitial[0][7]
        
        for i in range(1,len(DATAinitial)):
            if (DATAinitial[i][1]-DATAinitial[i-1][2]).seconds>50 and DATAinitial[i][3]<50:
                timetoaddfromprevious=(DATAinitial[i][1]-DATAinitial[i-1][2]).seconds-DATAinitial[i][3]+mpptime[-1]
            else:
                timetoaddfromprevious=DATAinitial[i][3] #need to keep using the actual first time used in the file because loses 1.9s after JV scan compared to file dates
            #print(timetoaddfromprevious)
            mpptime+=[j+timetoaddfromprevious for j in DATAinitial[i][4]]
            mpppower+=DATAinitial[i][5]
            mppvoltage+=DATAinitial[i][6]
            mppcurrent+=DATAinitial[i][7]
        
        txtfile=[]        
        
        for i in range(0, len(mpptime),10):#take only 1/10 data point
            txtfile.append(str(mpptime[i])+'\t'+str(mpppower[i])+'\t'+str(mppvoltage[i])+'\t'+str(mppcurrent[i])+'\n')    
        
        file = open('cell_mpp.txt','w')
        file.writelines("%s" % item for item in txtfile)
        file.close()
    
    
