import sqlite3
from faker import Faker
import random


conn = sqlite3.connect("task_management.db")
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname VARCHAR(100),
    email VARCHAR(100) UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100),
    description TEXT,
    status_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (status_id) REFERENCES status(id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
''')


cursor.executemany('''
INSERT OR IGNORE INTO status (name) VALUES (?)
''', [('new',), ('in progress',), ('completed',)])

conn.commit()
print("Таблицы созданы и заполнены статусами.")


fake = Faker()


for _ in range(10):
    fullname = fake.name()
    email = fake.unique.email()
    cursor.execute('''
    INSERT INTO users (fullname, email) VALUES (?, ?)
    ''', (fullname, email))


cursor.execute("SELECT id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT id FROM status")
status_ids = [row[0] for row in cursor.fetchall()]


for _ in range(20):
    title = fake.sentence(nb_words=5)
    description = fake.text()
    status_id = random.choice(status_ids)
    user_id = random.choice(user_ids)
    cursor.execute('''
    INSERT INTO tasks (title, description, status_id, user_id) VALUES (?, ?, ?, ?)
    ''', (title, description, status_id, user_id))

conn.commit()
print("База данных заполнена случайными данными.")

user_id = 1  # замените на нужный user_id
cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
print("Задания пользователя:", cursor.fetchall())


cursor.execute('''
SELECT * FROM tasks WHERE status_id = (
    SELECT id FROM status WHERE name = 'new'
)
''')
print("Задания со статусом 'new':", cursor.fetchall())

task_id = 1  # замените на нужный task_id
cursor.execute("UPDATE tasks SET status_id = (SELECT id FROM status WHERE name = 'in progress') WHERE id = ?", (task_id,))
conn.commit()
print(f"Статус задания с id {task_id} обновлен.")


cursor.execute('''
SELECT * FROM users WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks)
''')
print("Пользователи без заданий:", cursor.fetchall())

cursor.execute('''
INSERT INTO tasks (title, description, status_id, user_id) VALUES (?, ?, ?, ?)
''', ("Новое задание", "Описание нового задания", 1, user_id))
conn.commit()
print("Новое задание добавлено для пользователя.")


cursor.execute('''
SELECT * FROM tasks WHERE status_id != (SELECT id FROM status WHERE name = 'completed')
''')
print("Незавершенные задания:", cursor.fetchall())


task_id_to_delete = 2  # замените на нужный task_id
cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id_to_delete,))
conn.commit()
print(f"Задание с id {task_id_to_delete} удалено.")


email_domain = "%@example.com"  # замените на нужный домен
cursor.execute("SELECT * FROM users WHERE email LIKE ?", (email_domain,))
print("Пользователи с доменной частью '@example.com':", cursor.fetchall())


new_name = "Новое Имя"
cursor.execute("UPDATE users SET fullname = ? WHERE id = ?", (new_name, user_id))
conn.commit()
print(f"Имя пользователя с id {user_id} обновлено.")


cursor.execute('''
SELECT status.name, COUNT(tasks.id) FROM tasks
JOIN status ON tasks.status_id = status.id
GROUP BY status.name
''')
print("Количество задач для каждого статуса:", cursor.fetchall())


cursor.execute('''
SELECT tasks.* FROM tasks
JOIN users ON tasks.user_id = users.id
WHERE users.email LIKE ?
''', (email_domain,))
print("Задания пользователей с доменом '@example.com':", cursor.fetchall())


cursor.execute("SELECT * FROM tasks WHERE description IS NULL OR description = ''")
print("Задания без описания:", cursor.fetchall())


cursor.execute('''
SELECT users.fullname, tasks.title FROM tasks
JOIN users ON tasks.user_id = users.id
JOIN status ON tasks.status_id = status.id
WHERE status.name = 'in progress'
''')
print("Пользователи и их задачи со статусом 'in progress':", cursor.fetchall())


cursor.execute('''
SELECT users.fullname, COUNT(tasks.id) FROM users
LEFT JOIN tasks ON users.id = tasks.user_id
GROUP BY users.id
''')
print("Пользователи и количество их задач:", cursor.fetchall())


conn.close()
