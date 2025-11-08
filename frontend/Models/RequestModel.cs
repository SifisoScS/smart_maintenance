namespace frontend.Models
{
    /// <summary>
    /// Maintenance Request model matching the Flask backend
    /// </summary>
    public class RequestModel
    {
        public int Id { get; set; }
        public string Type { get; set; } = string.Empty;
        public string RequestType => Type; // Alias for consistency
        public string Category { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string Priority { get; set; } = string.Empty;
        public int SubmitterId { get; set; }
        public int? AssignedTechnicianId { get; set; }
        public int? TechnicianId => AssignedTechnicianId; // Alias for consistency
        public int AssetId { get; set; }
        public decimal? EstimatedHours { get; set; }
        public decimal? ActualHours { get; set; }
        public string? CompletionNotes { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public DateTime? AssignedAt { get; set; }

        // Navigation properties
        public UserModel? Submitter { get; set; }
        public UserModel? AssignedTechnician { get; set; }
        public AssetModel? Asset { get; set; }

        // Computed properties for easier access
        public string ClientName => Submitter?.FullName ?? "Unknown";
        public string TechnicianName => AssignedTechnician?.FullName ?? string.Empty;
        public string AssetName => Asset?.Name ?? string.Empty;
        public string AssetCode => Asset?.AssetCode ?? string.Empty;
    }

    /// <summary>
    /// DTO for creating a new maintenance request
    /// Backend extracts SubmitterId from JWT token
    /// RequestType is the technical category (electrical, plumbing, hvac) for Factory pattern
    /// </summary>
    public class CreateRequestDto
    {
        [System.Text.Json.Serialization.JsonPropertyName("request_type")]
        public string RequestType { get; set; } = string.Empty;

        [System.Text.Json.Serialization.JsonPropertyName("asset_id")]
        [System.Text.Json.Serialization.JsonIgnore(Condition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull)]
        public int? AssetId { get; set; }

        [System.Text.Json.Serialization.JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;

        [System.Text.Json.Serialization.JsonPropertyName("description")]
        public string Description { get; set; } = string.Empty;

        [System.Text.Json.Serialization.JsonPropertyName("priority")]
        public string Priority { get; set; } = "medium";
    }

    /// <summary>
    /// DTO for assigning a technician to a request
    /// </summary>
    public class AssignRequestDto
    {
        public int TechnicianId { get; set; }
        public int AssignedByUserId { get; set; }
    }

    /// <summary>
    /// DTO for completing a request
    /// </summary>
    public class CompleteRequestDto
    {
        public string CompletionNotes { get; set; } = string.Empty;
        public string ResolutionNotes // Alias for CompletionNotes
        {
            get => CompletionNotes;
            set => CompletionNotes = value;
        }
        public decimal? ActualHours { get; set; }
    }
}
