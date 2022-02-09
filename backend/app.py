from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from bson import objectid
import hashlib
import jwt
import os
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == "__main__":
    app.run(host='0.0.0.0')

def get_database():
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(
        "mongodb+srv://mongodbAdmin:12345abcD@cluster0.kxpuj.mongodb.net/devlopment?retryWrites=true&w=majority")
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['development']


@app.route("/")
def welcome():
    return jsonify({"Version": "0.0.0.1"})


@app.route("/users/")
def get_all_user():
    db = get_database()
    collection = db['users']
    result = list(collection.aggregate([
        {
            "$lookup": {
                "from": "tasks",
                "localField": "tasks",
                "foreignField": "_id",
                "as": "tasks"
            }
        },
        {
            "$project": {
                "_id": {
                    "$toString": "$_id"
                },
                "first_name": 1,
                "last_name": 1,
                "username": 1,
                "tasks": {
                    "_id": {
                        "$toString": "$_id"
                    },
                    "task_name": 1,
                    "description": 1,
                    "finished": 1
                }
            }
        }
    ]))
    return jsonify(result)


@app.route("/users/<uid>")
def get_user(uid):
    db = get_database()
    collection = db['users']
    result = list(collection.aggregate([
        {
            "$match": {"_id": objectid.ObjectId(uid)}
        },
        {
            "$lookup": {
                "from": "tasks",
                "localField": "tasks",
                "foreignField": "_id",
                "as": "tasks"
            }
        },
        {
            "$project": {
                "_id": {
                    "$toString": "$_id"
                },
                "first_name": 1,
                "last_name": 1,
                "username": 1,
                "tasks": {
                    "_id": {
                        "$toString": "$_id"
                    },
                    "task_name": 1,
                    "description": 1,
                    "finished": 1
                }
            }
        }
    ]))
    if result:
        return jsonify(result[0])
    return jsonify({})


@app.route("/users/", methods=["POST"])
def create_user():
    db = get_database()
    collection = db['users']
    user_data = request.get_json()
    user_data['password'] = hashlib.sha256(
        user_data['password'].encode()).hexdigest()
    user_data['tasks'] = []
    id = collection.insert_one(user_data).inserted_id

    return jsonify({"id": str(id)})


@app.route("/users/<uid>", methods=["PATCH"])
def edit_user(uid):
    db = get_database()
    collection = db['users']
    user_data = request.get_json()
    user_db = collection.find_one({"_id": objectid.ObjectId(uid)})
    user_password = user_db['password']
    user_data['tasks'] = user_db['tasks']
    user_data['old_password'] = hashlib.sha256(
        user_data['old_password'].encode()).hexdigest()
    if user_password != user_data['old_password']:
        return jsonify({"error": "password match"})
    user_data['password'] = hashlib.sha256(
        user_data['password'].encode()).hexdigest()
    user_data.pop('old_password', None)
    collection.update_one({"_id": objectid.ObjectId(uid)}, {"$set": user_data})

    return jsonify({"success": True})


@app.route("/users/<uid>", methods=["DELETE"])
def delete_user(uid):
    db = get_database()
    collection = db['users']
    task_collection = db['tasks']
    try:
        tasks = list(collection.find_one(
            {"_id": objectid.ObjectId(uid)})['tasks'])
        collection.delete_one({"_id": objectid.ObjectId(uid)})
        task_collection.update_many({"_id": {"$in": tasks}}, {
                                    "$pull": {"users": objectid.ObjectId(uid)}})
        task_collection.delete_many(
            {"users": {"$lt": [{"$size": "users"}, 1]}})
    except:
        return jsonify({"success": False})

    return jsonify({"success": True})

# [ TASK ]========================================================================


@app.route("/tasks/")
def get_all_tasks():
    db = get_database()
    collection = db['tasks']
    result = list(collection.aggregate([
        {
            "$lookup": {
                "from": "users",
                "localField": "users",
                "foreignField": "_id",
                "as": "users"
            }
        },
        {
            "$project": {
                "_id": {
                    "$toString": "$_id"
                },
                "task_name": 1,
                "description": 1,
                "finished": 1,
                "users": {
                    "_id": {
                        "$toString": "$_id"
                    },
                    "first_name": 1,
                    "last_name": 1,
                }
            }
        }
    ]))
    return jsonify(result)


@app.route("/tasks/<uid>")
def get_task(uid):
    db = get_database()
    collection = db['tasks']
    result = list(collection.aggregate([
        {
            "$match": {"_id": objectid.ObjectId(uid)}
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "users",
                "foreignField": "_id",
                "as": "users"
            }
        },
        {
            "$project": {
                "_id": {
                    "$toString": "$_id"
                },
                "task_name": 1,
                "description": 1,
                "finished": 1,
                "users": {
                    "_id": {
                        "$toString": "$_id"
                    },
                    "first_name": 1,
                    "last_name": 1,
                }
            }
        }
    ]))
    if result:
        return jsonify(result[0])
    return jsonify({})

@app.route("/users/<uid>/tasks")
def get_user_task(uid):
    db = get_database()
    collection = db['users']
    result = list(collection.aggregate([
        {
            "$match": {"_id": objectid.ObjectId(uid)}
        },
        {
            "$lookup": {
                "from": "tasks",
                "localField": "tasks",
                "foreignField": "_id",
                "as": "tasks"
            }
        },
        {
            "$project": {
                "_id":0,
                "tasks": {
                    "_id": {
                        "$toString": "$_id"
                    },
                    "task_name": 1,
                    "description": 1,
                    "finished": 1
                }
            }
        }
    ]))
    if result:
        return jsonify(result[0])
    return jsonify({})

@app.route("/tasks/", methods=["POST"])
def create_task():
    def mapping_obj_id(id):
        return objectid.ObjectId(id)
    db = get_database()
    collection = db['tasks']
    users_collection = db['users']
    task_data = request.get_json()
    task_data['users'] = list(map(mapping_obj_id, task_data['users']))
    id = collection.insert_one(task_data).inserted_id
    users_collection.update_many({"_id": {"$in": task_data['users']}}, {
                                 "$push": {"tasks": id}})

    return jsonify({"id": str(id)})


@app.route("/tasks/<uid>", methods=["PATCH"])
def edit_task(uid):
    db = get_database()
    collection = db['tasks']
    task_data = request.get_json()
    task_db = collection.find_one({"_id": objectid.ObjectId(uid)})
    task_data['users'] = task_db['users']
    collection.update_one({"_id": objectid.ObjectId(uid)}, {"$set": task_data})

    return jsonify({"success": True})


@app.route("/tasks/<uid>", methods=["DELETE"])
def delete_task(uid):
    db = get_database()
    collection = db['tasks']
    users_collection = db['users']
    try:
        users = list(collection.find_one(
            {"_id": objectid.ObjectId(uid)})['users'])

        collection.delete_one({"_id": objectid.ObjectId(uid)})
        users_collection.update_many({"_id": {"$in": users}}, {
                                     "$pull": {"tasks": objectid.ObjectId(uid)}})
    except:
        return jsonify({"success": False})

    return jsonify({"success": True})

#[User task] ======================================================
@app.route("/users/<uid>/tasks/<tid>", methods=["PATCH"])
def assign_user_task(uid, tid):
    db = get_database()
    collection = db['tasks']
    users_collection = db['users']
    try:
        collection.update_many({"_id":objectid.ObjectId(tid) }, {
                                     "$push": {"users": objectid.ObjectId(uid)}})
        users_collection.update_many({"_id":objectid.ObjectId(uid) }, {
                                     "$push": {"tasks": objectid.ObjectId(tid)}})
    except:
        return jsonify({"success": False})

    return jsonify({"success": True})

@app.route("/users/<uid>/tasks/<tid>", methods=["DELETE"])
def delete_user_task(uid, tid):
    db = get_database()
    collection = db['tasks']
    users_collection = db['users']
    try:
        collection.update_many({"_id":objectid.ObjectId(tid) }, {
                                     "$pull": {"users": objectid.ObjectId(uid)}})
        users_collection.update_many({"_id":objectid.ObjectId(uid) }, {
                                     "$pull": {"tasks": objectid.ObjectId(tid)}})
    except:
        return jsonify({"success": False})

    return jsonify({"success": True})

@app.route("/authen/login", methods=["POST"])
def login_user():
    db = get_database()
    collection = db['users']
    users_authen = request.get_json()
    user_username = users_authen['username']
    user_password = hashlib.sha256(users_authen['password'].encode()).hexdigest()
    try:
        user_authen_data = collection.find_one({"username": user_username,"password":user_password})
        if user_authen_data:
            encoded_jwt = jwt.encode({"uid": str(user_authen_data['_id'])}, "testWeb", algorithm="HS256")
            return {"success":True,"token":encoded_jwt}
        return {"success":False}
    except:
        return {"success":False}



@app.route("/authen/check", methods=["POST"])
def check_is_authen():
    db = get_database()
    collection = db['users']
    users_authen = request.get_json()
    user_token = users_authen['token']
    try:
        decoded_data = jwt.decode(user_token, "testWeb", algorithms=["HS256"])
        user_data = collection.find_one({"_id":objectid.ObjectId(decoded_data["uid"])})
        if user_data:
            return {"success":True}
        return {"success":False}
    except:
        return {"success":False}
@app.route("/upload/<file_name>")
def read_file(file_name):
    if file_name == "":
        return {"success":False}
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], file_name)

@app.route("/upload/<file_name>", methods = ['DELETE'])
def delete_file(file_name):
    if file_name == "":
        return {"success":False}

    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
    return {"success":True}

@app.route("/upload", methods=['POST'])
def upload_file():
    print(request.files)
    if 'file' not in request.files:
        return {"success":False}
    file = request.files['file']
    if file.filename == '':
        return {"success":False}
    file_type = file.filename.split('.')[1]
    current_time = datetime.now().timestamp()
    new_file_name = str(file.filename)+str(current_time)
    new_file_hash = hashlib.md5(new_file_name.encode()).hexdigest()
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_file_hash+'.'+file_type))
    return {"success":True}

