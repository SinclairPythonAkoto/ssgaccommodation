DROP TABLE if exists ssg_contact;
CREATE TABLE ssg_contact (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  age INTEGER,
  sex VARCHAR,
  email VARCHAR,
  interest VARCHAR,
  questions VARCHAR,
  );