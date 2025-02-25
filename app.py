#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Version  : 3.11
# @Author   : Lordera
# @Datetime : 2025/1/14 13:46
# @Project  : myLangGPT
# @File     : app.py.py


import json
import streamlit as st

from llms.models import qwen_langgpt, hunyuan_langgpt, glm_langgpt  # noqa
from templates.template_default import default_prompt, edit_content

prefix = r"""
下面就是待分析的 Prompt:
---
## 【CONTENT】
---
"""


def generate_response(_model, _template, _name, _api_key, _content, _max_tokens):
    """调用API生成回复"""
    try:
        _response = eval(_model)(
            template=_template,
            name=_name,
            api_key=_api_key,
            content=_content,
            max_tokens=_max_tokens,
            isStream=True,
        )
        
        return _response
    
    except Exception as e:
        st.error(f"生成回复时出错: {str(e)}")
        return None


# 页面配置
st.set_page_config(page_title="用户提示词生成", layout="wide")
st.title("用户提示词生成")

# 侧边栏设置
with st.sidebar:
    st.header("设置")
    
    model = st.selectbox(
        "模型选择",
        ["qwen-plus", "hunyuan-large", "glm-4"]
    )
    
    # api_key = st.text_input("API Key", type="password", value="password")
    
    # 快速调用
    if model == "qwen-plus":
        api_key = st.text_input("API Key", type="password", value=f"{model}-api-key")
    elif model == "hunyuan-large":
        api_key = st.text_input("API Key", type="password", value=f"{model}-api-key")
    elif model == "glm-4":
        api_key = st.text_input("API Key", type="password", value=f"{model}-api-key")
    else:
        api_key = st.text_input("API Key", type="password", value=f"{model}-api-key")
    
    if model == "qwen-plus":
        # base_url = st.text_input("Base URL", value="https://dashscope.aliyuncs.com/compatible-mode/v1")
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    elif model == "hunyuan-large":
        # base_url = st.text_input("Base URL", value="AKIDADRsCQfmx78141lIcmqjOF80kMo45rRv")
        base_url = "AKIDADRsCQfmx78141lIcmqjOF80kMo45rRv"
    elif model == "glm-4":
        # base_url = st.text_input("Base URL", value="")
        base_url = ""
    else:
        # base_url = st.text_input("Base URL", value="https://test-gw.xkw.com")
        base_url = "https://test-gw.xkw.com"
    
    max_tokens = st.slider("返回Token长度", 100, 2000, 800)
    
    # 创建一个大文本框，允许用户编辑默认内容
    edit_template = st.text_area("编辑你的用户提示词模板", value=edit_content.strip(), height=300)
    
    # 按钮来提交输入
    if st.button("提交"):
        # 显示原始输入字符串
        st.write("新模板:")
        st.code(edit_template, language='text')
        
        st.write("总模板:")
    template = default_prompt.replace("【【EDIT_CONTENT】】", edit_template)
    st.code(template)

# 主页面对话区
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # st.markdown(message["content"])
        st.code(message["content"], language="markdown")

# 用户输入
if content := st.chat_input("请输入您的问题"):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": content})
    with st.chat_message("user"):
        st.markdown(content)
    
    # 生成助手回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 检查必要参数
        if not api_key:
            st.error("请在侧边栏设置API Key")
        else:
            response = generate_response(
                _model=f"{model.split('-')[0]}_langgpt",
                _template=template,
                _name=model,
                _api_key=api_key,
                _content=prefix.replace('【CONTENT】', content),
                _max_tokens=max_tokens
            )
            
            switch, volume = 0, 0
            if response:
                try:
                    if model.split('-')[0] == 'qwen':
                        for chunk in response:
                            chunk_data = chunk.choices[0].delta.content if chunk.choices else ''
                            if "&" in chunk_data and volume:
                                switch = 0
                                full_response += chunk_data[:chunk_data.find("&")]
                                break
                            if switch == 1:
                                full_response += chunk_data
                                message_placeholder.code(full_response + "▌", language="markdown")
                                continue
                            if "#" in chunk_data and not volume:
                                switch = 1
                                volume = 1
                                full_response += chunk_data[chunk_data.find("#"):]
                                continue
                    
                    if model.split('-')[0] == 'hunyuan':
                        for chunk in response:
                            chunk_data = json.loads(chunk['data'])['Choices'][0]['Delta']['Content'] if chunk else ''
                            full_response += chunk_data
                            message_placeholder.code(full_response + "▌", language="markdown")
                    if model.split('-')[0] == 'glm':
                        for chunk in response:
                            chunk_data = chunk.choices[0].delta.content if chunk.choices else ''
                            full_response += chunk_data
                            message_placeholder.code(full_response + "▌", language="markdown")
                    if model.split('-')[0] in ['gpt', 'claude']:
                        full_response = response
                
                except json.JSONDecodeError:
                    raise
                
                # message_placeholder.markdown(full_response)
                message_placeholder.code(full_response, language="markdown")
                
                # 保存助手回复
                st.session_state.messages.append({"role": "assistant", "content": full_response})
