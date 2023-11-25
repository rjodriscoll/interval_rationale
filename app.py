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
    st.write("Chat history:")
    st.write('<div style="display: flex; flex-direction: column-reverse;">', unsafe_allow_html=True)
    for emoji, role, message in st.session_state["chat_history"]:
        if role == "user":
            st.markdown(
                f"""
                <div style="margin: 5px 0; display: flex; align-items: center;">
                    <div style="margin-right: 10px;">{emoji}</div>
                    <div style="line-height: 1.5; padding: 10px; background-color: #e5eff5; border-radius: 15px; max-width: 60%; margin-right: auto;">
                        {message}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:  # AI's messages
            st.markdown(
                f"""
                <div style="margin: 5px 0; display: flex; align-items: center; flex-direction: row-reverse;">
                    <div style="margin-left: 10px;">{emoji}</div>
                    <div style="line-height: 1.5; padding: 10px; background-color: #f0f0f0; border-radius: 15px; max-width: 60%; margin-left: auto;">
                        {message}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    st.write('</div>', unsafe_allow_html=True)


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
    st.title("Workout Analysis AI")
    st.write(
        "This is a demo of a workout analysis AI. "
        "The AI takes a .zwo file as input and outputs a workout analysis, "
        "including scientific justification for the intervals it finds within the workout."
    )

    with st.sidebar:
        api_key = st.text_input("Enter your OpenAI API Key and then press enter", type="password")
        model = st.selectbox("Select a model", ["gpt-4", "gpt-3.5-turbo"])
        temperature = st.slider("Select a model temperature", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

    if api_key:
        workout_ai = WorkoutAI(model=model, api_key=api_key, temperature=temperature)
        uploaded_file = st.file_uploader("Upload a .zwo file", type="zwo")

        if "is_initialised" not in st.session_state:
            st.session_state["is_initialised"] = False

        chat_container = st.container()

        if uploaded_file and not st.session_state["is_initialised"]:
            with st.spinner("Analysing workout..."):
                workout_segments = parse_uploaded_file(uploaded_file)
                if workout_segments:
                    workout_data = str(workout_segments)
                    ai_response = workout_ai.get_response(workout_data)
                    add_message("ai", ai_response)
                    st.session_state["is_initialised"] = True
                    with chat_container:
                        display_chat()


    if st.session_state.get("is_initialised", False):
        user_input = st.text_input("Ask the AI a question", key="user_input")

        if st.button("Send"):
            if user_input:
                with st.spinner("Asking the AI..."):
                    add_message("user", user_input)
                    ai_response = workout_ai.get_response(user_input)
                    add_message("ai", ai_response)
                with chat_container:
                    display_chat()

   


if __name__ == "__main__":
    main()
