// Pilot - Main JavaScript File
// =============================================================================

// Global helpers
window.getCsrfTokenGlobal = function() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    // Fall back to meta tag
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
};

window.showNotificationGlobal = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 280px; max-width: 480px;';
    notification.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(notification);
    setTimeout(() => { if (notification.parentNode) notification.remove(); }, 4000);
};

window.addToWishlist = function(productId, btnElement = null) {
    fetch(`/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': window.getCsrfTokenGlobal(),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(res => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
    })
    .then(data => {
        if (data.success) {
            window.showNotificationGlobal(data.message, 'success');
            if (btnElement) {
                if (data.is_favorite) {
                    btnElement.classList.remove('text-white', 'btn-outline-white');
                    btnElement.classList.add('text-danger');
                    if (btnElement.classList.contains('btn') && !btnElement.classList.contains('btn-link')) {
                        btnElement.classList.add('btn-outline-danger');
                    }
                    const icon = btnElement.querySelector('i');
                    if (icon) { icon.classList.remove('far'); icon.classList.add('fas'); }
                } else {
                    btnElement.classList.remove('text-danger', 'btn-outline-danger');
                    btnElement.classList.add('text-white');
                    if (btnElement.classList.contains('btn') && !btnElement.classList.contains('btn-link')) {
                        btnElement.classList.add('btn-outline-white');
                    }
                    const icon = btnElement.querySelector('i');
                    if (icon) { icon.classList.remove('fas'); icon.classList.add('far'); }
                }
            }
        } else {
            window.showNotificationGlobal(data.error || 'Could not update wishlist.', 'warning');
        }
    })
    .catch(err => {
        console.error('Wishlist error:', err);
        window.showNotificationGlobal('Could not update wishlist. Please try again.', 'warning');
    });
};

// Global helpers

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initCartFunctionality();
    initProductInteractions();
    initFormValidation();
    initAnimations();
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Animations on scroll
function initAnimations() {
    // Initialize Category Swiper
    if (document.querySelector('.category-swiper')) {
        new Swiper('.category-swiper', {
            slidesPerView: 1.2,
            spaceBetween: 20,
            freeMode: true,
            grabCursor: true,
            navigation: {
                nextEl: '.swiper-next-cat',
                prevEl: '.swiper-prev-cat',
            },
            breakpoints: {
                480: {
                    slidesPerView: 2.2,
                    spaceBetween: 25,
                },
                768: {
                    slidesPerView: 3.2,
                    spaceBetween: 30,
                },
                1024: {
                    slidesPerView: 4.2,
                    spaceBetween: 35,
                },
                1400: {
                    slidesPerView: 5.2,
                    spaceBetween: 40,
                }
            }
        });
    }

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // If it has fade-in-up, make it visible
                if (entry.target.classList.contains('fade-in-up')) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in-up, .animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Cart Management
// =============================================================================
function initCartFunctionality() {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });
    
    // Update cart quantity buttons
    document.querySelectorAll('.update-cart-btn').forEach(button => {
        button.addEventListener('click', handleUpdateCart);
    });
    
    // Remove from cart buttons
    document.querySelectorAll('.remove-cart-btn').forEach(button => {
        button.addEventListener('click', handleRemoveFromCart);
    });
}

async function handleAddToCart(event) {
    event.preventDefault();
    
    const button = event.currentTarget;
    const productId = button.dataset.productId;
    const quantity = getSelectedQuantity();
    const customization = getCustomizationText();
    
    // Get selected size and color
    const selectedSize = document.querySelector('.size-option.active')?.dataset.size;
    const selectedColor = document.querySelector('.color-option.active')?.dataset.color;
    
    // Validate selections
    if (!validateProductSelection()) {
        return;
    }
    
    // Show loading state
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ADDING...';
    
    try {
        const response = await fetch('/orders/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                product_id: productId,
                size: selectedSize,
                color: selectedColor,
                quantity: quantity,
                customization_text: customization
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Product added to cart successfully!', 'success');
            updateCartCount(data.cart_total);
            
            // Reset form if needed
            resetProductSelections();
        } else {
            showNotification(data.error || 'Failed to add product to cart', 'error');
        }
        
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Something went wrong. Please try again.', 'error');
    } finally {
        // Reset button state
        button.disabled = false;
        button.innerHTML = 'ADD TO CART';
    }
}

async function handleUpdateCart(event) {
    event.preventDefault();
    
    const button = event.currentTarget;
    const itemId = button.dataset.itemId;
    const quantityInput = document.querySelector(`input[data-item-id="${itemId}"]`);
    const quantity = parseInt(quantityInput.value);
    
    if (quantity < 1) {
        showNotification('Quantity must be at least 1', 'error');
        return;
    }
    
    try {
        const response = await fetch('/orders/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: quantity
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateCartCount(data.cart_total);
            updateCartTotal(data.total);
            showNotification('Cart updated successfully!', 'success');
            // If on cart page, we might want to reload to update all totals or use AJAX to update specifically
            if (window.location.pathname.includes('/cart/')) {
                location.reload();
            }
        } else {
            showNotification(data.error || 'Failed to update cart', 'error');
        }
        
    } catch (error) {
        console.error('Error updating cart:', error);
        showNotification('Something went wrong. Please try again.', 'error');
    }
}

async function handleRemoveFromCart(event) {
    event.preventDefault();
    
    if (!confirm('Are you sure you want to remove this item from your cart?')) {
        return;
    }
    
    const button = event.currentTarget;
    const itemId = button.dataset.itemId;
    
    try {
        const response = await fetch(`/orders/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Remove item from DOM
            const cartItem = button.closest('.cart-item');
            if (cartItem) {
                cartItem.remove();
            }
            
            showNotification('Item removed from cart', 'success');
            updateCartCount();
            
            // Reload page if cart is empty
            if (document.querySelectorAll('.cart-item').length === 0) {
                location.reload();
            }
        } else {
            showNotification(data.error || 'Failed to remove item', 'error');
        }
        
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('Something went wrong. Please try again.', 'error');
    }
}

// Product Interactions
// =============================================================================
function initProductInteractions() {
    // Image gallery
    initImageGallery();
    
    // Size and color selectors
    initVariantSelectors();
    
    // Quantity selectors
    initQuantitySelectors();
}

function initImageGallery() {
    const mainImage = document.querySelector('.product-main-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    
    if (!mainImage || thumbnails.length === 0) return;
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Update main image
            const newImageSrc = this.src.replace('-thumb', '');
            mainImage.src = newImageSrc;
            
            // Update active thumbnail
            thumbnails.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function initVariantSelectors() {
    // Size selectors
    document.querySelectorAll('.size-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.size-option').forEach(o => o.classList.remove('active'));
            this.classList.add('active');
            updateVariantInfo();
        });
    });
    
    // Color selectors
    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.color-option').forEach(o => o.classList.remove('active'));
            this.classList.add('active');
            updateVariantInfo();
        });
    });
}

function initQuantitySelectors() {
    document.querySelectorAll('.quantity-minus').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.nextElementSibling;
            const currentValue = parseInt(input.value);
            if (currentValue > 1) {
                input.value = currentValue - 1;
            }
        });
    });
    
    document.querySelectorAll('.quantity-plus').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const currentValue = parseInt(input.value);
            const maxValue = parseInt(input.getAttribute('max')) || 999;
            if (currentValue < maxValue) {
                input.value = currentValue + 1;
            } else {
                showNotification(`Maximum quantity available: ${maxValue}`, 'warning');
            }
        });
    });
}

async function updateVariantInfo() {
    const selectedSize = document.querySelector('.size-option.active')?.dataset.size;
    const selectedColor = document.querySelector('.color-option.active')?.dataset.color;
    const productId = document.querySelector('[data-product-id]')?.dataset.productId;
    
    if (!productId || (!selectedSize && !selectedColor)) return;
    
    try {
        const response = await fetch(`/api/product-variants/${productId}/`);
        const data = await response.json();
        
        if (data.success) {
            updatePriceAndStock(data.variants, selectedSize, selectedColor);
        }
    } catch (error) {
        console.error('Error fetching variant info:', error);
    }
}

function updatePriceAndStock(variants, selectedSize, selectedColor) {
    const variant = variants.find(v => 
        v.size === selectedSize && v.color === selectedColor
    );
    
    const priceElement = document.querySelector('.product-price');
    const stockElement = document.querySelector('.stock-info');
    const addToCartBtn = document.querySelector('.add-to-cart-btn');
    
    if (variant) {
        if (priceElement) {
            priceElement.textContent = `$${variant.price}`;
        }
        
        if (stockElement) {
            stockElement.textContent = `${variant.stock} in stock`;
            stockElement.className = variant.stock > 0 ? 'stock-info in-stock' : 'stock-info out-of-stock';
        }
        
        if (addToCartBtn) {
            addToCartBtn.disabled = variant.stock === 0;
            addToCartBtn.textContent = variant.stock === 0 ? 'OUT OF STOCK' : 'ADD TO CART';
        }
    }
}

// Form Validation
// =============================================================================
function initFormValidation() {
    // Real-time validation
    document.querySelectorAll('input[required], select[required]').forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
}


function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    clearFieldError(field);
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
        return false;
    }
    
    return true;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorElement = field.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

// Utility Functions
// =============================================================================
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

function getSelectedVariant() {
    const selectedSize = document.querySelector('.size-option.active')?.dataset.size;
    const selectedColor = document.querySelector('.color-option.active')?.dataset.color;
    const productId = document.querySelector('[data-product-id]')?.dataset.productId;
    
    if (!selectedSize && !selectedColor) {
        return null;
    }
    
    // We'll fetch the variant ID from the server based on the selected size and color
    return null; // This will be handled by the AddToCartView
}

function getSelectedQuantity() {
    const quantityInput = document.querySelector('.quantity-input');
    return quantityInput ? parseInt(quantityInput.value) : 1;
}

function getCustomizationText() {
    const customizationInput = document.querySelector('.customization-input');
    return customizationInput ? customizationInput.value.trim() : '';
}

function validateProductSelection() {
    const sizeOptions = document.querySelectorAll('.size-option');
    const colorOptions = document.querySelectorAll('.color-option');
    
    if (sizeOptions.length > 0 && !document.querySelector('.size-option.active')) {
        showNotification('Please select a size', 'error');
        return false;
    }
    
    if (colorOptions.length > 0 && !document.querySelector('.color-option.active')) {
        showNotification('Please select a color', 'error');
        return false;
    }
    
    return true;
}

function resetProductSelections() {
    document.querySelectorAll('.size-option.active, .color-option.active').forEach(option => {
        option.classList.remove('active');
    });
    
    const quantityInput = document.querySelector('.quantity-input');
    if (quantityInput) {
        quantityInput.value = 1;
    }
    
    const customizationInput = document.querySelector('.customization-input');
    if (customizationInput) {
        customizationInput.value = '';
    }
}

function updateCartCount(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    
    if (count !== undefined && count !== null) {
        cartCountElements.forEach(element => {
            element.textContent = count;
        });
    } else {
        // Fetch current cart count
        fetch('/orders/cart/count/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const totalItems = data.cart_total !== undefined ? data.cart_total : 0;
                    cartCountElements.forEach(element => {
                        element.textContent = totalItems;
                    });
                }
            })
            .catch(error => console.error('Error fetching cart count:', error));
    }
}

function updateCartTotal(total) {
    const totalElements = document.querySelectorAll('.cart-total');
    totalElements.forEach(element => {
        element.textContent = `LE ${total}`;
    });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Loading states
function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'global-loader';
    loader.className = 'position-fixed w-100 h-100 d-flex align-items-center justify-content-center';
    loader.style.cssText = `
        top: 0;
        left: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 9999;
    `;
    
    loader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.remove();
    }
}
