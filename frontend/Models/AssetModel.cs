namespace frontend.Models
{
    /// <summary>
    /// Asset model matching the Flask backend
    /// </summary>
    public class AssetModel
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string AssetCode { get; set; } = string.Empty; // Unique identifier for the asset
        public string AssetType { get; set; } = string.Empty;
        public string Location { get; set; } = string.Empty;
        public string Condition { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public DateTime PurchaseDate { get; set; }
        public decimal? PurchasePrice { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    /// <summary>
    /// DTO for updating asset condition
    /// </summary>
    public class UpdateAssetConditionDto
    {
        public string NewCondition { get; set; } = string.Empty;
    }
}
