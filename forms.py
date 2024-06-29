from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SelectField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, InputRequired, Length, Optional

class UserAddForm(FlaskForm):
    """Form for adding users."""

    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class PlaylistForm(FlaskForm):
    """Playlist form."""

    name = StringField('Playlist Name', validators=[DataRequired()])

class MusicForm(FlaskForm):
    """Music form."""

    mood = RadioField('How do you want to feel during your run today?', 
                       choices=[('low', 'Calm & Relaxing'), ('mid', 'Uplifting & Groovy'), ('high', 'Energetic & Exciting')],
                       validators=[DataRequired()])
    artist_1 = StringField('Artist 1')
    artist_2= StringField('Artist 2')
    artist_3 = StringField('Artist 3')

class NewRunForm(FlaskForm):
    """New run form."""

    # Custom validator for Select Field - Check if option was chosen
    def choose_option(form, field):
        if (field.data == '--'):
            raise ValidationError('Please select an option...')

    week = SelectField('Week', choices=[('--', 'Please select a week'), ('Week 1', 'Week 1'), ('Week 2', 'Week 2'), ('Week 3', 'Week 3'), ('Week 4', 'Week 4'), ('Week 5', 'Week 5'), ('Week 6', 'Week 6'), 
                                        ('Week 7', 'Week 7'), ('Week 8', 'Week 8'), ('Week 9', 'Week 9'), ('Week 10', 'Week 10')],
                                        validators=[choose_option])
    day = SelectField('Day', choices=[('--', 'Please select a day'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                                      ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
                                      ('Sunday', 'Sunday')], validators=[choose_option])
    
    distance = StringField('Distance (please specify mi/km)', validators = [DataRequired()])

    time = StringField('Total Time (in 00:00:00 or 0h 0m 0s format)', validators=[DataRequired()])
    
    pace = StringField('Pace', validators=[Optional()])

    notes = TextAreaField('Any additional notes or comments to add?', validators=[Optional()])
        
    