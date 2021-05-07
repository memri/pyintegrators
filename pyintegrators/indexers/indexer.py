# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/indexers.indexer.ipynb (unless otherwise specified).

__all__ = ['IndexerBase', 'IndexerData', 'get_indexer_run_data', 'test_registration', 'POD_FULL_ADDRESS_ENV',
           'RUN_UID_ENV', 'POD_SERVICE_PAYLOAD_ENV', 'DATABASE_KEY_ENV', 'OWNER_KEY_ENV', 'run_importer',
           'run_integrator_from_run_id', 'run_integrator', 'generate_test_env']

# Cell
from ..data.schema import *
from ..pod.client import PodClient, DEFAULT_POD_ADDRESS
from ..imports import *

# Cell
POD_FULL_ADDRESS_ENV    = 'POD_FULL_ADDRESS'
RUN_UID_ENV             = 'RUN_UID'
POD_SERVICE_PAYLOAD_ENV = 'POD_SERVICE_PAYLOAD'
DATABASE_KEY_ENV        = 'databaseKey'
OWNER_KEY_ENV           = 'ownerKey'


class IndexerBase(Indexer):

    def __init__(self, indexerClass=None, *args, **kwargs):
        if indexerClass is None: indexerClass=self.__class__.__name__
        super().__init__(indexerClass=indexerClass, *args, **kwargs)

    def populate(self, client, items, edges=False):
        new_items = [x for x in items if x.id is None]
        updated_items = [x for x in items if x.id is not None]

        for item in new_items:
            item.update(client, edges=False)

        new_photos = [x for x in new_items if isinstance(x, Photo)]

        for x in new_photos:
            print("uploading photo")
            client.upload_photo(x.data)

        for item in updated_items:
            item.update(client, edges=False)

        if edges:
            for item in new_items + updated_items:
                item.update(client, edges=True)

    def run(self, indexer_run, client):
        data = self.get_data(client, indexer_run)
        items = self.index(data, indexer_run, client)
        self.populate(client, items, edges=True)

class IndexerData():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __repr__(self):
        return f"IndexerData \n{self.__dict__}"


def get_indexer_run_data(client, indexer_run):
    if indexer_run.targetDataType is None:
        raise NotImplementedError
    else:
        return client.search_by_fields({"_type": indexer_run.targetDataType})

def test_registration(integrator):
    """Check whether an integrator is registred. Registration is necessary to be able to load the right indexer
    when retrieving it from the database."""
    import pyintegrators.integrator_registry as registry
    assert integrator.__name__ in dir(registry), f"Add {integrator.__name__} to integrators/integrator_registry.py"

# Cell
# export

def run_importer(importer_run, client):
    from ..integrator_registry import EmailImporter

    importer = importer_run.importer[0]
    # data = indexer.get_data(client, indexer_run)
    temp_importer = EmailImporter()
    temp_importer.run(importer_run, client)
    # indexer.populate(client, updated_items, new_items)

def run_integrator_from_run_id(run_id, client):
    run = client.get(run_id)

    if isinstance(run, IndexerRun):
        indexer = run.indexer[0]
        indexer.run(run, client)
    elif isinstance(run, ImporterRun):
        run_importer(run, client)
    else:
        raise NotImplementedError(f"Cannot execute item of type {run}")

# Cell

def run_integrator(environ=None, pod_full_address=None, integrator_run_id=None, database_key=None, owner_key=None,
                   verbose=False):
    """Runs an integrator, you can either provide the run settings as parameters to this function (for local testing)
    or via environment variables (this is how the pod communicates with integrators)."""
    params = [pod_full_address, integrator_run_id, database_key, owner_key]

    if all([p is None for p in params]):
        try:
            print("Reading run parameters from environment variables")
            pod_full_address    = environ.get(POD_FULL_ADDRESS_ENV, DEFAULT_POD_ADDRESS)
            integrator_run_id  = int(environ[RUN_UID_ENV])
            pod_service_payload = json.loads(environ[POD_SERVICE_PAYLOAD_ENV])

            database_key = pod_service_payload[DATABASE_KEY_ENV]
            owner_key    = pod_service_payload[OWNER_KEY_ENV]

        except KeyError as e:
            print(f"Environmentvariable {e} not found, exiting")
            return
    else:
        assert not (None in params), \
            f"Defined some params to run indexer, but not all. Missing {[p for p in params if p is None]}"
    if verbose:
        for name, val in [("pod_full_address", pod_full_address), ("integrator_run_id", integrator_run_id),
                  ("database_key", database_key), ("owner_key", owner_key)]:
            print(f"{name}={val}")

    client = PodClient(url=pod_full_address, database_key=database_key, owner_key=owner_key)
    run_integrator_from_run_id(integrator_run_id, client)


# Cell
def generate_test_env(client, indexer_run):
    payload = json.dumps({DATABASE_KEY_ENV: client.database_key, OWNER_KEY_ENV: client.owner_key})

    return {POD_FULL_ADDRESS_ENV: DEFAULT_POD_ADDRESS,
            RUN_UID_ENV: indexer_run.id,
            POD_SERVICE_PAYLOAD_ENV: payload}