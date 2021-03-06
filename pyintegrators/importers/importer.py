# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/importers.Importer.ipynb (unless otherwise specified).

__all__ = ['ImporterBase']

# Cell
from ..data.schema import *
class ImporterBase(Importer):
    def __init__(self, importerClass=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def update_progress(pod_client, importer_run, progress, total="total", verbose=True):
        if pod_client is not None:
            importer_run.progress = progress
            pod_client.update_item(importer_run)
        if verbose:
            print(f'PROGRESS: Importing {progress * 100}% of {total} ')

    @staticmethod
    def update_run_status(pod_client, importer_run, status, verbose=True):
        if pod_client is not None:
            importer_run.runStatus = status
            pod_client.update_item(importer_run)
        if verbose:
            print(f"RUN STATUS: {status}")

    @staticmethod
    def update_progress_message(pod_client, importer_run, message, verbose=True):
        if pod_client is not None:
            importer_run.progressMessage = message
            pod_client.update_item(importer_run)
        if verbose:
            print(f"PROGRESS MESSAGE: {message}")