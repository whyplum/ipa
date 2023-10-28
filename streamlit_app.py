from itertools import zip_longest

import nltk
import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth

nltk.download("punkt")
import itertools
import string

from nltk.tokenize import word_tokenize


def tokenize_with_spaces(s):
    ll = [[word_tokenize(w), " "] for w in s.split()]
    return list(itertools.chain(*list(itertools.chain(*ll))))


def is_punctuation(word):
    return word in string.punctuation


def get_sound_url(audio_name):
    if not audio_name:
        return None
    if not len(audio_name.strip()):
        return None

    if audio_name.startswith("bix"):
        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/bix/{audio_name}.mp3"
    elif audio_name.startswith("gg"):
        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/gg/{audio_name}.mp3"
    elif audio_name[0].isdigit():
        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/number/{audio_name}.mp3"
    elif audio_name[0] in string.punctuation:
        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/number/{audio_name}.mp3"

    return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{audio_name[0]}/{audio_name}.mp3"


def get_html_word_and_ipa(text):
    if is_punctuation(text):
        return (
            f'<span style="color:#999999">{text}</span>',
            f'<span style="color:#999999">{text}</span>',
            None,
        )

    try:
        url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{text}?key={api_key}"
        response = requests.get(url)
        data = response.json()

        text_syllables = data[0]["hwi"]["hw"].split("*")

        ipa_syllables = []
        auto_ipa = None

        for ipa_candidate in data[0]["hwi"]["prs"]:
            if "sound" in ipa_candidate:
                auto_ipa = ipa_candidate["sound"]["audio"]
                ipa_syllables = ipa_candidate["mw"].split("-")
                break

        if len(text_syllables) == 1:
            return text, "-".join(ipa_syllables), auto_ipa

        # something wrong
        # if len(text_syllables) != len(ipa_syllables):
        #     return text

        html_word = ""
        html_ipa = ""
        for tsy, isy in zip_longest(text_syllables, ipa_syllables, fillvalue=""):
            if isy.startswith("ˌ") and len(text_syllables) > 2:
                html_word += f'<span style="color:#f0bc6e">{tsy}</span>'
                html_ipa += f'<span style="color:#f0bc6e">{isy}</span>'

            elif isy.startswith("ˈ"):
                html_word += f'<span style="color:#f0776e">{tsy}</span>'
                html_ipa += f'<span style="color:#f0776e">{isy}</span>'
            else:
                html_word += tsy
                html_ipa += isy
        return html_word, html_ipa, auto_ipa
    except:
        return (
            f'<span style="color:#999999">{text}</span>',
            f'<span style="color:#999999">{text}</span>',
            None,
        )


# def open_page(url):
#     open_script= """
#         <script type="text/javascript">
#             window.open('%s', '_blank').focus();
#         </script>
#     """ % (url)
#     html(open_script)

st.title("Text to IPA")
url = "https://sd.blackball.lv/library/domain-driven_design_-_tackling_complexity_in_the_heart_of_software.pdf"


st.link_button("DDD link", url)

api_key = st.secrets["DICT_API_KEY"]

rows = []
text = st.text_input("Enter text", "")
if st.button("Transcribe"):
    html_output = ""
    ipa_output = ""
    words = tokenize_with_spaces(text)
    widget1 = st.empty()
    widget2 = st.empty()
    rows = []
    for word in words:
        if len(word.strip()):
            html_word, html_ipa, audio = get_html_word_and_ipa(word)
            html_output += html_word
            ipa_output += html_ipa
            widget1.write(html_output, unsafe_allow_html=True)
            sound_url = get_sound_url(audio)
            if sound_url:
                rows.append([html_word, html_ipa, sound_url])
        else:
            html_output += " "
            ipa_output += " "
            widget1.write(html_output, unsafe_allow_html=True)

    st.markdown("----")

    for row in rows:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(row[0], unsafe_allow_html=True)
        with col2:
            st.markdown(row[1], unsafe_allow_html=True)
        with col3:
            st.audio(row[2])

        st.markdown("----")
