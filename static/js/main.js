// Pharma-Express JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeQuantityControls();
    initializeCartUpdates();
    initializeSearch();
    initializePaymentMethods();
    initializeGeolocation();
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    });
});

// Quantity controls for product pages and cart
function initializeQuantityControls() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityInputs.forEach(input => {
        const minusBtn = input.parentElement.querySelector('.btn-quantity-minus');
        const plusBtn = input.parentElement.querySelector('.btn-quantity-plus');
        
        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 1;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    triggerQuantityChange(input);
                }
            });
        }
        
        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 1;
                const maxStock = parseInt(input.dataset.maxStock) || 999;
                if (currentValue < maxStock) {
                    input.value = currentValue + 1;
                    triggerQuantityChange(input);
                }
            });
        }
        
        input.addEventListener('change', () => {
            triggerQuantityChange(input);
        });
    });
}

function triggerQuantityChange(input) {
    const event = new Event('quantityChanged');
    input.dispatchEvent(event);
}

// Cart updates
function initializeCartUpdates() {
    const cartForm = document.getElementById('cart-form');
    if (cartForm) {
        const quantityInputs = cartForm.querySelectorAll('.quantity-input');
        
        quantityInputs.forEach(input => {
            input.addEventListener('quantityChanged', debounce(() => {
                updateCartItem(input);
            }, 1000));
        });
    }
}

function updateCartItem(input) {
    const cartItemId = input.dataset.cartItemId;
    const quantity = input.value;
    
    if (!cartItemId) return;
    
    // Show loading state
    input.disabled = true;
    const loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'loading';
    input.parentElement.appendChild(loadingSpinner);
    
    // Create form data
    const formData = new FormData();
    formData.append('cart_item_id', cartItemId);
    formData.append('quantity', quantity);
    
    fetch('/update_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            // Reload the page to show updated cart
            window.location.reload();
        } else {
            throw new Error('Erreur lors de la mise à jour');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la mise à jour du panier', 'danger');
    })
    .finally(() => {
        input.disabled = false;
        if (loadingSpinner) {
            loadingSpinner.remove();
        }
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const searchForm = document.getElementById('search-form');
    
    if (searchInput && searchForm) {
        searchInput.addEventListener('input', debounce(() => {
            if (searchInput.value.length >= 2 || searchInput.value.length === 0) {
                searchForm.submit();
            }
        }, 500));
    }
}

// Payment method selection
function initializePaymentMethods() {
    const paymentMethods = document.querySelectorAll('.payment-method');
    const paymentSelect = document.getElementById('payment_method');
    
    paymentMethods.forEach(method => {
        method.addEventListener('click', () => {
            // Remove selected class from all methods
            paymentMethods.forEach(m => m.classList.remove('selected'));
            
            // Add selected class to clicked method
            method.classList.add('selected');
            
            // Update hidden select
            if (paymentSelect) {
                paymentSelect.value = method.dataset.value;
            }
        });
    });
    
    // Initialize first method as selected
    if (paymentMethods.length > 0 && paymentSelect) {
        paymentMethods[0].classList.add('selected');
        paymentSelect.value = paymentMethods[0].dataset.value;
    }
}

// Geolocation for delivery address
function initializeGeolocation() {
    const getLocationBtn = document.getElementById('get-location-btn');
    const addressInput = document.getElementById('delivery_address');
    
    if (getLocationBtn && addressInput) {
        getLocationBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                getLocationBtn.disabled = true;
                getLocationBtn.innerHTML = '<div class="loading"></div> Localisation...';
                
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        
                        // Reverse geocoding (you would need a geocoding service)
                        // For now, just show coordinates
                        addressInput.value = `Coordonnées: ${lat.toFixed(6)}, ${lng.toFixed(6)}`;
                        
                        getLocationBtn.disabled = false;
                        getLocationBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Utiliser ma position';
                        
                        showAlert('Position détectée avec succès!', 'success');
                    },
                    (error) => {
                        console.error('Erreur de géolocalisation:', error);
                        showAlert('Erreur lors de la détection de votre position', 'warning');
                        
                        getLocationBtn.disabled = false;
                        getLocationBtn.innerHTML = '<i class="fas fa-map-marker-alt"></i> Utiliser ma position';
                    }
                );
            } else {
                showAlert('La géolocalisation n\'est pas supportée par votre navigateur', 'warning');
            }
        });
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

// Cart management
function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    
    fetch('/add_to_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            showAlert('Produit ajouté au panier!', 'success');
            updateCartCount();
        } else {
            throw new Error('Erreur lors de l\'ajout au panier');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showAlert('Erreur lors de l\'ajout au panier', 'danger');
    });
}

function updateCartCount() {
    // This would typically fetch the updated cart count
    // For now, we'll just reload the page component or update manually
    const cartBadge = document.querySelector('.cart-count');
    if (cartBadge) {
        const currentCount = parseInt(cartBadge.textContent) || 0;
        cartBadge.textContent = currentCount + 1;
    }
}

// Product filtering
function filterProducts(category = '', search = '') {
    const url = new URL(window.location.href);
    
    if (category) {
        url.searchParams.set('category', category);
    } else {
        url.searchParams.delete('category');
    }
    
    if (search) {
        url.searchParams.set('search', search);
    } else {
        url.searchParams.delete('search');
    }
    
    url.searchParams.delete('page'); // Reset pagination
    
    window.location.href = url.toString();
}

// Form validation
function validateCheckoutForm() {
    const form = document.getElementById('checkout-form');
    if (!form) return true;
    
    const required = form.querySelectorAll('[required]');
    let isValid = true;
    
    required.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Validate phone number format
    const phoneField = form.querySelector('[name="payment_phone"]');
    if (phoneField && phoneField.value) {
        const phoneRegex = /^\+243[0-9]{9}$/;
        if (!phoneRegex.test(phoneField.value)) {
            phoneField.classList.add('is-invalid');
            showAlert('Le numéro de téléphone doit être au format +243XXXXXXXXX', 'warning');
            isValid = false;
        }
    }
    
    return isValid;
}

// Initialize tooltips and popovers (Bootstrap)
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
