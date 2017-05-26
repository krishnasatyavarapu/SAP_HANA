"""
Implement a GUI for viewing and updating class instances stored in a shelve;
the shelve lives on the machine this script runs on, as 1 or more local files;
"""
import os
os.environ["PYRO_LOGFILE"] = "pyro.log"
os.environ["PYRO_LOGLEVEL"] = "DEBUG"
from tkinter import *
from tkinter import Radiobutton
from tkinter import Canvas
from tkinter import PhotoImage
from tkinter.messagebox import showerror
import shelve
import time
import json
from ttk import *
from purestorage.restclient.purestorage.purestorage import FlashArray
from pyhdb.connection import *
import time
import os
import subprocess
#import Pyro4.core
#import dbapi

def modesel():
    print ( "Inside Mode" + str(mode.get()))
    msgText.delete('1.0', END)
    if mode.get() == 2 :
      modeText = "Alpha version: Classical is not Supported...Only HANA"
      msgText.insert (END, modeText )

def saveconfig():
    msgText.delete('1.0', END)
    modeText = "Complete Configuration Saved."
    msgText.insert (END, modeText )
      
def operation():
    print ( "Inside Operation "+ str(ops.get()))
    msgText.delete('1.0', END)
    if ops.get() != 1 :
      operationText = "Alpha version: Only Backup of SAP HANA system is supported"
      msgText.insert (END, operationText )
      sidMenuTarget.configure(state="normal")
    else :
      operationText = "Select source SID only"
      msgText.insert (END, operationText )
      sidMenuTarget.configure(state="disabled")

      
def check():
 
    con = Connection ('XX.XX.XX.XXX',30015,'SYSTEM','XXXXXXX')
    Connection.connect(con)
    print ( str(con) )
    runlogText = "\n Check: Connected to SAP HANA " + str(con)
    msgText.insert (END, runlogText )
    
    con.close()
    arrayM50 = FlashArray("XX.XX.XX.XXX", "pureuser", "pureuser")
    array_info = arrayM50.get()
    print ("FlashArray {} (version {}) REST session established!".format(array_info['array_name'], array_info['version']))
    runlogText = "\n Check: Connected to FlashArray//m " + "FlashArray {} (version {}) REST session established!".format(array_info['array_name'], array_info['version'])
    msgText.insert (END, runlogText )
def config():
    note.tab(0, state="normal")
    note.tab(1, state="normal")
    note.tab(2, state="normal")
    msgText.delete('1.0', END)
    operationText = "Now the configuration can be edited"
    msgText.insert (END, operationText )
    window.update_idletasks()
    window.mainloop()

##    arrayM50 = FlashArray("10.21.39.2", "pureuser", "pureuser")
##    array_info = arrayM50.get()
##    print ("FlashArray {} (version {}) REST session established!".format(array_info['array_name'], array_info['version']))

def getvols():
    msgText.delete('1.0', END)
    volumesText = "Getting the list of volumes ....please wait..."
    msgText.insert (END, volumesText )
    arrayM50 = FlashArray("XX.XX.XX.XXX", "pureuser", "pureuser")
    array_info = arrayM50.get()
    print ("FlashArray {} (version {}) REST session established!".format(array_info['array_name'], array_info['version']))
    volList = arrayM50.list_volumes()
    msgText.insert (END, volumesText )
    window.update()
    for itemVol in volList:
        ##Spliting the volume name and removing ''
       itemVol = str(itemVol).replace("'","\"")
       print ( itemVol )
       try:
           jsonVol = json.loads(str(itemVol))
           print ( jsonVol['source'] )
           listbox.insert(END, jsonVol['source'])
       except :
           pass
 
###System Copy or Backup SAP HANA 
def run():

  if ops.get() == 1:
      backuphana()
  elif ops.get() == 3:
      systemcopyhana()


def systemcopyhana():      

##################################################################
#####################SYSTEM COPY..################################
##################################################################
## 1. Get connection to SAP HANA and put it in Backup Mode
    con = Connection ('10.21.39.45',30015,'SYSTEM','***********')
    Connection.connect(con)
    cursor = con.cursor()
    cursor.execute("BACKUP DATA CREATE SNAPSHOT")
##    desc = cursor.description
##    print ( cursor.description )
##    result = cursor.fetchone()
    msgText.delete('1.0', END)
    window.update()
    runlogText = "\n >> SAP HANA Put in Backup Mode"
    msgText.insert (END, runlogText )
    pgBar["value"]=14
    window.update()
    time.sleep(1)
#### 2. Get Backup ID and put it in variable
    cursor.execute("select * from M_BACKUP_CATALOG WHERE \"ENTRY_TYPE_NAME\" = 'data snapshot' and \"STATE_NAME\" = 'prepared'")
    result = cursor.fetchone()
    print ( result )
    desc = str(result)
    backupid = desc.split(",")
    print ( "Backup ID is--->" + backupid[2] )
    runlogText = "\n >>> Back up Id is:"+ backupid[2]
    msgText.insert (END, runlogText )
    backupidnum = backupid[2]
    pgBar["value"]=28
    window.update()
    time.sleep(1)

###3. Freeze the file system on source system(Calling the shell script)
    print ( "Freezing the file system for the snapshots")
    runlogText = "Freezing the file system for the snapshots"
    msgText.insert (END, runlogText )
    xfs_controller = Pyro4.core.getProxyForURI("PYRO://10.21.39.45:7766/0a15272d3ee2223f728b445954b40d0289")
    xfs_controller.xfsfreeze("freeze")
    pgBar["value"]=42
    window.update()
    time.sleep(1)
    
## 4. Take snapshot of Data volumes
    arrayM50 = FlashArray("10.21.39.2", "pureuser", "pureuser")
    array_info = arrayM50.get()
    print ("FlashArray {} (version {}) REST session established!".format(array_info['array_name'], array_info['version']))
    runlogText = "\n >>>> Taking snapshots of Data volumes...."
    msgText.insert (END, runlogText )
    backupidnum = backupid[2]
    snapDataVol = arrayM50.create_snapshot("hanadatavolPSD")
    snapLogVol = arrayM50.create_snapshot("hanalogvolPSD")
    pgBar["value"]=56
    window.update()
    time.sleep(1)
###5. Freeze the file system on source system(Calling the shell script)
    print ( "Unfreezing the file system....")
    runlogText = "Unfreezing the file system..."
    msgText.insert (END, runlogText )
    xfs_controller = Pyro4.core.getProxyForURI("PYRO://10.21.39.45:7766/0a15272d3ee2223f728b445954b40d0289")
    xfs_controller.xfsunfreeze("Unfreeze")
    pgBar["value"]=70
    window.update()
    time.sleep(1)
    
## 6. Confirm the Backup ID and put it in backup catalog
    confirmationstring = "BACKUP DATA CLOSE SNAPSHOT BACKUP_ID "+ backupidnum + " SUCCESSFUL 'FlashManager Alpha Version'"
    print ("Confirmation string " + confirmationstring)
    cursor.execute(confirmationstring)
    print ( "Confirmation of Backup using snapshot" )
    runlogText = "\n >>>>> Confirmation of Backup using snapshot"+ backupidnum  
    msgText.insert (END, runlogText )
    pgBar["value"]=84
    window.update()
    time.sleep(1)
## 7. Copy the snapshots to Target volume
    runlogText = "\n >>>> Copying snapshots of Source Data volumes to Target Volumes..."
    msgText.insert (END, runlogText )
    kwargs = {'overwrite': 'true'}
    copyDestoperation = arrayM50.copy_volume(snapDataVol['name'],"hanadatavolQSD", **kwargs)
    arrayM50.copy_volume(snapLogVol['name'],"hanalogvolQSD", **kwargs)
    print ( "Snapshot copied to Target--->"+ snapDataVol['name'] +"Target" + str(copyDestoperation) )
    pgBar["value"]=100
    window.update()
    time.sleep(1)
    
## 6. Show success in GUI    
    con.close()
##################################################################
#####################SAP HANA BACKUP..################################
##################################################################

def backuphana():
## 1. Get connection to SAP HANA and put it in Backup Mode
    con = Connection ('XX.XX.XX.XXX',30015,'SYSTEM','***********')
    Connection.connect(con)
    cursor = con.cursor()
    cursor.execute("BACKUP DATA CREATE SNAPSHOT")
##    desc = cursor.description
##    print ( cursor.description )
##    result = cursor.fetchone()
    msgText.delete('1.0', END)
    window.update()
    runlogText = "\n >> SAP HANA Put in Backup Mode"
    msgText.insert (END, runlogText )
    pgBar["value"]=16
    window.update()
    time.sleep(1)
#### 2. Get Backup ID and put it in variable
    cursor.execute("select * from M_BACKUP_CATALOG WHERE \"ENTRY_TYPE_NAME\" = 'data snapshot' and \"STATE_NAME\" = 'prepared'")
    result = cursor.fetchone()
    print ( result )
    desc = str(result)
    backupid = desc.split(",")
    print ( "Backup ID is--->" + backupid[2] )
    runlogText = "\n >>> Back up Id is:"+ backupid[2]
    msgText.insert (END, runlogText )
    backupidnum = backupid[2]
    pgBar["value"]=32
    window.update()
    time.sleep(1)
###3. Freeze the file system on source system(Calling the shell script)
##    Pyro4.config.SERIALIZER = 'pickle'
##    print ( "Freezing the file system for the snapshots")
##    runlogText = "Freezing the file system for the snapshots"
##    msgText.insert (END, runlogText )
##    xfs_controller = Pyro4.core.Proxy("PYRO:obj_e112e4cdd29e4cc8875be46e4542db7c@10.21.39.45:58787")
##    xfs_controller.xfsfreeze("freeze")
##    pgBar["value"]=48
##    window.update()
##    time.sleep(1)
    
## 4. Take snapshot of Data volumes
    arrayM50 = FlashArray("XX.XX.XX.XXX", "pureuser", "pureuser")
    array_info = arrayM50.get()
    print ("FlashArray {} (version {}) REST session established!".format(array_info['array_name'], array_info['version']))
    runlogText = "\n >>>> Taking snapshots of Data volumes...."
    msgText.insert (END, runlogText )
    backupidnum = backupid[2]
    snapDataVol = arrayM50.create_snapshot("saphanadatavolume1")
    snapDataVol = arrayM50.create_snapshot("saphanadatavolume2")
    print ("Snapshot name is--->"+ str(snapDataVol))
##    arrayM50.create_snapshot("hanadatavolume2dr")
    pgBar["value"]=64
    window.update()
    time.sleep(1)
###5. Freeze the file system on source system(Calling the shell script)
##    print ( "Unfreezing the file system....")
##    runlogText = "Unfreezing the file system..."
##    msgText.insert (END, runlogText )
##    xfs_controller = Pyro4.core.Proxy("PYRO://10.21.39.45:7766/0a15272d3ee2223f728b445954b40d0289")
##    xfs_controller.xfsunfreeze("Unfreeze")
##    pgBar["value"]=80
##    window.update()
##    time.sleep(1)
    
## 5. Confirm the Backup ID and put it in backup catalog
    confirmationstring = "BACKUP DATA CLOSE SNAPSHOT BACKUP_ID "+ backupidnum + " SUCCESSFUL 'FlashManager Alpha Version'"
    print ("Confirmation string " + confirmationstring)
    cursor.execute(confirmationstring)
    print ( "Confirmation of Backup using snapshot" )
    runlogText = "\n >>>>> Confirmation of Backup using snapshot"+ backupidnum  
    msgText.insert (END, runlogText )
    pgBar["value"]=100
    window.update()
    time.sleep(1)

    
## 5. Show success in GUI    
    con.close()    
    
def fetchRecord():
    key = entries['key'].get()
    try:
        record = db[key]                      # fetch by key, show in GUI
    except:
        showerror(title='Error', message='No such key!')
    else:
        for field in fieldnames:
            entries[field].delete(0, END)
            entries[field].insert(0, repr(getattr(record, field)))

def close():
     window.destroy()
#############################################################################
    ############# MAIN PROGRAM ##################
#############################################################################    

#shelvename = 'class-shelve'
#fieldnames = ('Source SID', 'Target SID')


global entries
window = Tk()
window.title('SAP FLASHMANAGER')
window.geometry('1430x620')
entries = {}
v = IntVar()
mode = IntVar()
ops =IntVar()

##Select Mode Frame.....
modeFrame = LabelFrame(window,text="Select Mode")
modeFrame.grid(row=0,column=0) 
Radiobutton(modeFrame, text=" SAP HANA Mode", variable=mode, value=1, command=modesel).grid(row=0,sticky=W+E+N+S,ipadx=10,ipady=10)
Radiobutton(modeFrame, text=" SAP Classical Mode", variable=mode, value=2, command=modesel).grid(row=1,sticky=W+E+N+S,ipadx=10,ipady=10)



##Select Operation Frame.....
opsFrame = LabelFrame(window,text="Select Operation")
opsFrame.grid(row=0,column=2,ipadx=10,ipady=10) 
Radiobutton(opsFrame, text=" Backup using Snapshots ", variable=ops, value=1, command=operation).grid(row=0,sticky=W+E+N+S,ipadx=10,ipady=5)
Radiobutton(opsFrame, text=" Recover System ", variable=ops, value=2,command=operation).grid(row=1,sticky=W+E+N+S,ipadx=10,ipady=5)
Radiobutton(opsFrame, text=" System Copy using Snapshots ", variable=ops, value=3,command=operation).grid(row=2,sticky=W+E+N+S,ipadx=10,ipady=5)
print ( "Inside Operation New... ")


##Photo Image embed
canvas = Canvas(window)
canvas.grid(row = 0, column = 3)
photo = PhotoImage(file = 'ps_200.gif')
canvas.create_image(200,130,image=photo)

##Select SID Selection Frame.....
sidFrame = LabelFrame(window,text="Main")
sidFrame.grid(row=1,column=0) 

##Label(sidFrame, text=" Select Source SID...").grid(row=0,column=0,columnspan=10)
vSourceSID = StringVar(sidFrame)
vSourceSID.set("Source SID")
sidMenuSource = OptionMenu(sidFrame, vSourceSID, "Source SID","PSD","QSD","DSD")
sidMenuSource.grid(row=0,column=0)

##Label(sidFrame, text=".............").grid(row=0, column=0,columnspan=20,sticky=W)

##Label(sidFrame, text=" Select Target SID...").grid(row=0,column=10)
vTargetSID = StringVar(sidFrame)
vTargetSID.set("Target SID")
sidMenuTarget = OptionMenu(sidFrame, vTargetSID, "Target SID","PSD", "QSD", "DSD")
sidMenuTarget.grid(row=0,column=1)


##Select Action Selection Frame.....
actionFrame = LabelFrame(sidFrame,text="Action")
actionFrame.grid(row=1,column=0,padx=10,pady=10,ipadx=10,ipady=10)

checkButton=Button(actionFrame, text="Check",  command=check)
Style().configure(checkButton, relief="flat")
Style().map(checkButton,background=[('pressed',  'cyan')])
checkButton.grid(row=1,column=0,columnspan=10,ipadx=10)
Button(actionFrame, text="Edit Config", command=config).grid(row=1,column=10,columnspan=10,ipadx=10)
Button(actionFrame, text="Run",   command=run).grid(row=1,column=20,columnspan=10,ipadx=10)
Button(actionFrame, text="Quit",   command=close).grid(row=1,column=30,columnspan=10,ipadx=10)


##Select Status Selection Frame.....
statusFrame = LabelFrame(sidFrame,text="Status")
statusFrame.grid(row=2,column=0,padx=10,pady=10,ipadx=10,ipady=10)

pgBar = Progressbar(statusFrame, orient = HORIZONTAL, length=300, mode = "determinate")
pgBar.grid(row=0,column=0,columnspan=400,ipadx=10)


##Select Messages Selection Frame.....
msgFrame = LabelFrame(sidFrame,text="Messages")
msgFrame.grid(row=3,column=0,padx=10,pady=10,ipadx=10,ipady=10)

msgText = Text(msgFrame,height=5,width=60)
msgText.grid(row=0,column=0,ipadx=10)



##Select Configuration Selection Frame.....
noteFrame = LabelFrame(window,text="Configuration",height=100,width=30)
noteFrame.grid(row=1,column=3,padx=10,pady=10,ipadx=10,ipady=10)

note = Notebook(noteFrame)
tab1 = Frame(note)
tab2 = Frame(note)
tab3 = Frame(note)

note.add(tab1, text = "FlashArray",compound=TOP)
note.add(tab2, text = "Host-SID Configuration")
note.add(tab3, text = "Lun Configuration")
note.grid(row=1,column=0,rowspan=400,ipadx=10)
Button(noteFrame, text="Save Config",  command=saveconfig).grid(row=0,column=0,columnspan=10,sticky=E)
##Tab1 
Label(tab1, text="FlashArray//m IP").grid(row=0, column=30,columnspan=20,sticky=W,ipady=5)
arrayIP = Text(tab1,height=1,width=20)
arrayIP.grid(row=0, column=60,columnspan=20,sticky=W,ipady=5)
arrayIP.insert (END, "10.21.39.2")
Label(tab1, text="User ID").grid(row=1, column=30,columnspan=20,sticky=W,ipady=5)
userArray = Text(tab1,height=1,width=20)
userArray.grid(row=1, column=60,columnspan=20,sticky=W,ipady=5)
userArray.insert (END, "pureuser")
Label(tab1, text="Password").grid(row=2, column=30,columnspan=20,sticky=W,ipady=5)
passArray=Text(tab1,height=1,width=20)
passArray.grid(row=2, column=60,columnspan=20,sticky=W,ipady=5)
passArray.insert (END, "pureuser")

##Tab2
Label(tab2, text="PSD  ").grid(row=0, column=30,columnspan=20,sticky=W,ipady=5)
arrayIP = Text(tab2,height=1,width=20)
arrayIP.grid(row=0, column=60,columnspan=20,sticky=W,ipady=5)
arrayIP.insert (END, "saphanaprod")
Label(tab2, text="QSD  ").grid(row=1, column=30,columnspan=20,sticky=W,ipady=5)
userArray = Text(tab2,height=1,width=20)
userArray.grid(row=1, column=60,columnspan=20,sticky=W,ipady=5)
userArray.insert (END, "saphanaqual")
Label(tab2, text="DSD  ").grid(row=2, column=30,columnspan=20,sticky=W,ipady=5)
passArray=Text(tab2,height=1,width=20)
passArray.grid(row=2, column=60,columnspan=20,sticky=W,ipady=5)
passArray.insert (END, "saphanadev")

##Tab3
vsidMenu = StringVar(tab3)
vsidMenu.set("SID")
sidMenuConfig = OptionMenu(tab3, vsidMenu, "SID","PSD", "QSD", "DSD")
sidMenuConfig.grid(row=0,column=0)

lunName = Text(tab3,height=1,width=10)
lunName.grid(row=0, column=1)
lunName.insert (END, "Search...")

Button(tab3, text="Get",  command=getvols).grid(row=0,column=2)

listbox = Listbox(tab3)
listbox.grid(row=0, column=3)

##Disable the configuration frame...
note.tab(0, state="disabled")
note.tab(1, state="disabled")
note.tab(2, state="disabled")


#db = shelve.open(shelvename)
window.mainloop()
#db.close() # back here after quit or window close

