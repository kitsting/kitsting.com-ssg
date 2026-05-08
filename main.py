import json
import os
import shutil
import filecmp
import pathlib
import shlex
import argparse

import post_scanner
import generator
from html_helper import build_template
from html_helper import handle_components



def main():

### Initial Load and Checks ###

    # Set working directory
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    print("Working in", dname)

    # Load the config file
    print("Reading config file...")
    with open("config.json") as config_read:
        config = json.load(config_read)
    print("Config file loaded!")

    #Don't proceed if there is no input directory
    if not os.path.isdir(config["input_dir"]):
        print("No input directory! Stopping...")
        exit


    # Parse commandline arguments
    mode_hard = False
    mode_push = False

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rebuild", help="Hard-reset mode, wipes output dir before building", action='store_true')
    parser.add_argument("-p", "--push", help="Push changed files to Neocities", action='store_true')
    parser.add_argument("-f", "--flush", help="Forget any previously changed files", action='store_true')
    args = parser.parse_args()

    if args.rebuild:
        mode_hard = True
        print("Hard-reset mode is ON")

        # Clear the output folder
        if os.path.isdir(config["output_dir"]):
            shutil.rmtree(config["output_dir"], True)
        os.mkdir(config["output_dir"])

    if args.push:
        mode_push = True
        print("Push mode is ON")

    if not args.flush:
        # Read any stored changed files from previous executions
        if os.path.isfile("changed"):
            print("Loading changed files...")
            with open("changed", 'r') as file:
                for line in file:
                    post_scanner.changed_files.append(line.strip())


    if os.path.isdir("temp/"):
        shutil.rmtree("temp/", True)
    os.mkdir("temp/")


    # Clear out the output folder if necessary
    if mode_hard:
        if os.path.isdir(config["output_dir"]):
            shutil.rmtree(config["output_dir"], True)
        os.mkdir(config["output_dir"])


### Generate the blogposts themselves ###


    # Scan for posts
    print("Scanning for posts...")
    post_names = post_scanner.get_all_post_names(config["input_dir"])

    # Generate posts
    for name in post_names:
        # Check to make sure a content file exists
        if not os.path.isfile(name + "index.md"):
            print("Content file " + name + "index.md not found, skipping...")
            break
        generator.generate_blog_post(name, config)


### Scan for tags and generate the browse pages ###


    # Scan for tags
    print("Scanning for tags...")
    taglist = post_scanner.get_list_of_tags(config["input_dir"])
    print("Finished scanning")

    tag_html = ""
    for tag in taglist:
        # Get all posts with the tag
        tag_names = post_scanner.get_all_posts_with_tag(config["input_dir"], tag)

        # Generate the post previews
        post_previews = ""
        for _, name in enumerate(tag_names):
            post_previews += build_template("templates/post_preview_template.html",
                                            "../"*config["browse_dir"].count("/") + name[0],
                                            name[1]["post_name"],
                                            name[1]["post_date"])

        # Put the previews in the browse page template
        browse_content = build_template("templates/browse_page_template.html",
                                        tag,
                                        post_previews)

        # Put the browse page template in the main content template
        main_content = build_template("templates/main_template_no_sidebar.html",
                                      browse_content)

        # Put the main content template in the base template
        final_content = build_template("templates/base_template.html",
                                       "Posts tagged with '{}'".format(tag),
                                       ("../"*config["browse_dir"].count("/"))+"favicon.ico",
                                       "../"*config["browse_dir"].count("/"),
                                       "../background.png",
                                       main_content)

        # Write out
        out_name = config["output_dir"] + config["browse_dir"] + tag + ".html"
        temp_path = post_scanner.write_temp_html(out_name, final_content)
        
        post_scanner.write_if_not_exists(temp_path, out_name)


        # Get the count of articles with a tag to show on the main browse page
        if len(tag_names) == 1:
            tag_html += "<p><a href={}.html>{} ({} article)</a><p>".format(tag, tag, len(tag_names))
        else:
            tag_html += "<p><a href={}.html>{} ({} articles)</a><p>".format(tag, tag, len(tag_names))


### Generate main browse page ###


    # Generate browse page
    browse_root_content = build_template("templates/browse_root_template.html", tag_html)

    main_content = build_template("templates/main_template_no_sidebar.html", browse_root_content)

    final_content = build_template("templates/base_template.html",
                                   "Browsing all tags",
                                   ("../"*config["browse_dir"].count("/")) + "favicon.ico",
                                   "../"*config["browse_dir"].count("/"),
                                   "../background.png",
                                   main_content)

    # Write out
    out_name = config["output_dir"] + config["browse_dir"] + "index.html"
    temp_path = post_scanner.write_temp_html(out_name, final_content)
    
    post_scanner.write_if_not_exists(temp_path, out_name)



### Populate other HTML pages ###


    # Get HTML pages that need to be updated
    html_pages = post_scanner.get_all_html_files(config["input_dir"])

    print("Found "+ str(len(html_pages)) +" HTML pages")

    for page in html_pages:
        content_html = open(config["input_dir"]+page).read()
        content_html = handle_components(content_html, config["input_dir"], page)

        # Write out
        out_name = config["output_dir"] + page
        temp_path = post_scanner.write_temp_html(out_name, content_html)

        post_scanner.write_if_not_exists(temp_path, out_name)



### Copy any other files that might be present

    files = post_scanner.scan_for_misc_files(config["input_dir"], post_names)

    for file in files:
        outfile = file.replace(config["input_dir"], config["output_dir"])
        post_scanner.write_if_not_exists(file, outfile)


### Wrap up ###

    if os.path.isdir("temp/"):
        shutil.rmtree("temp/", True)


    print("Files to be uploaded:\n", post_scanner.changed_files)

    if mode_push:
        #Push to Neocities
        pass
    else:
        #Store the changed files for later
        with open("changed", "w") as file:
            for path in post_scanner.changed_files:
                file.write(path + "\n")


if __name__ == "__main__":
    main()
