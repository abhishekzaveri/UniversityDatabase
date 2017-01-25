
import psycopg2
import os
import csv
#from sqlalchemy.exc import IntegrityError
from psycopg2 import IntegrityError

#GLOBAL VARIABLES
course_tuples = []
meeting_tuples = []
student_tuples = []


# Replaces "" with None (Postgres NULL)
def replaceNone(row):
    row = [None if (x == "") else x for x in row]
    return row


def main():
    for fn in os.listdir('Grades'):
        print "on " + fn
        fn = "Grades/" + fn

        f = open(fn,'rb')
        reader = csv.reader(f)
        row = next(reader)                # Read the first line

        try:
            while row is not None:


                if len(row) == 1:
                    pass

                elif row[0] == "CID":
                    row = replaceNone(next(reader))
                    course_tuples.append(row)

                elif row[0] == "INSTRUCTOR(S)":
                    row = replaceNone(next(reader))
                    while (len(row) != 1):
                        meeting_tuples.append(row)
                        row = replaceNone(next(reader))

                elif row[0] == "SEAT":
                    row = replaceNone(next(reader))
                    counter = 0
                    while (len(row) != 1):
                        counter = counter + 1
                        student_tuples.append(row)

                        row = replaceNone(next(reader))

                    if counter == 0:
                        course_tuples.pop()

                row = replaceNone(next(reader))



        except:
            #print course_tuples
            #print meeting_tuples
            #print len(student_tuples)
            #print student_tuples[0]
            f.close()



    # Connect to the database
    try:
        conn = psycopg2.connect(database='postgres', user=os.environ['USER'], port='5432')
    except:
        print "I am unable to connect to the database"

    # Create tables (first dropping them if they already exist)
    cur = conn.cursor()
    drop = """drop table if exists """
    for table in ['Course','Student','Meeting']:
        cur.execute(drop + table + " cascade")

    cur.execute("""CREATE TABLE Course (cid INT, term INT, subj TEXT, crse INT, sec INT,units TEXT, PRIMARY KEY(cid,term))""")
    cur.execute("""CREATE TABLE Meeting (instructor TEXT,type TEXT, days TEXT, times TEXT, build TEXT, room INT)""")
    cur.execute("""CREATE TABLE Student (seat INT, sid INT NOT NULL, surname TEXT, prefname TEXT, level TEXT,
                                         units DECIMAL, class TEXT, major TEXT,grade TEXT, status TEXT, email TEXT,
                                         courseid SERIAL PRIMARY KEY) """)


    # Insert tuples into Course table
    string = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s)", tup) for tup in course_tuples)
    cur.execute("INSERT INTO Course VALUES " + string)


    # Insert tuples into Meeting table
    string = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s)", tup) for tup in meeting_tuples)
    cur.execute("INSERT INTO Meeting VALUES "+ string)


    #I Insert tuples into Student table
    string = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", tup) for tup in student_tuples)
    cur.execute("INSERT INTO Student VALUES "+ string)

    conn.commit()

    cur.execute("""CREATE TABLE student_two AS SELECT DISTINCT sid,courseid FROM student""")
    conn.commit()


if __name__ == '__main__': main()
