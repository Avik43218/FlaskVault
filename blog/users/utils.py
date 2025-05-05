from PIL import Image
import secrets, os, string, random
from flask import current_app, url_for
from flask_mail import Message
from blog import mail


def save_picture(form_picture):

    random_hex = secrets.token_hex(10)
    _, f_ext = os.path.splitext(form_picture.filename)

    pic_name = random_hex + f_ext
    pic_path = os.path.join(current_app.root_path, 'static/profile', pic_name)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(pic_path)

    return pic_name


def generate_passwd():

    letters = string.ascii_letters
    numbers = string.digits
    symbols = string.punctuation

    charset = letters + numbers + symbols

    byte_size = 12

    temp = random.sample(charset , byte_size)
    final_passwd = "".join(temp)

    return final_passwd

def send_reset_email(user):

    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link,
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, then simply ignore this mail! Thank you!
'''
    mail.send(msg)
    