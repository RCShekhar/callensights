variable "elasticapp" {
  default = "cns_vertocity_app"
}

variable "beanstalkappenv" {
  default = "cns_vertocity_app_env"
}

variable "solution_stack_name" {
  type = string
}

variable "tier" {
  type = string
}

variable "Instance_type" {
  type = string
}

variable "minsize" {
  type = number
}

variable "maxsize" {
  type = number
}

variable "mysql_secret" {
  type = string
}

variable "mongodb_secret" {
  type = string
}

variable "clerk_secret" {
  type = string
}

variable "clerk_audience" {
  type = string
}

variable "region" {
  type = string
}

variable "default_schema" {
  type = string
}

variable "media_bucket" {
  type = string
}

variable "transcription_bucket" {
  type = string
}

variable "analysis_bucket" {
  type = string
}

variable "media_minsize" {
  type = number
}

variable "media_maxsize" {
  type = number
}

variable "vpc_id" {}
variable "public_subnets" {}
variable "elb_public_subnets" {}
