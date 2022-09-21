import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
            filepath = dirpath.get() + "\\" + filename
            messagebox.showinfo('Successfully Downloaded.', f"Your YouTube Vidoe Downloaded Successfully at {filepath!r}")


window = tk.Tk()
window.geometry("500x390")
window.title("YT Downloader")
window.resizable(0, 0)
url_var = tk.StringVar()
video_object = None
streams_object = None
RealPath = os.path.dirname(os.path.realpath(__file__))
dirpath = tk.StringVar(value=RealPath)
threads = []
info_video = {
    "title": tk.StringVar(),
    "view": tk.StringVar(),
    "length": tk.StringVar(),
    "author": tk.StringVar(),
    "description": tk.StringVar()
}


def open_folder():
    dirpath.set(filedialog.askdirectory(initialdir=dirpath.get()))
    if not os.path.isdir(dirpath.get()):
        dirpath.set(RealPath)


def clear_widget():
    global video_object, streams_object
    video_object = None
    streams_object = None
    # destroy children
    for widget in body_download_page.winfo_children():
        widget.destroy()
    # clear info
    info_video["title"].set('')
    info_video["view"].set('')
    info_video["length"].set('')
    info_video["author"].set('')
    info_video["description"]["state"] = tk.NORMAL
    info_video["description"].delete("1.0", "end")
    info_video["description"]["state"] = tk.DISABLED
    threads.clear()


def update():
    try:
        btn_search["state"] = tk.DISABLED
        clear_widget()
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
        info_video["description"]["state"] = tk.NORMAL
        info_video["description"].insert(tk.END, video_object.description)
        info_video["description"]["state"] = tk.DISABLED

        """ set vidoes and audio """
        no = 1
        for stream in streams_object.filter(progressive=True):
            _new_thread = Thread(target=frame_stream, kwargs={'stream': stream, 'no': no})
            threads.append(_new_thread)
            _new_thread.start()
            no += 1
        # audio
        for stream in streams_object.filter(only_audio=True, file_extension="mp4"):
            _new_thread = Thread(target=frame_stream, kwargs={'stream': stream, 'no': no})
            threads.append(_new_thread)
            _new_thread.start()
            no += 1

    finally:
        btn_search["state"] = tk.NORMAL


def frame_stream(stream, no):
    frame = ttk.Frame(body_download_page)
    label = ttk.Label(frame)

    mime_type = stream.mime_type.capitalize()
    if stream.type == "audio":
        mime_type = mime_type.replace("mp4", "mp3")

    quality = stream.resolution if stream.type == "video" else stream.abr
    size = round(stream.filesize / 1048576, 1)
    other = "Audio Only"
    if stream.includes_audio_track and stream.type == "video": 
        other = ", Include Audio"
    if not stream.includes_audio_track and stream.type == "video": 
        other = ", No Audio (Video Only)"

    label["text"] = f"{no}. {mime_type} file, Quality {quality}, Size {size} MB {other}"
    btn = ttk.Button(frame, text="Download", command=lambda: handle_download(stream))

    # set label, button, dan frame
    label.grid(row=0, column=0, sticky=tk.EW, padx=10)
    btn.grid(row=1, column=0, sticky=tk.W, padx=10)
    frame.grid(row=no, column=0, sticky=tk.NSEW)


def handle_download(stream):
    download = AsyncDownload(stream)
    download.start()


def handle_update():
    thread = Thread(target=update)
    thread.start()


# mambuat kepala
header = ttk.Frame(window)
header.columnconfigure(0, weight=1)
header.columnconfigure(1, weight=10)
header.columnconfigure(2, weight=1)
header.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
# labal url
lbl_url = ttk.Label(header, text="URL")
lbl_url.grid(row=0, column=0, sticky=tk.W)
# membuat entry untuk url
entry_url = ttk.Entry(header, textvariable=url_var, width=55)
entry_url.grid(row=0, column=1, sticky=tk.EW)
# menambahkan tombol cari
btn_search = ttk.Button(header, text="Search", command=handle_update)
btn_search.grid(row=0, column=2, sticky=tk.E)

# mambuat notebook
notebook = ttk.Notebook(window, height=300)
notebook.grid(row=1, column=0, sticky=tk.NSEW, padx=10, pady=10)

# page untuk informasi video
info_page = ttk.Frame(notebook)
info_page.pack(fill=tk.BOTH)
info_page.columnconfigure(0, weight=1)
info_page.columnconfigure(2, weight=5)
notebook.add(info_page, text="Info")

# mambuat label informasi
for i, name in enumerate(list(info_video.keys())):
    ttk.Label(info_page, text=name, anchor=tk.W).grid(row=i, column=0, sticky=tk.W, padx=10)

# membuat warp title
lbl_title = ttk.Label(info_page, width=50, textvariable=info_video["title"], justify=tk.LEFT)
lbl_title.grid(row=0, column=1, sticky=tk.W)
lbl_title.bind('<Configure>', lambda e: lbl_title.config(wraplength=lbl_title.winfo_width()))

# membuat label untuk view , length, and author
ttk.Label(info_page, textvariable=info_video["view"], justify=tk.LEFT).grid(row=1, column=1, sticky=tk.W)
ttk.Label(info_page, textvariable=info_video["length"], justify=tk.LEFT).grid(row=2, column=1, sticky=tk.W)
ttk.Label(info_page, textvariable=info_video["author"]).grid(row=3, column=1, sticky=tk.W)

# membuat sebuah description
frm_desc = ttk.Frame(info_page)
frm_desc.columnconfigure(0, weight=10)
frm_desc.columnconfigure(1, weight=1)
# membuat Scroll Bar h dan v
scroll_h = ttk.Scrollbar(frm_desc, orient=tk.HORIZONTAL)
scroll_v = ttk.Scrollbar(frm_desc, orient=tk.VERTICAL)
# setup scroll
scroll_h.grid(row=1, column=0, sticky=tk.EW)
scroll_v.grid(row=0, column=1, sticky=tk.NS)

info_video["description"] = tk.Text(frm_desc, wrap=tk.NONE, xscrollcommand=scroll_h.set, yscrollcommand=scroll_v.set, width=45, height=11, state=tk.DISABLED)
info_video["description"].grid(row=0, column=0, sticky=tk.NSEW)

scroll_h.config(command=info_video["description"].xview)
scroll_v.config(command=info_video["description"].yview)

frm_desc.grid(row=4, column=1, sticky=tk.NSEW)

# page untuk mendownload video dan audio
download_page = ttk.Frame(notebook)
download_page.pack(fill=tk.BOTH)
notebook.add(download_page, text="Download")

# kepala dari halaman download
header_download_page = ttk.Frame(download_page)
header_download_page.columnconfigure(0, weight=1)
header_download_page.columnconfigure(1, weight=5)
header_download_page.columnconfigure(2, weight=1)

# folder
lbl_folder = ttk.Label(header_download_page, text="Folder")
lbl_folder.grid(row=0, column=0, sticky=tk.W)
enty_folder = ttk.Entry(header_download_page, textvariable=dirpath, width=55, state=tk.DISABLED)
enty_folder.grid(row=0, column=1, sticky=tk.EW, padx=10)
btn_folder = ttk.Button(header_download_page, text="Open Folder", command=open_folder)
btn_folder.grid(row=0, column=2, sticky=tk.E)

header_download_page.pack(fill=tk.X, padx=5, pady=5)
ttk.Separator(download_page, orient=tk.HORIZONTAL).pack(fill=tk.X)
# badan dari halaman download
body_download_page = ttk.Frame(download_page)
body_download_page.pack(anchor=tk.W)

window.mainloop()
