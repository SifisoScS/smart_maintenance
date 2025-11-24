using frontend.Models;
using frontend.Services.Interfaces;
using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace frontend.Services
{
    /// <summary>
    /// API Service implementation
    /// Handles all HTTP communication with Flask backend
    /// Automatically includes JWT token in requests
    /// </summary>
    public class ApiService : IApiService
    {
        private readonly HttpClient _httpClient;
        private readonly IAuthService _authService;
        private readonly SemaphoreSlim _refreshLock = new SemaphoreSlim(1, 1);

        public ApiService(HttpClient httpClient, IAuthService authService)
        {
            _httpClient = httpClient;
            _authService = authService;
        }

        /// <summary>
        /// Add JWT token and tenant ID to request headers
        /// </summary>
        private async Task SetAuthHeaderAsync()
        {
            var token = await _authService.GetTokenAsync();
            if (!string.IsNullOrEmpty(token))
            {
                _httpClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", token);
            }

            // Add X-Tenant-ID header for multi-tenancy
            var user = await _authService.GetCurrentUserAsync();
            if (user?.TenantId.HasValue == true)
            {
                if (_httpClient.DefaultRequestHeaders.Contains("X-Tenant-ID"))
                {
                    _httpClient.DefaultRequestHeaders.Remove("X-Tenant-ID");
                }
                _httpClient.DefaultRequestHeaders.Add("X-Tenant-ID", user.TenantId.Value.ToString());
            }
        }

        /// <summary>
        /// Execute HTTP request with automatic token refresh on 401
        /// </summary>
        private async Task<HttpResponseMessage> ExecuteWithTokenRefreshAsync(Func<Task<HttpResponseMessage>> requestFunc)
        {
            var response = await requestFunc();

            // If we get 401 Unauthorized, try to refresh token and retry once
            if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                await _refreshLock.WaitAsync();
                try
                {
                    // Check if token refresh is successful
                    if (await _authService.RefreshTokenAsync())
                    {
                        // Retry the request with new token
                        await SetAuthHeaderAsync();
                        response = await requestFunc();
                    }
                }
                finally
                {
                    _refreshLock.Release();
                }
            }

            return response;
        }

        // ============ Request Endpoints ============

        public async Task<List<RequestModel>> GetRequestsAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>("/api/v1/requests");

                if (response?.Success == true && response.Data != null)
                {
                    // Backend returns data in ApiResponse wrapper
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var requests = System.Text.Json.JsonSerializer.Deserialize<List<RequestModel>>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return requests ?? new List<RequestModel>();
                }

                return new List<RequestModel>();
            }
            catch (Exception)
            {
                return new List<RequestModel>();
            }
        }

        public async Task<RequestModel?> GetRequestByIdAsync(int id)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/requests/{id}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var request = System.Text.Json.JsonSerializer.Deserialize<RequestModel>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return request;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<ApiResponse> CreateRequestAsync(CreateRequestDto request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/requests", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to create request" };
                }

                // Read error details from response
                var errorContent = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"CreateRequest error response: {errorContent}");

                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"CreateRequest exception: {ex}");
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> AssignRequestAsync(int requestId, AssignRequestDto dto)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync($"/api/v1/requests/{requestId}/assign", dto);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to assign request" };
                }

                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error: {response.StatusCode}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> StartWorkAsync(int requestId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsync($"/api/v1/requests/{requestId}/start", null);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to start work" };
                }

                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error: {response.StatusCode}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> CompleteRequestAsync(int requestId, CompleteRequestDto dto)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync($"/api/v1/requests/{requestId}/complete", dto);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to complete request" };
                }

                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error: {response.StatusCode}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        // ============ Asset Endpoints ============

        public async Task<List<AssetModel>> GetAssetsAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>("/api/v1/assets");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var assets = System.Text.Json.JsonSerializer.Deserialize<List<AssetModel>>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return assets ?? new List<AssetModel>();
                }

                return new List<AssetModel>();
            }
            catch (Exception)
            {
                return new List<AssetModel>();
            }
        }

        public async Task<AssetModel?> GetAssetByIdAsync(int id)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/assets/{id}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var asset = System.Text.Json.JsonSerializer.Deserialize<AssetModel>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return asset;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<ApiResponse> UpdateAssetConditionAsync(int assetId, UpdateAssetConditionDto dto)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PatchAsJsonAsync($"/api/v1/assets/{assetId}/condition", dto);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to update asset condition" };
                }

                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error: {response.StatusCode}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        // ============ User Endpoints ============

        public async Task<List<UserModel>> GetUsersAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>("/api/v1/users");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var users = System.Text.Json.JsonSerializer.Deserialize<List<UserModel>>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return users ?? new List<UserModel>();
                }

                return new List<UserModel>();
            }
            catch (Exception)
            {
                return new List<UserModel>();
            }
        }

        public async Task<List<UserModel>> GetTechniciansAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>("/api/v1/users?role=technician");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var technicians = System.Text.Json.JsonSerializer.Deserialize<List<UserModel>>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return technicians ?? new List<UserModel>();
                }

                return new List<UserModel>();
            }
            catch (Exception)
            {
                return new List<UserModel>();
            }
        }

        public async Task<UserModel?> GetUserByIdAsync(int id)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/users/{id}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var user = System.Text.Json.JsonSerializer.Deserialize<UserModel>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return user;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        // ============ Feature Flag Endpoints ============

        public async Task<FeatureFlagListResponse> GetFeatureFlagsAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<FeatureFlagListResponse>("/api/v1/features");
                return response ?? new FeatureFlagListResponse { Success = false, Error = "No response from server" };
            }
            catch (Exception ex)
            {
                return new FeatureFlagListResponse { Success = false, Error = $"Exception: {ex.Message}" };
            }
        }

        public async Task<FeatureFlagListResponse> GetEnabledFeatureFlagsAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<FeatureFlagListResponse>("/api/v1/features/enabled");
                return response ?? new FeatureFlagListResponse { Success = false, Error = "No response from server" };
            }
            catch (Exception ex)
            {
                return new FeatureFlagListResponse { Success = false, Error = $"Exception: {ex.Message}" };
            }
        }

        public async Task<MyFeaturesResponse> GetMyFeaturesAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<MyFeaturesResponse>("/api/v1/features/my-features");
                return response ?? new MyFeaturesResponse { Success = false, Error = "No response from server" };
            }
            catch (Exception ex)
            {
                return new MyFeaturesResponse { Success = false, Error = $"Exception: {ex.Message}" };
            }
        }

        public async Task<FeatureFlagResponse> GetFeatureFlagByKeyAsync(string featureKey)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<FeatureFlagResponse>($"/api/v1/features/{featureKey}");
                return response ?? new FeatureFlagResponse { Success = false, Error = "No response from server" };
            }
            catch (Exception ex)
            {
                return new FeatureFlagResponse { Success = false, Error = $"Exception: {ex.Message}" };
            }
        }

        public async Task<FeatureCheckResponse> CheckFeatureEnabledAsync(string featureKey)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<FeatureCheckResponse>($"/api/v1/features/{featureKey}/check");
                return response ?? new FeatureCheckResponse { Success = false, Error = "No response from server" };
            }
            catch (Exception ex)
            {
                return new FeatureCheckResponse { Success = false, Error = $"Exception: {ex.Message}" };
            }
        }

        public async Task<FeatureFlagResponse> CreateFeatureFlagAsync(CreateFeatureFlagRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/features", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<FeatureFlagResponse>()
                           ?? new FeatureFlagResponse { Success = false, Error = "Failed to create feature flag" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<FeatureFlagResponse> UpdateFeatureFlagAsync(int flagId, UpdateFeatureFlagRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PatchAsJsonAsync($"/api/v1/features/{flagId}", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<FeatureFlagResponse>()
                           ?? new FeatureFlagResponse { Success = false, Error = "Failed to update feature flag" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<FeatureFlagResponse> ToggleFeatureFlagAsync(int flagId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsync($"/api/v1/features/{flagId}/toggle", null);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<FeatureFlagResponse>()
                           ?? new FeatureFlagResponse { Success = false, Error = "Failed to toggle feature flag" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<FeatureFlagResponse> DeleteFeatureFlagAsync(int flagId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.DeleteAsync($"/api/v1/features/{flagId}");

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<FeatureFlagResponse>()
                           ?? new FeatureFlagResponse { Success = false, Error = "Failed to delete feature flag" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new FeatureFlagResponse
                {
                    Success = false,
                    Error = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<FeatureFlagListResponse> GetFeatureFlagsByCategoryAsync(string category)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<FeatureFlagListResponse>($"/api/v1/features/category/{category}");
                return response ?? new FeatureFlagListResponse { Success = false, Error = "No response from server" };
            }
            catch (Exception ex)
            {
                return new FeatureFlagListResponse { Success = false, Error = $"Exception: {ex.Message}" };
            }
        }

        // ============ Permission Endpoints ============

        public async Task<List<PermissionModel>> GetPermissionsAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>("/api/v1/permissions");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var permissions = System.Text.Json.JsonSerializer.Deserialize<List<PermissionModel>>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return permissions ?? new List<PermissionModel>();
                }

                return new List<PermissionModel>();
            }
            catch (Exception)
            {
                return new List<PermissionModel>();
            }
        }

        public async Task<GroupedPermissionsResponse?> GetPermissionsGroupedAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>("/api/v1/permissions/grouped");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var grouped = System.Text.Json.JsonSerializer.Deserialize<GroupedPermissionsResponse>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return grouped;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<PermissionModel?> GetPermissionByIdAsync(int id)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/permissions/{id}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var permission = System.Text.Json.JsonSerializer.Deserialize<PermissionModel>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return permission;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<ApiResponse> CreatePermissionAsync(CreatePermissionRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/permissions", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to create permission" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> UpdatePermissionAsync(int id, UpdatePermissionRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PatchAsJsonAsync($"/api/v1/permissions/{id}", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to update permission" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> DeletePermissionAsync(int id)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.DeleteAsync($"/api/v1/permissions/{id}");

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to delete permission" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<CheckPermissionResponse?> CheckUserPermissionAsync(int userId, string permissionName)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/permissions/check/{userId}/{permissionName}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var result = System.Text.Json.JsonSerializer.Deserialize<CheckPermissionResponse>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return result;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<UserPermissionsResponse?> GetUserPermissionsAsync(int userId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/permissions/user/{userId}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var result = System.Text.Json.JsonSerializer.Deserialize<UserPermissionsResponse>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return result;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        // ============ Role Endpoints ============

        public async Task<List<RoleModel>> GetRolesAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>("/api/v1/roles");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var roles = System.Text.Json.JsonSerializer.Deserialize<List<RoleModel>>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return roles ?? new List<RoleModel>();
                }

                return new List<RoleModel>();
            }
            catch (Exception)
            {
                return new List<RoleModel>();
            }
        }

        public async Task<RoleModel?> GetRoleByIdAsync(int id)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/roles/{id}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var role = System.Text.Json.JsonSerializer.Deserialize<RoleModel>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return role;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<ApiResponse> CreateRoleAsync(CreateRoleRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/roles", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to create role" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> UpdateRoleAsync(int id, UpdateRoleRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PatchAsJsonAsync($"/api/v1/roles/{id}", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to update role" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> DeleteRoleAsync(int id)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.DeleteAsync($"/api/v1/roles/{id}");

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to delete role" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> AddPermissionToRoleAsync(int roleId, AddPermissionToRoleRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync($"/api/v1/roles/{roleId}/permissions", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to add permission to role" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<ApiResponse> RemovePermissionFromRoleAsync(int roleId, int permissionId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.DeleteAsync($"/api/v1/roles/{roleId}/permissions/{permissionId}");

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>()
                           ?? new ApiResponse { Success = false, Message = "Failed to remove permission from role" };
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Error {response.StatusCode}: {errorContent}"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Exception: {ex.Message}"
                };
            }
        }

        public async Task<RoleUsersResponse?> GetRoleUsersAsync(int roleId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/roles/{roleId}/users");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var result = System.Text.Json.JsonSerializer.Deserialize<RoleUsersResponse>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return result;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<UserRolesResponse?> GetUserRolesAsync(int userId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ApiResponse>($"/api/v1/roles/user/{userId}");

                if (response?.Success == true && response.Data != null)
                {
                    var jsonElement = (System.Text.Json.JsonElement)response.Data;
                    var result = System.Text.Json.JsonSerializer.Deserialize<UserRolesResponse>(
                        jsonElement.GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return result;
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<RoleAssignmentResponse?> AssignRoleToUserAsync(int userId, AssignRoleRequest request)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync($"/api/v1/roles/user/{userId}/assign", request);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<RoleAssignmentResponse>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        public async Task<RoleAssignmentResponse?> RemoveRoleFromUserAsync(int userId, int roleId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.DeleteAsync($"/api/v1/roles/user/{userId}/remove/{roleId}");

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<RoleAssignmentResponse>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        // ============ Tenant Endpoints ============

        /// <summary>
        /// Register a new tenant (public endpoint - no auth required)
        /// </summary>
        public async Task<ApiResponse?> RegisterTenantAsync(SmartMaintenance.Blazor.Models.TenantRegistrationModel registration)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/tenants/register", registration);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>();
                }

                var errorContent = await response.Content.ReadAsStringAsync();
                return new ApiResponse { Success = false, Message = errorContent };
            }
            catch (Exception ex)
            {
                return new ApiResponse { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Get current tenant information with usage stats
        /// </summary>
        public async Task<SmartMaintenance.Blazor.Models.TenantWithUsageModel?> GetCurrentTenantAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<SmartMaintenance.Blazor.Models.TenantWithUsageModel>("/api/v1/tenants/current");
                return response;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Update current tenant settings
        /// </summary>
        public async Task<ApiResponse?> UpdateTenantSettingsAsync(SmartMaintenance.Blazor.Models.TenantSettingsModel settings)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PutAsJsonAsync("/api/v1/tenants/current", settings);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Update tenant branding (logo and colors)
        /// </summary>
        public async Task<ApiResponse?> UpdateTenantBrandingAsync(SmartMaintenance.Blazor.Models.TenantBrandingModel branding)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PutAsJsonAsync("/api/v1/tenants/current/branding", branding);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Get current tenant subscription details
        /// </summary>
        public async Task<SmartMaintenance.Blazor.Models.TenantSubscriptionModel?> GetSubscriptionAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<SmartMaintenance.Blazor.Models.TenantSubscriptionModel>("/api/v1/tenants/current/subscription");
                return response;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Upgrade tenant subscription
        /// </summary>
        public async Task<ApiResponse?> UpgradeSubscriptionAsync(SmartMaintenance.Blazor.Models.SubscriptionUpgradeModel upgrade)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/tenants/current/subscription/upgrade", upgrade);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Get plan limits and current usage
        /// </summary>
        public async Task<SmartMaintenance.Blazor.Models.PlanLimitsModel?> GetPlanLimitsAsync()
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<SmartMaintenance.Blazor.Models.PlanLimitsModel>("/api/v1/tenants/current/limits");
                return response;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Check if tenant can add more of a resource
        /// </summary>
        public async Task<SmartMaintenance.Blazor.Models.PlanLimitCheckResponseModel?> CheckPlanLimitAsync(string resource, int count = 1)
        {
            await SetAuthHeaderAsync();
            try
            {
                var checkModel = new SmartMaintenance.Blazor.Models.PlanLimitCheckModel
                {
                    Resource = resource,
                    Count = count
                };

                var response = await _httpClient.PostAsJsonAsync("/api/v1/tenants/current/limits/check", checkModel);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<SmartMaintenance.Blazor.Models.PlanLimitCheckResponseModel>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        // ============ Super Admin Tenant Endpoints ============

        /// <summary>
        /// List all tenants (super admin only)
        /// </summary>
        public async Task<List<SmartMaintenance.Blazor.Models.TenantModel>> GetAllTenantsAsync(string? status = null, string? plan = null, int? limit = null)
        {
            await SetAuthHeaderAsync();
            try
            {
                var queryParams = new List<string>();
                if (!string.IsNullOrEmpty(status)) queryParams.Add($"status={status}");
                if (!string.IsNullOrEmpty(plan)) queryParams.Add($"plan={plan}");
                if (limit.HasValue) queryParams.Add($"limit={limit}");

                var query = queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
                var response = await _httpClient.GetFromJsonAsync<TenantListResponse>($"/api/v1/tenants{query}");

                return response?.Tenants ?? new List<SmartMaintenance.Blazor.Models.TenantModel>();
            }
            catch (Exception)
            {
                return new List<SmartMaintenance.Blazor.Models.TenantModel>();
            }
        }

        /// <summary>
        /// Search tenants (super admin only)
        /// </summary>
        public async Task<List<SmartMaintenance.Blazor.Models.TenantModel>> SearchTenantsAsync(string query)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<TenantListResponse>($"/api/v1/tenants?search={query}");
                return response?.Tenants ?? new List<SmartMaintenance.Blazor.Models.TenantModel>();
            }
            catch (Exception)
            {
                return new List<SmartMaintenance.Blazor.Models.TenantModel>();
            }
        }

        /// <summary>
        /// Get tenant by ID (super admin only)
        /// </summary>
        public async Task<SmartMaintenance.Blazor.Models.TenantWithUsageModel?> GetTenantByIdAsync(int tenantId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.GetFromJsonAsync<SmartMaintenance.Blazor.Models.TenantWithUsageModel>($"/api/v1/tenants/{tenantId}");
                return response;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Suspend a tenant (super admin only)
        /// </summary>
        public async Task<ApiResponse?> SuspendTenantAsync(int tenantId, string reason)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsJsonAsync($"/api/v1/tenants/{tenantId}/suspend", new { reason });

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        /// <summary>
        /// Activate a suspended tenant (super admin only)
        /// </summary>
        public async Task<ApiResponse?> ActivateTenantAsync(int tenantId)
        {
            await SetAuthHeaderAsync();
            try
            {
                var response = await _httpClient.PostAsync($"/api/v1/tenants/{tenantId}/activate", null);

                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadFromJsonAsync<ApiResponse>();
                }

                return null;
            }
            catch (Exception)
            {
                return null;
            }
        }

        // Helper class for tenant list response
        private class TenantListResponse
        {
            public int Total { get; set; }
            public List<SmartMaintenance.Blazor.Models.TenantModel> Tenants { get; set; } = new List<SmartMaintenance.Blazor.Models.TenantModel>();
        }
    }
}
