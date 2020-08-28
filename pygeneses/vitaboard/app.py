from flask import Flask, request, render_template, redirect, flash, jsonify
import os
import pkgutil

from .graph_gen import get_life_stats, tsne

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'my-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        file_location = request.form['file_location']
        speed = request.form['speed']

        if not os.path.exists(file_location):
            return jsonify({"title": "Error", "text": "The location " + file_location + " does not exist",
                            "icon": "error"})

        if ".npy" not in file_location:
            return jsonify({"title": "Error", "text": "You need to pass a npy file",
                            "icon": "error"})

        with open('pass_params.txt', 'w') as file:
            file.write(file_location + '\n')
            file.write(speed + '\n')

        visualizer_contents = pkgutil.get_data(__name__, "visualizer.py").decode()
        with open('./visualizer.py', 'w') as file:
            file.write(visualizer_contents)

        os.system('python visualizer.py')

        os.remove('pass_params.txt')
        os.remove('visualizer.py')

        return jsonify({"title": "Success", "text": "Visualizer ran successfully",
                        "icon": "success"})

@app.route('/groups', methods=['POST'])
def groups():

    if request.method == 'POST':
        location = request.form['location']

        if not os.path.exists(location):
            return jsonify({"title": "Error", "text": "The location " + location + " does not exist",
                            "icon": "error"})

        if not os.path.exists(os.path.join(location, 'Embeddings')):
            return jsonify({"title": "Error", "text": "The location " + location + " does not have any embeddings",
                            "icon": "error"})

        coord = tsne(location)

        if(coord == -1):
            return jsonify({"title": "Error", "text": "The location " + location + " does not have any embeddings",
                            "icon": "error"})

        return jsonify({"title": "Success", "text": "Groups generated successfully",
                        "icon": "success", "coord": coord})

@app.route('/stats', methods=['POST'])
def stats():

    if request.method == 'POST':
        location = request.form['location']

        if not os.path.exists(location):
            return jsonify({"title": "Error", "text": "The location " + location + " does not exist",
                            "icon": "error"})

        mean, variance, qof = get_life_stats(location)

        if mean == -1 and variance == -1 and qof == -1:
            return jsonify({"title": "Error", "text": "The location " + location + " does not have any log files",
                            "icon": "error"})

        return jsonify({"title": "Success", "text": "Stats generated successfully",
                        "icon": "success", "mean": mean, "variance": variance, "qof": qof})

if __name__ == "__main__":
    app.run()
