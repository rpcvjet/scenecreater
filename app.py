import anthropic
import os
import streamlit as st
import pdfplumber as pdfplumber
from dotenv import load_dotenv
from utils.pdf_parser import extract_character_names, parsetext_tagged
from utils.prompts import build_scene_prompt
from utils.docx_exporter import save_scene_as_docx
from utils.extract_text import extract_mixed_layout_lines
from datetime import datetime
load_dotenv()
api_key = os.getenv("CLAUDE_API_KEY")

client = anthropic.Anthropic(api_key=api_key)


uses_bold = st.radio(
    "2. Are speaker names bolded?",
    options=["Yes", "No"]
)


uploaded_file = st.file_uploader(
    'Upload a Play For Extraction',
    type=['pdf'], 
    accept_multiple_files=False, 
    label_visibility="visible")

if uploaded_file is not None:
    st.success("File uploaded successfully! extracting text...")
    with pdfplumber.open(uploaded_file) as pdf:
        lines = extract_mixed_layout_lines(pdf)
        character_names = extract_character_names(pdf)
        dialogue = parsetext_tagged(lines, character_names)

    characters = sorted(character_names)

    selected = st.multiselect("Choose two characters for the scene", characters, max_selections=2)

    if len(selected) == 2:
        filtered = [d for d in dialogue if d["character"] in selected]
        formatted = "\n".join(
            f"{entry['character']} (p{entry['page']}, {entry['column']}): {entry['line']}"
            for entry in filtered
        )

        st.write(f"Found {len(filtered)} lines between {selected[0]} and {selected[1]}")
        st.text_area("🧾 Preview Filtered Dialogue", formatted, height=300)  # optional preview

        if st.button("Generate new scene"):
            if len(filtered) < 10:
                st.warning("Not enough dialogue to build a convincing scene.")
            else:
                with st.spinner("Claude is writing your new scene..."):
                    prompt = build_scene_prompt(selected[0], selected[1], formatted)
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1024,
                        temperature=0.7,
                        system="You are a brilliant playwright.",
                        messages=[{"role": "user", "content": prompt.strip()}]
                    )

                    scene_text = response.content[0].text
                    st.text_area("🎭 New Scene", scene_text, height=600)

                    if scene_text:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{selected[0]}_and_{selected[1]}_{timestamp}.docx"
                        docx_file_path = save_scene_as_docx(scene_text, filename)
                        with open(docx_file_path, "rb") as f:
                            st.download_button(
                                label="📄 Download Scene as .docx",
                                data=f,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )

    



