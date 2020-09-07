from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DECIMAL, Text, DateTime, Date
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from app import db


print('MODEL APP CREATED')


class User(db.Model):

    __tablename__ = "user"

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(50))
    email = Column('email', String(50))
    password = Column('password', String(200))
    age = Column('age', Integer)
    birthdate = Column('birthdate', DateTime)
    gender = Column('gender', String(15))
    interested_in = Column('interested in', String(15))
    bio = Column('bio', Text, nullable=True)
    interests = Column('interest', Text, nullable=True)
    pet_peeves = Column('pet peeves', Text, nullable=True)
    zip = Column('zip', String(15), nullable=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Match(db.Model):

    __tablename__ = "match"

    id = Column('id', Integer, primary_key=True)
    user_1 = Column(Integer, ForeignKey('user.id'))
    user_2 = Column(Integer, ForeignKey('user.id'))
    timestamp = Column('timestamp', Date, nullable=False, default=datetime.utcnow)
    blocked = Column('blocked', Boolean, default=False)


class Message(db.Model):

    __tablename__ = "message"

    id = Column('id', Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('match.id'))
    sender = Column(Integer, ForeignKey('user.id'))
    text = Column('text', Text)
    timestamp = Column('timestamp', DateTime)


class CreateMatch(db.Model):

    __tablename__ = "create_match"

    id = Column('id', Integer, primary_key=True)
    matcher = Column(Integer, ForeignKey('user.id'))
    matchee = Column(Integer, ForeignKey('user.id'))
    matched = Column('matched', Boolean, default=False)


class Pass(db.Model):

    __tablename__ = "pass"

    id = Column('id', Integer, primary_key=True)
    passer = Column(Integer, ForeignKey('user.id'))
    passee = Column(Integer, ForeignKey('user.id'))


class UserPhoto(db.Model):

    __tablename__ = "user_photos"

    id = Column('id', Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    photo = Column('photo', String(100))
