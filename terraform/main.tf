locals {
  full_project_name = "${var.environment}-${var.project_name}"
  tags = {
    owner        = "Gleb Khaykin"
    project_name = local.full_project_name
  }
}
