import contact as aict
import file_io as fio
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import simpledialog as sd
from markdown2 import Markdown
import tkhtmlview as tkh
import os

PATH = "/".join(__file__.split("/")[:-1:])
conf = fio.get_conf_file()#basically everything
model_file_endings = ["gguf"]
chat_models = []
chats = []#names
ver = "PAWMA 1.1 GUI"

version_info = f"""{ver}
Developed by IMG_25522.
Terms of Use: As continue using Pawma(Including all the features), you agree with:
    1. Pawma is not a commercial software, you may not use Pawma for commercial activities;
    2. AI(Artificial Intelligence) could make mistakes, and as the Pawma team is not the provider of the AIs, the Pawma team takes NO responsibility to the loss of profits (including but not limited by: being asked by the teacher to rewrite homework, being called to the honor concil) by using AI in Pawma;
    3. You(The user), confirm that Pawma and the Pawma team have NOT encouraging nor suggesting misuse of AI technology;
Contact Email:
    29zhang@heathwood.org
Redistribution License:
    GNU General Public License v3.0 or later
Date:
    09/24/2025

Update info:
    1.1_09252025 : 
        Fixed the uncomfortable way of loading (Before, all models are loaded at thebeginning, even they may never be used, that will takes huge amount of time. And now they are loaded when ever you call them the 1st time.)

"""

print("PATH:",PATH,"conf:",conf)

def init():
    global chats,chat_models
    loc_models = os.listdir("./models")
    print(loc_models)
    for i in loc_models:
        loc_model_path = "./models/"+i
        if(loc_model_path not in conf["models"] and i.split(".")[-1] in model_file_endings):
            conf["models"].append(loc_model_path)
    chats = list(conf["chats"].keys())
    print("Models to load:",conf["models"])
    chat_models = [i for i in conf["models"]]#when using, change the using model to aict.chat(i) (for now they are just strings)

def md2ht(thing):
    md2html = Markdown()
    return md2html.convert(thing)

class html_box_list(tkh.HTMLScrolledText):
    def __init__(self,master,width,background,fon):
        super().__init__(master,width=width,background=background,fon=fon)
        self.master = master
        self.html = ""
        self.items = []
        self.font = fon
        self.style = {"assistant":"background-color:white;color:black","user":"background-color:black;color:white"}
    def set_items(self,thing=[]):
        self.items = thing#[{"role":"user","content":"blah"},{SAME THING}]
        self.set_html("")
        to_put = ""
        for i in range(len(self.items)):
            to_put += "<div class=\"%s\" style=\"%s\">%s:%s</div>\n"%(self.items[i]["role"],self.style[self.items[i]["role"]],self.items[i]["role"],md2ht(self.items[i]["content"]))
        self.html = to_put
        self.set_html(self.html)
    def add_item(self,thing={}):
        thing["content"] = md2ht(thing["content"])
        self.html += "<div class=\"%s\" style=\"%s\">%s:%s</div>\n"%(thing["role"],self.style[thing["role"]],thing["role"],md2ht(thing["content"]))
        self.set_html(self.html)
        self.items.append(thing)
            


def put_ui(win:tk.Tk):
    global model_select
    model_select = ttk.Combobox(win,values=[i.split("/")[-1] for i in conf["models"]])
    model_select.pack()
    return model_select

class main_box(tk.Frame):
    def __init__(self, master=None,fon=("Helvetica",14)):
        tk.Frame.__init__(self, master)
        self.master = master
        self.myfont = font.Font(family=fon[0], size=fon[1])
        self.init_window()
        self.selected_chat = ""

    def init_window(self):
        self.pack(fill=tk.BOTH, expand=1)

        self.chat_select = tk.Listbox(self,width="20",height="20",font=self.myfont)
        self.chat_select.grid(column=0,row=0)
        for i in chats:
            self.chat_select.insert(0,i)
        self.chat_select.insert(0,"Delete Chat (-)")
        self.chat_select.insert(0,"New Chat (+)")
        self.chat_select.bind("<<ListboxSelect>>", self.on_chat_select)

        self.outputbox = html_box_list(self,width=50,background="black",fon=self.myfont)
        self.outputbox.grid(column=1,row=0,columnspan=2,sticky="nesw")
        self.outputbox.fit_height()
        self.outputbox.set_items()

        self.info_lb = tk.Label(self,text="Chat Anything:")
        self.info_lb.grid(column=0,row=1)

        self.columnconfigure(1,weight=2)
        self.entry = tk.Entry(self)
        self.entry.grid(column=1,row=1,sticky="ew")

        self.enter_bt = tk.Button(self,text="Send",command=self.send_msg)
        self.enter_bt.grid(column=2,row=1)

        self.info_label = tk.Label(self,text=version_info,wraplength=520,justify=tk.LEFT,fg="gray")
        self.info_label.grid(column=0,columnspan=3,row=2)

        print(self.outputbox.html)
        
    def on_chat_select(self,event):
        run = False
        if(event == "Have to do"):#莫须有的理由（主动调用时，请敲“Have to do”）
            run = True
            selected_thing = self.selected_chat
        elif isinstance(event.widget,tk.Listbox):#真的有事（点击）
            run = True
            selected_thing = self.chat_select.get(self.chat_select.curselection()[0])
        if run:
            print("!!!!!!!")
            if selected_thing == "New Chat (+)":
                new_name = sd.askstring("?","Name of the New chat?")
                if new_name:
                    conf["chats"][new_name] = []
                    self.outputbox.set_items(conf["chats"][new_name])
                    self.chat_select.insert(tk.END,new_name)
                    chats.append(new_name)
            elif selected_thing == "Delete Chat (-)":
                to_del = ask_pop_list_selection(self,"Delete Chat...","Choose a chat to delete",list(conf["chats"].keys()))
                print("delete:%s"%(to_del))
                if(to_del):
                    del conf["chats"][to_del]
                    entry_items = self.chat_select.get(0,tk.END)
                    for i in range(len(entry_items)):
                        if(entry_items[i] == to_del):
                            self.chat_select.delete(i,i+1)
            elif self.chat_select.curselection():
                self.outputbox.set_items(conf["chats"][selected_thing])
                self.selected_chat = selected_thing+""
                self.outputbox.see(tk.END)
    def send_msg(self):
        print(conf["chats"])
        if model_select.current() != -1:
            if(isinstance(chat_models[model_select.current()],str)):
                print("LOAD MODEL:",chat_models[model_select.current()])
                chat_models[model_select.current()] = aict.Chat(chat_models[model_select.current()])
            chat_models[model_select.current()].set_hist(conf["chats"][self.selected_chat])
            thing = self.entry.get()
            ai_res = chat_models[model_select.current()].chat(thing)
            self.entry.delete(0,tk.END)
            print("Before adding:",conf["chats"][self.selected_chat])
            conf["chats"][self.selected_chat].append({"role":"user","content":thing})
            conf["chats"][self.selected_chat].append({"role":"assistant","content":ai_res})
            self.on_chat_select(event="Have to do")
        

class ListSelectDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, options):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)  # Makes the dialog appear on top of the parent
        self.grab_set()         # Makes the dialog modal

        self.result = None
        self.selected_value = tk.StringVar(self)

        tk.Label(self, text=prompt).pack(pady=10)

        self.combobox = ttk.Combobox(self, textvariable=self.selected_value, values=options)
        self.combobox.pack(pady=5)
        # if options:
        #     self.combobox.set(options[0]) # Set initial selection

        tk.Button(self, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=10, pady=10)

        self.wait_window(self) # Wait for the dialog to close

    def on_ok(self):
        self.result = self.selected_value.get()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

def ask_pop_list_selection(parent, title, prompt, options):
    dialog = ListSelectDialog(parent, title, prompt, options)
    return dialog.result

def on_main_closing():
    fio.write_conf_file(conf)
    wd.destroy()

def main():
    global wd
    init()
    wd = tk.Tk()
    wd.geometry("690x690")
    wd.title(ver)
    put_ui(wd)
    main_box(wd).pack()
    wd.protocol("WM_DELETE_WINDOW", on_main_closing)
    wd.mainloop()

if __name__ == "__main__":
    main()
    
    