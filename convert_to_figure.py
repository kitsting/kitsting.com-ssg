import os.path


# Takes an array of parameters as well as a path for media (images, etc) and returns a figure in the right format
def convert_to_figure(figure_params, components_path, media_path):
    print("figure...")
    files_used = []  # Keeps track of all the files that are referenced

    print(components_path + figure_params[0] + ".html")
    if os.path.isfile(components_path + figure_params[0] + ".html"):
        print("is valid...")

        with open(components_path + figure_params[0] + ".html") as compo_file:
            component_text = compo_file.read()

        # Iterate through the parameters
        for index, param in enumerate(figure_params[1:]):
            print("check "+param)

            if os.path.isfile(media_path + param):
                component_text = component_text.replace("{{"+str(index)+"}}", param)
                files_used.append(param)

            else:
                component_text = component_text.replace("{{"+str(index)+"}}", param)

        return component_text, files_used
    else:
        return "", []


