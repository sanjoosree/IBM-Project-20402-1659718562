import flask
import pickle
import pandas as pd
import numpy as np


from sklearn.preprocessing import StandardScaler

ss = StandardScaler()


genders_to_int = {'MALE':1,
                  'FEMALE':0}

married_to_int = {'YES':1,
                  'NO':0}

education_to_int = {'GRADUATED':1,
                  'NOT GRADUATED':0}

dependents_to_int = {'0':0,
                      '1':1,
                      '2':2,
                      '3+':3}

self_employment_to_int = {'YES':1,
                          'NO':0}                      

property_area_to_int = {'RURAL':0,
                        'SEMIRURAL':1, 
                        'URBAN':2}


import requests

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "dxP1HCGL9lgecETNiZGb7KHLTBHtl66ozvcz999j_ML8"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

app = flask.Flask(__name__, template_folder='templates')
@app.route('/')
def main():
    return (flask.render_template('index.html'))

@app.route('/report')
def report():
    return (flask.render_template('report.html'))

@app.route('/jointreport')
def jointreport():
    return (flask.render_template('jointreport.html'))


@app.route("/Loan_Application", methods=['GET', 'POST'])
def Loan_Application():
    
    if flask.request.method == 'GET':
        return (flask.render_template('Loan_Application.html'))
    
    if flask.request.method =='POST':
        
        #get input
        #gender as string
        genders_type = flask.request.form['genders_type']
        #marriage status as boolean YES: 1 , NO: 0
        marital_status = flask.request.form['marital_status']
        #Dependents: No. of people dependent on the applicant (0,1,2,3+)
        dependents = flask.request.form['dependents']
        
        #dependents = dependents_to_int[dependents.upper()]
        
        #education status as boolean Graduated, Not graduated.
        education_status = flask.request.form['education_status']
        #Self_Employed: If the applicant is self-employed or not (Yes, No)
        self_employment = flask.request.form['self_employment']
        #Applicant Income
        applicantIncome = float(flask.request.form['applicantIncome'] if flask.request.form['applicantIncome'] else 0)
        #Co-Applicant Income
        coapplicantIncome = float(flask.request.form['coapplicantIncome'] if flask.request.form['coapplicantIncome'] else 0)
        #loan amount as integer
        loan_amnt = float(flask.request.form['loan_amnt'] if flask.request.form['loan_amnt'] else 0)
        #term as integer: from 10 to 365 days...
        term_d = int(flask.request.form['term_d'] if flask.request.form['term_d'] else 0)
        # credit_history
        credit_history = int(flask.request.form['credit_history'] if flask.request.form['credit_history'] else 1)
        # property are
        property_area = flask.request.form['property_area']
        #property_area = property_area_to_int[property_area.upper()]

        #create original output dict
        output_dict = dict()
        output_dict['ApplicantIncome'] = applicantIncome
        output_dict['CoapplicantIncome'] = coapplicantIncome
        output_dict['LoanAmount'] = loan_amnt
        output_dict['Loan Amount Term']=term_d
        output_dict['Credit History'] = credit_history
        output_dict['Gender'] = 1 if genders_type=='MALE' else 0
        output_dict['Marital Status'] = 1 if marital_status=='YES' else 0
        output_dict['Education Level'] = 1 if education_status=='GRADUATED' else 0
        output_dict['Dependents_0'] = 1 if dependents=='0' else 0
        output_dict['Dependents_1'] = 1 if dependents=='1' else 0
        output_dict['Dependents_2'] = 1 if dependents=='2' else 0
        output_dict['Dependents_3+'] = 1 if dependents=='3+' else 0
        output_dict['Self Employment'] = 1 if self_employment=='YES' else 0
        output_dict['Property Area Rural'] = 1 if property_area=='RURAL' else 0
        output_dict['Property Area Semirural'] = 1 if property_area=='SEMIRURAL' else 0
        output_dict['Property Area Urban'] = 1 if property_area=='URBAN' else 0

        df = pd.DataFrame([output_dict])
        

        df.ApplicantIncome = np.sqrt(df.ApplicantIncome)
        df.CoapplicantIncome = np.sqrt(df.CoapplicantIncome)
        df.LoanAmount = np.sqrt(df.LoanAmount)

        # print(type(df.values.tolist()))
        # print(df.values.tolist())
        x = df.values.tolist()

        payload_scoring = {"input_data": [{"fields": [['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 'Credit_History', 'Gender', 'Married', 'Education', 'Dependents_0', 'Dependents_1', 'Dependents_2', 'Dependents_3+', 'Self_Employed', 'Property_Area_Rural', 'Property_Area_Semiurban', 'Property_Area_Urban']], "values": x}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/17c96438-9f16-49ea-9f7d-e90409d0e746/predictions?version=2022-11-18', json=payload_scoring,
                            headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        print(response_scoring.json())
        pred = response_scoring.json()['predictions'][0]['values'][0][0]
        print(pred)
        if pred==1:
            res = '🎊🎊Congratulations! your Loan Application has been Approved!🎊🎊'
        else:
                res = '😔😔Unfortunatly your Loan Application has been Denied😔😔'
        

 
        #render form again and add prediction
        return flask.render_template('Loan_Application.html', original_input=output_dict, result=res)
      
if __name__ == '__main__':
    app.run(debug=True)