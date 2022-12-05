from tkinter import messagebox
from main_func import *
from tkinter.ttk import Combobox
import tkinter as tk
from tkinter import *



class Full_autopilot_menu():
    def __init__(self):
        self.window = Tk()
        self.window.title("FULL AUTOPILOT")
        self.window.geometry('440x100')

        self.f_right = Frame(self.window)
        self.f_mid = Frame(self.window)
        self.f_left = Frame(self.window)

        self.f_left.pack(side=LEFT, padx=5, pady=5, expand=True)
        self.f_mid.pack(side=LEFT, padx=5, pady=5, expand=True)
        self.f_right.pack(side=LEFT, padx=5, pady=5, expand=True)

        self.mode = Combobox(self.f_right)
        self.mode['values'] = ("Строгий режим", "Свободный режим")
        self.mode.current(0)  # установите вариант по умолчанию
        self.mode.pack(side=TOP, padx=5, pady=5, expand=True)

        self.draw_mode = Combobox(self.f_right)
        self.draw_mode['values'] = ("Отрисовка", "Быстрее")
        self.draw_mode.current(0)  # установите вариант по умолчанию
        self.draw_mode.pack(side=TOP, padx=5, pady=5, expand=True)

        self.lbl_h1 = Label(self.f_left, text="Высота подъема")
        self.lbl_d2 = Label(self.f_left, text="Время работы двигателя")
        self.lbl_a2 = Label(self.f_left, text="Угол поворота")

        self.lbl_h1.pack(side=TOP, padx=5, pady=5, expand=True)
        self.lbl_d2.pack(side=TOP, padx=5, pady=5, expand=True)
        self.lbl_a2.pack(side=TOP, padx=5, pady=5, expand=True)

        self.input_h1 = Entry(self.f_mid, width=20)
        self.input_d2 = Entry(self.f_mid, width=20)
        self.input_a2 = Entry(self.f_mid, width=20)

        self.input_h1.pack(side=TOP, padx=5, pady=5, expand=True)
        self.input_d2.pack(side=TOP, padx=5, pady=5, expand=True)
        self.input_a2.pack(side=TOP, padx=5, pady=5, expand=True)

        self.btn = Button(self.f_right, text="Создать автопилот", command=self.compile_full)
        self.btn.pack(side=TOP, padx=5, pady=5, expand=True)


    def compile_full(self):
        h1 = self.input_h1.get()
        a2 = self.input_a2.get()
        d2 = self.input_d2.get()
        if self.mode.get() == "Свободный режим": FREE_MOD = True
        else: FREE_MOD = False
        if self.draw_mode.get() == "Отрисовка": DRAW = True
        else: DRAW = False

        try:
            get_autopilot_and_staff(float(h1), float(a2), float(d2), FREE_MOD=FREE_MOD, DRAW=DRAW, ORBIT_START=False)
        except ValueError:
            messagebox.showinfo('Ошибка', 'Ошибка ввода')




class Orbit_autopilot_menu():
    def __init__(self):
        self.window = Tk()
        self.window.title("FULL AUTOPILOT")
        self.window.geometry('550x65')




        self.draw_mode = Combobox(self.window)
        self.draw_mode['values'] = ("Отрисовка", "Быстрее")
        self.draw_mode.current(0)  # установите вариант по умолчанию
        self.draw_mode.pack(side=LEFT, padx=5, pady=5, expand=True)

        self.lbl_h1 = Label(self.window, text="Высота LEO")


        self.lbl_h1.pack(side=LEFT, padx=5, pady=5, expand=True)

        self.input_h1 = Entry(self.window, width=20)


        self.input_h1.pack(side=LEFT, padx=5, pady=5, expand=True)


        self.btn = Button(self.window, text="Создать автопилот", command=self.compile_orbit)
        self.btn.pack(side=LEFT, padx=5, pady=5, expand=True)

    def compile_orbit(self):
        h1 = self.input_h1.get()
        a2 = 0
        d2 = 0
        if self.draw_mode.get() == "Отрисовка": DRAW = True
        else: DRAW = False

        try:
            get_autopilot_and_staff(float(h1), float(a2), float(d2), FREE_MOD=True, DRAW=DRAW, ORBIT_START=True)
        except ValueError:
            messagebox.showinfo('Ошибка', 'Ошибка ввода')



class Menu():
    def __init__(self):
        self.window = Tk()
        self.window.title("PRI-MAT   01   ---   AUTOPILOT")
        self.window.geometry('400x200')

        self.btn1 = Button(self.window, text="Создать полный автопилот", command=self.full_autopilot)
        self.btn2 = Button(self.window, text="Создать орбитальный автопилот", command=self.orbit_autopilot)

        self.btn1.pack(padx=40, pady=20, expand=True, fill=tk.BOTH)
        self.btn2.pack(padx=40, pady=20, expand=True, fill=tk.BOTH)

        self.window.mainloop()
    def full_autopilot(self):
        self.window.destroy()
        full_window = Full_autopilot_menu()
    def orbit_autopilot(self):
        self.window.destroy()
        orbit_window = Orbit_autopilot_menu()


if __name__ == "__main__":
    main = Menu()