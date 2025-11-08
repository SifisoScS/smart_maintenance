using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using frontend;
using frontend.Services;
using frontend.Services.Interfaces;
using Blazored.LocalStorage;
using Blazored.Toast;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// Configure HttpClient with Flask backend base address
builder.Services.AddScoped(sp => new HttpClient
{
    BaseAddress = new Uri("http://localhost:5001/") // Flask backend URL with trailing slash
});

// Add Blazored packages
builder.Services.AddBlazoredLocalStorage();
builder.Services.AddBlazoredToast();

// Register services with Dependency Injection
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<IApiService, ApiService>();

// Add authorization (for @attribute [Authorize])
builder.Services.AddAuthorizationCore();

await builder.Build().RunAsync();
