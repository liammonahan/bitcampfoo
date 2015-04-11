import json
import requests
from datetime import date, datetime

data_path = "../data/stalled-construction-sites-pristine.json"
save_path = "../data/%s"


def main():
    # retrieve all entries from pristine data where
    # complaint date falls after Jan 1st 2013
    filter_date = date(2013, 1, 1)
    new_data_path = save_path % 'stalled-construction-after-2013.json'
    filter_by_date(filter_date, new_data_path)


def get_coordinates(location_string):
    '''
    Return a (longitude, latitude) tuple given a location string

    A location string can be any location that can be reverse-geoencoded.
    E.g. 123 Fake Street, NYC
    '''
    response = requests.get(
        'http://maps.google.com/maps/api/geocode/json?address=%s' %
        location_string)
    location = response.json()['results'][0]['geometry']['location']
    return (location['lat'], location['lng'])


def filter_by_date(date_in, save_path):
    """Using the given json data, filter out the stalled construction
    entries that fall before or after a certain date and return the
    data as a json file. """

    output_json = {}
    output_json['objects'] = []
    objects = output_json['objects']
    # the original unmodified json data provided by NYC open data
    with open(data_path) as data_file:
        pristine_data = json.load(data_file)
        data_entries = pristine_data['data']
        complaint_date_idx = 14
        json_date_format = "%Y-%m-%dT%H:%M:%S"
        for entry in data_entries:
            raw_date = entry[complaint_date_idx]
            datetime_obj = datetime.strptime(raw_date, json_date_format)
            if datetime_obj.date() > date_in:
                objects.append(entry)

    with open(save_path, 'w+') as outfile:
        json.dump(output_json, outfile)


def read_json(file_path):
    with open(file_path) as data:
        json_data = json.load(data)
        return json_data


if "__main__" == __name__:
    main()
