module "vertex_ai" {
  source          = "../../modules/vertex-ai"
  project_id      = var.project_id
  vertex_ai_users = var.vertex_ai_users
}
