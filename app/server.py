import os
import pgeocode
import datetime
import boto3
import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import db, photos
from app.models import User, Match, Message, CreateMatch, UserPhoto
from app.auth import get_user

profile_bp = Blueprint('profile_bp', __name__)

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


@profile_bp.route('/home', methods=['POST', 'GET'])
def home():
    user = get_user(session.get('email'))

    if request.method == 'POST':
        print('POST REQUEST SENT')
        if request.form.get('age'):
            user.age = int(request.form['age'])
        if request.form.get('gender'):
            user.gender = request.form['gender']
        if request.form.get('interested_in'):
            user.interested_in = request.form['interested_in']
        if request.form.get('bio'):
            user.bio = request.form['bio']
        if request.form.get('interests'):
            user.interests = request.form['interests']
        if request.form.get('pet_peeves'):
            user.pet_peeves = request.form['pet_peeves']
        if request.form.get('zip'):
            print('ZIP CODE:', request.form['zip'])
            user.zip = request.form['zip']
        db.session.add(user)
        db.session.commit()
    if not user.zip:
        city = None
        state = None
    else:
        location_pd = get_location(user.zip)
        city = location_pd.place_name
        state = location_pd.state_name

    user_photos = UserPhoto.query.filter_by(user_id=user.id).all()

    photo_urls = []
    for photo in user_photos:
        url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo)
        photo_urls.append(url)

    return render_template('home.html', user=user, city=city, state=state, photos=photo_urls)


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

    search_users = []
    for user in users_nearby:

        photo = UserPhoto.query.filter_by(user_id=user.id).first()
        photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo)

        search_users.append((user, photo_url))

    return render_template('search.html', users_nearby=users_nearby, search_users=search_users)


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

    photos = UserPhoto.query.filter_by(user_id=profile.id).all()
    photo_urls = []
    for photo in photos:
        photo_urls.append('https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo))
    print(photo_urls)

    return render_template('profile.html', user=profile, location=location_pd, matched=matched, match=match, photos=photo_urls)


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
    user_photo = UserPhoto.query.filter_by(user_id=user.id).first()
    match_photo = UserPhoto.query.filter_by(user_id=profile.id).first()

    if user_photo:
        user_photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(user_photo.photo)
    else:
        user_photo_url = ""
    if match_photo:
        match_photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(match_photo.photo)
    else:
        match_photo_url = ""

    match_photos = UserPhoto.query.filter_by(user_id=profile.id).all()
    profile_photos =[]
    for photo in match_photos:
        profile_photos.append('https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo))
    print(profile_photos)

    return render_template('messages.html', profile=profile, messages=messages, location=location_pd,
                           user_photo=user_photo_url, match_photo=match_photo_url, profile_photos=profile_photos)


@profile_bp.route('/matches', methods=['GET', 'POST'])
def show_matches():
    user = get_user(session.get('email'))

    matches = CreateMatch.query.filter_by(matcher=user.id).filter_by(matched=True).all()

    match_users = []
    for match in matches:
        mu = User.query.filter_by(id=match.matchee).first()

        photo = UserPhoto.query.filter_by(user_id=mu.id).first()
        photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo)

        match_users.append((mu, photo_url))

    return render_template('matches.html', matches=match_users)


@profile_bp.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    print("TEST")

    user = get_user(session.get('email'))
    bucket = 'spectrum-user-images'

    img = request.files['img']

    filename = photos.save(img)
    print("NEW", filename)

    img_name = secure_filename(img.filename)
    print(img.headers, img.name)
    user_id = str(user.id)
    file_name = '/tmp/{}'.format(filename)
    print(file_name)

    # If S3 object_name was not specified, use file_name
    object_name = 'user-images/{}/{}'.format(user_id, img_name)

    # Upload the file
    s3 = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY
                      )

    try:
        print("TRYING")

        response = s3.upload_file(file_name, bucket, object_name)
        print(response)
    except Exception as e:
        logging.error(e)
        flash('Image failed to upload')
        return redirect(url_for('profile_bp.home'))

    os.remove(file_name)
    save_image_to_profile(object_name)

    flash('Image uploaded successfully')
    return redirect(url_for('profile_bp.home'))


def save_image_to_profile(s3_path):
    user = get_user(session.get('email'))

    new_photo = UserPhoto(user_id=user.id, photo=s3_path)
    print(s3_path)
    db.session.add(new_photo)
    db.session.commit()


# s3 = boto3.client('s3')
# with open("FILE_NAME", "rb") as f:
#     s3.upload_fileobj(f, "BUCKET_NAME", "OBJECT_NAME")
