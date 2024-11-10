def build_template(template_file, *text):
    # Load text from template file
    with open(template_file) as template:
        return_text = template.read()

    # Add text in a loop
    for index, arg in enumerate(text):
        return_text = return_text.replace("{"+str(index)+"}", arg)

    # Return text
    return return_text

