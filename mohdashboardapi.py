import json
import os
import requests
import subprocess
import time

api_query = {'requests': [
    {'id': '0', 'queryName': 'lastUpdate', 'single': True, 'parameters': {}},
    {'id': '1', 'queryName': 'patientsPerDate', 'single': False, 'parameters': {}},
    {'id': '2', 'queryName': 'testResultsPerDate', 'single': False, 'parameters': {}},
    {'id': '3', 'queryName': 'contagionDataPerCityPublic', 'single': False, 'parameters': {}},
    {'id': '4',
     'queryName': 'infectedByAgeAndGenderPublic',
     'single': False,
     'parameters': {'ageSections': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]}},
    {'id': '5', 'queryName': 'hospitalStatus', 'single': False, 'parameters': {}},
    {'id': '6', 'queryName': 'isolatedDoctorsAndNurses', 'single': True, 'parameters': {}},
    {'id': '7', 'queryName': 'otherHospitalizedStaff', 'single': False, 'parameters': {}},
    {'id': '8', 'queryName': 'infectedPerDate', 'single': False, 'parameters': {}},
    {'id': '9', 'queryName': 'updatedPatientsOverallStatus', 'single': False, 'parameters': {}},
    {'id': '10', 'queryName': 'sickPerDateTwoDays', 'single': False, 'parameters': {}},
    {'id': '11', 'queryName': 'sickPerLocation', 'single': False, 'parameters': {}},
    {'id': '12', 'queryName': 'deadPatientsPerDate', 'single': False, 'parameters': {}},
    {'id': '13', 'queryName': 'recoveredPerDay', 'single': False, 'parameters': {}},
    {'id': '14', 'queryName': 'doublingRate', 'single': False, 'parameters': {}},
    ]}
api_address = 'https://datadashboardapi.health.gov.il/api/queries/_batch'
def get_api_data():
    data = requests.post(api_address, json=api_query).json()
    data_dict = {r['queryName']:data[int(r['id'])]['data'] for r in api_query['requests']}
    return data_dict

GIT_DIR = r'C:\GitHub\israel_moh_covid_dashboard_data'
os.chdir(GIT_DIR)
DATA_FNAME = 'moh_dashboard_api_data.json'
COMMIT_HIST_FNAME = 'commit_history.json'

def update_git(new_date):
    assert os.system('git add '+DATA_FNAME) == 0
    assert os.system('git commit -m "Update to %s"'%(new_date)) == 0
    assert os.system('git push') == 0
    print 'git committed and pushed successfully'

def update_git_history(new_date):
    history = json.load(file(COMMIT_HIST_FNAME,'r'))
    curr_commit_hash = subprocess.check_output('git log').split()[1]
    history.append((new_date, curr_commit_hash))
    json.dump(history, file(COMMIT_HIST_FNAME,'w'), indent = 2)
    assert os.system('git add '+COMMIT_HIST_FNAME) == 0
    print 'updated git history file'
    

def update_json():
    prev_date = json.load(file(DATA_FNAME,'r'))['lastUpdate']['lastUpdate']
    new_data = get_api_data()
    new_date = new_data['lastUpdate']['lastUpdate']
    if new_date == prev_date:
        print time.ctime()+': ', 'No update since', prev_date
        return
    
    print time.ctime()+': ', 'Data updated! New time:', new_date
    json.dump(new_data, file(DATA_FNAME,'w'), indent = 2)
    update_git(new_date)
    update_git_history(new_date)

    
def update_json_loop():
    while True:
        update_json()
        time.sleep(60*60 - 4)


def fetch_historic_data(index):
    history = json.load(file(COMMIT_HIST_FNAME,'r'))
    if type(index) == int:
        commit_hash = history[index][1]
    elif type(index) == str:
        commit_hash = dict(history)[index]
    else:
        raise TypeError('argument index of type %s, expected int or str'%(type(index)))

    assert os.system('git checkout %s -- %s'%(commit_hash, DATA_FNAME)) == 0
    data = json.load(file(DATA_FNAME,'r'))
    assert os.system('git checkout master -- ' + DATA_FNAME) == 0

    return data


def get_age_dist_from_json(data):
    return [sec['male'] + sec['female'] for sec in data['infectedByAgeAndGenderPublic']]
