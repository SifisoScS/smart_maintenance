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
    }
}
