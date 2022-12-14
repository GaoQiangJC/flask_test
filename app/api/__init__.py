from flask import Blueprint
from app.models import Member, Exam
from flask import jsonify, g, request
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.libs.MemberService import MemberService
from app import db
from werkzeug.http import HTTP_STATUS_CODES
# 全局
api = Blueprint('api', __name__)

# 设置 Token 验证
auth = HTTPTokenAuth(scheme='Bearer')
serializer = Serializer('mrsoft', expires_in=1800)

@auth.verify_token
def verify_token(token):
    try:
        data = serializer.loads(token)    # 验证token
    except:
        return False
    if 'user_id' in data:
        g.user_id = data['user_id']
        return True
    return False

@auth.error_handler
def token_auth_error():
    return error_response(401)

def error_response(status_code, message=None):
    response = {
        "code": status_code,
        "msg": HTTP_STATUS_CODES.get(status_code),
        "data": {}
    }
    return jsonify(response)



# 接口路径
@api.route('/users/wx_login', methods=['POST'])
def wx_login():
    req = request.values # 接受数据
    # 接受数据
    nickname = req['nickname'] if 'nickname' in req else ''
    avatar = req['avatar'] if 'avatar' in req else ''
    # 判断 code 是否存在
    code = req['code'] if 'code' in req else ''
    sesion = req['sesion'] if 'sesion' in req else 0
    print("nickname:" + nickname)
    print("avatar:" +avatar)
    print("code:" +code)
    print(sesion)
    if not code or len( code ) < 1:
        result = {
            "code": -1,
            "msg": "需要微信授权code",
            "data": {}
        }
        return jsonify(result)

    # 根据 code, 获取 openid
    openid = MemberService.getWeChatOpenId(code)
    print(openid)
    if openid is None:
        result = {
            "code":-1,
            "msg":"调用微信出错",
            "data":{}
        }
        return jsonify(result)

    # 如果用户存在，写入 member 表中
    member = Member.query.filter_by(openid = openid).first()
    if not member:
        member = Member(
            openid = openid,
            nickname = nickname,
            avatar = avatar,
            sesion = sesion,)
        db.session.add(member)
        db.session.commit()
    sesionTotal = db.session.query(Exam).count()
    print(sesionTotal)
    token = serializer.dumps({'user_id':member.id})       # 服务器生成 token
    print(token)
    # 返回结果
    result = {
        "code":1,
        "msg":"登录成功",
        "data":{"userInfo":{
                                "userId": member.id,
                                "nickName": member.nickname,
                                "avatar": member.avatar,
                                "sesion": member.sesion,
                            },
                 "sesionTotal":sesionTotal,
                 "token": token.decode(),  # byte 转化为 string
            }
    }
    return jsonify(result)

@api.route('/exams',methods=["POST"])
@auth.login_required
def get_exam():
    sesion = request.values['sesion']
    try:
        exam = Exam.query.filter_by(id=sesion).first()
        result = {
            "code": 1,
            "data": {
                    "answer": exam.answer,
                    "candidates": exam.candidates.split(","),
                    "image": exam.pictureUrl
                },
            "message": "请求成功"
        }
    except:
        result = {
            "code": 0,
            "data": {},
            "message": "请求失败"
        }
    return jsonify(result)

@api.route('/exams/update_sesion',methods=["POST"])
@auth.login_required
def update():
    sesion = int(request.values['sesion'])
    userId = int(request.values['userId'])
    # 更改用户关卡
    try:
        # 更新数据
        member = Member.query.filter_by(id=userId).first()
        member.sesion = sesion
        db.session.commit()
        result = {
            "code": 1,
            "msg": "请求成功",
            "data": {
                "sesion": sesion
            }
        }
    except:
        result = {
            "code": 0,
            "msg": "更新失败",
            "data": {}
        }
    return jsonify(result)


@api.route('/rank',methods=["POST"])
@auth.login_required
def get_rank():
    '''
    排行榜
    '''
    members = Member.query.order_by(Member.sesion.desc()).limit(10).all()
    data = []
    for item in members:
        userInfo = {
            "userId": item.id,
            "nickname": item.nickname,
            "avatar": item.avatar,
            "sesion": item.sesion,
        }
        data.append(userInfo)
    # 返回结果
    result = {
        "code":1,
        "msg":"请求成功",
        "data": data
    }
    return jsonify(result)



