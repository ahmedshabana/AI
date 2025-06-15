#!/usr/bin/env python
# coding: utf-8

# In[1]:


import uuid
from datetime import datetime 
from datetime import timedelta
from requests.auth import HTTPBasicAuth
from requests_ntlm2 import HttpNtlmAuth
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Create authentication object used for the TFS requests
auth = HttpNtlmAuth('aas\\ashabana', 'Esraa@789321')


def activate_iterations(projects, pi_name, start_date, auth=auth):
    """Create PI container and sprint iterations for each project.

    Parameters
    ----------
    projects : list[str]
        List of project names.
    pi_name : str
        Name of the PI iteration container.
    start_date : datetime
        Start date of the first iteration.
    auth : HttpNtlmAuth
        Authentication object used for the API calls.
    """

    for project in projects:
        base_url = (
            f"https://tfs.aas.com.sa/Medad/{project}/_apis/wit/"
            "classificationnodes/Iterations"
        )

        # Create the PI iteration container
        pi_url = f"{base_url}/?api-version=6.0"
        end_date = start_date + timedelta(days=88)
        pi_data = {
            "name": pi_name,
            "attributes": {
                "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "finishDate": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
        response = requests.post(pi_url, json=pi_data, auth=auth)
        print(response, response.text)

        # Prepare to create sprint iterations within the PI container
        iter_url = f"{base_url}/{pi_name}?api-version=6.0"
        iter_start = start_date
        iter_finish = start_date + timedelta(days=18)

        for index in range(1, 7):
            if index == 6:
                iter_name = f"IP iteration-{pi_name}"
            else:
                iter_name = f"iteration {index}-{pi_name}"

            data = {
                "name": iter_name,
                "attributes": {
                    "startDate": iter_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "finishDate": iter_finish.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            }
            iter_resp = requests.post(iter_url, json=data, auth=auth)
            print(iter_resp, iter_resp.text)

            if index == 1:
                iter_start += timedelta(days=21)
                iter_finish += timedelta(days=14)
            else:
                iter_start += timedelta(days=14)
                iter_finish += timedelta(days=14)



  
# Printing random id using uuid1()
print ("The random id using uuid1() is : ",end="")
print (uuid.uuid1())

# In[8]:


#projects =['Medad Knowledge management',
projects =['Medad Artifact','Medad Pass', 'Medad Elearning Integration','Medad TMP','Medad MCS', 'Medad SEP' ,'Medad BAB','Medad Library Portal','Medad LMS', 'Medad ILS','Medad IEP','Medad DAR', 'Medad core','Medad Payment','Medad Services','Medad AI Gateway','Medad Insights']
projects.append('Medad discover') 
projects.append('Medad Edu Edge')
projects.append('Medad Deposit')
projects.append('Medad DevOps')
projects.append('Architecture Team Space')
projects.append('Medad Knowledge management')
projects.append('Medad Releases')
projects.append('Medad Customer Portal')
projects.append('Enterprise AI')
projects.append('UX Team Space')
projects


# In[11]:


projects = ['Medad PI Objectives']


projects2=['Medad Pass']
PI='25-PI 3'

if __name__ == "__main__":
    start = datetime(2025, 6, 1, 0, 0, 0)
    activate_iterations(projects, PI, start)
   


