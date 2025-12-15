from flask import jsonify

class Result:
    @staticmethod
    def success(data=None):
        return jsonify({
            "code": 1,
            "msg": "success",
            "data": data
        })

    @staticmethod
    def error(msg="系统异常", code=0):
        return jsonify({
            "code": code,
            "msg": msg,
            "data": None
        })