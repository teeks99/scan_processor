import PythonMagick as magick
from gi.repository import GExiv2
import json
from collections import deque
import datetime
import os

# The areas in each template are order dependant and it is important
# that the pictures are recorded in the json file in this order as well
# See the .svg templates
templates = {}

areas = []
areas.append({'x':0,'y':0,'h':360,'w':540,'dpi':90,'rotation':0})
areas.append({'x':0,'y':450,'h':540,'w':360,'dpi':90,'rotation':90})
areas.append({'x':405,'y':450,'h':540,'w':360,'dpi':90,'rotation':90})
templates['4x6'] = areas

areas = []
areas.append({'x':0,'y':0,'h':450,'w':630,'dpi':90,'rotation':0})
areas.append({'x':0,'y':540,'h':450,'w':630,'dpi':90,'rotation':0})
templates['5x7'] = areas

display_sized_path="disp/"
scanner_dpi=600

def zero_trim(number_string):
    while number_string.starts_with("0"):
        number_string = number_string[1:]
    return int(number_string)

def zero_pad(number, digits):
    number_string = str(number)
    while len(number_string) < digits:
        number_string = "0" + number_string
    return number_string
    
def scale_area_dpi(area, new_dpi):
    new_area = {}
    old_dpi = area['dpi']
    new_area['x'] = area['x'] * new_dpi / old_dpi
    new_area['y'] = area['y'] * new_dpi / old_dpi
    new_area['h'] = area['h'] * new_dpi / old_dpi
    new_area['w'] = area['w'] * new_dpi / old_dpi
    return new_area

class ImageSet(object):
    def __init__(self):
        self.make_display = True
        self.make_html = True
        
    def process(self, json_file):
        self.data = json.dump(json_file)
        self.generate_special_lookup()
        self.developed = datetime.datetime.strptime(self.data['develop_date'],
            "%Y-%m-%d")
        
        if self.make_display:
            self.display_path = display_sized_path
            # Make directory
            if not os.path.exists(self.display_path):
                os.makedirs(self.display_path)
        
        self.raw_start_num = zero_trim(self.data['raw_start'])
        self.raw_end_num = zero_trim(self.data['raw_end'])
        
        self.current_image_number = 0
        self.start_number_num = zero_trim(self.data['start_number'])
        self.image_num_strs = deque()
        for raw_num in range(raw_start_num, raw_end_num):
            images = self.split(raw_num)
            
            # An order-dependant deque
            while images:
                image = images.popleft()
                img_num = self.start_number_num + self.current_image_number
                img_num_str = zero_pad(img_num, 5)
                
                self.rotate(image)
                
                self.last_digitized = datetime.datetime.now()
                    
                if self.make_display:
                    self.display_size(image)
                    
                image.write(img_num_str + '.jpg')
                self.image_num_strs.append(img_num_str)

                if img_num_str in self.lookup:
                    self.add_comment(img_num_str + '.jpg', self.lookup[img_num_str]['comment'])

                # Increment after
                self.current_image_number += 1
                
        if self.make_html:
            self.generate_html()
            
    
    def generate_special_lookup(self):
        self.lookup = {}
        for img in self.data['special_images']:
            self.lookup[img['number']] = img
        
    def split(self, raw_num):
        # Open Raw with imagemagick (format r00000.jpg)
        data=file('r' + zero_fill(raw_num, 5) + '.jpg','rb').read()
        raw=magick.Image(magick.Blob(data))
  
        images = deque()
        for area in templates[self.data['size']]:
            images.append(self.crop(raw, area))          
            
        data.close()
        return images
            
    def crop(raw, area):
        # Make a copy of the raw image
        img = magick.Image(raw)
        
        area = scale_area_dpi(area, scanner_dpi)

        # Use imagemagick to crop
        rect = "%sx%s+%s+%s" % (area['w'], area['h'], area['x1'], area['y1'])
        img.crop(rect)
        
        return img
        
    def rotate(img, area, rotation="landscape"):
        if (rotation=="landscape" and area['rotation'] == 90) or 
            (rotation=="portrait" and area['rotation'] == 0):
            img.rotate(90)            
        
    def add_comment(img_path, comment="", rotation="landscape"):
        # Comment tags used by various programs: http://redmine.yorba.org/projects/shotwell/wiki/PhotoTags
        # All the supported tags: http://www.exiv2.org/metadata.html
        metadata = GExiv2.Metadata(img_path)

        metadata[Iptc.Application2.DateCreated] = self.developed.date().strftime('%Y%m%d')
        metadata[Iptc.Application2.DigitizationDate] = self.last_digitized.date().strftime('%Y%m%d')
        metadata[Iptc.Application2.DigitizationTime] = self.last_digitized.time().strftime('%H%M%S%z')
        metadata[Exif.Photo.DateTimeOriginal] = self.developed.date().strftime('%Y-%m-%d')
        metadata[Exif.Photo.DateTimeDigitized] = self.last_digitized.strftime('%Y-%m-%d %H:%M:%S')

        metadata[Iptc.Application2.Caption] = comment
        metadata[Exif.Image.ImageDescription] = comment

        # We already rotated correctly, so specify that there are no further
        # rotations.
        #See: http://sylvana.net/jpegcrop/exif_orientation.html
        metadata[Exif.Image.Orientation] = 1            
            
        metadata.save_file()
            
    def display_size(self, img):
        # Make a copy
        img = magick.Image(img) 
        # Resize
        img.sample('640x480')
        img_num_str = zero_pad(self.start_number_num + 
            self.current_image_number, 5)

        img_path = self.display_path + img_num_str + '.jpg'            
        img.write(img_path)

        if img_num_str in self.lookup:
            self.add_comment(img_path, self.lookup[img_num_str]['comment'])
        
    def generate_html(self, filename="view.html"):
        file = open(filename, 'w')
        file.write('<html>\n')
        file.write('<head>\n')
        file.write('    <title>Scanned Images</title>\n')
        file.write('</head>\n')
        file.write('<body>\n')
        file.write('    <h1>Scanned Images</h1>\n')
        file.write('    <p>\n')
        file.write('        Images Developed on' + self.data['develop_date'] + 
            '<br>\n')
        file.write('        Comments written on the enevelop:<br>\n')
        # TODO Escape the comments string
        file.write('        ' + self.data['envelop_comments'] +'<br>\n')
        file.write('    </p>\n')

        while self.image_num_strs:
            img_num_str = self.image_num_strs.popleft()
            file.write('    <p>\n')
            file.write('        <a href="' + img_num_str + '.jpg">\n')
            file.write('            <img src="' + self.display_path + 
                img_num_str + '.jpg" />\n')
            if img_num_str in self.lookup:
                if 'comment' in self.lookup[img_num_str]:
                    # TODO Escape the comments string
                    file.write('            <br />\n')
                    file.write('            ' + 
                        self.lookup[img_num_str]['comment'] + '\n')                
            file.write('        </a>\n')
            file.write('    </p>\n')
        
        
        file.write('</body>\n')
        file.write('</html>\n')
        file.close()

if __name__ == '__main__':
    pass

