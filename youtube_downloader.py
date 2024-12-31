from customtkinter import *
from tkinter import filedialog
from threading import Thread
from copy import deepcopy, copy
import requests
from io import BytesIO
from PIL import Image
import tkinter.messagebox
from pytube import *
import pytube.request
import pyperclip
import os
# from CTkMessagebox import CTkMessagebox

# from pytube.cli import on_progress 
pytube.request.default_range_size=1024*1024

#######################################################################################################################
os.system('cls')
tabs_counter=0
user=os.environ.get('USERNAME')
default_value={
    "output_path": f"C:\\Users\\{user}\\Downloads\\",
    "is_playlist": False,
    "prefer_audio_quality":"128kbps",
    "prefer_video_quality":"1080p",
}
video_resolution={
    "4320p":4320,
    "2160p": 2160,
    "1440p":1440,
    "1920p":1920,
    "1080p": 1080,
    "1280p":1280,
    "720p": 720,
    "360p": 360,
    "240p": 240,
    "144p": 144,
}
options={
    "media":"",
    "thumbnail": "",
    "caption": "",
}
select_stream={
    "stream":None,
    "media_type":None,
    "formate":None,
    "quality":None,
    "size":0,
    "status":None,
    "downloaded":0
}
video={
    "id":0,
    "url":"",
    "YouTube":None,
    "title":"",
    "thumbnail": None,
    "output_path":default_value["output_path"],
    "options": None,
    "streams":[],
    "select_menue": "",
    "select_stream":None,
    "progress":None,
    "frame": None,
    "downloaded":0
}
tab={
    "url":"",
    "id":"",
    "is_playlist":False,
    "is_subfolder":None,
    "output_path":default_value["output_path"],
    "name":"",
    "title":"",
    "status":None,
    "progress":None,
    "total_size":None,
    "total_media":0,
    "array":[],
}
band_char=[':','/','\\','*','<','>','"']
is_process=0
tabs_info = []


#######################################################################################################################

def download(tab_id: int):
    tab=tabs_info[tab_id]
    tabs_info[tab_id]["status"].grab_set()
    tabs_info[tab_id]["status"].configure(state=DISABLED)
    
    name=tabs_info[tab_id]["title"].get()
    for ele in band_char:
        name=name.replace(ele, "")
    name=name.replace("|","-")
    name=name.replace("?","؟")
    if tab["is_subfolder"].get()==1:
        tabs_info[tab_id]["output_path"]=default_value["output_path"] + name + "\\"
    else:
        tabs_info[tab_id]["output_path"]=default_value["output_path"]

    for e, ele in enumerate(tab["array"]):
        x=ele["select_menue"].get()
        for m, med in enumerate(ele["streams"]):
            # preper for downloading
            if x==med["select"]:
                tabs_info[tab_id]["array"][e]["select_stream"]["stream"] = med["stream"]
                tabs_info[tab_id]["array"][e]["select_stream"]["media_type"]=x.split("|")[0].strip().split("/")[0]
                tabs_info[tab_id]["array"][e]["select_stream"]["formate"]=x.split("|")[0].strip().split("/")[1]
                tabs_info[tab_id]["array"][e]["select_stream"]["quality"]=x.split("|")[1].strip()
                tabs_info[tab_id]["array"][e]["select_stream"]["size"]=x.split("|")[2].strip()
                break
            
        if(ele["options"]["thumbnail"].get()==1):
            # write thumbnail Image module
            img=download_thumnail(ele["YouTube"],-1)
            try:
                os.mkdir(tabs_info[tab_id]["output_path"])
            except: 
                pass
            if(os.path.isfile(tabs_info[tab_id]["output_path"] + ele["title"].get() + ".jpg")==False):
                img.save(tabs_info[tab_id]["output_path"] + ele["title"].get() + ".jpg")
        
        if(ele["options"]["caption"].get()==1): pass
            # write str file
            # ele["caption"].save()
    
        if(ele["options"]["media"].get()==1):
            # download youtube media
            tabs_info[tab_id]["array"][e]["select_stream"]["stream"].download(output_path=tabs_info[tab_id]["output_path"], 
                                                                              filename=str(ele['title'].get()+"."+tabs_info[tab_id]["array"][e]["select_stream"]["formate"])
                                                                              )
    tabs_info[tab_id]["status"].grab_release()
    tabs_info[tab_id]["status"].configure(state=NORMAL)
    

def total_media(tab_id):
    m=0
    c=0
    t=0
    tab=tabs_info[tab_id]
    for ele in tab["array"]:
        if(ele["options"]["media"].get()==1):
            m+=1
        if(ele["options"]["caption"].get()==1):
            c+=1
        if(ele["options"]["thumbnail"].get()==1):
            t+=1
    
    tabs_info[tab_id]["total_media"]=m
    if (m or c or t):
        n=f"download"  
    else: 
        n= "No selected"
    if m: 
        n=n+f" ({m} media)" ""
    if (m and c) or (m and t):
        n=n+" and" 
    if c:
        n=n+f" ({c} caption)"
    if m and c and t:
        n=n+"\n"
    if (t and c):
        n=n+ " and"  
    if t:
        n=n+f" ({t} thumbnails)" 
    # n = f"download" if (m or c or t) else "No selected" +\
    # f" ({m} media)" if ((m and c) or (m and t)) else ""+\
    # " and" if (m and c) or (m and t) else ""+\
    # f" ({c} caption)" if c else ""+\
    # " and" if(t and c) else ""+\
    # f" ({t} thumbnails)" if t else ""
    
    tabs_info[tab_id]["status"].configure(text=n)
    
    

def change_select(tab_id, type_media="video"):
    if type_media=="video":
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            tabs_info[tab_id]["array"][c]["select_menue"].configure(variable=StringVar(value=tabs_info[tab_id]["array"][c]["streams"][0]["select"]))
            
        for c, i in enumerate(tabs_info[tab_id]["array"]):
                for z, e in enumerate(i["streams"]):
                    if e["select"].split("|")[1].strip()=="1080p":
                        tabs_info[tab_id]["array"][c]["select_menue"].configure(variable=StringVar(value=e["select"]))
                        break
    elif type_media== "audio": 
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            for z, e in enumerate(i["streams"]):
                if e["select"].split("|")[0].strip().split("/")[0]=="audio":
                    tabs_info[tab_id]["array"][c]["select_menue"].configure(variable=StringVar(value=e["select"]))
                    break
        for c, i in enumerate(tabs_info[tab_id]["array"]):
                for z, e in enumerate(i["streams"]):
                    if e["select"].split("|")[1].strip()=="128kbps":
                        tabs_info[tab_id]["array"][c]["select_menue"].configure(variable=StringVar(value=e["select"]))
                        break
    elif type_media=="select all media":
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            tabs_info[tab_id]["array"][c]["options"]["media"].configure(variable=IntVar(value=1))
    elif type_media=="deselect all media":
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            tabs_info[tab_id]["array"][c]["options"]["media"].configure(variable=IntVar(value=0))
    elif type_media=="select all captions":
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            tabs_info[tab_id]["array"][c]["options"]["caption"].configure(variable=IntVar(value=1))
    elif type_media=="deselect all captions":
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            tabs_info[tab_id]["array"][c]["options"]["caption"].configure(variable=IntVar(value=0))
    elif type_media=="select all thumbnails":
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            tabs_info[tab_id]["array"][c]["options"]["thumbnail"].configure(variable=IntVar(value=1))
    elif type_media=="deselect all thumbnails":
        for c, i in enumerate(tabs_info[tab_id]["array"]):
            tabs_info[tab_id]["array"][c]["options"]["thumbnail"].configure(variable=IntVar(value=0))
    total_media(tab_id)



def download_thumnail(youtube: YouTube, index: int)-> Image:
    url_img=youtube.vid_info["videoDetails"]["thumbnail"]["thumbnails"][index]["url"]
    url_width=youtube.vid_info["videoDetails"]["thumbnail"]["thumbnails"][index]["width"]
    url_height=youtube.vid_info["videoDetails"]["thumbnail"]["thumbnails"][index]["height"]
    response = requests.get(url_img)
    img = Image.open(BytesIO(response.content))
    return img
    # return {"img": img, "width": url_width, "height":url_height}



def on_progress(stream, chunk, bytes_remaining: float, tab_id, media_id)->None: 
    tab=copy(tabs_info[tab_id])
    
    media_size=tab["array"][media_id]["select_stream"]["stream"].filesize  
    down=media_size-bytes_remaining
    tabs_info[tab_id]["array"][media_id]["progress"].configure(variable=DoubleVar(value=(down/media_size)))
    tabs_info[tab_id]["array"][media_id]["downloaded"]=down
    
    tab_size=0
    for ele in tab["array"]:
        if(ele["options"]["media"].get()==1):
            f=stream.filesize
            tab_size+=(f)    
    
    tab_downloaded=0
    for i, ele in enumerate(tab["array"]):
        if(ele["options"]["media"].get()==1):
            #f=round(float(ele["select_stream"]["stream"].filesize))
            tab_downloaded+=tabs_info[tab_id]["array"][i]["downloaded"]
    p=tab_downloaded/tab_size
    tabs_info[tab_id]["progress"].configure(variable=DoubleVar(value=(p)))
    
    app.update_idletasks() 



def on_complete(stream, file_path, tab_id, med_id):
    tabs_info[tab_id]["array"][med_id]["frame"].configure(border_color="lightgreen")
    tabs_info[tab_id]["array"][med_id]["progress"].configure(variable=DoubleVar(value=1))
    tabs_info[tab_id]["array"][med_id]["progress"].configure(progress_color="forestgreen")
    


def new_tab(event=None):
    global is_process
    global tabs_counter
    global default_value
    global my_font
    global tabs_info
    global tab
    global select_stream
    global video
    ####################
    # Check existing Link
    if is_process==1: return
    is_process=1
    tab_id=tabs_counter
    tabs_info.append(deepcopy(tab))
    
    url_link=pyperclip.paste()
    if tabs_info != []: 
        for i in tabs_info:
            if tabs_info[tab_id]["url"] == url_link:
                tb_container.set("playlist: " if i["is_playlist"]==True else "video: "+f"{i['name']}")
                tabs_info.pop()
                return
    tabs_info[tab_id]["url"]=url_link
    tabs_info[tab_id]["id"]=tab_id
    ####################
    # Check link type and availability 
    try:
        if "youtube.com/playlist?list=" in url_link:
            is_playlist = True
            yt=Playlist(url_link)
            l=yt.video_urls
        else:
            is_playlist=False
            yt=YouTube(url_link)
            l=[url_link]
    except:
        tkinter.messagebox.showerror("Error", "invalid link")
        is_process=0
        return
    
    tabs_info[tab_id]["name"]=yt.title
    tabs_info[tab_id]["is_playlist"]=is_playlist
    tabs_info[tab_id]["title"]=yt.title
    name_tab= "playlist: "+f"{tabs_info[tab_id]['name']}" if is_playlist==True else "video: "+f"{tabs_info[tab_id]['name']}" 
    i=0
    for c,ele in enumerate(tabs_info):
        if ele["name"]==name_tab:
            i+=1
    try: # faild to add tab for some reason (dont delete this try)
        tb_container.add(name_tab + "" if i==0 else f" ({i})")
        tb_container.set(name_tab)
    except:
        return
    tabs_counter+=1
    is_process=0
    ####################
    # fill data of the tab
    for c,i in enumerate(l,0):
        tabs_info[tab_id]["array"].append(deepcopy(video))
        tabs_info[tab_id]["array"][c]["options"]=deepcopy(options)
        tabs_info[tab_id]["array"][c]["select_stream"]=deepcopy(select_stream)
        tabs_info[tab_id]["array"][c]["id"]=c
        tabs_info[tab_id]["array"][c]["url"]=i
        tabs_info[tab_id]["array"][c]["YouTube"]=YouTube(i, 
                                    on_progress_callback= lambda stream, chunk, bytes_remaining, temp1=tab_id, temp2=c: on_progress(stream, chunk, bytes_remaining, temp1, temp2),
                                    on_complete_callback= lambda stream, file_path, temp1=tab_id, temp2=c: on_complete(stream, file_path, temp1, temp2)
                                )
        tabs_info[tab_id]["array"][c]["title"]=YouTube(i).title
        for ele in band_char:
            tabs_info[tab_id]["array"][c]["title"]=tabs_info[tab_id]["array"][c]["title"].replace(ele, "")
        tabs_info[tab_id]["array"][c]["title"]=tabs_info[tab_id]["array"][c]["title"].replace("|","-")
        tabs_info[tab_id]["array"][c]["title"]=tabs_info[tab_id]["array"][c]["title"].replace("?","؟")
    
    for ele in band_char:
        # tabs_info[tab_id]["name"]=tabs_info[tab_id]["name"].replace(ele, "")
        tabs_info[tab_id]["title"]=tabs_info[tab_id]["title"].replace(ele, "")
    # tabs_info[tab_id]["name"]=tabs_info[tab_id]["name"].replace("|","-")
    tabs_info[tab_id]["title"]=tabs_info[tab_id]["title"].replace("?","؟")    
    
    ####################
    # creat content of the tab
    xx=CTkScrollableFrame(tb_container.tab(name_tab))
    xx.pack(expand=1,fill=BOTH, side=LEFT)
    frame_tab=CTkFrame(xx)
    frame_tab.pack()
    
    for count,vid in enumerate(tabs_info[tab_id]["array"]):
        # video and thime part
        frame_element=CTkFrame(frame_tab, border_width=5, corner_radius=10,border_color="red", bg_color="transparent", fg_color=None)
        frame_element.grid(column=count%2, row=int(count/2), pady=5, padx=5, sticky = 'news')
        tabs_info[tab_id]["array"][count]["id"]=count
        length_in_sec=vid["YouTube"].length
        
        x=download_thumnail(vid["YouTube"], 0)
        img = CTkImage(x, size=(x.width,x.height))
        
        tabs_info[tab_id]["array"][count]["frame"]=frame_element
        lbl_pic=CTkLabel(frame_element, bg_color="transparent", 
                         text=f"{str(int(length_in_sec/3600)).zfill(2)}:{str(int(length_in_sec%3600/60)).zfill(2)}:{str(length_in_sec%60).zfill(2)}", 
                         font=my_font,image=img, anchor="w", compound="top"
                         )
        lbl_pic.grid(column=0, row=0, padx=10, pady=10)
        
        #####################################
        # title and select formate and quality part
        frm_title=CTkFrame(frame_element)
        frm_title.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky="EW")
        frm_options=CTkFrame(frame_element)
        frm_options.grid(column=1, row=0, padx=10, pady=10)
        CTkLabel(frm_options, text="Chose which to download:",font=my_font, text_color="lightgreen").pack()
        lbl_title=CTkEntry(frm_title, font=my_font, fg_color=None, bg_color="transparent")
        lbl_title.pack(fill=X)
        lbl_title.insert(END,vid["title"])
        tabs_info[tab_id]["array"][count]["title"]=lbl_title
        # Sort quality data #need review and simplify
        stream=vid["YouTube"].streams
        available_resolution=[]
        available_audio=[]
        steam_resolution=set([i.resolution for i in stream])
        stream_audio=stream.filter(only_audio=1)
        stream_audio=[i.abr for i in stream_audio]
        for i in stream_audio:
            available_audio.append(int(i[:-4]))
        available_audio.sort()
        for i,ele in enumerate(available_audio):
            available_audio[i]=str(ele)+"kbps"
        for i in video_resolution.keys():
            if (i in steam_resolution):
                available_resolution.append(i)
        available_resolution.extend(available_audio)            
        for c, ele in enumerate(available_resolution):
            if("kbps" in ele):
                strm=stream.filter(abr=ele).first()
                sz=strm.filesize_mb
            else:
                strm=stream.filter(res=ele).first()
                sz=strm.filesize_mb
            formate=strm.mime_type
            if formate=="audio/mp4":
                formate= "audio/mp3"
            available_resolution[c]= f"{formate}    |    {available_resolution[c]}    |    {sz}MB"
            tabs_info[tab_id]["array"][count]["streams"].append(deepcopy({"stream":strm, "select": available_resolution[c]}))  

        #####################################
        # creat content of select [download media, thumbnail, caption or all?]
        # creat content of single video
        tabs_info[tab_id]["array"][count]["select_menue"] = CTkOptionMenu(frm_title, values=available_resolution, font=my_font, variable= StringVar(value=available_resolution[0]))
        tabs_info[tab_id]["array"][count]["select_menue"].pack()
        
        tabs_info[tab_id]["array"][count]["options"]["media"] = CTkCheckBox(frm_options, variable=IntVar(value=1), text="media", font=my_font, command= lambda: total_media(tab_id))
        tabs_info[tab_id]["array"][count]["options"]["media"].pack(padx=10, pady=10, anchor='w')
        
        tabs_info[tab_id]["array"][count]["options"]["thumbnail"] = CTkCheckBox(frm_options, variable=IntVar(value=0), text="thumbnail", font=my_font, command= lambda: total_media(tab_id))
        tabs_info[tab_id]["array"][count]["options"]["thumbnail"].pack(padx=10, pady=10, anchor='w')
        
        tabs_info[tab_id]["array"][count]["options"]["caption"] = CTkCheckBox(frm_options, variable=IntVar(value=0), text="captions", font=my_font, command= lambda: total_media(tab_id))
        tabs_info[tab_id]["array"][count]["options"]["caption"].pack(padx=10, pady=10, anchor='w')
        
        tabs_info[tab_id]["array"][count]["progress"]=CTkProgressBar(frame_element, variable=DoubleVar(value=0.0), corner_radius=0)
        tabs_info[tab_id]["array"][count]["progress"].grid(column=0, row=2, columnspan=2, sticky="NEWS", padx=5, pady=5)
           
    tabs_info[tab_id]["total_media"]=count+1
    
    
    #####################################
    # creat content of options download, select all, deselect all, select video or audio 
    frm_options=CTkFrame(tb_container.tab(name_tab))
    frm_options.pack(expand=0,side=RIGHT)
    CTkLabel(frm_options, text="Options", font=my_font).grid(row=0, column=0, sticky="ew", columnspan=2)
    
    n=tabs_info[tab_id]["title"]
    tabs_info[tab_id]["title"]=CTkEntry(frm_options, font=my_font)
    tabs_info[tab_id]["title"].grid(row=1, column=0, sticky="ew", columnspan=2)
    tabs_info[tab_id]["title"].insert(END,n)
    tabs_info[tab_id]["title"].configure(state= NORMAL if is_playlist else DISABLED)
    
    tabs_info[tab_id]["is_subfolder"]=CTkCheckBox(frm_options,  text=f"do you want sub folder?", variable=IntVar(value=1 if is_playlist else 0),font=my_font,
                                    command= lambda: tabs_info[tab_id]["title"].configure(state= NORMAL if tabs_info[tab_id]["is_subfolder"].get() else DISABLED))
    tabs_info[tab_id]["is_subfolder"].grid(row= 2, column= 0, padx=5, pady=5, sticky="ew", columnspan=2)
    
    CTkButton(frm_options, text="select video 1080p", font=my_font, command= lambda: change_select(tab_id,"video")).grid(row= 3 ,column= 1 , padx=5, pady=5, sticky="ew")
    CTkButton(frm_options, text="select audio 128kbps", font=my_font, command= lambda: change_select(tab_id,"audio")).grid(row= 3 ,column= 0, padx=5, pady=5, sticky="ew")
    
    CTkButton(frm_options, text="select all media", font=my_font, command= lambda: change_select(tab_id,"select all media")).grid(row= 4 ,column= 1 , padx=5, pady=5, sticky="ew")
    CTkButton(frm_options, text="deselect all media", font=my_font, command= lambda: change_select(tab_id,"deselect all media")).grid(row= 4 ,column= 0, padx=5, pady=5, sticky="ew")
    
    CTkButton(frm_options, text="select all captions", font=my_font, command= lambda: change_select(tab_id,"select all captions")).grid(row= 5 ,column= 1 , padx=5, pady=5, sticky="ew")
    CTkButton(frm_options, text="deselect all captions", font=my_font, command= lambda: change_select(tab_id,"deselect all captions")).grid(row= 5 ,column= 0, padx=5, pady=5, sticky="ew")
    
    CTkButton(frm_options, text="select all thumbnails", font=my_font, command= lambda: change_select(tab_id,"select all thumbnails")).grid(row= 6 ,column= 1 , padx=5, pady=5, sticky="ew")
    CTkButton(frm_options, text="deselect all thumbnails", font=my_font, command= lambda: change_select(tab_id,"deselect all thumbnails")).grid(row= 6 ,column= 0, padx=5, pady=5, sticky="ew")
    
    
    tabs_info[tab_id]["status"]=CTkButton(frm_options, text="download ("+str(tabs_info[tab_id]["total_media"])+" media)", font=my_font,
                                          command= lambda: Thread(target= lambda: download(tab_id)).start())
    tabs_info[tab_id]["status"].grid(row= 7 ,column= 0, padx=5, pady=5, columnspan=2, sticky="ew")
       
    tabs_info[tab_id]["progress"]=CTkProgressBar(frm_options, variable=DoubleVar(value=0.0), corner_radius=0)
    tabs_info[tab_id]["progress"].grid(row=8,column=0, columnspan=2, sticky="ew")   



def change_default(newpath:CTkEntry):
    global default_value
    xx=filedialog.askdirectory()
    if xx == "":
        return
    xx=xx+"/"
    newpath.configure(state=NORMAL)
    newpath.delete(0, END)
    newpath.insert(END, xx)
    newpath.configure(state=DISABLED)
    default_value["output_path"]=newpath.get()
    print(default_value["output_path"])




def setting():
    win_setting = CTkToplevel(app)
    win_setting.title("setting")
    win_setting.resizable(0,0)
    win_setting.grab_set()
    
    


#######################################################################################################################
app = CTk()
app.geometry("950x500")
my_font=CTkFont("time", 18, "bold")


app.title("Youtube downloader")
app.bind('<Control-v>', lambda x: Thread(target=new_tab).start())
frm_setting=CTkFrame(app)
frm_setting.pack(fill=X)
CTkButton(frm_setting, text="Browse path", font=my_font, command= lambda: change_default(tt)).pack(side=LEFT)
tt=CTkEntry(frm_setting, font=my_font, width=250)
tt.pack(side=LEFT)

tt.insert(END, default_value["output_path"])
tt.configure(state=DISABLED)




btn_setting=CTkButton(frm_setting, text="Setting", font=my_font, command=setting)
btn_setting.pack(side=LEFT)
btn_past=CTkButton(frm_setting, text="Click to past link", font=my_font, command=lambda : Thread(target=new_tab).start(), fg_color='green', hover_color='darkgreen')
btn_past.pack(fill=X)
tb_container = CTkTabview(app, anchor='s')
tb_container.pack(expand=1,fill=BOTH)


# if(tkinter.messagebox.askquestion("", "عامل اي يبن عمي\nأحوالك تمام؟")=="yes"):
#     tkinter.messagebox.showinfo("","يا رب دايما، ابدأ التجربة بقى\n.مع العلم حاولت أخلي البرنامج دا ضد غباء المستخدم على قد ما أقدر")
#     tkinter.messagebox.showinfo("",".وهو عقيم شوية فاستحمله معلش، حتى الرسالة دي هتظهر كل مرة")
    
# else:
#     tkinter.messagebox.showinfo("", "خلاص أشوفك وقت تاني بقى\nسلام!")
#     app.destroy()

app.mainloop()

