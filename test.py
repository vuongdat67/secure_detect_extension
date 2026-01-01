import os

def run(user_input):
    os.system("ping " + user_input)
def calc(expr):
    return eval(expr)
API_KEY = "sk_test_123456789"

def call_api():
    return API_KEY
def read_file(name):
    with open("/var/data/" + name) as f:
        return f.read()
import pickle

def load(data):
    return pickle.loads(data)
import sqlite3

def login(user, pwd):
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    q = f"SELECT * FROM users WHERE u='{user}' AND p='{pwd}'"
    cur.execute(q)
    return cur.fetchone()
import yaml

def load_config(data):
    return yaml.load(data)
import hashlib

def hash_pwd(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()
