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
        /// Add JWT token to Authorization header
        /// </summary>
        private async Task SetAuthHeaderAsync()
        {
            var token = await _authService.GetTokenAsync();
            if (!string.IsNullOrEmpty(token))
            {
                _httpClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", token);
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
    }
}
