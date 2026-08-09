variable "name_prefix" {
  type        = string
  description = "Environment-specific resource prefix."
  default     = "DEV"
}

variable "enable_snowflake" {
  type        = bool
  description = "Opt in to Snowflake resources only after approval."
  default     = false
}

variable "enable_databricks" {
  type        = bool
  description = "Opt in to Databricks resources only after approval."
  default     = false
}

variable "snowflake_warehouse_size" {
  type        = string
  description = "Warehouse size constrained by the Snowflake module."
  default     = "XSMALL"
}

variable "databricks_host" {
  type        = string
  description = "Databricks workspace URL supplied through environment or uncommitted tfvars."
  default     = null
  nullable    = true
}

variable "databricks_token" {
  type        = string
  description = "Databricks personal access token; never commit a value."
  default     = null
  nullable    = true
  sensitive   = true
}

variable "databricks_max_dbus_per_hour" {
  type        = number
  description = "Cost guard for the optional Databricks policy."
  default     = 2
}
