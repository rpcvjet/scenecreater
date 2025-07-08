from pathlib import Path
import streamlit as st


def build_scene_prompt(char1, char2, sample_lines):
    template_path = Path(__file__).parent / "prompt_template.txt"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(char1=char1, char2=char2, sample_lines=sample_lines)
