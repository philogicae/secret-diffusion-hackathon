from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view-collection')
def view_collection():
    return render_template('view-collection.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
