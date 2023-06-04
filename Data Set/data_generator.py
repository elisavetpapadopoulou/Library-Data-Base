# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from collections import OrderedDict
from faker import Faker
from datetime import datetime, timedelta
import codecs
import random

locales = OrderedDict ([
    #('el-GR', 7),
    ('en-US', 2),
    #('el-CY', 4)
])
fake = Faker(locales)

########## AUTHORS ################
AUTHOR_NUMBER = 68
TABLE_NAME = "author"
TABLE_COLUMNS = [ "first_name", "last_name", "biography"]
content = ""

for i in range(AUTHOR_NUMBER):
    first_name = fake.first_name()
    last_name = fake.last_name()
    biography = fake.paragraph(nb_sentences=3)
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{first_name}", "{last_name}", "{biography}");\n'

########## CATEGORY ###############
TABLE_NAME = "category"
TABLE_COLUMNS = ["name"]
predefined_categories = ['Fiction', 'Science Fiction', 'Mystery', 'Romance', 'Fantasy', 'Thriller', 'Biography', 'History', 'Self-help', 'Poetry']
CATEGORY_NUMBER = 10;

for i in range(CATEGORY_NUMBER):
    name = predefined_categories[i]
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{name}");\n'
    
########## LANGUAGE ###############
TABLE_NAME = "language"
TABLE_COLUMNS = ["language_id", "name"]
language_ids = ['ENG', 'GR', 'GER']
predifined_languages = ['English', 'Greek', 'German']
LANGUAGE_NUMBER = 3

for i in range(LANGUAGE_NUMBER):
    language_id = language_ids[i]
    name = predifined_languages[i]

    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{language_id}", "{name}");\n'

########## SCHOOLS ################

SCHOOL_NUMBER = 4
TABLE_NAME = "school"
TABLE_COLUMNS = [ "school_name", "address", "city", "phone_number", "email", "school_director_name", "library_operator_name"]


for i in range(SCHOOL_NUMBER):
    school_name = fake.company()
    address = fake.address() 
    city = fake.city()
    phone_number = fake.random_int(min=1000000000, max=9999999999)
    email = fake.email()
    school_director_name = fake.name()
    library_operator_name = fake.name()
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{school_name}", "{address}", "{city}", "{phone_number}", "{email}", "{school_director_name}", "{library_operator_name}");\n'


########## BOOKS ##################

BOOK_NUMBER = 300
TABLE_NAME = "book"
TABLE_COLUMNS = ["ISBN", "title", "publisher", "number_of_pages", "summary", "available_copies", "image", "language_id","school_id", "keywords"]
books = []
for i in range(BOOK_NUMBER):
    ISBN = random.randint(1000000000000, 9999999999999)
    title = fake.catch_phrase()
    publisher = fake.company()
    number_of_pages = random.randint(100, 1000)
    summary = fake.paragraph(nb_sentences=3)
    available_copies = random.randint(1, 7)
    image = fake.image_url()
    language_id = random.choice(language_ids)
    school_id = random.randint(1, SCHOOL_NUMBER)  # Adjust the range based on your school IDs
    keywords = fake.words(nb=random.randint(2, 6))
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{ISBN}", "{title}", "{publisher}", "{number_of_pages}", "{summary}", "{available_copies}", "{image}", "{language_id}", "{school_id}", "{keywords}");\n'
    
######### BOOK_AUTHORS ##############
BOOK_AUTHOR_NUMBER = 506
TABLE_NAME = "book_author"
TABLE_COLUMNS = ["book_id", "author_id"]

for i in range(1, BOOK_AUTHOR_NUMBER + 1):
    book_id = (i - 1) % BOOK_NUMBER + 1
    author_id = (i - 1) % AUTHOR_NUMBER + 1

    values = [f"{book_id}", f"{author_id}"]
    content += f"INSERT INTO {TABLE_NAME} ({','.join(TABLE_COLUMNS)}) VALUES ({','.join(values)});\n"

########## BOOK CATEGORIES ###########
BOOK_CATEGORY_NUMBER = 500
TABLE_NAME = "book_category"
TABLE_COLUMNS = ["book_id", "category_id"]

for i in range(1, BOOK_AUTHOR_NUMBER + 1):
    book_id = (i - 1) % BOOK_NUMBER + 1
    category_id = (i - 1) % CATEGORY_NUMBER + 1 
    values = [f"{book_id}", f"{category_id}"]
    content += f"INSERT INTO {TABLE_NAME} ({','.join(TABLE_COLUMNS)}) VALUES ({','.join(values)});\n"

########## USERS ###################

USER_NUMBER = 100
TABLE_NAME = "user"
roles = ["teacher", "student"]

for i in range(USER_NUMBER-SCHOOL_NUMBER-1):
    username = fake.user_name()
    password = fake.password()
    first_name = fake.first_name()
    last_name = fake.last_name()
    date_of_birth = fake.date_of_birth(minimum_age=7, maximum_age=18) if "student" in roles else fake.date_of_birth(minimum_age=20)
    role = random.choice(roles)
    school_id = random.randint(1, SCHOOL_NUMBER)  # Replace with the actual range of school IDs
    weekly_borrowings = 0
    weekly_reservations = 0
    is_approved = "yes"

    
    if is_approved == None:
        TABLE_COLUMNS = ["username", "password", "first_name", "last_name", "date_of_birth", "role", "school_id", "weekly_borrowings", "weekly_reservations"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{username}", "{password}", "{first_name}", "{last_name}", "{date_of_birth}", "{role}", "{school_id}", "{weekly_borrowings}", "{weekly_reservations}");\n'
    else:
        TABLE_COLUMNS = ["username", "password", "first_name", "last_name", "date_of_birth", "role", "school_id", "weekly_borrowings", "weekly_reservations", "is_approved"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{username}", "{password}", "{first_name}", "{last_name}", "{date_of_birth}", "{role}", "{school_id}", "{weekly_borrowings}", "{weekly_reservations}", "{is_approved}");\n'

    
extra_roles = ["administrator", "operator"] 
for i in range (SCHOOL_NUMBER+1): # i from 0 to 5
    username = fake.user_name()
    password = fake.password()
    first_name = fake.first_name()
    last_name = fake.last_name()
    date_of_birth = fake.date_of_birth(minimum_age=20)
    if i <= 3:
        role = extra_roles[1]
        school_id = i+1
    else:
        role = extra_roles[0]
        school_id = 1  # Replace with the actual range of school IDs
    weekly_borrowings = 0
    weekly_reservations = 0
    is_approved = random.choice(["yes", "no", None])

    if is_approved == None:
        TABLE_COLUMNS = ["username", "password", "first_name", "last_name", "date_of_birth", "role", "school_id", "weekly_borrowings", "weekly_reservations"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{username}", "{password}", "{first_name}", "{last_name}", "{date_of_birth}", "{role}", "{school_id}", "{weekly_borrowings}", "{weekly_reservations}");\n'
    else:
        TABLE_COLUMNS = ["username", "password", "first_name", "last_name", "date_of_birth", "role", "school_id", "weekly_borrowings", "weekly_reservations", "is_approved"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{username}", "{password}", "{first_name}", "{last_name}", "{date_of_birth}", "{role}", "{school_id}", "{weekly_borrowings}", "{weekly_reservations}", "{is_approved}");\n'

 

########## BORROWINGS #############

BORROWING_NUMBER = 1000
TABLE_NAME = "borrowing"


for i in range(BORROWING_NUMBER):
    user_id = random.randint(1, USER_NUMBER)
    book_id = random.randint(1, BOOK_NUMBER)
    borrowing_date = fake.date_between(start_date = '-1y', end_date='today')
    
    if random.random() < 0.5:
        TABLE_COLUMNS = ["user_id", "book_id", "borrowing_date", "returning_date"]
        returning_date = borrowing_date + timedelta(days=random.randint(1, 14))
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{user_id}", "{book_id}", "{borrowing_date}", "{returning_date}");\n'


    else:
        TABLE_COLUMNS = ["user_id", "book_id", "borrowing_date"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ( "{user_id}", "{book_id}", "{borrowing_date}");\n'

    
########## RESERVATIONS ############

RESERVATION_NUMBER = 800
TABLE_NAME = "reservation"
TABLE_COLUMNS = ["user_id", "book_id", "reservation_date"]

for i in range(RESERVATION_NUMBER):
    reservation_id = i
    user_id = random.randint(1, USER_NUMBER)
    book_id = random.randint(1, BOOK_NUMBER)
    reservation_date = fake.date_between(start_date = datetime.now() - timedelta(days=5), end_date='today')
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{user_id}", "{book_id}", "{reservation_date}");\n'
    

            
######### REVIEWS ####################
REVIEW_NUMBER = 150
TABLE_NAME = "review"

for i in range(REVIEW_NUMBER):
    review_id = i
    user_id = random.randint(1, USER_NUMBER-1)  # Replace with the actual range of user IDs
    book_id = random.randint(1, BOOK_NUMBER-1)  # Replace with the actual range of book IDs
    rating = random.randint(1, 5)
    comments = fake.paragraph(nb_sentences=2)
    is_approved = random.choice(['yes', 'no', None])

    if is_approved == None:
        TABLE_COLUMNS = ["user_id", "book_id", "rating", "comments"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{user_id}", "{book_id}", "{rating}","{comments}");\n'

    else:
        TABLE_COLUMNS = ["user_id", "book_id", "rating", "comments", "is_approved"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{user_id}", "{book_id}", "{rating}","{comments}", "{is_approved}");\n'

########## NON-APPROVED USERS ###################

NOT_USER_NUMBER = 20
TABLE_NAME = "user"
roles = ["teacher", "student"]
for i in range(NOT_USER_NUMBER):
    username = fake.user_name()
    password = fake.password()
    first_name = fake.first_name()
    last_name = fake.last_name()
    date_of_birth = fake.date_of_birth(minimum_age=7, maximum_age=18) if "student" in roles else fake.date_of_birth(minimum_age=20)
    role = random.choice(roles)
    school_id = random.randint(1, SCHOOL_NUMBER)  # Replace with the actual range of school IDs
    weekly_borrowings = 0
    weekly_reservations = 0
    is_approved = random.choice(["no", None])

    if is_approved == None:
        TABLE_COLUMNS = ["username", "password", "first_name", "last_name", "date_of_birth", "role", "school_id", "weekly_borrowings", "weekly_reservations"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{username}", "{password}", "{first_name}", "{last_name}", "{date_of_birth}", "{role}", "{school_id}", "{weekly_borrowings}", "{weekly_reservations}");\n'
    else:
        TABLE_COLUMNS = ["username", "password", "first_name", "last_name", "date_of_birth", "role", "school_id", "weekly_borrowings", "weekly_reservations", "is_approved"]
        content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{username}", "{password}", "{first_name}", "{last_name}", "{date_of_birth}", "{role}", "{school_id}", "{weekly_borrowings}", "{weekly_reservations}", "{is_approved}");\n'


f = open("dummy_data.txt", "w", encoding="utf-8")
f.write(content)