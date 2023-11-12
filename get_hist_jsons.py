import json, os

COMMIT_HIST_FNAME = 'commit_history.json'
DATA_FNAME = 'moh_dashboard_api_data.json'

with open(COMMIT_HIST_FNAME, 'r') as commitfile:
    history = json.load(commitfile)
# print(json.dumps(history, sort_keys=True, indent=4))
for [timestamp, commit_hash] in history:
    print(timestamp, commit_hash)
    assert os.system('git checkout %s -- %s'%(commit_hash, DATA_FNAME)) == 0
    with open(DATA_FNAME, 'r') as oldfile:
        olddata = json.load(oldfile)
        with open('jsons/' + timestamp + '.json', 'w') as jsonfile:
            jsonfile.write(json.dumps(olddata, sort_keys=True, indent=4))
