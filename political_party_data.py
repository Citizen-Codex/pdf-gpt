import pandas as pd

def get_political_info():

    # read in member data
    #load legislators json data from url
    cur = pd.read_json('https://theunitedstates.io/congress-legislators/legislators-current.json')

    #subset to take keys "name", "bio", and "terms"
    cur = cur[['name','bio','terms']]

    #add start
    congress_start = '2021-01-03'

    legis = pd.DataFrame()

    for x in range(len(cur)):
        ind_terms = cur['terms'][x]
        for y in ind_terms:
            if y['start'] == '2023-01-03' and y['type'] == 'rep':
                #create dict to store results
                results = {
                    'full_name': cur['name'][x]['official_full'],
                    'bday': cur['bio'][x]['birthday'],
                    'gender': cur['bio'][x]['gender'],
                    # 'terms_end': y['start'],
                    'party': y['party'],
                    'state': y['state'],
                    'district': y['district'],
                    'type': y['type']
                    }
                #concat dict results to df
                legis = pd.concat([legis, pd.DataFrame([results])], ignore_index=True)
                break

    #Make district a string. Make sure all number have two digits
    legis['district'] = legis['district'].astype(str)
    legis['district'] = legis['district'].apply(lambda x: x.zfill(2))

    #concat state and district to create district code. Make district a string 
    legis['statedst'] = legis['state'] + legis['district']

    return legis

legis = get_political_info()
