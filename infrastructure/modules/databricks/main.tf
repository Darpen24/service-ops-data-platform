resource "databricks_cluster_policy" "service_ops" {
  name = "${var.name_prefix}-service-ops-cost-guard"
  definition = jsonencode({
    "autotermination_minutes" = { type = "fixed", value = 15 }
    "num_workers"             = { type = "range", maxValue = 1 }
    "dbus_per_hour"           = { type = "range", maxValue = var.max_dbus_per_hour }
  })
}
