import os
import pgeocode
import datetime
import boto3
import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import db
from app.models import User, Match, Message, CreateMatch
from app.auth import get_user

profile_bp = Blueprint('profile_bp', __name__)


@profile_bp.route('/home', methods=['POST', 'GET'])
def home():
    user = get_user(session.get('email'))

    if request.method == 'POST':
        if request.form['age']:
            user.age = int(request.form['age'])
        if request.form['gender']:
            user.gender = request.form['gender']
        if request.form['interested_in']:
            user.interested_in = request.form['interested_in']
        if request.form['bio']:
            user.bio = request.form['bio']
        if request.form['interests']:
            user.interests = request.form['interests']
        if request.form['pet_peeves']:
            user.pet_peeves = request.form['pet_peeves']
        if request.form['zip']:
            user.zip = request.form['zip']
        db.session.add(user)
        db.session.commit()
    location_pd = get_location(user.zip)

    return render_template('home.html', user=user, location=location_pd)


def get_location(zip):
    pgeo = pgeocode.Nominatim('us')
    pd = pgeo.query_postal_code(zip)

    return pd


@profile_bp.route('/update_profile', methods=['POST', 'GET'])
def update_profile():
    user = get_user(session.get('email'))


@profile_bp.route('/search_users')
def search_users():
    user = get_user(session.get('email'))

    users_nearby = User.query.filter_by(zip=user.zip).filter(User.email != user.email).all()
    print(users_nearby)

    return render_template('search.html', users_nearby=users_nearby)


@profile_bp.route('/profile_<user_id>', methods=['POST', 'GET'])
def user_profile(user_id):
    user = get_user(session.get('email'))

    profile = User.query.filter_by(id=user_id).first()
    location_pd = get_location(profile.zip)

    if request.method == 'POST':
        if request.form['userID']:
            print(request.form['userID'])
            new_match = match_user(int(request.form['userID']))
            if new_match:
                flash("New match created")
    match = CreateMatch.query.filter_by(matcher=user.id).filter_by(matchee=profile.id).filter_by(matched=True).first()
    if match:
        matched = True
    else:
        matched = False

    return render_template('profile.html', user=profile, location=location_pd, matched=matched, match=match)


def match_user(user_id):
    user = get_user(session.get('email'))

    profile = User.query.filter_by(id=user_id).first()
    new_create_match = CreateMatch(matcher=user.id, matchee=profile.id)
    existing_match = CreateMatch.query.filter_by(matcher=profile.id).filter_by(matchee=user.id).first()
    db.session.add(new_create_match)
    db.session.commit()

    if existing_match:
        new_create_match.matched = True
        db.session.add(new_create_match)

        existing_match.matched = True
        db.session.add(existing_match)

        # new_match = Match(user_1=user.id, user_2=profile.id, timestamp=datetime.datetime.now())
        # db.session.add(new_match)
        db.session.commit()

    return True


@profile_bp.route('/send_message_<user_id>', methods=['GET', 'POST'])
def send_message(user_id):
    user = get_user(session.get('email'))
    profile = User.query.filter_by(id=user_id).first()
    location_pd = get_location(profile.zip)

    if request.method == 'POST':
        text = request.form.get('text')
        print(text)
        match = Match.query.filter_by(user_1=int(user_id)).first()
        if not match:
            match = Match.query.filter_by(user_2=int(user_id)).first()
        if match.user_1 == user.id:
            receiver = match.user_2
        else:
            receiver = match.user_1
        print(receiver)

        message = Message(match_id=match.id,
                          sender=user.id,
                          text=text,
                          timestamp=datetime.datetime.now())
        db.session.add(message)
        db.session.commit()

    messages = Message.query.filter_by()

    return render_template('messages.html', profile=profile, messages=messages, location=location_pd)


@profile_bp.route('/matches', methods=['GET', 'POST'])
def show_matches():
    user = get_user(session.get('email'))

    matches = CreateMatch.query.filter_by(matcher=user.id).filter_by(matched=True).all()

    match_users = []
    for match in matches:
        mu = User.query.filter_by(id=match.matchee).first()
        match_users.append(mu)

    return render_template('matches.html', matches=match_users)


from botocore.exceptions import ClientError
from botocore.config import Config
from werkzeug.utils import secure_filename


my_config = Config(
    region_name='us-east-2',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')


@profile_bp.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    print("TEST")

    user = get_user(session.get('email'))
    bucket = 'spectrum-user-images'

    img = request.files['img']
    print(img)
    img_name = secure_filename(img.filename)
    user_id = str(user.id)
    file_name = '{}/{}'.format(user_id, img_name)
    print(file_name)
    img.save(os.path.join('/tmp', file_name))

    # If S3 object_name was not specified, use file_name
    object_name = file_name

    # Upload the file
    s3 = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY
                      )
    try:
        response = s3.upload_file(file_name, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        flash('Image failed to upload')
        return redirect('profile_bp.home')

    flash('Image uploaded successfully')
    return redirect('profile_bp.home')


# s3 = boto3.client('s3')
# with open("FILE_NAME", "rb") as f:
#     s3.upload_fileobj(f, "BUCKET_NAME", "OBJECT_NAME")
