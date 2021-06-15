from flask import Flask

app = Flask(__name__)

""" Config """
# 操作字典dict一樣的設定方式
app.config['TESTING'] = True
# 設定物件屬性的方式來設定
app.testing = True
# 透過字典dict的update方法一次設定資料的內容
app.config.update(
    TESTING=True,
    SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/'
)

""" Logging """
app.logger.debug('A value for debugging')
app.logger.warning('A warning occurred (%d apples)', 42)
app.logger.error('An error occurred')


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run()
