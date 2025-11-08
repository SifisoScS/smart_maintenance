# TODO: Fix Create Request Functionality

## Current Status
- [x] Update backend/app/schemas/request_schemas.py: Add business types to category validation
- [x] Update frontend/Pages/Requests/CreateRequest.razor: Send category = business type from "Request Type" field
- [x] Update backend/app/controllers/request_controller.py: Return standard {'success':bool, 'data':..., 'message':...} format
- [x] Update frontend/Services/ApiService.cs: Simplify response handling since backend will return consistent format

## Followup Steps
- [ ] Test create request from frontend
- [ ] Verify data validation and factory creation works
- [ ] Check notifications and event publishing
