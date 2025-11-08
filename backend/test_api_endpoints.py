"""
Test API Endpoints

Verify all API endpoints are registered correctly.
"""

from app import create_app

def test_endpoints():
    """Test that all endpoints are registered."""
    app = create_app('development')

    print("="*70)
    print("API ENDPOINTS TEST")
    print("="*70)

    print("\nFlask app created successfully!")
    print("\nRegistered API Endpoints:\n")

    # Group endpoints by blueprint
    endpoints_by_blueprint = {}

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if rule.rule.startswith('/api/v1'):
            blueprint = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'main'
            methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])

            if blueprint not in endpoints_by_blueprint:
                endpoints_by_blueprint[blueprint] = []

            endpoints_by_blueprint[blueprint].append((methods, rule.rule))

    # Print organized by blueprint
    for blueprint, endpoints in sorted(endpoints_by_blueprint.items()):
        print(f"\n[{blueprint.upper()}]")
        for methods, rule in endpoints:
            print(f"  {methods:20} {rule}")

    print("\n" + "="*70)
    print(f"Total API endpoints: {sum(len(eps) for eps in endpoints_by_blueprint.values())}")
    print("="*70)

    return True


if __name__ == '__main__':
    test_endpoints()
