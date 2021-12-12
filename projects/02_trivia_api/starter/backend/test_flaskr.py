import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://benbarber@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {'question': 'Why?', 'answer': 'Because.', 'category': 4, 'difficulty': 5}
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_root(self):
        res = self.client().get("/")

        self.assertEqual(res.status_code, 302)

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['categories'])

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
        self.assertIsNotNone(data['categories'])
        self.assertIsNone(data['current_category'])

    def test_get_questions_out_of_range(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)

    def test_delete_question(self):
        res = self.client().delete("/questions/5")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 5)
        self.assertIsNone(Question.query.get(5))

    def test_delete_nonexistant_question(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)

    def test_submit_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['created'], 24)
        self.assertIsNotNone(Question.query.get(24))
    
    def test_submit_question_without_answer(self):
        self.new_question.update({'answer': ''})

        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 422)
        self.assertIsNone(Question.query.get(25))

    def test_search_questions_with_results(self):
        res = self.client().post("/questions", json={'searchTerm': 'what'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['questions'])
        self.assertEqual(data['total_questions'], 8)
        self.assertIsNone(data['current_category'])

    def test_search_questions_without_results(self):
        res = self.client().post("/questions", json={'searchTerm': 'ewokoniad segournith juniorstein'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['questions'], [])
        self.assertEqual(data['total_questions'], 0)
        self.assertIsNone(data['current_category'])

    def test_get_questions_by_category(self):
        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
        self.assertEqual(data['current_category'], 'Entertainment')

    def test_get_questions_by_category_out_of_range(self):
        res = self.client().get("/categories/5/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 404)

    def test_get_next_question(self):
        res = self.client().post("/quizzes", json={'quiz_category': {'type': 'Science', 'id': 1}, 'previous_questions': [20]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['question']['id'])
        self.assertIsNotNone(data['question']['question'])
        self.assertIsNotNone(data['question']['answer'])
        self.assertEqual(data['question']['category'], 1)
        self.assertIsNotNone(data['question']['difficulty'])

    def test_get_next_question_no_questions_left(self):
        res = self.client().post("/quizzes", json={'quiz_category': {'type': 'Science', 'id': 1}, 'previous_questions': [20, 21, 22]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNone(data['question'])
    
    def test_get_next_question_wrong_method(self):
        res = self.client().get("/quizzes")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 405)



    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()