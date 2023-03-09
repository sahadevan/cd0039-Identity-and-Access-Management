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

# base_url = https://dev-gz5tjefp2qw5ta7u.us.auth0.com
# options.Authority = "https://dev-gz5tjefp2qw5ta7u.us.auth0.com/";
# options.Audience = "drinks";
# barista@gmail.com, barista@123
# manager@gmail.com, manager@123
# https://dev-gz5tjefp2qw5ta7u.us.auth0.com/authorize?audience=drinks&response_type=token&client_id=J5za50yzGym3IF6Ayv1GBy7sIb88qMnK&redirect_uri=https://127.0.0.1:5000/login-results

#vaishnavi-manager-access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InlLMGxKS1UtN0xjcndvT0RTbEUxdCJ9.eyJpc3MiOiJodHRwczovL2Rldi1nejV0amVmcDJxdzV0YTd1LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwODI2MTk1NjE2MTk3MzY0MDM0MSIsImF1ZCI6ImRyaW5rcyIsImlhdCI6MTY3ODEyMTkwOSwiZXhwIjoxNjc4MTI5MTA5LCJhenAiOiJKNXphNTB5ekd5bTNJRjZBeXYxR0J5N3NJYjg4cU1uSyIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmRyaW5rcyIsImdldDpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.DDcp3-aP6Ee5AFDcBerzkwtTplLjEuGSpSvlMa-1B9AXP475zCtBDcMfWTDZCeQZfJKHI6F7jOsZ7N6UeTiaYB9AapgY2oI0_hRE0KL5ZW92Sh28R7D5k1wb6_Qx7xgXL8xbsbdaAjM6LZriJz0GNDJv-rJHwYjgeSSn-JSkig0OXFWk728SJde64MAY-by-gzmF9clhJ_1TCbfVCPjKf8S3vIlK1FzC-6y-gKWJ7jBstsCBeCMSO0Ok6bOSBPqzkFR_ZryzwI6_FhYDylpRaf5KskC_eN9KPyPNSSGvECp1PQkgBsN8iWkigeHKIcsm8aY8VCFvUdtyS7bpqJyxPw

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
with app.app_context():
    db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    if len(drinks) == 0: 
        abort(404)       
    formatted_drinks = [drink.short() for drink in drinks]       
    return jsonify({ 'success': True, 'drinks': formatted_drinks })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
def get_drinks_detail():
    drinks = Drink.query.all()
    if len(drinks) == 0: 
        abort(404)       
    formatted_drinks = [drink.long() for drink in drinks]       
    return jsonify({ 'success': True, 'drinks': formatted_drinks })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def create_drinks():
    body = request.get_json()
    try:
         title = body.get('title', None)
         receipe = body.get('recipe', None)
         drink = Drink(title = title, receipe = receipe)         
         filtered_drink = Drink.query.filter(Drink.id == drink.id).one_or_none()     
         return jsonify({ 'success': True, 'drinks': None if filtered_drink is None else filtered_drink.long() })
    except:
         abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({ "success": False, "error": 422, "message": "unprocessable" }), 422

@app.errorhandler(400)
def bad_request(error):
        return jsonify({ "success": False,  "error": 400, "message": "bad request" }), 400

@app.errorhandler(405)
def method_not_allowed(error):
        return jsonify({ "success": False, "error": 405, "message": "method not allowed" }), 405

@app.errorhandler(500)
def internal_error(error):
        return jsonify({ "success": False, "error": 500, "message": "internal server error" }), 500


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
