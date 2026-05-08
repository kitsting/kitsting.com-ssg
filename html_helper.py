import shlex
import os.path

import post_scanner

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