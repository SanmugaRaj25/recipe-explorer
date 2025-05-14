from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
import pymysql  # Use pymysql for MySQL
import os
from werkzeug.security import generate_password_hash, check_password_hash

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'
app.static_folder = 'static'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# MySQL connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MYsqlpass@123',
    'database': 'recipes'
}

# Database initialization
def init_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                ingredients TEXT,
                steps TEXT,
                prep_time VARCHAR(50),
                category VARCHAR(100),
                image VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS meal_planner (
                user_id INT NOT NULL,
                recipe_id INT NOT NULL,
                PRIMARY KEY (user_id, recipe_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (recipe_id) REFERENCES recipes(id)
            )''')
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    filename = filename.replace('\\', '/').replace('uploads/', '')  # Normalize the filename
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# View all recipes
@app.route('/')
def view_recipes():
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, prep_time, image FROM recipes")
            recipes = cursor.fetchall()
    except pymysql.MySQLError as e:
        flash(f"Database error: {e}")
        recipes = []
    finally:
        conn.close()
    return render_template('view_recipes.html', recipes=recipes)

# View recipe details
@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
            recipe = cursor.fetchone()
            if not recipe:
                flash('Recipe not found.')
                return redirect(url_for('view_recipes'))
    except pymysql.MySQLError as e:
        flash(f"Database error: {e}")
        return redirect(url_for('view_recipes'))
    finally:
        conn.close()
    return render_template('recipe_details.html', recipe=recipe)

# Add a new recipe
@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        steps = request.form['steps']
        prep_time = request.form['prep_time']
        category = request.form['category']
        image = request.files.get('image')

        if not title or not ingredients or not steps or not prep_time or not category:
            flash('All fields are required.')
            return redirect(request.url)

        if image and allowed_file(image.filename):
            filename = image.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(file_path)
        else:
            filename = 'default.jpg'

        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO recipes (title, description, ingredients, steps, prep_time, category, image)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                               (title, description, ingredients, steps, prep_time, category, filename))
            conn.commit()
            flash('Recipe added successfully!')
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}")
        finally:
            conn.close()
        return redirect(url_for('view_recipes'))
    return render_template('add_recipe.html')

# Edit a recipe
@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
            recipe = cursor.fetchone()
            if not recipe:
                flash('Recipe not found.')
                return redirect(url_for('view_recipes'))
    except pymysql.MySQLError as e:
        flash(f"Database error: {e}")
        return redirect(url_for('view_recipes'))
    finally:
        conn.close()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        steps = request.form['steps']
        prep_time = request.form['prep_time']
        category = request.form['category']
        image = request.files.get('image')

        if not title or not ingredients or not steps or not prep_time or not category:
            flash('All fields are required.')
            return redirect(request.url)

        if image and allowed_file(image.filename):
            filename = image.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(file_path)
        else:
            filename = recipe['image']

        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cursor:
                cursor.execute('''UPDATE recipes SET title = %s, description = %s, ingredients = %s, steps = %s, 
                                  prep_time = %s, category = %s, image = %s WHERE id = %s''',
                               (title, description, ingredients, steps, prep_time, category, filename, recipe_id))
            conn.commit()
            flash('Recipe updated successfully!')
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}")
        finally:
            conn.close()
        return redirect(url_for('recipe_details', recipe_id=recipe_id))
    return render_template('edit_recipe.html', recipe=recipe)

# Register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO users (username, password_hash, email)
                                  VALUES (%s, %s, %s)''', (username, password_hash, email))
            conn.commit()
            flash('Registration successful! Please log in.')
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}")
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login a user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                user = cursor.fetchone()
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login successful!')
                return redirect(url_for('view_recipes'))
            else:
                flash('Invalid username or password.')
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}")
        finally:
            conn.close()
    return render_template('login.html')

# Logout a user
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Meal Planner
@app.route('/meal_planner', methods=['GET', 'POST'])
def meal_planner():
    if 'user_id' not in session:
        flash('You must be logged in to access the meal planner.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        if not recipe_id:
            flash('Please select a recipe to add to your meal planner.')
            return redirect(url_for('meal_planner'))

        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cursor:
                cursor.execute('''INSERT IGNORE INTO meal_planner (user_id, recipe_id) VALUES (%s, %s)''',
                               (session.get('user_id'), recipe_id))
            conn.commit()
            flash('Recipe added to your meal planner!')
        except pymysql.MySQLError as e:
            flash(f"Database error: {e}")
        finally:
            conn.close()

    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            # Fetch all recipes for the dropdown
            cursor.execute("SELECT id, title FROM recipes")
            recipes = cursor.fetchall()

            # Fetch the user's meal plan
            cursor.execute('''SELECT recipes.id, recipes.title, recipes.image 
                              FROM meal_planner 
                              JOIN recipes ON meal_planner.recipe_id = recipes.id 
                              WHERE meal_planner.user_id = %s''', (session.get('user_id'),))
            meal_plan = cursor.fetchall()
    except pymysql.MySQLError as e:
        flash(f"Database error: {e}")
        recipes = []
        meal_plan = []
    finally:
        conn.close()
    return render_template('meal_planner.html', recipes=recipes, meal_plan=meal_plan)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)