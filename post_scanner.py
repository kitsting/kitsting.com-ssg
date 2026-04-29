import os
import json
import datetime

def scantree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def get_all_post_names(directory):
    return_names = []

    # Scan for files
    for entry in scantree(directory):
        if (entry.name.find("EXAMPLE") == -1) and (entry.name.find("meta.json") != -1):  # Don't scan example files
            return_names.append(entry.path.replace(entry.name, "")) #Append the directory without the file name
            print("Found ", entry.path)

    print(return_names)
    return return_names


def get_all_html_files(directory):
    return_names = []

    # Scan for files
    for entry in scantree(directory):
        if entry.name.find("EXAMPLE") == -1:  # Don't scan example files
            if entry.name.find(".html") != -1:
                return_names.append(entry.path.replace(directory, ""))
                print("Found ", entry.path)

    return return_names



def get_list_of_tags(directory):
    return_tags = []

    # Scan for files
    for entry in scantree(directory):
        if entry.name.find("EXAMPLE") == -1:  # Don't scan example files
            if entry.name.find("meta.json") != -1:
                with open(entry.path) as post_metadata:
                    metadata_json = json.load(post_metadata)
                    for tag in metadata_json["tags"]:
                        if tag not in return_tags:
                            return_tags.append(tag)
                            print("Found tag ", tag, "(", entry.path, ")")

    return return_tags


def get_all_posts_with_tag(directory, tag, maximum=0):
    return_names = []

    # Scan for files
    for entry in scantree(directory):
        if (entry.name.find("EXAMPLE") == -1) and (entry.name.find("meta.json") != -1):  # Don't scan example files
            with open(entry.path) as post_metadata:
                metadata_json = json.load(post_metadata)
                for post_tag in metadata_json["tags"]:
                    if tag == post_tag:
                        return_names.append((entry.path.replace(entry.name, "").replace(directory, ""), metadata_json))

    print("Found", len(return_names), "posts tagged " + tag)

    # Sort (latest posts come first)
    return_names = sorted(return_names, key=lambda name: datetime.datetime.strptime(name[1]["post_date"], "%Y/%m/%d"), reverse=True)

    # Only return the top results if a maximum is specified
    if maximum > 0:
        return_names = return_names[:maximum]

    return return_names



def scan_for_misc_files(directory, blog_posts):
    return_names = []
    for entry in scantree(directory):
        if (any(x in entry.path for x in blog_posts) == False): # Don't scan files handled earlier by the post generator
            if entry.name.find(".html") == -1: # Don't scan html files, those were already handled in the last step
                return_names.append(entry.path)

    return return_names