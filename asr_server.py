# encoding: utf-8
"""
    author： hxuanz
    data: 20170524
    desc: 基于falsk实现的asr web服务
"""
from flask import Flask
from asr import asr_api
from flask import request
from baidu_token import TOKEN
import traceback
app = Flask(__name__)

@app.route('/asr', methods=['POST'])
def asr_server():
    try:
        data_params = dict(type= request.args['type'], data=request.data)
        result = asr_api(data_params, TOKEN)
    except Exception as e:
        traceback.print_exc()
        return "err: %s" % e.message
    else:
        return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12346)