import json
import shutil
import os
import shlex
import markdown

from html_helper import build_template
from convert_to_figure import convert_to_figure


blogpost_dir = "blogposts/"


def generate_blog_post(name, config):
    print("(", name, ") Generating page...")

    # Directories
    post_dir = config["input_dir"] + blogpost_dir
    templates_dir = config["templates_loc"]

    # Keep track of the files being used to copy later (all posts should have an icon.png)
    used_media = ["icon.png"]

    # Read json and get data
    with open(post_dir + name + "_meta.json") as article_metadata:
        article_info = json.load(article_metadata)

    # Determine if a sidebar file exists
    using_sidebar = os.path.isfile(post_dir + name + "_sidebar.md")

    # Read the markdown from the content file
    with open(post_dir + name + "_content.md", 'r') as readfile:
        content_html = markdown.markdown(readfile.read())

    # Convert the placeholder figures to actual figures
    print("(", name, ") Converting components...")
    figure_end = 0
    while content_html.count("{{") != 0:
        figure_start = content_html.find("{{", figure_end)
        figure_end = content_html.find("}}", figure_start)
        figure_params = shlex.split(content_html[figure_start+2:figure_end])
        figure, files = convert_to_figure(figure_params, config["components_loc"], post_dir + name + "_media/")
        for file in files:
            used_media.append(file)

        content_html = content_html.replace(content_html[figure_start:figure_end+2], figure, 1)

    # Read the markdown from the sidebar file (if applicable)
    if using_sidebar:
        with open(post_dir + name + "_sidebar.md", 'r') as readfile:
            sidebar_html = markdown.markdown(readfile.read())

    # Write the finished thing to the out folder
    print("(", name, ") Writing out...")
    if not os.path.isdir(config["output_dir"] + "blog"):  # Make the appropriate folder if it doesn't exist already
        os.mkdir(config["output_dir"] + "blog")

    if not os.path.isdir(config["output_dir"] + "blog/" + name):  # Make the appropriate folder if it doesn't exist already
        os.mkdir(config["output_dir"] + "blog/" + name)

    # Lowest Level (blog info and content)
    tags = ""
    for tag in article_info["tags"]:
        tags += "<a href=\"../browse/{}.html\">{}<a>, ".format(tag, tag)
    tags = tags[0:len(tags) - 2]

    main_content = build_template(templates_dir + "blogpost_header.html",
                                  article_info["post_name"],
                                  article_info["post_date"],
                                  tags,
                                  content_html)

    # Second Lowest Level (sidebar content (if applicable) and divs)
    if using_sidebar:
        page_content = build_template(templates_dir + "main_template_sidebar.html",
                                      sidebar_html,
                                      main_content)
    else:
        page_content = build_template(templates_dir + "main_template_no_sidebar.html", content_html)

    # Calculate levels from root
    levels_deep = "../" * config["default_levels_from_root"]

    # Check automagically if a favicon file exists
    if os.path.isfile(post_dir + name + "_media/favicon.ico"):
        favicon = "favicon.ico"
        used_media.append("favicon.ico")
    else:
        favicon = levels_deep + "favicon.ico"  # Use the favicon at the site root if none exists

    # Check automagically if a background file exists
    if os.path.isfile(post_dir + name + "_media/background.png"):
        background = "background.png"
        used_media.append("background.png")
    else:
        background = "../background.png"  # Use the background one level up if no custom background exists

    # Highest level (HTML header and navigation bar)
    final_content = build_template(templates_dir + "base_template.html",
                                   article_info["page_title"],
                                   favicon,
                                   levels_deep,
                                   background,
                                   page_content)

    # Write out
    with open(config["output_dir"] + "blog/" + name + "/index.html", 'w') as write_out:
        write_out.write(final_content)

    # Copy files
    for file in used_media:
        shutil.copy2(post_dir + name + "_media/" + file, config["output_dir"] + "blog/" + name + "/")

    print("(", name, ") Page Generated!! :>")