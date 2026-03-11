folder_id      = "folders/YOUR_FOLDER_ID"
region         = "us-central1"

# Add team members who need viewer access to the folder
viewer_members = [
  # Example: "user:developer@example.com",
  # Example: "group:team@example.com",
]

# Add any custom role bindings as needed
custom_role_bindings = {
  # Example:
  # "sa_editor" = {
  #   role   = "roles/editor"
  #   member = "serviceAccount:terraform-sa@colt-sbx-infra-001.iam.gserviceaccount.com"
  # }
}
