import json
import os
import shutil
import filecmp
import pathlib

import post_scanner
import generator
from html_helper import build_template



def main():

### Initial Load and Checks ###

    # Load the config file
    print("Reading config file...")
    with open("config.json") as config_read:
        config = json.load(config_read)
    print("Config file loaded!")

    #Don't proceed if there is no input directory
    if not os.path.isdir(config["input_dir"]):
        print("No input directory! Stopping...")
        exit

    # Clear out the output folder if necessary
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
        if not os.path.isfile(config["input_dir"] + name + "index.md"):
            print("Content file " + config["input_dir"] + name + "index.md not found, skipping...")
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
            print(name)
            post_previews += build_template(config["templates_loc"] + "post_preview_template.html",
                                            "../"*config["browse_dir"].count("/") + name[0],
                                            name[1]["post_name"],
                                            name[1]["post_date"])

        # Put the previews in the browse page template
        browse_content = build_template(config["templates_loc"] + "browse_page_template.html",
                                        tag,
                                        post_previews)

        # Put the browse page template in the main content template
        main_content = build_template(config["templates_loc"] + "main_template_no_sidebar.html",
                                      browse_content)

        # Put the main content template in the base template
        final_content = build_template(config["templates_loc"] + "base_template.html",
                                       "Posts tagged with '{}'".format(tag),
                                       ("../"*config["browse_dir"].count("/"))+"favicon.ico",
                                       "../"*config["browse_dir"].count("/"),
                                       "../background.png",
                                       main_content)

        # Write out
        if not os.path.isdir(config["output_dir"] + config["browse_dir"]): # Make the appropriate folder if it doesn't exist already
            os.makedirs(config["output_dir"] + config["browse_dir"], exist_ok=True)
        with open(config["output_dir"] + config["browse_dir"] + tag + ".html", 'w') as write_out:
            write_out.write(final_content)

        print("Generated browse page for", tag)

        # Get the count of articles with a tag to show on the main browse page
        if len(tag_names) == 1:
            tag_html += "<p><a href={}.html>{} ({} article)</a><p>".format(tag, tag, len(tag_names))
        else:
            tag_html += "<p><a href={}.html>{} ({} articles)</a><p>".format(tag, tag, len(tag_names))


### Generate main browse page ###


    # Generate browse page
    browse_root_content = build_template(config["templates_loc"] + "browse_root_template.html",
                                         tag_html)
    main_content = build_template(config["templates_loc"] + "main_template_no_sidebar.html",
                                  browse_root_content)
    final_content = build_template(config["templates_loc"] + "base_template.html",
                                   "Browsing all tags",
                                   ("../"*config["browse_dir"].count("/")) + "favicon.ico",
                                   "../"*config["browse_dir"].count("/"),
                                   "../background.png",
                                   main_content)
    if not os.path.isdir(config["output_dir"] + config["browse_dir"]):  # Make the appropriate folder if it doesn't exist already
        os.mkdir(config["output_dir"] + config["browse_dir"])
    with open(config["output_dir"] + config["browse_dir"] + "index.html", 'w') as write_out:
        write_out.write(final_content)
        print("Generated 'all tags' page")



### Populate other HTML pages ###


    # Generate the main page
    # Get all posts with the tag
    tag_names = post_scanner.get_all_posts_with_tag(config["input_dir"], "blogpost")

    # Generate the post previews
    post_previews = ""
    for _, name in enumerate(tag_names):
        post_previews += build_template(config["templates_loc"] + "post_preview_template.html",
                                        name[0],
                                        name[1]["post_name"],
                                        name[1]["post_date"])

    # Put the previews in the browse page template
    browse_content = build_template(config["templates_loc"] + "blog_index_template.html",
                                    post_previews)

    # Put the browse page template in the main content template
    main_content = build_template(config["templates_loc"] + "main_template_no_sidebar.html",
                                  browse_content)

    # Put the main content template in the base template
    final_content = build_template(config["templates_loc"] + "base_template.html",
                                   "Kitsting's Little Blog",
                                   ("../" * (config["default_levels_from_root"]-1)) + "favicon.ico",
                                   "../" * (config["default_levels_from_root"]-1),
                                   "background.png",
                                   main_content)
    # Write out
    if not os.path.isdir(config["output_dir"] + "blog"): # Make the appropriate folder if it doesn't exist already
        os.mkdir(config["output_dir"] + "blog")
    with open(config["output_dir"] + "blog/index.html", 'w') as write_out:
        write_out.write(final_content)




### Check for changed files ###

    # Make a copy of the out folder to check for changed files later
    if not os.path.isdir("out_old"): # Make the appropriate folder if it doesn't exist already
        os.mkdir("out_old")

    # Check for new and changed files
    old_path = pathlib.Path("out_old")
    out_path = pathlib.Path(config["output_dir"])

    print("Scanning for new and changed files...")
    changed_files = []
    for outfile in out_path.rglob("*"):
        outfile_name = str(outfile)[len(config["output_dir"]):]
        for oldfile in old_path.rglob("*"):
            oldfile_name = str(oldfile)[len("out_old/"):]
            if oldfile_name == outfile_name and oldfile_name.find(".") != -1:
                if not filecmp.cmp(str(oldfile), str(outfile), False):
                    changed_files.append(str(outfile))
                    print("Changed file:", str(outfile))

        if (not os.path.isfile("out_old/" + outfile_name)) and outfile_name.find(".") != -1:
            changed_files.append(str(outfile))
            print("New file:", str(outfile))

    shutil.rmtree("out_old", True)
    shutil.copytree(config["output_dir"], "out_old")

    print("Files to be uploaded:\n", changed_files)


if __name__ == "__main__":
    main()
