from flask import Flask, render_template, request, redirect, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import uuid

#LOOKA TEARLIER PROGRAMS, 
app = Flask(__name__)
app.secret_key = 'asdasvdascfveae2313123'
client = MongoClient("mongodb+srv://kingaryaprince:nF8L5zLTS0rLccJj@cluster0.zzqvh.mongodb.net/?retryWrites=true&w=majority")
db = client["movieticketsapp"]

users = db["users"]
# movies = db["movies"]

# #put in some movies here

# movies.insert_many([
#     {"title": "Avengers: Endgame", "showtimes": ["10:00 AM", "2:00 PM", "7:00 PM"]},
#     {"title": "Mission Impossible: Fallout", "showtimes": ["11:00 AM", "3:00 PM", "8:00 PM"]},
# ])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        existing_user = users.find_one({'username': username})
        if existing_user:
            flash('account already exists', 'danger')
            return redirect('/signup')

        user_data = {'username': username, 'password': password}
        users.insert_one(user_data)
        flash('successfully created account', 'success')
        return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({'username': username, 'password': password})
        if user:
            session['user_id'] = str(user['_id'])
            flash('login successful', 'success')
            return redirect('/dashboard')
        else:
            flash('invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = ObjectId(session['user_id'])
        user = users.find_one({'_id': user_id})
        print()
        return render_template('dashboard.html', user=user)
    
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    if 'user_id' in session:
        if request.method == 'POST':
            user_id = ObjectId(session['user_id'])
            movie = request.form.get('movie')
            showtime = request.form.get('showtime')

            # Store purchased ticket information in the user's record in MongoDB
            users.update_one({'_id': user_id}, {'$push': {'tickets': {'movie': movie, 'showtime': showtime, 'ticket_id': str(uuid.uuid4())}}})
            flash('Ticket purchased successfully!', 'success')

        return render_template('movies.html')

    else:
        return redirect('/login')

@app.route('/purchase', methods=['POST'])
def purchase_ticket():
    if 'user_id' in session:
        user_id = ObjectId(session['user_id'])
        movie = request.form.get('movie')
        showtime = request.form.get('showtime')
        amount = request.form.get('amount')

        users.update_one({'_id': user_id}, {'$push': {'tickets': {'movie': movie, 'showtime': showtime, 'amount': amount, 'ticket_id': str(uuid.uuid4())}}})
        flash('Ticket purchased successfully!', 'success')

        return redirect('/dashboard')  # eedirect to the dashboard after purchase
    else:
        return redirect('/login')
    

@app.route('/cancel')
def cancel_ticket():
    if 'user_id' in session:
        user_id = ObjectId(session['user_id'])
        print('cancelticket')
        ticket_id = request.args['ticket_id']
        print("Ticket ID received: " + ticket_id)

        users.update_one({'_id': user_id}, {'$pull': {'tickets': {'ticket_id': ticket_id}}})
        #add flash messahe if it works
        return redirect('/dashboard')  # Redirect to the dashboard after you cancel ticket.
    else:
        return redirect('/login')



if __name__ == '__main__':
    app.run(debug=True)
    