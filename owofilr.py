"""
Created by
 _          _ _       _          _ _       _       
| |__   ___| | | ___ | |__   ___| | | ___ (_)_   _ 
| '_ \ / _ \ | |/ _ \| '_ \ / _ \ | |/ _ \| | | | |
| | | |  __/ | | (_) | | | |  __/ | | (_) | | |_| |
|_| |_|\___|_|_|\___/|_| |_|\___|_|_|\___// |\__,_|
                                        |__/  
"""

import pyrebase,json,requests,time,os
import random as ran
import tkinter as tk
from tkinter import ttk,filedialog

config = {
  'apiKey': "AIzaSyAuEUKhkn58P28ogs_nFtVC1mCpVDjSsf8",
  'authDomain': "python-owo.firebaseapp.com",
  'projectId': "python-owo",
  'storageBucket': "python-owo.appspot.com",
  'messagingSenderId': "983242282186",
  'appId': "1:983242282186:web:863ead54f16ef8bd94d033",
  'measurementId': "G-J5S6CJFTC1",
  'databaseURL': "https://python-owo-default-rtdb.asia-southeast1.firebasedatabase.app/"
}
email,password,username, token,info = "","","","",""
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
main = tk.Tk()
main.title("owofilr - login")
main.geometry('300x200+%d+%d' % ((main.winfo_screenwidth() - 300) / 2, (main.winfo_screenheight() - 200) / 2))
def errorwindow(reason):
    error = tk.Tk()
    error.title("owofilr - notification")
    error.geometry("1000x50")
    errorlabel = tk.Label(error,text="Oops, "+reason).pack()
    error.mainloop()
def createuser():
    global user
    global token
    global info
    em = entryemail.get()
    ps = entrypass.get()
    ur = entryuser.get()
    try:
        auth.create_user_with_email_and_password(em,ps)
        user = auth.sign_in_with_email_and_password(em,ps)
        token = user['idToken']
    except requests.HTTPError as er:
        error_json = er.args[1]
        error = json.loads(error_json)['error']['message']
        if error == "WEAK_PASSWORD : Password should be at least 6 characters":
            errorwindow("Password too weak! (At least 6 chars)")
        elif error == "INVALID_EMAIL":
            errorwindow("Invalid Email!")
        elif error == "INVALID_PASSWORD":
            errorwindow('Password entered is not correct')
        else:
            errorwindow(str(error))
    everified = auth.get_account_info(token).get('users')[0].get('emailVerified')
    em = em.replace(".","*")
    db.child('usernames').update({em:ur})
    db.child('sharefile').update({ur:"default.txt"})
    if everified == False:
        auth.send_email_verification(token)
        errorwindow("your email isn't verified, we've sent you an email! After verifying, click login")
    else:
        afterlogin(ur)
        main.destroy()  
def login():
    global user
    global token
    global info
    em=entryemail.get()
    ps=entrypass.get()
    try:
        user = auth.sign_in_with_email_and_password(em,ps)
        token = user['idToken']
    except requests.HTTPError as er:
        error_json = er.args[1]
        error = json.loads(error_json)['error']['message']
        if error == "EMAIL_EXISTS":
            errorwindow("Account With This Email Already Exists")
        elif error == "WEAK_PASSWORD : Password should be at least 6 characters":
            errorwindow("Password too weak! (At least 6 chars)")
        elif error == "INVALID_EMAIL":
            errorwindow("Invalid Email!")
        else:
            errorwindow(str(error))
    everified = auth.get_account_info(token).get('users')[0].get('emailVerified')
    if everified == False:
        auth.send_email_verification(token)
        errorwindow("It appears your email hasnt been verified, weve sent you an email!")
    else:
        data = db.child("usernames").child(em.replace('.','*')).get().val()
        afterlogin(data)
        main.destroy()     
def displayfileinfo(event):
    global curfileurl
    global curfilename
    data = event.widget.get(event.widget.curselection()[0])
    fileinfo = db.child('fileinfo').child(data.replace('.','*')).get().val()
    nameinfolbl.config(text=fileinfo['name'])
    curfilename = data
    frominfolbl.config(text=fileinfo['owner'])
    curfileurl = fileinfo['url']
def choosefilefunc():
    global curfilepath
    f= filedialog.askopenfile()
    curfilepath= f.name
    filea.config(text=f)
def uploadbtncmd(ur):
    global usernamelist
    global namefile
    global uploadmenu
    global filea
    uploadmenu = tk.Tk()
    uploadmenu.title("owofilr - Upload File")
    screenwidth,screenheight = uploadmenu.winfo_screenwidth(),uploadmenu.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (371, 175, (screenwidth - 371) / 2, (screenheight - 175) / 2)
    uploadmenu.geometry(alignstr)
    uploadmenu.resizable(width=False, height=False)
    namefilelbl = tk.Label(uploadmenu,justify='left',text='Name your file').place(x=10,y=10,width=88,height=30)
    namefile = tk.Entry(uploadmenu,justify='left',text='Homework')
    namefile.place(x=10,y=40,width=207,height=30)
    usernamelbl = tk.Label(uploadmenu,justify='left',text='share with (list of usernames, seperate by commas)').place(x=10,y=70,height=30)
    usernamelist=tk.Entry(uploadmenu,justify='left',text='Bob,Jack')
    usernamelist.place(x=10,y=100,width=350,height=30)
    choosefilebtn = tk.Button(uploadmenu,justify='center',text='Choose File',command=lambda: choosefilefunc()).place(x=10,y=140,width=70,height=25)
    filea = tk.Label(uploadmenu,justify='left',text='/')
    filea.place(x=90,y=140,height=25)
    uploadbtn = tk.Button(uploadmenu,justify='center',text='Upload',command=lambda: funcupload(ur)).place(x=290,y=140,width=70,height=25)
    uploadmenu.mainloop()
def funcupload(ur):
    filename = os.path.basename(curfilepath)
    usrlist = usernamelist.get()
    nameofile = namefile.get()
    usrlist=usrlist+","+ur
    e = storage.child(ur+'/'+nameofile).put(curfilepath)
    nfileurl = storage.child(ur+'/'+nameofile).get_url(e['downloadTokens'])
    db.child('fileinfo').child(filename.replace('.','*')).update({'name':nameofile})
    db.child('fileinfo').child(filename.replace('.','*')).update({'owner':ur})
    db.child('fileinfo').child(filename.replace('.','*')).update({'url':nfileurl})
    usrlisttemp = usrlist.split(',')
    for user in usrlisttemp:
        temp = db.child('sharefile').get().val()[user]
        temp=temp+','+filename
        db.child('sharefile').update({user:temp})
    print('funcupload')  
    uploadmenu.destroy()
    uploadmenu()
def downloadbtncmd():
    directory = filedialog.askdirectory(initialdir = "/",title = "Directory to download to")
    r = requests.get(curfileurl)
    f = open(str(directory+"/"+curfilename),'wb')
    f.write(r.content)
    f.close()
def filelistupdate(ur):
    filelist.delete(0,tk.END)
    list_itemstemp = db.child("sharefile").child(ur).get().val().split(',')
    for item in list_itemstemp:
        filelist.insert(tk.END,item)
def afterlogin(ur):
    print(ur)
    #setup of home menu
    global filelist
    global testl
    global nameinfolbl
    global frominfolbl
    list_items = []
    dl = tk.Tk()
    dl.title("owofilr - "+ur)
    dl.geometry('323x205+%d+%d' % ((dl.winfo_screenwidth() - 323) / 2, (dl.winfo_screenheight() - 205) / 2))
    dl.resizable(width=False, height=False)
    username=tk.Label(dl,justify='left',text=ur).place(x=10,y=10,width=159,height=30)
    uploadbtn=tk.Button(dl,borderwidth='1px',justify="center",text='Upload',command=lambda: uploadbtncmd(ur))
    uploadbtn.place(x=10,y=170,width=70,height=25)
    updatebtn=tk.Button(dl,borderwidth='1px',justify="center",text='Refresh',command=lambda: filelistupdate(ur))
    updatebtn.place(x=10,y=140,width=70,height=25)
    filelist=tk.Listbox(dl,borderwidth='1px',justify="center",selectmode=tk.SINGLE,listvariable=list_items)
    filelistupdate(ur)
    filelist.place(x=170,y=10,width=141,height=186)
    filelist.bind('<<ListboxSelect>>', displayfileinfo)
    dowloadbtn=tk.Button(dl, justify="center",text='Download',command=lambda: downloadbtncmd())
    dowloadbtn.place(x=90,y=170,width=70,height=25)
    namelbl = tk.Label(dl,justify='center',text='Name:').place(x=10,y=40,height=25)
    fromlbl = tk.Label(dl,justify='center',text='From:').place(x=10,y=90,height=25)
    nameinfolbl = tk.Label(dl,justify='left',text='')
    nameinfolbl.place(x=20,y=65,height=25)
    frominfolbl = tk.Label(dl,justify='left',text='')
    frominfolbl.place(x=20,y=115,height=25)
#tkinter login menu setup
labelemail= tk.Label(main,text="Email:").pack()
entryemail = tk.Entry(main,textvariable=email)
entryemail.pack()
labelpass = tk.Label(main,text="Password:").pack()
entrypass = tk.Entry(main,show='•',textvariable=password)
entrypass.pack()
labeluser = tk.Label(main,text="Username (only when registering").pack()
entryuser = tk.Entry(main,textvariable=username)
entryuser.pack()
regbutton = ttk.Button(main,text="Register",command=lambda: createuser()).pack()
loginbutton = ttk.Button(main,text="Login",command=lambda: login()).pack()
main.mainloop()
