# Libraries to be used ------------------------------------------------------------

import streamlit as st
import requests
import json
import os

# title and favicon ------------------------------------------------------------

st.set_page_config(page_title="Speech to Text Transcription App", page_icon="👨‍⚕️")

# _max_width_()

# logo and header -------------------------------------------------

st.text("")
st.image(
    "https://emojipedia-us.s3.amazonaws.com/source/skype/289/parrot_1f99c.png",
    width=125,
)

st.title("Speech to text transcription app")

st.write(
    """  
-   Upload a wav file, transcribe it, then export it to a text file!
-   Use cases: call centres, team meetings, training videos, school calls etc.
	    """
)

st.text("")
c1, c2, c3 = st.columns([1, 4, 1])
with c2:
    with st.form(key="my_form"):
        f = st.file_uploader("", type=[".wav"])
        st.info("upload a .wav file")
        submit_button = st.form_submit_button(label="Transcribe")

if f is not None:
    st.audio(f, format="wav")
    path_in = f.name
    f.seek(0, os.SEEK_END)
    getsize = f.tell() 
    getsize = round((getsize / 1e6), 1)

    if getsize < 10:  
        # To read file as bytes:
        bytes_data = f.getvalue()

        # Load your API key from an environment variable or secret management service
        api_token = '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'

        # endregion API key
        headers = {"Authorization": f"Bearer {api_token}"}
        API_URL = (
            "https://api-inference.huggingface.co/models/facebook/wav2vec2-base-960h"
        )

        def query(data):
            response = requests.request("POST", API_URL, headers=headers, data=data)
            return json.loads(response.content.decode("utf-8"))

        # st.audio(f, format="wav")
        data = query(bytes_data)

        values_view = data.values()
        value_iterator = iter(values_view)
        text_value = next(value_iterator)
        text_value = text_value.lower()

        st.info(text_value)

        st.download_button(
            "Download the transcription",
            text_value,
            file_name=None,
            mime=None,
            key=None,
            help=None,
            on_click=None,
            args=None,
            kwargs=None,
        )

    else:
        st.warning(
            "🚨 We've limited this demo to 10MB files. Please upload a smaller file."
        )
        st.stop()


else:
    path_in = None
    st.stop()

