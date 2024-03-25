import os
import json
import datetime


def get_all_post_names(directory):
    return_names = []

    # Scan for files
    for entry in os.scandir(directory):
        if entry.name.find("EXAMPLE") == -1:  # Don't scan example files
            if entry.name.find("_meta.json") != -1:
                return_names.append(entry.name[0:entry.name.find("_meta.json")])
                print("Found ", entry.name)

    return return_names


def get_list_of_tags(directory):
    return_tags = []

    # Scan for files
    for entry in os.scandir(directory):
        if entry.name.find("EXAMPLE") == -1:  # Don't scan example files
            if entry.name.find("_meta.json") != -1:
                with open(directory + entry.name) as post_metadata:
                    metadata_json = json.load(post_metadata)
                    for tag in metadata_json["tags"]:
                        if tag not in return_tags:
                            return_tags.append(tag)
                            print("Found", tag, "( in", entry.name,")")

    return return_tags


def get_all_posts_with_tag(directory, tag, maximum=0):
    return_names = []

    # Scan for files
    for entry in os.scandir(directory):
        if entry.name.find("EXAMPLE") == -1:  # Don't scan example files
            if entry.name.find("_meta.json") != -1:
                with open(directory + entry.name) as post_metadata:
                    metadata_json = json.load(post_metadata)
                    for post_tag in metadata_json["tags"]:
                        if tag == post_tag:
                            return_names.append((entry.name[0:entry.name.find("_meta.json")], metadata_json))
                            print("Found", tag, "( in", entry.name, ")")
        if len(return_names) >= maximum > 0:
            break

    # Sort (latest posts come first)
    return_names = sorted(return_names, key=lambda name: datetime.datetime.strptime(name[1]["post_date"], "%Y/%m/%d"), reverse=True)

    return return_names
