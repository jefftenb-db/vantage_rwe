# Databricks notebook source
# MAGIC %md
# MAGIC # PLEASE READ
# MAGIC ## Follow the following 5 steps.  Be sure to update the widget values before running steps 4 and 5
# MAGIC 1) pip install
# MAGIC 2) Create widgets
# MAGIC 3) Update widget values
# MAGIC 4) Create Genie Space
# MAGIC 5) Capture Genie Space ID

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

dbutils.widgets.text("catalog_name", "vantage_rwe", "Catalog Name")
dbutils.widgets.text("schema_name", "omop", "Schema Name")
dbutils.widgets.text("warehouse_id", "", "Warehouse ID")


# COMMAND ----------

# MAGIC %md
# MAGIC # Step 3
# MAGIC ## Update widget parameters with Catalog, Schema, Warehouse ID

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 4
# MAGIC ## Run code below to create Genie Space

# COMMAND ----------

CATALOG_NAME = dbutils.widgets.get("catalog_name")
SCHEMA_NAME = dbutils.widgets.get("schema_name")
WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI

w = WorkspaceClient()

GENIE_TITLE = "Vantage RWE Space2"
GENIE_DESCRIPTION = "The OMOP Common Data Model (CDM) is an open-source standard for organizing diverse healthcare data (like EHRs, claims) into a unified format, enabling large-scale, reproducible research across different institutions.This includes several tables from that CDM"

g = w.genie.create_space(
    warehouse_id = WAREHOUSE_ID,
    title = GENIE_TITLE,
    description = GENIE_DESCRIPTION,
    serialized_space = f"""{{\"version\":1,\"data_sources\":{{\"tables\":[{{\"identifier\":\"{CATALOG_NAME}.{SCHEMA_NAME}.concept\",\"column_configs\":[{{\"column_name\":\"concept_class_id\",\"get_example_values\":true}},{{\"column_name\":\"concept_code\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"concept_id\",\"get_example_values\":true}},{{\"column_name\":\"concept_name\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"domain_id\",\"get_example_values\":true}},{{\"column_name\":\"invalid_reason\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"standard_concept\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"valid_end_date\",\"get_example_values\":true}},{{\"column_name\":\"valid_start_date\",\"get_example_values\":true}},{{\"column_name\":\"vocabulary_id\",\"get_example_values\":true}}]}},{{\"identifier\":\"{CATALOG_NAME}.{SCHEMA_NAME}.concept_ancestor\",\"column_configs\":[{{\"column_name\":\"ancestor_concept_id\",\"get_example_values\":true}},{{\"column_name\":\"descendant_concept_id\",\"get_example_values\":true}},{{\"column_name\":\"max_levels_of_separation\",\"get_example_values\":true}},{{\"column_name\":\"min_levels_of_separation\",\"get_example_values\":true}}]}},{{\"identifier\":\"{CATALOG_NAME}.{SCHEMA_NAME}.condition_occurrence\",\"column_configs\":[{{\"column_name\":\"CONDITION_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_END_DATE\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_END_DATETIME\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_OCCURRENCE_ID\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_SOURCE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"CONDITION_START_DATE\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_START_DATETIME\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_STATUS_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"CONDITION_STATUS_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"CONDITION_TYPE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"PERSON_ID\",\"get_example_values\":true}},{{\"column_name\":\"PROVIDER_ID\",\"get_example_values\":true}},{{\"column_name\":\"STOP_REASON\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"VISIT_DETAIL_ID\",\"get_example_values\":true}},{{\"column_name\":\"VISIT_OCCURRENCE_ID\",\"get_example_values\":true}}]}},{{\"identifier\":\"{CATALOG_NAME}.{SCHEMA_NAME}.drug_exposure\",\"column_configs\":[{{\"column_name\":\"DAYS_SUPPLY\",\"get_example_values\":true}},{{\"column_name\":\"DOSE_UNIT_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"DRUG_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"DRUG_EXPOSURE_END_DATE\",\"get_example_values\":true}},{{\"column_name\":\"DRUG_EXPOSURE_END_DATETIME\",\"get_example_values\":true}},{{\"column_name\":\"DRUG_EXPOSURE_ID\",\"get_example_values\":true}},{{\"column_name\":\"DRUG_EXPOSURE_START_DATE\",\"get_example_values\":true}},{{\"column_name\":\"DRUG_EXPOSURE_START_DATETIME\",\"get_example_values\":true}},{{\"column_name\":\"DRUG_SOURCE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"DRUG_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"DRUG_TYPE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"LOT_NUMBER\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"PERSON_ID\",\"get_example_values\":true}},{{\"column_name\":\"PROVIDER_ID\",\"get_example_values\":true}},{{\"column_name\":\"QUANTITY\",\"get_example_values\":true}},{{\"column_name\":\"REFILLS\",\"get_example_values\":true}},{{\"column_name\":\"ROUTE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"ROUTE_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"SIG\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"STOP_REASON\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"VERBATIM_END_DATE\",\"get_example_values\":true}},{{\"column_name\":\"VISIT_DETAIL_ID\",\"get_example_values\":true}},{{\"column_name\":\"VISIT_OCCURRENCE_ID\",\"get_example_values\":true}}]}},{{\"identifier\":\"{CATALOG_NAME}.{SCHEMA_NAME}.person\",\"column_configs\":[{{\"column_name\":\"BIRTH_DATETIME\",\"get_example_values\":true}},{{\"column_name\":\"CARE_SITE_ID\",\"get_example_values\":true}},{{\"column_name\":\"DAY_OF_BIRTH\",\"get_example_values\":true}},{{\"column_name\":\"ETHNICITY_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"ETHNICITY_SOURCE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"ETHNICITY_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"GENDER_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"GENDER_SOURCE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"GENDER_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"LOCATION_ID\",\"get_example_values\":true}},{{\"column_name\":\"MONTH_OF_BIRTH\",\"get_example_values\":true}},{{\"column_name\":\"PERSON_ID\",\"get_example_values\":true}},{{\"column_name\":\"PERSON_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"PROVIDER_ID\",\"get_example_values\":true}},{{\"column_name\":\"RACE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"RACE_SOURCE_CONCEPT_ID\",\"get_example_values\":true}},{{\"column_name\":\"RACE_SOURCE_VALUE\",\"get_example_values\":true,\"build_value_dictionary\":true}},{{\"column_name\":\"YEAR_OF_BIRTH\",\"get_example_values\":true}}]}}]}},\"instructions\":{{\"text_instructions\":[{{\"id\":\"01f0eb127c331ac18897a8a4c2a88dc3\",\"content\":[\"the data in this room is from the OMOP common data model: https://ohdsi.github.io/CommonDataModel/ \\nThe concept table has names to all concepts.The concept_ID can be derived from this table. \\nThe concept_ancestor table is used to match concept_ids as ancestor_concept_ids and descendant_concept_id \\nThe descendant_concept_id is used to match conditions in the condition_occurance table as the condition_concept_id \\nThe descendant_concept_id is used to match drug exposures in the drug_exposre table as the drug_concept_id\"]}}],\"example_question_sqls\":[{{\"id\":\"01f0eb1282d51706b412ff89bf6d3a51\",\"question\":[\"What patients were diagnosed with chronic congestive heart failure?\"],\"sql\":[\"SELECT person_id, MIN(condition_start_date) AS condition_start_date\",\"FROM {CATALOG_NAME}.{SCHEMA_NAME}.condition_occurrence\",\"WHERE condition_concept_id IN (\",\"SELECT descendant_concept_id FROM {CATALOG_NAME}.{SCHEMA_NAME}.concept_ancestor WHERE ancestor_concept_id IN ('4229440')\",\")\",\"GROUP BY person_id\"]}},{{\"id\":\"01f0eb128bf31094b8bc6a6ff150f48a\",\"question\":[\"what patients have been exposed to Furosemide?\"],\"sql\":[\"SELECT person_id, MIN(drug_exposure_start_date) AS drug_exposure_start_date\",\"FROM {CATALOG_NAME}.{SCHEMA_NAME}.drug_exposure\",\"WHERE drug_concept_id IN (\",\"SELECT descendant_concept_id FROM {CATALOG_NAME}.{SCHEMA_NAME}.concept_ancestor WHERE ancestor_concept_id IN ('1719286')\",\")\",\"GROUP BY person_id\"]}}]}}}}""")

# COMMAND ----------

# MAGIC %md
# MAGIC # Step 5
# MAGIC ## Capture Genie Space ID for use in Databricks App

# COMMAND ----------

print("Genie Space ID: \n", g.space_id)