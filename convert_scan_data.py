"""
This script will go through the scans and convert the old-format data*.txt
to the new format data*.json files.

**** Old Format ****
start=12345
end=12355
raw_start=r34567
raw_end=r34570
develop_date=A date string, will not be processed?
all=there is something here
12347=this is an individual one
12352=this is another individual one
...

**** New Format ****
{
    "raw_start":"34567",
    "raw_end":"89012",
    "develop_date":"A date string",
    "envelop_comments":"there is something here",
    "start_number":"12345",
    "number_of_images":10,
    "special_images": [
        {"number":"12347","comment":"this is an individual one"},
        {"number":"12352","comment":"this is another individual one"}
    ]
}

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

def convert_all():
    f = open("overall.json",'r')
    number_old_format = json.load(f)["number_of_old_format"]
    f.close()    
    
    for dir_number in range(1,number_old_format+1):
        dir_number_str = zero_pad(dir_number, 3)
        
        new = {}
        new['size'] = 'manual'
        new['special_images'] = []
        old = open(dir_number_str + "/data_" + dir_number_str + ".txt",'r')
        
        start_str = old.readline().split('=')
        if start_str[0] != 'start':
            print("Dir: " + dir_number_str + " does not have a correctly formatted data_*.txt start")
        new['start_number'] = start_str[1].rstrip('\n')
        
        end_str = old.readline().split('=')
        if end_str[0] != 'end':
            print("Dir: " + dir_number_str + " does not have a correctly formatted data_*.txt end")
        # Add the +1 because if your start is 12345 and end is 12346 you have two images
        new['number_of_images'] = zero_trim(end_str[1]) - zero_trim(start_str[1]) + 1 
        
        raw_start_str = old.readline().split('=r')
        if raw_start_str[0] != 'raw_start':
            print("Dir: " + dir_number_str + " does not have a correctly formatted data_*.txt raw_start")
        new['raw_start'] = raw_start_str[1].rstrip('\n')
        
        raw_end_str = old.readline().split('=r')
        if raw_end_str[0] != 'raw_end':
            print("Dir: " + dir_number_str + " does not have a correctly formatted data_*.txt raw_end")
        new['raw_end'] = raw_end_str[1].rstrip('\n')

        develop_str = old.readline()
        if develop_str[:12] != 'develop_date':
            print("Dir: " + dir_number_str + " does not have a correctly formatted data_*.txt develop_date")
        date_str = develop_str[13:].rstrip('\n')
        date = None
        if (date_str == "") or (date_str == "various"):
            date = datetime.datetime(1900, 1, 1)
        else:
            date = datetime.datetime.strptime(date_str, "%B %d, %Y")
        new['develop_date'] = date.strftime("%Y-%m-%d") #develop_str[13:].rstrip('\n')
        
        all_str = old.readline()
        all_start = all_str[:3]
        if all_str[:3] != 'all':
            print("Dir: " + dir_number_str + " does not have a correctly formatted data_*.txt all")
        new['envelop_comments'] = all_str[4:].rstrip('\n')
        
        for line in old.readlines():
            if len(line) > 6 and line[5] == '=':
                img = {'number':line[:5], 'comment':line[6:].rstrip('\n')}
                new['special_images'].append(img)
        
        old.close()
    
        new_file = open(dir_number_str + "/data_" + dir_number_str + ".json",'w')
        json.dump(new, new_file, indent=True)
        new_file.close()


if __name__ == '__main__':
    convert_all()
