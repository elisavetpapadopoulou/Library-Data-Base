from collections import OrderedDict
import faker 
from datetime import datetime, timedelta
import codecs
import random

locales = OrderedDict ([
    ('el-GR', 7),
    ('en-US', 2),
    ('el-CY', 4)
])
fake = faker.Faker(locales)

########## SCHOOLS ################

DUMMY_DATA_NUMBER = 4
TABLE_NAME = "school"
TABLE_COLUMNS = ["school_id", "school_name", "address", "city", "phone_number", "email", "school_director_name", "library_operator_name"]
content = ""

for i in range(DUMMY_DATA_NUMBER):
    school_id = i
    school_name = fake.text(max_nb_chars=20).replace('.','')
    address = fake.address() 
    city = fake.city()
    phone_number = fake.random_int(min=1000000000, max=9999999999)
    email = fake.email()
    school_director_name = fake.name()
    library_operator_name = fake.name()
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{school_id}", "{school_name}", "{address}", "{city}", "{phone_number}", "{email}", "{school_director_name}", "{library_operator_name}");\n'


########## BOOKS ##################

DUMMY_DATA_NUMBER = 150
TABLE_NAME = "book"
TABLE_COLUMNS = ["book_id", "ISBN", "publisher", "number_of_pages", "summary", "available_copies", "image", "language_id","school_id", "keywords"]
books = []
for i in range(DUMMY_DATA_NUMBER):
    book_id = i
    ISBN = random.randint(1000000000000, 9999999999999)
    title = fake.catch_phrase()
    publisher = fake.company()
    number_of_pages = random.randint(100, 1000)
    summary = fake.paragraph(nb_sentences=3)
    available_copies = random.randint(1, 100)
    image = fake.image_url()
    language_id = fake.word()
    school_id = random.randint(1, 4)  # Adjust the range based on your school IDs
    keywords = fake.words(nb=random.randint(2, 6))
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{book_id}", "{ISBN}", "{title}", "{publisher}", "{number_of_pages}", "{summary}", "{available_copies}", "{image}", "{language_id}", "{school_id}", "{keywords}");\n'
    
########## AUTHORS ################
DUMMY_DATA_NUMBER = 66
TABLE_NAME = "author"
TABLE_COLUMNS = ["author_id", "first_name", "last_name", "biography"]

for i in range(DUMMY_DATA_NUMBER):
    author_id = i
    first_name = fake.first_name()
    last_name = fake.last_name()
    biography = fake.paragraph(nb_sentences=3)
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{author_id}", "{first_name}", "{last_name}", "{biography}");\n'

########## CATEGORY ###############
TABLE_NAME = "category"
TABLE_COLUMNS = ["category_id", "name"]
predefined_categories = ['Fiction', 'Science Fiction', 'Mystery', 'Romance', 'Fantasy', 'Thriller', 'Biography', 'History', 'Self-help', 'Poetry']

for i in range(10):
    category_id = i
    name = random.choice(predefined_categories)
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{category_id}", "{name}");\n'
    
########## BORROWINGS #############

DUMMY_DATA_NUMBER = 70
TABLE_NAME = "borrowing"
TABLE_COLUMNS = ["borrowing_id", "user_id", "book_id", "borrowing_date", "returning_date"]

for i in range(DUMMY_DATA_NUMBER):
    borrowing_id = i
    user_id = random.randint(1, 100)
    book_id = random.randint(1, 150)
    borrowing_date = fake.date_between(start_date = '-1y', end_date='today')
    
    if random.random() < 0.5:
        returning_date = borrowing_date + timedelta(days=random.randint(1, 14))
    
    else:
        returning_date = None
        
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{borrowing_id}", "{user_id}, {book_id}, {borrowing_date}, {returning_date}");\n'
    
########## RESERVATIONS ############

DUMMY_DATA_NUMBER = 60
TABLE_NAME = "reservation"
TABLE_COLUMNS = ["resrvation_id", "user_id", "book_id", "reservation_date"]

for i in range(DUMMY_DATA_NUMBER):
    reservation_id = i
    user_id = random.randint(1, 100)
    book_id = random.randint(1, 150)
    today = datetime.now().date()
    five_days_ago = today - timedelta(days=5)
    reservation_date = fake.date_between_dates(date_start=five_days_ago, date_end=today)
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{reservation_id}", "{user_id}", "{book_id}", "{reservation_date}");\n'
    
########## USERS ###################

DUMMY_DATA_NUMBER = 100
TABLE_NAME = "user"
TABLE_COLUMNS = ["user_id", "username", "password", "first_name", "last_name", "date_of_birth", "role", "school_id", "weekly_borrowings", "weekly_reservations", "is_approved"]
roles = ["teacher", "student", "administrator", "operator", "operator", "operator", "operator"]
operators_count = 4  # Number of operators
administrator_count = 1  # Number of administrators
users = []

for i in range(DUMMY_DATA_NUMBER):
    user_id = i
    username = fake.user_name()
    password = fake.password()
    first_name = fake.first_name()
    last_name = fake.last_name()
    date_of_birth = fake.date_of_birth(minimum_age=7, maximum_age=18) if "student" in roles else fake.date_of_birth(minimum_age=20)
    role = random.choice(roles)
    school_id = random.randint(1, 4)  # Replace with the actual range of school IDs
    weekly_borrowings = random.randint(0, 2)
    weekly_reservations = random.randint(0, 2)
    is_approved = "yes"
    
    content += f'INSERT INTO {TABLE_NAME} ({",".join(TABLE_COLUMNS)}) VALUES ("{user_id}", "{username}", "{password}", "{first_name}", "{last_name}", "{date_of_birth}", "{role}", "{school_id}", "{weekly_borrowings}", "{weekly_reservations}", "{is_approved}");\n'
    
    
#   Adjust the count for operators and administrators
    if role == "operator":
        operators_count -= 1
        if operators_count == 0:
            roles.remove("operator")
    elif role == "administrator":
        administrator_count -= 1
        if administrator_count == 0:
            roles.remove("administrator")
            
######### REVIEWS ####################
DUMMY_DATA_NUMBER = 60
TABLE_NAME = "review"
TABLE_COLUMNS = ["review_id", "user_id", "book_id", "rating", "comments", "is_approved"]

for i in range(DUMMY_DATA_NUMBER):
    review_id = i
    user_id = random.randint(1, 100)  # Replace with the actual range of user IDs
    book_id = random.randint(1, 150)  # Replace with the actual range of book IDs
    rating = random.randint(1, 5)
    comments = fake.paragraph(nb_sentences=2)
    is_approved = random.choice(['yes', 'no', None])

    values = [str(review_id), str(user_id), str(book_id), str(rating), "'" + comments + "'", "'" + is_approved + "'"]
    content += f"INSERT INTO {TABLE_NAME} ({','.join(TABLE_COLUMNS)}) VALUES ({','.join(values)});\n"

######### BOOK_AUTHORS ##############
DUMMY_DATA_NUMBER = 170
TABLE_NAME = "book_author"
TABLE_COLUMNS = ["book_id", "author_id"]

for i in range(DUMMY_DATA_NUMBER):
    book_id = random.randint(1, 150)  # Replace with the actual range of book IDs
    author_id = random.randint(1, 66)  # Replace with the actual range of author IDs

    values = [f"{book_id}", f"{author_id}"]
    content += f"INSERT INTO {TABLE_NAME} ({','.join(TABLE_COLUMNS)}) VALUES ({','.join(values)});\n"

########## BOOK CATEGORIES ###########
DUMMY_DATA_NUMBER = 250
TABLE_NAME = "book_category"
TABLE_COLUMNS = ["book_id", "category_id"]

for i in range(DUMMY_DATA_NUMBER):
    book_id = random.randint(1, 150)  # Replace with the actual range of book IDs
    category_id = random.randint(1, 100)  # Replace with the actual range of category IDs

    values = [f"{book_id}", f"{category_id}"]
    content += f"INSERT INTO {TABLE_NAME} ({','.join(TABLE_COLUMNS)}) VALUES ({','.join(values)});\n"

f = open("dummy_data.txt", "w", encoding="utf-8")
f.write(content)