variable "name_prefix" {
  type        = string
  description = "Prefix for Databricks policy resources."
}

variable "max_dbus_per_hour" {
  type        = number
  description = "Cost guard for an opt-in job-cluster policy."
  default     = 2
  validation {
    condition     = var.max_dbus_per_hour > 0 && var.max_dbus_per_hour <= 4
    error_message = "max_dbus_per_hour must be between 0 and 4."
  }
}
