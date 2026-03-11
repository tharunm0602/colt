resource "google_folder_iam_member" "folder_viewers" {
  for_each = toset(var.viewer_members)
  
  folder = var.folder_id
  role   = "roles/viewer"
  member = each.value
}

resource "google_folder_iam_member" "custom_roles" {
  for_each = var.custom_role_bindings
  
  folder = var.folder_id
  role   = each.value.role
  member = each.value.member
}
