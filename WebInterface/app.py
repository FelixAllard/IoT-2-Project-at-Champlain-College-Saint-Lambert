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

@app.route('/login', methods=['GET'])
def login():
    raspberryPi_IP = request.cookies.get('raspberryPi_IP', default_raspberryPi_IP)
    return render_template('login.html', raspberryPi_IP=raspberryPi_IP)

@app.route('/login', methods=['POST'])
def post_login():
    if request.is_json:
        data = request.get_json()
        pi_id = data.get('id')

        user = User(id=pi_id)
        login_user(user)

        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid request format.'}), 400


@app.route('/data')
@login_required
def data():
    return render_template('data.html')

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
