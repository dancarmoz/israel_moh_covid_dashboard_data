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
    {'id': '6', 'queryName': 'isolatedDoctorsAndNurses', 'single': False, 'parameters': {}},
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
     'parameters': {'ageSections': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]}},
    {'id': '19', 'queryName': 'spotlightLastupdate', 'single': False, 'parameters': {}},
    {'id': '20', 'queryName': 'patientsStatus', 'single': False, 'parameters': {}},
    {'id': '21', 'queryName': 'cumSeriusAndBreath', 'single': False, 'parameters': {}},
    {'id': '22', 'queryName': 'LastWeekLabResults', 'single': False, 'parameters': {}},
    {'id': '23', 'queryName': 'verifiedDoctorsAndNurses', 'single': False, 'parameters': {}},
    {'id': '24', 'queryName': 'isolatedVerifiedDoctorsAndNurses', 'single': False, 'parameters': {}},
    {'id': '25', 'queryName': 'spotlightPublic', 'single': False, 'parameters': {}},
    {'id': '26', 'queryName': 'vaccinated', 'single': False, 'parameters': {}},
    {'id': '27', 'queryName': 'vaccinationsPerAge', 'single': False, 'parameters': {}},
    {'id': '28', 'queryName': 'testsPerDate', 'single': False, 'parameters': {}},
    {'id': '29', 'queryName': 'averageInfectedPerWeek', 'single': False, 'parameters': {}},
    {'id': '30', 'queryName': 'spotlightAggregatedPublic', 'single': True, 'parameters': {}},
    {'id': '31', 'queryName': 'HospitalBedStatusSegmentation', 'single': False, 'parameters': {}},
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
VAC_FNAME = 'vaccinated.csv'
VAC_AGES_FNAME = 'vaccinated_by_age.csv'
HOSPITALS_FNAME = 'hospital_occupancy.csv'
HOSP_HEB_FIELD_NAMES = [
    '\xd7\xaa\xd7\xa4\xd7\x95\xd7\xa1\xd7\x94 \xd7\x9b\xd7\x9c\xd7\x9c\xd7\x99\xd7\xaa',
    '\xd7\xaa\xd7\xa4\xd7\x95\xd7\xa1\xd7\xaa \xd7\xa7\xd7\x95\xd7\xa8\xd7\x95\xd7\xa0\xd7\x94',
    '\xd7\xa6\xd7\x95\xd7\x95\xd7\xaa \xd7\x91\xd7\x91\xd7\x99\xd7\x93\xd7\x95\xd7\x93']
ISOLATED_FNAME = 'isolated_staff.csv'

names_trans = {
    'doctors' : u'\u05e8\u05d5\u05e4\u05d0\u05d9\u05dd/\u05d5\u05ea',
    'nurses' : u'\u05d0\u05d7\u05d9\u05dd/\u05d5\u05ea',
    'others' : u'\u05de\u05e7\u05e6\u05d5\u05e2\u05d5\u05ea\n\u05d0\u05d7\u05e8\u05d9\u05dd'}


heb_map = {
    u'\u05e6\u05d4\u05d5\u05d1': 'yellow',
    u'\u05e6\u05d4\u05d5\u05d1 ': 'yellow',
    u'\u05d0\u05d3\u05d5\u05dd': 'red',
    u'\u05d0\u05d3\u05d5\u05dd ': 'red',
    u'\u05db\u05ea\u05d5\u05dd': 'orange',
    u'\u05db\u05ea\u05d5\u05dd ': 'orange',
    u'\u05d9\u05e8\u05d5\u05e7': 'green',
    u'\u05d9\u05e8\u05d5\u05e7 ': 'green',
    u'\u05d0\u05e4\u05d5\u05e8': 'gray',
    u'\u05d0\u05e4\u05d5\u05e8 ': 'gray',
    u' \u05e7\u05d8\u05df \u05de-15 ': '<15'
}

heb_translit = {
    u'\u05d0': 'a',
    u'\u05d1': 'b',
    u'\u05d2': 'g',
    u'\u05d3': 'd',
    u'\u05d4': 'h',
    u'\u05d5': 'v',
    u'\u05d6': 'z',
    u'\u05d7': 'j',
    u'\u05d8': 't',
    u'\u05d9': 'y',
    u'\u05da': 'C',
    u'\u05db': 'c',
    u'\u05dc': 'l',
    u'\u05dd': 'M',
    u'\u05de': 'm',
    u'\u05df': 'N',
    u'\u05e0': 'n',
    u'\u05e1': 's',
    u'\u05e2': 'e',
    u'\u05e3': 'f',
    u'\u05e4': 'p',
    u'\u05e5': 'X',
    u'\u05e6': 'x',
    u'\u05e7': 'q',
    u'\u05e8': 'r',
    u'\u05e9': 'SH',
    u'\u05ea': 'T',
    '"' : '', 
    ' ': '_'
}

def safe_str(s):
    return '%s'%(heb_map.get(s, s))

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
    

def safe_int(x):
    # converts possible None returned by API to 0
    return x if x else 0

def add_line_to_file(fname, new_line):
    prev_file = file(fname, 'r').read()
    new_file = prev_file + new_line + '\n'
    file(fname, 'w').write(new_file)
    assert os.system('git add ' + fname) == 0

def ages_csv_line(data, prefix='infected'):
    date = data['lastUpdate']['lastUpdate']
    ages_dicts = data[prefix + 'ByAgeAndGenderPublic']
    males = [safe_int(sec['male']) for sec in ages_dicts]
    females = [safe_int(sec['female']) for sec in ages_dicts]
    totals = [m+f for m,f in zip(males, females)]
    return ','.join([date]+map(str,totals) + map(str, males) + map(str,females))


def update_ages_csv(data):
    ages_line = ages_csv_line(data)
    add_line_to_file(AGES_FNAME, ages_line)

def update_specific_ages_csv(data, prefix):
    fname = ALL_AGES_FNAMES[prefix]
    ages_line = ages_csv_line(data, prefix)
    add_line_to_file(fname, ages_line)
    
def update_all_ages_csvs(data):
    for prefix in ALL_AGES_FNAMES.keys():
        update_specific_ages_csv(data, prefix)

def update_age_vaccinations_csv(data):
    vac_ages = data['vaccinationsPerAge']
    # Check for surprising age group
    assert len(vac_ages) == 9
    new_line = data['lastUpdate']['lastUpdate']+',' + ','.join(['%d,%d,%d'%(
        g['age_group_population'],g['vaccinated_first_dose'],g['vaccinated_second_dose'])
                                                  for g in vac_ages])
    add_line_to_file(VAC_AGES_FNAME, new_line)

def patients_to_csv_line(pat):
    keys = ['Counthospitalized', 'Counthospitalized_without_release',
            'CountEasyStatus', 'CountMediumStatus', 'CountHardStatus',
            'CountCriticalStatus' ,'CountBreath', 'CountDeath',
            'CountSeriousCriticalCum', 'CountBreathCum', 'CountDeathCum',
            'new_hospitalized', 'serious_critical_new',
            'patients_hotel', 'patients_home',
            ]
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
    tests2 = data['testsPerDate'][-N:]
    assert tests[0]['date'] == tests2[0]['date'] == start_date
    epi_lines = [','.join(map(str, [t['positiveAmount'],r['amount'],t['amount'],
                                    t['amountVirusDiagnosis'],t['amountMagen'],
                                    t2['amountSurvey']])) for \
                 r, t, t2 in zip(recs, tests, tests2)]
    
    title_line = ','.join(['Date', 'Hospitalized', 'Hospitalized without release',
                           'Easy', 'Medium', 'Hard', 'Critical', 'Ventilated', 'New deaths',
                           'Serious (cumu)', 'Ventilated (cumu)', 'Dead (cumu)',
                           'New hosptialized', 'New serious', 'In hotels', 'At home',
                           'New infected', 'New receovered', 'Total tests',
                           'Tests for idenitifaction', 'Tests for Magen', 'Survey tests'])
    csv_data = '\n'.join([title_line] + [p+','+e for p,e in zip(pat_lines, epi_lines)])
    file(HOSP_FNAME, 'w').write(csv_data+'\n')
    assert os.system('git add '+HOSP_FNAME) == 0    


def create_vaccinated_csv(data):
    vac = data['vaccinated']
    title_line = ','.join([
        'Date', 'Vaccinated (daily)','Vaccinated (cumu)','Vaccinated population percentage',
        'Second dose (daily)','Second dose (cumu)','Second dose population precentage'])
    data_lines = [','.join([d['Day_Date'][:10]]+map(str, [
        d['vaccinated'], d['vaccinated_cum'], d['vaccinated_population_perc'],
        d['vaccinated_seconde_dose'], d['vaccinated_seconde_dose_cum'],
        d['vaccinated_seconde_dose_population_perc']])) for d in vac]
    csv_data = '\n'.join([title_line]+data_lines)
    file(VAC_FNAME, 'w').write(csv_data+'\n')
    assert os.system('git add '+VAC_FNAME) == 0


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
    isols = {item['name'] : item['amount'] for item in data['isolatedDoctorsAndNurses']}
    veris = {item['name'] : item['amount'] for item in data['verifiedDoctorsAndNurses']}
    new_line = [data['lastUpdate']['lastUpdate']] + [str(dic[names_trans[k]]) for dic,k in
                 [(isols, 'doctors'),(veris, 'doctors'),
                  (isols, 'nurses'), (veris, 'nurses'),
                  (isols, 'others'), (veris, 'others')]]
##    new_line = [data['lastUpdate']['lastUpdate']] + [str(data['isolatedDoctorsAndNurses'][k]) for k in
##                 ['Verified_Doctors', 'Verified_Nurses', 'isolated_Doctors', 'isolated_Nurses', 'isolated_Other_Sector']]
    if new_line[1:] == csv_lines[-1].split(',')[1:]: return
    file(ISOLATED_FNAME, 'w').write('\n'.join(csv_lines + [','.join(new_line)]))
    assert os.system('git add '+ISOLATED_FNAME) == 0    


city_title_line = ','.join(['Date']+[
    'sickCount', 'actualSick', 'patientDiffPopulationForTenThousands', 'testLast7Days',
    'verifiedLast7Days'] + [
    u'activeSick', u'activeSickTo1000',u'sickTo10000', u'growthLastWeek', u'positiveTests',
    u'score', u'color', u'governmentColor', u'firstDose', u'secondDose'
])

def create_city_line(cpp_ent, spp_ent, date):
    cpp_keys = ['sickCount', 'actualSick', 'patientDiffPopulationForTenThousands', 'testLast7Days',
                'verifiedLast7Days']
    spp_keys = [u'activeSick', u'activeSickTo1000',u'sickTo10000', u'growthLastWeek', u'positiveTests',
                u'score', u'color', u'governmentColor', u'firstDose', u'secondDose']
    line = ','.join([date]+[safe_str(cpp_ent.get(key, '')) for key in cpp_keys] + \
                    [safe_str(spp_ent.get(key, '')) for key in spp_keys])
    return line


def strip_name(name):
    return ''.join([heb_translit.get(c,c) for c in name])

    
def update_cities(new_data):
    date = new_data['lastUpdate']['lastUpdate']
    cd_dict = {a['city'] : a for a in new_data['contagionDataPerCityPublic']}
    sp_dict = {a['name'] : a for a in new_data['spotlightPublic']}
    for n in set(sp_dict.keys())|set(cd_dict.keys()):
        line = create_city_line(cd_dict.get(n, {}), sp_dict.get(n, {}), date)
        fname = 'cities/%s.csv'%(strip_name(n))
        try:
            add_line_to_file(fname, line)
        except IOError:
            # file didn't exist - new city name encountered
            print 'New city!'
            print fname
            file(fname, 'w').write(city_title_line+'\n'+line+'\n')
            assert os.system('git add ' + fname) == 0
            add_line_to_file('cities_transliteration.csv', ('%s,%s'%(n, strip_name(n))).encode('utf-8'))


def update_json():
    prev_date = json.load(file(DATA_FNAME,'r'))['lastUpdate']['lastUpdate']
    new_data = get_api_data()
    new_date = new_data['lastUpdate']['lastUpdate']
    if new_date == prev_date:
        print time.ctime()+': ', 'No update since', prev_date
        return
    
    print time.ctime()+': ', 'Data updated! New time:', new_date
    # update_ages_csv(new_data) # Obsolete
    update_all_ages_csvs(new_data)
    try:
        create_patients_csv(new_data)
    except:
        print 'Exception in patients csv'
    try:
        create_vaccinated_csv(new_data)
    except:
        print 'Exception in vaccination csv'
    # extend_hospital_csv(new_data)
    try:
        update_age_vaccinations_csv(new_data)
    except:
        print 'Exception in vaccination ages csv'
    try:
        update_cities(new_data)
    except:
        print 'Exception in vaccination ages csv'
    update_isolated_csv(new_data)
    
    json.dump(new_data, file(DATA_FNAME,'w'), indent = 2)
    update_git(new_date)
    update_git_history(new_date)


    
def update_json_loop():
    while True:
        try:
            update_json()
            time.sleep(60*60 - 4)
        except Exception, e:
            print e
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
