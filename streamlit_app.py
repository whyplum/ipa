import nltk
import requests
import streamlit as st

# from streamlit.components.v1 import html

nltk.download("punkt")
import itertools
import string

from nltk.tokenize import word_tokenize


def tokenize_with_spaces(s):
    ll = [[word_tokenize(w), " "] for w in s.split()]
    return list(itertools.chain(*list(itertools.chain(*ll))))


def is_punctuation(word):
    return word in string.punctuation


def get_html_word(text):
    if is_punctuation(text):
        return text

    try:
        url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{text}?key={api_key}"
        response = requests.get(url)
        data = response.json()

        text_syllables = data[0]["hwi"]["hw"].split("*")

        if len(text_syllables) == 1:
            return text

        ipa_syllables = data[0]["hwi"]["prs"][0]["mw"].split("-")

        # something wrong
        # if len(text_syllables) != len(ipa_syllables):
        #     return text

        html_word = ""
        for tsy, isy in zip(text_syllables, ipa_syllables):
            if isy.startswith("ˌ") and len(text_syllables) > 2:
                html_word += f'<span style="color:#f0bc6e">{tsy}</span>'
            elif isy.startswith("ˈ"):
                html_word += f'<span style="color:#f0776e">{tsy}</span>'
            else:
                html_word += tsy
        return html_word
    except:
        return text


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

api_key = st.text_input(
    "Enter API key",
)

text = st.text_input("Enter text", "")
if st.button("Transcribe"):
    html_output = ""
    words = tokenize_with_spaces(text)
    widget = st.empty()
    for word in words:
        if len(word.strip()):
            html_word = get_html_word(word)
            html_output += html_word
            widget.write(html_output, unsafe_allow_html=True)
        else:
            html_output += " "
            widget.write(html_output, unsafe_allow_html=True)
