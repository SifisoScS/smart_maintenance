using frontend.Models;

namespace frontend.Services.Interfaces
{
    /// <summary>
    /// Interface for authentication service
    /// Handles login, logout, token management, and user state
    /// </summary>
    public interface IAuthService
    {
        /// <summary>
        /// Authenticate user with email and password
        /// </summary>
        Task<LoginResponse> LoginAsync(LoginRequest request);

        /// <summary>
        /// Register a new user
        /// </summary>
        Task<ApiResponse> RegisterAsync(RegisterRequest request);

        /// <summary>
        /// Logout the current user (clear tokens and state)
        /// </summary>
        Task LogoutAsync();

        /// <summary>
        /// Get the current JWT token from storage
        /// </summary>
        Task<string?> GetTokenAsync();

        /// <summary>
        /// Get the current refresh token from storage
        /// </summary>
        Task<string?> GetRefreshTokenAsync();

        /// <summary>
        /// Refresh the access token using refresh token
        /// </summary>
        Task<bool> RefreshTokenAsync();

        /// <summary>
        /// Get the currently authenticated user
        /// </summary>
        Task<UserModel?> GetCurrentUserAsync();

        /// <summary>
        /// Check if user is currently authenticated
        /// </summary>
        Task<bool> IsAuthenticatedAsync();
    }
}
