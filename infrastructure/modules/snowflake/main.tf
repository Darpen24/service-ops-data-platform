resource "snowflake_database" "service_ops" {
  name                        = "${var.name_prefix}_SERVICE_OPS"
  data_retention_time_in_days = 1
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.service_ops.name
  name     = "RAW"
}

resource "snowflake_warehouse" "service_ops" {
  name                = "${var.name_prefix}_SERVICE_OPS_XS"
  warehouse_size      = var.warehouse_size
  auto_suspend        = 60
  auto_resume         = true
  initially_suspended = true
}
