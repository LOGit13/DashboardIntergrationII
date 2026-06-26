import json
import os

def naechste_user_id(data):
    if data:
        return max(person['id'] for person in data) + 1
    else:
        return 1
    
def naechste_ekg_id(data):
     ekg_ids = [ekg['id'] for person in data for ekg in person['ekg_tests']]
     if ekg_ids:
         return max(ekg_ids) + 1
     else:
         return 1
     
def benutzer_verwaltung(json_file, user_info, update=False):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    user_found = False

    if update:
        for person in data:
            if person['id'] == user_info['id']:
                person.update(user_info)
                user_found = True
                break
        if not user_found:
            raise ValueError("User nicht gefunden.")
    else:
        user_info['id'] = naechste_user_id(data)
        data.append(user_info)

    with open(json_file, 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    json_file = 'data/person_db_test.json'