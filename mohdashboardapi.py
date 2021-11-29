import json
import os
import requests
import subprocess
import time
from collections import defaultdict
try:
    from pprint import pprint as out
except:
    pass

# TODO list:
### a) Fix exception in cities, update format?
###    a1) activeKidsCity - add to other city info?
### b) Add JSON tree tracking
### c) Add "minor version" robsutness

api_query = {'requests': [
    {'id': '0', 'queryName': 'lastUpdate', 'single': True, 'parameters': {}},
    {'id': '1', 'queryName': 'patientsPerDate', 'single': False, 'parameters': {}},
    {'id': '2', 'queryName': 'testResultsPerDate', 'single': False, 'parameters': {}},
    # {'id': '3', 'queryName': 'contagionDataPerCityPublic', 'single': False, 'parameters': {}},
    {'id': '4', 'queryName': 'infectedByPeriodAndAgeAndGender',
     'single': False,  'parameters': {}},
    {'id': '5', 'queryName': 'hospitalStatus', 'single': False, 'parameters': {}},
    # {'id': '6', 'queryName': 'isolatedDoctorsAndNurses', 'single': False, 'parameters': {}},
    {'id': '7', 'queryName': 'otherHospitalizedStaff', 'single': False, 'parameters': {}},
    {'id': '8', 'queryName': 'infectedPerDate', 'single': False, 'parameters': {}},
    {'id': '9', 'queryName': 'updatedPatientsOverallStatus', 'single': False, 'parameters': {}},
    {'id': '10', 'queryName': 'sickPerDateTwoDays', 'single': False, 'parameters': {}},
    {'id': '11', 'queryName': 'sickPatientPerLocation', 'single': False, 'parameters': {}},
    {'id': '12', 'queryName': 'deadPatientsPerDate', 'single': False, 'parameters': {}},
    # {'id': '13', 'queryName': 'recoveredPerDay', 'single': False, 'parameters': {}},
    # {'id': '14', 'queryName': 'doublingRate', 'single': False, 'parameters': {}},
    # {'id': '15', 'queryName': 'CalculatedVerified', 'single': False, 'parameters': {}},
    {'id': '16',
     'queryName': 'deadByPeriodAndAgeAndGender',
      'single': False,  'parameters': {}},
    {'id': '17',
     'queryName': 'breatheByPeriodAndAgeAndGender',
     'single': False,  'parameters': {}},
    {'id': '18',
     'queryName': 'severeByPeriodAndAgeAndGender',
     'single': False,  'parameters': {}},
    {'id': '19', 'queryName': 'spotlightLastupdate', 'single': False, 'parameters': {}},
    {'id': '20', 'queryName': 'patientsStatus', 'single': False, 'parameters': {}},
    # {'id': '21', 'queryName': 'cumSeriusAndBreath', 'single': False, 'parameters': {}},
    # {'id': '22', 'queryName': 'LastWeekLabResults', 'single': False, 'parameters': {}},
    # {'id': '23', 'queryName': 'verifiedDoctorsAndNurses', 'single': False, 'parameters': {}},
    {'id': '24', 'queryName': 'isolatedVerifiedDoctorsAndNurses', 'single': False, 'parameters': {}},
    {'id': '25', 'queryName': 'spotlightPublic', 'single': False, 'parameters': {}},
    {'id': '26', 'queryName': 'vaccinated', 'single': False, 'parameters': {}},
    {'id': '27', 'queryName': 'vaccinationsPerAge', 'single': False, 'parameters': {}},
    {'id': '28', 'queryName': 'testsPerDate', 'single': False, 'parameters': {}},
    {'id': '29', 'queryName': 'averageInfectedPerWeek', 'single': False, 'parameters': {}},
    {'id': '30', 'queryName': 'spotlightAggregatedPublic', 'single': True, 'parameters': {}},
    {'id': '31', 'queryName': 'HospitalBedStatusSegmentation', 'single': False, 'parameters': {}},
    {'id': '32', 'queryName': 'infectionFactor', 'single': False, 'parameters': {}},
    # {'id': '33', 'queryName': 'vaccinatedVerifiedDaily', 'single': False, 'parameters': {'days': 0}},
    # {'id': '34', 'queryName': 'vaccinatedVerifiedByAge', 'single': False, 'parameters': {}},
    {'id': '35', 'queryName': 'researchGraph', 'single': False, 'parameters': {}},
    {'id': '36', 'queryName': 'tileDisplay', 'single': False, 'parameters': {}},
    {'id': '37', 'queryName': 'deathVaccinationStatusDaily', 'single': False, 'parameters': {}},
    {'id': '38', 'queryName': 'SeriousVaccinationStatusDaily', 'single': False, 'parameters': {}},
    {'id': '39', 'queryName': 'VerfiiedVaccinationStatusDaily', 'single': False, 'parameters': {}},
    {'id': '40', 'queryName': 'VaccinationStatusAgg', 'single': False, 'parameters': {}},
    {'id': '41', 'queryName': 'arrivingAboardCountry', 'single': False, 'parameters': {}},
    {'id': '42', 'queryName': 'arrivingAboardDaily', 'single': False, 'parameters': {}},
    {'id': '43', 'queryName': 'positiveArrivingAboardDaily', 'single': False, 'parameters': {}},
    {'id': '44', 'queryName': 'hardPatient', 'single': True, 'parameters': {}},
    {'id': '45', 'queryName': 'hospitalizationStatusDaily', 'single': False, 'parameters': {}},
    {'id': '46', 'queryName': 'summaryLast7Days', 'single': True, 'parameters': {}},
    {'id': '47', 'queryName': 'hospVaccinationDuration', 'single': False, 'parameters': {}},
    {'id': '48', 'queryName': 'testedByAge', 'single': False, 'parameters': {}},
    {'id': '49', 'queryName': 'activeKidsSickCityPublic', 'single': False, 'parameters': {}},
    {'id': '50', 'queryName': 'verifiedKidsAgeDaily', 'single': False, 'parameters': {}},
    {'id': '51', 'queryName': 'isolatedKidsAgeDaily', 'single': False, 'parameters': {}},
    {'id': '52', 'queryName': 'sickReturnsAgeVaccination', 'single': False, 'parameters': {}},
    {'id': '53', 'queryName': 'dailyReturnSick', 'single': False, 'parameters': {}},
]}

api_address = 'https://datadashboardapi.health.gov.il/api/queries/_batch'
def get_api_data():
    data = requests.post(api_address, json=api_query).json()
    data_dict = {
        r['queryName']:(data[i]['data'] if 'data' in data[i] else None)
        for i, r in enumerate(api_query['requests'])}
    return data_dict

GIT_DIR = r'C:\GitHub\israel_moh_covid_dashboard_data'
os.chdir(GIT_DIR)
DATA_FNAME = 'moh_dashboard_api_data.json'
COMMIT_HIST_FNAME = 'commit_history.json'
##AGES_FNAME = 'ages_dists.csv'
ALL_AGES_FNAMES = {'infected':'ages_dists.csv', 'dead':'deaths_ages_dists.csv',
                   'severe':'severe_ages_dists.csv', 'breathe':'ventilated_ages_dists.csv'}
ALL_AGES_FNAMES_V2 = {'infected':'ages_dists_v2.csv', 'dead':'deaths_ages_dists_v2.csv',
                   'severe':'severe_ages_dists_v2.csv', 'breathe':'ventilated_ages_dists_v2.csv'}
HOSP_FNAME = 'hospitalized_and_infected.csv'
VAC_FNAME = 'vaccinated.csv'
VAC_AGES_FNAME = 'vaccinated_by_age.csv'
VAC_CASES_DAILY = 'cases_by_vaccination_daily.csv'
VAC_CASES_DAILY_ABS = 'cases_by_vaccination_daily_absolute.csv'
VAC_CASES_DAILY_NORM = 'cases_by_vaccination_daily_normalized.csv'
VAC_CASES_AGES = 'cases_by_vaccination_ages.csv'
HOSPITALS_FNAME = 'hospital_occupancy.csv'
HOSP_HEB_FIELD_NAMES = [
    '\xd7\xaa\xd7\xa4\xd7\x95\xd7\xa1\xd7\x94 \xd7\x9b\xd7\x9c\xd7\x9c\xd7\x99\xd7\xaa',
    '\xd7\xaa\xd7\xa4\xd7\x95\xd7\xa1\xd7\xaa \xd7\xa7\xd7\x95\xd7\xa8\xd7\x95\xd7\xa0\xd7\x94',
    '\xd7\xa6\xd7\x95\xd7\x95\xd7\xaa \xd7\x91\xd7\x91\xd7\x99\xd7\x93\xd7\x95\xd7\x93']
ISOLATED_FNAME = 'isolated_staff.csv'
ABROAD_FNAME = 'from_abroad.csv'
KIDS_AGES_DAILY = 'kids_ages_daily.csv'
AGE_TESTS_FNAME = 'tests_by_age.csv'
SICK_RETS_AGES_FNAME = 'reinfected_by_age.csv'

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
    print 'committing...',
    assert os.system('git commit -m "Update to %s"'%(new_date)) == 0
    print 'pushing...'
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
    ages_dicts = data[prefix + 'ByPeriodAndAgeAndGender']
    period = u'\u05de\u05ea\u05d7\u05d9\u05dc\u05ea \u05e7\u05d5\u05e8\u05d5\u05e0\u05d4'
    secs = [ent for ent in ages_dicts if ent['period'] == period]
    assert ''.join([s['section'][0] for s in secs]) == '0123456789'
##    assert [s['section'] for s in secs] == [
##        '0-9', '10-11', '12-15', '16-19', '20-29', '30-39',
##        '40-49', '50-59', '60-69', '70-74', '75+']
    males = [safe_int(sec['male']['amount']) for sec in secs]
    females = [safe_int(sec['female']['amount']) for sec in secs]
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
    assert len(vac_ages) == 11
    new_line = data['lastUpdate']['lastUpdate']+','*10 + ','.join([('%d,'*3 +'%.1f,'*6)[:-1]%(
        g['vaccinated_first_dose'],g['vaccinated_second_dose'],g['vaccinated_third_dose'],
        g['percent_vaccinated_first_dose'],g['persent_vaccinated_second_dose'],
        g['persent_vaccinated_third_dose'],g['not_vaccinated_amount_perc'],
        g['vaccinated_amount_perc'], g['vaccinated_expired_amount_perc'])
        for g in vac_ages])
    add_line_to_file(VAC_AGES_FNAME, new_line)

def update_age_vaccinations_csv_old_ver(data):
    vac_ages = data['vaccinationsPerAge']
    # Check for surprising age group
    assert len(vac_ages) == 10
    new_line = data['lastUpdate']['lastUpdate']+','*5 + ','.join(['%d,%d,%d,%d'%(
        g['age_group_population'],g['vaccinated_first_dose'],
        g['vaccinated_second_dose'],g['vaccinated_third_dose'])
        for g in vac_ages])
    add_line_to_file(VAC_AGES_FNAME, new_line)

def update_age_tests_csv(data):
    test_ages = [x for x in data['testedByAge'] if x['period_desc']=='All']
    assert ''.join([s['age_group'][0] for s in test_ages]) == '0123456789'
    new_line = data['lastUpdate']['lastUpdate'] + ',' +','.join(
        str(s[item]) for item in ['count_testeds', 'positive_testeds'] for s in test_ages)
    add_line_to_file(AGE_TESTS_FNAME, new_line)

def update_sick_returns_ages_csv(data):
    srages = [x for x in data['sickReturnsAgeVaccination'] if x['period']=='All']
    assert [s['ageGroup'] for s in srages] == [
        '5-11', '12-15', '16-19', '20-29', '30-39',
        '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
    new_line = data['lastUpdate']['lastUpdate'] + ',' +','.join(
        str(s[item]) for item in ['sickReturnsVaccinated', 'sickReturnsNotVaccinated']
        for s in srages)
    add_line_to_file(SICK_RETS_AGES_FNAME, new_line)




def patients_to_csv_line(pat):
    keys = ['Counthospitalized', 'Counthospitalized_without_release',
            'CountEasyStatus', 'CountMediumStatus', 'CountHardStatus',
            'CountCriticalStatus' ,'CountBreath', 'count_ecmo', 'CountDeath',
            'CountSeriousCriticalCum', 'CountBreathCum', 'CountDeathCum',
            'new_hospitalized', 'serious_critical_new',
            'patients_hotel', 'patients_home',
            ]
    return str(','.join([pat['date'][:10]]+[str(pat[key]) for key in keys]))


def create_patients_csv(data):
    start_date = u'2020-03-02T00:00:00.000Z'
    patients = sorted(data['patientsPerDate'], key = lambda x: x['date'])
    assert patients[0]['date'] == start_date
    N = len(patients)
    # Sometimes the json contains multiple entires... argh
    if len(set([p['date'] for p in patients])) != N:
        rev_pat_dates = [p['date'] for p in patients[::-1]]
        pat_dates_fil = sorted(set(rev_pat_dates))
        patients = [patients[N-1-rev_pat_dates.index(date)] for date in pat_dates_fil]
        N = len(patients)       
    
    pat_lines = map(patients_to_csv_line, patients)
    
    # recs = data['recoveredPerDay'][-N:]
    inf = data['infectedPerDate'][-N:]
    assert inf[0]['date'] == start_date

    tests = [t for t in data['testResultsPerDate'] if t['positiveAmount']!=-1][-N:]
    tests2 = data['testsPerDate'][-N:]
    rets = data['dailyReturnSick'][-N:]
    assert tests[0]['date'] == tests2[0]['date'] == rets[0]['date'] == start_date

    epi_lines = [','.join(map(str, [t['positiveAmount'], i['sum'],
                                    i['amount'], i['recovered'],
                                    t['amount'], t['amountVirusDiagnosis'],
                                    t['amountPersonTested'], t['amountMagen'],
                                    t2['numAntigenOfficialTest'],
                                    r['verifiedReturnsVaccinated'],
                                    r['verifiedReturnsNotVaccinated'],
                                    r['verifiedReturnsCumPerc']
                                    ])) for \
                 i, t, t2, r in zip(inf, tests, tests2, rets)]

    inff = data['infectionFactor']
    def repr_if_not_none(x):
        if x is None: return ''
        return repr(x)
    inff_dict = {i['day_date']:repr_if_not_none(i['R']) for i in inff}
    inff_lines = [inff_dict.get(p['date'], '') for p in patients]

    def utf_if_not_none(x):
        if x is None: return ''
        return x.encode('utf8')
    event_lines = [utf_if_not_none(i['coronaEvents']) for i in inf]
    
    title_line = ','.join(['Date', 'Hospitalized', 'Hospitalized without release',
                           'Easy', 'Medium', 'Hard', 'Critical', 'Ventilated',
                           'ECMO', 'New deaths',
                           'Serious (cumu)', 'Ventilated (cumu)', 'Dead (cumu)',
                           'New hosptialized', 'New serious', 'In hotels', 'At home',
                           
                           'Positive results', 'Total infected', 'New infected',
                           'New receovered', 'Total tests', 'Tests for idenitifaction',
                           'People tested', 'Tests for Magen', 'Official antigen tests',
                           'Vaccinated reinfected', 'Unvaccinated reinfected',
                           'Reinfected cumulative percentage',
                           'Official R', 'Epidemiological Event'])
    csv_data = '\n'.join([title_line] + [
        ','.join([p,e,i,ev]) for p,e,i,ev in zip(pat_lines, epi_lines, inff_lines, event_lines)])
    file(HOSP_FNAME, 'w').write(csv_data+'\n')
    assert os.system('git add '+HOSP_FNAME) == 0


def simulate_vvd(data):
    dailys = [data[pre + 'VaccinationStatusDaily'] for pre in ['death', 'Serious', 'Verfiied']]
    assert len(set([tuple([x['day_date'] for x in d]) for d in dailys])) == 1
    assert len(set([tuple([x['age_group'] for x in d]) for d in dailys])) == 1
    merged = [dict(x.items()+y.items()+z.items()) for x,y,z in zip(*dailys)]
##    for m in merged:
##        m.update({s.lower():m[s] for s in [
##            'new_Serious_amount_boost_vaccinated', 'new_Serious_boost_vaccinated_normalized']})
##        m.update({
##            'death_boost_vaccinated_normalized':m['death_amount_boost_vaccinated_normalized']})
    return merged

def create_cases_by_vaccinations_absolute(data):
    res = ',' + ',,,'.join([
        pre + ' - ' + suf
        for pre in ['All ages', 'Above 60', 'Below 60']
        for suf in [
            'Daily verified', 'Total serious', 'New serious', 'Total deaths']
        ]) + ','*2 + '\n'
    res += 'Date'+',Recently vaccinated,Expired vaccinated,Not vaccinated'*12+'\n'
    vvd = simulate_vvd(data)
    vacc_types = ['vaccinated', 'expired', 'not_vaccinated']
    case_types = ['verified', 'serious', 'new_serious', 'death']
    for i in range(0, len(vvd), 3):
        s = sorted(vvd[i:i+3], key=lambda x: x['age_group'])
        assert s[0]['day_date'] == s[1]['day_date'] == s[2]['day_date']
        line = s[0]['day_date'] + ',' + ','.join([
            str(ss[case_type + '_amount_' + vacc_type])
            for ss in s for case_type in case_types for vacc_type in vacc_types])
        res += line + '\n'
    file(VAC_CASES_DAILY_ABS, 'w').write(res)
    assert os.system('git add '+VAC_CASES_DAILY_ABS) == 0

def create_cases_by_vaccinations_normalized(data):
    res = ',' + ',,,'.join([
        pre + ' - ' + suf
        for pre in ['All ages', 'Above 60', 'Below 60']
        for suf in [
            'Daily verified', 'Total serious', 'New serious', 'Total deaths']
        ]) + ','*2 + '\n'
    res += 'Date'+',Recently vaccinated,Expired vaccinated,Not vaccinated'*12+'\n'
    vvd = simulate_vvd(data)
    vacc_types = ['vaccinated', 'expired', 'not_vaccinated']
    case_types = ['verified', 'serious', 'new_serious', 'death']
    for i in range(0, len(vvd), 3):
        s = sorted(vvd[i:i+3], key=lambda x: x['age_group'])
        assert s[0]['day_date'] == s[1]['day_date'] == s[2]['day_date']
        line = s[0]['day_date'] + ',' + ','.join([
            str(ss[case_type + '_' + vacc_type + '_normalized'])
            for ss in s for case_type in case_types for vacc_type in vacc_types])
        res += line + '\n'
    file(VAC_CASES_DAILY_NORM, 'w').write(res)
    assert os.system('git add '+VAC_CASES_DAILY_NORM) == 0


def create_cases_by_vaccinations_daily_old_old(data):
##    res = ',' + (','*9).join(['All ages', 'Above 60', 'Below 60']) + ','*8 + '\n'
    res = ',' + ',,,,,'.join([pre+' - '+suf
                            for pre in ['All ages', 'Above 60', 'Below 60']
                            for suf in [
                                'booster vaccinated', 'fully vaccinated',
                                'partially vaccinated', 'not vaccinated']
                            ]) + ','*4 + '\n'
    res += 'Date' + ',Total Amount,Daily verified,Total serious,New serious,Total deaths'*12 + '\n'
    vvd = data['vaccinatedVerifiedDaily']
    vacc_types = ['boost_vaccinated', 'vaccinated', 'vaccinated_procces', 'not_vaccinated']
    case_types = ['%s_amount_cum', 'verified_amount_%s', 'Serious_amount_%s',
                 'New_Serious_amount_%s', 'Death_amount_%s']
    for i in range(0, len(vvd), 3):
        s = sorted(vvd[i:i+3], key=lambda x: x['age_group'])
        assert s[0]['day_date'] == s[2]['day_date'] == s[2]['day_date']
        line = s[0]['day_date']+','
        line += ','.join([
            str(ss[case_type%vacc_type])
            for ss in s for vacc_type in vacc_types for case_type in case_types])
        res += line + '\n'
    file(VAC_CASES_DAILY, 'w').write(res)
    assert os.system('git add '+VAC_CASES_DAILY) == 0

def create_cases_by_vaccinations_absolute_old(data):
    res = ',' + ',,,,'.join([
        pre + ' - ' + suf
        for pre in ['All ages', 'Above 60', 'Below 60']
        for suf in [
            'Total population', 'Daily verified', 'Total serious', 'New serious', 'Total deaths']
        ]) + ','*3 + '\n'
    res += 'Date'+',Booster vaccinated,Fully vaccinated,Partially vaccinated,Not vaccinated'*15+'\n'
    vvd = data['vaccinatedVerifiedDaily']
    vacc_types = ['boost_vaccinated', 'vaccinated', 'vaccinated_procces', 'not_vaccinated']
    case_types = ['verified', 'Serious', 'New_Serious', 'Death']
    for i in range(0, len(vvd), 3):
        s = sorted(vvd[i:i+3], key=lambda x: x['age_group'])
        assert s[0]['day_date'] == s[1]['day_date'] == s[2]['day_date']
        line = s[0]['day_date']
        for ss in s:
            line += ',' + ','.join([str(ss[vacc_type+'_amount_cum']) for vacc_type in vacc_types])
            line += ',' + ','.join([
                str(ss[case_type + '_amount_' + vacc_type])
                for case_type in case_types for vacc_type in vacc_types])
        res += line + '\n'
    file(VAC_CASES_DAILY_ABS, 'w').write(res)
    assert os.system('git add '+VAC_CASES_DAILY_ABS) == 0

def safe_normalize(cases, population):
    if cases is None or population is None: return None
    if cases == population == 0: return 0
    return cases*100000./population

def create_cases_by_vaccinations_normalized_old(data):
    res = ',' + ',,,,'.join([
        pre + ' - ' + suf
        for pre in ['All ages', 'Above 60', 'Below 60']
        for suf in [
            'Total population', 'Daily verified', 'Total serious', 'New serious', 'Total deaths']
        ]) + ','*3 + '\n'
    res += 'Date'+',Booster vaccinated,Fully vaccinated,Partially vaccinated,Not vaccinated'*15+'\n'
    vvd = data['vaccinatedVerifiedDaily']
    vacc_types = ['boost_vaccinated', 'vaccinated', 'vaccinated_procces', 'not_vaccinated']
    case_types = ['verified', 'Serious', 'New_Serious', 'Death']
    for i in range(0, len(vvd), 3):
        s = sorted(vvd[i:i+3], key=lambda x: x['age_group'])
        assert s[0]['day_date'] == s[1]['day_date'] == s[2]['day_date']
        line = s[0]['day_date']
        for ss in s:
            line += ',' + ','.join([str(ss[vacc_type+'_amount_cum']) for vacc_type in vacc_types])
            line += ',' + ','.join([
                str(safe_normalize(
                    ss[case_type + '_amount_' + vacc_type], ss[vacc_type + '_amount_cum']))
                for case_type in case_types for vacc_type in vacc_types])
        res += line + '\n'
    file(VAC_CASES_DAILY_NORM, 'w').write(res)
    assert os.system('git add '+VAC_CASES_DAILY_NORM) == 0


def update_cases_by_vaccinations_ages(data):
    date = data['lastUpdate']['lastUpdate']
    vvba = data['VaccinationStatusAgg']
    new_line = date+',' + ','.join([
        str(ss[case_type%vacc_type])
        for case_type in [
            'active_amount_%s', 'active_%s_normalized', 'serious_amount_%s', 'serious_%s_normalized']
        for ss in vvba
        for vacc_type in ['vaccinated', 'vaccinated_expired', 'not_vaccinated']])
    add_line_to_file(VAC_CASES_AGES, new_line)


def update_cases_by_vaccinations_ages_old(data):
    date = data['lastUpdate']['lastUpdate']
    vvba = data['vaccinatedVerifiedByAge']
    new_line = date+',' + ','.join([
        str(ss[case_type%vacc_type])
        for ss in vvba
        for vacc_type in ['vaccinated', 'vaccinated_procces', 'not_vaccinated']
        for case_type in ['%s_amount_cum', 'Active_amount_%s', 'Serious_amount_%s']])
    add_line_to_file(VAC_CASES_AGES, new_line)

def create_kids_ages_daily(data):
    isols, vers = data['isolatedKidsAgeDaily'], data['verifiedKidsAgeDaily']
    N = min(len(isols), len(vers))
    isols, vers = isols[-N:], vers[-N:]
    assert all([i['dayDate']==v['dayDate'] for i,v in zip(isols,vers)])
    lines = 'Date,' + ','.join(
        age + ' ' + suf
        for suf in ['verified', 'verified normalized', 'isolated', 'isolated normalized']
        for age in ['0-4', '5-11', '12-15', '16-19']) + '\n'
    for i in range(0, N, 4):
        line = vers[0]['dayDate'][:10]+','+','.join(
            str(arr[j][item]) for arr,item in [
                (vers, 'verified'), (vers, 'verifiedNormalized'),
                (isols, 'isolated'), (isols, 'isolatedNormalized')]
            for j in range(i, i+4) )
        lines += line + '\n'
    file(KIDS_AGES_DAILY, 'w').write(lines)
    assert os.system('git add '+KIDS_AGES_DAILY) == 0



def create_abroad_csv(data):
    inc, pos = data['arrivingAboardDaily'], data['positiveArrivingAboardDaily']
    dates = sorted(set([i['date'] for i in inc]))
    all_co=u'\u05db\u05dc\u05dc \u05d4\u05de\u05d3\u05d9\u05e0\u05d5\u05ea'
    countries = sorted(set([i['visited_country'] for i in inc]),
                       key=lambda x:(x if x!=all_co else ''))
    c2data = {c : {d : (0,0,0,0,0,0) for d in dates} for c in countries}
    for  i, p in zip(inc, pos):
        c,d = i['visited_country'], i['date']
        assert (c,d) == (p['visited_country'], p['date'])
        c2data[c][d] = (
            # p['positive_None_vaccination_ind'], p['positive_Vaccination_ind'],
            i['none_vaccination_ind'], i['vaccination_ind'],
            p['israeli_positive'], p['foreigner_positive'],
            p['israeli_percnet_positive'], p['foreigner_percnet_positive'])
##    for d in dates:
##        c2data['Total'][d] = tuple(map(sum,zip(*[c2data[c][d] for c in countries[1:]])))

    lines = ','+',,,,,,'.join(countries)+',,,,,' + '\n'
    lines += 'Date' + \
             ',Incoming non-vacc,Incoming vacc,Positive Israeli'\
             ',Positive foreign,Positive Israeli perc,Positive foreign perc'*len(countries) + '\n'
    lines += '\n'.join([
        ','.join([d] + ['%d,%d,%d,%d,%.1f,%.1f'%(c2data[c][d]) for c in countries]) for d in dates]) + '\n'
    file(ABROAD_FNAME, 'w').write(lines.encode('utf8'))
    assert os.system('git add '+ABROAD_FNAME) == 0
        
def create_vaccinated_csv(data):
    vac = data['vaccinated']
    title_line = ','.join([
        'Date',
        'Vaccinated (daily)','Vaccinated (cumu)','Vaccinated population percentage',
        'Second dose (daily)','Second dose (cumu)','Second dose population precentage',
        'Third dose (daily)','Third dose (cumu)','Third dose population precentage'])
    data_lines = [','.join([d['Day_Date'][:10]]+map(str, [
        d['vaccinated'], d['vaccinated_cum'], d['vaccinated_population_perc'],
        d['vaccinated_seconde_dose'], d['vaccinated_seconde_dose_cum'],
        d['vaccinated_seconde_dose_population_perc'],
        d['vaccinated_third_dose'], d['vaccinated_third_dose_cum'],
        d['vaccinated_third_dose_population_perc'],
        ])) for d in vac]
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
    isolveris = {item['name'] : item['amount'] for item in data['isolatedVerifiedDoctorsAndNurses']}
    # veris = {item['name'] : item['amount'] for item in data['verifiedDoctorsAndNurses']}
    new_line = [data['lastUpdate']['lastUpdate']] + [str(isolveris[names_trans[k]]) for k in
                 ['doctors', 'nurses', 'others']]
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


def get_json_tree(data):
    pass

def try_func(func, pref, name, data):
    try:
        print pref + ' ' + name
        func(data)
    except:
        print 'Exception in ' + name


def update_json():
    prev_date = json.load(file(DATA_FNAME,'r'))['lastUpdate']['lastUpdate']
    new_data = get_api_data()
    new_date = new_data['lastUpdate']['lastUpdate']
    if new_date == prev_date:
        print time.ctime()+': ', 'No update since', prev_date
        return
    
    print time.ctime()+': ', 'Data updated! New time:', new_date
    # update_ages_csv(new_data) # Obsolete
    try_func(update_all_ages_csvs, 'updating', 'ages csvs', new_data)
    try_func(create_patients_csv, 'creating', 'patients csv', new_data)
    try_func(create_vaccinated_csv, 'creating', 'vaccinated csv', new_data)
    try_func(update_age_vaccinations_csv, 'updating', 'vaccination ages csvs', new_data)
    try_func(create_cases_by_vaccinations_absolute,
             'creating', 'cases by vaccinations daily absolute csv', new_data)
    try_func(create_cases_by_vaccinations_normalized,
             'creating', 'cases by vaccinations daily normalized csv', new_data)
    try_func(update_cases_by_vaccinations_ages,
             'updating', 'cases by vaccinations ages csvs', new_data)
    try_func(create_abroad_csv, 'creating', 'incomings/cases from abroad csv', new_data)
    try_func(update_age_tests_csv, 'updating', 'tests by age csv', new_data)
    try_func(update_sick_returns_ages_csv, 'updating', 'reinfected by age csv', new_data)
    try_func(create_kids_ages_daily, 'creating', 'infected kids ages csv', new_data)

    # These are broken, but no harm running them. cities should be fixed at some point
    try_func(update_cities, 'updating', 'cities csvs', new_data)
    try_func(update_isolated_csv, 'updating', 'isolated csvs', new_data)


    # extend_hospital_csv(new_data) # Broken long ago
    
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
            if type(e) is ValueError and e.message == "No JSON object could be decoded":
                time.sleep(10)
            else:
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
