using System.Text.Json.Serialization;

namespace frontend.Models
{
    /// <summary>
    /// Role model matching the Flask backend Role entity
    /// Represents a collection of permissions assigned to users
    /// </summary>
    public class RoleModel
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("is_system")]
        public bool IsSystem { get; set; }

        [JsonPropertyName("created_at")]
        public DateTime CreatedAt { get; set; }

        [JsonPropertyName("updated_at")]
        public DateTime UpdatedAt { get; set; }

        [JsonPropertyName("permissions")]
        public List<PermissionModel>? Permissions { get; set; }

        [JsonPropertyName("permission_count")]
        public int? PermissionCount { get; set; }

        [JsonPropertyName("users")]
        public List<UserSummary>? Users { get; set; }

        [JsonPropertyName("user_count")]
        public int? UserCount { get; set; }

        // Helper properties
        public string SystemBadge => IsSystem ? "System" : "Custom";
        public int DisplayPermissionCount => PermissionCount ?? Permissions?.Count ?? 0;
        public int DisplayUserCount => UserCount ?? Users?.Count ?? 0;
    }

    /// <summary>
    /// Simplified user info for role relationships
    /// </summary>
    public class UserSummary
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("email")]
        public string Email { get; set; } = string.Empty;

        [JsonPropertyName("full_name")]
        public string FullName { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request DTO for creating a new role
    /// </summary>
    public class CreateRoleRequest
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("is_system")]
        public bool IsSystem { get; set; } = false;

        [JsonPropertyName("permission_ids")]
        public List<int>? PermissionIds { get; set; }
    }

    /// <summary>
    /// Request DTO for updating an existing role
    /// </summary>
    public class UpdateRoleRequest
    {
        [JsonPropertyName("name")]
        public string? Name { get; set; }

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("permission_ids")]
        public List<int>? PermissionIds { get; set; }
    }

    /// <summary>
    /// Request DTO for adding a permission to a role
    /// </summary>
    public class AddPermissionToRoleRequest
    {
        [JsonPropertyName("permission_id")]
        public int PermissionId { get; set; }
    }

    /// <summary>
    /// Request DTO for assigning a role to a user
    /// </summary>
    public class AssignRoleRequest
    {
        [JsonPropertyName("role_id")]
        public int RoleId { get; set; }
    }

    /// <summary>
    /// Response containing user's roles
    /// </summary>
    public class UserRolesResponse
    {
        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("roles")]
        public List<RoleModel> Roles { get; set; } = new();

        [JsonPropertyName("total_permissions")]
        public int TotalPermissions { get; set; }
    }

    /// <summary>
    /// Response containing users with a specific role
    /// </summary>
    public class RoleUsersResponse
    {
        [JsonPropertyName("role_id")]
        public int RoleId { get; set; }

        [JsonPropertyName("role_name")]
        public string RoleName { get; set; } = string.Empty;

        [JsonPropertyName("users")]
        public List<UserSummary> Users { get; set; } = new();

        [JsonPropertyName("user_count")]
        public int UserCount { get; set; }
    }

    /// <summary>
    /// Success response for role assignment operations
    /// </summary>
    public class RoleAssignmentResponse
    {
        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;

        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("role_id")]
        public int RoleId { get; set; }

        [JsonPropertyName("roles")]
        public List<RoleModel>? Roles { get; set; }
    }
}
