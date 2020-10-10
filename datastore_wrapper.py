
from google.cloud import datastore
from constants import PROJECT_ID, DATASTORE_DATA_KIND

datastore_client = None


def initialize_datastore_client():
    global datastore_client
    if datastore_client is None:
        datastore_client = datastore.Client(PROJECT_ID)

def save_to_datastore(name, values):
    initialize_datastore_client()
    task_key = datastore_client.key(DATASTORE_DATA_KIND, name)
    task = datastore.Entity(key=task_key)
    for key, value in values.items():
        task[key] = value
    datastore_client.put(task)

def get_from_datastore(name):
    initialize_datastore_client()
    task_key = datastore_client.key(DATASTORE_DATA_KIND, name)
    return datastore_client.get(task_key)