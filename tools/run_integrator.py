from fastscript import *
import os
from integrators.indexers.indexer import run_integrator


@call_parse
def main(pod_full_address:Param("The pod full address", str)=None,
         integrator_run_uid:Param("Run uid of the integrator to be executed", int)=None,
         database_key:Param("Database key of the pod", str)=None,
         owner_key:Param("Owner key of the pod", str)=None):

    environment = os.environ

    run_integrator(environ=environment, pod_full_address=pod_full_address, integrator_run_uid=integrator_run_uid,
                   database_key=database_key, owner_key=owner_key, verbose=True)