from wtforms import ValidationError
from blog.customValidation.scoring import categorize_passwd

def passwd_strength(form, field):

    passwd = field.data

    if int(categorize_passwd(passwd)["score"]) <= 2:
        raise ValidationError("Password is weak!")
    
