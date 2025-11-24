using System;
using System.Collections.Generic;

namespace SmartMaintenance.Blazor.Models
{
    /// <summary>
    /// Tenant model representing an organization in the multi-tenant system
    /// </summary>
    public class TenantModel
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Subdomain { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;  // trial, active, suspended, cancelled
        public string Plan { get; set; } = string.Empty;  // free, basic, premium, enterprise

        // Plan Limits
        public int? MaxUsers { get; set; }
        public int? MaxAssets { get; set; }
        public int? MaxRequestsPerMonth { get; set; }

        // Settings
        public Dictionary<string, object>? Settings { get; set; }

        // Branding
        public string? LogoUrl { get; set; }
        public string PrimaryColor { get; set; } = "#667eea";
        public string SecondaryColor { get; set; } = "#764ba2";

        // Contact Information
        public string? BillingEmail { get; set; }
        public string? ContactName { get; set; }
        public string? ContactPhone { get; set; }

        // Dates
        public DateTime? SubscriptionExpires { get; set; }
        public DateTime? TrialEnds { get; set; }

        // Status
        public bool IsActive { get; set; } = true;
        public bool Onboarded { get; set; } = false;

        // Timestamps
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }

        // Computed properties
        public bool IsUnlimited => MaxUsers == null && MaxAssets == null && MaxRequestsPerMonth == null;
        public bool IsTrial => Status == "trial";
        public bool IsTrialExpired => TrialEnds.HasValue && TrialEnds.Value < DateTime.UtcNow;
    }

    /// <summary>
    /// Tenant usage statistics
    /// </summary>
    public class TenantUsageModel
    {
        public ResourceUsageModel Users { get; set; } = new ResourceUsageModel();
        public ResourceUsageModel Assets { get; set; } = new ResourceUsageModel();
        public ResourceUsageModel Requests { get; set; } = new ResourceUsageModel();
    }

    /// <summary>
    /// Resource usage details
    /// </summary>
    public class ResourceUsageModel
    {
        public int Current { get; set; }
        public int? Limit { get; set; }
        public int? Remaining { get; set; }
        public double? PercentageUsed { get; set; }
        public bool AtLimit => Limit.HasValue && Current >= Limit.Value;
        public bool IsUnlimited => Limit == null;
    }

    /// <summary>
    /// Tenant with usage statistics
    /// </summary>
    public class TenantWithUsageModel : TenantModel
    {
        public TenantUsageModel? Usage { get; set; }
    }

    /// <summary>
    /// Tenant subscription details
    /// </summary>
    public class TenantSubscriptionModel
    {
        public int Id { get; set; }
        public int TenantId { get; set; }
        public string Plan { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;  // trial, active, past_due, cancelled
        public string BillingCycle { get; set; } = "monthly";  // monthly, annual
        public decimal Price { get; set; }
        public string Currency { get; set; } = "USD";

        // Stripe Integration
        public string? StripeSubscriptionId { get; set; }
        public string? StripeCustomerId { get; set; }
        public string? StripePaymentMethodId { get; set; }

        // Billing Period
        public DateTime? CurrentPeriodStart { get; set; }
        public DateTime? CurrentPeriodEnd { get; set; }

        // Trial
        public DateTime? TrialStart { get; set; }
        public DateTime? TrialEnd { get; set; }

        // Cancellation
        public DateTime? CancelAt { get; set; }
        public DateTime? CancelledAt { get; set; }

        // Timestamps
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }

        // Computed properties
        public bool IsTrial => Status == "trial";
        public bool IsActive => Status == "active";
        public bool IsCancelled => Status == "cancelled";
        public int? DaysUntilRenewal
        {
            get
            {
                if (!CurrentPeriodEnd.HasValue) return null;
                var days = (CurrentPeriodEnd.Value - DateTime.UtcNow).Days;
                return days > 0 ? days : 0;
            }
        }
    }

    /// <summary>
    /// Tenant registration request model
    /// </summary>
    public class TenantRegistrationModel
    {
        public string Name { get; set; } = string.Empty;
        public string Subdomain { get; set; } = string.Empty;
        public string AdminEmail { get; set; } = string.Empty;
        public string AdminPassword { get; set; } = string.Empty;
        public string AdminFirstName { get; set; } = string.Empty;
        public string AdminLastName { get; set; } = string.Empty;
        public string Plan { get; set; } = "free";
        public string? BillingEmail { get; set; }
        public string? ContactName { get; set; }
        public string? ContactPhone { get; set; }
    }

    /// <summary>
    /// Tenant settings update model
    /// </summary>
    public class TenantSettingsModel
    {
        public string? Name { get; set; }
        public string? BillingEmail { get; set; }
        public string? ContactName { get; set; }
        public string? ContactPhone { get; set; }
    }

    /// <summary>
    /// Tenant branding update model
    /// </summary>
    public class TenantBrandingModel
    {
        public string? LogoUrl { get; set; }
        public string? PrimaryColor { get; set; }
        public string? SecondaryColor { get; set; }
    }

    /// <summary>
    /// Subscription upgrade model
    /// </summary>
    public class SubscriptionUpgradeModel
    {
        public string Plan { get; set; } = string.Empty;
        public string BillingCycle { get; set; } = "monthly";
        public string? StripeSubscriptionId { get; set; }
    }

    /// <summary>
    /// Plan limit check request
    /// </summary>
    public class PlanLimitCheckModel
    {
        public string Resource { get; set; } = string.Empty;  // users, assets, requests
        public int Count { get; set; } = 1;
    }

    /// <summary>
    /// Plan limit check response
    /// </summary>
    public class PlanLimitCheckResponseModel
    {
        public bool Allowed { get; set; }
        public string Message { get; set; } = string.Empty;
    }

    /// <summary>
    /// Plan limits and usage model
    /// </summary>
    public class PlanLimitsModel
    {
        public string Plan { get; set; } = string.Empty;
        public Dictionary<string, int?> Limits { get; set; } = new Dictionary<string, int?>();
        public TenantUsageModel? Usage { get; set; }
        public Dictionary<string, bool> Unlimited { get; set; } = new Dictionary<string, bool>();
    }

    /// <summary>
    /// Subscription plan information
    /// </summary>
    public class SubscriptionPlanInfo
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public decimal Price { get; set; }
        public string Description { get; set; } = string.Empty;
        public int? MaxUsers { get; set; }
        public int? MaxAssets { get; set; }
        public int? MaxRequestsPerMonth { get; set; }
        public List<string> Features { get; set; } = new List<string>();
        public bool IsPopular { get; set; }
        public bool IsEnterprise { get; set; }

        public static List<SubscriptionPlanInfo> GetAllPlans()
        {
            return new List<SubscriptionPlanInfo>
            {
                new SubscriptionPlanInfo
                {
                    Id = "free",
                    Name = "Free Trial",
                    Price = 0,
                    Description = "14-day trial to test the platform",
                    MaxUsers = 3,
                    MaxAssets = 10,
                    MaxRequestsPerMonth = 50,
                    Features = new List<string> { "Basic Dashboard", "Email Notifications" }
                },
                new SubscriptionPlanInfo
                {
                    Id = "basic",
                    Name = "Basic",
                    Price = 29,
                    Description = "Perfect for small teams",
                    MaxUsers = 10,
                    MaxAssets = 100,
                    MaxRequestsPerMonth = 500,
                    Features = new List<string>
                    {
                        "Basic Dashboard", "Email Notifications", "Mobile App",
                        "API Access", "Custom Fields"
                    }
                },
                new SubscriptionPlanInfo
                {
                    Id = "premium",
                    Name = "Premium",
                    Price = 99,
                    Description = "For growing organizations",
                    MaxUsers = 50,
                    MaxAssets = 500,
                    MaxRequestsPerMonth = 5000,
                    Features = new List<string>
                    {
                        "Everything in Basic", "Advanced Reporting", "Predictive Analytics",
                        "Custom Workflows", "Priority Support", "Data Export"
                    },
                    IsPopular = true
                },
                new SubscriptionPlanInfo
                {
                    Id = "enterprise",
                    Name = "Enterprise",
                    Price = 299,
                    Description = "Unlimited scale for large enterprises",
                    MaxUsers = null,
                    MaxAssets = null,
                    MaxRequestsPerMonth = null,
                    Features = new List<string>
                    {
                        "Everything in Premium", "Unlimited Resources", "SSO/SAML",
                        "Dedicated Support", "Custom Integrations", "SLA Guarantee"
                    },
                    IsEnterprise = true
                }
            };
        }
    }
}
