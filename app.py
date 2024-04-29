from flask import Flask,render_template,redirect,request,url_for
from flask_sqlalchemy import SQLAlchemy
import random as rnd
import os


#initialising the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static'
db = SQLAlchemy(app)
rno = rnd.randrange(1000,9999)


#initiating the modal
class data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    specialid = db.Column(db.Integer, unique =True)
    image1  = db.Column(db.LargeBinary)
    image2 = db.Column(db.LargeBinary)
    likes1 = db.Column(db.Integer, default=0)
    likes2 = db.Column(db.Integer, default=0)
    
@app.route('/',methods = ['POST','GET'])
def main():
    return render_template('main.html')

@app.route('/create', methods = ['GET','POST'])
def create():
    if request.method == 'POST':
        specialid = rno
        m1 = request.files['image1']
        m2 = request.files['image2']
        upload = data(specialid = specialid , image1 = m1.read(), image2 = m2.read())
        db.session.add(upload)
        db.session.commit()
        ###########################################################################################
        save_image_to_file(upload.image1, f"image1_{specialid}.png")
        save_image_to_file(upload.image2, f"image2_{specialid}.png")
        return render_template('specialid.html', code = specialid)
        ###########################################################################################

    return render_template('index.html')

def save_image_to_file(image_data, filename):
    # Create the 'uploads' folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Save the image data to a file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'wb') as file:
        file.write(image_data)


@app.route('/rate', methods=['GET', 'POST'])
def rate():
    if request.method == 'POST':
        pagecode = request.form['code']
        code = data.query.filter_by(specialid=pagecode).first()
        if code:
            return redirect(url_for('result',code=pagecode))
        else:
            return "Entered code dosen't matches to any data"
    return render_template('rate.html')

@app.route('/result/<int:code>', methods=['GET', 'POST'])
def result(code):
    abc = data.query.filter_by(specialid = code).first()
    print(abc.likes1)
    if request.method == "POST":
        likea = request.form['flames11']
        likeb = request.form['flames22']
        abc = data.query.filter_by(specialid = code).first()
        abc.likes1 += int(likea)
        abc.likes2 += int(likeb)
        db.session.add(abc)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('compare.html',image1loc = 'image1_'+str(code)+'.png',image2loc = 'image2_'+str(code)+'.png',abc1 = abc.likes1,abc2 = abc.likes2)

@app.route('/admin', methods = ['POST','GET'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'aadi' and password == '1492':
            return redirect(url_for('showdata'))
    return render_template('admin.html')

@app.route('/showdata', methods = ['POST','GET'])
def showdata():
    if request.method == "GET":
        complete_data = data.query.all()
        return render_template('admindata.html',complete_data = complete_data)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if request.method == 'POST':
        user_to_delete = data.query.get_or_404(user_id)
        # Delete the user from the database
        db.session.delete(user_to_delete)
        db.session.commit()
        complete_data = data.query.all()
        image_path1 = os.path.join(app.config['UPLOAD_FOLDER'], 'image1_'+ str(user_to_delete.specialid) + '.png')
        image_path2 = os.path.join(app.config['UPLOAD_FOLDER'], 'image2_'+ str(user_to_delete.specialid) + '.png')

    # Checking if the file exists
    print(os.path.exists(image_path1))
    if os.path.exists(image_path1) and os.path.exists(image_path2):
        # The file exists
        os.remove(image_path1)
        os.remove(image_path2)
        return render_template('admindata.html',complete_data = complete_data)
    else:
        # The file does not exist
        print('Failed')
    
        return render_template('admindata.html',complete_data = complete_data)
    
if __name__ == "__main__":
    app.run(debug=True)