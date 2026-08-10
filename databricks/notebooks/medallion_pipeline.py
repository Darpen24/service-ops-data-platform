# Databricks notebook source
# MAGIC %md
# MAGIC Phase 7 design: Bronze preserves raw JSON/Parquet with batch metadata; Silver validates,
# MAGIC casts, deduplicates and quarantines; Gold calculates SLA/team/category metrics.

# COMMAND ----------

# A production workspace runs these operations only after an approved deployment.
# bronze = spark.read.json(source_path).withColumn("_batch_id", lit(batch_id))
# silver = bronze.dropDuplicates(["ticket_id", "updated_at"])
# silver.write.format("delta").option("mergeSchema", "true").mode("append").saveAsTable(
#     "silver.tickets"
# )
# Delta MERGE, OPTIMIZE, history/time travel, broadcast joins, partitions, and streaming checkpoints
# are documented in docs/learning/phase-07-databricks.md rather than executed locally.
