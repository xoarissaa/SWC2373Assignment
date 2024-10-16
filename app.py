from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"

WEBEX_API_URL = "https://webexapis.com/v1"

# Helper function to make requests
def webex_api_request(endpoint, access_token, method='GET', data=None):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = f"{WEBEX_API_URL}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=data)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        response = webex_api_request("people/me", access_token)
        if "errors" in response:
            flash("Invalid Token. Please try again.")
            return redirect(url_for('index'))
        return render_template('user_info.html', user_info=response, access_token=access_token)
    return render_template('index.html')

@app.route('/rooms/<access_token>', methods=['GET', 'POST'])
def rooms(access_token):
    rooms_data = webex_api_request("rooms", access_token).get('items', [])[:5]
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        message = request.form.get('message')
        data = {"roomId": room_id, "text": message}
        message_response = webex_api_request("messages", access_token, method="POST", data=data)
        if "errors" not in message_response:
            flash("Message sent successfully!")
        else:
            flash("Failed to send the message.")
    return render_template('rooms.html', rooms=rooms_data, access_token=access_token)

@app.route('/create_room/<access_token>', methods=['GET', 'POST'])
def create_room(access_token):
    if request.method == 'POST':
        room_title = request.form.get('room_title')
        data = {"title": room_title}
        response = webex_api_request("rooms", access_token, method='POST', data=data)
        if "errors" not in response:
            flash(f"Room '{room_title}' created successfully!")
        else:
            flash("Failed to create the room. Please try again.")
        return redirect(url_for('rooms', access_token=access_token))
    return render_template('create_room.html', access_token=access_token)

if __name__ == '__main__':
    app.run(debug=True)
