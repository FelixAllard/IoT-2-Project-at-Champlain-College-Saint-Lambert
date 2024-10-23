from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import matplotlib
from flask_cors import CORS
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})

app.config['SECRET_KEY'] = 'secure_key'

raspberryPi_IP = 'http://localhost:4999'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Routes/Routing

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
@login_required
def data():
    try:
        sensor_response = requests.get(f'{raspberryPi_IP}/sensors')
        sensor_response.raise_for_status()
        sensors = sensor_response.json()

        ping_response = requests.get(f'{raspberryPi_IP}/ping')
        ping_response.raise_for_status()
        ping_data = ping_response.json()

    except requests.RequestException as e:
        flash(f"Error fetching data: {e}")
        sensors = []
        ping_data = None

    img = io.BytesIO()
    plt.plot([0, 1, 2, 3], [10, 11, 12, 13])
    plt.title('Example Plot')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    if sensors:
        avg = sum(sensor['battery_percentage'] for sensor in sensors) / len(sensors)
    else:
        avg = 0

    return render_template('data.html', plot_url=plot_url, avg=avg, sensors=sensors, ping_data=ping_data)

@app.route('/aboutUs')
def about():
    return render_template('aboutus.html', title='About Us')

@app.route('/id', methods=['GET'])
def get_id():
    raspberry_pi_id = '1'
    return jsonify({'id': raspberry_pi_id})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pi_id = request.form.get('id')
        password = request.form['password']

        if not pi_id:
            flash('Raspberry Pi ID is missing. Please try again.')
            return render_template('login.html')

        try:
            response = requests.post(f'{raspberryPi_IP}/password', json={'id': pi_id, 'password': password})
            if response.status_code == 200:
                user = User(id=pi_id)
                login_user(user)
                return redirect(url_for('data'))
            else:
                flash('Invalid password')
        except requests.RequestException as e:
            flash(f"Error during authentication: {e}")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
