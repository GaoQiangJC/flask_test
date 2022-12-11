class Config:
    SECRET_KEY = 'mrsoft'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 小程序配置信息
    AppID = 'wxc42c410e5b390670'     # 小程序的 AppID
    AppSecret = 'a454fbc0f836ed83ab80caa7fbb1d093' # 小程序的 AppSecret

    @staticmethod
    def init_app(app):
        '''初始化配置文件'''
        pass

# the config for development
# 继承 Config
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/idom'
    DEBUG = True

# define the config
config = {
    'default': DevelopmentConfig
}
