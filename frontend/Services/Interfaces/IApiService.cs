using frontend.Models;

namespace frontend.Services.Interfaces
{
    /// <summary>
    /// Interface for API service
    /// Handles all HTTP communication with Flask backend
    /// </summary>
    public interface IApiService
    {
        // ============ Request Endpoints ============

        /// <summary>
        /// Get all maintenance requests (filtered by user role on backend)
        /// </summary>
        Task<List<RequestModel>> GetRequestsAsync();

        /// <summary>
        /// Get a specific request by ID
        /// </summary>
        Task<RequestModel?> GetRequestByIdAsync(int id);

        /// <summary>
        /// Create a new maintenance request
        /// </summary>
        Task<ApiResponse> CreateRequestAsync(CreateRequestDto request);

        /// <summary>
        /// Assign a technician to a request (admin only)
        /// </summary>
        Task<ApiResponse> AssignRequestAsync(int requestId, AssignRequestDto dto);

        /// <summary>
        /// Start work on a request (technician only)
        /// </summary>
        Task<ApiResponse> StartWorkAsync(int requestId);

        /// <summary>
        /// Complete a request (technician only)
        /// </summary>
        Task<ApiResponse> CompleteRequestAsync(int requestId, CompleteRequestDto dto);

        // ============ Asset Endpoints ============

        /// <summary>
        /// Get all assets
        /// </summary>
        Task<List<AssetModel>> GetAssetsAsync();

        /// <summary>
        /// Get a specific asset by ID
        /// </summary>
        Task<AssetModel?> GetAssetByIdAsync(int id);

        /// <summary>
        /// Update asset condition (admin only)
        /// </summary>
        Task<ApiResponse> UpdateAssetConditionAsync(int assetId, UpdateAssetConditionDto dto);

        // ============ User Endpoints ============

        /// <summary>
        /// Get all users (admin only)
        /// </summary>
        Task<List<UserModel>> GetUsersAsync();

        /// <summary>
        /// Get all technicians (for assignment dropdown)
        /// </summary>
        Task<List<UserModel>> GetTechniciansAsync();

        /// <summary>
        /// Get a specific user by ID
        /// </summary>
        Task<UserModel?> GetUserByIdAsync(int id);

        // ============ Feature Flag Endpoints ============

        /// <summary>
        /// Get all feature flags
        /// </summary>
        Task<FeatureFlagListResponse> GetFeatureFlagsAsync();

        /// <summary>
        /// Get all enabled feature flags
        /// </summary>
        Task<FeatureFlagListResponse> GetEnabledFeatureFlagsAsync();

        /// <summary>
        /// Get feature flags enabled for current user
        /// </summary>
        Task<MyFeaturesResponse> GetMyFeaturesAsync();

        /// <summary>
        /// Get specific feature flag by key
        /// </summary>
        Task<FeatureFlagResponse> GetFeatureFlagByKeyAsync(string featureKey);

        /// <summary>
        /// Check if feature is enabled for current user
        /// </summary>
        Task<FeatureCheckResponse> CheckFeatureEnabledAsync(string featureKey);

        /// <summary>
        /// Create a new feature flag (admin only)
        /// </summary>
        Task<FeatureFlagResponse> CreateFeatureFlagAsync(CreateFeatureFlagRequest request);

        /// <summary>
        /// Update a feature flag (admin only)
        /// </summary>
        Task<FeatureFlagResponse> UpdateFeatureFlagAsync(int flagId, UpdateFeatureFlagRequest request);

        /// <summary>
        /// Toggle feature flag on/off (admin only)
        /// </summary>
        Task<FeatureFlagResponse> ToggleFeatureFlagAsync(int flagId);

        /// <summary>
        /// Delete a feature flag (admin only)
        /// </summary>
        Task<FeatureFlagResponse> DeleteFeatureFlagAsync(int flagId);

        /// <summary>
        /// Get feature flags by category
        /// </summary>
        Task<FeatureFlagListResponse> GetFeatureFlagsByCategoryAsync(string category);

        // ============ Permission Endpoints ============

        Task<List<PermissionModel>> GetPermissionsAsync();
        Task<GroupedPermissionsResponse?> GetPermissionsGroupedAsync();
        Task<PermissionModel?> GetPermissionByIdAsync(int id);
        Task<ApiResponse> CreatePermissionAsync(CreatePermissionRequest request);
        Task<ApiResponse> UpdatePermissionAsync(int id, UpdatePermissionRequest request);
        Task<ApiResponse> DeletePermissionAsync(int id);
        Task<CheckPermissionResponse?> CheckUserPermissionAsync(int userId, string permissionName);
        Task<UserPermissionsResponse?> GetUserPermissionsAsync(int userId);

        // ============ Role Endpoints ============

        Task<List<RoleModel>> GetRolesAsync();
        Task<RoleModel?> GetRoleByIdAsync(int id);
        Task<ApiResponse> CreateRoleAsync(CreateRoleRequest request);
        Task<ApiResponse> UpdateRoleAsync(int id, UpdateRoleRequest request);
        Task<ApiResponse> DeleteRoleAsync(int id);
        Task<ApiResponse> AddPermissionToRoleAsync(int roleId, AddPermissionToRoleRequest request);
        Task<ApiResponse> RemovePermissionFromRoleAsync(int roleId, int permissionId);
        Task<RoleUsersResponse?> GetRoleUsersAsync(int roleId);
        Task<UserRolesResponse?> GetUserRolesAsync(int userId);
        Task<RoleAssignmentResponse?> AssignRoleToUserAsync(int userId, AssignRoleRequest request);
        Task<RoleAssignmentResponse?> RemoveRoleFromUserAsync(int userId, int roleId);
    }
}
