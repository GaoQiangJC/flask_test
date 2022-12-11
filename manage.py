from app import create_app

# 走 默认类
app = create_app('default')
# Flask 对象 app
app.run(debug=True, host='192.168.2.205', port=5000)
