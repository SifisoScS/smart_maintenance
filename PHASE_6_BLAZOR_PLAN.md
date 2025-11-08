# Phase 6: Blazor Frontend Implementation Plan
## Building the WebAssembly Frontend with MVVM Architecture

**Status:** 🚀 **READY TO START**
**Dependencies:** Phase 5 (Event-Driven Backend) ✅ Complete
**Duration:** 4-5 days
**Focus:** Component-based UI, MVVM pattern, API integration

---

## 📋 Overview

Build a **Blazor WebAssembly** frontend that consumes the Flask REST API, demonstrating:
- **MVVM Pattern** for clean separation of UI and logic
- **Dependency Injection** using Blazor's built-in DI container
- **Repository Pattern** (frontend) for API abstraction
- **Component-based architecture** for reusability
- **Role-based routing** and authentication

---

## 🎯 Implementation Steps

### Step 1: Project Setup & Structure (Day 1)

#### 1.1 Create Blazor WebAssembly Project

```bash
cd "C:\users\sifisos\smart projects\smart_maintenance"
dotnet new blazorwasm -o frontend --pwa
cd frontend
```

#### 1.2 Install Required NuGet Packages

```bash
dotnet add package Microsoft.AspNetCore.Components.WebAssembly.Authentication
dotnet add package Blazored.LocalStorage
dotnet add package Blazored.Toast
dotnet add package System.Net.Http.Json
dotnet add package Microsoft.Extensions.Http
```

#### 1.3 Project Structure

```
frontend/
├── wwwroot/
│   ├── css/
│   ├── js/
│   └── index.html
├── Models/              # DTOs matching backend
│   ├── UserModel.cs
│   ├── RequestModel.cs
│   ├── AssetModel.cs
│   └── NotificationModel.cs
├── Services/            # API and business logic
│   ├── Interfaces/
│   │   ├── IApiService.cs
│   │   ├── IAuthService.cs
│   │   └── IStateService.cs
│   ├── ApiService.cs
│   ├── AuthService.cs
│   └── StateService.cs
├── Pages/               # Main views (routable)
│   ├── Index.razor
│   ├── Login.razor
│   ├── Register.razor
│   ├── Dashboard.razor
│   ├── Requests/
│   │   ├── RequestList.razor
│   │   ├── RequestDetails.razor
│   │   └── CreateRequest.razor
│   ├── Assets/
│   │   ├── AssetList.razor
│   │   └── AssetDetails.razor
│   └── Profile.razor
├── Shared/              # Reusable components
│   ├── Components/
│   │   ├── RequestCard.razor
│   │   ├── StatusBadge.razor
│   │   ├── LoadingSpinner.razor
│   │   └── ErrorMessage.razor
│   ├── MainLayout.razor
│   ├── NavMenu.razor
│   └── LoginDisplay.razor
├── ViewModels/          # MVVM view models (optional for complex pages)
│   ├── RequestViewModel.cs
│   └── DashboardViewModel.cs
└── Program.cs           # DI configuration
```

---

### Step 2: Models & DTOs (Day 1)

Create C# models matching the backend API responses.

#### 2.1 UserModel.cs

```csharp
namespace SmartMaintenance.Models
{
    public class UserModel
    {
        public int Id { get; set; }
        public string Email { get; set; }
        public string FullName { get; set; }
        public string Role { get; set; }
        public bool IsActive { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public class LoginRequest
    {
        public string Email { get; set; }
        public string Password { get; set; }
    }

    public class LoginResponse
    {
        public string AccessToken { get; set; }
        public UserModel User { get; set; }
    }

    public class RegisterRequest
    {
        public string Email { get; set; }
        public string Password { get; set; }
        public string FullName { get; set; }
        public string Role { get; set; } = "client";
    }
}
```

#### 2.2 RequestModel.cs

```csharp
namespace SmartMaintenance.Models
{
    public class RequestModel
    {
        public int Id { get; set; }
        public string Type { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Status { get; set; }
        public string Priority { get; set; }
        public int SubmitterId { get; set; }
        public int? AssignedTechnicianId { get; set; }
        public int AssetId { get; set; }
        public decimal? EstimatedHours { get; set; }
        public decimal? ActualHours { get; set; }
        public string CompletionNotes { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Navigation properties
        public UserModel Submitter { get; set; }
        public UserModel AssignedTechnician { get; set; }
        public AssetModel Asset { get; set; }
    }

    public class CreateRequestDto
    {
        public string RequestType { get; set; }
        public int SubmitterId { get; set; }
        public int AssetId { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Priority { get; set; } = "medium";
    }
}
```

#### 2.3 AssetModel.cs

```csharp
namespace SmartMaintenance.Models
{
    public class AssetModel
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string AssetType { get; set; }
        public string Location { get; set; }
        public string Condition { get; set; }
        public string Status { get; set; }
        public DateTime PurchaseDate { get; set; }
        public decimal? PurchasePrice { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}
```

---

### Step 3: Services Layer (Day 2)

#### 3.1 IAuthService.cs (Interface)

```csharp
namespace SmartMaintenance.Services.Interfaces
{
    public interface IAuthService
    {
        Task<LoginResponse> LoginAsync(LoginRequest request);
        Task<ApiResponse> RegisterAsync(RegisterRequest request);
        Task LogoutAsync();
        Task<string> GetTokenAsync();
        Task<UserModel> GetCurrentUserAsync();
        bool IsAuthenticated();
    }
}
```

#### 3.2 AuthService.cs (Implementation)

```csharp
using Blazored.LocalStorage;
using System.Net.Http.Json;

namespace SmartMaintenance.Services
{
    public class AuthService : IAuthService
    {
        private readonly HttpClient _httpClient;
        private readonly ILocalStorageService _localStorage;
        private const string TOKEN_KEY = "authToken";
        private const string USER_KEY = "currentUser";

        public AuthService(HttpClient httpClient, ILocalStorageService localStorage)
        {
            _httpClient = httpClient;
            _localStorage = localStorage;
        }

        public async Task<LoginResponse> LoginAsync(LoginRequest request)
        {
            var response = await _httpClient.PostAsJsonAsync("/api/v1/auth/login", request);

            if (response.IsSuccessStatusCode)
            {
                var loginResponse = await response.Content.ReadFromJsonAsync<LoginResponse>();
                await _localStorage.SetItemAsync(TOKEN_KEY, loginResponse.AccessToken);
                await _localStorage.SetItemAsync(USER_KEY, loginResponse.User);
                return loginResponse;
            }

            throw new Exception("Login failed");
        }

        public async Task<ApiResponse> RegisterAsync(RegisterRequest request)
        {
            var response = await _httpClient.PostAsJsonAsync("/api/v1/auth/register", request);
            return await response.Content.ReadFromJsonAsync<ApiResponse>();
        }

        public async Task LogoutAsync()
        {
            await _localStorage.RemoveItemAsync(TOKEN_KEY);
            await _localStorage.RemoveItemAsync(USER_KEY);
        }

        public async Task<string> GetTokenAsync()
        {
            return await _localStorage.GetItemAsync<string>(TOKEN_KEY);
        }

        public async Task<UserModel> GetCurrentUserAsync()
        {
            return await _localStorage.GetItemAsync<UserModel>(USER_KEY);
        }

        public bool IsAuthenticated()
        {
            // Check if token exists (synchronous check for routing)
            return _localStorage.GetItemAsync<string>(TOKEN_KEY).Result != null;
        }
    }
}
```

#### 3.3 IApiService.cs (Interface)

```csharp
namespace SmartMaintenance.Services.Interfaces
{
    public interface IApiService
    {
        // Requests
        Task<List<RequestModel>> GetRequestsAsync();
        Task<RequestModel> GetRequestByIdAsync(int id);
        Task<ApiResponse> CreateRequestAsync(CreateRequestDto request);
        Task<ApiResponse> AssignRequestAsync(int requestId, int technicianId);
        Task<ApiResponse> UpdateRequestStatusAsync(int requestId, string status);
        Task<ApiResponse> CompleteRequestAsync(int requestId, string notes, decimal hours);

        // Assets
        Task<List<AssetModel>> GetAssetsAsync();
        Task<AssetModel> GetAssetByIdAsync(int id);
        Task<ApiResponse> UpdateAssetConditionAsync(int assetId, string condition);

        // Users
        Task<List<UserModel>> GetUsersAsync();
        Task<List<UserModel>> GetTechniciansAsync();
        Task<UserModel> GetUserByIdAsync(int id);
    }
}
```

#### 3.4 ApiService.cs (Implementation)

```csharp
using System.Net.Http.Json;
using System.Net.Http.Headers;

namespace SmartMaintenance.Services
{
    public class ApiService : IApiService
    {
        private readonly HttpClient _httpClient;
        private readonly IAuthService _authService;

        public ApiService(HttpClient httpClient, IAuthService authService)
        {
            _httpClient = httpClient;
            _authService = authService;
        }

        private async Task SetAuthHeaderAsync()
        {
            var token = await _authService.GetTokenAsync();
            if (!string.IsNullOrEmpty(token))
            {
                _httpClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", token);
            }
        }

        // Requests
        public async Task<List<RequestModel>> GetRequestsAsync()
        {
            await SetAuthHeaderAsync();
            return await _httpClient.GetFromJsonAsync<List<RequestModel>>("/api/v1/requests");
        }

        public async Task<RequestModel> GetRequestByIdAsync(int id)
        {
            await SetAuthHeaderAsync();
            return await _httpClient.GetFromJsonAsync<RequestModel>($"/api/v1/requests/{id}");
        }

        public async Task<ApiResponse> CreateRequestAsync(CreateRequestDto request)
        {
            await SetAuthHeaderAsync();
            var response = await _httpClient.PostAsJsonAsync("/api/v1/requests", request);
            return await response.Content.ReadFromJsonAsync<ApiResponse>();
        }

        // ... implement other methods similarly
    }
}
```

---

### Step 4: Pages & Components (Day 3)

#### 4.1 Login.razor

```razor
@page "/login"
@inject IAuthService AuthService
@inject NavigationManager Navigation
@inject IToastService ToastService

<div class="login-container">
    <div class="card">
        <div class="card-header">
            <h3>Smart Maintenance Login</h3>
        </div>
        <div class="card-body">
            <EditForm Model="@loginRequest" OnValidSubmit="HandleLogin">
                <DataAnnotationsValidator />
                <ValidationSummary />

                <div class="form-group">
                    <label>Email</label>
                    <InputText @bind-Value="loginRequest.Email" class="form-control" />
                </div>

                <div class="form-group">
                    <label>Password</label>
                    <InputText type="password" @bind-Value="loginRequest.Password" class="form-control" />
                </div>

                <button type="submit" class="btn btn-primary" disabled="@isLoading">
                    @if (isLoading)
                    {
                        <span class="spinner-border spinner-border-sm"></span>
                    }
                    Login
                </button>
            </EditForm>

            <div class="mt-3">
                <a href="/register">Don't have an account? Register</a>
            </div>
        </div>
    </div>
</div>

@code {
    private LoginRequest loginRequest = new();
    private bool isLoading = false;

    private async Task HandleLogin()
    {
        isLoading = true;
        try
        {
            var response = await AuthService.LoginAsync(loginRequest);
            ToastService.ShowSuccess("Login successful!");
            Navigation.NavigateTo("/dashboard");
        }
        catch (Exception ex)
        {
            ToastService.ShowError($"Login failed: {ex.Message}");
        }
        finally
        {
            isLoading = false;
        }
    }
}
```

#### 4.2 Dashboard.razor

```razor
@page "/dashboard"
@inject IApiService ApiService
@inject IAuthService AuthService
@attribute [Authorize]

<div class="dashboard">
    <h2>Dashboard</h2>

    @if (currentUser != null)
    {
        <div class="welcome-message">
            <h4>Welcome, @currentUser.FullName</h4>
            <p>Role: @currentUser.Role</p>
        </div>

        @if (currentUser.Role == "admin")
        {
            <AdminDashboard Requests="@requests" />
        }
        else if (currentUser.Role == "technician")
        {
            <TechnicianDashboard Requests="@myRequests" />
        }
        else
        {
            <ClientDashboard Requests="@myRequests" />
        }
    }
</div>

@code {
    private UserModel currentUser;
    private List<RequestModel> requests = new();
    private List<RequestModel> myRequests = new();

    protected override async Task OnInitializedAsync()
    {
        currentUser = await AuthService.GetCurrentUserAsync();
        requests = await ApiService.GetRequestsAsync();

        if (currentUser.Role == "technician")
        {
            myRequests = requests.Where(r => r.AssignedTechnicianId == currentUser.Id).ToList();
        }
        else if (currentUser.Role == "client")
        {
            myRequests = requests.Where(r => r.SubmitterId == currentUser.Id).ToList();
        }
    }
}
```

#### 4.3 RequestCard.razor (Component)

```razor
<div class="request-card @GetPriorityClass()">
    <div class="card-header">
        <h5>@Request.Title</h5>
        <StatusBadge Status="@Request.Status" />
    </div>
    <div class="card-body">
        <p class="description">@Request.Description</p>
        <div class="meta-info">
            <span><i class="icon-type"></i> @Request.Type</span>
            <span><i class="icon-priority"></i> @Request.Priority</span>
            <span><i class="icon-date"></i> @Request.CreatedAt.ToString("MMM dd, yyyy")</span>
        </div>
        @if (Request.AssignedTechnician != null)
        {
            <div class="technician-info">
                Assigned to: @Request.AssignedTechnician.FullName
            </div>
        }
    </div>
    <div class="card-footer">
        <button class="btn btn-sm btn-primary" @onclick="() => OnViewDetails.InvokeAsync(Request.Id)">
            View Details
        </button>
    </div>
</div>

@code {
    [Parameter] public RequestModel Request { get; set; }
    [Parameter] public EventCallback<int> OnViewDetails { get; set; }

    private string GetPriorityClass()
    {
        return Request.Priority.ToLower() switch
        {
            "high" => "priority-high",
            "medium" => "priority-medium",
            "low" => "priority-low",
            _ => ""
        };
    }
}
```

---

### Step 5: DI Configuration (Day 2)

#### Program.cs

```csharp
using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using SmartMaintenance;
using SmartMaintenance.Services;
using SmartMaintenance.Services.Interfaces;
using Blazored.LocalStorage;
using Blazored.Toast;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Configure HttpClient with base address
builder.Services.AddScoped(sp => new HttpClient
{
    BaseAddress = new Uri("http://localhost:5000") // Flask backend URL
});

// Add Blazored packages
builder.Services.AddBlazoredLocalStorage();
builder.Services.AddBlazoredToast();

// Register services
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IApiService, ApiService>();
builder.Services.AddScoped<IStateService, StateService>();

// Add authorization
builder.Services.AddAuthorizationCore();

await builder.Build().RunAsync();
```

---

### Step 6: Routing & Authorization (Day 4)

#### App.razor

```razor
<Router AppAssembly="@typeof(App).Assembly">
    <Found Context="routeData">
        <AuthorizeRouteView RouteData="@routeData" DefaultLayout="@typeof(MainLayout)">
            <NotAuthorized>
                @if (context.User.Identity?.IsAuthenticated != true)
                {
                    <RedirectToLogin />
                }
                else
                {
                    <p role="alert">You are not authorized to access this resource.</p>
                }
            </NotAuthorized>
        </AuthorizeRouteView>
        <FocusOnNavigate RouteData="@routeData" Selector="h1" />
    </Found>
    <NotFound>
        <PageTitle>Not found</PageTitle>
        <LayoutView Layout="@typeof(MainLayout)">
            <p role="alert">Sorry, there's nothing at this address.</p>
        </LayoutView>
    </NotFound>
</Router>
```

---

### Step 7: Styling & UX Polish (Day 5)

#### wwwroot/css/app.css

```css
/* Modern, clean design */
:root {
    --primary-color: #4f46e5;
    --secondary-color: #10b981;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --border-color: #e5e7eb;
}

.request-card {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.3s;
}

.request-card:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.priority-high {
    border-left: 4px solid var(--danger-color);
}

.priority-medium {
    border-left: 4px solid var(--warning-color);
}

.priority-low {
    border-left: 4px solid var(--secondary-color);
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.875rem;
    font-weight: 600;
}

.status-submitted { background-color: #dbeafe; color: #1e40af; }
.status-assigned { background-color: #fef3c7; color: #92400e; }
.status-in-progress { background-color: #e0e7ff; color: #3730a3; }
.status-completed { background-color: #d1fae5; color: #065f46; }
```

---

## 📊 Deliverables Checklist

### Core Infrastructure
- [ ] Blazor WebAssembly project created
- [ ] NuGet packages installed
- [ ] Project structure organized
- [ ] DI configured in Program.cs

### Models & DTOs
- [ ] UserModel, LoginRequest, RegisterRequest
- [ ] RequestModel, CreateRequestDto
- [ ] AssetModel
- [ ] ApiResponse wrapper

### Services
- [ ] IAuthService interface & implementation
- [ ] IApiService interface & implementation
- [ ] JWT token management (localStorage)
- [ ] Authenticated HTTP requests

### Pages
- [ ] Login.razor with form validation
- [ ] Register.razor
- [ ] Dashboard.razor (role-based)
- [ ] RequestList.razor with filtering
- [ ] RequestDetails.razor
- [ ] CreateRequest.razor form
- [ ] AssetList.razor (admin only)
- [ ] Profile.razor

### Components
- [ ] RequestCard.razor
- [ ] StatusBadge.razor
- [ ] LoadingSpinner.razor
- [ ] ErrorMessage.razor
- [ ] TechnicianSelector.razor
- [ ] AssetSelector.razor

### Routing & Auth
- [ ] AuthorizeRouteView configured
- [ ] RedirectToLogin component
- [ ] Role-based route guards
- [ ] MainLayout with NavMenu

### Styling
- [ ] Responsive CSS
- [ ] Component-specific styles
- [ ] Loading states
- [ ] Error handling UI

---

## 🧪 Testing Strategy

### Manual Testing
1. **Authentication Flow**
   - [ ] Register new user
   - [ ] Login with credentials
   - [ ] Token stored in localStorage
   - [ ] Logout clears token

2. **Request Management**
   - [ ] Create new request
   - [ ] View request list
   - [ ] View request details
   - [ ] Admin can assign technician
   - [ ] Technician can update status
   - [ ] Client can only see own requests

3. **Role-Based Access**
   - [ ] Admin sees all requests
   - [ ] Technician sees assigned requests
   - [ ] Client sees only their requests
   - [ ] Admin-only pages blocked for others

---

## 📈 Success Criteria

- [ ] **Authentication**: Users can login and access protected pages
- [ ] **CRUD Operations**: All request/asset operations work
- [ ] **Role-Based UI**: Different dashboards for each role
- [ ] **Responsive Design**: Works on mobile, tablet, desktop
- [ ] **Error Handling**: Friendly error messages displayed
- [ ] **Loading States**: Spinners during API calls
- [ ] **MVVM Pattern**: Clean separation of concerns
- [ ] **DI Pattern**: Services injected properly

---

## 🚀 Next Steps After Phase 6

1. **Phase 7: Integration & Polish**
   - Real-time notifications (SignalR)
   - Advanced analytics dashboard
   - Image upload for requests
   - PDF export functionality

2. **Phase 8: Testing & Documentation**
   - bUnit tests for components
   - Service integration tests
   - User documentation
   - Deployment guide

---

**Ready to build the frontend!** 🎉
