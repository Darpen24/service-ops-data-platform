variable "name_prefix" {
  type        = string
  description = "Uppercase prefix used for Snowflake resource names."
  validation {
    condition     = can(regex("^[A-Z][A-Z0-9_]{2,30}$", var.name_prefix))
    error_message = "name_prefix must be an uppercase Snowflake-safe identifier."
  }
}

variable "warehouse_size" {
  type        = string
  description = "Smallest appropriate warehouse size for this environment."
  default     = "XSMALL"
  validation {
    condition     = contains(["XSMALL", "SMALL"], var.warehouse_size)
    error_message = "Only XSMALL or SMALL are permitted by this portfolio module."
  }
}
