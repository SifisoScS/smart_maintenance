using frontend.Services.Interfaces;
using Microsoft.JSInterop;

namespace frontend.Services
{
    /// <summary>
    /// Service for managing tenant branding
    /// Loads tenant colors and logo, applies them dynamically via JS
    /// </summary>
    public class TenantBrandingService : ITenantBrandingService
    {
        private readonly IApiService _apiService;
        private readonly IJSRuntime _jsRuntime;
        private readonly IAuthService _authService;
        private TenantBranding? _currentBranding;

        public TenantBrandingService(IApiService apiService, IJSRuntime jsRuntime, IAuthService authService)
        {
            _apiService = apiService;
            _jsRuntime = jsRuntime;
            _authService = authService;
        }

        public async Task<TenantBranding?> GetBrandingAsync()
        {
            // Return cached branding if available
            if (_currentBranding != null)
            {
                return _currentBranding;
            }

            // Try to load from API
            var user = await _authService.GetCurrentUserAsync();
            if (user == null)
            {
                return null;
            }

            var tenant = await _apiService.GetCurrentTenantAsync();
            if (tenant != null)
            {
                _currentBranding = new TenantBranding
                {
                    LogoUrl = tenant.LogoUrl,
                    PrimaryColor = tenant.PrimaryColor,
                    SecondaryColor = tenant.SecondaryColor,
                    TenantName = tenant.Name
                };
            }

            return _currentBranding;
        }

        public async Task LoadAndApplyBrandingAsync()
        {
            var branding = await GetBrandingAsync();
            if (branding != null)
            {
                await ApplyBrandingAsync(branding);
            }
        }

        public async Task ApplyBrandingAsync(TenantBranding branding)
        {
            _currentBranding = branding;

            // Apply CSS custom properties for colors
            await _jsRuntime.InvokeVoidAsync("applyTenantBranding", new
            {
                primaryColor = branding.PrimaryColor,
                secondaryColor = branding.SecondaryColor,
                logoUrl = branding.LogoUrl
            });
        }

        public async Task ResetBrandingAsync()
        {
            _currentBranding = null;

            // Reset to default branding
            var defaultBranding = new TenantBranding
            {
                PrimaryColor = "#667eea",
                SecondaryColor = "#764ba2",
                LogoUrl = null
            };

            await ApplyBrandingAsync(defaultBranding);
        }
    }
}
