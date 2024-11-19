from pymongo import MongoClient
import random
from datetime import datetime, timedelta

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['tasktrail_db']

# Collections
tasks_collection = db['tasks']
users_collection = db['users']

# Predefined users
users = [
    {'username': 'alice_w', 'email': 'alice@example.com', 'full_name': 'Alice Wonderland'},
    {'username': 'bob_m', 'email': 'bob@example.com', 'full_name': 'Bob Marley'},
    {'username': 'charlie_s', 'email': 'charlie@example.com', 'full_name': 'Charlie Sheen'},
    {'username': 'diana_j', 'email': 'diana@example.com', 'full_name': 'Diana Johnson'},
    {'username': 'edward_c', 'email': 'edward@example.com', 'full_name': 'Edward Cullen'},
    {'username': 'fiona_p', 'email': 'fiona@example.com', 'full_name': 'Fiona Prince'},
    {'username': 'george_o', 'email': 'george@example.com', 'full_name': 'George Orwell'},
    {'username': 'hannah_b', 'email': 'hannah@example.com', 'full_name': 'Hannah Brown'},
    {'username': 'ian_k', 'email': 'ian@example.com', 'full_name': 'Ian Kirk'},
    {'username': 'julia_t', 'email': 'julia@example.com', 'full_name': 'Julia Thompson'}
]

# Task titles and priorities
task_titles = [
    "Complete project proposal", "Review code changes", "Update documentation", 
    "Prepare for team meeting", "Fix bugs in app", "Plan marketing strategy", 
    "Design new logo", "Write test cases", "Deploy to production", 
    "Conduct user interviews"
]

priorities = ['low', 'medium', 'high']

# Function to create random tasks and assign to users
def create_tasks(user_ids, n):
    for i in range(n):
        task = {
            'title': random.choice(task_titles),
            'description': f"Task {i + 1} description",
            'status': random.choice(['todo', 'in_progress', 'done']),
            'priority': random.choice(priorities),
            'dueDate': (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            'assigned_user': random.choice(user_ids)  # Assign a random user
        }
        tasks_collection.insert_one(task)

if __name__ == '__main__':
    # Delete existing data
    users_collection.delete_many({})
    tasks_collection.delete_many({})
    
    # Insert users into database
    print("Seeding users...")
    user_ids = []
    for user in users:
        user_id = users_collection.insert_one(user).inserted_id
        user_ids.append(user_id)
    
    # Create 20 tasks and assign them to the users
    print("Seeding tasks...")
    create_tasks(user_ids, 20)
    
    print("Database seeded successfully!")
