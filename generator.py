import json
import shutil
import os
import shlex
import markdown

from html_helper import build_template
from html_helper import convert_to_figure
from post_scanner import write_if_not_exists
from post_scanner import write_temp_html


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

    # Make the appropriate folder if it doesn't exist already
    out_name = name.replace(config["input_dir"], config["output_dir"])
    temp_path = write_temp_html(out_name + "index.html", final_content)

    write_if_not_exists(temp_path, out_name + "index.html")

    # Copy files
    for file in used_media:
        write_if_not_exists(name + file, out_name + file)