#!/usr/bin/env python
"""Quick test script for predictive maintenance service"""

from app import create_app
from app.services.predictive_maintenance_service import PredictiveMaintenanceService
from app.database import db

# Initialize app
app = create_app()
app.app_context().push()

# Test predictive insights
service = PredictiveMaintenanceService(db.session)
result = service.get_predictive_insights()

print('\n=== PREDICTIVE INSIGHTS TEST - SUCCESS ===')
print(f'Total assets analyzed: {result["summary"]["total_assets"]}')
print(f'Critical assets: {result["summary"]["critical_assets"]}')
print(f'Average health: {result["summary"]["average_health"]:.1f}')
print(f'Upcoming maintenance (30d): {result["summary"]["upcoming_maintenance_30d"]}')
print(f'Upcoming maintenance (7d): {result["summary"]["upcoming_maintenance_7d"]}')
print(f'\nTop 5 Risk Assets:')
for i, asset in enumerate(result['top_risk_assets'][:5], 1):
    print(f'{i}. {asset["asset_info"]["name"]}')
    print(f'   Risk: {asset["prediction"]["risk_score"]*100:.0f}%, Health: {asset["health_score"]:.0f}/100')
    print(f'   Action: {asset["prediction"]["recommended_action"]}')

print(f'\nRecommendations ({len(result["recommendations"])})  :')
for rec in result['recommendations'][:5]:
    print(f'  - {rec}')

print('\n=== TEST COMPLETED SUCCESSFULLY ===')
