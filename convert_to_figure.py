import os.path

# Priority for finding files to reference. Ideally uses the one with the lowest file size first
img_ext_priority = ["webp", "jpg", "png"]
audio_ext_priority = ["mp3"]

# Long HTML code is defined here, so it's not cluttering up code elsewhere
html_audiofile = ("<audio controls>"
                  "     <source src=\"{}\" type=\"audio/mpeg\">This browser can't play this audio :("
                  "</audio>")


# Takes an array of parameters as well as a path for media (images, etc) and returns a figure in the right format
def convert_to_figure(figure_params, media_path):
    files_used = []  # Keeps track of all the files that are referenced
    param_middle = ""  # Keeps track of the params used so far

    # Iterate through the parameters
    for index, param in enumerate(figure_params):
        match param:
            case "img":  # Image File
                if param != figure_params[-1]:
                    for ext in img_ext_priority:
                        filepath = media_path + figure_params[index + 1] + "." + ext
                        if os.path.isfile(filepath):
                            file_used = figure_params[index + 1] + "." + ext
                            param_middle += "<img src=\"{}\" class=\"post_img\"/>".format(file_used)
                            files_used.append(file_used)
                            break

            case "audio":  # Audio File
                if param != figure_params[-1]:
                    for ext in audio_ext_priority:
                        filepath = media_path + figure_params[index + 1] + "." + ext
                        if os.path.isfile(filepath):
                            file_used = figure_params[index + 1] + "." + ext
                            param_middle += html_audiofile.format(file_used)
                            files_used.append(file_used)
                            break

            case "autosize":  # Set the height of the media to 350px (should be used directly after a filename)
                param_middle = param_middle.replace("/>", " height=\"350px\"/>", 1)

            case "caption":  # Set a caption for the figure
                if param != figure_params[-1]:
                    param_middle += "<figcaption>{}</figcaption>".format(figure_params[index + 1])

    # Return the figure in the proper format, as well as a list of the paths of the files the figure references
    return "<figure class = \"post_figure\">{}</figure>".format(param_middle), files_used


