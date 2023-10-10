#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Research, Author, ResearchAuthors

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Researches(Resource):
    def get(self):
        research = [research.to_dict(only=('id', 'topic', 'year', 'page_count')) for research in Research.query.all()]
        return make_response(research, 200)
    
api.add_resource(Researches, '/research')

class ResearchById(Resource):
    def get(self, id):
        try:
            research = Research.query.filter_by(id=id).first().to_dict(only = ('id', 'topic', 'year', 'page_count', 'authors.id', 'authors.name', 'authors.field_of_study'))
            return make_response(research, 200)
        except Exception:
            return make_response({"error": "Research paper not found"}, 404)
        
    def delete(self, id):
        research = Research.query.filter_by(id=id).first()
        if research:
            try:
                db.session.delete(research)
                db.session.commit()
                return make_response('', 204)
            except Exception:
                return make_response('', 400)
        else:
            return make_response({"error": "Research paper not found"}, 404)
api.add_resource(ResearchById, '/research/<int:id>')

class Authors(Resource):
    def get(self):
        authors = [author.to_dict(only=('id', 'name', 'field_of_study')) for author in Author.query.all()]
        return make_response(authors, 200)
api.add_resource(Authors, '/authors')

class ResearchAuthor(Resource):
    def post(self):
        try:
            new_researchauthor = ResearchAuthors(
                author_id=request.get_json()['author_id'],
                research_id=request.get_json()['research_id']
            )
        except ValueError as e:
            return make_response({"errors": str(e)}, 400)
            

        db.session.add(new_researchauthor)
        db.session.commit()

        return make_response(new_researchauthor.to_dict(only=('author.id', 'author.name', 'author.field_of_study')), 200)
api.add_resource(ResearchAuthor, '/research_author')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
