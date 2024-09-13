import streamlit as st
import random
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API configuration
API_KEY = os.environ.get("API_KEY")
ENDPOINT = os.environ.get("ENDPOINT")
HEADERS = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Function to get response from the API
def get_response(word: str) -> dict:
    """
    Send a request to the API and return the parsed response.
    
    :param word: The input word to be explained
    :return: A dictionary containing the explanation and translations
    """
    payload = {
        "messages": [
            {
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": """你是一个汉语老师，年轻、批判现实、思考深刻，语言风趣。你表达方式类似于Oscar Wilde、鲁迅、王朔和刘震云的风格，擅长一针见血的语言，常用隐喻与讽刺来表达批判。

任务: 当用户输入一个词汇或短语时，你会用一个特别的视角解释它，解释要充满隐喻，结合日常语言，直接指出问题的核心，同时带有辛辣的讽刺和幽默感。解释总长度不要超过20个汉字。

Few-shot示例:
委婉：当你不得不刺向他人时，决定在剑刃上撒上一层止痛药。

请按下列格式，以JSON返回结果。

{
"en":"词语的最佳英文翻译",
"jp":"词语的最佳日语翻译",
"explanation":"词语的讽刺性解释"
}"""
                }]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": word}]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
    }

    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
        response.raise_for_status()
        result_data = response.json()
        if "choices" not in result_data or not result_data["choices"]:
            raise ValueError("Invalid response format")
        return json.loads(result_data["choices"][0]["message"]["content"])
    except requests.RequestException as e:
        st.error(f"请求失败。错误：{e}")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        st.error(f"解析响应数据失败。错误：{e}")
    return {}

# Modigliani color schemes
color_schemes = [
    {"primary": "#6E6259", "secondary": "#4E4A45"},  # 深灰褐色
    {"primary": "#5F6366", "secondary": "#3F4346"},  # 深蓝灰色
    {"primary": "#847C74", "secondary": "#5A534C"},  # 深棕色
    {"primary": "#7B8D8E", "secondary": "#4A5A5B"},  # 深青灰色
    {"primary": "#686C5E", "secondary": "#4B4F3E"},  # 深绿色调
    {"primary": "#5C5E66", "secondary": "#3C3E46"},  # 深蓝紫色
    {"primary": "#8A7967", "secondary": "#5E4F42"},  # 深棕灰色
    {"primary": "#4F585E", "secondary": "#343C41"},  # 深蓝绿调
    {"primary": "#7D7068", "secondary": "#534A43"},  # 暖灰色
    {"primary": "#6D7275", "secondary": "#454A4C"},  # 冷灰色
    {"primary": "#8C857B", "secondary": "#605B53"},  # 米灰色
    {"primary": "#6A7A7C", "secondary": "#414B4D"},  # 青灰色
    {"primary": "#767D6E", "secondary": "#4E5347"},  # 橄榄灰色
    {"primary": "#796E7E", "secondary": "#4F4653"},  # 紫灰色
    {"primary": "#826F5B", "secondary": "#574A3C"},  # 褐灰色
    {"primary": "#5B6E76", "secondary": "#3A474D"},  # 深蓝灰色
]

# Initialize session state variables
for key in ["input_word", "translation_en", "translation_jp", "explanation", "color_scheme", "use_custom_colors"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key not in ["color_scheme", "use_custom_colors"] else (random.choice(color_schemes) if key == "color_scheme" else False)

# Set page configuration
st.set_page_config(page_title="汉语新解", layout="centered")

# Add title
st.title("汉语新解")

# Add input field
word = st.text_input("输入词语", max_chars=10)

# Button to generate explanation
if st.button("解释吧", type="primary"):
    if word != st.session_state.input_word:
        st.session_state.input_word = word
        result = get_response(word)
        if result:
            st.session_state.translation_en = result.get("en", "")
            st.session_state.translation_jp = result.get("jp", "")
            st.session_state.explanation = result.get("explanation", "")

# Color selection
st.sidebar.header("颜色设置")
use_custom_colors = st.sidebar.checkbox("使用自定义颜色", value=st.session_state.use_custom_colors)

if use_custom_colors:
    primary_color = st.sidebar.color_picker("选择主要颜色", st.session_state.color_scheme["primary"])
    secondary_color = st.sidebar.color_picker("选择次要颜色", st.session_state.color_scheme["secondary"])
    st.session_state.color_scheme = {"primary": primary_color, "secondary": secondary_color}
else:
    if st.sidebar.button("随机更换颜色"):
        st.session_state.color_scheme = random.choice(color_schemes)

st.session_state.use_custom_colors = use_custom_colors

# Read HTML template
with open("word_card_template.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Insert color scheme and user input into HTML
html_content = html_content.format(
    primary_color=st.session_state.color_scheme["primary"],
    secondary_color=st.session_state.color_scheme["secondary"],
    word=st.session_state.input_word,
    translation_en=st.session_state.translation_en,
    translation_jp=st.session_state.translation_jp,
    explanation=st.session_state.explanation.replace("\n", "<br>"),
)

# Display HTML if input word exists
if st.session_state.input_word:
    st.components.v1.html(html_content, height=600)

# Add instructions
st.markdown("---")
st.write("使用说明：")
st.write("1. 输入词语，点击按钮，即可生成")
st.write("2. 在侧边栏选择使用自定义颜色或随机颜色")
st.write("3. 灵感来源：李维刚的Prompt。")
st.write("4. 制作者：李伯阳律师 （微信：legal-lby）")