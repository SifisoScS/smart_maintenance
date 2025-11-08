using Blazored.LocalStorage;
using frontend.Models;
using frontend.Services.Interfaces;
using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace frontend.Services
{
    /// <summary>
    /// Authentication service implementation
    /// Manages JWT tokens, user state, and authentication flow
    /// </summary>
    public class AuthService : IAuthService
    {
    private readonly HttpClient _httpClient;
    private readonly ILocalStorageService _localStorage;
    private const string TOKEN_KEY = "authToken";
    private const string REFRESH_TOKEN_KEY = "refreshToken";
    private const string USER_KEY = "currentUser";

        public AuthService(HttpClient httpClient, ILocalStorageService localStorage)
        {
            _httpClient = httpClient;
            _localStorage = localStorage;
        }

        /// <summary>
        /// Login user and store JWT token
        /// </summary>
        public async Task<LoginResponse> LoginAsync(LoginRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/auth/login", request);
                var content = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var loginResponse = System.Text.Json.JsonSerializer.Deserialize<LoginResponse>(content,
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    if (loginResponse != null && !string.IsNullOrEmpty(loginResponse.AccessToken))
                    {
                        // Store JWT token
                        await _localStorage.SetItemAsync(TOKEN_KEY, loginResponse.AccessToken);

                        // Store refresh token
                        if (!string.IsNullOrEmpty(loginResponse.RefreshToken))
                        {
                            await _localStorage.SetItemAsync(REFRESH_TOKEN_KEY, loginResponse.RefreshToken);
                        }

                        // Store user info
                        if (loginResponse.User != null)
                        {
                            await _localStorage.SetItemAsync(USER_KEY, loginResponse.User);
                        }

                        return loginResponse;
                    }
                }

                // Handle failed login
                return new LoginResponse
                {
                    Message = "Invalid email or password"
                };
            }
            catch (Exception ex)
            {
                return new LoginResponse
                {
                    Message = $"Login error: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Register a new user
        /// </summary>
        public async Task<ApiResponse> RegisterAsync(RegisterRequest request)
        {
            try
            {
                var response = await _httpClient.PostAsJsonAsync("/api/v1/auth/register", request);
                var content = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    // Backend returns: {"message": "...", "data": {...}}
                    var result = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object>>(content,
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return new ApiResponse
                    {
                        Success = true,
                        Message = result?["message"]?.ToString() ?? "Registration successful",
                        Data = result?["data"]
                    };
                }

                // Backend returns: {"error": {"code": "...", "message": "...", "details": {...}}}
                var errorResult = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, System.Text.Json.JsonElement>>(content,
                    new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                if (errorResult != null && errorResult.ContainsKey("error"))
                {
                    var error = System.Text.Json.JsonSerializer.Deserialize<ErrorResponse>(errorResult["error"].GetRawText(),
                        new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                    return new ApiResponse
                    {
                        Success = false,
                        Message = error?.Message ?? "Registration failed",
                        Error = error
                    };
                }

                return new ApiResponse
                {
                    Success = false,
                    Message = "Registration failed"
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse
                {
                    Success = false,
                    Message = $"Registration error: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Logout user and clear stored data
        /// </summary>
        public async Task LogoutAsync()
        {
            await _localStorage.RemoveItemAsync(TOKEN_KEY);
            await _localStorage.RemoveItemAsync(REFRESH_TOKEN_KEY);
            await _localStorage.RemoveItemAsync(USER_KEY);
        }

        /// <summary>
        /// Get stored JWT token
        /// </summary>
        public async Task<string?> GetTokenAsync()
        {
            return await _localStorage.GetItemAsync<string>(TOKEN_KEY);
        }

        /// <summary>
        /// Get stored refresh token
        /// </summary>
        public async Task<string?> GetRefreshTokenAsync()
        {
            return await _localStorage.GetItemAsync<string>(REFRESH_TOKEN_KEY);
        }

        /// <summary>
        /// Refresh access token using refresh token
        /// </summary>
        public async Task<bool> RefreshTokenAsync()
        {
            try
            {
                var refreshToken = await GetRefreshTokenAsync();
                if (string.IsNullOrEmpty(refreshToken))
                {
                    return false;
                }

                var requestMessage = new HttpRequestMessage(HttpMethod.Post, "/api/v1/auth/refresh")
                {
                    Headers = { Authorization = new AuthenticationHeaderValue("Bearer", refreshToken) }
                };

                var response = await _httpClient.SendAsync(requestMessage);

                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
                    if (result != null && result.ContainsKey("access_token"))
                    {
                        var newAccessToken = result["access_token"]?.ToString();
                        if (!string.IsNullOrEmpty(newAccessToken))
                        {
                            await _localStorage.SetItemAsync(TOKEN_KEY, newAccessToken);
                            return true;
                        }
                    }
                }

                // If refresh fails, clear all tokens
                await LogoutAsync();
                return false;
            }
            catch (Exception)
            {
                await LogoutAsync();
                return false;
            }
        }

        /// <summary>
        /// Get current user from storage
        /// </summary>
        public async Task<UserModel?> GetCurrentUserAsync()
        {
            return await _localStorage.GetItemAsync<UserModel>(USER_KEY);
        }

        /// <summary>
        /// Check if user is authenticated
        /// </summary>
        public async Task<bool> IsAuthenticatedAsync()
        {
            var token = await GetTokenAsync();
            return !string.IsNullOrEmpty(token);
        }
    }
}
