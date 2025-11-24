using System.Text.Json.Serialization;

namespace frontend.Models
{
    /// <summary>
    /// User model matching the Flask backend User entity
    /// </summary>
    public class UserModel
    {
        public int Id { get; set; }
        public string Email { get; set; } = string.Empty;
        public string FullName { get; set; } = string.Empty;
        public string Role { get; set; } = string.Empty;
        public bool IsActive { get; set; }
        public int? TenantId { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    /// <summary>
    /// Login request DTO
    /// </summary>
    public class LoginRequest
    {
        public string Email { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }

    /// <summary>
    /// Login response from backend (matches actual structure)
    /// </summary>
    public class LoginResponse
    {
        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;

        [JsonPropertyName("access_token")]
        public string AccessToken { get; set; } = string.Empty;

        [JsonPropertyName("refresh_token")]
        public string RefreshToken { get; set; } = string.Empty;

        [JsonPropertyName("user")]
        public UserModel? User { get; set; }

        // Helper property for frontend use
        public bool Success => !string.IsNullOrEmpty(AccessToken);
    }

    /// <summary>
    /// Register request DTO (matches backend schema)
    /// </summary>
    public class RegisterRequest
    {
        [JsonPropertyName("email")]
        public string Email { get; set; } = string.Empty;

        [JsonPropertyName("password")]
        public string Password { get; set; } = string.Empty;

        [JsonPropertyName("first_name")]
        public string FirstName { get; set; } = string.Empty;

        [JsonPropertyName("last_name")]
        public string LastName { get; set; } = string.Empty;

        [JsonPropertyName("role")]
        public string Role { get; set; } = "client";

        [JsonPropertyName("phone")]
        public string? Phone { get; set; }

        [JsonPropertyName("department")]
        public string? Department { get; set; }
    }

    /// <summary>
    /// Generic API response wrapper
    /// </summary>
    public class ApiResponse
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public object? Data { get; set; }
        public ErrorResponse? Error { get; set; }
    }

    /// <summary>
    /// Error response structure from backend
    /// </summary>
    public class ErrorResponse
    {
        public string Code { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
        public Dictionary<string, string[]>? Details { get; set; }
    }
}
