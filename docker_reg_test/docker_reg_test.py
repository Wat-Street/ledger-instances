import sys
import docker

sys.path.append("..")
from utils.docker_utils import get_docker_client


IP = "localhost"
PORT = "5000"

registry = f"{IP}:{PORT}"


def tag_and_push_image():
    """
    Tags a Docker image with a new name/tag and pushes it to a registry.
    """
    image_name = "busybox:latest"
    target_image = f"{registry}/test-busybox:latest"
    try:
        client = get_docker_client()

        # Ensure image is pulled
        client.images.pull(image_name)

        # Tag the image
        image = client.images.get(image_name)
        image.tag(target_image)
        print(f"Tagged {image_name} as {target_image}")

        # Push the image
        response = client.images.push(target_image)
        print(f"Pushed image to {target_image}")

        return response
    except Exception as e:
        raise RuntimeError(f"Error tagging or pushing Docker image: {e}")


def pull_image():
    client = get_docker_client()
    image_to_pull = f"{registry}/test-alpine:latest"
    image = client.images.pull(image_to_pull)
    print(f"Pulled image: {image.tags}")


if __name__ == "__main__":
    print("Log: Tagging and Pushing Image")
    tag_and_push_image()

    print("Log: Pulling Image")
    pull_image()
