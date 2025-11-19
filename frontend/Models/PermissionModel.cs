using System.Text.Json.Serialization;

namespace frontend.Models
{
    /// <summary>
    /// Permission model matching the Flask backend Permission entity
    /// Represents a granular access control permission
    /// </summary>
    public class PermissionModel
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("resource")]
        public string Resource { get; set; } = string.Empty;

        [JsonPropertyName("action")]
        public string Action { get; set; } = string.Empty;

        [JsonPropertyName("created_at")]
        public DateTime CreatedAt { get; set; }

        [JsonPropertyName("updated_at")]
        public DateTime UpdatedAt { get; set; }

        // Helper property for display
        public string DisplayName => $"{Resource}:{Action}";
    }

    /// <summary>
    /// Request DTO for creating a new permission
    /// </summary>
    public class CreatePermissionRequest
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("resource")]
        public string Resource { get; set; } = string.Empty;

        [JsonPropertyName("action")]
        public string Action { get; set; } = string.Empty;
    }

    /// <summary>
    /// Request DTO for updating an existing permission
    /// </summary>
    public class UpdatePermissionRequest
    {
        [JsonPropertyName("name")]
        public string? Name { get; set; }

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("resource")]
        public string? Resource { get; set; }

        [JsonPropertyName("action")]
        public string? Action { get; set; }
    }

    /// <summary>
    /// Response for checking if a user has a permission
    /// </summary>
    public class CheckPermissionResponse
    {
        [JsonPropertyName("has_permission")]
        public bool HasPermission { get; set; }

        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("permission_name")]
        public string PermissionName { get; set; } = string.Empty;
    }

    /// <summary>
    /// Response containing user's permissions
    /// </summary>
    public class UserPermissionsResponse
    {
        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("permissions")]
        public List<string> Permissions { get; set; } = new();

        [JsonPropertyName("permission_objects")]
        public List<PermissionModel> PermissionObjects { get; set; } = new();
    }

    /// <summary>
    /// Grouped permissions by resource
    /// </summary>
    public class GroupedPermissionsResponse
    {
        [JsonPropertyName("grouped")]
        public Dictionary<string, List<PermissionModel>> Grouped { get; set; } = new();

        [JsonPropertyName("total_count")]
        public int TotalCount { get; set; }
    }
}
