-- Create the `recipes` table
CREATE TABLE  recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients TEXT,
    steps TEXT,
    prep_time VARCHAR(50),
    category VARCHAR(100),
    image VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the `users` table
CREATE TABLE  users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the `meal_planner` table
CREATE TABLE  meal_planner (
    user_id INT NOT NULL,
    recipe_id INT NOT NULL,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

-- Fetch all recipes
SELECT id, title, prep_time, image FROM recipes;

-- Fetch recipe details by ID
SELECT * FROM recipes WHERE id = %s;

-- Insert a new recipe
INSERT INTO recipes (title, description, ingredients, steps, prep_time, category, image)
VALUES (%s, %s, %s, %s, %s, %s, %s);

-- Update an existing recipe
UPDATE recipes 
SET title = %s, description = %s, ingredients = %s, steps = %s, 
    prep_time = %s, category = %s, image = %s 
WHERE id = %s;

-- Insert a new user
INSERT INTO users (username, password_hash, email)
VALUES (%s, %s, %s);

-- Fetch user details by username
SELECT * FROM users WHERE username = %s;

-- Add a recipe to the meal planner
INSERT IGNORE INTO meal_planner (user_id, recipe_id)
VALUES (%s, %s);

-- Fetch all recipes for the dropdown
SELECT id, title FROM recipes;

-- Fetch the user's meal plan
SELECT recipes.id, recipes.title, recipes.image 
FROM meal_planner 
JOIN recipes ON meal_planner.recipe_id = recipes.id 
WHERE meal_planner.user_id = %s;
