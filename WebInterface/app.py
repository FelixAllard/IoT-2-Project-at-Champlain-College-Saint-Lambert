from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import requests

app = Flask(__name__)
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

@app.route('/data')
@login_required
def data():
    try:
        sensor_response = requests.get('http://localhost:4999/sensors') # Temporarily localhost
        sensor_response.raise_for_status()
        sensors = sensor_response.json()

        ping_response = requests.get('http://localhost:4999/ping')
        ping_response.raise_for_status()
        ping_data = ping_response.json()

    except requests.RequestException as e:
        flash(f"Error fetching data: {e}")
        sensors = []
        ping_data = None

    # Example plot
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'pwd':
            user = User(id=1)
            login_user(user)
            return redirect(url_for('data'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
