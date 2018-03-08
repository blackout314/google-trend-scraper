import webbrowser
import time
import os
import shutil
import copy
import re
import csv
import numpy as np
import sys
import json
import urllib
from datetime import datetime, timedelta
import requests

def get_buckets(start_date, end_date):
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    bucket_limits = [start_date_dt]
    left_limit = start_date_dt
    while left_limit <= end_date_dt:
        new_limit = left_limit + timedelta(days=181)
        if new_limit < end_date_dt:
            bucket_limits.append(new_limit)
        left_limit = new_limit
    bucket_limits.append(end_date_dt)
    return bucket_limits

def get_data(bucket_start_date,bucket_end_date, keyword):
    bucket_start_date_printed = datetime.strftime(bucket_start_date, '%Y-%m-%d')
    bucket_end_date_printed = datetime.strftime(bucket_end_date, '%Y-%m-%d')
    time_formatted = bucket_start_date_printed + '+' + bucket_end_date_printed

    req = {"comparisonItem":[{"keyword":keyword, "geo":geo, "time": time_formatted}], "category":category,"property":""}
    hl = "en-GB"
    tz = "-120"

    explore_URL = 'https://trends.google.com/trends/api/explore?hl={0}&tz={1}&req={2}'.format(hl,tz,json.dumps(req).replace(' ','').replace('+',' '))
    return requests.get(explore_URL).text

def get_token(response_text):
    try:
        return response_text.split('token":"')[1].split('","')[0]
    except:
        return None

def get_csv_request(response_text):
    try:
        return response_text.split('"widgets":')[1].split(',"lineAnno')[0].split('"request":')[1]       
    except:
        return None

def get_csv(response_text):
    request = get_csv_request(response_text)
    token = get_token(response_text)

    csv = requests.get('https://www.google.com/trends/api/widgetdata/multiline/csv?req={0}&token={1}&tz=-120'.format(request,token))
    return csv.text.encode('utf8')

def get_daily_frames(start_date, end_date, keyword, outputfile):

    bucket_list = get_buckets(start_date, end_date)
    frames = []
    for i in range(0,len(bucket_list) - 1):
        resp_text = get_data(bucket_list[i], bucket_list[i+1], keyword)
        frames.append((get_csv(resp_text)))

    file = open(outputfile, 'w')
    file.write(''.join(frames))
    file.close()

def get_weekly_frame(start_date, end_date, keyword, outputfile):

    if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=180):
        print 'No need to stitch; your time interval is short enough. '
        return None
    else:
        resp_text = get_data(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d'), keyword)
        file = open(outputfile, 'w')
        file.write(get_csv(resp_text))
        file.close()

if __name__ == '__main__':

    start_date = sys.argv[1]
    end_date = sys.argv[2]
    outputfile = sys.argv[3]
    geo = ''
    category = 22
    keywords = '+'.join(sys.argv[4:])

    daily_frames = get_daily_frames(start_date, end_date, keywords, outputfile)
    # weekly_frame = get_weekly_frame(start_date, end_date, keywords, outputfile)

