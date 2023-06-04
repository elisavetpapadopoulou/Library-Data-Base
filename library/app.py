from flask import Flask, render_template, request, flash, redirect, url_for, request, session
import mysql.connector
from forms import register_form, login_form, edit_password_form, school_form, book_form, review_form, edit_review_form, delayed_borrowers_form, delayed_borrowers_form, loan_statistics_form, category_statistics_form, year_selection_form, average_ratings_form

app = Flask(__name__)
# Set a secret key
app.secret_key = "hii"

# Establish a connection to the database
connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='library'
)


global is_student
is_student = False
global is_teacher
is_teacher = False
global is_administrator
is_administrator = False
global is_operator
is_operator = False


@app.route("/")
def home():
    return render_template("home.html")
    

@app.route("/login", methods=['GET', 'POST']) 
def login():
    form = login_form()
    global is_student, is_teacher, is_operator, is_administrator
    if form.validate_on_submit():
        cursor = connection.cursor()
        query = "SELECT user_id FROM user WHERE username = %s"
        cursor.execute(query, (form.username.data,))
        user_id = cursor.fetchone()
        cursor.close()
        session['user_id'] = user_id

        if (user_id is None):
            flash("Incorrect username! Please try again.", "error")
            return redirect(url_for("login"))

        cursor = connection.cursor()
        query = "SELECT password FROM user WHERE username = %s"
        cursor.execute(query, (form.username.data,))
        password = cursor.fetchone()[0]
        cursor.close()

        if (password != form.password.data):
            flash("Incorrect password! Please try again.", "error")
            return redirect(url_for("login"))


        cursor = connection.cursor()
        query = "SELECT school_id FROM user WHERE username = %s"
        cursor.execute(query, (form.username.data,))
        school_id = cursor.fetchone()
        cursor.close()
        session['school_id'] = school_id

        cursor = connection.cursor()
        query = """
        SELECT is_approved FROM user WHERE username = %s
        """
        cursor.execute(query, (form.username.data,))
        is_approved = cursor.fetchone()[0]
        cursor.close()

        cursor = connection.cursor()
        query = """
        SELECT role FROM user WHERE username = %s
        """
        cursor.execute(query, (form.username.data,))
        role = cursor.fetchone()[0]
        cursor.close()

        if role.lower() == 'student':
            is_student = True
            if is_approved == 'yes':
                return redirect(url_for("user"))
            else:
                return redirect(url_for("home"))
        elif role.lower() == 'teacher':
            is_teacher = True
            if is_approved == 'yes':
                return redirect(url_for("user"))
            else:
                return redirect(url_for("home"))
        elif role.lower() == 'administrator':
            is_administrator = True
            return redirect(url_for("administrator"))
        else: 
            is_operator = True
            if is_approved == 'yes':
                return redirect(url_for("operator"))
            else:
                return redirect(url_for("home"))
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    global is_student
    is_student = False
    global is_teacher
    is_teacher = False
    global is_administrator
    is_administrator = False
    global is_operator
    is_operator = False
    session.clear()
    flash("Logged out", "success")
    return redirect(url_for("home"))

@ app.route('/register', methods=['GET', 'POST']) 
def register():
    try:
        form = register_form()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            date_of_birth = form.date_of_birth.data
            role = form.role.data
            school = form.school.data
            cursor = connection.cursor()

            query_school = "SELECT school_id FROM school WHERE school_name = %s"
            cursor.execute(query_school, (school,))
            school_id = cursor.fetchone()[0]

            connection.commit() 
            query_user = """
            INSERT INTO user (username, password, first_name, last_name, date_of_birth, role, school_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_user, (username, password, first_name, last_name, date_of_birth, role, school_id,))
            connection.commit()
            cursor.close()
            return redirect(url_for("login"))

        return render_template('register.html', form=form)
    except Exception as e:
        flash(f"There isn't a school named {school}. Please try again!" , "error")
        return render_template('home.html')

@app.route("/user")
def user():
    if is_student:
        return render_template('user.html')
    if is_teacher:
        return render_template('user.html', user_role='teacher')

@app.route("/administrator")
def administrator():
    if is_administrator:
        return render_template('administrator.html')
    else:
        flash("You have to be an administrator", "error")
        return render_template('home.html')
    
@app.route("/operator")
def operator():
    if is_operator:
        return render_template('operator.html')
    else:
        flash("You have to be an operator", "error")
        return render_template('home.html')


@app.route('/personal_information') 
def personal_information():
    try:
        user_id = session.get('user_id')[0]
        school_id = session.get('school_id')[0]

        cursor = connection.cursor()
        query = """
        SELECT username, first_name, last_name, date_of_birth, role, school_id
        FROM user
        WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()

        cursor = connection.cursor()
        query = """
        SELECT school_name FROM school WHERE school_id = %s
        """
        cursor.execute(query, (school_id,))
        school_name = cursor.fetchone()[0]
        cursor.close()

        user_data = list(user_data)
        user_data[5] = school_name

        return render_template('personal_information.html', user=user_data)
    
    except Exception as e:
        flash("Something went wrong! Please try again.", "error")
        return render_template('home.html')


@app.route('/edit_password', methods=['GET', 'POST']) 
def edit_password():
    form = edit_password_form()
    message = None
    if form.validate_on_submit():
        username = form.username.data
        current_password = form.current_password.data
        new_password = form.new_password.data
        cursor = connection.cursor()
        query_user = "SELECT password FROM user WHERE username = %s"
        cursor.execute(query_user, (username,))
        password = cursor.fetchone()[0]
        cursor.close()
        if (password != current_password):
            message = 'You have a wrong password. Try again!'
        else:
            cursor = connection.cursor()
            query_user = "UPDATE user SET password = %s WHERE username = %s"
            cursor.execute(query_user, (new_password, username,))
            connection.commit()
            cursor.close()
            message = 'Password updated successfully!'
    return render_template('edit_password.html', form=form, message=message)

@app.route("/administrator/insert_school", methods=['GET', 'POST']) 
def insert_school():
    try:
        if is_administrator:
            form = school_form()
            if form.validate_on_submit():
                school_name = form.school_name.data
                address = form.address.data
                city = form.city.data
                phone_number = form.phone_number.data
                email = form.email.data
                school_director_name = form.school_director_name.data
                library_operator_name = form.library_operator_name.data
                
                cursor = connection.cursor()
                query_school = """
                INSERT INTO school (school_name, address, city, phone_number, email, school_director_name, library_operator_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_school, (school_name, address, city, phone_number, email, school_director_name, library_operator_name,))

                connection.commit()
                cursor.close()
                flash("School inserted successfully!", "success")
                return redirect(url_for('administrator'))
            return render_template('insert_school.html', form=form)
        else: 
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("Something went wrong! Please try again.", "error")
        return render_template('administrator.html')
    
@app.route("/administrator/operator_requests") 
def get_operator_requests():
    try:
        if is_administrator:
            cursor = connection.cursor(dictionary=True)
            query_requests = """
            SELECT username, first_name, last_name, is_approved FROM user WHERE is_approved IS NULL AND role IN ('operator')
            """
            cursor.execute(query_requests,)
            requests = cursor.fetchall()
            cursor.close()

            return render_template('operator_requests.html', users=requests)
        else: 
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("They weren't any operator requests! Please try again.", "error")
        return render_template('administrator.html')

@app.route('/administrator/approve-user/<string:username>', methods=['POST']) 
def approve_operator(username):
    if is_administrator:
        cursor = connection.cursor()
        query = f"UPDATE user SET is_approved = 'yes' WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        cursor.close()
        return redirect('/administrator/operator_requests')
    else: 
        flash("You have to be an administrator", "error")
        return render_template('home.html')
    
@app.route('/administrator/decline-user/<string:username>', methods=['POST']) 
def decline_operator(username):
    if is_administrator:
        cursor = connection.cursor()
        query = f"UPDATE user SET is_approved = 'no' WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        cursor.close()
        return redirect('/administrator/operator_requests')
    else: 
        flash("You have to be an administrator", "error")
        return render_template('home.html')


@app.route('/administrator/loan_statistics', methods=['GET', 'POST'])
def loan_statistics():
    try:
        if is_administrator:
            form = loan_statistics_form()

            if form.validate_on_submit():
                year = form.year.data
                month = form.month.data

                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT s.school_id, s.school_name, COUNT(*) AS total_loans
                    FROM borrowing b
                    INNER JOIN user u ON b.user_id = u.user_id
                    INNER JOIN school s ON u.school_id = s.school_id
                    WHERE YEAR(b.borrowing_date) = %s AND MONTH(b.borrowing_date) = %s
                    GROUP BY s.school_id, s.school_name
                """
                cursor.execute(query, (year, month))
                loan_statistics = cursor.fetchall()
                cursor.close()

                return render_template('loan_statistics.html', form=form, loan_statistics=loan_statistics)

            return render_template('loan_statistics.html', form=form)
        else:
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('administrator.html')
    
@app.route('/administrator/category_statistics', methods=['GET', 'POST']) 
def category_statistics():
    try:
        if is_administrator:
            form = category_statistics_form()
            if form.validate_on_submit():
                category_id = form.category.data

                cursor = connection.cursor()
                query_authors = """
                    SELECT DISTINCT a.author_id, a.first_name, a.last_name
                    FROM author a
                    JOIN book_author ba ON a.author_id = ba.author_id
                    JOIN book_category bc ON ba.book_id = bc.book_id
                    JOIN category c ON bc.category_id = c.category_id
                    WHERE c.name = %s;
                """
                cursor.execute(query_authors, (category_id,))
                authors = cursor.fetchall()
                cursor.close()
        
                cursor = connection.cursor()
                query_teachers = """
                    SELECT DISTINCT u.user_id, u.first_name, u.last_name
                    FROM user u
                    JOIN borrowing b ON u.user_id = b.user_id
                    JOIN book bo ON b.book_id = bo.book_id
                    JOIN book_category bc ON bo.book_id = bc.book_id
                    JOIN category c ON bc.category_id = c.category_id
                    WHERE c.name = %s
                    AND b.borrowing_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                    AND u.role = 'teacher';
                """
                cursor.execute(query_teachers, (category_id,))
                teachers = cursor.fetchall()
                cursor.close()


                return render_template('category_statistics.html', form=form, authors=authors, teachers=teachers)

            return render_template('category_statistics.html', form=form)
        else:
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('administrator.html')
    
@app.route('/administrator/young_teachers')
def young_teachers():
    try:
        if is_administrator:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT u.user_id, u.first_name, u.last_name, COUNT(*) AS num_borrowed_books
                FROM user u
                JOIN borrowing b ON u.user_id = b.user_id
                JOIN book bo ON b.book_id = bo.book_id
                WHERE u.role = 'Teacher'
                AND TIMESTAMPDIFF(YEAR, u.date_of_birth, CURDATE()) < 40
                GROUP BY u.user_id, u.first_name, u.last_name
                ORDER BY num_borrowed_books DESC
                LIMIT 10;
            """
            cursor.execute(query)
            young_teachers = cursor.fetchall()
            cursor.close()
            return render_template('young_teachers.html', young_teachers=young_teachers)
        else:
            flash("You have to be an administrator", "error")
            return render_template('home.html')
        
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('administrator.html')
    

@app.route('/administrator/unborrowed_authors') 
def unborrowed_authors():
    try:
        if is_administrator:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT DISTINCT a.author_id, a.first_name, a.last_name
                FROM author a
                JOIN book_author ba ON a.author_id = ba.author_id
                JOIN book b ON ba.book_id = b.book_id
                LEFT JOIN borrowing bor ON b.book_id = bor.book_id
                WHERE bor.borrowing_id IS NULL;
            """
            cursor.execute(query)
            unborrowed_authors = cursor.fetchall()
            cursor.close()

            return render_template('unborrowed_authors.html', unborrowed_authors=unborrowed_authors)
        else:
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('administrator.html')
    
@app.route('/administrator/operators_with_same_loans', methods=['GET', 'POST'])
def operators_with_same_loans():
    try:
        if is_administrator:
            form = year_selection_form()
            if form.validate_on_submit():
                year = form.year.data

                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT username, school_id FROM user WHERE role='operator'
                """
                cursor.execute(query)
                operators = cursor.fetchall()
                cursor.close()
                operator_loan_count = []

                for operator in operators:
                    cursor = connection.cursor()
                    query = """
                       SELECT COUNT(borrowing_id) FROM borrowing 
                       JOIN user ON user.user_id=borrowing.user_id 
                       WHERE user.school_id = %s AND YEAR(borrowing.borrowing_date) = %s
                    """
                    cursor.execute(query, (operator['school_id'], year))
                    loan_count = cursor.fetchone()[0]
                    cursor.close()
                    operator_loan_count.append(loan_count)
                
                if not operator_loan_count:
                    flash("No operators found with the same loan count.", "error")
                    return render_template('operators_with_same_loans.html', operators=[])

                duplicate_dict = {}
                for index, value in enumerate(operator_loan_count):
                    if value not in duplicate_dict:
                        duplicate_dict[value] = [index]
                    else:
                        duplicate_dict[value].append(index)

                duplicate_dict = {key: value for key, value in duplicate_dict.items() if len(value) > 1}
                for key, values in duplicate_dict.items():
                    if key>20:
                        matched_operators = [(operators[v]['username'], key) for v in values] 

                return render_template('operators_with_same_loans.html', operators=matched_operators)
            return render_template('year_selection.html', form=form)
        else:
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('administrator.html')


@app.route('/administrator/common_category_pairs')
def find_common_category_pairs():
    try:
        if is_administrator:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT bc1.category_id AS category1_id, c1.name AS category1_name,
                    bc2.category_id AS category2_id, c2.name AS category2_name,
                    COUNT(*) AS borrowings_count
                FROM borrowing b
                JOIN book bo ON b.book_id = bo.book_id
                JOIN book_category bc1 ON bo.book_id = bc1.book_id
                JOIN book_category bc2 ON bo.book_id = bc2.book_id
                JOIN category c1 ON bc1.category_id = c1.category_id
                JOIN category c2 ON bc2.category_id = c2.category_id
                WHERE bc1.category_id < bc2.category_id
                GROUP BY bc1.category_id, c1.name, bc2.category_id, c2.name
                ORDER BY borrowings_count DESC
                LIMIT 3;

            """
            cursor.execute(query)
            common_pairs = cursor.fetchall()
            cursor.close()

            return render_template('common_category_pairs.html', common_pairs=common_pairs)
        else:
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('administrator.html')



@app.route('/administrator/authors_with_fewer_books')
def authors_with_fewer_books():
    try:
        if is_administrator:
            cursor = connection.cursor(dictionary=True)

            query_max_books = """
                SELECT author_id, COUNT(*) AS book_count
                FROM book_author
                GROUP BY author_id
                ORDER BY book_count DESC
                LIMIT 1
            """
            cursor.execute(query_max_books)
            max_books_author = cursor.fetchone()

            if max_books_author:
                max_book_count = max_books_author['book_count']
                author_id = max_books_author['author_id']

                query_fewer_books = """
                    SELECT ba.author_id, COUNT(*) AS book_count, a.first_name, a.last_name
                    FROM book_author ba
                    INNER JOIN author a ON ba.author_id = a.author_id
                    WHERE ba.author_id != %s
                    GROUP BY ba.author_id, a.first_name, a.last_name
                    HAVING COUNT(*) <= %s - 5
                    ORDER BY book_count DESC
                """

                cursor.execute(query_fewer_books, (author_id, max_book_count))

                authors_with_fewer_books = cursor.fetchall()
            else:
                authors_with_fewer_books = []

            cursor.close()

            return render_template('authors_with_fewer_books.html', authors=authors_with_fewer_books)
        else:
            flash("You have to be an administrator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('administrator.html')

@app.route('/operator/add_book', methods=['GET', 'POST'])
def add_book():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            form = book_form()
            if form.validate_on_submit():
                ISBN = form.ISBN.data
                title = form.title.data
                publisher = form.publisher.data
                number_of_pages = form.number_of_pages.data
                summary = form.summary.data
                available_copies = form.available_copies.data
                image = form.image.data
                keywords = form.keywords.data
                category = form.category.data
                language = form.language.data
                author_first_name = form.author_first_name.data
                author_last_name = form.author_last_name.data

                cursor = connection.cursor()
                query_category = "SELECT category_id FROM category WHERE name = %s"
                cursor.execute(query_category, (category,))
                category_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_language = "SELECT language_id FROM language WHERE name = %s"
                cursor.execute(query_language, (language,))
                language_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_author = "SELECT author_id FROM author WHERE first_name = %s AND last_name = %s"
                cursor.execute(query_author, (author_first_name, author_last_name))
                author_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_book = """
                INSERT INTO book (ISBN, title, publisher, number_of_pages, summary, available_copies, image, language_id, school_id, keywords)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_book, (ISBN, title, publisher, number_of_pages, summary, available_copies, image, language_id, school_id, keywords))
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                query = "SELECT book_id FROM book WHERE ISBN = %s AND school_id = %s"
                cursor.execute(query, (ISBN, school_id))
                book_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_book_author = """
                INSERT INTO book_author (book_id, author_id)
                VALUES (%s, %s)
                """
                cursor.execute(query_book_author, (book_id, author_id))
                connection.commit()
                cursor.close()

                cursor = connection.cursor()
                query_book_category = """
                INSERT INTO book_category (book_id, category_id)
                VALUES (%s, %s,)
                """
                cursor.execute(query_book_category, (book_id, category_id))
                connection.commit()
                cursor.close()

            return render_template('add_book.html', form=form)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')
    
@app.route('/operator/edit_book', methods=['GET', 'POST'])
def edit_book():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            form = book_form()
            if form.validate_on_submit():
                ISBN = form.ISBN.data
                title = form.title.data
                publisher = form.publisher.data
                number_of_pages = form.number_of_pages.data
                summary = form.summary.data
                available_copies = form.available_copies.data
                image = form.image.data
                keywords = form.keywords.data
                category = form.category.data
                language = form.language.data
                author_first_name = form.author_first_name.data
                author_last_name = form.author_last_name.data

                cursor = connection.cursor()
                query_category = "SELECT category_id FROM category WHERE name = %s"
                cursor.execute(query_category, (category,))
                category_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_language = "SELECT language_id FROM language WHERE name = %s"
                cursor.execute(query_language, (language,))
                language_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_author = "SELECT author_id FROM author WHERE first_name = %s AND last_name = %s"
                cursor.execute(query_author, (author_first_name, author_last_name,))
                author_id = cursor.fetchone()[0]
                cursor.close()
                
                cursor = connection.cursor()
                query_book = """
                UPDATE book
                SET title = %s, publisher = %s, number_of_pages = %s, summary = %s,
                    available_copies = %s, image = %s, language_id = %s, keywords = %s
                WHERE ISBN = %s AND school_id = %s
                """
                cursor.execute(query_book, (title, publisher, number_of_pages, summary, available_copies, image, language_id, keywords, ISBN, school_id,))
                connection.commit()
                cursor.close()


                cursor = connection.cursor()
                query = "SELECT book_id FROM book WHERE ISBN = %s AND school_id = %s"
                cursor.execute(query, (ISBN, school_id))
                book_id = cursor.fetchone()[0]
                cursor.close()


                for author in author_id:
                    cursor = connection.cursor()
                    query_book_author = "UPDATE book_author SET author_id = %s WHERE book_id = %s"
                    cursor.execute(query_book_author, (author, book_id,))
                    connection.commit()
                    cursor.close()
                
                cursor = connection.cursor()
                query_book_category = "UPDATE book_category SET category_id = %s WHERE book_id = %s"
                cursor.execute(query_book_category, (category_id, book_id,))
                connection.commit()
                cursor.close()

            return render_template('edit_book.html', form=form)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')
    
@app.route('/operator/loan_without_reservation', methods=['GET', 'POST']) 
def loan_without_reservation():
    try:
        if is_operator:
            if request.method == 'POST':
                school_id = session.get('school_id')[0]
                username = request.form.get('username')
                title = request.form.get('title')

                cursor = connection.cursor()
                query_user = "SELECT user_id FROM user WHERE username = %s"
                cursor.execute(query_user, (username,))
                user_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_book = "SELECT book_id FROM book WHERE title = %s"
                cursor.execute(query_book, (title,))
                book_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query_role = "SELECT role FROM user WHERE user_id = %s"
                cursor.execute(query_role, (user_id,))
                role = cursor.fetchone()[0]
                cursor.close()

                if role.lower() == 'operator' or role.lower() == 'administrator':
                    error = "User can not reserve or borrow a book."
                    return render_template('loan_without_reservation.html', error=error)
                
                cursor = connection.cursor()
                query_user = "SELECT weekly_borrowings FROM user WHERE user_id = %s"
                cursor.execute(query_user, (user_id,))
                loan_count = cursor.fetchone()[0]
                cursor.fetchall()
                cursor.close()

                if (role.lower() == 'student' and loan_count >= 2) or (role.lower() == 'teacher' and loan_count >= 1):
                    error = "User has reached the maximum number of loans per week."
                    return render_template('loan_without_reservation.html', error=error)

                cursor = connection.cursor()
                query_reservations = "SELECT weekly_reservations FROM user WHERE user_id = %s"
                cursor.execute(query_reservations, (user_id,))
                reservation_count = cursor.fetchone()[0]
                cursor.close()
                
                cursor = connection.cursor()
                query_available_copies = "SELECT available_copies FROM book WHERE title = %s AND school_id = %s"
                cursor.execute(query_available_copies, (title, school_id))
                available_copies = cursor.fetchone()[0]
                cursor.fetchall()
                cursor.close()

                if available_copies == 0 and ((role.lower() == 'student' and reservation_count >= 2) or (role.lower() == 'teacher' and reservation_count >= 1)):
                    error = "User has reached the maximum number of reservations per week."
                    return render_template('loan_without_reservation.html', error=error)
                
                if available_copies == 0 and ((role.lower() == 'student' and reservation_count < 2) or (role.lower() == 'teacher' and reservation_count < 1)):
                    cursor = connection.cursor()
                    query_create_reservation = "INSERT INTO reservation (user_id, book_id, reservation_date) VALUES (%s, (SELECT book_id FROM book WHERE title = %s), CURDATE())"
                    cursor.execute(query_create_reservation, (user_id, title))
                    connection.commit()
                    cursor.close()
                    
                    success = "No copies of the book are available. Your request has been put on hold."
                    return render_template('loan_without_reservation.html', success=success)
                
                if (role.lower() == 'student' and loan_count < 2) or (role.lower() == 'teacher' and loan_count < 1):
                    cursor = connection.cursor()
                    query_create_loan = "INSERT INTO borrowing (user_id, book_id, borrowing_date) VALUES (%s, %s, CURDATE())"
                    cursor.execute(query_create_loan, (user_id, book_id))
                    connection.commit()
                    cursor.close()

                    success = "Loan created successfully."
                    return render_template('loan_without_reservation.html', success=success)
            
            return render_template('loan_without_reservation.html')
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

    
@app.route("/operator/reviews") 
def get_reviews():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            cursor = connection.cursor(dictionary=True)
            query_requests = """
            SELECT r.user_id, r.book_id, r.rating, r.comments, r.is_approved
            FROM review r
            INNER JOIN user u ON r.user_id = u.user_id
            WHERE u.school_id = %s AND r.is_approved IS NULL
            """
            cursor.execute(query_requests, (school_id, ))
            reviews = cursor.fetchall()
            cursor.close()

            for review in reviews:
                cursor = connection.cursor()
                query = "SELECT username FROM user WHERE user_id = %s"
                cursor.execute(query, (review['user_id'],))
                username = cursor.fetchone()
                cursor.close()
                review['user_id'] = username[0]

                cursor = connection.cursor()
                query = "SELECT title FROM book WHERE book_id = %s"
                cursor.execute(query, (review['book_id'],))
                title = cursor.fetchone()
                cursor.close()
                review['book_id'] = title[0]
            return render_template('reviews.html', reviews=reviews)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/approve-review/<string:username>', methods=['POST']) 
def approve_review(username):
    if is_operator:
        cursor = connection.cursor()
        query = "SELECT user_id FROM user WHERE username= %s"
        cursor.execute(query, (username,))
        user_id = cursor.fetchone()[0]
        cursor.close()

        cursor = connection.cursor()
        query = "UPDATE review SET is_approved = 'yes' WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
        cursor.close()
        return redirect('/operator/reviews')
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')
    
@app.route('/operator/decline-review/<string:username>', methods=['POST'])
def decline_review(username):
    if is_operator:
        cursor = connection.cursor()
        query = "SELECT user_id FROM user WHERE username= %s"
        cursor.execute(query, (username,))
        user_id = cursor.fetchone()[0]
        cursor.close()

        cursor = connection.cursor()
        query = "UPDATE review SET is_approved = 'no' WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
        cursor.close()
        return redirect('/operator/reviews')
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')

@app.route("/operator/user_requests") 
def get_user_requests():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            cursor = connection.cursor(dictionary=True)
            query_requests = """
            SELECT username, first_name, last_name, is_approved FROM user WHERE is_approved is NULL and role IN ('student', 'teacher') AND school_id = %s
            """
            cursor.execute(query_requests, (school_id,))
            users = cursor.fetchall()
            cursor.close()
            return render_template('user_requests.html', users=users)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')
    
@app.route('/operator/approve-user/<string:username>', methods=['POST']) 
def approve_user(username):
    if is_operator:
        cursor = connection.cursor()
        query = "UPDATE user SET is_approved = 'yes' WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        cursor.close()
        return redirect('/operator/user_requests')
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')
    
@app.route('/operator/decline-user/<string:username>', methods=['POST']) 
def decline_user(username):
    if is_operator:
        cursor = connection.cursor()
        query = "UPDATE user SET is_approved = 'no' WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        cursor.close()
        return redirect('/operator/user_requests')
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')
    
@app.route('/operator/users') 
def users():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            cursor = connection.cursor(dictionary=True)
            query = "SELECT username, first_name, last_name, is_approved FROM user WHERE role IN ('student', 'teacher')  AND school_id = %s"
            cursor.execute(query, (school_id,))
            users = cursor.fetchall()
            cursor.close()
            return render_template('users.html', users=users)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/disable-user/<string:username>', methods=['POST']) 
def disable_user(username):
    if is_operator:
        cursor = connection.cursor()
        query = f"UPDATE user SET is_approved = 'no' WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        cursor.close()

        return redirect('/operator/users')
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')

@app.route('/operator/delete-user/<string:username>', methods=['POST']) 
def delete_user(username):
    if is_operator:
        cursor = connection.cursor()
        query = f"DELETE FROM user WHERE username = %s"
        cursor.execute(query, (username,))
        connection.commit()
        cursor.close()

        return redirect('/operator/users')
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')

@app.route('/operator/reservations') 
def view_reservations():

        if is_operator:
            school_id = session.get('school_id')[0]
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT r.reservation_id, r.user_id, r.book_id, r.reservation_date 
            FROM reservation r 
            INNER JOIN book b ON r.book_id = b.book_id 
            WHERE b.school_id = %s
            """
            cursor.execute(query, (school_id,))
            reservations = cursor.fetchall()
            cursor.close()
            for reservation in reservations:
                cursor = connection.cursor()
                query = "SELECT username FROM user WHERE user_id = %s"
                cursor.execute(query, (reservation['user_id'],))
                username = cursor.fetchone()
                cursor.close()
                reservation['user_id'] = username[0]

                cursor = connection.cursor()
                query = "SELECT title FROM book WHERE book_id = %s"
                cursor.execute(query, (reservation['book_id'],))
                title = cursor.fetchone()
                cursor.close()
                reservation['book_id'] = title[0]

            return render_template('reservations.html', reservations=reservations)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')


@app.route('/operator/reservations_by_user', methods=['GET', 'POST'])
def reservations_by_user():
    try:
        if is_operator:
            if request.method == 'POST':
                username = request.form['username']
                cursor = connection.cursor()
                query = "SELECT user_id FROM user WHERE username = %s"
                cursor.execute(query, (username,))
                user_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM reservation WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                reservations = cursor.fetchall()
                cursor.close()

                for reservation in reservations:
                    cursor = connection.cursor()
                    query = "SELECT ISBN FROM book WHERE book_id = %s"
                    cursor.execute(query, (reservation['book_id'],))
                    ISBN = cursor.fetchone()
                    cursor.close()
                    reservation['book_id'] = ISBN[0]
                return render_template('reservations_by_user.html', username=username, reservations=reservations)
            return render_template('reservations_by_user.html', username=None, reservations=None)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/loans') 
def view_loans():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT b.*
            FROM borrowing AS b
            INNER JOIN book AS bk ON b.book_id = bk.book_id
            WHERE bk.school_id = %s
            """
            cursor.execute(query, (school_id,))
            loans = cursor.fetchall()
            cursor.close()

            for loan in loans: 
                
                cursor = connection.cursor()
                query = "SELECT username FROM user WHERE user_id = %s"
                cursor.execute(query, (loan['user_id'],))
                username = cursor.fetchone()
                cursor.close()
                loan['user_id'] = username[0]

                cursor = connection.cursor()
                query = "SELECT title FROM book WHERE book_id = %s"
                cursor.execute(query, (loan['book_id'],))
                title = cursor.fetchone()
                cursor.close()
                loan['book_id'] = title[0]
            
            return render_template('loans.html', loans=loans)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/loans_by_user', methods=['GET', 'POST']) 
def loans_by_user():
    try:
        if is_operator:
            if request.method == 'POST':
                username = request.form['username']
                cursor = connection.cursor()
                query = "SELECT user_id FROM user WHERE username = %s"
                cursor.execute(query, (username,))
                user_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM borrowing WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                loans = cursor.fetchall()
                cursor.close()

                for loan in loans:
                    cursor = connection.cursor()
                    query = "SELECT ISBN FROM book WHERE book_id = %s"
                    cursor.execute(query, (loan['book_id'],))
                    ISBN = cursor.fetchone()
                    cursor.close()
                    loan['book_id'] = ISBN[0]
                return render_template('loans_by_user.html', username=username, loans=loans)
            return render_template('loans_by_user.html', username=None, reservations=None)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/delayed_returns')
def delayed_returns():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT bk.title, u.username, b.borrowing_date, b.due_date, b.returning_date
                FROM borrowing b
                INNER JOIN book bk ON b.book_id = bk.book_id
                INNER JOIN user u ON b.user_id = u.user_id
                WHERE b.due_date < CURDATE()
                AND bk.school_id = %s
            """

            cursor.execute(query, (school_id,))
            delayed_returns = cursor.fetchall()
            cursor.close()

            return render_template('delayed_returns.html', delayed_returns=delayed_returns)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

  
@app.route('/operator/loan_with_reservation') 
def loan_with_reservation():
    try:
        if is_operator:
            school_id = session.get('school_id')[0]
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT r.reservation_id, r.user_id, r.book_id, r.reservation_date 
            FROM reservation r 
            INNER JOIN book b ON r.book_id = b.book_id 
            WHERE b.school_id = %s
            """
            cursor.execute(query, (school_id,))
            reservations = cursor.fetchall()
            cursor.close()

            for reservation in reservations:
                cursor = connection.cursor()
                query = "SELECT username FROM user WHERE user_id = %s"
                cursor.execute(query, (reservation['user_id'],))
                username = cursor.fetchone()
                cursor.close()
                reservation['user_id'] = username[0]

                cursor = connection.cursor()
                query = "SELECT title FROM book WHERE book_id = %s"
                cursor.execute(query, (reservation['book_id'],))
                title = cursor.fetchone()
                cursor.close()
                reservation['book_id'] = title[0]

            return render_template('loan_with_reservation.html', reservations=reservations)
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/record-loan/<int:reservation_id>', methods=['POST']) 
def record_loan(reservation_id):
    if is_operator:
        school_id = session.get('school_id')[0]
        cursor = connection.cursor()
        query_user = "SELECT user_id FROM reservation WHERE reservation_id = %s"
        cursor.execute(query_user, (reservation_id,))
        user_id = cursor.fetchone()[0]
        cursor.close()

        cursor = connection.cursor()
        query_book = "SELECT book_id FROM reservation WHERE reservation_id = %s"
        cursor.execute(query_book, (reservation_id,))
        book_id = cursor.fetchone()[0]
        cursor.close()

        cursor = connection.cursor()
        query_available_copies = "SELECT available_copies FROM book WHERE book_id = %s AND school_id = %s"
        cursor.execute(query_available_copies, (book_id, school_id))
        available_copies = cursor.fetchone()[0]
        cursor.close()

        cursor = connection.cursor()
        query_user = "SELECT weekly_borrowings FROM user WHERE user_id = %s"
        cursor.execute(query_user, (user_id,))
        loan_count = cursor.fetchone()[0]
        cursor.close()

        cursor = connection.cursor()
        query_role = "SELECT role FROM user WHERE user_id = %s"
        cursor.execute(query_role, (user_id,))
        role = cursor.fetchone()[0]
        cursor.close()

        if role.lower() == 'operator' or role.lower() == 'administrator':
            error = "User can not borrow a book."
            return redirect(url_for('loan_with_reservation', reservation_id=reservation_id, error=error))

        if (role.lower() == 'student' and loan_count >= 2) or (role.lower() == 'teacher' and loan_count >= 1):
            error = "User has reached the maximum number of loans per week."
            return redirect(url_for('loan_with_reservation', reservation_id=reservation_id, error=error))

        if available_copies == 0:
            error = "No copies of the book are available."
            return redirect(url_for('loan_with_reservation', reservation_id=reservation_id, error=error))
        
        if available_copies > 0 and ((role.lower() == 'student' and loan_count < 2) or (role.lower() == 'teacher' and loan_count < 1)):
            cursor = connection.cursor()
            query_create_loan = "INSERT INTO borrowing (user_id, book_id, borrowing_date, due_date) VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY))"
            cursor.execute(query_create_loan, (user_id, book_id,))
            connection.commit()
            cursor.close()

            cursor = connection.cursor()
            query_delete_reservation = "DELETE FROM reservation WHERE reservation_id = %s"
            cursor.execute(query_delete_reservation, (reservation_id,))
            connection.commit()
            cursor.close()

            success = "Loan created successfully."
            return redirect(url_for('loan_with_reservation', reservation_id=reservation_id, success=success))
        error = "Something happened." 
        return redirect(url_for('loan_with_reservation', reservation_id=reservation_id, error=error))
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')
    
@app.route('/operator/return_book') 
def return_book():
    try:
        if is_operator:
            return render_template('return_book.html')
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/record-return', methods=['POST']) 
def record_return():
    if is_operator:
        borrowing_id = request.form.get('borrowing_id')
        cursor = connection.cursor()
        query_update_returning_date = "UPDATE borrowing SET returning_date = CURDATE() WHERE borrowing_id = %s"
        cursor.execute(query_update_returning_date, (borrowing_id,))
        connection.commit()
        cursor.close()

        success = "Return recorded successfully."
        return render_template('return_book.html', success=success)
    else: 
        flash("You have to be an operator", "error")
        return render_template('home.html')

@app.route('/operator/all_books', methods=['GET', 'POST']) 
def all_books():
    try:
        if is_operator:
            if request.method == 'POST':
                search_criteria = request.form['search_criteria']
                keyword = request.form['keyword']
                school_id = session.get('school_id')[0]
                
                if (search_criteria == 'title'):
                    cursor = connection.cursor(dictionary=True)
                    query_title = "SELECT * FROM book WHERE title = %s AND school_id = %s"
                    cursor.execute(query_title, (keyword, school_id,))
                    books = cursor.fetchall()
                    cursor.close()
                    
                elif (search_criteria == 'category'):
                    cursor = connection.cursor()
                    query_category = "SELECT category_id FROM category WHERE name = %s"
                    cursor.execute(query_category, (keyword,))
                    category_id = cursor.fetchone()[0]
                    cursor.fetchall()
                    cursor.close()
                    
                    cursor = connection.cursor(dictionary=True)
                    query = "SELECT * FROM book JOIN book_category ON book.book_id = book_category.book_id WHERE book_category.category_id = %s AND book.school_id = %s"
                    cursor.execute(query, (category_id, school_id, ))
                    books = cursor.fetchall()
                    cursor.close()
                    

                elif (search_criteria == 'author'):
                    name_parts = keyword.split()
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                    cursor = connection.cursor()
                    query_author = "SELECT author_id FROM author WHERE first_name = %s AND last_name = %s"
                    cursor.execute(query_author, (first_name, last_name,))
                    author_id = cursor.fetchone()[0]
                    cursor.fetchall()
                    cursor.close()

                    cursor = connection.cursor(dictionary=True)
                    query = "SELECT * FROM book JOIN book_author ON book.book_id = book_author.book_id WHERE book_author.author_id = %s AND book.school_id = %s"
                    cursor.execute(query, (author_id, school_id, ))
                    books = cursor.fetchall()
                    cursor.close()

                elif (search_criteria == 'available_copies'):
                    cursor = connection.cursor(dictionary=True)
                    query = "SELECT * FROM book WHERE available_copies = %s AND school_id = %s"
                    cursor.execute(query, (keyword, school_id,))
                    books = cursor.fetchall()
                    cursor.close()
                else:   
                    flash("We don't have a book meeting your criteria. Please try again!")
                    return render_template('all_books.html', books=None)
                
                if books:
                    for book in books:
                        cursor = connection.cursor()
                        query = "SELECT author_id, first_name, last_name FROM author WHERE author_id IN (SELECT author_id FROM book_author WHERE book_id = %s)"
                        cursor.execute(query, (book['book_id'],))
                        authors = cursor.fetchall()
                        cursor.close()
                        book['author_id'] = ', '.join([author[1] + ' ' + author[2] for author in authors])
            
                return render_template('all_books.html', books=books)
            
            return render_template('all_books.html')
        else: 
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/delayed_borrowers', methods=['GET', 'POST']) 
def delayed_borrowers():
    try:
        if is_operator:
            form = delayed_borrowers_form()

            if form.validate_on_submit():
                first_name = form.first_name.data
                last_name = form.last_name.data
                delay_days = form.delay_days.data

                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT u.first_name, u.last_name, DATEDIFF(CURDATE(), b.due_date) AS delay_days
                    FROM borrowing b
                    INNER JOIN user u ON b.user_id = u.user_id
                    WHERE u.first_name = %s
                    AND u.last_name = %s
                    AND b.returning_date IS NULL
                    AND DATEDIFF(CURDATE(), b.due_date) = %s
                """
                cursor.execute(query, (first_name, last_name, delay_days))
                delayed_borrowers = cursor.fetchall()
                cursor.close()

                return render_template('delayed_borrowers.html', form=form, delayed_borrowers=delayed_borrowers)

            return render_template('delayed_borrowers.html', form=form)
        else:
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/operator/average_ratings', methods=['GET', 'POST']) 
def average_ratings():
    try:
        if is_operator:
            form = average_ratings_form()

            if form.validate_on_submit():
                username = form.username.data
                category = form.category.data

                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT u.username, c.name AS category, AVG(r.rating) AS average_rating
                    FROM user u
                    INNER JOIN review r ON u.user_id = r.user_id
                    INNER JOIN book_category bc ON r.book_id = bc.book_id
                    INNER JOIN category c ON bc.category_id = c.category_id
                    WHERE u.username = %s
                    AND c.name = %s
                    GROUP BY u.username, c.name
                """
                cursor.execute(query, (username, category))
                average_ratings = cursor.fetchall()
                cursor.close()

                return render_template('average_ratings.html', form=form, average_ratings=average_ratings)

            return render_template('average_ratings.html', form=form)
        else:
            flash("You have to be an operator", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')


@app.route('/user/edit_personal_information', methods=['GET', 'POST']) 
def edit_personal_information():
    try:
        if is_teacher:
            user_id = session.get('user_id')[0]

            cursor = connection.cursor()
            query = """
            SELECT username, first_name, last_name, date_of_birth, role, school_id
            FROM user
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()

            school_id = user_data[5]
            cursor = connection.cursor()
            query = """
            SELECT school_name FROM school WHERE school_id = %s
            """
            cursor.execute(query, (school_id,))
            school_name = cursor.fetchone()[0]
            cursor.close()

            user_data = list(user_data)
            user_data[5] = school_name

            if request.method == 'POST':
                username = request.form['username']
                first_name = request.form['first_name']
                last_name = request.form['last_name']
                date_of_birth = request.form['date_of_birth']
                school = request.form['school']

                cursor = connection.cursor()
                query = """
                SELECT school_id FROM school WHERE school_name = %s
                """
                cursor.execute(query, (school,))
                school_id = cursor.fetchone()[0]
                cursor.close()

                cursor = connection.cursor()
                query = """
                UPDATE user
                SET username = %s, first_name = %s, last_name = %s, date_of_birth = %s, school_id = %s
                WHERE user_id = %s
                """
                cursor.execute(query, (username, first_name, last_name, date_of_birth, school_id, user_id))
                connection.commit()
                cursor.close()

                flash('Personal information updated', 'success')
                return redirect(url_for('user'))

            return render_template('edit_personal_information.html', user=user_data)
        else:
            flash("You have to be a teacher", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')

@app.route('/user/write_review', methods=['GET', 'POST']) 
def write_review():
    try:
        if is_teacher or is_student:
            form = review_form()
            if form.validate_on_submit():
                user_id = session.get('user_id')[0]
                ISBN = form.ISBN.data
                rating = form.rating.data
                comments = form.comments.data
                cursor = connection.cursor()
                query = "SELECT book_id FROM book WHERE ISBN = %s"
                cursor.execute(query, (ISBN,))
                book_id = cursor.fetchone()[0]
                cursor.fetchall()
                cursor.close()

                cursor = connection.cursor()
                query = "INSERT INTO review (user_id, book_id, rating, comments) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (user_id, book_id, rating, comments,))
                connection.commit()
                cursor.close()

                flash("Review submitted successfully.", "success")
                return redirect(url_for('write_review'))

            return render_template('write_review.html', form=form)
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('operator.html')

@app.route('/user/book_search', methods=['GET', 'POST']) 
def book_search():
    try:
        if is_teacher or is_student:
            if request.method == 'POST':
                search_criteria = request.form['search_criteria']
                keyword = request.form['keyword']

                school_id = session.get('school_id')[0]
                
                if (search_criteria == 'title'):
                    cursor = connection.cursor(dictionary=True)
                    query_title = "SELECT * FROM book WHERE title = %s AND school_id = %s"
                    cursor.execute(query_title, (keyword, school_id,))
                    books = cursor.fetchall()
                    cursor.close()
                    
                elif (search_criteria == 'category'):
                    cursor = connection.cursor()
                    query_category = "SELECT category_id FROM category WHERE name = %s"
                    cursor.execute(query_category, (keyword,))
                    category_id = cursor.fetchone()[0]
                    cursor.fetchall()
                    cursor.close()
                    
                    cursor = connection.cursor(dictionary=True)
                    query = "SELECT * FROM book JOIN book_category ON book.book_id = book_category.book_id WHERE book_category.category_id = %s AND book.school_id = %s"
                    cursor.execute(query, (category_id, school_id, ))
                    books = cursor.fetchall()
                    cursor.close()

                elif (search_criteria == 'author'):
                    name_parts = keyword.split()
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                    cursor = connection.cursor()
                    query_author = "SELECT author_id FROM author WHERE first_name = %s AND last_name = %s"
                    cursor.execute(query_author, (first_name, last_name,))
                    author_id = cursor.fetchone()[0]
                    cursor.fetchall()
                    cursor.close()

                    cursor = connection.cursor(dictionary=True)
                    query = "SELECT * FROM book JOIN book_author ON book.book_id = book_author.book_id WHERE book_author.author_id = %s AND book.school_id = %s"
                    cursor.execute(query, (author_id, school_id, ))
                    books = cursor.fetchall()
                    cursor.close()
                    
                else:   
                    flash("We don't have a book meeting your criteria. Please try again!")
                    return render_template('book_search.html', books=None)
                
                if books:
                    for book in books:
                        book['keywords'] = ', '.join([keyword for keyword in eval(book['keywords']) ])

                        cursor = connection.cursor()
                        query = "SELECT name FROM category WHERE category_id IN (SELECT category_id FROM book_category WHERE book_id = %s)"
                        cursor.execute(query, (book['book_id'],))
                        categories = cursor.fetchall()
                        cursor.close()

                        book['category_id'] = ', '.join([category[0] for category in categories])
                        
                        cursor = connection.cursor()
                        query = "SELECT name FROM language WHERE language_id = %s"
                        cursor.execute(query, (book['language_id'],))
                        language = cursor.fetchone()
                        cursor.close()
                        book['language_id'] = language[0]

                        cursor = connection.cursor()
                        query = "SELECT author_id, first_name, last_name FROM author WHERE author_id IN (SELECT author_id FROM book_author WHERE book_id = %s)"
                        cursor.execute(query, (book['book_id'],))
                        authors = cursor.fetchall()
                        cursor.close()
                        book['author_id'] = ', '.join([author[1] + ' ' + author[2] for author in authors])
                else:   
                    flash("We don't have a book meeting your criteria. Please try again!")
                    return render_template('book_search.html', books=None)
                return render_template('book_search.html', books=books)


            return render_template('book_search.html')
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')
    
@app.route('/user/create_reservation/<int:ISBN>', methods=['POST']) 
def create_reservation(ISBN):
    try:
        if is_teacher or is_student:
            user_id = session.get('user_id')[0]
            school_id = session.get('school_id')[0]
            cursor = connection.cursor()
            query = "SELECT book_id FROM book WHERE ISBN = %s AND school_id = %s"
            cursor.execute(query, (ISBN, school_id))
            book_id = cursor.fetchall()[0]
            cursor.close()

            cursor = connection.cursor()
            query_role = "SELECT role FROM user WHERE user_id = %s"
            cursor.execute(query_role, (user_id,))
            role = cursor.fetchone()[0]
            cursor.close()

            cursor = connection.cursor()
            query_reservation = "SELECT weekly_reservations FROM user WHERE user_id = %s"
            cursor.execute(query_reservation, (user_id,))
            reservation_count = cursor.fetchone()[0]
            cursor.close()

            if (role.lower() == 'student' and reservation_count < 2) or (role.lower() == 'teacher' and reservation_count < 1):
                cursor = connection.cursor()
                query_create_reservation = "INSERT INTO reservation (user_id, book_id, reservation_date) VALUES (%s, %s, (CURDATE))"
                cursor.execute(query_create_reservation, (user_id, book_id))
                connection.commit()
                cursor.close()

                success = "Reservation created successfully."
                return redirect(url_for('book_search', success=success))
            else:
                error = "You have reached the maximum number of reservations per week."
                return redirect(url_for('book_search', error=error))
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')
    
@app.route('/user/my_reservations') 
def my_reservations():
    try:
        if is_teacher or is_student:
            user_id = session.get('user_id')[0]

            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT r.reservation_id, b.title, r.reservation_date
                FROM reservation r
                INNER JOIN book b ON r.book_id = b.book_id
                WHERE r.user_id = %s
            """
            cursor.execute(query, (user_id,))
            reservations = cursor.fetchall()
            cursor.close()
            if not reservations:
                error = "You don't have any reservations."
                return render_template('my_reservations.html', reservations=None, error=error)
            else:
                return render_template('my_reservations.html', reservations=reservations, error=None)
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')

@app.route('/user/delete_reservation/<int:reservation_id>', methods=['POST']) 
def delete_reservation(reservation_id):
    try:
        if is_teacher or is_student:
            user_id = session.get('user_id')[0]
            cursor = connection.cursor()
            query = "DELETE FROM reservation WHERE reservation_id = %s AND user_id = %s"
            cursor.execute(query, (reservation_id, user_id,))
            connection.commit()
            cursor.close()

            success = "Reservation deleted successfully."
            return redirect(url_for('my_reservations', success=success))
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')


@app.route('/user/my_reviews') 
def my_reviews():
    try:
        if is_teacher or is_student:
            user_id = session.get('user_id')[0]

            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT r.review_id, b.title, r.rating, r.comments
                FROM review r
                INNER JOIN book b ON r.book_id = b.book_id
                WHERE r.user_id = %s
            """
            cursor.execute(query, (user_id,))
            reviews = cursor.fetchall()
            cursor.close()
            if not reviews:
                error = "You don't have any reviews."
                return render_template('my_reviews.html', reviews=None, error=error)
            else:
                return render_template('my_reviews.html', reviews=reviews, error=None)
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')


@app.route('/user/delete_review/<int:review_id>', methods=['POST']) 
def delete_review(review_id):
    try:
        if is_teacher or is_student:
            user_id = session.get('user_id')[0]
            cursor = connection.cursor()
            query = "DELETE FROM review WHERE review_id = %s AND user_id = %s"
            cursor.execute(query, (review_id, user_id,))
            connection.commit()
            cursor.close()

            success = "Review deleted successfully."
            return redirect(url_for('my_reviews', success=success))
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')

@app.route('/user/edit_review/<int:review_id>', methods=['GET', 'POST']) 
def edit_review(review_id):
    try:
        if is_teacher or is_student:
            user_id = session.get('user_id')[0]

            cursor = connection.cursor(dictionary=True)
            query_review = """
            SELECT r.review_id, b.title, r.rating, r.comments
            FROM review r
            INNER JOIN book b ON r.book_id = b.book_id
            WHERE r.review_id = %s AND r.user_id = %s
            """
            cursor.execute(query_review, (review_id, user_id,))
            review = cursor.fetchone()
            cursor.close()
            if review:
                form = edit_review_form()
                if form.validate_on_submit():
                    rating = form.rating.data
                    comments = form.comments.data

                    cursor = connection.cursor()
                    query_update = """
                    UPDATE review
                    SET rating = %s, comments = %s
                    WHERE review_id = %s AND user_id = %s
                    """
                    cursor.execute(query_update, (rating, comments, review['review_id'], user_id,))
                    connection.commit()
                    cursor.close()

                    success_message = "Review updated successfully."
                    return redirect(url_for('my_reviews', success=success_message))
                return render_template('edit_review.html', form=form, review=review, review_id=review_id)
            else:
                error_message = "Review not found or you don't have permission to edit it."
                return redirect(url_for('my_reviews', error=error_message))
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')

@app.route('/user/borrowed_books') 
def borrowed_books():
    try:
        if is_teacher or is_student:
            user_id = session.get('user_id')[0]
            
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT b.*
                FROM borrowing br
                INNER JOIN book b ON br.book_id = b.book_id
                WHERE br.user_id = %s
            """
            cursor.execute(query, (user_id,))
            borrowed_books = cursor.fetchall()
            cursor.close()

            if borrowed_books:
                for book in borrowed_books:
                    book['keywords'] = ', '.join([keyword for keyword in eval(book['keywords']) ]) 

                    cursor = connection.cursor()
                    query = "SELECT name FROM category WHERE category_id IN (SELECT category_id FROM book_category WHERE book_id = %s)"
                    cursor.execute(query, (book['book_id'],))
                    categories = cursor.fetchall()
                    cursor.close()

                    book['category_id'] = ', '.join([category[0] for category in categories])
                    
                    cursor = connection.cursor()
                    query = "SELECT name FROM language WHERE language_id = %s"
                    cursor.execute(query, (book['language_id'],))
                    language = cursor.fetchone()
                    cursor.close()
                    book['language_id'] = language[0]

                    cursor = connection.cursor()
                    query = "SELECT author_id, first_name, last_name FROM author WHERE author_id IN (SELECT author_id FROM book_author WHERE book_id = %s)"
                    cursor.execute(query, (book['book_id'],))
                    authors = cursor.fetchall()
                    cursor.close()
                    book['author_id'] = ', '.join([author[1] + ' ' + author[2] for author in authors])
                return render_template('borrowed_books.html', borrowed_books=borrowed_books)
            else:
                error = "You have not borrowed any books."
                return render_template('borrowed_books.html', error=error)
        else:
            flash("You have to be a user", "error")
            return render_template('home.html')
    except Exception as e:
        flash("There weren't any results for your request! Please try again.", "error")
        return render_template('user.html')



if __name__ == '__main__':
    app.run()
