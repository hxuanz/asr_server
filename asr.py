# encoding: utf-8
"""
asr的实现：
1 利用ffmpeg 转换语音文件格式 【百度只支持特定格式】
2 调用百度在线API识别
"""
import subprocess
import requests
import json
import base64
import wave
import time
import os
import uuid

error = {3300: '输入参数不正确',
         3301:' 识别错误',
         3302:' 验证失败',
         3303:' 语音服务器后端问题',
         3304:' 请求 GPS 过大，超过限额',
         3305:' 产品线当前日请求数超过限额'
}
MAC_ADDRESS = uuid.UUID(int=uuid.getnode()).hex[-12:]
headers = {'Content-Type': 'application/json'}

def baidu_asr(wav_path, token):
    """
    baidu asr api 参考 http://yuyin.baidu.com/docs/asr/57
    :param token:
    :return:
    """
    f = wave.open(wav_path, 'rb')
    wav_data = f.readframes(f.getnframes())
    framerate = f.getframerate()
    assert framerate in [8000, 16000], "%d 采样率不支持" % framerate
    assert f.getnchannels() == 1, "仅支持单声道, %d" % f.getnchannels()
    wav_base64 = base64.b64encode(wav_data)
    f.close()
    os.remove(wav_path)  ##删除临时文件

    url = 'http://vop.baidu.com/server_api'
    data = {
        "format": "wav",  #	语音压缩的格式，请填写上述格式之一，不区分大小写
        "rate": framerate,  #采样率，支持 8000 或者 16000
        "channel": 1,  #声道数，仅支持单声道，请填写 1
        "token": token,
        "cuid": str(MAC_ADDRESS),  # 用户唯一标识，机器 MAC 地址
        "len": len(wav_data),
        "speech": wav_base64,  #真实的语音数据 ，需要进行base64 编码
    }

    r = requests.post(url, json=data, headers=headers)
    if r.status_code == 200:
        res = json.loads(r.text)
        if res['err_no'] == 0:
            return res['result']
        else:
            print(error.get(res['err_no'], res['err_no']))
            print(res['err_msg'])

def convert2wav(data_params):
    cwd = os.getcwd().replace('\\', '/')
    tmp_file_path = "%s/tmp/%d" % (cwd, time.time())
    file_in = "%s.%s" % (tmp_file_path, data_params['type'])
    file_out = "%s.wav" % (tmp_file_path)

    # 数据流存为 文件
    av_data = base64.b64decode(data_params['data'])
    with open(file_in, 'wb') as f:
        f.write(av_data)

    cwd = os.getcwd().replace('\\', '/')
    # 调用ffmpeg程序
    commond = "%s/ffmpeg.exe -i %s -ar 16000 -ac 1 %s" % (cwd, file_in, file_out)
    subprocess.call(commond, shell=True)
    os.remove(file_in)  #删除临时文件
    return file_out

def asr_api(data_params, token):
    assert 'data' in data_params
    assert 'type' in data_params

    file_out = convert2wav(data_params)
    result = baidu_asr(file_out, token)
    return result[0]