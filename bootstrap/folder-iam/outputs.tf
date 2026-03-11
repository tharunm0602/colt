output "viewer_bindings" {
  description = "List of viewer role bindings created"
  value       = [for binding in google_folder_iam_member.folder_viewers : binding.member]
}
