# Libraries to be used ------------------------------------------------------------

import streamlit as st
import requests
import json
import os
import time
import boto3

import random
import string

import streamlit_ext as ste

os.environ['AWS_ACCESS_KEY_ID'] = st.secrets['AWS_id']
os.environ['AWS_SECRET_ACCESS_KEY'] = st.secrets['AWS_key']


s3 = boto3.client('s3')
transcribe = boto3.client('transcribe',region_name='us-east-1')


# title and favicon ------------------------------------------------------------

st.set_page_config(page_title="Speech to Text Transcription App", page_icon="👨‍⚕️")

# logo and header -------------------------------------------------

st.text("")
st.image(
    "https://emojipedia-us.s3.amazonaws.com/source/skype/289/parrot_1f99c.png",
    width=125,
)
st.title("Speech to text transcription app")
st.write(
    """  
-   Upload a mp3 file, transcribe it, then export it to a text file!
-   Use cases: call centres, team meetings, training videos, school calls etc.
	    """
)

st.text("")
c1, c2, c3 = st.columns([1, 4, 1])
with c2:
    with st.form(key="my_form"):
        f = st.file_uploader("", type=[".mp3"])
        st.info("upload a .mp3 file")
        submit_button = st.form_submit_button(label="Transcribe")

if f is not None:
    st.audio(f, format="mp3")
    path_in = f.name
    f.seek(0, os.SEEK_END)
    getsize = f.tell() 
    getsize = round((getsize / 1e6), 1)

    with st.spinner('Processing.. Please wait a minute'):
        if getsize < 20:
            # To read file as bytes:
            bytes_data = f.getvalue()
            filename='audio_file.mp3'
            with open(filename, 'wb') as f: 
                f.write(bytes_data) # stroing locally 

            s3.upload_file(filename,'temp-bucket-1729',filename) #uploading to s3 bucket
            job_name=''.join(random.choice(string.ascii_letters) for _ in range(16))
            bucket_name='temp-bucket-1729'

            response = transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': 's3://temp-bucket-1729/audio_file.mp3'},
                MediaFormat='mp3',
                LanguageCode='en-US',
                OutputBucketName=bucket_name,
            ) # triggering transcription job
            while True:
                # loop until job is complted.
                status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                    break
                print('Transcription job still in progress...')
                time.sleep(5)
            
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                file_object = s3.get_object(Bucket=bucket_name, Key=job_name+".json")
                file_content = file_object['Body'].read().decode('utf-8')
                text = json.loads(file_content)['results']['transcripts'][0]['transcript']
                # print(text)
                st.success('Processing completed!', icon="✅")
                st.info(text)

                ste.download_button(
                    "Download the transcription",
                    text,
                    file_name='transcription.txt',
                ) 

        else:
            st.warning(
                "🚨 We've limited this demo to 20MB files. Please upload a smaller file."
            )
            st.stop()


else:
    path_in = None
    st.stop()

