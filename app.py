from flask import Flask, render_template, request, redirect, url_for, session,Response,jsonify
import cv2

from ultralytics import YOLO
app = Flask(__name__)
users = 0

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("database.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://smart-grain-1032a-default-rtdb.firebaseio.com/"})
root_ref = db.reference('/') 
data = root_ref.get()
import qrcode
from flask import send_file

# Function to capture frames from camera
def generate_framesqr():
    cap = cv2.VideoCapture(0)  # Adjust camera index as needed
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to display camera feed
@app.route('/camera')
def camera():
    return Response(generate_framesqr(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to capture a frame, detect QR code, and return result
@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    # Capture a frame from the camera
    cap = cv2.VideoCapture(0)  # Adjust camera index as needed
    success, frame = cap.read()
    if not success:
        return jsonify({"success": False, "message": "Failed to capture frame"})

    # Initialize the QR code detector
    detector = cv2.QRCodeDetector()

    # Detect and decode QR codes
    data, _, _ = detector.detectAndDecode(frame)
    cv2.imshow("frame",frame)
    print(data)
    if data:
        return jsonify({"success": True, "qr_data": data})
    else:
        return jsonify({"success": False, "message": "No QR code detected"})
@app.route('/QR')
def QR():
    return render_template('qrscan.html',cam_url=url_for('camera'))


#delete
# Route to display all data and provide delete buttons
@app.route("/show_data", methods=['GET'])
def show_data():
    # Fetch all data from Firebase
    users_ref = root_ref.child('users')
    users = users_ref.get()

    # Pass the fetched data to the HTML template
    return render_template("show_data.html", users=users)

# Route to handle deletion of data
@app.route("/delete_data/<user_id>", methods=['POST'])
def delete_data(user_id):
    # Reference the user's data
    user_ref = root_ref.child('users').child(user_id)
    
    # Delete the user's data
    user_ref.delete()

    # Redirect to the route displaying all data
    return redirect(url_for('show_data'))

@app.route("/generate_qr", methods=['POST'])
def generate_qr():
    # Get the data from the form
    farmer_name = request.form['farmername']
    farmer_phone = request.form['phone']
    farmer_address = request.form['address']
    grain_type = request.form['graintype']
    bags_count = request.form['bags']
    bags_weight = request.form['weight']
    date = request.form['date']

    # Generate the QR code
    data = f"Name: {farmer_name}\nPhone: {farmer_phone}\nAddress: {farmer_address}\nGrain Type: {grain_type}\nBags Count: {bags_count}\nBags Weight: {bags_weight}\nDate: {date}"
    filename = f"{farmer_name}.png"
    qr_img = qrcode.make(data)
    qr_img_path = f"static/{filename}"
    qr_img.save(qr_img_path)

    # Return the file path to the template
    return send_file(qr_img_path, mimetype='image/png')

# Function to generate QR code


@app.route("/adddata", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Save data to the database
        farmer_name = request.form['farmername']
        farmer_phone = request.form['phone']
        farmer_address = request.form['address']
        grain_type = request.form['graintype']
        bags_count = request.form['bags']
        bags_weight = request.form['weight']
        date = request.form['date']
        
        users_ref = root_ref.child('users')
        new_user_ref = users_ref.push()
        new_user_ref.set({
            'farmer_name': farmer_name,
            'farmer_phone': farmer_phone,
            'farmer_address': farmer_address,
            'grain_type': grain_type,
            'bags_count': bags_count,
            'bags_weight': bags_weight,
            'date': date
        })
        
        # Generate QR code
       
        
        # Render the template with the QR code
        return render_template("addData.html", qr_generated=True)
    else:
        # Render the form to add data
        return render_template("addData.html", qr_generated=False)

user_list = []


@app.route("/user_details", methods=['GET'])
def user_details():
    name = request.args.get('name')
    grain_type = request.args.get('type')
    user_exists = False
    users_ref = root_ref.child('users')
    users = users_ref.get()
    if users:
        for user_id, user_data in users.items():
            if user_data.get('farmer_name') == name and user_data.get('grain_type') == grain_type:
                user_exists = True
                phone = user_data.get('farmer_phone', '')
                address = user_data.get('farmer_address', '')
                bags_count = user_data.get('bags_count', '')
                bags_weight = user_data.get('bags_weight', '')
                date = user_data.get('date', '')
                return render_template('user_details.html', name=name, grain_type=grain_type, phone=phone, address=address, bags_count=bags_count, bags_weight=bags_weight, date=date)
    if not user_exists:
        return "User not found."



    
print(user_list)
user_list = []

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    user_list = []
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        if username=="Mastek" and password=="mastek123":
            users_ref = root_ref.child('users')
            users = users_ref.get()
            if users:
                for user_id, user_data in users.items():
                    print(user_id)
                    user_info = {
                        'farmer_name': user_data.get('farmer_name', ''),
                        'farmer_phone': user_data.get('farmer_phone', ''),
                        'farmer_address': user_data.get('farmer_address', ''),
                        'grain_type': user_data.get('grain_type', ''),
                        'bags_count': user_data.get('bags_count', ''),
                        'bags_weight': user_data.get('bags_weight', ''),
                        'date': user_data.get('date', '')
                    }
                    user_list.append(user_info)
            return render_template('home.html',users=user_list)
        else:
            return render_template('index.html', error='invalid username or password')
    return render_template('index.html')



#camera

def video_detection(path_x):
    
    
    # Load the YOLOv8 model
    model = YOLO("pest.pt")

    video_path = 0
    cap = cv2.VideoCapture(path_x)

    # Loop through the video fram   es
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        
        if success:
            # Run YOLOv8 inference on the frame
            results = model.predict(frame,verbose=False,conf=0.75)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            if len(results[0]) > 0:
                # sms_fun()
                for result in results:
                    if result.boxes:
                        box = result.boxes[0]
                        class_id = int(box.cls)
                        object_name = model.names[class_id]
                        print(object_name)
      
            # Display the annotated frame
            # cv2.imshow("YOLOv8 Inference", annotated_frame)
            yield annotated_frame
            # Break the loop if 'q' is pressed
            
def generate_frames(path_x=""):
    yolo_output = video_detection(path_x)
    for dec in yolo_output:
        ref, buffer = cv2.imencode('.jpg', dec)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  

pestcam = 0
@app.route('/cam',methods=['GET','POST'])
def pc1():
    return Response(generate_frames(path_x=pestcam), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/view_cam')
def view_cam():
    return render_template('cam.html', cam_url=url_for('pc1'))



@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))

