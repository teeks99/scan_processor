
iimport PythonMagick as magick
import json
from collections import deque

templates = {}
corners = []
corners.append([0,0,0,0])
corners.append([0,0,0,0])
corners.append([0,0,0,0])
corners.append([0,0,0,0])
templates['4x6'] = corners

corners = []
corners.append([0,0,0,0])
corners.append([0,0,0,0])
corners.append([0,0,0,0])
templates['5x7'] = corners

display_sized_path="disp/"

def zero_trim(number_string):
    while number_string.starts_with("0"):
        number_string = number_string[1:]
    return int(number_string)

def zero_pad(number, digits):
    number_string = str(number)
    while len(number_string) < digits:
        number_string = "0" + number_string
    return number_string

class ImageSet(object):
    def __init__(self):
        self.make_display = True
        self.make_html = True
        
    def process(self, json_file):
        self.data = json.dump(json_file)
        self.generate_special_lookup()
        
        self.raw_start_num = zero_trim(self.data['raw_start'])
        self.raw_end_num = zero_trim(self.data['raw_end'])
        
        self.current_image_number = 0
        self.start_number_num = zero_trim(self.data['start_number'])
        for raw_num in range(raw_start_num, raw_end_num):
            images = self.split(raw_num)
            
            # An order-dependant deque
            while images:
                image = images.popleft()
                img_num = self.start_number_num + self.current_image_number
                img_num_str = zero_pad(img_num, 5)
                if img_num_str in self.lookup:
                    self.add_comment(image, self.lookup[img_num_str])
                    
                if self.make_display:
                    self.display_size(image)
                    
                image.write(img_num_str + '.jpg')
                
                # Increment after
                self.current_image_number += 1
                
        if self.make_html:
            
    
    def generate_special_lookup(self):
        self.lookup = {}
        for img in self.data['special_images']:
            self.lookup[img['number']] = img
        
    def split(self, raw):
        # Open Raw with imagemagick
                
        images = deque()
        for corners in templates[self.data['size']]:
            images.append(self.crop(raw, corners))          
            
        # close the raw image
        return images
            
    def crop(raw, corners):
        # Make a copy of the raw image
        img = None
        # Use imagemagick to crop
        return img
        
    def add_comment(img, comment):
        # Add EXIF/IPTC Caption, Description, Abstract, Exif.Image.ImageDescription
        
    def display_size(self, img):
        # Make a copy
        img = magick.Image(img) 
        img.sample('640x480')
        # Resize


if __name__ == '__main__':
    pass

