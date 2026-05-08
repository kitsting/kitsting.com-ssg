import json
import shutil
import os
import shlex
import markdown

import post_scanner
from post_scanner import write_if_not_exists
from post_scanner import write_temp_html

def build_template(template_file, *text):
    # Load text from template file
    with open(template_file) as template:
        return_text = template.read()

    # Add text in a loop
    for index, arg in enumerate(text):
        return_text = return_text.replace("{"+str(index)+"}", arg)

    #Handle custom components
    return_text = handle_components(return_text)


    # Return text
    return return_text


def handle_components(text, input_dir = "in/", page_name = ""):
    figure_end = 0
    figure_count = text.count("{{")
    for idx in range(figure_count):
        figure_start = text.find("{{", figure_end)
        figure_end = text.find("}}", figure_start)
        figure_params = shlex.split(text[figure_start+2:figure_end])

        #Get X posts with specified tag
        if figure_params[0] == "tag":
            if len(figure_params) > 2:
                tag_names = post_scanner.get_all_posts_with_tag(input_dir, figure_params[1], int(figure_params[2]))
            else:
                tag_names = post_scanner.get_all_posts_with_tag(input_dir, figure_params[1])

            # Generate the post previews
            post_previews = ""
            for _, name in enumerate(tag_names):
                post_previews += build_template("templates/post_preview_template.html",
                                                "../"*page_name.count("/")+name[0],
                                                name[1]["post_name"],
                                                name[1]["post_date"])
                
            text = text.replace(text[figure_start:figure_end+2], post_previews)

        #Paste in components
        if figure_params[0] == "component":
            text = text.replace(text[figure_start:figure_end+2], build_template("components/" + figure_params[1] + ".html"))

    return text



# Takes an array of parameters as well as a path for media (images, etc) and returns a figure in the right format
def convert_to_figure(figure_params, components_path, media_path):
    files_used = []  # Keeps track of all the files that are referenced

    # Only use the component if it exists
    if os.path.isfile(components_path + figure_params[0] + ".html"):

        # Read the content of the component into memory
        with open(components_path + figure_params[0] + ".html") as compo_file:
            component_text = compo_file.read()

        # Iterate through the parameters
        for index, param in enumerate(figure_params[1:]):

            # Check if a file is being used or not
            if os.path.isfile(media_path + param):
                component_text = component_text.replace("{{"+str(index)+"}}", param)
                files_used.append(param)

            else:
                component_text = component_text.replace("{{"+str(index)+"}}", param)

        return component_text, files_used
    else:
        return "", []


def generate_blog_post(name, config):
    print("(", name, ") Generating page...")

    # Keep track of the files being used to copy later (all posts should have an icon.png)
    used_media = ["icon.png"]

    # Read json and get data
    with open(name + "meta.json") as article_metadata:
        article_info = json.load(article_metadata)

    # Determine if a sidebar file exists
    using_sidebar = os.path.isfile(name + "sidebar.md")

    # Read the markdown from the content file
    with open(name + "index.md", 'r') as readfile:
        content_html = markdown.markdown(readfile.read())

    # Convert the placeholder figures to actual figures
    print("(", name, ") Found about", content_html.count("{{"), "components")
    figure_end = 0
    while content_html.count("{{") != 0:
        figure_start = content_html.find("{{", figure_end)
        figure_end = content_html.find("}}", figure_start)
        figure_params = shlex.split(content_html[figure_start+2:figure_end])
        figure, files = convert_to_figure(figure_params, "components/", name + "/")
        for file in files:
            used_media.append(file)

        content_html = content_html.replace(content_html[figure_start:figure_end+2], figure, 1)

    # Read the markdown from the sidebar file (if applicable)
    if using_sidebar:
        with open(name + "sidebar.md", 'r') as readfile:
            sidebar_html = markdown.markdown(readfile.read())


    # Lowest Level (blog info and content)
    tags = ""
    for tag in article_info["tags"]:
        tags += "<a href=\"../browse/{}.html\">{}<a>, ".format(tag, tag)
    tags = tags[0:len(tags) - 2]

    main_content = build_template("templates/blogpost_header.html",
                                  article_info["post_name"],
                                  article_info["post_date"],
                                  tags,
                                  content_html)

    # Second Lowest Level (sidebar content (if applicable) and divs)
    if using_sidebar:
        page_content = build_template("templates/main_template_sidebar.html",
                                      sidebar_html,
                                      main_content)
    else:
        page_content = build_template("templates/main_template_no_sidebar.html", content_html)


    # Check automagically if a favicon file exists
    if os.path.isfile(name + "/favicon.ico"):
        favicon = "favicon.ico"
        used_media.append("favicon.ico")
    else:
        favicon = "/favicon.ico"  # Use the favicon at the site root if none exists

    # Check automagically if a background file exists
    if os.path.isfile(name + "/background.png"):
        background = "background.png"
        used_media.append("background.png")
    else:
        background = "../background.png"  # Use the background one level up if no custom background exists

    # Highest level (HTML header and navigation bar)
    final_content = build_template("templates/base_template.html",
                                   article_info["page_title"],
                                   favicon,
                                   "0", #Vestigial levels deep
                                   background,
                                   page_content)

    # Write out
    out_name = name.replace(config["input_dir"], config["output_dir"])
    temp_path = write_temp_html(out_name + "index.html", final_content)

    write_if_not_exists(temp_path, out_name + "index.html")

    # Copy files
    for file in used_media:
        write_if_not_exists(name + file, out_name + file)