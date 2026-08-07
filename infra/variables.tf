variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
}

variable "region" {
  type        = string
  description = "Google Cloud Region for deployment"
  default     = "us-central1"
}

variable "service_name" {
  type        = string
  description = "Cloud Run service name for Agentic-News-Summarizer"
  default     = "agentic-news-summarizer"
}

variable "container_image" {
  type        = string
  description = "Container image URI for deployment"
  default     = "gcr.io/your-gcp-project-id/agentic-news-summarizer:latest"
}
