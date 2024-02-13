from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator

from racetrack_client.utils.quantity import Quantity


class GitManifest(BaseModel, extra='forbid'):
    # URL of git remote: HTTPS, SSH or directory path to a remote repository
    remote: str
    branch: Optional[str] = None
    # subdirectory relative to git repo root
    directory: str = '.'


class DockerManifest(BaseModel, extra='forbid'):
    dockerfile_path: Optional[str] = None


class ResourcesManifest(BaseModel, extra='forbid', arbitrary_types_allowed=True):
    # minimum memory amount in bytes, eg. 256Mi
    memory_min: Optional[Quantity] = None
    # maximum memory amount in bytes, eg. 1Gi
    memory_max: Optional[Quantity] = None
    # minimum CPU consumption in cores, eg. 10m
    cpu_min: Optional[Quantity] = None
    # maximum CPU consumption in cores, eg. 1000m
    cpu_max: Optional[Quantity] = None

    @field_validator('memory_min', 'memory_max', 'cpu_min', 'cpu_max', mode='before')
    @classmethod
    def _quantity_field_must_be_valid(cls, v: str) -> Optional[Quantity]:
        if v is None:
            return None
        return Quantity(str(v))


class Manifest(BaseModel, extra='forbid', arbitrary_types_allowed=True, populate_by_name=True):
    """Job Manifest file - build recipe to get deployable image from source code workspace"""

    # name of the Job Workload
    name: str

    # email address of the Job's owner to reach out
    owner_email: str

    git: GitManifest

    # version of the Job
    version: str = '0.0.1'

    # Jobtype wrapper used to embed model
    jobtype: Optional[str] = None
    lang: Optional[str] = None  # Deprecated

    # relative path to base manifest file, which will be extended by this manifest
    extends: Optional[str] = None

    # Docker-specific configuration
    docker: Optional[DockerManifest] = None

    # type of deployed image: docker image, packer, AMI
    image_type: str = 'docker'

    # system-wide packages that should be installed with apt
    system_dependencies: Optional[List[str]] = None

    # env vars for building
    build_env: Optional[Dict[str, str]] = None
    # env vars for runtime
    runtime_env: Optional[Dict[str, str]] = None
    # secret env vars loaded from an external file applied on building
    secret_build_env_file: Optional[str] = None
    # secret env vars loaded from an external file applied at runtime
    secret_runtime_env_file: Optional[str] = None

    # labels - job metadata for humans
    labels: Optional[Dict[str, Any]] = None

    # list of public job endpoints that can be accessed without authentication
    public_endpoints: Optional[List[str]] = None

    # number of instances of the Job
    replicas: int = 1

    # resources demands to allocate to the Job
    resources: Optional[ResourcesManifest] = None

    # Extra parameters specified by the jobtype
    jobtype_extra: Optional[Dict[str, Any]] = None
    golang: Optional[Dict[str, Any]] = None  # Deprecated
    python: Optional[Dict[str, Any]] = None  # Deprecated
    wrapper_properties: Optional[Dict[str, Any]] = None  # Deprecated

    # Back-end platform where to deploy the service
    infrastructure_target: Optional[str] = None

    # original YAML string from which the manifest was parsed, field for internal use only
    origin_yaml_: Optional[str] = Field(None, exclude=True)

    def get_jobtype(self):
        return self.jobtype if self.jobtype else self.lang

    def get_jobtype_extra(self):
        for field in [self.jobtype_extra, self.golang, self.python, self.wrapper_properties]:
            if field is not None:
                return field
