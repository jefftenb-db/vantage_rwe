#!/usr/bin/env python
"""
Test script to verify Databricks connection and OMOP data access.
"""

import sys
from app.config import settings
from app.db.databricks import db
import logging

# Enable connector debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("databricks.sql").setLevel(logging.DEBUG)

# Enable urllib3 logging for HTTP details
logging.getLogger("urllib3").setLevel(logging.DEBUG)

def test_connection():
    """Test basic Databricks connection."""
    print("🔍 Testing Databricks Connection...")
    print(f"   Host: {settings.databricks_host}")
    print(f"   Schema: {settings.omop_full_schema}")
    
    try:
        result = db.execute_scalar("SELECT 1")
        if result == 1:
            print("✅ Basic connection successful!\n")
            return True
        else:
            print("❌ Connection returned unexpected result\n")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}\n")
        return False

def test_omop_tables():
    """Test access to OMOP tables."""
    print("🔍 Testing OMOP Table Access...")
    
    tables = [
        'person',
        'condition_occurrence',
        'drug_exposure',
        'procedure_occurrence',
        'visit_occurrence',
        'concept'
    ]
    
    results = {}
    for table in tables:
        try:
            query = f"SELECT COUNT(*) FROM {settings.omop_full_schema}.{table}"
            count = db.execute_scalar(query)
            results[table] = count
            print(f"✅ {table}: {count:,} rows")
        except Exception as e:
            results[table] = None
            print(f"❌ {table}: {str(e)}")
    
    print()
    return results

def test_concept_search():
    """Test concept search functionality."""
    print("🔍 Testing Concept Search...")
    
    try:
        query = f"""
        SELECT concept_id, concept_name, domain_id, vocabulary_id
        FROM {settings.omop_full_schema}.concept
        WHERE LOWER(concept_name) LIKE '%diabetes%'
        AND domain_id = 'Condition'
        LIMIT 5
        """
        
        results = db.execute_query(query)
        
        if results:
            print(f"✅ Found {len(results)} diabetes concepts:")
            for concept in results:
                print(f"   - {concept['concept_name']} (ID: {concept['concept_id']})")
            print()
            return True
        else:
            print("⚠️  No diabetes concepts found\n")
            return False
    except Exception as e:
        print(f"❌ Concept search failed: {e}\n")
        return False

def test_patient_query():
    """Test basic patient query."""
    print("🔍 Testing Patient Query...")
    
    try:
        # Get total patient count
        query = f"SELECT COUNT(*) FROM {settings.omop_full_schema}.person"
        count = db.execute_scalar(query)
        print(f"✅ Total patients: {count:,}")
        
        # Get gender distribution
        query = f"""
        SELECT 
            c.concept_name as gender,
            COUNT(*) as count
        FROM {settings.omop_full_schema}.person p
        JOIN {settings.omop_full_schema}.concept c ON p.gender_concept_id = c.concept_id
        GROUP BY c.concept_name
        """
        
        results = db.execute_query(query)
        
        if results:
            print("✅ Gender distribution:")
            for row in results:
                print(f"   - {row['gender']}: {row['count']:,}")
            print()
            return True
        else:
            print("⚠️  No gender distribution data\n")
            return False
    except Exception as e:
        print(f"❌ Patient query failed: {e}\n")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("OMOP Cohort Builder - Connection Test")
    print("=" * 60)
    print()
    
    # Run tests
    connection_ok = test_connection()
    if not connection_ok:
        print("⚠️  Cannot proceed without basic connection")
        sys.exit(1)
    
    print("🔍 Testing OMOP Table Access...")
    tables_ok = test_omop_tables()
    concepts_ok = test_concept_search()
    patients_ok = test_patient_query()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Connection:     {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"OMOP Tables:    {'✅ PASS' if any(tables_ok.values()) else '❌ FAIL'}")
    print(f"Concept Search: {'✅ PASS' if concepts_ok else '❌ FAIL'}")
    print(f"Patient Query:  {'✅ PASS' if patients_ok else '❌ FAIL'}")
    print()
    
    if all([connection_ok, any(tables_ok.values()), concepts_ok, patients_ok]):
        print("🎉 All tests passed! You're ready to run the application.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()

