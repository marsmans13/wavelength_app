import os
import pgeocode
import datetime
import boto3
import logging
import requests
import random
from flask import (
    Blueprint, flash, g, redirect, render_template, session, url_for, request
)
from app import db, photos
from app.models import User, Match, Message, CreateMatch, UserPhoto, Pass
from app.auth import get_user, login_required

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


ice_breakers = ['What is the last thing you read?', 'What is your favorite thing to read about?',
                'Who do you look up to most?', 'Do you listen to music, and if so, what kind?',
                'If you could do any job in the world, what would it be?']


@profile_bp.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    user = get_user(session.get('email'))
    print("USER ID", user.id)

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
        city = 'None'
        state = 'None'
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

    return render_template('home.html', user=user, city=city, state=state, photos=user_photos, age=age)


def get_location(zip):
    pgeo = pgeocode.Nominatim('us')
    pd = pgeo.query_postal_code(zip)

    return pd


@profile_bp.route('/search_users')
@login_required
def search_users():
    user = get_user(session.get('email'))

    # https://www.zipcodeapi.com/API#radius
    api_key = os.environ.get('ZIP_API_KEY_TEST')
    print(api_key)
    zip_api_url = "https://www.zipcodeapi.com/rest/{api_key}/radius.{format}/{zip_code}/{distance}/{units}?minimal".format(
        api_key=api_key, format="json", zip_code=user.zip, distance="5", units="miles"
    )

    zips_nearby = [user.zip]
    try:
        zips_request = requests.get(zip_api_url)
        print(zips_request.text)
        print(dir(zips_request))
        zips_nearby = zips_request.json().get('zip_codes') + [user.zip]
        # returns {'zip_codes': ['30315', '30316'...]}
    except Exception as e:
        print(f'Zip code API request failed: {e}')

    users_nearby = User.query.filter(User.zip.in_(zips_nearby)).filter(User.email != user.email).all()
    print(users_nearby)

    passed_users = Pass.query.filter_by(passer=user.id).all()
    pass_ids = []
    for passed in passed_users:
        pass_ids.append(passed.passee)

    create_matches = CreateMatch.query.filter_by(matcher=user.id).all()
    awaiting_matches = []
    for match in create_matches:
        awaiting_matches.append(match.matchee)

    search_users = []
    for user in users_nearby:

        if user.id not in pass_ids and user.id not in awaiting_matches:

            photo = UserPhoto.query.filter_by(user_id=user.id).first()
            photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo)

            location_pd = get_location(user.zip)

            age = 0
            print(user.birthdate)
            if user.birthdate:
                age = calculate_age(user.birthdate)

            search_users.append((user, photo_url, age, location_pd))

    return render_template('search.html', users_nearby=users_nearby, search_users=search_users)


@profile_bp.route('/profile_<user_id>', methods=['POST', 'GET'])
@login_required
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

                ice_breaker = random.choice(ice_breakers)
                love_bot = User.query.filter_by(id=10).first()
                love_bot_message = Message(match_id=new_match.id, sender=love_bot.id, text=ice_breaker)
                db.session.add(love_bot_message)
                db.session.commit()

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

        return new_match


def pass_user(user_id):
    user = get_user(session.get('email'))

    profile = User.query.filter_by(id=user_id).first()
    new_pass = Pass(passer=user.id, passee=profile.id)
    db.session.add(new_pass)
    db.session.commit()

    return True


@profile_bp.route('/unmatch_user_<user_id>', methods=['GET', 'POST'])
@login_required
def unmatch_user(user_id):
    user = get_user(session.get('email'))

    match = Match.query.filter_by(user_1=int(user_id)).filter_by(user_2=user.id).first()
    if not match:
        match = Match.query.filter_by(user_2=int(user_id)).filter_by(user_1=user.id).first()

    db.session.delete(match)
    db.session.commit()

    create_match = CreateMatch.query.filter_by(matcher=user.id).filter_by(matchee=int(user_id)).first()
    create_match.matched = False
    db.session.add(create_match)
    db.session.commit()

    create_match_matchee = CreateMatch.query.filter_by(matcher=int(user_id)).filter_by(matchee=user.id).first()
    create_match_matchee.matched = False
    db.session.add(create_match_matchee)
    db.session.commit()

    flash('Unmatched successfully.')

    return redirect(url_for('profile_bp.show_matches'))


@profile_bp.route('/block_user_<user_id>', methods=['GET', 'POST'])
@login_required
def block_user(user_id):
    user = get_user(session.get('email'))

    match_user = User.query.filter_by(id=int(user_id)).first()

    match = Match.query.filter_by(user_1=int(user_id)).filter_by(user_2=user.id).first()
    if not match:
        match = Match.query.filter_by(user_2=int(user_id)).filter_by(user_1=user.id).first()

    match.blocked = True
    db.session.add(match)
    db.session.commit()

    create_match = CreateMatch.query.filter_by(matcher=user.id).filter_by(matchee=int(user_id)).first()
    create_match.matched = False
    db.session.add(create_match)
    db.session.commit()

    create_match_matchee = CreateMatch.query.filter_by(matcher=int(user_id)).filter_by(matchee=user.id).first()
    create_match_matchee.matched = False
    db.session.add(create_match_matchee)
    db.session.commit()

    flash('{} blocked.'.format(match_user.username))

    return redirect(url_for('profile_bp.show_matches'))


@profile_bp.route('/send_message_<user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    user = get_user(session.get('email'))
    profile = User.query.filter_by(id=user_id).first()
    location_pd = get_location(profile.zip)

    match = Match.query.filter_by(user_1=int(user_id)).filter_by(user_2=user.id).first()
    if not match:
        match = Match.query.filter_by(user_2=int(user_id)).filter_by(user_1=user.id).first()
    print('MATCH', match)

    if request.method == 'POST':
        text = request.form.get('text')
        print(text)

        message = Message(match_id=match.id,
                          sender=user.id,
                          text=text,
                          timestamp=datetime.datetime.utcnow())
        db.session.add(message)
        db.session.commit()

    ice_breaker_message = Message.query.filter_by(match_id=match.id).filter_by(sender=10).first()
    messages = Message.query.filter_by(match_id=match.id).filter(Message.sender != 10).all()
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
                           age=age, ice_breaker_message=ice_breaker_message)


@profile_bp.route('/matches', methods=['GET', 'POST'])
@login_required
def show_matches():
    user = get_user(session.get('email'))

    matches = CreateMatch.query.filter_by(matcher=user.id).filter_by(matched=True).all()

    match_users = []
    for match in matches:
        mu = User.query.filter_by(id=match.matchee).first()

        photo = UserPhoto.query.filter_by(user_id=mu.id).first()
        photo_url = 'https://spectrum-user-images.s3.us-east-2.amazonaws.com/{}'.format(photo.photo)

        age = 0
        if mu.birthdate:
            age = calculate_age(mu.birthdate)

        match_obj = Match.query.filter_by(user_1=mu.id).filter_by(user_2=user.id).first()
        if not match_obj:
            match_obj = Match.query.filter_by(user_2=mu.id).filter_by(user_1=user.id).first()

        messages = Message.query.filter_by(match_id=match_obj.id).filter(Message.sender != 10).all()
        if messages:
            last_message = messages[-1]
            print(last_message.timestamp)
        else:
            last_message = None

        match_users.append((mu, photo_url, age, last_message))

    return render_template('matches.html', matches=match_users)


@profile_bp.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():

    user = get_user(session.get('email'))
    bucket = 'spectrum-user-images'

    img = request.files['img']

    filename = photos.save(img)

    img_name = secure_filename(img.filename)
    user_id = str(user.id)
    file_name = '/tmp/{}'.format(filename)

    # If S3 object_name was not specified, use file_name
    object_name = 'user-images/{}/{}'.format(user_id, img_name)

    # Upload the file
    s3 = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY
                      )

    try:
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


@profile_bp.route('/delete_image_<photo_id>', methods=['GET', 'POST'])
@login_required
def delete_image(photo_id):

    user = get_user(session.get('email'))
    bucket = 'spectrum-user-images'
    photo = UserPhoto.query.filter_by(id=int(photo_id)).first()

    try:
        s3 = boto3.resource('s3',
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY
                            )
        obj = s3.Object(bucket, photo.photo)
        obj.delete()
        print('photo deleted')
    except Exception as e:
        print("Failed to delete photo from bucket {}: {}".format(bucket, e))
        return redirect(url_for('profile_bp.home'))

    try:
        UserPhoto.query.filter_by(user_id=user.id).filter_by(id=int(photo_id)).delete()
        print("deleted photo from records")
        db.session.commit()
    except:
        print("delete photo from db failed")

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
