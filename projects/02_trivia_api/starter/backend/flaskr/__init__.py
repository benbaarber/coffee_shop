import os
from flask import Flask, request, abort, jsonify, redirect
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from sqlalchemy.sql.sqltypes import ARRAY

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def check_page(request, selection, per_page):
  page = request.args.get('page', 1, type=int)


def serialize(selection):
  return [item.format() for item in selection]

def paginate(request, selection, per_page):
  page = request.args.get('page', 1, type=int)
  
  return serialize(selection)[(page - 1) * per_page:page * per_page]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r'/*': {'origins': '*'}})
  
  '''
  @DONE TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @DONE TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PUT, PATCH, DELETE, OPTION')
    
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/')
  def root():
    return redirect(url_for('get_categories'))

  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()

    return jsonify({
      'success': True,
      'categories': {str(category.id): category.type for category in categories}
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    paginated_questions = paginate(request, questions, 10)
    categories = Category.query.order_by(Category.id).all()

    if len(paginated_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(serialize(questions)),
      'categories': {str(category.id): category.type for category in categories},
      'current_category': None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      question.delete()

      return jsonify({
        'success': True,
        'deleted': id
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def submit_question():
    body = request.get_json()
    search_term = body.get('searchTerm')

    try:
      if search_term:
        questions = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search_term)))

        return jsonify({
          'success': True,
          'questions': paginate(request, questions, 10),
          'total_questions': len(serialize(questions)),
          'current_category': None
        })

      else:
        new_question = Question(question=body.get('question'), answer=body.get('answer'), category=body.get('category') ,difficulty=body.get('difficulty'))
        
        if new_question.question and new_question.answer:
          new_question.insert()
        else:
          abort()

        return jsonify({
          'success': True,
          'created': new_question.id
        })
    
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    questions = Question.query.filter(Question.category == id).order_by(Question.id).all()
    paginated_questions = paginate(request, questions, 10)

    if len(paginated_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(serialize(questions)),
      'current_category': Category.query.get(id).type
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    try:
      body = request.get_json()
      category_id = int(body['quiz_category'].get('id'))
      category = Category.query.get(category_id) if category_id != 0 else None
      questions = Question.query.filter(Question.category == category.id).all() if category is not None else Question.query.all()
      available_questions = [question.id for question in questions if question.id not in body['previous_questions']]  

      if len(available_questions) != 0:
        random_question = Question.query.get(random.choice(available_questions))
        
        return jsonify({
          'success': True,
          'question': random_question.format()
        })

      else:
        return jsonify({
          'success': True,
          'question': None
        })
   
    except:
      abort(400)
    


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404, 
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422, 
      "message": "unprocessable"
    }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405, 
      "message": "method not allowed"
    }), 405

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400, 
      "message": "bad request"
    }), 400
  
  return app

    