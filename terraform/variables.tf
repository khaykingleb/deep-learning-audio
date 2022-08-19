variable "project_name" {
  type        = string
  description = "The name of the project."
  default     = ""
}

variable "environment" {
  type        = string
  description = "The environment type."
  default     = ""
}

variable "region" {
  type        = string
  description = "Servers location in Amazon's data centers."
  default     = ""
}

# variable "instance_type" {
#   type        = string
#   description = "Instance type for the EC2."
#   default     = ""
# }
#
# variable "ami_id" {
#   description = "AMI ID to use for the EC2 instance."
#   type        = string
#   default     = ""
# }
