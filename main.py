import pandas as pd
import sys
import json

# process the csv files and returns a dataframe
def processCsv(filename): 
    df = pd.read_csv(filename, error_bad_lines=False)
    return df

# calculates the weighted average of a student for a certain course and returns a float
def calculateWeightedAvg(final, studentName, className):  
    grades_class = final.loc[(final['name'] == studentName) & (final['class_name'] == className)]    
    if sum(grades_class['weight']) == 100:
        average = grades_class['mark'].multiply(grades_class['weight']/100).sum()
        return average
    return -1
    
# generates the final report
def generateReport(final):
    dic = []
    for student_name in final['name'].drop_duplicates():  
        data = {}
        data["id"] = int(final.loc[(final['name'] == student_name)]['id'].drop_duplicates())
        for class_name in final.loc[(final['name'] == student_name)]['class_name'].drop_duplicates():
            course = {}
            grades = []
            courseAverage = round(calculateWeightedAvg(final, student_name, class_name), 2)
            
            #building the inner layer of the nested dictionary data by filling in information on the courses 
            course["id"] = int(final.loc[(final['class_name'] == class_name)]['course_id'].drop_duplicates())
            course["name"] = class_name
            course["teacher"] = final.loc[final.class_name == class_name, 'teacher'].array[0]
            course["courseAverage"] = courseAverage
            
            grades.append(round(calculateWeightedAvg(final, student_name, class_name), 2))
            
            #edge case in case the total weights of the tests of a course is not equal to 100
            if courseAverage < 0:
                return {"error": "Invalid course weights"} 
            
            #building the outer layer of the nested dictionary by filling in information on the student 
            data["name"] = student_name
            data["totalAverage"] = sum(grades)/len(grades)
            data.setdefault("courses", []).append(course)
        
        dic.append(data) 
    return dic  

if __name__=="__main__":
    coursesF = str(sys.argv[1])
    studentsF = str(sys.argv[2])
    testsF = str(sys.argv[3])
    marksF = str(sys.argv[4])
    output = str(sys.argv[5]) # "output.json" 
    
    courses = processCsv(coursesF) #  "courses.csv"         use these if console arguments do not work
    students = processCsv(studentsF) #  "students.csv"
    tests = processCsv(testsF) # "tests.csv"
    marks = processCsv(marksF) # "marks.csv"
   
    courses = courses.rename(columns={"id": "class_id"})
    courses = courses.rename(columns={"name": "class_name"}) 
    tests = tests.rename(columns={"id": "tests_id"})
    
    # creation of a dataframe "final" which contains all the four csv information for easy access
    temp1 = students.join(marks.set_index('student_id'), on='id')
    temp2 = tests.join(courses.set_index('class_id'), on='course_id')
    final = temp1.join(temp2.set_index('tests_id'), on='test_id')
    
    report = generateReport(final)
    
    # format final report
    formatted_report = {"students": report} 
    formatted_report = json.dumps(formatted_report, sort_keys=False, indent=4)
     
    with open(output, 'w') as f:
        for row in formatted_report:
            f.write(row)
        
    f.close()
    #print(formatted_report) used for testing