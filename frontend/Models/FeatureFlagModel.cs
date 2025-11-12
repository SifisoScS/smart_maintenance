using System.Text.Json.Serialization;

namespace frontend.Models
{
    /// <summary>
    /// Feature flag model matching the Flask backend FeatureFlag entity
    /// </summary>
    public class FeatureFlagModel
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("feature_key")]
        public string FeatureKey { get; set; } = string.Empty;

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("category")]
        public string Category { get; set; } = string.Empty;

        [JsonPropertyName("enabled")]
        public bool Enabled { get; set; }

        [JsonPropertyName("rollout_percentage")]
        public int RolloutPercentage { get; set; } = 100;

        [JsonPropertyName("config_data")]
        public Dictionary<string, object>? ConfigData { get; set; }

        [JsonPropertyName("created_at")]
        public DateTime CreatedAt { get; set; }

        [JsonPropertyName("updated_at")]
        public DateTime UpdatedAt { get; set; }
    }

    /// <summary>
    /// Feature flag categories
    /// </summary>
    public static class FeatureCategories
    {
        public const string Analytics = "analytics";
        public const string Notifications = "notifications";
        public const string Integrations = "integrations";
        public const string Mobile = "mobile";
        public const string Automation = "automation";
        public const string Security = "security";
        public const string UI = "ui";
        public const string Experimental = "experimental";
    }

    /// <summary>
    /// Create feature flag request DTO
    /// </summary>
    public class CreateFeatureFlagRequest
    {
        [JsonPropertyName("feature_key")]
        public string FeatureKey { get; set; } = string.Empty;

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("category")]
        public string Category { get; set; } = FeatureCategories.Experimental;

        [JsonPropertyName("enabled")]
        public bool Enabled { get; set; } = false;

        [JsonPropertyName("rollout_percentage")]
        public int RolloutPercentage { get; set; } = 100;

        [JsonPropertyName("config_data")]
        public Dictionary<string, object>? ConfigData { get; set; }
    }

    /// <summary>
    /// Update feature flag request DTO
    /// </summary>
    public class UpdateFeatureFlagRequest
    {
        [JsonPropertyName("name")]
        public string? Name { get; set; }

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("category")]
        public string? Category { get; set; }

        [JsonPropertyName("enabled")]
        public bool? Enabled { get; set; }

        [JsonPropertyName("rollout_percentage")]
        public int? RolloutPercentage { get; set; }

        [JsonPropertyName("config_data")]
        public Dictionary<string, object>? ConfigData { get; set; }
    }

    /// <summary>
    /// Response wrapper for feature flag operations
    /// </summary>
    public class FeatureFlagResponse
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("message")]
        public string? Message { get; set; }

        [JsonPropertyName("data")]
        public FeatureFlagModel? Data { get; set; }

        [JsonPropertyName("error")]
        public string? Error { get; set; }
    }

    /// <summary>
    /// Response for list of feature flags
    /// </summary>
    public class FeatureFlagListResponse
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("data")]
        public List<FeatureFlagModel> Data { get; set; } = new();

        [JsonPropertyName("total")]
        public int Total { get; set; }

        [JsonPropertyName("error")]
        public string? Error { get; set; }
    }

    /// <summary>
    /// Response for user-specific enabled features
    /// </summary>
    public class MyFeaturesResponse
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("features")]
        public Dictionary<string, bool> Features { get; set; } = new();

        [JsonPropertyName("error")]
        public string? Error { get; set; }
    }

    /// <summary>
    /// Response for checking if feature is enabled for user
    /// </summary>
    public class FeatureCheckResponse
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("feature_key")]
        public string FeatureKey { get; set; } = string.Empty;

        [JsonPropertyName("enabled")]
        public bool Enabled { get; set; }

        [JsonPropertyName("user_id")]
        public int UserId { get; set; }

        [JsonPropertyName("error")]
        public string? Error { get; set; }
    }
}
