from flask import Flask, render_template, request
import pandas as pd
import joblib
import os
import time

app=Flask(__name__)

@app.route('/', methods=['GET','POST'])
def main():
    if request.method=='POST':
        csv_file=request.files['csv_file']
        if csv_file:
            data = pd.read_csv(csv_file)
            threshold = float(request.form.get("percent_threshold")) / 100
            if not (0 <= threshold <= 1):
                return render_template('index.html', error="Invalid threshold: Must be between 0 and 1.")
            model = joblib.load('model.pkl')
            pred = model.predict_proba(data[["Curricular units 2nd sem (approved)", "Curricular units 1st sem (approved)", "Curricular units 2nd sem (grade)", "Course", "Tuition fees up to date"]])
            dropout_prob = pred[:, 0]
            data['Dropout Prediction'] = dropout_prob
            dropout_students = data[data['Dropout Prediction'] >= threshold]
            dropout_students['Dropout Prediction'] = dropout_students['Dropout Prediction'] * 100
            dropout_students.to_csv('dropout_students.csv')
            dropout_students = dropout_students.to_dict('records')
            num_students=len(dropout_students)
            return render_template('results.html', dropout_students=dropout_students, num_students=num_students)
    else:
        return render_template('index.html')
@app.route('/explore_data/<int:student_index>', methods=['GET','POST'])
def explore_data(student_index):
    if request.method=='POST':
        data=pd.read_csv('dropout_students.csv')
        student_data = data.loc[data['index'] == student_index]
        student=student_data.iloc[0].to_dict()
        return render_template("student_info.html", student=student)
    
@app.route('/update_data/<int:student_index>', methods=['GET','POST'])
def update_data(student_index):
    if request.method=='POST':
        curricular_units_2nd_approved = int(request.form.get("Curricular units 2nd sem (approved)"))
        curricular_units_1st_approved = int(request.form.get("Curricular units 1st sem (approved)"))
        curricular_units_2nd_grade = float(request.form.get("Curricular units 2nd sem (grade)"))
        course = request.form.get("Course")
        tuition_fees = int(request.form.get("Tuition fees up to date"))
        student = pd.DataFrame([{
            "Curricular units 2nd sem (approved)": curricular_units_2nd_approved,
            "Curricular units 1st sem (approved)": curricular_units_1st_approved,
            "Curricular units 2nd sem (grade)": curricular_units_2nd_grade,
            "Course": course,
            "Tuition fees up to date": tuition_fees
        }])
        model = joblib.load('model.pkl')
        pred = model.predict_proba(student)
        dropout_prob=pred[:, 0]*100
        dropout_prob=float(dropout_prob)

        return render_template("student_info.html", student={
            "index": student_index,
            "Curricular units 2nd sem (approved)": curricular_units_2nd_approved,
            "Curricular units 1st sem (approved)": curricular_units_1st_approved,
            "Curricular units 2nd sem (grade)": curricular_units_2nd_grade,
            "Course": course,
            "Tuition fees up to date": tuition_fees,
            "Dropout Prediction": dropout_prob
        })
    else:
        return render_template("index.html")



if __name__ == '__main__':
    app.secret_key = '69420'
    app.run(debug=True)