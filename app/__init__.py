from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# config 字典
from config import config

db = SQLAlchemy() # 实例化 SQLAlchemy

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name]) # 获取配置信息中的开发环境
    # Config 对象 config[config_name]
    config[config_name].init_app(app)           # 初始化 app
    db.init_app(app) # 数据库初始化

    # 注册蓝图
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")

    return app
