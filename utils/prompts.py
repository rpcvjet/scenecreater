def build_scene_prompt(char1, char2, sample_lines):
    with open("prompt_template.txt", "r") as f:
        template = f.read()
    return template.format(char1=char1, char2=char2, sample_lines=sample_lines)

