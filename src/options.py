import os
import pickle
import appdirs

pref_dir = appdirs.user_data_dir(appname="SpaceInvaders", appauthor="Los Albatros")

if not os.path.exists(pref_dir):
    os.makedirs(pref_dir)

pref_file = os.path.join(pref_dir, 'preferences.pickle')


def save_pref(params):
    with open(pref_file, 'wb') as f:
        pickle.dump(params, f)


def load_pref():
    try:
        with open(pref_file, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}
