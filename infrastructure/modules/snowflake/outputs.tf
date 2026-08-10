output "database_name" {
  value       = snowflake_database.service_ops.name
  description = "Created database name."
}
