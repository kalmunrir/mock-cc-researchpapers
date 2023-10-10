from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
import math

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Add models here
class Research(db.Model, SerializerMixin):
    __tablename__ = 'research'

    serialize_rules = ('-researchAuthors.research',)

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String)
    year = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    researchAuthors = db.relationship('ResearchAuthors', back_populates='research')

    authors = association_proxy('researchAuthors', 'author', creator=lambda author_obj: ResearchAuthors(author = author_obj))

    @validates('year')
    def validate_year(self, key, year):
        if math.floor(math.log10(year)) != 3:
            raise ValueError('Year must be a 4 digit integer')
        return year

class ResearchAuthors(db.Model, SerializerMixin):
    __tablename__ = 'researchAuthors'

    serialize_rules = ('-research.researchAuthors', '-author.researchAuthors')

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    research_id = db.Column(db.Integer, db.ForeignKey('research.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    research = db.relationship('Research', back_populates='researchAuthors')
    author = db.relationship('Author', back_populates='researchAuthors')

class Author(db.Model, SerializerMixin):
    __tablename__='authors'

    serialize_rules = ('-researchAuthors.author',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    researchAuthors = db.relationship('ResearchAuthors', back_populates = 'author')

    research = association_proxy('researchAuthors', 'research', creator=lambda research_obj: ResearchAuthors(research = research_obj))

    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        FIELDS = ['AI', 'Robotics', 'Machine Learning', 'Vision', 'Cybersecurity']
        if field_of_study not in FIELDS:
            raise ValueError(f'Field of study must be one of the following: {FIELDS}')
        return field_of_study
