import docker
import os

_docker_client = None


def get_docker_client():
    global _docker_client
    if _docker_client is None:
        _docker_client = docker.from_env()
    return _docker_client


def build_docker_image(name, dockerfile_path):
    try:
        client = get_docker_client()
        image, logs = client.images.build(path=dockerfile_path, tag=name)
        return image
    except Exception as e:
        raise RuntimeError(f"Error building Docker image: {e}")


def run_docker_container(image_name, command=None):
    try:
        client = get_docker_client()
        container = client.containers.run(
            image_name,
            command=command
        )
        return container
    except Exception as e:
        raise RuntimeError(f"Error running Docker container: {e}")


def stop_docker_container(image_name):
    try:
        client = get_docker_client()
        container = client.containers.get(image_name)
        container.stop()
    except docker.errors.NotFound:
        print(f"Container '{image_name}' not found")
    except Exception as e:
        raise RuntimeError(f"Error stopping Docker container: {e}")
