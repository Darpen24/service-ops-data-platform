provider "snowflake" {}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

module "snowflake" {
  count          = var.enable_snowflake ? 1 : 0
  source         = "../../modules/snowflake"
  name_prefix    = var.name_prefix
  warehouse_size = var.snowflake_warehouse_size
}

module "databricks" {
  count             = var.enable_databricks ? 1 : 0
  source            = "../../modules/databricks"
  name_prefix       = lower(var.name_prefix)
  max_dbus_per_hour = var.databricks_max_dbus_per_hour
}
