import psycopg2
import csv
import os
import pprint
import datetime as dt
import collections
import math


#helper functions -----------------------------------
def convertToMilitary(time):
	timeZone = time[-3:]
	if time[0] == " ":
		time = time[1:]
	if timeZone[0] == " ":
		timeZone = timeZone[1:3]
	nums = time.split(" ")[0].split(":")
	if timeZone[0:2] == "PM" and nums[0] != "12":
		nums[0] = str(int(nums[0]) + 12)
	returnTime = nums[0] + nums[1] 
	return int(returnTime)

def isOverlap(st1,et1,st2,et2):
	st1 = convertToMilitary(st1)
	et1 = convertToMilitary(et1)
	st2 = convertToMilitary(st2)
	et2 = convertToMilitary(et2)
	if st1 < st2 and st2 < et1:
		return True
	elif st1 < et1 and et1 < et1:
		return True
	elif st1 == st2 and et1 ==et2:
		return True
	else:
		return False

#-----------------------------------------------------


def problem3A(cursor):
    print "Part A"
    cursor.execute("SELECT units, COUNT(*) AS num FROM( SELECT SID, term, SUM(units) as units FROM ( SELECT DISTINCT CID, SID, term, units FROM student NATURAL JOIN studentclasslog) AS test GROUP BY SID, term) AS test2 GROUP BY units ORDER BY units")
    allRows = cursor.fetchall()
    totalUnits = 0
    rowList = []
    answer = []
    for row in allRows:
        rowList = list(row)
        totalUnits = totalUnits + row[1]
    for row in allRows:
        rowList = list(row)
        if rowList[0] >= 1 and rowList[0] <= 20 and math.floor(rowList[0]) == rowList[0]:        
            percent = (float(rowList[1]) / totalUnits) * 100
            answer.append([rowList[0], percent])
    print "Units per Quarter | Percent"
    for row in answer:
        out = "{:<18}".format(row[0]) + "|" + str(row[1]) + "%"
        print out
    print "\n"

def problem3B(cursor):
    print "Part B"
    cursor.execute("SELECT totalunits, AVG(GPA) FROM ( SELECT points, totalunits,  CASE WHEN totalunits = 0 THEN 0 ELSE points / totalunits END AS GPA FROM ( SELECT SID, term, SUM(gradepoints) AS points, SUM(units) AS totalunits FROM ( SELECT SID, term, units, points * units AS gradepoints FROM ( SELECT SID, term, units, grade, CASE WHEN grade = 'A+' THEN 4.0 WHEN grade = 'A' THEN 4.0 WHEN grade = 'A-' THEN 3.7 WHEN grade = 'B+' THEN 3.3 WHEN grade = 'B' THEN 3.0 WHEN grade = 'B-' THEN 2.7 WHEN grade = 'C+' THEN 2.3 WHEN grade = 'C' THEN 2.0 WHEN grade = 'C-' THEN 1.7 WHEN grade = 'D+' THEN 1.3 WHEN grade = 'D' THEN 1.0 WHEN grade = 'D-' THEN 0.7 WHEN grade = 'F' THEN 0.0 END as points FROM ( SELECT DISTINCT CID, SID, term, units, grade FROM student NATURAL JOIN studentclasslog) AS test WHERE grade = 'A' OR grade = 'A-' OR grade = 'B+' OR grade = 'B' OR grade = 'B-' OR grade = 'C+' OR grade = 'C' OR grade = 'C-' OR grade = 'D+' OR grade = 'D' OR grade = 'D-' OR grade = 'F' OR grade = 'A+') AS test2) AS test3 GROUP BY SID, term) AS test4) AS test5 WHERE totalunits >= 1 AND totalunits <= 20 AND totalunits = FLOOR(totalunits) GROUP BY totalunits ORDER BY totalunits")
    answer = cursor.fetchall()
    print "Units per Quarter | Average GPA"
    for row in answer:
        out = "{:<18}".format(row[0]) + "|" + str(row[1])
        print out
    print "\n"

def problem3C(quora):
	print "Part C"
	hardDict = {}
	easyDict = {}
	easiest = []
	hardest = []
	goodGrades = ['A+', 'A','A-','B+']
	badGrades = ['F','D-','D','D+'] 

	quora.execute("""
		WITH InstructorGrades AS(
			SELECT instructor, CourseInformation.CID ,SID,term, grade
			FROM CourseInformation NATURAL JOIN StudentClassLog
		),
		DedupedClasses AS (
			SELECT instructor,cast(count(SID) AS FLOAT) AS num1 FROM(
				SELECT  instructor, CID, SID 
					FROM InstructorGrades 
					GROUP BY instructor, CID, SID
					ORDER BY instructor
				) AS foo
				GROUP BY instructor
				ORDER BY instructor
		),
		deletedGrades AS (
			SELECT  instructor, grade, cast(count(grade) AS FLOAT )as num2
				FROM (
					SELECT instructor, CID,SID,term,grade FROM InstructorGrades
					GROUP BY instructor,CID,SID,term,grade
				)AS bar
			GROUP BY instructor, grade
			ORDER BY num2 DESC
		),
		gradeRatios AS (
			SELECT teacher, grade, num2/num1 AS ratio, num1 FROM (
				SELECT A.instructor AS teacher, num1,
				B.instructor i2, grade, num2
					FROM DedupedClasses AS A,deletedGrades AS B
					WHERE A.instructor = B.instructor
			) AS foo 
		)
		SELECT * FROM gradeRatios
		ORDER BY num1 DESC;""")
	for x in quora:
		if x[1] in goodGrades and x[2] >= .30:
			easiest.append(x[0])
		if x[1] in badGrades and x[2] >= .20:
			hardest.append(x[0])
		easiest = list(set(easiest))
		hardest = list(set(hardest))

	print "\nThe easiest teachers are: "
	pprint.pprint(easiest)
	print '\n'
	print "The hardest teachers are:" 
	pprint.pprint(hardest)
	print "\nThe average grade assigned for each teacher is as follows: \n"

	quora.execute("""
		WITH InstructorGrades AS(
			SELECT instructor, CourseInformation.CID ,SID,term, grade
			FROM CourseInformation NATURAL JOIN StudentClassLog
		),
		DedupedClasses AS (
			SELECT instructor,cast(count(SID) AS FLOAT) AS num1 FROM(
				SELECT  instructor, CID, SID 
					FROM InstructorGrades 
					GROUP BY instructor, CID, SID
					ORDER BY instructor
				) AS foo
				GROUP BY instructor
				ORDER BY instructor
		),
		deletedGrades AS (
			SELECT  instructor, grade, cast(count(grade) AS FLOAT )as num2
				FROM (
					SELECT instructor, CID,SID,term,grade FROM InstructorGrades
					GROUP BY instructor,CID,SID,term,grade
				)AS bar
			GROUP BY instructor, grade
			ORDER BY num2 DESC
		)
		SELECT instructor, grade, num2 FROM deletedGrades
		WHERE
		  num2 = (SELECT MAX(num2) FROM deletedGrades i 
				  WHERE i.instructor = deletedGrades.instructor);""")
	for x in quora:
		if x[0] in easiest:
			print "The average grade given by " + x[0] + " is " + x[1]+ "\n"
		if x[0] in hardest:
			print "The average grade given by " + x[0] + " is " + x[1] + "\n"
	print "\n"

def problem3D(cursor):
    print "Part D"
    cursor.execute("SELECT course_name, MAX(GPA) AS easiest FROM ( SELECT course_name, instructor, totalpoints / totalunits AS GPA FROM ( SELECT course_name, instructor, SUM(gradepoints) AS totalpoints, SUM(units) AS totalunits FROM ( SELECT course_name, instructor, grade, points, units, SID, points * units AS gradepoints FROM ( SELECT DISTINCT CID, subject || course_number AS course_name, instructor, term, SID, units, grade, CASE WHEN grade = 'A+' THEN 4.0 WHEN grade = 'A' THEN 4.0 WHEN grade = 'A-' THEN 3.7 WHEN grade = 'B+' THEN 3.3 WHEN grade = 'B' THEN 3.0 WHEN grade = 'B-' THEN 2.7 WHEN grade = 'C+' THEN 2.3 WHEN grade = 'C' THEN 2.0 WHEN grade = 'C-' THEN 1.7 WHEN grade = 'D+' THEN 1.3 WHEN grade = 'D' THEN 1.0 WHEN grade = 'D-' THEN 0.7 WHEN grade = 'F' THEN 0.0 END AS points FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation WHERE (grade = 'A' OR grade = 'A-' OR grade = 'B+' OR grade = 'B' OR grade = 'B-' OR grade = 'C+' OR grade = 'C' OR grade = 'C-' OR grade = 'D+' OR grade = 'D' OR grade = 'D-' OR grade = 'F' OR grade = 'A+') AND subject = 'ABC' AND  course_number >= 100 AND course_number <= 199) AS test ORDER BY instructor) AS test2 GROUP BY course_name, instructor ORDER BY course_name) AS test3) AS test4 GROUP BY course_name")
    easiestLetterGrade = cursor.fetchall()
    
    cursor.execute("SELECT course_name, MIN(GPA) AS hardest FROM ( SELECT course_name, instructor, totalpoints / totalunits AS GPA FROM ( SELECT course_name, instructor, SUM(gradepoints) AS totalpoints, SUM(units) AS totalunits FROM ( SELECT course_name, instructor, grade, points, units, SID, points * units AS gradepoints FROM ( SELECT DISTINCT CID, subject || course_number AS course_name, instructor, term, SID, units, grade, CASE WHEN grade = 'A+' THEN 4.0 WHEN grade = 'A' THEN 4.0 WHEN grade = 'A-' THEN 3.7 WHEN grade = 'B+' THEN 3.3 WHEN grade = 'B' THEN 3.0 WHEN grade = 'B-' THEN 2.7 WHEN grade = 'C+' THEN 2.3 WHEN grade = 'C' THEN 2.0 WHEN grade = 'C-' THEN 1.7 WHEN grade = 'D+' THEN 1.3 WHEN grade = 'D' THEN 1.0 WHEN grade = 'D-' THEN 0.7 WHEN grade = 'F' THEN 0.0 END AS points FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation WHERE (grade = 'A' OR grade = 'A-' OR grade = 'B+' OR grade = 'B' OR grade = 'B-' OR grade = 'C+' OR grade = 'C' OR grade = 'C-' OR grade = 'D+' OR grade = 'D' OR grade = 'D-' OR grade = 'F' OR grade = 'A+') AND subject = 'ABC' AND  course_number >= 100 AND course_number <= 199) AS test ORDER BY instructor) AS test2 GROUP BY course_name, instructor ORDER BY course_name) AS test3) AS test4 GROUP BY course_name")
    hardestLetterGrade = cursor.fetchall()
    
    cursor.execute("SELECT course_name, instructor, totalpoints / totalunits AS GPA FROM ( SELECT course_name, instructor, SUM(gradepoints) AS totalpoints, SUM(units) AS totalunits FROM ( SELECT course_name, instructor, grade, points, units, SID, points * units AS gradepoints FROM ( SELECT DISTINCT CID, subject || course_number AS course_name, instructor, term, SID, units, grade, CASE WHEN grade = 'A+' THEN 4.0 WHEN grade = 'A' THEN 4.0 WHEN grade = 'A-' THEN 3.7 WHEN grade = 'B+' THEN 3.3 WHEN grade = 'B' THEN 3.0 WHEN grade = 'B-' THEN 2.7 WHEN grade = 'C+' THEN 2.3 WHEN grade = 'C' THEN 2.0 WHEN grade = 'C-' THEN 1.7 WHEN grade = 'D+' THEN 1.3 WHEN grade = 'D' THEN 1.0 WHEN grade = 'D-' THEN 0.7 WHEN grade = 'F' THEN 0.0 END AS points FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation WHERE (grade = 'A' OR grade = 'A-' OR grade = 'B+' OR grade = 'B' OR grade = 'B-' OR grade = 'C+' OR grade = 'C' OR grade = 'C-' OR grade = 'D+' OR grade = 'D' OR grade = 'D-' OR grade = 'F' OR grade = 'A+') AND subject = 'ABC' AND  course_number >= 100 AND course_number <= 199) AS test ORDER BY instructor) AS test2 GROUP BY course_name, instructor ORDER BY course_name) AS test3 WHERE instructor IS NOT NULL")
    allLetterGrade = cursor.fetchall()
    
    cursor.execute(""" 
    SELECT course_name, MAX(passrate) AS easiest
FROM (
    SELECT course_name, instructor, passes / totalunits AS passrate
    FROM (
        SELECT course_name, instructor,  SUM(units) AS totalunits, SUM(CASE WHEN grade = 'P' THEN 1.0 * units
                                                                              WHEN grade = 'S' THEN 1.0 * units END)::float AS passes
        FROM (      
            SELECT DISTINCT CID, subject || course_number AS course_name, instructor, term, SID, grade, units
            FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation
            WHERE (grade = 'P' OR grade = 'NP' OR grade = 'S') AND subject = 'ABC' AND course_number >= 100 AND course_number <= 199) AS test
        GROUP BY course_name, instructor) AS test2) AS test3
GROUP BY course_name""")
    easiestPassRate = cursor.fetchall()
    
    cursor.execute("""
    SELECT course_name, MIN(passrate) AS hardest
FROM (
    SELECT course_name, instructor, passes / totalunits AS passrate
    FROM (
        SELECT course_name, instructor,  SUM(units) AS totalunits, SUM(CASE WHEN grade = 'P' THEN 1.0 * units
                                                                            WHEN grade = 'S' THEN 1.0 * units END)::float AS passes
        FROM (      
            SELECT DISTINCT CID, subject || course_number AS course_name, instructor, term, SID, grade, units
            FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation
            WHERE (grade = 'P' OR grade = 'NP' OR grade = 'S') AND subject = 'ABC' AND course_number >= 100 AND course_number <= 199) AS test
        GROUP BY course_name, instructor) AS test2) AS test3
GROUP BY course_name
    """)
    hardestPassRate = cursor.fetchall()
    
    cursor.execute("""
    SELECT course_name, instructor, passes / totalunits AS passrate
FROM (
    SELECT course_name, instructor, units, SUM(units) AS totalunits, SUM(CASE WHEN grade = 'P' THEN 1.0 * units
                                                                              WHEN grade = 'S' THEN 1.0 * units END)::float AS passes
    FROM (      
        SELECT DISTINCT CID, subject || course_number AS course_name, instructor, term, SID, grade, units
        FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation
        WHERE (grade = 'P' OR grade = 'NP' OR grade = 'S') AND subject = 'ABC' AND course_number >= 100 AND course_number <= 199) AS test
    GROUP BY course_name, instructor, units) AS test2
    """)
    allPassRate = cursor.fetchall()
    
    easiestGPA = []
    hardestGPA = []
    easiestGPAList = []
    hardestGPAList = []
    for row in allLetterGrade:
        rowList = list(row)
        for easiest in easiestLetterGrade:
            easiestGPAList = list(easiest)
            if rowList[0] == easiestGPAList[0] and rowList[2] == easiestGPAList[1]:
                easiestGPAList.append(rowList[1])
                easiestGPA.append(easiestGPAList)
        for hardest in hardestLetterGrade:
            hardestGPAList = list(hardest)
            if rowList[0] == hardestGPAList[0] and rowList[2] == hardestGPAList[1]:
                hardestGPAList.append(rowList[1])
                hardestGPA.append(hardestGPAList)
                
    easiestAnswer = []
    hardestAnswer = []
    easiestList = []
    hardestList = []
    for row in allPassRate:
        rowList = list(row)
        for easiest in easiestPassRate:
            easiestList = list(easiest)
            if rowList[0] == easiestList[0] and rowList[2] == easiestList[1]:
                easiestList.append(rowList[1])
                easiestAnswer.append(easiestList)
        for hardest in hardestPassRate:
            hardestList = list(hardest)
            if rowList[0] == hardestList[0] and rowList[2] == hardestList[1]:
                hardestList.append(rowList[1])
                hardestAnswer.append(hardestList)
    #still need to check if there's any overlap between the P/NP lists and the GPA lists
    #if there is, remove P/NP portion of list
    for rowGPA in hardestGPA:
        for rowPNP in hardestAnswer:
            if rowGPA[0] == rowPNP[0]:
                hardestAnswer.remove(rowPNP)
                
    for rowGPA in easiestGPA:
        for rowPNP in easiestAnswer:
            if rowGPA[0] == rowPNP[0]:
                easiestAnswer.remove(rowPNP)
                
                
    print "Courses with Letter Grades"
    print "Course | Easiest Instructor(s) | Average GPA"
    for row in easiestGPA:
        out = "{:<7}".format(row[0]) + "|" + "{:<23}".format(row[2]) + "|" + str(row[1])
        print out
    
    print "Course | Hardest Instructor(s) | Average GPA"
    for row in hardestGPA:
        out = "{:<7}".format(row[0]) + "|" + "{:<23}".format(row[2]) + "|" + str(row[1])
        print out
        
    print "Courses without Letter Grades"
    print "Course | Easiest Instructor(s) | Pass Rate"
    for row in easiestAnswer:
        out = "{:<7}".format(row[0]) + "|" + "{:<23}".format(row[2]) + "|" + str(row[1] * 100) + "%"
        print out
    print "Course | Hardest Instructor(s) | Pass Rate"
    for row in hardestAnswer:
        out = "{:<7}".format(row[0]) + "|" + "{:<23}".format(row[2]) + "|" + str(row[1] * 100) + "%"
        print out
	print "\n"


def problem3E(quora):
	print "Part E"
	soln = []
	quora.execute("""
	WITH CourseInfo AS (
	    SELECT c1.term, c1.CID, c1.building building,room, start_time,end_time, course_number,days 
	        FROM CourseInformation c1 , Course c2
	        WHERE c1.CID = c2.CID 
	        AND c1.term = c2.term  
	        AND start_time is not NULL AND end_time is not NULL
	),
	InfoJoin AS (
	    SELECT c1.term, c1.CID id1, c1.course_number crs1,c1.start_time st1,c1.end_time et1,
	    c2.CID id2, c2.course_number crs2,c2.start_time st2,
	    c2.end_time et2
	        FROM CourseInfo c1, CourseInfo c2
	        WHERE c1.term = c2.term
	        AND c1.days = c2.days
	        AND c1.building = c2.building
	        AND c1.room = c2.room
	        AND c1.course_number != c2.course_number
	        AND c1.CID != c2.CID 
	)
	SELECT DISTINCT * FROM InfoJoin
	ORDER BY crs1;""")

	for x in quora:
		if isOverlap(x[3],x[4],x[7],x[8]):
			soln.append((x[0],x[1], x[2],x[5],x[6]))

	quora.execute("""CREATE TABLE Solution(CID1 TEXT, day1 TEXT, crs TEXT,
		start_time1 TEXT,end_time1 TEXT,CID2 TEXT, day2 TEXT, crs2 TEXT,
		start_time2 TEXT,end_time2 TEXT);""")
	for x in soln:
		print x
	print "\n"


def problem3F(cursor):
    print "Part F"
    cursor.execute("SELECT major, totalpoints / totalunits AS GPA FROM ( SELECT major, SUM(units) AS totalunits, SUM(gradepoints) AS totalpoints FROM ( SELECT CID, SID, major, units, points, grade, units * points AS gradepoints FROM ( SELECT DISTINCT CID, subject, SID, major, units, grade,  CASE WHEN grade = 'A+' THEN 4.0 WHEN grade = 'A' THEN 4.0 WHEN grade = 'A-' THEN 3.7 WHEN grade = 'B+' THEN 3.3 WHEN grade = 'B' THEN 3.0 WHEN grade = 'B-' THEN 2.7 WHEN grade = 'C+' THEN 2.3 WHEN grade = 'C' THEN 2.0 WHEN grade = 'C-' THEN 1.7 WHEN grade = 'D+' THEN 1.3 WHEN grade = 'D' THEN 1.0 WHEN grade = 'D-' THEN 0.7 WHEN grade = 'F' THEN 0.0 END AS points FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation WHERE subject = 'ABC') AS test) AS test2 GROUP BY major) AS test3 WHERE totalpoints IS NOT NULL")
    allGPA = cursor.fetchall()
    
    cursor.execute("SELECT MAX(totalpoints / totalunits) AS GPA FROM ( SELECT major, SUM(units) AS totalunits, SUM(gradepoints) AS totalpoints FROM ( SELECT CID, SID, major, units, points, units * points AS gradepoints FROM ( SELECT DISTINCT CID, subject, SID, major, units, grade,  CASE WHEN grade = 'A+' THEN 4.0 WHEN grade = 'A' THEN 4.0 WHEN grade = 'A-' THEN 3.7 WHEN grade = 'B+' THEN 3.3 WHEN grade = 'B' THEN 3.0 WHEN grade = 'B-' THEN 2.7 WHEN grade = 'C+' THEN 2.3 WHEN grade = 'C' THEN 2.0 WHEN grade = 'C-' THEN 1.7 WHEN grade = 'D+' THEN 1.3 WHEN grade = 'D' THEN 1.0 WHEN grade = 'D-' THEN 0.7 WHEN grade = 'F' THEN 0.0 END AS points FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation WHERE subject = 'ABC') AS test) AS test2 GROUP BY major) AS test3 WHERE totalpoints IS NOT NULL")
    maxGPA = cursor.fetchall()
    
    cursor.execute("SELECT MIN(totalpoints / totalunits) AS GPA FROM ( SELECT major, SUM(units) AS totalunits, SUM(gradepoints) AS totalpoints FROM ( SELECT CID, SID, major, units, points, units * points AS gradepoints FROM ( SELECT DISTINCT CID, subject, SID, major, units, grade,  CASE WHEN grade = 'A+' THEN 4.0 WHEN grade = 'A' THEN 4.0 WHEN grade = 'A-' THEN 3.7 WHEN grade = 'B+' THEN 3.3 WHEN grade = 'B' THEN 3.0 WHEN grade = 'B-' THEN 2.7 WHEN grade = 'C+' THEN 2.3 WHEN grade = 'C' THEN 2.0 WHEN grade = 'C-' THEN 1.7 WHEN grade = 'D+' THEN 1.3 WHEN grade = 'D' THEN 1.0 WHEN grade = 'D-' THEN 0.7 WHEN grade = 'F' THEN 0.0 END AS points FROM student NATURAL JOIN studentclasslog NATURAL JOIN course NATURAL JOIN courseinformation WHERE subject = 'ABC') AS test) AS test2 GROUP BY major) AS test3 WHERE totalpoints IS NOT NULL")
    minGPA = cursor.fetchall()
    maxAnswer = []
    minAnswer = []
    maxList = []
    minList = []
    for row in allGPA:
        rowList = list(row)
        for min in minGPA:
            minList = list(min)
            if minList[0] == rowList[1]:
                minList.append(rowList[0])
                minAnswer.append(minList)
        for max in maxGPA:
            maxList = list(max)
            if maxList[0] == rowList[1]:
                maxList.append(rowList[0])
                maxAnswer.append(maxList)
    print "Best Major(s) | Average GPA"
    for row in maxAnswer:
        out = "{:<14}".format(row[1]) + "|" + str(row[0])
        print out
    print "Worst Major(s) | Average GPA"
    for row in minAnswer:
        out = "{:<15}".format(row[1]) + "|" + str(row[0])
        print out
    print "\n"


def problem3G(cursor):
	print "part G"
	countDict = {}
	reverseLargest = []
	cursor.execute("""
	WITH majorChange as (
	    SELECT s1.sid id1,s1.term term ,s1.major major1,s2.term term2, s2.major major2
	        FROM (SELECT sid,major,term FROM Student WHERE major NOT LIKE '%ABC%')  s1,
	             (SELECT sid,major,term FROM Student WHERE major LIKE '%ABC%')  s2
	        WHERE s1.sid = s2.sid AND CAST(s1.term AS INT) < CAST(s2.term AS INT)
	)
	SELECT  DISTINCT id1, major1,major2 FROM majorChange
	ORDER BY major1;""")
	for x in cursor:
		if x[1] not in countDict:
			countDict[x[1]] = 1
		else:
			countDict[x[1]] += 1
	od = collections.OrderedDict(sorted(countDict.items(), key=lambda t: t[1]))

	cursor.execute("""SELECT count(id) FROM (SELECT DISTINCT SID id FROM Student) foo; """) #total number of students
	totalStudents = int(cursor.fetchone()[0])
	totalTransfers = 0
	for x in od:
		reverseLargest.append(x)
	for x in countDict:
		totalTransfers += countDict[x]
	print "\nThe percetage of students who transferred into an ABC major is: %f " % ((float(totalTransfers)/float(totalStudents))*100)
	print "\nThe top 5 most common majors transferred from and their corresponding percentages are as follows: \n"
	for x in range(1,6):
		index = int(-1 * x)
		print str(reverseLargest[index]) + ": " + str((float(countDict[reverseLargest[index]])/float(totalStudents)) *100) + "%"




if __name__ == "__main__":
	conn = psycopg2.connect("dbname='FakeU_Data'")
	quora = conn.cursor()
	problem3A(quora)
	problem3B(quora)
	problem3C(quora)
	problem3E(quora)
	problem3F(quora)
	problem3G(quora)
	#problem3D(quora)
	

	
