import itertools
import pathlib

from kubernetes import client
from yaml import safe_dump

from seaquest.utils.loggus import init_logger

logger = init_logger(__name__ if __name__ != "__main__" else pathlib.Path(__file__).stem, level="debug")


def _prepare_afinity(job_config: dict) -> client.V1Affinity:
    return client.V1Affinity( # TODO: make this configurable
                node_affinity=client.V1NodeAffinity(
                    required_during_scheduling_ignored_during_execution=client.V1NodeSelector(
                        node_selector_terms=[client.V1NodeSelectorTerm(
                            match_expressions=[client.V1NodeSelectorRequirement(
                                key="nvidia.com/gpu.product",
                                operator="In",
                                values=[job_config["graphics-card"]],
                            )]
                        )]
                    )
                )
            )


def _prepare_containers(config: dict, job_name: str, pvc: str, arguments: dict) -> list[client.V1Container]:
    output_dir_name = arguments["-od"]
    requirements_path = str(pathlib.PurePosixPath(arguments["-md"]).joinpath("requirements.txt"))

    arguments["-od"] = str(pathlib.PurePosixPath("/").joinpath(pvc).joinpath(output_dir_name))
    list_arguments = " ".join(itertools.chain.from_iterable(zip(list(arguments.keys()), list(arguments.values()))))
    
    return [client.V1Container(
                name="program",
                image="iancuonescu/seaquest:latest",
                #image="alpine:latest",
                #image="huggingface/transformers-pytorch-gpu:4.41.2", # TODO: make this configurable
                volume_mounts=[client.V1VolumeMount(
                    name=pvc,
                    mount_path="/{pvc}".format(pvc=pvc)
                )],
                resources=client.V1ResourceRequirements(
                    limits=config["limits"],
                    requests=config["requests"]
                ),
                command=[
                    "/bin/sh",
                    "-c"
                    # 'tail', '-f', '/dev/null'
                ],
                args=[
                    "cd {pvc} && \
                    mkdir {copy_dir} -p && \
                    cp -R {source} {dest} && \
                    rm -R {source} && \
                    mkdir {output_dir} -p && \
                    cd {copy_dir} && \
                    python -m pip install -r {reqs} --no-build-isolation &&\
                    python -m seaquest.runner -cf /{pvc}/{copy_dir}/{source}/runner.yaml {arguments}".format(pvc=pvc, copy_dir=job_name, \
                                                                source=arguments["-md"], dest=job_name, \
                                                                output_dir=output_dir_name, \
                                                                reqs=requirements_path, \
                                                                arguments=list_arguments), # TODO: make this prettier (perhaps a shell script)
                ],
            )]


def _prepare_volumes(pvc: str) -> list[client.V1Volume]:
    return [client.V1Volume(
                name=pvc,
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(pvc)
            )]


def _prepare_job_spec(job_config: dict, job_name: str, pvc: str, arguments: dict) -> client.V1JobStatus:
    return client.V1JobSpec(
        backoff_limit=0, # TODO: make this configurable?
        # ttl_seconds_after_finished = 0, : # TODO: make this configurable
        template=client.V1PodTemplateSpec(
            spec=client.V1PodSpec(
                affinity=_prepare_afinity(job_config) if "graphics-card" in job_config else None,
                containers=_prepare_containers(job_config["resources"], job_name, pvc, arguments),
                volumes=_prepare_volumes(pvc),
                restart_policy="Never"
            )
        )
    )


def _launch_job(api_instance: client.BatchV1Api, namespace: str, job_name:str, job_config: dict, pvc: str, arguments: dict) -> str:
    logger.info("Launching job {job} ...".format(job=job_name))
    
    body = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name, namespace=namespace),
        spec=_prepare_job_spec(job_config, job_name, pvc, arguments),
        status=client.V1JobStatus(), # None?
    )

    api_instance.create_namespaced_job(namespace, body)
    logger.info("Succesfully launched job {job}!".format(job=job_name))


def create_jobs(api_instance: client.BatchV1Api, num_jobs: int, namespace: str, job_config: dict, prefix: str, model_name:str, model_fun: str, pvc: str, model_dir: str, data_file: str) -> list:
    all_created_jobs = []
    for idx in range(num_jobs):
        job_name = "{prefix}-{model}-{fun}-{data_file}-job-{idx}".format(prefix=prefix, model=model_name, fun=model_fun, idx=idx, data_file=data_file)
        job_name = job_name.lower() # kube convention

        arguments = {
            "-od": "{job_name}_output".format(job_name=job_name),
            "-md": model_dir
        }

        try:
            _launch_job(api_instance, namespace, job_name, job_config, pvc, arguments)
        except Exception as e:
            logger.critical("Failed to launch job number {num} due to error {err}".format(num=idx, err=e))
            raise e

        all_created_jobs.append(job_name)

    return all_created_jobs