#!/usr/bin/env python

import creds
import json
import requests
import sys

save_path = "../data/%s"
pristine_data_path = save_path % "stalled-construction-sites-pristine.json"
trimmed_data_path = save_path % "stalled-construction-after-2013.json"
addresses_data_path = save_path % "addresses.json"

GOOGLE_API_KEY = creds.GOOGLE_API_KEY

ADDRESSES = {}


def load_addresses():
    global ADDRESSES
    ADDRESSES = read_json(addresses_data_path)['addresses']


def save_addresses():
    write_json(addresses_data_path, {"addresses": ADDRESSES})


def main():
    new_data_path = trimmed_data_path
    trim_data(new_data_path)

    load_addresses('../data/addresses.json')

    output = {}
    output['objects'] = []
    output_json = output['objects']

    existing_addresses = {}

    input_json = read_json(trimmed_data_path)
    input_objects = input_json['objects']
    for complaint_entry in input_objects[:50]:
        address = get_address_from_entry(complaint_entry)
        complaint = get_complaint_dict(complaint_entry)
        if address in existing_addresses:
            existing_address = existing_addresses[address]
            existing_address['complaints'].append(complaint)
        else:
            new_address = get_google_maps_dict_from_entry(complaint_entry)
            if new_address is None:
                print "failed to get google maps data for %s" % address
                continue
            new_address['complaints'] = [complaint]
            existing_addresses[address] = new_address
    print json.dumps(existing_addresses,
                     indent=4, separators=(',', ':'))

    save_addresses('../data/addresses.json')


def get_complaint_dict(complaint_entry):
    complaint = {}
    complaint['complaint_number'] = complaint_entry[13]
    complaint['date_received'] = complaint_entry[14]
    return complaint


def get_google_maps_dict_from_entry(entry):
    address = get_address_from_entry(entry)
    return get_google_maps_result(address)


def get_address_from_entry(entry):
    '''
    Return a (latitude, longitude) tuple given a single json entry
    '''
    house_no = entry[11].strip()
    street = entry[12].strip()
    borough = entry[8].strip()
    address = '%s %s, %s, New York' % (house_no, street, borough)
    return address


def persist_address(address_string, coordinates):
    '''
    Write the coordnates hash to a json file if not already cached
    '''
    if address_string not in ADDRESSES:
        ADDRESSES[address_string] = coordinates


def get_google_maps_result(location_string):
    print "getting google maps result for '%s'" % location_string

    resp = requests.get(
        'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' %
        (location_string, GOOGLE_API_KEY)).json()['results']
    if len(resp) == 0:
        return None
    resp = resp[0]
    returning = {}
    returning['formatted_address'] = resp['formatted_address']
    returning['location'] = resp['geometry']['location']
    return returning


def trim_data(save_path):
    """Using the given json data, filter out the stalled construction
    entries that fall before or after a certain date and return the
    data as a json file. """

    complaint_numbers = {}
    output_json = {}
    output_json['objects'] = []
    objects = output_json['objects']
    # the original unmodified json data provided by NYC open data
    with open(pristine_data_path) as data_file:
        pristine_data = json.load(data_file)
        data_entries = pristine_data['data']
        for entry in data_entries:
            complaint_number = entry[13]
            if complaint_number in complaint_numbers:
                continue
            objects.append(entry)
            complaint_numbers[complaint_number] = True

    with open(save_path, 'w+') as outfile:
        json.dump(output_json, outfile)


def read_json(file_path):
    with open(file_path, 'r') as data:
        json_data = json.load(data)
        return json_data


def write_json(file_path, json_to_write):
    with open(file_path, 'w+') as f:
        json.dump(json_to_write, f, indent=4)

if "__main__" == __name__:
    main()
