import os
import time
import random
import threading
from PIL import Image, ImageTk
from tkinter import Tk, Label, Scale, W, HORIZONTAL

crossfadesleep = 0.01
transitionsleep = 0.00

def load_images(screen_width, event):
    random.shuffle(image_files)  # Randomize the order of image files

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path).convert('RGBA')
        resized_image = resize_image(image,
                                     (1024, 1024))
        image = resized_image
        preloaded_images.append(resized_image)

    event.set()  # Signal that the images have finished loading

def resize_image(image, size):
    width, height = size
    image.thumbnail(size, Image.ANTIALIAS)
    new_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    new_image.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    return new_image

def transition_images():
    i = 0
    while True:
        current_image = preloaded_images[i]
        next_image = preloaded_images[(i + 1) % len(preloaded_images)]
        crossfade(current_image, next_image)
        time.sleep(transitionsleep)  # Adjust the interval between transitions
        i = (i + 1) % len(preloaded_images)

def crossfade(image1, image2):
    if image1.size != image2.size:
        image2 = image2.resize(image1.size)

    for alpha in range(0, 256, crossfade_speeds[crossfade_speed.get()]):
        blended = Image.blend(image1, image2, alpha / 255.0)
        photo = ImageTk.PhotoImage(blended)
        image_label.configure(image=photo)
        image_label.image = photo  # Store a reference to prevent garbage collection
        window.update()
        time.sleep(crossfadesleep)  # Adjust the crossfade speed

def update_crossfade_speed(value):
    value = int(value)
    speed = crossfade_speeds[value]

folder_path = "path\to\folder"
image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and not f.lower().endswith('.mov')]

window = Tk()
window.title("Slideshow App")
window.geometry("1000x750")

preloaded_images = []

event = threading.Event()
loading_thread = threading.Thread(target=load_images, args=(window.winfo_screenwidth(), event))
loading_thread.start()

event.wait()  # Wait for the images to finish loading

crossfade_speeds = [2, 4, 8, 16, 32, 64, 128]

crossfade_speed = Scale(window, from_=0, to=len(crossfade_speeds)-1, orient=HORIZONTAL, command=update_crossfade_speed)
crossfade_speed.pack(anchor=W)

image_label = Label(window)
image_label.pack()

transition_thread = threading.Thread(target=transition_images)
transition_thread.start()

shuffle_interval = 1  # Shuffle interval in seconds (e.g., shuffle every 60 seconds)

def shuffle_images():
    random.shuffle(preloaded_images)
    
window.after(shuffle_interval * 1000, shuffle_images)

while len(preloaded_images) < len(image_files):
    # Wait for images to be loaded before starting the slideshow
    window.update()  # Update the tkinter window within the main loop
    time.sleep(0.1)


window.mainloop()
