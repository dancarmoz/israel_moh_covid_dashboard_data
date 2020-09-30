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
    {'id': '15', 'queryName': 'CalculatedVerified', 'single': False, 'parameters': {}},
    {'id': '16',
     'queryName': 'deadByAgeAndGenderPublic',
     'single': False,
     'parameters': {'ageSections': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]}},
    {'id': '17',
     'queryName': 'breatheByAgeAndGenderPublic',
     'single': False,
     'parameters': {'ageSections': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]}},
    {'id': '18',
     'queryName': 'severeByAgeAndGenderPublic',
     'single': False,
     'parameters': {'ageSections': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]}}
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
AGES_FNAME = 'ages_dists.csv'
ALL_AGES_FNAMES = {'infected':'ages_dists.csv', 'dead':'deaths_ages_dists.csv',
                   'severe':'severe_ages_dists.csv', 'breathe':'ventilated_ages_dists.csv'}
HOSP_FNAME = 'hospitalized_and_infected.csv'
HOSPITALS_FNAME = 'hospital_occupancy.csv'
HOSP_HEB_FIELD_NAMES = [
    '\xd7\xaa\xd7\xa4\xd7\x95\xd7\xa1\xd7\x94 \xd7\x9b\xd7\x9c\xd7\x9c\xd7\x99\xd7\xaa',
    '\xd7\xaa\xd7\xa4\xd7\x95\xd7\xa1\xd7\xaa \xd7\xa7\xd7\x95\xd7\xa8\xd7\x95\xd7\xa0\xd7\x94',
    '\xd7\xa6\xd7\x95\xd7\x95\xd7\xaa \xd7\x91\xd7\x91\xd7\x99\xd7\x93\xd7\x95\xd7\x93']
ISOLATED_FNAME = 'isolated_staff.csv'

def update_git(new_date):
    assert os.system('git add '+DATA_FNAME) == 0
    assert os.system('git commit -m "Update to %s"'%(new_date)) == 0
    assert os.system('git push') == 0
    print('git committed and pushed successfully')

def update_git_history(new_date):
    history = json.load(file(COMMIT_HIST_FNAME,'r'))
    curr_commit_hash = subprocess.check_output('git log').split()[1]
    history.append((new_date, curr_commit_hash))
    json.dump(history, file(COMMIT_HIST_FNAME,'w'), indent = 2)
    assert os.system('git add '+COMMIT_HIST_FNAME) == 0
    print('updated git history file')
    

def safe_int(x):
    # converts possible None returned by API to 0
    return x if x else 0

def ages_csv_line(data, prefix='infected'):
    date = data['lastUpdate']['lastUpdate']
    ages_dicts = data[prefix + 'ByAgeAndGenderPublic']
    males = [safe_int(sec['male']) for sec in ages_dicts]
    females = [safe_int(sec['female']) for sec in ages_dicts]
    totals = [m+f for m,f in zip(males, females)]
    return ','.join([date]+map(str,totals) + map(str, males) + map(str,females))


def update_ages_csv(data):
    ages_line = ages_csv_line(data)
    prev_file = file(AGES_FNAME, 'r').read()
    new_file = prev_file + ages_line + '\n'
    file(AGES_FNAME, 'w').write(new_file)
    assert os.system('git add ' + AGES_FNAME) == 0

def update_specific_ages_csv(data, prefix):
    fname = ALL_AGES_FNAMES[prefix]
    ages_line = ages_csv_line(data, prefix)
    prev_file = file(fname, 'r').read()
    new_file = prev_file + ages_line + '\n'
    file(fname, 'w').write(new_file)
    assert os.system('git add ' + fname) == 0    
    
def update_all_ages_csvs(data):
    for prefix in ALL_AGES_FNAMES.keys():
        update_specific_ages_csv(data, prefix)

def patients_to_csv_line(pat):
    keys = ['Counthospitalized', 'Counthospitalized_without_release',
            'CountEasyStatus', 'CountMediumStatus',
            'CountHardStatus', 'CountBreath', 'CountDeath',
            'new_hospitalized', 'patients_hotel', 'patients_home']
    return ','.join([pat['date'][:10]]+[str(pat[key]) for key in keys])


def create_patients_csv(data):
    start_date = u'2020-03-02T00:00:00.000Z'
    patients = data['patientsPerDate']
    assert patients[0]['date'] == start_date
    N = len(patients)
    pat_lines = map(patients_to_csv_line, patients)
    
    recs = data['recoveredPerDay'][-N:]
    assert recs[0]['date'] == start_date

    tests = [t for t in data['testResultsPerDate'] if t['positiveAmount']!=-1][-N:]
    assert tests[0]['date'] == start_date
    epi_lines = [','.join(map(str, [t['positiveAmount'],r['amount'],t['amount'],
                                    t['amountVirusDiagnosis']])) for \
                 r, t in zip(recs, tests)]
    
    title_line = ','.join(['Date', 'Hospitalized', 'Hospitalized without release',
                           'Easy', 'Medium', 'Hard', 'Ventilated', 'New deaths',
                           'New hosptialized', 'In hotels', 'At home',
                           'New infected', 'New receovered', 'Total tests',
                           'Tests for idenitifaction'])
    csv_data = '\n'.join([title_line] + [p+','+e for p,e in zip(pat_lines, epi_lines)])
    file(HOSP_FNAME, 'w').write(csv_data+'\n')
    assert os.system('git add '+HOSP_FNAME) == 0    


def extend_hospital_csv(data):
    csv_prev_lines = file(HOSPITALS_FNAME).read().splitlines()
    keys = [k.split(':')[0] for k in csv_prev_lines[0].split(',')[1::3]]
    hosp_dict = dict([(z['name'].encode('utf8').replace('"','').replace("'",""),
                       (z['normalOccupancy'], z['coronaOccupancy'], z['isolatedTeam']))
                      for z in data['hospitalStatus']])
    new_line = [data['lastUpdate']['lastUpdate'].encode('utf8')]
    for k in keys:
        if k in hosp_dict.keys():
            no, co, it = hosp_dict[k]
            if no is None:
                no = 'None'
            else:
                no = '%.2f'%(no)
            new_line.append('%s,%.2f,%d'%(no,co,it))
        else:
                new_line.append(',,')
    a,b,c = HOSP_HEB_FIELD_NAMES
    for k in sorted(list(set(hosp_dict.keys()).difference(set(keys)))):
        csv_prev_lines[0] += ',%s: %s,%s: %s,%s :%s'%(k,a,k,b,k,c)
        for j in range(1,len(csv_prev_lines)):
            csv_prev_lines[j] += ',,,'
        no, co, it = hosp_dict[k]
        if no is None:
            no = 'None'
        else:
            no = '%.2f'%(no)
        new_line.append('%s,%.2f,%d'%(no,co,it))
    csv_prev_lines.append(','.join(new_line))
    file(HOSPITALS_FNAME, 'w').write('\n'.join(csv_prev_lines))
    assert os.system('git add '+HOSPITALS_FNAME) == 0    


def update_isolated_csv(data):
    csv_lines = file(ISOLATED_FNAME).read().splitlines()
    new_line = [data['lastUpdate']['lastUpdate']] + [str(data['isolatedDoctorsAndNurses'][k]) for k in
                 ['Verified_Doctors', 'Verified_Nurses', 'isolated_Doctors', 'isolated_Nurses', 'isolated_Other_Sector']]
    if new_line[1:] == csv_lines[-1].split(',')[1:]: return
    file(ISOLATED_FNAME, 'w').write('\n'.join(csv_lines + [','.join(new_line)]))
    assert os.system('git add '+ISOLATED_FNAME) == 0    

def update_json():
    prev_date = json.load(file(DATA_FNAME,'r'))['lastUpdate']['lastUpdate']
    new_data = get_api_data()
    new_date = new_data['lastUpdate']['lastUpdate']
    if new_date == prev_date:
        print(time.ctime()+': ', 'No update since', prev_date)
        return
    
    print(time.ctime()+': ', 'Data updated! New time:', new_date)
    # update_ages_csv(new_data) # Obsolete
    update_all_ages_csvs(new_data)
    create_patients_csv(new_data)
    # extend_hospital_csv(new_data)
    update_isolated_csv(new_data)
    
    json.dump(new_data, file(DATA_FNAME,'w'), indent = 2)
    update_git(new_date)
    update_git_history(new_date)


    
def update_json_loop():
    while True:
        try:
            update_json()
            time.sleep(60*60 - 4)
        except requests.ConnectionError, e:
            print(e)
            time.sleep(10*60 - 4)
            


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


def get_all_historic_data(start = 0, end = None):
    history = json.load(file(COMMIT_HIST_FNAME,'r'))
    if end == None:
        end = len(history)
    dataa = []
    for i in range(start, end):
        commit_hash = history[i][1]
        assert os.system('git checkout %s -- %s'%(commit_hash, DATA_FNAME)) == 0
        dataa.append(json.load(file(DATA_FNAME,'r')))

    assert os.system('git checkout master -- ' + DATA_FNAME) == 0
    return dataa


def get_age_dist_from_json(data):
    return [sec['male'] + sec['female'] for sec in data['infectedByAgeAndGenderPublic']]
