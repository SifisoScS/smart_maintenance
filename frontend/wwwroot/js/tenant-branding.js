/**
 * Tenant Branding - Dynamically apply tenant colors and logo
 *
 * This script applies tenant-specific branding to the UI using CSS custom properties
 * and dynamically updates the logo image.
 */

window.applyTenantBranding = function(branding) {
    console.log('Applying tenant branding:', branding);

    if (!branding) {
        console.warn('No branding provided');
        return;
    }

    // Apply CSS custom properties for colors
    const root = document.documentElement;

    if (branding.primaryColor) {
        root.style.setProperty('--tenant-primary-color', branding.primaryColor);
        root.style.setProperty('--primary-color', branding.primaryColor);

        // Generate lighter and darker variations
        const primaryRgb = hexToRgb(branding.primaryColor);
        if (primaryRgb) {
            root.style.setProperty('--tenant-primary-rgb', `${primaryRgb.r}, ${primaryRgb.g}, ${primaryRgb.b}`);
            root.style.setProperty('--tenant-primary-light', lightenColor(branding.primaryColor, 20));
            root.style.setProperty('--tenant-primary-dark', darkenColor(branding.primaryColor, 20));
        }
    }

    if (branding.secondaryColor) {
        root.style.setProperty('--tenant-secondary-color', branding.secondaryColor);
        root.style.setProperty('--secondary-color', branding.secondaryColor);

        // Generate lighter and darker variations
        const secondaryRgb = hexToRgb(branding.secondaryColor);
        if (secondaryRgb) {
            root.style.setProperty('--tenant-secondary-rgb', `${secondaryRgb.r}, ${secondaryRgb.g}, ${secondaryRgb.b}`);
            root.style.setProperty('--tenant-secondary-light', lightenColor(branding.secondaryColor, 20));
            root.style.setProperty('--tenant-secondary-dark', darkenColor(branding.secondaryColor, 20));
        }
    }

    // Apply gradient backgrounds using tenant colors
    if (branding.primaryColor && branding.secondaryColor) {
        const gradient = `linear-gradient(135deg, ${branding.primaryColor} 0%, ${branding.secondaryColor} 100%)`;
        root.style.setProperty('--tenant-gradient', gradient);
    }

    // Update logo if provided
    if (branding.logoUrl) {
        updateTenantLogo(branding.logoUrl);
    } else {
        removeTenantLogo();
    }

    console.log('Tenant branding applied successfully');
};

/**
 * Update tenant logo in the UI
 */
function updateTenantLogo(logoUrl) {
    // Find all elements with tenant-logo class
    const logoElements = document.querySelectorAll('.tenant-logo');

    logoElements.forEach(element => {
        if (element.tagName === 'IMG') {
            element.src = logoUrl;
            element.style.display = 'block';
        } else {
            // Create img if element is a container
            let img = element.querySelector('img');
            if (!img) {
                img = document.createElement('img');
                img.alt = 'Tenant Logo';
                img.style.maxWidth = '100%';
                img.style.maxHeight = '100%';
                img.style.objectFit = 'contain';
                element.appendChild(img);
            }
            img.src = logoUrl;
            element.style.display = 'block';
        }
    });
}

/**
 * Remove tenant logo from UI
 */
function removeTenantLogo() {
    const logoElements = document.querySelectorAll('.tenant-logo');
    logoElements.forEach(element => {
        element.style.display = 'none';
    });
}

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex) {
    // Remove # if present
    hex = hex.replace(/^#/, '');

    // Parse hex values
    if (hex.length === 3) {
        hex = hex.split('').map(char => char + char).join('');
    }

    const num = parseInt(hex, 16);
    return {
        r: (num >> 16) & 255,
        g: (num >> 8) & 255,
        b: num & 255
    };
}

/**
 * Lighten a hex color by a percentage
 */
function lightenColor(hex, percent) {
    const rgb = hexToRgb(hex);
    if (!rgb) return hex;

    const amt = Math.round(2.55 * percent);
    const r = Math.min(255, rgb.r + amt);
    const g = Math.min(255, rgb.g + amt);
    const b = Math.min(255, rgb.b + amt);

    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/**
 * Darken a hex color by a percentage
 */
function darkenColor(hex, percent) {
    const rgb = hexToRgb(hex);
    if (!rgb) return hex;

    const amt = Math.round(2.55 * percent);
    const r = Math.max(0, rgb.r - amt);
    const g = Math.max(0, rgb.g - amt);
    const b = Math.max(0, rgb.b - amt);

    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
}

/**
 * Get current tenant branding from CSS
 */
window.getCurrentBranding = function() {
    const root = document.documentElement;
    const style = getComputedStyle(root);

    return {
        primaryColor: style.getPropertyValue('--tenant-primary-color').trim() || '#667eea',
        secondaryColor: style.getPropertyValue('--tenant-secondary-color').trim() || '#764ba2'
    };
};

console.log('Tenant branding script loaded');
