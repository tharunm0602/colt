project_id    = "cloud-practice-dev-2"
location      = "us-central1"
repository_id = "colt-artifact_1"
format        = "DOCKER"
description   = "Docker repository"
labels        = {
  env = "sbx"
}
docker_config = {
  immutable_tags = true
}
