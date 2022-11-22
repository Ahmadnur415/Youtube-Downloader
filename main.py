import os
import re
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from threading import Thread
from pytube import YouTube


class AsyncDownload(Thread):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    def run(self):
        try:
            name = self.stream.title
            if self.stream.type == "audio":
                name += f" ({self.stream.abr}).mp3"
            else:
                name += f" ({self.stream.resolution}).mp4"
            filename = re.sub(r'[:|$|*|"|\\|<|>|?|/]', r'', name)
            self.stream.download(dirpath.get(), filename)
        except:
            messagebox.showerror("ERROR", "Connection Problem !")
        else:
            os.startfile(dirpath.get())
            filepath = dirpath.get() + "/" + filename
            messagebox.showinfo('Successfully Downloaded.', f"Your YouTube Vidoe Downloaded Successfully at {filepath!r}")


def open_folder():
    pre_path = dirpath.get()
    dirpath.set(askdirectory(initialdir=dirpath.get()))
    if not os.path.isdir(dirpath.get()):
        dirpath.set(pre_path)

def clear_widget():
    """ menghancurkan semua widget yang sudah di tambahkan """
    for widget in body_page.winfo_children():
        widget.destroy()
    """ menghapus semua informasi """
    for text in info_video.values():
        if isinstance(text, ScrolledText):
            text["state"] = NORMAL
            text.delete("1.0", END)
            text["state"] = DISABLED
        else:
            text.set("")

def append(stream, no):
    """ menambahkan stream frame ke dalam download page """
    frame = Frame(body_page)
    frame.grid(row=no, column=0, sticky=NSEW)

    mime_type = stream.mime_type.capitalize()
    quality = stream.resolution if stream.type == "video" else stream.abr
    size = round(stream.filesize / 1048576, 1)
    audio = "Audio Only"
    
    if stream.type == "audio":
        mime_type = mime_type.replace("mp4", "mp3")

    if stream.includes_audio_track and stream.type == "video": 
        audio = ", Include Audio"

    elif not stream.includes_audio_track and stream.type == "video": 
        audio = ", No Audio (Video Only)"

    Label(
        frame,
        text=f"{no}. {mime_type} file, Quality {quality}, Size {size} MB {audio}"
    ).grid(row=0, column=0, sticky=EW, padx=10)

    Button(frame, text="Download", command=lambda: AsyncDownload(stream).start()).grid(row=1, column=0, sticky=W, padx=10)


def get_video():
    """ mengambil video dari url_var """
    try:
        clear_widget()
        btn_search["state"] = DISABLED
        video_object = YouTube(url_var.get())
        streams_object = video_object.streams
    except:
        messagebox.showerror("Error", "Url not found")
    else:
        """ update info video"""
        info_video["title"].set(video_object.title)
        info_video["view"].set(str(video_object.views))
        info_video["length"].set(f"{round(video_object.length / 60, 2)}".replace(".", ":"))
        info_video["author"].set(video_object.author)
        info_video["description"]["state"] = NORMAL
        info_video["description"].insert(END, video_object.description)
        info_video["description"]["state"] = DISABLED

        """ mengambil video dan audio dari streams """
        streams = list(streams_object.filter(progressive=True))
        streams += list(streams_object.filter(only_audio=True, file_extension="mp4"))

        for i, stream in enumerate(streams):
            append(stream, i+1)

    finally:
        btn_search["state"] = NORMAL

""" setup window """
window = Tk()
window.geometry("500x390")
window.title("YT Downloader")
window.resizable(0, 0)
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

url_var = StringVar()
dirpath = StringVar(value=os.path.dirname(os.path.realpath(__file__)))
info_video = {
    "title": StringVar(),
    "view": StringVar(),
    "length": StringVar(),
    "author": StringVar()
}


""" membuat Header """
header = Frame(window)
header.columnconfigure(1, weight=1)
header.grid(row=0, column=0, sticky=EW, padx=10, pady=10)

Label(header, text="URL").grid(row=0, column=0, sticky=W, padx=(0, 10))
Entry(header, textvariable=url_var).grid(row=0, column=1, sticky=EW)

btn_search = Button(header, text="Search", command=lambda : Thread(target=get_video).start())
btn_search.grid(row=0, column=2, sticky=E, padx=(10, 0))

""" membuat Body yang berupa notebook """
body = Notebook(window)
body.grid(row=1, column=0, sticky=NSEW, padx=10, pady=10)

""" mengisi notebook dengan frame info """
info_page = Frame(body)
info_page.pack(fill=BOTH, anchor="center")
info_page.columnconfigure(1, weight=1)
body.add(info_page, text="Info")

""" membuat label informasi dari video """
Label(info_page, text="Title", anchor=W).grid(row=0, column=0, sticky=W)
Label(info_page, text="View", anchor=W).grid(row=1, column=0, sticky=W)
Label(info_page, text="Length", anchor=W).grid(row=2, column=0, sticky=W)
Label(info_page, text="Author", anchor=W).grid(row=3, column=0, sticky=W)
Label(info_page, text="Description", anchor=NW).grid(row=4, column=0, sticky=W)

""" warp text untuk title """
lbl_title = Label(info_page, width=50, justify=LEFT, text="aaaaaaaaaaaaaa", textvariable=info_video["title"])
lbl_title.grid(row=0, column=1, sticky=EW)
lbl_title.bind('<Configure>', lambda e: lbl_title.config(wraplength=lbl_title.winfo_width()))

Label(info_page, justify=LEFT, text="Jumlah View", textvariable=info_video["view"]).grid(row=1, column=1, sticky=EW)
Label(info_page, justify=LEFT, text="InI Panjang dari Sebuah video", textvariable=info_video["length"]).grid(row=2, column=1, sticky=EW)
Label(info_page, justify=LEFT, text="Ini Nama Channel", textvariable=info_video["author"]).grid(row=3, column=1, sticky=EW)
info_video["description"] = ScrolledText(info_page, height=12, state=DISABLED, wrap=NONE)
info_video["description"].grid(row=4, column=1, sticky=NSEW)


""" Download Page """
download_page = Frame(body)
download_page.pack(fill=BOTH)
body.add(download_page, text="Download")

""" Header dari halaman download """
header_page = Frame(download_page)
header_page.columnconfigure(1, weight=1)
header_page.pack(fill=X, padx=5, pady=5)

""" Folder """
Label(header_page, text="Folder").grid(row=0, column=0, sticky=W)
Entry(header_page, textvariable=dirpath, state=DISABLED).grid(row=0, column=1, sticky=EW, padx=10)
Button(header_page, text="Open Folder", command=open_folder).grid(row=0, column=2, sticky=E)
Separator(download_page, orient=HORIZONTAL).pack(fill=X)

""" body dari halaman download """
body_page = Frame(download_page)
body_page.pack(anchor=W)

window.mainloop()