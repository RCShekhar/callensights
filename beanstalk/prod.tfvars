vpc_id         = "vpc-0436c7d2b0fdad8aa"
Instance_type  = "t3.medium"
minsize        = 1
maxsize        = 2
public_subnets = [
  "subnet-03f1082b19bf6f1c1",
  "subnet-0aa8e0b299d1ddcac",
  "subnet-02636addc4fb41ef9",
  "subnet-0b7288f9eb73fa099",
  "subnet-04b712ad4b8faf19b",
  "subnet-069574164891bc811"
] # Service Subnet
elb_public_subnets  = [] # ELB Subnet
tier                = "WebServer"
solution_stack_name = "Python 3.11 running on 64bit Amazon Linux 2023"

mysql_secret         = "callensights/mysql"
mongodb_secret       = "callensights/mongodb"
clerk_secret         = "callensights/clerk"
clerk_audience       = "callensights-api-prod"
region               = "ap-south-1"
default_schema       = "callensights_dev"
media_bucket         = "callensights-media"
transcription_bucket = "callensights-transcript"
analysis_bucket      = "callensights-analysis"
media_minsize        = 1024
media_maxsize        = 1073741824