import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

with app.app_context():
    db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    if drinks is None:
         formatted_drinks = []
    else:
        formatted_drinks = [drink.short() for drink in drinks]       
    return jsonify({ 'success': True, 'drinks': formatted_drinks })

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    if drinks is None:
        formatted_drinks = []
    else:
        formatted_drinks = [drink.long() for drink in drinks]       
    return jsonify({ 'success': True, 'drinks': formatted_drinks })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()
    try:
         title = body.get('title', None)
         recipe = body.get('recipe', None)
         drink = Drink(title = title, recipe = json.dumps(recipe))  
         drink.insert()     
         filtered_drink = Drink.query.filter(Drink.id == drink.id).one_or_none()
         if filtered_drink is None:
            abort(404)     
         return jsonify({ 'success': True, 'drinks': [filtered_drink.long()] })
    except:
         abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
     try:
          drink = Drink.query.filter(Drink.id == id).one_or_none()
          if drink is None:
               abort(404)
          else:
             body = request.get_json()
             title = body.get('title', None)
             recipe = body.get('recipe', None)
             drink.title = title
             drink.recipe =  json.dumps(recipe)
             drink.update()
             filtered_drink = Drink.query.filter(Drink.id == drink.id).one_or_none() 
             if filtered_drink is None:
                abort(404)       
             return jsonify({ 'success': True, 'drinks': [filtered_drink.long()] })
     except:
          abort(422)

@app.route('/drinks/<int:id>', methods= ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
     try:
          drink = Drink.query.filter(Drink.id == id).one_or_none()
          if drink is None:
               abort(404)
          else:
             drink.delete()
             return jsonify({ 'success': True, 'delete': id})
     except:
          abort(422)     


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    print(error)
    return jsonify({ "success": False, "error": 422, "message": "unprocessable" }), 422

@app.errorhandler(400)
def bad_request(error):
        return jsonify({ "success": False,  "error": 400, "message": "bad request" }), 400

@app.errorhandler(500)
def internal_error(error):
        return jsonify({ "success": False, "error": 500, "message": "internal server error" }), 500

@app.errorhandler(401)
def unauthorized_error(error):
        return jsonify({ "success": False, "error": 401, "message": "unAuthorized" }), 401

@app.errorhandler(403)
def forbidden_error(error):
        return jsonify({ "success": False, "error": 403, "message": "forbidden access" }), 403

@app.errorhandler(404)
def not_found_error(error):
        return jsonify({ "success": False, "error": 404, "message": "drink not found" }), 404

@app.errorhandler(405)
def method_not_error(error):
        return jsonify({ "success": False, "error": 405, "message": "method not allowed" }), 405

@app.errorhandler(AuthError)
def authorization_error(error):
     print(error)
     return jsonify({ "success": False, "error": error.status_code, "message": error.error['description'] }), error.status_code
