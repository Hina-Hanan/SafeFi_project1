"""
System Integration Test Script
Tests the complete backend-frontend integration chain
"""
import os
import sys
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, func
from app.database.models import Protocol, ProtocolMetric, RiskScore

load_dotenv()

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
DATABASE_URL = os.getenv("DATABASE_URL")

def print_header(text: str) -> None:
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_database() -> bool:
    """Test database connection and data"""
    print_header("Testing Database Connection")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Test connection
            result = conn.execute(select(func.version()))
            version = result.fetchone()
            print(f"✅ Database connected: {version[0][:50]}...")
            
        # Check data
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            # Count protocols
            protocol_count = db.query(Protocol).count()
            print(f"✅ Protocols in database: {protocol_count}")
            
            if protocol_count == 0:
                print("⚠️  WARNING: No protocols found! Run: python scripts/seed_real_protocols.py")
                return False
            
            # Count metrics
            metric_count = db.query(ProtocolMetric).count()
            print(f"✅ Metrics records: {metric_count}")
            
            if metric_count == 0:
                print("⚠️  WARNING: No metrics found! Run: python scripts/collect_live_data.py")
            
            # Count risk scores
            risk_count = db.query(RiskScore).count()
            print(f"✅ Risk scores: {risk_count}")
            
            if risk_count == 0:
                print("⚠️  WARNING: No risk scores found! Run: python scripts/calculate_risks.py")
            
            # Sample protocols
            protocols = db.query(Protocol).limit(3).all()
            print(f"\n✅ Sample protocols:")
            for p in protocols:
                print(f"   - {p.name} ({p.chain})")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_backend_api() -> bool:
    """Test backend API endpoints"""
    print_header("Testing Backend API")
    
    try:
        # Test health endpoint
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health endpoint: {response.status_code}")
            print(f"   Database connected: {health_data.get('database_connected', False)}")
            print(f"   Total protocols: {health_data.get('total_protocols', 0)}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test protocols endpoint
        response = requests.get(f"{BACKEND_URL}/protocols", params={"limit": 5}, timeout=10)
        if response.status_code == 200:
            protocols = response.json()
            print(f"✅ Protocols endpoint: {response.status_code}")
            print(f"   Protocols returned: {len(protocols)}")
            
            if len(protocols) > 0:
                # Check data structure
                sample = protocols[0]
                print(f"\n✅ Sample protocol data structure:")
                print(f"   - id: {sample.get('id', 'MISSING')}")
                print(f"   - name: {sample.get('name', 'MISSING')}")
                print(f"   - latest_risk: {'✅ Present' if sample.get('latest_risk') else '❌ Missing'}")
                print(f"   - latest_metrics: {'✅ Present' if sample.get('latest_metrics') else '❌ Missing'}")
                
                # Check nested data
                if sample.get('latest_risk'):
                    risk = sample['latest_risk']
                    print(f"\n✅ Risk data:")
                    print(f"   - risk_score: {risk.get('risk_score', 'MISSING')}")
                    print(f"   - risk_level: {risk.get('risk_level', 'MISSING')}")
                
                if sample.get('latest_metrics'):
                    metrics = sample['latest_metrics']
                    print(f"\n✅ Metrics data:")
                    print(f"   - tvl_usd: {metrics.get('tvl_usd', 'MISSING')}")
                    print(f"   - price_change_24h: {metrics.get('price_change_24h', 'MISSING')}")
            else:
                print("⚠️  WARNING: No protocols returned from API!")
                return False
        else:
            print(f"❌ Protocols endpoint failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        # Test risk endpoint
        if len(protocols) > 0:
            protocol_id = protocols[0]['id']
            response = requests.get(
                f"{BACKEND_URL}/risk/protocols/{protocol_id}/history",
                params={"days": 7, "limit": 10},
                timeout=10
            )
            if response.status_code == 200:
                history = response.json()
                print(f"\n✅ Risk history endpoint: {response.status_code}")
                print(f"   History records: {len(history)}")
            else:
                print(f"\n⚠️  Risk history endpoint: {response.status_code} (may be empty)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        print("   Make sure backend server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        return False


def test_cors() -> bool:
    """Test CORS configuration"""
    print_header("Testing CORS Configuration")
    
    try:
        # Check CORS headers
        response = requests.options(
            f"{BACKEND_URL}/protocols",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            },
            timeout=5
        )
        
        if "access-control-allow-origin" in response.headers:
            allowed_origin = response.headers.get("access-control-allow-origin")
            print(f"✅ CORS configured: {allowed_origin}")
            
            if allowed_origin == "*" or "localhost:5173" in allowed_origin:
                print("✅ Frontend origin allowed")
                return True
            else:
                print(f"⚠️  Frontend origin may not be allowed: {allowed_origin}")
                print("   Check CORS_ORIGINS in backend/.env")
                return False
        else:
            print("❌ CORS headers not present")
            print("   Check CORS middleware configuration in backend/app/main.py")
            return False
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False


def test_frontend() -> bool:
    """Test frontend availability"""
    print_header("Testing Frontend")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend accessible at {FRONTEND_URL}")
            return True
        else:
            print(f"⚠️  Frontend returned: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️  Cannot connect to frontend at {FRONTEND_URL}")
        print("   Frontend may not be running. Start with:")
        print("   cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"⚠️  Frontend test warning: {e}")
        return False


def print_summary(results: dict) -> None:
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTests Passed: {passed}/{total}\n")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Check the protocol heat map is displaying")
        print("3. Click on a protocol to view trends")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Ensure backend server is running (port 8000)")
        print("3. Ensure frontend server is running (port 5173)")
        print("4. Check .env files are configured correctly")
        print("5. Run database initialization scripts if needed")


def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("  DeFi Risk Assessment - System Integration Test")
    print("="*60)
    
    results = {}
    
    # Run tests
    results["Database Connection"] = test_database()
    results["Backend API"] = test_backend_api()
    results["CORS Configuration"] = test_cors()
    results["Frontend Availability"] = test_frontend()
    
    # Print summary
    print_summary(results)
    
    # Exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()



