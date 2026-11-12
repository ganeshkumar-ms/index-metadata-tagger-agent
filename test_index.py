import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from services import index_service

def test_index_aws_content():
    aws_text = """
    # Serverless Architecture Guide v2.0
    Author: Cloud Infrastructure Team
    Target: Enterprise Solutions Architects & DevOps Engineers
    Date: October 2026

    This architecture specification defines our deployment pattern for event-driven microservices on Amazon Web Services (AWS).
    All microservices must use AWS Lambda compute with Amazon API Gateway HTTP endpoints.
    State must be persisted in Amazon DynamoDB with point-in-time recovery enabled.
    All data at rest and in transit must adhere to PCI-DSS Level 1 encryption standards.
    Deployment must be automated using AWS CDK pipelines within 15 minutes of PR merge.
    """
    print("[TEST] Running INDEX on AWS Serverless document...")
    res = index_service.extract_metadata(aws_text, file_name="DOC_93812_ARCH_FINAL.pdf")
    print("\n=== EXTRACTED METADATA ===")
    import json
    print(json.dumps(res, indent=2))
    assert res.get("status") == "success"
    data = res.get("data", {})
    assert "basic" in data
    assert "business" in data
    assert "content" in data
    assert "search_optimization" in data
    print("\n[SUCCESS] INDEX metadata test passed!")

if __name__ == "__main__":
    test_index_aws_content()

