"""
This script will create an index page of all the scanned images.


"""

import json
import datetime

def zero_trim(number_string):
    while number_string.startswith("0") and len(number_string) > 1:
        number_string = number_string[1:]
    return int(number_string)

def zero_pad(number, digits):
    number_string = str(number)
    while len(number_string) < digits:
        number_string = "0" + number_string
    return number_string

def create_index():
    f = open("overall.json",'r')
    total_number_of_packets = json.load(f)["total_number_of_packets"]
    f.close()    

    index = open("view_index.html", "w")
    write_header(index)
    
    for dir_number in range(1,total_number_of_packets+1):
        dir_number_str = zero_pad(dir_number, 3)

        jf = open(dir_number_str + "/data_" + dir_number_str + ".json", 'r')
        packet = json.load(jf)
        

        index.write('        <li>\n')
        index.write('            <p>\n')
        index.write('            <a href="' + dir_number_str + '/view.html">\n')
        index.write('            Packet Number: ' + dir_number_str + '<br />\n')
        index.write('            Develop Date: ' + packet['develop_date'] + '<br />\n')
        index.write('            Envelop Comments: ' + packet['envelop_comments'] + '\n')
        index.write('            </a>\n')
        index.write('            </p>\n')
        index.write('        </li>\n')

    write_footer(index)
    index.close()

def write_header(index):
    index.write('<html>\n')
    index.write('<head>\n')
    index.write('    <title>Scanned Images Index</title>\n')
    index.write('</head>\n')
    index.write('<body>\n')
    index.write('    <h1>Scanned Images Index</h1>\n')
    index.write('    <p>\n')
    index.write('        Last Updated on: ' + datetime.datetime.now().strftime('%Y-%m-%d') + '\n')
    index.write('    </p>\n')
    index.write('    <ul>\n')

def write_footer(index):
    index.write('    </ul>\n')
    index.write('</body>\n')
    index.write('</html>\n')   
        


if __name__ == '__main__':
    create_index()
