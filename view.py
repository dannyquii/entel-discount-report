from tkinter import filedialog as FileDialog
from tkinter import *
from tkinter import StringVar
from discount_report import make_reports
import threading


def interrupt(report_thread, label_text, button):
    report_thread._stop()
    label_text.set('Seleccione el directorio de trabajo')
    button.configure(text='Abrir carpeta', command=lambda: process_workpad(label_text, button))
    pass


def again(label_text, button):
    label_text.set('Seleccione el directorio de trabajo')
    button.configure(text='Abrir carpeta', command=lambda: process_workpad(label_text, button))


def process_workpad(label_text, button):
    work_path = FileDialog.askdirectory(title="Seleccione el directorio de trabajo")

    if not work_path:
        return

    report_thread = threading.Thread(
        target=make_reports,
        args=(work_path,)
    )

    report_thread.start()

    label_text.set("Proceando archivos...")
    button.configure(text='Cancelar', command=lambda: interrupt(report_thread, label_text, button))

    report_thread.join()

    label_text.set("Proceso finalizado")
    button.configure(text='Volver a comenzar', command=lambda: again(label_text, button))


def view():
    window = Tk()
    window.resizable(0, 0)

    view_head = Frame(window, borderwidth=48, bg='white')
    view_head.pack(fill=BOTH, expand=1)
    window.title('Discount report app by Carol')
    window.geometry('360x480')

    label_text = StringVar()
    label_text.set('Seleccione el directorio de trabajo')

    Label(
        view_head,
        textvariable=label_text,
        bg='white',
        fg='#333333',
        font='Serif 11 bold'
    ).pack(fill=X, expand=1)

    button = Button(
        view_head,
        text='Abrir carpeta',
        bg='blue',
        fg='white',
        font='Serif 11 bold'
    )

    button.pack(fill=X, expand=0)
    button.configure(command=lambda: process_workpad(label_text, button))

    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    window.geometry('%dx%d+%d+%d' % (360, 480, (ws / 2) - 180, (hs / 2) - 240))

    window.mainloop()
    return


if __name__ == '__main__':
    view()
