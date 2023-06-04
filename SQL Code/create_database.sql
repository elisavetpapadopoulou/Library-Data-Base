CREATE TABLE author (
    	author_id INT PRIMARY KEY AUTO_INCREMENT,
    	first_name VARCHAR(50) NOT NULL,
    	last_name VARCHAR(50) NOT NULL,
    	biography VARCHAR(50) NOT NULL
    	);

CREATE TABLE book (
	book_id INT PRIMARY KEY AUTO_INCREMENT,
	ISBN BIGINT NOT NULL, 
	title VARCHAR(100) NOT NULL, 
	publisher VARCHAR(50) NOT NULL, 
	number_of_pages INT NOT NULL, 
	summary VARCHAR(500) NOT NULL,
	available_copies INT NOT NULL,
	image VARCHAR(50) NOT NULL, 
	language_id VARCHAR(10) NOT NULL, 
	school_id INT NOT NULL, 
	keywords VARCHAR(150) NOT NULL 
	);

CREATE TABLE borrowing (
	borrowing_id INT PRIMARY KEY AUTO_INCREMENT, 
	user_id INT NOT NULL,
	book_id INT NOT NULL,
	borrowing_date DATE DEFAULT CURRENT_DATE, 
	due_date DATE DEFAULT DATE_ADD(borrowing_date, INTERVAL 1 WEEK), 
	returning_date DATE 
	);

CREATE TABLE category (
	category_id INT PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(70)
	);

CREATE TABLE language (
	language_id VARCHAR(10) PRIMARY KEY, 
	name VARCHAR(100)
	);

CREATE TABLE reservation (
	reservation_id INT PRIMARY KEY AUTO_INCREMENT, 	
	user_id INT NOT NULL, 
	book_id INT NOT NULL, 
	reservation_date DATE DEFAULT CURRENT_DATE
	);

CREATE TABLE review (
	review_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id INT NOT NULL, 
	book_id INT NOT NULL, 
	rating INT NOT NULL, 
	comments VARCHAR(200),
	is_approved VARCHAR(50)
	);

CREATE TABLE school (
	school_id INT PRIMARY KEY AUTO_INCREMENT,
	school_name VARCHAR(150) NOT NULL, 
	address VARCHAR(100) NOT NULL, 
	city VARCHAR(100) NOT NULL, 
	phone_number VARCHAR(10) NOT NULL, 
	email VARCHAR(50) NOT NULL, 
	school_director_name VARCHAR(100) NOT NULL, 
	library_operator_name VARCHAR(100) NOT NULL
	);

CREATE TABLE user (
	user_id INT PRIMARY KEY AUTO_INCREMENT, 
	username VARCHAR(80) NOT NULL,
	password VARCHAR(50) NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	date_of_birth DATE NOT NULL, 
	role VARCHAR(50) NOT NULL, 
	school_id INT NOT NULL,
	weekly_borrowings INT NOT NULL,
	weekly_reservations INT NOT NULL, 
	is_approved VARCHAR(10) 
	);

CREATE TABLE book_author (
  	book_id INT,
  	author_id INT,
  	PRIMARY KEY (book_id, author_id)
	);

CREATE TABLE book_category (
	book_id INT,
	category_id INT,
	PRIMARY KEY (book_id, category_id)
	); 
-- ------- BOOK CONSTSTRAINTS ---------------------------------------- 

ALTER TABLE book 
	ADD CONSTRAINT book_language_id
	FOREIGN KEY (language_id) REFERENCES language(language_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE book 
	ADD CONSTRAINT book_school_id
	FOREIGN KEY (school_id) REFERENCES school(school_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE book 
	ADD CONSTRAINT book_ISBN CHECK(ISBN >= 1000000000000 AND ISBN <= 9999999999999);

-- ------- BORROWING CONSTRAINTS ---------------------------------------
ALTER TABLE borrowing
	ADD CONSTRAINT borrowing_user_id
	FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE borrowing
	ADD CONSTRAINT borrowing_book_id
	FOREIGN KEY (book_id) REFERENCES book(book_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE reservation
	ADD CONSTRAINT reservation_user_id
	FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE reservation 
	ADD CONSTRAINT reservation_book_id
	FOREIGN KEY (book_id) REFERENCES book(book_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

-- ------------- REVIEW CONSTRAINTS ------------------------------------------

ALTER TABLE review 
	ADD CONSTRAINT review_user_id
	FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE review 
	ADD CONSTRAINT review_ISBN
	FOREIGN KEY (book_id) REFERENCES book(book_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE review 
	ADD CONSTRAINT review_rating CHECK(rating >=0 AND rating <= 5);

ALTER TABLE review 
	ADD CONSTRAINT review_is_approved CHECK(LOWER(is_approved) IN ('yes', 'no') OR is_approved IS NULL); 

-- ----------- SCHOOL CONSTRAINTS --------------------------------------------

ALTER TABLE school
	ADD CONSTRAINT school_phone_number CHECK(phone_number REGEXP '^[0-9]{10}$');

-- ------------ USER CONSTRAINTS ---------------------------------------------
ALTER TABLE user 	
	ADD CONSTRAINT user_school_id
	FOREIGN KEY (school_id) REFERENCES school(school_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE user
	ADD CONSTRAINT user_is_approved CHECK(LOWER(is_approved) IN ('yes', 'no') OR is_approved IS NULL);

-------------- BOOK_AUTHOR CONSTRAINTS ----------------------------------------
ALTER TABLE book_author 
	ADD CONSTRAINT book_author_book_id
	FOREIGN KEY (book_id) REFERENCES book (book_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE book_author 
	ADD CONSTRAINT book_author_author_id
	FOREIGN KEY (author_id) REFERENCES author (author_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

--------------- BOOK_CATEGORY CONSTRAINTS -------------------------------------

ALTER TABLE book_category 
	ADD CONSTRAINT book_category_book_id
	FOREIGN KEY (book_id) REFERENCES book (book_id)
	ON DELETE RESTRICT
	ON UPDATE CASCADE;

ALTER TABLE book_category 
	ADD CONSTRAINT book_category_category_id
	FOREIGN KEY (category_id) REFERENCES category (category_id)
	ON DELETE RESTRICT 
	ON UPDATE CASCADE;

CREATE INDEX author_name_idx ON author(first_name, last_name);

CREATE INDEX ISBN_idx ON book(ISBN);
CREATE INDEX title_idx ON book(title);
CREATE INDEX keywords_idx ON book(keywords);

CREATE INDEX borrowing_date_idx ON borrowing(borrowing_date);
CREATE INDEX due_date_idx ON borrowing(due_date);
CREATE INDEX returning_date_idx ON borrowing(returning_date);

CREATE INDEX name_idx ON category(name);

CREATE INDEX name_idx ON language(name);

CREATE INDEX reservation_date_idx ON reservation(reservation_date);

CREATE INDEX school_name_idx ON school(school_name);

CREATE UNIQUE INDEX username_idx ON user(username);
CREATE INDEX user_name_idx ON user(first_name, last_name);
CREATE INDEX date_of_birth_idx ON user(date_of_birth);

SET GLOBAL event_scheduler = ON;

-- ----- when both isbn and school_id are the same with an already inserted book don't let it be inserted----

DELIMITER //

CREATE TRIGGER before_insert_book
BEFORE INSERT ON book
FOR EACH ROW
BEGIN
    DECLARE existing_book_id INT;
    
    -- Check if a book with the same school_id and isbn already exists
    SELECT book_id INTO existing_book_id
    FROM book
    WHERE school_id = NEW.school_id AND isbn = NEW.isbn
    LIMIT 1;
    
    IF existing_book_id IS NOT NULL THEN
        -- Cancel the insert operation
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book already exists.';
    END IF;
END //

DELIMITER ;


-- ---- decrease the available copies if a book is borrowed -------------

DELIMITER //

CREATE TRIGGER decrease_copies 
AFTER INSERT ON borrowing 
FOR EACH ROW
BEGIN 
	IF NEW.returning_date IS NULL THEN 
	 UPDATE book
	 SET available_copies = available_copies-1
	 WHERE book_id = NEW.book_id;
	END IF;
END //

DELIMITER ;

-- ---- increase the available copies if a book is returned --------------

DELIMITER // 

CREATE TRIGGER increase_copies
AFTER UPDATE ON borrowing
FOR EACH ROW 
BEGIN 
	IF NEW.returning_date IS NOT NULL AND OLD.returning_date IS NULL THEN 
		UPDATE book
		SET available_copies = available_copies + 1
		WHERE book_id = NEW.book_id;
	END IF;
END //

DELIMITER ;

-- ---- delete a reservation after the passing of a week --------------

DELIMITER //

CREATE EVENT delete_reservation
ON SCHEDULE EVERY 1 DAY 
STARTS CURRENT_TIMESTAMP
DO
    DELETE FROM reservation WHERE reservation_date <= DATE_SUB(NOW(), INTERVAL 1 WEEK);
END//

DELIMITER ;


-- ---- reset the values of the weekly_reservations and weekly_borrowings every Sunday ----
-- ---- which will be the begginning of the new week --------------------------------------

DELIMITER //

CREATE EVENT reset_weekly_values
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP + INTERVAL 1 DAY
DO
BEGIN
    -- Check if it's Sunday (weekday 1) to perform the reset
    	IF DAYOFWEEK(CURDATE()) = 1 THEN
    -- Reset weekly_borrowings and weekly_reservations to 0
    		UPDATE user
    		SET weekly_borrowings = 0, weekly_reservations = 0;
	END IF;
END //

DELIMITER ;

-- ---- prevent a reservation when the limit is exceeded, a return is belated, ----------
-- ---- the user already has a copy of this book in his possession via borrowing, -------
-- ---- the user is trying to reserve a book fromm another school, ---------------------- 
-- ---- or the user has already  made a resrvation for this book ------------------------ 

DELIMITER //

CREATE TRIGGER check_reservation 
BEFORE INSERT ON reservation 
FOR EACH ROW 
BEGIN 
	DECLARE user_role VARCHAR(50);
	DECLARE borrowings_counter INT;
	DECLARE user_school INT;
	DECLARE reservations_counter INT;
	DECLARE existing_borrowing INT;
	DECLARE existing_reservation INT;
	
	-- Get the user's role --
	SELECT role INTO user_role FROM user WHERE user_id = NEW.user_id;
	
	-- Get the user's current weekly borrowings and reservations ----
	SELECT weekly_borrowings, weekly_reservations INTO borrowings_counter, reservations_counter FROM user WHERE user_id = NEW.user_id;
	
	-- Get the user's school_id -- 
	SELECT school_id INTO user_school FROM user WHERE user_id = NEW.user_id; 

	-- Check the user is reserving a book from his own school -- 
	IF user_school != (SELECT school_id FROM book WHERE book_id = NEW.book_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You can only reserve books from your own school';
    	END IF;
	
	-- Check if the limit for reservations is exceeded based on their role --
	IF user_role = 'student' AND reservations_counter >= 2 THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation limit exceeded for student';
	ELSEIF user_role = 'teacher' AND reservations_counter >= 1 THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Resrvation limit exceeded for teacher';
	ELSEIF (user_role = 'administrator' OR user_role = 'operator') THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You cannot reserve a book!';
	END IF;

	-- Check if the user already has a copy of the book borrowed at the moment ----
	SELECT COUNT(*) INTO existing_borrowing FROM borrowing WHERE user_id = NEW.user_id AND book_id = NEW.book_id AND returning_date IS NULL;
	IF existing_borrowing > 0 THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User already has a copy of this book'; 
	END IF;

	-- Check id the user has already made a reservation for this book --------
	SELECT COUNT(*) INTO existing_reservation FROM reservation WHERE user_id = NEW.user_id AND book_id = NEW.book_id;
	IF existing_reservation > 0 THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User has already made a reservation for this book'; 
	END IF;

	-- Check if the user has a belated return ---
	IF EXISTS (SELECT 1 FROM borrowing WHERE user_id = NEW.user_id AND returning_date IS NULL AND CURDATE() >= due_date) THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User has a belated return';
	END IF;
	
	-- If it's this week's reservation, update weekly_reservations 
	IF YEARWEEK(NEW.reservation_date) = YEARWEEK(CURDATE()) THEN
		UPDATE user
		SET weekly_reservations = weekly_reservations+1
		WHERE user_id = NEW.user_id;
	END IF;
END//

DELIMITER ; 


-- ---- prevent a borrowing when the borrowing limit is exceeded, a return is belated,    ---------------
-- ---- the user already has a copy of this book in his possession via borrowing,         ---------------
-- ---- there are no available copies left, and the user is trying to borrow a book from another school-- 


DELIMITER //

CREATE TRIGGER check_borrowing 
BEFORE INSERT ON borrowing 
FOR EACH ROW 
BEGIN 
	DECLARE user_role VARCHAR(50);
	DECLARE borrowings_counter INT;
	DECLARE user_school INT;
	DECLARE reservations_counter INT;
	DECLARE existing_borrowing INT;
	DECLARE current_available_copies INT;
	
	-- Get the user's role --
	SELECT role INTO user_role FROM user WHERE user_id = NEW.user_id;
	
	-- Get the user's current weekly borrowings and reservations ----
	SELECT weekly_borrowings, weekly_reservations INTO borrowings_counter, reservations_counter FROM user WHERE user_id = NEW.user_id;

	-- Get the user's school_id -- 
	SELECT school_id INTO user_school FROM user WHERE user_id = NEW.user_id;

	-- Get the book's current available copies -------
	SELECT available_copies INTO current_available_copies FROM book WHERE book_id = NEW.book_id;

	-- Check that the user is borrowing a book form his own school -- 
	IF user_school != (SELECT school_id FROM book WHERE book_id = NEW.book_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You can only borrow books from your own school';
    	END IF;

	-- Check if there are any available copies at the moment ------
	IF current_available_copies < 1 THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No available copies at the moment, please make a reservation';
	END IF;

	-- Check if the limit for borrowings is exceeded based on their role --
	IF user_role = 'student' AND borrowings_counter >= 2 THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Borrowing limit exceeded for student';
	ELSEIF user_role = 'teacher' AND borrowings_counter >= 1 THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Borrowing limit exceeded for teacher';
	ELSEIF (user_role = 'administrator' OR user_role = 'operator') THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You cannot borrow a book!';
	END IF;

	-- Check if the user already has a copy of the book borrowed at the moment ----
	SELECT COUNT(*) INTO existing_borrowing FROM borrowing WHERE user_id = NEW.user_id AND book_id = NEW.book_id AND returning_date IS NULL;
	IF existing_borrowing > 0 THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User already has a copy of this book'; 
	END IF;

	-- Check if the user has a belated return ---
	IF EXISTS (SELECT 1 FROM borrowing WHERE user_id = NEW.user_id AND returning_date IS NULL AND CURDATE() >= due_date) THEN 
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User has a belated return';
	END IF;

	-- If it's this week's reservation, update weekly_borrowings 
	IF YEARWEEK(NEW.borrowing_date) = YEARWEEK(CURDATE()) THEN
		UPDATE user
		SET weekly_borrowings = weekly_borrowings+1
		WHERE user_id = NEW.user_id;
	END IF;
END//

DELIMITER ;
