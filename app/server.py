import os
import pgeocode
import datetime
import boto3
import logging
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app import db, photos
from app.models import User, Match, Message, CreateMatch, UserPhoto, Pass
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
        if request.form.get('birthdate'):
            print(request.form['birthdate'])
            user.birthdate = request.form['birthdate']
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

    age = 0
    print(user.birthdate)
    if user.birthdate:
        age = calculate_age(user.birthdate)

    return render_template('home.html', user=user, city=city, state=state, photos=photo_urls, age=age)


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

    passed_users = Pass.query.filter_by(passer=user.id).all()
    pass_ids = []
    for passed in passed_users:
        pass_ids.append(passed.passee)
    print(pass_ids)
    create_matches = CreateMatch.query.filter_by(matcher=user.id).all()
    awaiting_matches = []
    for match in create_matches:
        awaiting_matches.append(match.matchee)
    print(awaiting_matches)

    search_users = []
    for user in users_nearby:

        if user.id not in pass_ids and user.id not in awaiting_matches:

            photo = UserPhoto.query.filter_by(user_id=user.id).first()
            photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo)

            age = 0
            print(user.birthdate)
            if user.birthdate:
                age = calculate_age(user.birthdate)

            search_users.append((user, photo_url, age))

    return render_template('search.html', users_nearby=users_nearby, search_users=search_users)


@profile_bp.route('/profile_<user_id>', methods=['POST', 'GET'])
def user_profile(user_id):
    user = get_user(session.get('email'))

    profile = User.query.filter_by(id=user_id).first()
    location_pd = get_location(profile.zip)

    awaiting_match = False

    if request.method == 'POST':
        if request.form.get('match_user_id'):
            new_match = match_user(int(request.form['match_user_id']))
            if new_match:
                flash("You have matched!")
        elif request.form.get('pass_user_id'):
            pass_user(int(request.form['pass_user_id']))
            flash('You have passed.')
            return redirect(url_for('profile_bp.search_users'))

    matched = False
    match = CreateMatch.query.filter_by(matcher=user.id).filter_by(matchee=profile.id).first()
    if match:
        matched = match.matched
        if not matched:
            awaiting_match = True

    photos = UserPhoto.query.filter_by(user_id=profile.id).all()
    photo_urls = []
    for photo in photos:
        photo_urls.append('https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo))
    print(photo_urls)

    age = 0
    print(profile.birthdate)
    if profile.birthdate:
        age = calculate_age(profile.birthdate)

    return render_template('profile.html', user=profile, location=location_pd, matched=matched, match=match,
                           photos=photo_urls, awaiting_match=awaiting_match, age=age)


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

        new_match = Match(user_1=user.id, user_2=profile.id, timestamp=datetime.datetime.now())
        db.session.add(new_match)
        db.session.commit()

        return True


def pass_user(user_id):
    user = get_user(session.get('email'))

    profile = User.query.filter_by(id=user_id).first()
    new_pass = Pass(passer=user.id, passee=profile.id)
    db.session.add(new_pass)
    db.session.commit()

    return True


@profile_bp.route('/unmatch_user_<user_id>', methods=['GET', 'POST'])
def unmatch_user(user_id):
    user = get_user(session.get('email'))

    match = Match.query.filter_by(user_1=int(user_id)).filter_by(user_2=user.id).first()
    if not match:
        match = Match.query.filter_by(user_2=int(user_id)).filter_by(user_1=user.id).first()
    print("MATCH", match)
    print(match.user_1, match.user_2)

    db.session.delete(match)
    db.session.commit()

    create_match = CreateMatch.query.filter_by(matcher=user.id).filter_by(matchee=int(user_id)).first()
    print(create_match)
    create_match.matched = False
    db.session.add(create_match)
    db.session.commit()

    create_match_matchee = CreateMatch.query.filter_by(matcher=int(user_id)).filter_by(matchee=user.id).first()
    print(create_match_matchee)
    create_match_matchee.matched = False
    db.session.add(create_match_matchee)
    db.session.commit()

    flash('Unmatched successfully.')

    return redirect(url_for('profile_bp.show_matches'))


@profile_bp.route('/send_message_<user_id>', methods=['GET', 'POST'])
def send_message(user_id):
    user = get_user(session.get('email'))
    profile = User.query.filter_by(id=user_id).first()
    location_pd = get_location(profile.zip)

    match = Match.query.filter_by(user_1=int(user_id)).filter_by(user_2=user.id).first()
    if not match:
        match = Match.query.filter_by(user_2=int(user_id)).filter_by(user_1=user.id).first()

    if request.method == 'POST':
        text = request.form.get('text')
        print(text)

        message = Message(match_id=match.id,
                          sender=user.id,
                          text=text,
                          timestamp=datetime.datetime.now())
        db.session.add(message)
        db.session.commit()

    messages = Message.query.filter_by(match_id=match.id).all()
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

    age = 0
    print(profile.birthdate)
    if profile.birthdate:
        age = calculate_age(profile.birthdate)

    return render_template('messages.html', profile=profile, messages=messages, location=location_pd,
                           user_photo=user_photo_url, match_photo=match_photo_url, profile_photos=profile_photos,
                           age=age)


@profile_bp.route('/matches', methods=['GET', 'POST'])
def show_matches():
    user = get_user(session.get('email'))

    matches = CreateMatch.query.filter_by(matcher=user.id).filter_by(matched=True).all()

    match_users = []
    for match in matches:
        mu = User.query.filter_by(id=match.matchee).first()

        photo = UserPhoto.query.filter_by(user_id=mu.id).first()
        photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo)

        age = 0
        print(mu.birthdate)
        if mu.birthdate:
            age = calculate_age(mu.birthdate)

        match_users.append((mu, photo_url, age))


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


def calculate_age(birthdate):
    today = datetime.date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    return age


# s3 = boto3.client('s3')
# with open("FILE_NAME", "rb") as f:
#     s3.upload_fileobj(f, "BUCKET_NAME", "OBJECT_NAME")
