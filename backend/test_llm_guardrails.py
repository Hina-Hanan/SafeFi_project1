#!/usr/bin/env python3
"""
Test script for LLM guardrails.
Tests both in-scope and out-of-scope queries to verify guardrails work.
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "https://api.safefi.live"

def test_query(query, expected_behavior="refuse"):
    """Test a single query and check if it behaves as expected."""
    print(f"\n🔍 Testing query: '{query}'")
    print(f"   Expected: {expected_behavior}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/llm/query",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            reason = data.get("reason", "")
            context_used = data.get("context_used", 0)
            
            print(f"   ✅ Response: '{answer}'")
            print(f"   📊 Context used: {context_used}")
            if reason:
                print(f"   🚫 Reason: {reason}")
            
            # Check if behavior matches expectation
            if expected_behavior == "refuse":
                if "i don't know" in answer.lower():
                    print("   ✅ PASS: Correctly refused")
                    return True
                else:
                    print("   ❌ FAIL: Should have refused but didn't")
                    return False
            elif expected_behavior == "answer":
                if "i don't know" not in answer.lower() and len(answer) > 10:
                    print("   ✅ PASS: Provided answer")
                    return True
                else:
                    print("   ❌ FAIL: Should have answered but refused")
                    return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    """Run all guardrail tests."""
    print("🧪 LLM Guardrails Test Suite")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # Out-of-scope queries (should refuse)
        ("Who won the 2010 World Cup?", "refuse"),
        ("What's the weather like today?", "refuse"),
        ("How do I cook pasta?", "refuse"),
        ("What is the capital of France?", "refuse"),
        ("Tell me a joke", "refuse"),
        
        # In-scope queries (should answer)
        ("What protocols are monitored by SafeFi?", "answer"),
        ("How does SafeFi calculate risk scores?", "answer"),
        ("What is the TVL of Uniswap?", "answer"),
        ("What DeFi protocols have high risk?", "answer"),
        ("How does the risk assessment work?", "answer"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for query, expected in test_cases:
        if test_query(query, expected):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All guardrails working correctly!")
        return 0
    else:
        print("⚠️  Some guardrails need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())

