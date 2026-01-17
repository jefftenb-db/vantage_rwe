# Databricks notebook source
# MAGIC %md
# MAGIC # PLEASE READ
# MAGIC ## Follow the following 3 steps.  Be sure to update the widget values before running step 4
# MAGIC 1) pip install
# MAGIC 2) Create widgets
# MAGIC 3) Update widget values
# MAGIC 4) Create Secret Scope and Secrets

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 1
# MAGIC ## Run pip install, restart Python

# COMMAND ----------

# MAGIC %pip install --upgrade databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 2
# MAGIC ## Create widget parameters

# COMMAND ----------

dbutils.widgets.text("secret_scope", "", "Secret Scope")
dbutils.widgets.text("http_path", "", "HTTP Path")
dbutils.widgets.text("genie_space_id", "", "Genie Space ID")

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 3
# MAGIC ## Update widget parameters with Catalog, Schema, Warehouse ID

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 4
# MAGIC ## Run code below to create secret scope and secrets

# COMMAND ----------

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

SECRET_SCOPE = dbutils.widgets.get("secret_scope")
HTTP_PATH = dbutils.widgets.get("http_path")
GENIE_SPACE_ID = dbutils.widgets.get("genie_space_id")

w.secrets.create_scope(scope=SECRET_SCOPE)
w.secrets.put_secret(scope=SECRET_SCOPE, key="http_path", string_value=HTTP_PATH)
w.secrets.put_secret(scope=SECRET_SCOPE, key="genie_space_id", string_value=GENIE_SPACE_ID)
