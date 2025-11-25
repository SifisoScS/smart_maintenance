using System;
using System.Collections.Generic;

namespace frontend.Models
{
    public class PredictiveInsightsModel
    {
        public InsightsSummaryModel Summary { get; set; } = new();
        public TrendsModel? Trends { get; set; }
        public List<string> Recommendations { get; set; } = new();
        public List<AlertModel> Alerts { get; set; } = new();
        public List<AssetHealthModel> TopRiskAssets { get; set; } = new();
        public Dictionary<string, List<MaintenanceCalendarItemModel>> MaintenanceCalendar { get; set; } = new();
        public WorkloadStatusModel? WorkloadStatus { get; set; }
        public DateTime GeneratedAt { get; set; }
    }

    public class InsightsSummaryModel
    {
        public int TotalAssets { get; set; }
        public int CriticalAssets { get; set; }
        public int UpcomingMaintenance30d { get; set; }
        public int UpcomingMaintenance7d { get; set; }
        public double AverageHealth { get; set; }
        public double AverageRisk { get; set; }
    }

    public class TrendsModel
    {
        public double AverageHealth { get; set; }
        public string HealthStatus { get; set; } = "";
        public int CriticalAssets { get; set; }
        public int MaintenanceWorkload30d { get; set; }
        public string WorkloadLevel { get; set; } = "";
    }

    public class AlertModel
    {
        public string Type { get; set; } = "";
        public string Title { get; set; } = "";
        public string Message { get; set; } = "";
        public int AssetId { get; set; }
        public string Severity { get; set; } = "";
        public string ActionRequired { get; set; } = "";
    }

    public class AssetHealthModel
    {
        public AssetInfoModel AssetInfo { get; set; } = new();
        public double HealthScore { get; set; }
        public PredictionModel Prediction { get; set; } = new();
        public MaintenanceSummaryModel MaintenanceSummary { get; set; } = new();
        public List<string> Recommendations { get; set; } = new();
        public DateTime AnalyzedAt { get; set; }
    }

    public class AssetInfoModel
    {
        public int Id { get; set; }
        public string Name { get; set; } = "";
        public string AssetCode { get; set; } = "";
        public string Type { get; set; } = "";
        public string Location { get; set; } = "";
        public string Condition { get; set; } = "";
        public string Status { get; set; } = "";
        public DateTime? PurchaseDate { get; set; }
        public decimal? PurchasePrice { get; set; }
    }

    public class PredictionModel
    {
        public double RiskScore { get; set; }
        public DateTime? PredictedFailureDate { get; set; }
        public double Confidence { get; set; }
        public string Reasoning { get; set; } = "";
        public string RecommendedAction { get; set; } = "";
        public RiskFactorsModel? RiskFactors { get; set; }
    }

    public class RiskFactorsModel
    {
        public double TimeBased { get; set; }
        public double Frequency { get; set; }
        public double Condition { get; set; }
        public double Age { get; set; }
    }

    public class MaintenanceSummaryModel
    {
        public int TotalRequests { get; set; }
        public int RecentRequests30d { get; set; }
        public int RecentRequests90d { get; set; }
        public double AverageResolutionDays { get; set; }
        public DateTime? LastMaintenanceDate { get; set; }
    }

    public class MaintenanceCalendarItemModel
    {
        public string AssetName { get; set; } = "";
        public string Priority { get; set; } = "";
        public string Action { get; set; } = "";
    }

    public class WorkloadStatusModel
    {
        public int TotalActiveRequests { get; set; }
        public int Technicians { get; set; }
        public double AveragePerTech { get; set; }
        public string Status { get; set; } = "";
    }

    public class WorkloadModel
    {
        public int TechnicianId { get; set; }
        public string TechnicianName { get; set; } = "";
        public string Email { get; set; } = "";
        public int ActiveRequests { get; set; }
        public int PendingRequests { get; set; }
        public int InProgressRequests { get; set; }
        public int CompletedLast30d { get; set; }
        public double AvailabilityScore { get; set; }
        public string WorkloadLevel { get; set; } = "";
        public double AvgCompletionTime { get; set; }
    }

    public class MaintenanceScheduleModel
    {
        public int AssetId { get; set; }
        public string AssetName { get; set; } = "";
        public string AssetCode { get; set; } = "";
        public string Location { get; set; } = "";
        public DateTime ScheduledDate { get; set; }
        public double RiskScore { get; set; }
        public string Priority { get; set; } = "";
        public string Action { get; set; } = "";
        public string Reasoning { get; set; } = "";
        public int DaysUntil { get; set; }
    }

    public class AssignmentResultModel
    {
        public int RequestId { get; set; }
        public int AssignedTechnicianId { get; set; }
        public string TechnicianName { get; set; } = "";
        public double AssignmentScore { get; set; }
        public string AssignmentReason { get; set; } = "";
        public DateTime AssignedAt { get; set; }
    }
}
