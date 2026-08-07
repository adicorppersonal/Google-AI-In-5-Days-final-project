output "service_url" {
  description = "Deployed Cloud Run Service URL"
  value       = google_cloud_run_v2_service.agent_service.uri
}

output "secret_manager_id" {
  description = "Secret Manager Secret ID for GEMINI_API_KEY"
  value       = google_secret_manager_secret.gemini_api_key_secret.name
}

output "service_account_email" {
  description = "Agent Runner IAM Service Account Email"
  value       = google_service_account.agent_runner.email
}
