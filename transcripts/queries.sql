create table if not exists course(
    course_code text primary key,
    course_name text not null,
    credits integer default 0,
    hrs integer default 0
);
create table if not exists department(
    department_id integer primary key,
    dname text not null,
    hod_name text not null
);
create table if not exists location(
    location_id integer primary key,
    street text,
    city text not null,
    state text not null,
    country text not null,
    pincode text
);
create table if not exists college(
    college_id integer primary key,
    college_name text not null,
    location_id integer not null,
    foreign key(location_id) references location(location_id)
);

create table if not exists student(
    student_id integer primary key AUTOINCREMENT,
    email_id text not null,
    sname text not null,
    DOB DATE not null,
    phone text not null,
    ssnum text not null unique,
    start_date date not null,
    end_date date not null,
    department_id integer not null,
    college_id integer not null,
    location_id integer not null,
    FOREIGN KEY(department_id) references department(department_id),
    FOREIGN KEY(location_id) references location(location_id) ,
    FOREIGN KEY(college_id) references college(college_id)
);


create table if not exists student_course(
    student_id integer not null,
    course_code text not null,
    taken_in_sem text not null,
    grade text default 'I',
    FOREIGN KEY(student_id) references student(student_id),
    FOREIGN KEY(course_code) references course(course_code)

);


insert into location values(1,'32.Baker street','nagpur','maharashtra','india','440011');
insert into location values(2,'gittikhadan','nagpur','maharashtra','india','440001');
insert into college values(1,"RCOEM",2);
insert into department values(1,'CSE','Dr. M.B Chandak');
insert into course values('CST312','Advanced Data Structures',9,60);
insert into course values('CST313','Mobile Application Programming',9,65);
insert into student('email_id','sname','DOB','phone','ssnum','start_date','end_date','department_id','college_id','location_id') values('agrawalrs_1@rknec.edu','rajat agrawal','10/10/1998','9876543210','RCOEM73','08/08/2016','08-06-2020',1,1,1);
insert into student_course values(1,'CST312','V','AA');