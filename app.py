from intrat.parse_zwo import ZwoParser
from intrat.ai_prompts.caller import WorkoutAI

import streamlit as st
import xml.etree.ElementTree as ET
from io import StringIO


if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


def add_message(role, message):
    emoji = "🚴" if role == "user" else "🧠"
    st.session_state["chat_history"].append((emoji, role, message))


def display_chat():
    for emoji, role, message in st.session_state["chat_history"]:
        with st.container():
            col1, col2 = st.columns([1, 20])
            with col1:
                st.write(emoji)
            with col2:
                st.markdown(f"**{role.capitalize()}:** {message}")


def parse_uploaded_file(uploaded_file) -> list:
    try:
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        zwo_parser = ZwoParser(StringIO(uploaded_file.getvalue().decode()))
        zwo_parser.parse()
        return zwo_parser.workout_segments
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return []


def main():
    st.title("Workout analysis AI")
    st.write(
        """This is a demo of a workout analysis AI. 
        The AI takes a .zwo file as input and outputs a workout analysis, including scientific justification for the intervals it finds within the workout."""
    )

    
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    model = st.selectbox("Select a model", ["gpt-4", "gpt-3.5-turbo"])
    is_initialised = False
    if api_key:
        workout_ai = WorkoutAI(model=model ,api_key=api_key)
        uploaded_file = st.file_uploader("Upload a .zwo file", type="zwo")

        display_chat()

        if uploaded_file is not None and is_initialised is False:
            with st.spinner("Analysing workout..."):
                workout_segments = parse_uploaded_file(uploaded_file)
                if workout_segments:
                    workout_data = str(workout_segments)
                    ai_response = workout_ai.get_response(workout_data)

        if is_initialised:
            user_input = st.text_input("Ask the AI a question")

            if st.button("Send"):
                if user_input:
                    add_message("user", user_input)
                    ai_response = workout_ai.get_response(user_input)
                    add_message("ai", ai_response)


if __name__ == "__main__":
    main()
