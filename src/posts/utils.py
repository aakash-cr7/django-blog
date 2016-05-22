import datetime
import math
import re

from django.utils.html import strip_tags

def count_words(html_string):
    # Strip html tags from html
    words_string = strip_tags(html_string)
    count = len(re.findall(r'\w+', words_string))
    return count

def get_read_time(html_string):
    count = count_words(html_string)
    # Assuming a human can read 200 words per min
    read_time_min = math.ceil(count/200.0)
    # if using DateTimeField in models , then return read_time
    #read_time_sec = read_time_min * 60
    #read_time = str(datetime.timedelta(seconds = read_time_sec))
    #read_time = str(datetime.timedelta(minutes = read_time_min))
    return int(read_time_min)
