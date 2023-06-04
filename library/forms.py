from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, SelectField, RadioField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, InputRequired, Length, ValidationError, Regexp, EqualTo

## when passed as a parameter to a template, an object of this class will be rendered as a regular HTML form
## with the additional restrictions specified for each field

class register_form(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)])
    first_name = StringField(validators=[InputRequired()])
    last_name = StringField(validators=[InputRequired()])
    date_of_birth = DateField(validators=[InputRequired()])
    role = SelectField('Role', validators=[DataRequired(message="Role is a required field.")],
                       choices=[('student', 'student'), ('teacher', 'teacher'), ('operator', 'operator')]) 
    school = StringField(validators=[InputRequired()])
    submit = SubmitField('Register')


class login_form(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    
class edit_password_form(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    current_password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)])
    new_password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField(validators=[InputRequired(), Length(min=8, max=20), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField("Edit password")
    

class school_form(FlaskForm):
    school_name = StringField(label = "Name", validators = [DataRequired(message = "Name is a required field.")])
    address = StringField(label = "Address", validators = [DataRequired(message = "Address is a required field.")])
    city = StringField(label = "City", validators = [DataRequired(message = "City is a required field.")])
    phone_number = StringField(label = "Phone Number", validators = [DataRequired(message = "Phone is a required field."), Length(min=10, max=15, message='Phone number must be between 10 and 15 characters.'),                                                               Regexp(r'^[0-9+\-() ]*$', message='Phone number can only contain digits, plus, hyphen, parentheses and spaces.')])
    email = StringField(label = "Email", validators = [DataRequired(message = "Email address is a required field."), Email()])
    school_director_name = StringField(label = "School Director Name", validators = [DataRequired(message = "School director name is a required field.")])
    library_operator_name = StringField(label = "Library Operator Name", validators = [DataRequired(message = "Library operator name is a required field.")])
    submit = SubmitField("Insert School")

class book_form(FlaskForm):
    ISBN = StringField(label = "ISBN", validators = [DataRequired(message = "ISBN is a required field."), Length(min=10, max=15), Regexp(r'^[0-9- ]*$', message='ISBN can only contain digits, hyphen and spaces.')])
    title = StringField(label = "Title", validators = [DataRequired(message = "Title is a required field.")])
    publisher = StringField(label = "Publisher", validators = [DataRequired(message = "Publisher is a required field.")])
    number_of_pages = IntegerField(label = "Number of Pages", validators = [DataRequired(message = "Number of pages is a required field.")])
    summary = StringField(label = "Summary", validators = [DataRequired(message = "Summary is a required field.")])
    available_copies = IntegerField(label = "Available Copies", validators = [DataRequired(message = "Available copies is a required field.")])
    image = StringField(label = "Image", validators = [DataRequired(message = "Image is a required field.")])
    keywords = StringField(label = "Keywords", validators = [DataRequired(message = "Keywords is a required field.")])
    author_first_name = StringField(label = "Author Name", validators = [DataRequired(message = "Author name is a required field.")])
    author_last_name = StringField(label = "Author Surname", validators = [DataRequired(message = "Author surname is a required field.")])
    category = StringField(label = "Category", validators = [DataRequired(message = "Category is a required field.")])
    language = StringField(label = "Language", validators = [DataRequired(message = "Language is a required field.")])

    submit = SubmitField("Submit")


class review_form(FlaskForm):
    ISBN = IntegerField(label = "ISBN", validators = [DataRequired(message = "ISBN is a required field.")])
    rating = RadioField(u'Rating', choices=['1', '2', '3', '4', '5'], validators = [DataRequired(message = "Rating is a required field.")])
    comments = StringField(label = "Comments", validators = [Optional()])
    
    submit = SubmitField("Submit")

class edit_review_form(FlaskForm):
    rating = RadioField(u'Rating', choices=['1', '2', '3', '4', '5'], validators = [DataRequired(message = "Rating is a required field.")])
    comments = StringField(label = "Comments", validators = [Optional()])
    
    submit = SubmitField("Submit")

class delayed_borrowers_form(FlaskForm):
    first_name = StringField(label = "Name", validators = [DataRequired(message = "Name is a required field.")])
    last_name = StringField(label = "Surname", validators = [DataRequired(message = "Surname is a required field.")])
    delay_days = IntegerField(label = "Delay days", validators = [DataRequired(message = "Delay days is a required field.")])
  
    submit = SubmitField("Submit")

class average_ratings_form(FlaskForm):
    username = StringField(label = "Username", validators = [DataRequired(message = "Username is a required field.")])
    category = StringField(label = "Category", validators = [DataRequired(message = "Category is a required field.")])

    submit = SubmitField("Submit")

class loan_statistics_form(FlaskForm):
    year = SelectField('Year', validators=[DataRequired(message="Year is a required field.")],
                       choices=[('2022', '2022'), ('2023', '2023')])  
    month = SelectField('Month', validators=[DataRequired(message="Month is a required field.")],
                        choices=[('1', 'January'), ('2', 'February'), ('3', 'March'),  
                                 ('4', 'April'), ('5', 'May'), ('6', 'June'),
                                 ('7', 'July'), ('8', 'August'), ('9', 'September'),
                                 ('10', 'October'), ('11', 'November'), ('12', 'December')])
    submit = SubmitField("Search")

class category_statistics_form(FlaskForm):
    category = SelectField('Category', validators=[DataRequired(message="Category is a required field.")],
                        choices=[('Science Fiction', 'Science Fiction'), ('Mystery', 'Mystery'), ('Poetry', 'Poetry'), 
                                 ('Self-help', 'Self-help'),  ('Thriller', 'Thriller'), ('History', 'History'), 
                                 ('Fantasy', 'Fantasy'), ('Fiction', 'Fiction'), ('Biography', 'Biography'), ('Romance', 'Romance')])
    submit = SubmitField("Search")

    
class year_selection_form(FlaskForm):
    year = SelectField('Year', validators=[DataRequired(message="Year is a required field.")],
                       choices=[('2022', '2022'), ('2023', '2023')])  
    submit = SubmitField("Search")

