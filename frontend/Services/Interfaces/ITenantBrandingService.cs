using SmartMaintenance.Blazor.Models;

namespace frontend.Services.Interfaces
{
    /// <summary>
    /// Service for managing tenant branding (colors, logo)
    /// </summary>
    public interface ITenantBrandingService
    {
        /// <summary>
        /// Get current tenant branding
        /// </summary>
        Task<TenantBranding?> GetBrandingAsync();

        /// <summary>
        /// Load and apply tenant branding
        /// </summary>
        Task LoadAndApplyBrandingAsync();

        /// <summary>
        /// Apply branding colors and logo to UI
        /// </summary>
        Task ApplyBrandingAsync(TenantBranding branding);

        /// <summary>
        /// Reset branding to default
        /// </summary>
        Task ResetBrandingAsync();
    }

    /// <summary>
    /// Tenant branding information
    /// </summary>
    public class TenantBranding
    {
        public string? LogoUrl { get; set; }
        public string PrimaryColor { get; set; } = "#667eea";
        public string SecondaryColor { get; set; } = "#764ba2";
        public string TenantName { get; set; } = string.Empty;
    }
}
