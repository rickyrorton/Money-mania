from os import path as ospath
from os import remove
import sys
from tkinter import *
from random import randrange
from pickle import load,dump
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter.ttk import Notebook
from mysql.connector import connect
from tkinter import Frame

#database connectivity
db=connect(
    host="",
    user="",
    password="",
    database="")

dbcursor=db.cursor(buffered=True)

global application_path
if getattr(sys, 'frozen', False):
    application_path = ospath.dirname(sys.executable)
elif __file__:
    application_path = ospath.dirname(__file__)

#Defines the window and its details
window = Tk()
window.title("Money mania")
icon_path=Image.open(ospath.join(application_path,'game_logo.png'))
icon=ImageTk.PhotoImage(icon_path)
window.iconphoto(False,icon)
window.geometry("500x400")
window.resizable(False,False)
window.configure(bg = '#3d3d3d')

def keepsqlalive():
    def ping():
        global db
        try:
            db.ping(reconnect=False, attempts=1, delay=0)
            print('Alive')
        except:
            print('connection lost')
        window.after(10000,lambda:ping())
    ping()
keepsqlalive()
#getting data from sql db
def readfromdb(username):
    global application_path
    global hand
    global bank
    global inventory
    global businesses
    f=open(ospath.join(application_path,'gameData.dat'),'wb')
    dbcursor.execute('select hand,bank,inventory,businesses from players where username=%s',(username,))
    dbdata=dbcursor.fetchone()
    hand=dbdata[0]
    bank=dbdata[1]
    inventory=[]
    businesses=[]
    for i in dbdata[2].split():
        inventory.append(i.replace('_',' '))
    for i in dbdata[3].split():
        businesses.append(i.replace('_',' ')) 
    data = {'hand' : hand, 'bank' : bank, 'inventory':inventory,'businesses':businesses}
    dump(data,f)
    f.close()
    money_hand.config(text="Money in hand : " + str(hand))
    money_bank.config(text="Money in bank : " + str(bank))

#writting data to sql db
def write_to_db():
    global application_path
    global retrieved_data
    f=open(ospath.join(application_path,'gameData.dat'),'rb')
    data=load(f)
    hand = data['hand']
    bank = data['bank']
    inventory=data['inventory']
    businesses=data['businesses']
    invdb=''
    businessdb=''
    count=0
    for i in inventory:
        if count==0:
            invdb=invdb+i.replace(' ','_')
            count+=1
        elif count == 1:
            invdb=invdb+' '+i.replace(' ','_')
    count=0
    for i in businesses:
        if count==0:
            businessdb=businessdb+i.replace(' ','_')
            count+=1
        elif count == 1:
            businessdb=businessdb+' '+i.replace(' ','_')
    vals=(hand,bank,invdb,businessdb,retrieved_data[0])
    dbcursor.execute('update players set hand=%s,bank=%s,inventory=%s,businesses=%s where username=%s',vals)
    db.commit()
    f.close()
    remove(ospath.join(application_path,"gameData.dat"))
    window.destroy()

window.protocol("WM_DELETE_WINDOW", write_to_db)

def register():
    def register_but(event=None):
        global retrieved_data
        val=(user.get(),)
        dbcursor.execute('select hand,bank,inventory,businesses from players where username=%s',val)
        dbdata=dbcursor.fetchone()
        if dbdata == None:
            if len(password.get()) != 0 or len(reg_pass_confirm.get()) != 0 or len(user.get()) != 0: 
                if password.get()==reg_pass_confirm.get():
                    dbcursor.execute('insert into players values(%s,%s,1000,0,"","")',(user.get(),password.get()))
                    db.commit()
                    dbcursor.execute('select hand,bank,inventory,businesses from players where username=%s',(user.get(),))
                    retrieved_data = dbcursor.fetchone()
                    reg_result.config(text='Account successfully created!\nGame will load shortly.')
                    login.after(3000, lambda:window.deiconify())
                    login.after(3000, lambda:login.destroy())
                else:
                    reg_result.config(text='Passwords do not match \nenter again',fg='red')
            else:
                reg_result.config(text='Please fill all the boxes',fg='red')
        else:
            reg_result.config(text='Username already exists \nEnter a different one',fg='red')

    reg_pass_confirm=Entry(login,width=15,bg = '#c4c3c0')
    reg_pass_confirm.place(relx=0.5,rely=0.6,anchor=CENTER)
    reg_pass_confirm_label=Label(login,text='Confirm:',font=("Arial Bold",10),bg = '#3d3d3d', fg = 'white')
    reg_pass_confirm_label.place(relx=0.18,rely=0.6,anchor=CENTER)
    reg_result=Label(login,text='Press the enter button to register',font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white')
    reg_result.place(relx=0.5,rely=0.85,anchor=CENTER)
    login.bind('<Return>', register_but)

#login page
def logincheck():
    global retrieved_data
    val=(user.get(),)
    dbcursor.execute('SELECT * from players where username=%s',val)
    retrieved_data=dbcursor.fetchone()
    if retrieved_data == None:
        login_result.config(text='Invalid username')
    elif retrieved_data[1] != password.get():
        login_result.config(text='Wrong password')
    elif retrieved_data[1] == password.get():
        readfromdb(retrieved_data[0])
        window.deiconify()
        login.destroy()
        initialize()

def cancellogin():
    window.destroy()

login=Toplevel()
login.title('Welcome')
login.geometry('300x300')
login.resizable(False,False)
login.configure(bg = '#3d3d3d')
login.protocol("WM_DELETE_WINDOW", cancellogin)

login_button=Button(login,text='Login',command=logincheck).place(relx=0.3,rely=0.73,anchor=CENTER)
user=Entry(login,width=15,bg = '#c4c3c0')
user.place(relx=0.5,rely=0.4,anchor=CENTER)
login_result=Label(login,text='',font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white')
login_result.place(relx=0.5,rely=0.85,anchor=CENTER)
password=Entry(login,width=15,bg = '#c4c3c0')
password.place(relx=0.5,rely=0.5,anchor=CENTER)
user_label=Label(login,text="Username:",font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white').place(relx=0.2,rely=0.4,anchor=CENTER)
password_label=Label(login,text="Password:",font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white').place(relx=0.198,rely=0.5,anchor=CENTER)
cancel_button=Button(login,text='Cancel',command=cancellogin).place(relx=0.5,rely=0.73,anchor=CENTER)
register_button=Button(login,text='Register',command=register).place(relx=0.7,rely=0.73,anchor=CENTER)
game_name=Label(login,text='MONEY MANIA',font=("Impact",20), bg = '#3d3d3d', fg = '#fcc600')
game_name.place(relx=0.587,rely=0.185,anchor=CENTER)
maker_name=Label(login,text='Made by Nishant and Rishi',font=("Impact",10), bg = '#3d3d3d', fg = 'white')
maker_name.place(relx=0.58,rely=0.26,anchor=CENTER)


global hand
global bank
global businesses
global inventory

#Checks if game data file exists, if it does, it loads the data
if ospath.exists(ospath.join(application_path,"gameData.dat")) == True:
    with open(ospath.join(application_path,'gameData.dat'),'rb') as f:
        data = load(f)

        hand = data['hand']
        bank = data['bank']
        inventory=data['inventory']
        businesses=data['businesses']

        global hand_session
        global bank_session
        global inventory_session
        global businesses_session

        hand_session = hand
        bank_session = bank
        inventory_session = inventory
        businesses_session = businesses

else:#when the .dat file does not exist
    hand = 1000
    bank = 0
    inventory=[]
    businesses = []

def saveData():#writes data to the file
    global application_path
    global hand
    global bank
    global inventory
    global businesses
    data = {'hand' : hand, 'bank' : bank, 'inventory':inventory,'businesses':businesses}
    f = open(ospath.join(application_path,'gameData.dat'),'wb')
    dump(data,f)
    f.close()

global cooldown
cooldown=2000

def work_cooldown():
    global cooldown
    work.config(state=DISABLED)
    work.after(cooldown, lambda: work.config(state=NORMAL))

global multiplier
multiplier=1    

def workcmd():
    global hand
    global multiplier
    
    moneyadd = int(randrange(10,101,10) * multiplier)
    hand += moneyadd
    money_hand.config(text="Money in hand : "+"{:,}".format(hand))
    saveData()
    work_cooldown()

def depall():
    global hand
    global bank

    bank += hand
    money_hand.config(text="Money in hand : 0")
    money_bank.config(text="Money in bank : "+"{:,}".format(bank))
    hand=0
    saveData()

def withall():
    global hand
    global bank
    
    hand += bank
    money_hand.config(text="Money in hand : "+"{:,}".format(hand))
    money_bank.config(text="Money in bank : 0")
    bank=0
    saveData()

def depamt(event = None):
    global hand
    global bank

    amount = 0    
    try:
        amount=int(deposit.get())
        if amount > 0:
            pass
        else:
            messagebox.showerror("ERROR", "You can only input a positive integer!")
            amount = 0
    except:
        messagebox.showerror("ERROR", "You can only input a positive integer!")
    
    if amount > hand:
        amount = hand
        hand -= amount
        bank += amount
    elif hand <= 0:
        amount = 0
        hand -= amount
        bank += amount
    else:
        hand -= amount
        bank += amount
    money_hand.config(text="Money in hand : "+"{:,}".format(hand))
    money_bank.config(text="Money in bank : "+"{:,}".format(bank))
    saveData()
    deposit.delete(0, len(str(amount)) + 1)

def withamt(event = None):
    global hand
    global bank

    amount = 0
    try:
        amount=int(withdraw.get())
        if amount > 0:
            pass
        else:
            messagebox.showerror("ERROR", "You can only input a positive integer!")
            amount = 0
    except:
        messagebox.showerror("ERROR", "You can only input a positve integer!")
    
    if amount > bank:
        amount = bank
        hand += amount
        bank -= amount
    else:
        hand += amount
        bank -= amount

    money_hand.config(text="Money in hand : "+"{:,}".format(hand))
    money_bank.config(text="Money in bank : "+"{:,}".format(bank))
    saveData()
    withdraw.delete(0, len(str(amount)) + 1)

def quit_game():
        global hand
        global bank
        global data
        global inventory
        global businesses
        global application_path
                
        MsgBox = messagebox.askquestion('Quit Game','Do you want to save your progress before quitting?',icon = 'warning')
        if MsgBox == 'yes':
            saveData()
            write_to_db()
        else:
            MsgBox = messagebox.askquestion('Quit Game','Do you want to erase all your progress?\nBy clicking \"no\", only the progress of this session will be erased.',icon = 'warning')
            if MsgBox == 'yes':
                remove(ospath.join(application_path,"gameData.dat"))
            else:
                global hand_session
                global bank_session
                global inventory_session
                global businesses_session

                hand = hand_session
                bank = bank_session 
                inventory=inventory_session
                businesses=businesses_session
                saveData()
                write_to_db()

def image_import(filename,height,width):
    global application_path
    image_path=ospath.join(application_path,filename)
    img=Image.open(image_path)
    img=img.resize((height,width), Image.ANTIALIAS)
    pic=ImageTk.PhotoImage(img)
    return pic
#importing pics
global login_logo
login_logo=image_import('game_logo.png',64,64)
login_logo_label=Label(login,image=login_logo,compound=CENTER,bg='#3d3d3d').place(relx=0.1,rely=0.1)

global Energy_pic
Energy_pic=image_import("Energy_drink.png",46,46)

global steroids_pic
steroids_pic=image_import("steroids.png",46,46)

global Efficiency_pic
Efficiency_pic=image_import("effieciency_shot.png",46,46)

global demigod_pic
demigod_pic=image_import('Demigod_pill.png', 46, 46)

global god_pic
god_pic=image_import('god_pills.png',46,46)

global saiyan_pic
saiyan_pic=image_import('supersaiyanpills.png',46,46)

global lemonade_pic
lemonade_pic=image_import('lemonade.png',40,40)

global res_pic
res_pic=image_import('restaurant.png',40,40)

global space_pic
space_pic=image_import('space.png',40,40)

global market_pic
market_pic=image_import('supermarket.png',40,40)

global football_pic
football_pic=image_import('football.png',40,40)

global car_pic
car_pic=image_import('car.png',40,40)

def buy_consumable(name,price):
    global hand
    global inventory
    global data
    
    if hand >= price:
        MsgBox = messagebox.askquestion('Buy Item','Are you sure you want to buy this item?',icon = 'warning')
        if MsgBox == 'yes':
            hand -= price
            inventory.append(name)
            messagebox.showinfo("Congrats!", "Succesfully bought {}!" . format(name))
    else:
        messagebox.showerror("ERROR","you dont have enough money in hand, if u have money in bank, you can withdraw it and buy {}".format(name))
        return "Not enough money"

    money_hand.config(text="Money in hand : "+"{:,}".format(hand))
    saveData()

def buy_business(name,price):
    global bank
    global businesses
    MsgBox = messagebox.askquestion('Buy Business','Are you sure you want to buy {}?'.format(name),icon = 'warning')
    if MsgBox == 'yes':
        if bank >= price:
            if name not in businesses:
                bank -= price
                businesses.append(name)
                
            else:
                messagebox.showerror("ERROR","You have already bought {}".format(name))
        else:
            messagebox.showerror("ERROR","you dont have enough money in bank, if u have money on hand, you can deposit it and buy {}".format(name))
    else:
        pass
    money_bank.config(text="Money in bank : "+"{:,}".format(bank))
    saveData()

def start_business(name,time):
    global businesses
    global hand
    if name in businesses:
        moneyadd = randrange(10,101,10)
        hand += moneyadd
        money_hand.config(text="Money in hand : "+"{:,}".format(hand))
        saveData()
        window.after(time,lambda:start_business(name, time))

#to make the businesses start working 
def initialize():    
    start_business('Lemonade Stand', 10000)
    start_business('Fancy restaurant', 7000)
    start_business('Supermarket', 5000)
    start_business('Car Showroom', 2000)
    start_business('Football team', 1000)
    start_business('Space tourism company', 500)

def buy_lemonade():
    global lemonade_button
    buy_business('Lemonade Stand', 5000)
    start_business('Lemonade Stand', 10000)
    if 'Lemonade Stand' in businesses:
        lemonade_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_restaurant():
    global restaurant_button
    buy_business('Fancy restaurant', 10000)
    start_business('Fancy restaurant', 7000)
    if 'Fancy restaurant' in businesses:
        restaurant_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_market():
    global market_button
    buy_business('Supermarket', 50000)
    start_business('Supermarket', 5000)
    if 'Supermarket' in businesses:
        market_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_showroom():
    global car_button
    buy_business('Car Showroom', 100000)
    start_business('Car Showroom', 2000)
    if 'Car Showroom' in businesses:
        car_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_team():
    global football_button
    buy_business('Football team', 250000)
    start_business('Football team', 1000)
    if 'Football team' in businesses:
        football_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_space():
    global space_button
    buy_business('Space tourism company', 1000000)
    start_business('Space tourism company', 500)
    if 'Space tourism company' in businesses:
        space_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_energy():
    global Energy_button
    buy_consumable('Energy Drink',15000)
    if 'Energy Drink' in inventory:
        Energy_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_steroids():
    global Steroids_button
    global steroids_use
    buy_consumable('Steroids',2000)
    if 'Steroids' in inventory:
        Steroids_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    
def buy_eff():
    global Efficiency_button
    buy_consumable('Efficiency shot', 25000)
    if 'Efficiency shot' in inventory:
        Efficiency_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_demi():
    global Demigod_button
    buy_consumable('Demigod pills',100000)
    if 'Demigod pills' in inventory:
        Demigod_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_god():
    global God_button
    buy_consumable('God pills',1000000)
    if 'God pills' in inventory:
        God_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def buy_saiyan():
    global Saiyan_button
    buy_consumable('Super saiyan pills',100000000)
    if 'Super saiyan pills' in inventory:
        Saiyan_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

def shopbutton():
    def on_closing_shop():
        shop_open.config(state=NORMAL)
        shop.destroy()
    global shop
    shop_open.config(state=DISABLED)
    shop=Toplevel()
    shop.title("Shop")
    shop.geometry("600x400")
    shop.resizable(False,False)
    shop.configure(bg='#3d3d3d')
    shop.protocol("WM_DELETE_WINDOW", on_closing_shop)
    
    #ttk notebook stuff
    notebook=Notebook(shop)
    notebook.place(relx=0.5,rely=0.48,anchor=CENTER)
    frame1 = Frame(notebook, width=580, height=350)
    frame1.configure(bg='#3d3d3d')
    frame2 = Frame(notebook, width=580, height=350)
    frame2.configure(bg='#3d3d3d')
    frame1.pack(fill='both', expand=True)
    frame2.pack(fill='both', expand=True)
    notebook.add(frame1, text='Businesses')
    notebook.add(frame2, text='Consumables')
    
    #frame1(employee specific stuff)
    global lemonade_pic
    global lemonade_button
    lemonade_label=Label(frame1,text="Name : Lemonade Stand\nPrice : 5,000$\nInfo : Earns every 10 seconds",bg="#3d3d3d",fg='white',justify=LEFT,image=lemonade_pic,compound=LEFT).place(relx=0.18,rely=0.2,anchor=CENTER)
    lemonade_button=Button(frame1,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_lemonade)
    lemonade_button.place(relx=0.4,rely=0.2,anchor=CENTER)
    if 'Lemonade Stand' in businesses:
        lemonade_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    
    global res_pic
    global restaurant_button
    restaurant_label=Label(frame1,text="Name : Fancy Restaurant\nFee : 10,000$\nInfo : Earns every 7 seconds",bg="#3d3d3d",fg='white',justify=LEFT,image=res_pic,compound=LEFT).place(relx=0.18,rely=0.5,anchor=CENTER)
    restaurant_button=Button(frame1,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_restaurant)
    restaurant_button.place(relx=0.4,rely=0.5,anchor=CENTER)
    if 'Fancy restaurant' in businesses:
        restaurant_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    
    global market_pic
    global market_button
    market_label=Label(frame1,text="Name : Supermarket\nFee : 50,000$\nInfo : Earns every 5 seconds",bg="#3d3d3d",fg='white',justify=LEFT,image=market_pic,compound=LEFT).place(relx=0.18,rely=0.8,anchor=CENTER)
    market_button=Button(frame1,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_market)
    market_button.place(relx=0.4,rely=0.8,anchor=CENTER)
    if 'Supermarket' in businesses:
        market_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    
    global car_pic
    global car_button
    car_label=Label(frame1,text="Name : Car Showroom\nFee : 100,000$\nInfo : Earns every 2 seconds",bg="#3d3d3d",fg='white',justify=LEFT,image=car_pic,compound=LEFT).place(relx=0.7,rely=0.2,anchor=CENTER)
    car_button=Button(frame1,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_showroom)
    car_button.place(relx=0.9,rely=0.2,anchor=CENTER)
    if 'Car Showroom' in businesses:
        car_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    
    global football_pic
    global football_button
    football_label=Label(frame1,text="Name : Football team\nFee : 250,000$\nInfo : Earns every second",bg="#3d3d3d",fg='white',justify=LEFT,image=football_pic,compound=LEFT).place(relx=0.7,rely=0.5,anchor=CENTER)
    football_button=Button(frame1,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_team)
    football_button.place(relx=0.9,rely=0.5,anchor=CENTER)
    if 'Football team' in businesses:
        football_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    
    global space_pic
    global space_button
    space_label=Label(frame1,text="Name : Space tourism company\nFee : 1,000,000$\nInfo : Earns every 0.5 seconds",bg="#3d3d3d",fg='white',justify=LEFT,image=space_pic,compound=LEFT).place(relx=0.68,rely=0.8,anchor=CENTER)
    space_button=Button(frame1,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_space)
    space_button.place(relx=0.9,rely=0.8,anchor=CENTER)
    if 'Space tourism company' in businesses:
        space_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    

    #frame2(consumables specific stuff) 
    global Energy_pic
    Energy_label=Label(frame2,text="Name : Energy drink\nPrice : 15,000$\nInfo : Increases earnings by 10%",bg="#3d3d3d",fg='white',justify=LEFT,image=Energy_pic,compound=LEFT).place(relx=0.18,rely=0.2,anchor=CENTER)
    global Energy_button
    Energy_button=Button(frame2,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_energy)
    Energy_button.place(relx=0.45,rely=0.16,anchor=CENTER)
    if 'Energy Drink' in inventory:
        Energy_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

    global steroids_pic
    Steroids_label=Label(frame2,text="Name : Steroids\nPrice : 2,000$\nInfo : No work cooldown for 20 secs",bg="#3d3d3d",fg='white',justify=LEFT,image=steroids_pic,compound=LEFT).place(relx=0.2,rely=0.47,anchor=CENTER)
    global Steroids_button
    Steroids_button=Button(frame2,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_steroids)
    Steroids_button.place(relx=0.45,rely=0.43,anchor=CENTER)
    if 'Steroids' in inventory:
        Steroids_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

    global Efficiency_pic
    Efficiency_label=Label(frame2,text="Name : Efficiency Shot\nPrice : 25,000$\nInfo : Increases earnings by 25%",bg="#3d3d3d",fg='white',justify=LEFT,image=Efficiency_pic,compound=LEFT).place(relx=0.18,rely=0.75,anchor=CENTER)
    global Efficiency_button
    Efficiency_button=Button(frame2,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_eff)
    Efficiency_button.place(relx=0.45,rely=0.71,anchor=CENTER)
    if 'Efficiency shot' in inventory:
        Efficiency_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

    global demigod_pic
    Demigod_label=Label(frame2,text="Name : Demigod pills\nPrice : 100,000$\nInfo : Increases earnings by 50%",bg="#3d3d3d",fg='white',justify=LEFT,image=demigod_pic,compound=LEFT).place(relx=0.7,rely=0.2,anchor=CENTER)
    global Demigod_button
    Demigod_button=Button(frame2,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_demi)
    Demigod_button.place(relx=0.95,rely=0.16,anchor=CENTER)
    if 'Demigod pills' in inventory:
        Demigod_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
        
    global god_pic
    God_label=Label(frame2,text="Name : God Pills\nPrice : 1,000,000$\nInfo : Increases earnings by 100%",bg="#3d3d3d",fg='white',justify=LEFT,image=god_pic,compound=LEFT).place(relx=0.7,rely=0.47,anchor=CENTER)
    global God_button
    God_button=Button(frame2,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_god)
    God_button.place(relx=0.95,rely=0.43,anchor=CENTER)
    if 'God pills' in inventory:
        God_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)
    
    global saiyan_pic
    Saiyan_label=Label(frame2,text="Name : Super Saiyan Pills\nPrice : 100,000,000$\nInfo : Increases earnings by 125% \nand decreases work cooldown \nto 0.5 seconds",bg="#3d3d3d",fg='white',justify=LEFT,image=saiyan_pic,compound=LEFT).place(relx=0.7,rely=0.77,anchor=CENTER)
    global Saiyan_button
    Saiyan_button=Button(frame2,text="Buy",font=("Arial",10),bg="#bbbebf",fg="black",command=buy_saiyan)
    Saiyan_button.place(relx=0.95,rely=0.70,anchor=CENTER)
    if 'Super saiyan pills' in inventory:
        Saiyan_button.config(bg = 'red', fg = 'white', text='Owned', state=DISABLED)

    #functions controlling the 'use' buttons
    def increase_earning(item,time,mul):
        global inventory
        dic = {
            "Energy Drink" : [energy_use, Energy_button],
            "Efficiency shot" : [efficiency_use, Efficiency_button],
            "Demigod pills" : [demigod_use, Demigod_button],
            "God pills" : [god_use, God_button]
        }
        if item in inventory:
            def decrease_mul():
                global multiplier
                multiplier=1
                button = dic[item][1]
                button_use = dic[item][0]
                button.config(bg='white', fg='black', text='Buy', state=NORMAL)
                button_use.config(text='Use', bg='light grey', fg='black', state=NORMAL)
            global multiplier
            multiplier=mul
            button_use = dic[item][0]
            button_use.config(bg = 'grey', fg = 'white', text='Using', state=DISABLED)
            frame2.after(time,lambda:decrease_mul())
            inventory.remove(item)
            return True
        else:
            messagebox.showerror("ERROR", "You need to buy {} to use them".format(item)) 

    def energy_cmd():
        increase_earning('Energy Drink',30000, 1.1)
            
    def steroid_cmd():
        global inventory
        if 'Steroids' in inventory:
            def decreasecooldown():
                global cooldown
                cooldown=2000
                Steroids_button.config(bg='white', fg='black', text='Buy', state=NORMAL)
                steroids_use.config(text='Use',bg = 'light grey', fg = 'black', state=NORMAL)
            global cooldown
            global steroids_use
            cooldown=0
            steroids_use.config(bg = 'grey', fg = 'white', text='Using', state=DISABLED)
            frame2.after(20000,lambda:decreasecooldown())
            inventory.remove('Steroids')
            
        else:
            messagebox.showerror("ERROR", "You need to buy steroids to use them")
    
    def efficiency_cmd():
        increase_earning('Efficiency shot',30000, 1.25)

    def demigod_cmd():
        increase_earning('Demigod pills',60000, 1.50)
            
    def god_cmd():
        increase_earning('God pills',120000, 2)

    def saiyan_cmd():
        global inventory
        if 'Super saiyan pills' in inventory:
            def decrease_mul_cooldown():
                global multiplier
                global cooldown
                multiplier=1
                cooldown=2000
                Saiyan_button.config(bg = 'white', fg = 'black', text='Buy', state=NORMAL)
                saiyan_use.config(text='Use', bg='white', fg='black', state=NORMAL)
            global multiplier
            global cooldown
            multiplier = 2.25
            cooldown = 500
            saiyan_use.config(bg = 'grey', fg = 'white', text='Using', state=DISABLED)
            frame2.after(60000,lambda:decrease_mul_cooldown())
            inventory.remove('Super saiyan pills')
        else:
            messagebox.showerror("ERROR", "You need to buy {} to use them".format('Super saiyan pills'))
    
    #the actual 'use' buttons
    global energy_use
    energy_use=Button(frame2,text='Use',command=energy_cmd)
    energy_use.place(relx=0.45,rely=0.26,anchor=CENTER)

    global steroids_use
    steroids_use=Button(frame2,text='Use',command=steroid_cmd)
    steroids_use.place(relx=0.45,rely=0.53,anchor=CENTER)

    global efficiency_use
    efficiency_use=Button(frame2,text='Use',command=efficiency_cmd)
    efficiency_use.place(relx=0.45,rely=0.81,anchor=CENTER)
    
    global demigod_use
    demigod_use=Button(frame2,text='Use',command=demigod_cmd)
    demigod_use.place(relx=0.95,rely=0.26,anchor=CENTER)
    
    global god_use
    god_use=Button(frame2,text='Use',command=god_cmd)
    god_use.place(relx=0.95,rely=0.53,anchor=CENTER)

    global saiyan_use
    saiyan_use=Button(frame2,text='Use',command=saiyan_cmd)
    saiyan_use.place(relx=0.95,rely=0.81,anchor=CENTER)
    
def lottery():
    global hand
    if hand>=2000:
        hand-=2000
        money_won=randrange(1000,10000,100)
        hand+=money_won
        if money_won>=2000:
            lot_result.config(text='You have won '+str(money_won)+'!')
        else:
            lot_result.config(text='You have lost '+str(2000-money_won))
        lot_but.config(state=DISABLED)
    else:
        lot_result.config(text='You don\'t have\nenough money!')
    window.after(10000,lambda: lot_result.config(text=''))
    window.after(60000,lambda:lot_but.config(state=NORMAL))
    money_hand.config(text="Money in hand : "+"{:,}".format(hand))

def leaderboard():
    def on_closing_lb():
        lb_open.config(state=NORMAL)
        lb.destroy()
    global lb
    lb_open.config(state=DISABLED)
    lb=Toplevel()
    lb.title("Leaderboards")
    lb.geometry("300x300")
    lb.resizable(False,False)
    lb.configure(bg='#3d3d3d')
    lb.protocol("WM_DELETE_WINDOW", on_closing_lb)
    lb_title_label=Label(lb,text='Leaderboards',font=("Arial Bold",15),fg = 'white', bg='#3d3d3d').place(relx=0.5,rely=0.075,anchor=CENTER)
    lb_label=Label(lb,text='',justify=LEFT,font=("Arial Bold",12),fg = 'white', bg='#3d3d3d')
    lb_label.place(relx=0.28,rely=0.5,anchor=CENTER)
    dbcursor.execute('select username,(hand+bank) as money from players order by (hand+bank)desc')
    data=dbcursor.fetchmany(10)
    string=''
    count=1
    for i in data:
        string+=str(count)+') '+i[0]+' - '+str(i[1])+'$'+'\n'
        count+=1
    lb_label.config(text=string)

#lottery stuff
lot_frame=Frame(window,width=180,height=150, bg='#272b28')
lot_frame.place(relx=0.75,rely=0.53,anchor=CENTER)
lot_pic=image_import('lottery_logo.png',40,40)
lot_title=Label(lot_frame,text="Lottery Draw",font=("Arial Bold",15),bg='#272b28',image=lot_pic,compound=LEFT,fg = 'white')
lot_title.place(relx=0.5,rely=0.16,anchor=CENTER)
lot_but=Button(lot_frame,text='Buy lottery ticket\nfor 2000$', bg='#3d3d3d', fg='white', command=lottery)
lot_but.place(relx=0.5,rely=0.45,anchor=CENTER)
lot_result=Label(lot_frame, text='Results appear here',bg='#272b28',fg='white', font=("Arial Bold",12))
lot_result.place(relx=0.5,rely=0.76,anchor=CENTER)
#Shows amount of money in hand and bank    
myWallet=Label(window,text="My Wallet:",font=("Arial Bold",15), bg = '#3d3d3d', fg = 'white')
myWallet.place(relx=0.02,rely=0.0,anchor=NW)

money_hand=Label(window,text="Money in hand : "+"{:,}".format(hand),font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white')
money_hand.place(relx=0.02,rely=0.07,anchor=NW)

money_bank=Label(window,text="Money in bank : "+"{:,}".format(bank),font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white')
money_bank.place(relx=0.02,rely=0.12,anchor=NW)

#Work button and picture
global work_pic
work_pic=image_import("work_pic.png",30,30)
global work
work=Button(window,text="Work",bg="#46b9f2",fg="dark blue",command=workcmd,image=work_pic,compound=LEFT,font=("Arial",20))
work.place(relx=0.14,rely=0.3,anchor=CENTER)

#Deposit stuff and picture
dep_pic=image_import("Deposit_logo.png",40,40)

depositall=Button(window,text="Deposit All ",bg="#bbbebf",fg="black",command=depall,image=dep_pic,compound=LEFT,font=("Arial",9))
depositall.place(relx=0.14,rely=0.46,anchor=CENTER)

depositamt=Button(window,text="Confirm",bg="light green",fg="black",command=depamt,font=("Arial",9), height = 1, width = 7)
depositamt.place(relx=0.45,rely=0.56,anchor=CENTER)

deposit=Entry(window,width=7,  bg = '#c4c3c0')
deposit.place(relx=0.33,rely=0.56,anchor=CENTER)
deposit.bind('<Return>', depamt)

depositlabel=Label(window,text="Or deposit amount:",font=("Arial Bold",10),  bg = '#3d3d3d', fg = 'white')
depositlabel.place(relx=0.15,rely=0.56,anchor=CENTER)

#Withdraw stuff and picture
with_pic=image_import("Withdraw_logo.png",40,40)
withdrawall=Button(window,text="Withdraw All ",bg="#bbbebf",fg="black",command=withall,image=with_pic,compound=LEFT,font=("Arial",9))
withdrawall.place(relx=0.14,rely=0.71,anchor=CENTER)

withdrawamt=Button(window,text="Confirm",bg="light green",fg="black",command=withamt,font=("Arial",9), height = 1, width = 7)
withdrawamt.place(relx=0.48,rely=0.80,anchor=CENTER)

withdraw=Entry(window,width=7,  bg = '#c4c3c0')
withdraw.place(relx=0.36,rely=0.80,anchor=CENTER,)
withdraw.bind('<Return>', withamt)

withdrawlabel=Label(window,text="Or withdraw amount:",font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white')
withdrawlabel.place(relx=0.172,rely=0.80,anchor=CENTER)

#for shop
shop_pic=image_import("shop_logo.png",40,40)

shop_open=Button(window,text="Shop",command=shopbutton,image=shop_pic,compound=LEFT,font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white')
shop_open.place(relx=0.71,rely=0.25,anchor=CENTER)

#leaderboards
global lb_pic
lb_pic=image_import('leaderboards.png',40,40)
lb_open=Button(window,text="Leaderboards",command=leaderboard,image=lb_pic,compound=LEFT,font=("Arial Bold",10), bg = '#3d3d3d', fg = 'white')
lb_open.place(relx=0.71,rely=0.1,anchor=CENTER)

#for quitting game
quit_game_but = Button(window, text = "Quit\ngame", command=quit_game, height=3, width=6, bg='red', fg = 'white')
quit_game_but.place(relx = 0.9, rely = 0)

window.withdraw()
window.mainloop()   
