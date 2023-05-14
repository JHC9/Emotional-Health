import csv
import cv2
print(cv2.__version__)
import numpy as np
from tensorflow.keras.models import model_from_json  
from tensorflow.keras.preprocessing import image  
from flask import Flask, session, render_template, request, redirect, url_for, Response
# from flask_session import Session
import os
import sqlite3
import time
import joblib
import numpy as np

#load model  
model = model_from_json(open("fer.json", "r").read())  

#load weights  
model.load_weights('fer.h5')  


model2 = joblib.load('linear_regression_model.pkl')

face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')  


app = Flask(__name__)



camera = cv2.VideoCapture(0)
boolean_value = True



# @app.route('/start_signal')
# def start_signal():
#     global boolean_value
#     boolean_value = True
#     return 'Start signal received'

# @app.route('/stop_signal')
# def stop_signal():
#     global boolean_value
#     boolean_value = False
#     return 'Stop signal received'

# @app.route('/check_status')
# def check_status():
#     global boolean_value
#     return f'The current value of boolean_value is: {boolean_value}'
# global da_score
da_score = None

def gen_frames():
    
    emoscore = [0, 0, 0, 0, 0, 0, 1]
    emocent = []
    running = True
    start_time = time.time()
    while running:
        print(True)
        # Capture frame by frame
        success, frame = camera.read()
        if not success:
            break
        else:
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)

            for (x, y, w, h) in faces_detected:
                print('WORKING')
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), thickness=7)
                roi_gray = gray_img[y:y + w, x:x + h]  # cropping region of interest i.e. face area from  image
                roi_gray = cv2.resize(roi_gray, (48, 48))
                img_pixels = image.img_to_array(roi_gray)
                img_pixels = np.expand_dims(img_pixels, axis=0)
                img_pixels /= 255

                print(img_pixels.shape)

                predictions = model.predict(img_pixels)

                # find max indexed array
                max_index = np.argmax(predictions[0])

                emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
                predicted_emotion = emotions[max_index]
                emoscore[max_index] += 1
                print(predicted_emotion)
                cv2.putText(frame, predicted_emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            resized_img = cv2.resize(frame, (1000, 700))

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            frame = buffer.tobytes()
            print(emoscore)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  # Concatenate frame and emoscore

            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time >= 10:  # Check if 5 minutes (300 seconds) have elapsed
                running = False  # Set running to False to exit the loop
            
    emocent = [score / sum(emoscore) for score in emoscore]

    # Check if the file exists and is empty
    if not os.path.exists('score.csv') or os.stat('score.csv').st_size == 0:
        with open('score.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(emotions)

    # Append data to the file
    with open('score.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(emocent)
    
    file.close()
    # with app.app_context():
    #     global da_score
    #     da_score = model2.predict(np.array(emocent).reshape(1, -1))
        
    #     da_score = da_score  # Update the global variable
        
    #     return redirect(url_for('score'))
    da_score = model2.predict(np.array(emocent).reshape(1, -1))    
    print('Mental Wellness Score: ',da_score)
    with open('avg.txt', 'a') as file:
    # Write the value as a string
        file.write(str(da_score) + '\n')
   
# Read the data from the text file
with open('avg.txt', 'r') as file:
    lines = file.readlines()

# Remove the brackets and whitespace from each line and split the values
data = [line.strip()[1:-1].split(',') for line in lines]

# Check if there are exactly 7 sets of values
if len(data) == 7:
    # Convert the values to floats and calculate the average
    values = [float(val) for sublist in data for val in sublist]
    average = sum(values) / len(values)

    # Print the average
    print(average)



app.secret_key = 'secret_key'

if not os.path.exists('accounts'):
    os.makedirs('accounts')

conn = sqlite3.connect('accounts/users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL)')


# ***Underneath is the test login

# cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', ('user@example.com', 'password123'))
conn.commit()

@app.route('/')
def login():
    return render_template('login.html')
@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    if user:
        # Login successful
        return redirect(url_for('home'))
    else:
        # Login failed
        message = 'Invalid email or password'
        return render_template('login.html', message=message)


@app.route('/home')
# def home():
#     if 'email' in session:
#         # Get the absolute path of the Pictures directory
#         pictures_path = os.path.join(app.root_path, 'Pictures')
#         # Render the template and pass the pictures_path variable to it
#         return render_template('main.html', pictures_path=pictures_path)
#     else:
#         return redirect(url_for('login'))
def home():
    pictures_path = os.path.join(app.root_path, 'Pictures')
    
    # Check if da_score is available
    if da_score is None:
        da_score_placeholder = "N/A"  # Placeholder value when da_score is not available
        return render_template('main.html', pictures_path=pictures_path, da_score=da_score_placeholder)
    
    return render_template('main.html', pictures_path=pictures_path, da_score=da_score)

@app.route('/score')
def score():
    # Check if da_score is available
    if da_score is None:
        da_score_placeholder = "N/A"  # Placeholder value when da_score is not available
        return render_template('score.html', da_score=da_score_placeholder)

    return render_template('score.html', da_score=da_score)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if len(password) < 8:
            message = 'Error: Password must be at least 8 characters long.'
            return render_template('signup.html', message=message)
        conn = sqlite3.connect('accounts/users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if user:
            # Email already in use
            message = 'Error: Email is already in use.'
            return render_template('signup.html', message=message)
        else:
            c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
            conn.close()
            return render_template('login.html')
    return render_template('signup.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            message = 'Error: Passwords do not match.'
            return render_template('forgot.html', message=message)
        conn = sqlite3.connect('accounts/users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if user:
            c.execute('UPDATE users SET password = ? WHERE email = ?', (password, email))
            conn.commit()
            conn.close()
            message = 'Password updated successfully.'
            return render_template('forgot.html', message=message)
        else:
            message = 'Error: Email not found.'
            return render_template('forgot.html', message=message)
    return render_template('forgot.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

app.run(host='0.0.0.0', port=8080)