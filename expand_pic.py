# Importing Image class from PIL module
from PIL import Image

# Opens a image in RGB mode
im = Image.open(r'C:\Users\jamel\Downloads\pixil-frame-0 (7).png')

newsize = (1280//10, 720//10)
im1 = im.resize(newsize)
# Shows the image in image viewer
im1.show()
