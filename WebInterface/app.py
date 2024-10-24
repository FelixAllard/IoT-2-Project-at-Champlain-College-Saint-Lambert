from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Default IP address for first time logging in
default_raspberryPi_IP = "http://192.168.0.100:5000"
app.config['SECRET_KEY'] = 'secure_key'

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

@app.route('/set_ip_port', methods=['GET', 'POST'])
def set_ip_port():
    if request.method == 'POST':
        ip_address = request.form.get('ip_address')
        port_number = request.form.get('port_number')
        raspberryPi_IP = f"http://{ip_address}:{port_number}"

        response = make_response(redirect(url_for('login')))
        response.set_cookie('raspberryPi_IP', raspberryPi_IP)
        return response

    return render_template('set_ip_port.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    raspberryPi_IP = request.cookies.get('raspberryPi_IP', default_raspberryPi_IP)

    if request.method == 'POST':
        pi_id = request.form.get('id')
        password = request.form['password']

        if not pi_id:
            flash('Raspberry Pi ID is missing. Please try again.')
            return render_template('login.html', raspberryPi_IP=raspberryPi_IP)

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

    return render_template('login.html', raspberryPi_IP=raspberryPi_IP)


@app.route('/data')
@login_required
def data():
    raspberryPi_IP = request.cookies.get('raspberryPi_IP', default_raspberryPi_IP)

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


    if sensors:
        avg = sum(sensor['battery_percentage'] for sensor in sensors) / len(sensors)
    else:
        avg = 0

    return render_template('data.html', avg=avg, sensors=sensors, ping_data=ping_data)

@app.route('/aboutUs')
def about():
    return render_template('aboutus.html', title='About Us')

@app.route('/id', methods=['GET'])
def get_id():
    raspberry_pi_id = '1'
    return jsonify({'id': raspberry_pi_id})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=25565)
