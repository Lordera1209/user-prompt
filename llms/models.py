#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Version  : 3.11
# @Author   : Lordera
# @Datetime : 2025/1/14 11:18
# @Project  : myLangGPT
# @File     : models.py


from openai import OpenAI
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from zhipuai import ZhipuAI


def qwen_langgpt(template, name, api_key, content, max_tokens, isStream):
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model=name,
        messages=[{'role': 'system', 'content': template},
                  {'role': 'user', 'content': content}],
        max_tokens=max_tokens,
        stream=isStream,
        stream_options={"include_usage": True}
    )
    if isStream:
        return completion
    else:
        return completion.choices[0].message.content


def hunyuan_langgpt(template, name, api_key, content, max_tokens, isStream):
    # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
    cred = credential.Credential(
        secret_id="AKIDADRsCQfmx78141lIcmqjOF80kMo45rRv",
        secret_key=api_key,
    )
    
    cpf = ClientProfile()
    # 预先建立连接可以降低访问延迟
    cpf.httpProfile.pre_conn_pool_size = 3
    client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", cpf)
    
    req = models.ChatCompletionsRequest()
    req.Model = name
    msg1 = models.Message()
    msg1.Role = "system"
    msg1.Content = template
    
    msg2 = models.Message()
    msg2.Role = "user"
    msg2.Content = content
    
    req.Messages = [msg1, msg2]
    
    req.Stream = isStream
    resp = client.ChatCompletions(req)
    
    if isStream:
        return resp
    else:
        return resp.Choices[0].Message.Content


def glm_langgpt(template, name, api_key, content, max_tokens, isStream):
    client = ZhipuAI(api_key=api_key)
    response = client.chat.completions.create(
        model=name,
        messages=[
            {"role": "system", "content": template},
            {"role": "user", "content": content},
        ],
        stream=isStream,
        max_tokens=max_tokens
    )
    
    if isStream:
        return response
    else:
        return
