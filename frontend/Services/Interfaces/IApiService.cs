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
    }
}
