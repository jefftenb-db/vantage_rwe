#!/usr/bin/env python3
"""
Test script to verify CORS configuration handles Databricks wildcard patterns correctly.
"""
import re
import os
import sys
from pathlib import Path

# Add backend/app to path so we can import config
sys.path.insert(0, str(Path(__file__).parent / "app"))

def test_cors_regex():
    """Test that the CORS regex pattern matches Databricks App URLs correctly."""
    
    # Simulate the CORS_ORIGINS environment variable
    test_cors_origins = "http://localhost:3000,https://*.databricks.com"
    
    # Parse and convert to regex (same logic as in config.py)
    regex_patterns = []
    exact_origins = []
    
    for origin in test_cors_origins.split(","):
        origin = origin.strip()
        if "*" in origin:
            # Convert wildcard pattern to regex
            pattern = re.escape(origin).replace(r"\*", ".*")
            regex_patterns.append(pattern)
        else:
            exact_origins.append(origin)
    
    if regex_patterns:
        cors_regex = "^(" + "|".join(regex_patterns) + ")$"
    else:
        cors_regex = None
    
    print("=" * 70)
    print("CORS Configuration Test")
    print("=" * 70)
    print(f"\nInput CORS_ORIGINS: {test_cors_origins}")
    print(f"\nExact Origins: {exact_origins}")
    print(f"Regex Pattern: {cors_regex}")
    
    # Test URLs that should match
    # Note: CORS Origin headers NEVER include paths - only scheme://host:port
    # So https://workspace.databricks.com/apps/app-123 sends Origin: https://workspace.databricks.com
    test_urls = [
        # Should match
        ("http://localhost:3000", True, "Exact match - localhost"),
        ("https://myworkspace.cloud.databricks.com", True, "Databricks workspace (origin from App URL)"),
        ("https://company.databricks.com", True, "Databricks custom domain"),
        ("https://e2-demo-field-eng.cloud.databricks.com", True, "Databricks workspace origin"),
        ("https://subdomain.workspace.databricks.com", True, "Databricks multi-level subdomain"),
        
        # Should NOT match
        ("http://localhost:3001", False, "Wrong port"),
        ("https://databricks.com.evil.com", False, "Malicious domain"),
        ("https://notdatabricks.com", False, "Different domain"),
        ("http://databricks.com", False, "HTTP instead of HTTPS"),
    ]
    
    print("\n" + "=" * 70)
    print("Testing URL Matches")
    print("=" * 70)
    
    compiled_regex = re.compile(cors_regex) if cors_regex else None
    all_passed = True
    
    for url, should_match, description in test_urls:
        # Check exact match
        matches_exact = url in exact_origins
        
        # Check regex match
        matches_regex = False
        if compiled_regex:
            matches_regex = bool(compiled_regex.match(url))
        
        matches = matches_exact or matches_regex
        status = "✓ PASS" if matches == should_match else "✗ FAIL"
        
        if matches != should_match:
            all_passed = False
        
        print(f"\n{status} - {description}")
        print(f"  URL: {url}")
        print(f"  Expected: {'MATCH' if should_match else 'NO MATCH'}")
        print(f"  Got: {'MATCH' if matches else 'NO MATCH'}")
        if compiled_regex and not matches_exact:
            print(f"  Regex matched: {matches_regex}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All tests PASSED!")
        print("\nThe CORS configuration correctly:")
        print("  1. Allows exact localhost origins")
        print("  2. Matches Databricks wildcard patterns with regex")
        print("  3. Blocks malicious/incorrect domains")
    else:
        print("✗ Some tests FAILED!")
        print("\nPlease review the CORS configuration.")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    success = test_cors_regex()
    sys.exit(0 if success else 1)

