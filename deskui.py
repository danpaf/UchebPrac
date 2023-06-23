import pprint
import re
import subprocess
import tkinter as tk
from tkinter import messagebox, BOTH, END

import hues
from peewee import *

from tkinter import ttk
import main
import settings

from models import User, AccessLog

data = []


class MainMenuUi:
    def __init__(self, window):
        self.window = window
        self.window.title('Main Menu')

        
        menu_label = tk.Label(window, text='Welcome to the Main Menu!')
        menu_label.pack()
        settings_button = ttk.Button(self.window, text='Settings', command=self.option6)
        settings_button.pack(side=tk.LEFT)

        
        button_frame = tk.Frame(window)
        button_frame.pack()

        
        button1 = tk.Button(button_frame, text='Group logs by IP address', command=self.option1)
        button1.pack(side=tk.LEFT)

        button2 = tk.Button(button_frame, text='Group logs by date', command=self.option2)
        button2.pack(side=tk.LEFT)

        button3 = tk.Button(button_frame, text='List API routes', command=self.option3)
        button3.pack(side=tk.LEFT)

        button4 = tk.Button(button_frame, text='Get logs by IP', command=self.option4)
        button4.pack(side=tk.LEFT)

        button5 = tk.Button(button_frame, text='Flask start', command=self.option5)
        button5.pack(side=tk.LEFT)

        columns = ("ipaddress", "date", "httpmethod", "responsecode", "someint")

        tree = ttk.Treeview(columns=columns, show="headings")
        tree.pack(fill=BOTH, expand=1)

        tree.column("#0", stretch=tk.NO)  
        for column in ("ipaddress", "date", "httpmethod", "responsecode", "someint"):
            tree.column(column, stretch=tk.YES)  

        # определяем заголовки
        tree.heading("ipaddress", text="IP адрес")
        tree.heading("date", text="Дата")
        tree.heading("httpmethod", text="Метод")
        tree.heading("responsecode", text="Ответ код")
        tree.heading("someint", text="Н-ое число")

        try:
            for log in AccessLog.select():
                ip = log.ip_address
                date = log.date
                httpmethod = log.http_method
                responsecode = log.response_code
                someint = log.some_int
                data.append({
                    "ip": ip,
                    "date": date,
                    "httpmethod": httpmethod,
                    "responsecode": responsecode,
                    "someint": someint
                })
        except Exception as e:
            print(f"Error fetching logs: {e}")

        
        for datas in data:
            tree.insert("", END, values=(
            datas["ip"], datas["date"], datas["httpmethod"], datas["responsecode"], datas["someint"]))

    def option1(self):
        print('Selected Option 1')
        try:
            with main.app.app_context():
                result = main.get_logs_group_by_ip()
                logs = result.json

                tree = ttk.Treeview(columns=("ipaddress", "count"), show="headings")
                tree.pack(fill=BOTH, expand=1)

                tree.heading("ipaddress", text="IP адрес")
                tree.heading("count", text="Количество")

                for log in logs:
                    tree.insert("", END, values=(log["ip_address"], log["count"]))
        except Exception as e:
            print(f"Error grouping logs by IP address: {e}")

    def option2(self):
        print('Selected Option 2')
        try:
            with main.app.app_context():
                result = main.get_logs_group_by_date()
                logs = result.json

                tree = ttk.Treeview(columns=("date", "count"), show="headings")
                tree.pack(fill=BOTH, expand=1)

                tree.heading("date", text="Дата")
                tree.heading("count", text="Количество")

                for log in logs:
                    tree.insert("", END, values=(log["date"], log["count"]))
        except Exception as e:
            print(f"Error grouping logs by date: {e}")

    def option3(self):
        print('Selected Option 3')
        try:
            with main.app.app_context():
                result = main.get_api_routes()
                routes = result.json

                tree = ttk.Treeview(columns=("route", "description"), show="headings")
                tree.pack(fill=BOTH, expand=1)

                tree.heading("route", text="Маршрут")
                tree.heading("description", text="Описание")

                for route in routes:
                    tree.insert("", END, values=(route["route"], route["description"]))
        except Exception as e:
            print(f"Error listing API routes: {e}")

    def option4(self):
        print('Selected Option 4')

        
        ip_window = tk.Toplevel(self.window)
        ip_window.title('Enter IP address')

        
        ip_label = tk.Label(ip_window, text='Enter IP address: ')
        ip_label.pack()

        
        ip_entry = tk.Entry(ip_window)
        ip_entry.pack()

        
        def validate_input(event):
            ip_pattern = r'^\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}$'
            ip = ip_entry.get()
            if re.match(ip_pattern, ip) is None:
                ip_entry.config(fg='red')
            else:
                ip_entry.config(fg='black')

        ip_entry.bind('<KeyRelease>', validate_input)


        
        def get_by_ip():
            logs = []
            ip_address = ip_entry.get()
            try:
                for log in AccessLog.select().where(AccessLog.ip_address == ip_address):
                    ip = log.ip_address
                    date = log.date
                    httpmethod = log.http_method
                    logs.append({
                        "ip": ip,
                        "date": date,
                        "httpmethod": httpmethod,
                    })

                tree = ttk.Treeview(columns=("ipaddress", "date", "method"), show="headings")
                tree.pack(fill=BOTH, expand=1)

               
                tree.heading("ipaddress", text="IP адрес")
                tree.heading("date", text="Дата")
                tree.heading("method", text="Метод")

                
                for logged in logs:
                    tree.insert("", END, values=(logged["ip"], logged["date"], logged["httpmethod"]))
            except Exception as e:
                print(f"Error fetching logs by IP address: {e}")

        ok_button = tk.Button(ip_window, text='OK', command=get_by_ip)
        ok_button.pack()

        ip_window.mainloop()

    def option5(self):
        print('Selected Option 5')
        try:
            self.window.destroy()
            main.app.run()
        except Exception as e:
            print(f"Error starting Flask: {e}")

    def option6(self):
        print('Selected Option 6')

        def open_settings(self):
            try:
                with open('settings.py', 'r') as f:
                    settings = f.read()

                
                subprocess.call(['notepad.exe', 'settings.py'])
            except Exception as e:
                print(f"Error opening settings file: {e}")

        open_settings(self.window)


class LoginUi:
    def __init__(self, window):
        self.window = window
        self.window.title('Login Form')

        
        username_label = tk.Label(window, text='Username')
        username_label.pack()
        self.username_entry = tk.Entry(window)
        self.username_entry.pack()

        password_label = tk.Label(window, text='Password')
        password_label.pack()
        self.password_entry = tk.Entry(window, show='*')
        self.password_entry.pack()

        login_button = tk.Button(window, text='Login', command=self.login)
        login_button.pack()

    def authenticate(self, username, password):
        try:
            user = User.get(User.login == username, User.password == password)
            return True
        except User.DoesNotExist:
            return False

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.authenticate(username, password):
            messagebox.showinfo('Login', 'Authentication successful')

            main_menu = MainMenuUi(window=self.window)
        else:
            messagebox.showerror('Login', 'Invalid username or password')


def run_app():
    window = tk.Tk()
    window.geometry(settings.resolution)
    login_ui = LoginUi(window)

    window.mainloop()


