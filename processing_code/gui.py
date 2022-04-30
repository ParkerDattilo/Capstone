# hyperspectral camera gui
import matplotlib
from matplotlib.pyplot import imread, imsave
import os
import subprocess
import time
matplotlib.use('Agg')
from vimba import *
from tkinter import *
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
from PIL import Image, ImageTk
from calibrate import calibrate_focus
from camera import run_camera_wavelength
from intensity_plot import focus_plot
from one_image import one_image
# ADDITIONAL SELECTOR CODE

vals = [0,0,0]
class MousePositionTracker(tk.Frame):
    """ Tkinter Canvas mouse position widget. """

    def __init__(self, canvas, tab):
        self.canvas = canvas
        self.tab=tab
        self.canv_width = self.canvas.cget('width')
        self.canv_height = self.canvas.cget('height')
        self.reset()

        # Create canvas cross-hair lines.
        xhair_opts = dict(dash=(3, 2), fill='white', state=tk.HIDDEN)
        self.lines = (self.canvas.create_line(0, 0, 0, self.canv_height, **xhair_opts),
                      self.canvas.create_line(0, 0, self.canv_width,  0, **xhair_opts))

    def cur_selection(self):
        return (self.start, self.end)

    def begin(self, event):
        self.hide()
        self.start = (event.x, event.y)  # Remember position (no drawing).

    def update(self, event):
        self.end = (event.x, event.y)
        self._update(event)
        self._command(self.start, (event.x, event.y))  # User callback.

    def _update(self, event):
        # Update cross-hair lines.
        self.canvas.coords(self.lines[0], event.x, 0, event.x, self.canv_height)
        self.canvas.coords(self.lines[1], 0, event.y, self.canv_width, event.y)
        self.show()

    def reset(self):
        self.start = self.end = None

    def hide(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.HIDDEN)
        self.canvas.itemconfigure(self.lines[1], state=tk.HIDDEN)

    def show(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.NORMAL)
        self.canvas.itemconfigure(self.lines[1], state=tk.NORMAL)

    def autodraw(self, command=lambda *args: None):
        """Setup automatic drawing; supports command option"""
        self.reset()
        self._command = command
        self.canvas.bind("<Button-1>", self.begin)
        self.canvas.bind("<B1-Motion>", self.update)
        self.canvas.bind("<ButtonRelease-1>", self.quit)

    def quit(self, event):
        self.hide()  # Hide cross-hairs.
        vals[0]=self.start
        vals[1]=self.end
        self.reset()



class SelectionObject:
    """ Widget to display a rectangular area on given canvas defined by two points
        representing its diagonal.
    """
    def __init__(self, canvas, select_opts):
        # Create attributes needed to display selection.
        self.canvas = canvas
        self.select_opts1 = select_opts
        self.width = self.canvas.cget('width')
        self.height = self.canvas.cget('height')

        # Options for areas outside rectanglar selection.
        select_opts1 = self.select_opts1.copy()  # Avoid modifying passed argument.
        select_opts1.update(state=tk.HIDDEN)  # Hide initially.
        # Separate options for area inside rectanglar selection.
        select_opts2 = dict(dash=(2, 2), fill='', outline='white', state=tk.HIDDEN)

        # Initial extrema of inner and outer rectangles.
        imin_x, imin_y,  imax_x, imax_y = 0, 0,  1, 1
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height

        self.rects = (
            # Area *outside* selection (inner) rectangle.
            self.canvas.create_rectangle(omin_x, omin_y,  omax_x, imin_y, **select_opts1),
            self.canvas.create_rectangle(omin_x, imin_y,  imin_x, imax_y, **select_opts1),
            self.canvas.create_rectangle(imax_x, imin_y,  omax_x, imax_y, **select_opts1),
            self.canvas.create_rectangle(omin_x, imax_y,  omax_x, omax_y, **select_opts1),
            # Inner rectangle.
            self.canvas.create_rectangle(imin_x, imin_y,  imax_x, imax_y, **select_opts2)
        )

    def update(self, start, end):
        # Current extrema of inner and outer rectangles.
        imin_x, imin_y,  imax_x, imax_y = self._get_coords(start, end)
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height

        # Update coords of all rectangles based on these extrema.
        self.canvas.coords(self.rects[0], omin_x, omin_y,  omax_x, imin_y),
        self.canvas.coords(self.rects[1], omin_x, imin_y,  imin_x, imax_y),
        self.canvas.coords(self.rects[2], imax_x, imin_y,  omax_x, imax_y),
        self.canvas.coords(self.rects[3], omin_x, imax_y,  omax_x, omax_y),
        self.canvas.coords(self.rects[4], imin_x, imin_y,  imax_x, imax_y),

        for rect in self.rects:  # Make sure all are now visible.
            self.canvas.itemconfigure(rect, state=tk.NORMAL)

    def _get_coords(self, start, end):
        """ Determine coords of a polygon defined by the start and
            end points one of the diagonals of a rectangular area.
        """
        return (min((start[0], end[0])), min((start[1], end[1])),
                max((start[0], end[0])), max((start[1], end[1])))

    def hide(self):
        for rect in self.rects:
            self.canvas.itemconfigure(rect, state=tk.HIDDEN)


class Application(tk.Frame):

    # Default selection object options.
    SELECT_OPTS = dict(dash=(2, 2), stipple='gray25', fill='red',
                          outline='')

    def __init__(self, parent, img, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # path = "combined_image.png"
        # img = ImageTk.PhotoImage(Image.open(path))

        self.canvas = tk.Canvas(parent, width=img.width(), height=img.height(),
                                borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True)

        self.created_image = self.canvas.create_image(0, 0, image=img, anchor=tk.NW)
        self.canvas.img = img  # Keep reference.

        # Create selection object to show current selection boundaries.
        self.selection_obj = SelectionObject(self.canvas, self.SELECT_OPTS)

        # Callback function to update it given two points of its diagonal.
        def on_drag(start, end, **kwarg):  # Must accept these arguments.
            self.selection_obj.update(start, end)

        # Create mouse position tracker that uses the function.
        self.posn_tracker = MousePositionTracker(self.canvas, parent)
        self.posn_tracker.autodraw(command=on_drag)  # Enable callbacks.

# --- this is for the image viewer tab ----
# need to have wavelength range (start and stop wavelength)
# object distance with distance input number box and the units dropdown menu
# wavelength increments with distance input number box and the units dropdown menu
# detector setting with two radio buttons: auto and manual 
# image capture on the right and under the picture display, have the start capture button

#create a new window
class RegionImage():
    def __init__(self, r_image, c_image):
        self.regionImage=r_image
        self.combinedImage=c_image
    def update_r_image(self,img):
        self.regionImage=img
        print(f"image updated to {img}")
    def update_c_image(self,img):
        self.combinedImage=img
        print(f"image updated to {img}")

fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

matplotlib.use("TkAgg")

def draw_figure(figure,tab3):
    canvas = FigureCanvasTkAgg(fig,
                               master = tab3)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
def quit_me():
    print('quit')
    root.quit()
    root.destroy()
root = Tk()
root.protocol("WM_DELETE_WINDOW", quit_me)
fn = IntVar()
radio_var = StringVar()
root.title("Hyperspectral Camera GUI")

tabControl = ttk.Notebook(root)
tabControl.pack(pady=15)

tab1 = Frame(tabControl)
tab2 = Frame(tabControl)
tab3 = Frame(tabControl)
# tab4 = Frame(tabControl)
tab1.pack(expand = 1, fill ="both")
tab2.pack(expand = 1, fill ="both")
tab3.pack(expand = 1, fill ="both")
# tab4.pack(expand = 1, fill ="both")

  
tabControl.add(tab1, text ='Detector Interface')
tabControl.add(tab2, text ='Translator Control Interface')
tabControl.add(tab3, text ='Data Output Display')
# tabControl.add(tab4, text ='Display Image')

# DATA OUTPUT DISPLAY

# canvas = Canvas(
#     tab3,
#     width=2464/6+20,
#     height=2056/6+20
#     )      
# canvas.pack()      
img = Image.open('./combined_image.png')  
# img = PhotoImage(file='./combined_image.png')
resized_image= img.resize((int(2464/6),int(2056/6)), Image.ANTIALIAS)
new_image= ImageTk.PhotoImage(resized_image)
regionFrame = Application(tab3,new_image)

def combinedImage():
    one_image()
    img = Image.open('./combined_image.png')  
    # img = PhotoImage(file='./combined_image.png')
    resized_image= img.resize((int(2464/6),int(2056/6)), Image.ANTIALIAS)
    new_image= ImageTk.PhotoImage(resized_image)
    region_image.update_c_image(new_image)

    
def updateCombined():
    regionFrame.canvas.itemconfig(regionFrame.created_image, image=region_image.combinedImage)

startCombinedBTN = Button(tab3, text = 'Generate combined image from "captured_images" folder',command = combinedImage)
startCombinedBTN.pack()
updateCombinedBTN = Button(tab3, text = 'Update generated combined image',command = updateCombined)
updateCombinedBTN.pack()
img = Image.open('./selected_plot_0.png')
resized_image_2= img.resize((int(1000),int(400)), Image.ANTIALIAS)
img=ImageTk.PhotoImage(resized_image_2)
region_image=RegionImage(img, new_image)

def getRegion():
    vals[2]+=1
    focus_plot(vals[0], vals[1], vals[2])
    line.set(f"Region selected: {vals[0]}, {vals[1]}")
    root.update_idletasks
    image=Image.open(f'./selected_plot_{vals[2]}.png')
    resized_image_2= image.resize((int(1000),int(400)), Image.ANTIALIAS)
    image=ImageTk.PhotoImage(resized_image_2)
    region_image.update_r_image(image)
selectRegionBTN = Button(tab3, text = 'Select Region of Interest',command = getRegion)
selectRegionBTN.pack()

# global region_image 
# region_image = RegionImage(tab3)
selected_canvas = tk.Canvas(tab3, width=img.width(), height=img.height(),
                        borderwidth=0, highlightthickness=0)
selected_canvas.pack(expand=True)

selected_region=selected_canvas.create_image(0, 0, image=img, anchor=tk.NW)
# canvas = Canvas(
#     tab3,
#     width=2464/6+20,
#     height=2056/6+20
#     )      
# canvas.pack()
# img = Image.open('../im_proc/red_led.png')
# resized_image_2= img.resize((int(2464/4),int(2056/4)), Image.ANTIALIAS)
line=StringVar()
line.set(f"Region selected: (0, 0), (0, 0)")
currRegion = tk.Label(tab3, textvariable=line)
currRegion.pack()
        
def updateImage():
    selected_canvas.itemconfig(selected_region, image=region_image.regionImage)


updateRegionBTN = Button(tab3, text = 'Update Region Image',command = updateImage)
updateRegionBTN.pack()

# draw_figure(fig, tab3)


# DETECTOR INTERFACE

startWavelength = tk.Label(tab1, text="Start Wavelength (nm)")
entry_StartWavelength = tk.Entry(tab1)
startWavelength.pack()
entry_StartWavelength.pack()
startWavelength = entry_StartWavelength.get()

stopWavelength = tk.Label(tab1, text="Stop Wavelength (nm)")
entry_StopWavelength = tk.Entry(tab1)
stopWavelength.pack()
entry_StopWavelength.pack()
stopWavelength = entry_StopWavelength.get()

objectDistance = tk.Label(tab1, text="Object Distance (mm)")
entry_ObjectDistance = tk.Entry(tab1)
objectDistance.pack()
entry_ObjectDistance.pack()
objectDistance = entry_ObjectDistance.get()

wavelengthIncrement = tk.Label(tab1, text="Wavelength Increments (nm)")
entry_WavelengthIncrement= tk.Entry(tab1)
wavelengthIncrement.pack()
entry_WavelengthIncrement.pack()
wavelengthIncrement = entry_WavelengthIncrement.get()

# TRANSLATOR CONTROL INTERFACE

currentPosition=StringVar()
currentPosition.set('Move the stage to see current position...')
posLabel=tk.Label(tab2, textvar=currentPosition)
posLabel.pack()

def calibrateStage():
    done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", "Desktop/translation_stage/calibrate_stage_pos.py"],stdout=subprocess.DEVNULL)

calibrateStageBTN = Button(tab2, text = 'Calibrate Location On Stage (set current position to 0 mm)',command = calibrateStage)
calibrateStageBTN.pack()

moveToPosition = tk.Label(tab2, text="Move To Position (mm)")
entry_MovePosition = tk.Entry(tab2)
moveToPosition.pack()
entry_MovePosition.pack()
moveToPosition = entry_MovePosition.get()

def movePosition():
    error_str = ""
    if checkEntry(entry_MovePosition.get()):
        done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", "Desktop/translation_stage/move_to_pos.py", entry_MovePosition.get()],stdout=subprocess.DEVNULL)
    else:
        print("please use a number")
    if (done.returncode!=0):
        print("Error, out of bounds location selected")
        error_str=" Error, out of bounds location selected"
    p=subprocess.Popen(["ssh",  "pi@192.168.5.1", "cat", "Desktop/translation_stage/pos.txt"],stdout=subprocess.PIPE)
    curpos, err = p.communicate()
    curpos=curpos.decode("utf-8")
    currentPosition.set(curpos+error_str)
    root.update_idletasks

startMovePosBTN = Button(tab2, text = 'Move Position',command = movePosition)
startMovePosBTN.pack()

moveDistance = tk.Label(tab2, text="Move Distance (mm). (+) towards motor, (-) towards lens.")
entry_MoveDistance = tk.Entry(tab2)
moveDistance.pack()
entry_MoveDistance.pack()
moveDistance = entry_MoveDistance.get()

def moveDistance():
    error_str = ""
    if checkEntry(entry_MoveDistance.get()):
        done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", "Desktop/translation_stage/move_dist.py", entry_MoveDistance.get()],stdout=subprocess.DEVNULL)
    else:
        print("Please enter a number")
    if (done.returncode!=0):
        error_str=" Error, out of bounds location selected"
        print("Error, out of bounds location selected")
    p=subprocess.Popen(["ssh",  "pi@192.168.5.1", "cat", "Desktop/translation_stage/pos.txt"],stdout=subprocess.PIPE)
    curpos, err = p.communicate()
    curpos=curpos.decode("utf-8")
    currentPosition.set(curpos+error_str)
    root.update_idletasks

startMoveDistBTN = Button(tab2, text = 'Move Distance',command = moveDistance)
startMoveDistBTN.pack()

moveWavelength = tk.Label(tab2, text="Move to Wavelength (nm)")
entry_MoveWavelength = tk.Entry(tab2)
moveWavelength.pack()
entry_MoveWavelength.pack()
moveWavelength = entry_MoveWavelength.get()

moveObjDist = tk.Label(tab2, text="Move to Wavelength Object Distance (mm)")
entry_ObjDist = tk.Entry(tab2)
moveObjDist.pack()
entry_ObjDist.pack()
moveObjDist = entry_ObjDist.get()


def moveWavelength():
    error_str=""
    if checkEntry(entry_MoveWavelength.get()) and checkEntry(entry_ObjDist.get()):
        done=subprocess.run(["ssh",  "pi@192.168.5.1", "python3", "Desktop/translation_stage/move_wavelength.py", entry_MoveWavelength.get(), entry_ObjDist.get()],stdout=subprocess.DEVNULL)
    else:
        print("Please enter a number")
        return
    if (done.returncode!=0):
        error_str=" Error, out of bounds location selected"
        print("Error, out of bounds location selected")
    p=subprocess.Popen(["ssh",  "pi@192.168.5.1", "cat", "Desktop/translation_stage/pos.txt"],stdout=subprocess.PIPE)
    curpos, err = p.communicate()
    curpos=curpos.decode("utf-8")
    currentPosition.set(curpos+error_str)
    root.update_idletasks

startMoveDistBTN = Button(tab2, text = 'Move to Wavelength',command = moveWavelength)
startMoveDistBTN.pack()

def captureImage():
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        with cams[0] as cam:
            for frame in cam.get_frame_generator(limit=1):
                image=np.reshape(frame.as_numpy_ndarray(),(frame.as_numpy_ndarray().shape[0],frame.as_numpy_ndarray().shape[1]))
                im=Image.fromarray(image)
                im.save('./current_view.png')  
                # img = PhotoImage(file='./combined_image.png')
                resized_image= im.resize((int(2464/6),int(2056/6)), Image.ANTIALIAS)
                currIm=ImageTk.PhotoImage(resized_image)
                panel.configure(image=currIm) 
                panel.image=currIm
                # new_image=ImageTk.PhotoImage(resized_image)  
                root.update_idletasks

temp = Image.open('./current_view.png')
resized_temp= temp.resize((int(2464/6),int(2056/6)), Image.ANTIALIAS)
currIm=ImageTk.PhotoImage(resized_temp)
panel = tk.Label(tab2, image=currIm)
panel.pack(side="bottom", fill="both", expand="yes")

# canvas_cur = tk.Canvas(tab2, width=int(2464/6), height=int(2056/6),
#                         borderwidth=0, highlightthickness=0)
# canvas_cur.pack(expand=True)
    
startSingleImageBTN = Button(tab2, text = 'Take Single Image',command = captureImage)
startSingleImageBTN.pack()

calibrationWavelength = tk.Label(tab2, text="Calibration Known Wavelength (nm)")
entry_calibrationWavelength = tk.Entry(tab2)
calibrationWavelength.pack()
entry_calibrationWavelength.pack()
calibrationWavelength = entry_calibrationWavelength.get()

calibrationDistance = tk.Label(tab2, text="Calibration Object Distance (mm)")
entry_calibrationDistance = tk.Entry(tab2)
calibrationDistance.pack()
entry_calibrationDistance.pack()
calibrationDistance = entry_calibrationDistance.get()

calibrationRange = tk.Label(tab2, text="Calibration Wavelength Range (nm)")
entry_calibrationRange = tk.Entry(tab2)
calibrationRange.pack()
entry_calibrationRange.pack()
calibrationRange = entry_calibrationRange.get()

calibrationStepSize = tk.Label(tab2, text="Calibration Step Size (nm)")
entry_calibrationStepSize = tk.Entry(tab2)
calibrationStepSize.pack()
entry_calibrationStepSize.pack()
calibrationStepSize = entry_calibrationStepSize.get()

def checkEntry(val):
    try:
        float(val)
        return True
    except:
        return False

def calibrateWavelength():
    dist=entry_calibrationDistance.get()
    wl=entry_calibrationWavelength.get()
    r=entry_calibrationRange.get()
    step=entry_calibrationStepSize.get()
    if checkEntry(dist) and checkEntry(wl) and checkEntry(r) and checkEntry(step):
        calibrate_focus(float(wl),float(dist),int(step),float(r))
        root.update_idletasks
    else:
        print("Please enter number values for the calibration")

startCalibrateBTN = Button(tab2, text = 'Start Calibration',command = calibrateWavelength)
startCalibrateBTN.pack()


#detector setting
def detectorSetting():
   selection = "Detector Setting " + str(var.get())
   label.config(text = selection)

var = IntVar()
# r1 = Radiobutton(tab1, text="Auto", variable=var, value= "Auto Selected",
#                   command=detectorSetting)
# r1.pack( anchor = W )

# r2 = Radiobutton(tab1, text="Manual", variable=var, value= "Manual Selected",
#                   command=detectorSetting)
# r2.pack( anchor = W )

def imageCapture():
    res=entry_WavelengthIncrement.get()
    startw=entry_StartWavelength.get()
    stopw=entry_StopWavelength.get()
    od=entry_ObjectDistance.get()
    if checkEntry(res) and checkEntry(startw) and checkEntry(stopw) and checkEntry(od):
        run_camera_wavelength(int(res),float(startw),float(stopw),float(od))
        root.update_idletasks
    else:
        print(f"Please enter number values for the capture: {res}, {startw},{stopw}, {od}")


startCaptureBTN = Button(tab1, text = 'Start Capture',command = imageCapture)
#need to connect to start capture in the command = part
startCaptureBTN.pack() 

label = Label(root)
label.pack()
print("before")
root.mainloop()
print("after")

