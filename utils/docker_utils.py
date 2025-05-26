import docker
import os

_docker_client = None

# Docker Registry configuration
DOCKER_REGISTRY_HOST = os.environ.get("DOCKER_REGISTRY_HOST", "localhost")
DOCKER_REGISTRY_PORT = os.environ.get("DOCKER_REGISTRY_PORT", "5000")
DOCKER_REGISTRY_URL = f"{DOCKER_REGISTRY_HOST}:{DOCKER_REGISTRY_PORT}"


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


def push_image_to_registry(image_name, registry_tag=None):
    """
    Push a Docker image to the registry.
    Compatible with your docker_reg_test.py approach.

    Args:
        image_name (str): Local image name
        registry_tag (str): Optional custom tag for the registry. If None, uses image_name

    Returns:
        str: The full registry image path
    """
    try:
        client = get_docker_client()

        # Create registry tag
        if registry_tag is None:
            registry_tag = image_name

        target_image = f"{DOCKER_REGISTRY_URL}/{registry_tag}:latest"

        # Get the local image
        image = client.images.get(image_name)

        # Tag the image for the registry
        image.tag(target_image)
        print(f"Tagged {image_name} as {target_image}")

        # Push to registry
        response = client.images.push(target_image)
        print(f"Pushed image to {target_image}")

        return target_image

    except Exception as e:
        raise RuntimeError(f"Error pushing image to registry: {e}")


def pull_image_from_registry(registry_image_path):
    """
    Pull a Docker image from the registry.
    Compatible with your docker_reg_test.py approach.

    Args:
        registry_image_path (str): Full registry path to the image

    Returns:
        docker.models.images.Image: The pulled image
    """
    try:
        client = get_docker_client()
        image = client.images.pull(registry_image_path)
        print(f"Pulled image: {image.tags}")
        return image
    except Exception as e:
        raise RuntimeError(f"Error pulling image from registry: {e}")


def run_docker_container(image_name, command=None):
    try:
        client = get_docker_client()
        container = client.containers.run(image_name, command=command)
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
