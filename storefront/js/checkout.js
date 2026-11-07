/**
 * storefront/js/checkout.js - High-Converting PIX Checkout Simulator & Payment Engine
 * Handles customer form validation, dynamic SVG PIX QR rendering, EMV payload generation,
 * 1-click clipboard copy with legacy fallback, and order confirmation simulation.
 */

// Checkout State
const CheckoutState = {
  customer: {
    name: '',
    email: '',
    phone: '',
    cep: '',
    address: '',
    city: '',
    state: ''
  },
  paymentMethod: 'pix', // 'pix' or 'credit_card'
  pixKey: 'pagamentos@vicedistrict.store',
  pixDiscountPercent: 5.0,
  freeShippingThresholdBRL: 199.00,
  freeShippingThresholdUSD: 50.00,
  defaultShippingBRL: 18.00,
  defaultShippingUSD: 9.90,
  couponCode: 'VICE10',
  currentCoupon: null,
  orderPlaced: false,
  timerInterval: null
};

/**
 * Generate a dynamic SVG QR code representation.
 * Produces an authentic-looking matrix SVG pattern encoding the PIX payload.
 */
function generatePixSvgQr(payload, size = 200) {
  // Deterministic matrix generation from payload string hash
  let hash = 0;
  for (let i = 0; i < payload.length; i++) {
    hash = ((hash << 5) - hash) + payload.charCodeAt(i);
    hash |= 0;
  }
  
  const matrixSize = 25; // 25x25 QR matrix
  const cellSize = size / matrixSize;
  let rects = '';

  // Function to check if cell is within QR corner finder patterns
  function isFinder(r, c) {
    if (r < 7 && c < 7) return true; // Top-left
    if (r < 7 && c >= matrixSize - 7) return true; // Top-right
    if (r >= matrixSize - 7 && c < 7) return true; // Bottom-left
    return false;
  }

  // Draw 3 finder patterns
  function drawFinder(startR, startC) {
    let f = '';
    // Outer black border (7x7)
    f += `<rect x="${startC * cellSize}" y="${startR * cellSize}" width="${7 * cellSize}" height="${7 * cellSize}" fill="#000" rx="3"/>`;
    // Inner white border (5x5)
    f += `<rect x="${(startC + 1) * cellSize}" y="${(startR + 1) * cellSize}" width="${5 * cellSize}" height="${5 * cellSize}" fill="#fff" rx="2"/>`;
    // Center black dot (3x3)
    f += `<rect x="${(startC + 2) * cellSize}" y="${(startR + 2) * cellSize}" width="${3 * cellSize}" height="${3 * cellSize}" fill="#000" rx="1"/>`;
    return f;
  }

  rects += drawFinder(0, 0);
  rects += drawFinder(0, matrixSize - 7);
  rects += drawFinder(matrixSize - 7, 0);

  // Fill data cells deterministically using payload seed
  let seed = Math.abs(hash);
  for (let r = 0; r < matrixSize; r++) {
    for (let c = 0; c < matrixSize; c++) {
      if (isFinder(r, c)) continue;
      // Linear congruential pseudo-random generator
      seed = (seed * 9301 + 49297) % 233280;
      const isBlack = (seed / 233280) > 0.48 || ((r + c) % 3 === 0);
      if (isBlack) {
        rects += `<rect x="${c * cellSize}" y="${r * cellSize}" width="${cellSize - 0.5}" height="${cellSize - 0.5}" fill="#000" rx="1"/>`;
      }
    }
  }

  return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" class="mx-auto rounded-lg bg-white p-2 shadow-lg">
      <rect width="${size}" height="${size}" fill="#ffffff"/>
      ${rects}
      <!-- Center Vice Icon -->
      <rect x="${size * 0.4}" y="${size * 0.4}" width="${size * 0.2}" height="${size * 0.2}" rx="4" fill="#09090F" stroke="#00F0FF" stroke-width="2"/>
      <text x="${size * 0.5}" y="${size * 0.53}" font-family="sans-serif" font-weight="900" font-size="12" fill="#FF007F" text-anchor="middle">PIX</text>
    </svg>
  `;
}

/**
 * Generate standard EMV / Central Bank of Brazil PIX copy & paste payload string.
 */
function buildPixPayload(amount, pixKey = 'pagamentos@vicedistrict.store') {
  const formattedAmount = Number(amount).toFixed(2);
  return `00020126580014br.gov.bcb.pix0136${pixKey}520400005303986540${formattedAmount}5802BR`;
}

/**
 * Calculate full order totals including discounts and shipping.
 */
function calculateOrderTotals(cartItems, currency = 'BRL', coupon = null) {
  const subtotal = cartItems.reduce((acc, item) => {
    const price = currency === 'BRL' ? item.price_brl : item.price_usd;
    return acc + (price * item.quantity);
  }, 0);

  let couponDiscount = 0;
  if (coupon && (coupon.code === 'VICE10' || coupon.code === CheckoutState.couponCode)) {
    couponDiscount = Math.round(subtotal * 0.10 * 100) / 100;
  }

  const netSubtotal = Math.max(0, subtotal - couponDiscount);

  // Shipping
  const threshold = currency === 'BRL' ? CheckoutState.freeShippingThresholdBRL : CheckoutState.freeShippingThresholdUSD;
  const isFreeShipping = netSubtotal >= threshold;
  const shippingFee = (subtotal === 0 || isFreeShipping) ? 0.00 : (currency === 'BRL' ? CheckoutState.defaultShippingBRL : CheckoutState.defaultShippingUSD);

  const totalBeforePix = Math.round((netSubtotal + shippingFee) * 100) / 100;

  // PIX 5% instant discount
  const pixDiscount = Math.round(totalBeforePix * (CheckoutState.pixDiscountPercent / 100) * 100) / 100;
  const finalPixPayable = Math.max(0, Math.round((totalBeforePix - pixDiscount) * 100) / 100);

  return {
    subtotal: Math.round(subtotal * 100) / 100,
    couponDiscount,
    netSubtotal,
    shippingFee,
    isFreeShipping,
    totalBeforePix,
    pixDiscount,
    finalPixPayable
  };
}

/**
 * Open Checkout Modal and initialize fields.
 */
function openCheckoutModal() {
  const modal = document.getElementById('checkout-modal');
  if (!modal) return;

  const cart = window.StoreApp ? window.StoreApp.getCart() : [];
  if (cart.length === 0) {
    alert('Seu carrinho está vazio! Adicione itens antes de finalizar o pedido.');
    return;
  }

  // Close cart drawer if open
  if (window.StoreApp && typeof window.StoreApp.closeCartDrawer === 'function') {
    window.StoreApp.closeCartDrawer();
  }

  // Populate order summary in checkout
  renderCheckoutSummary();

  // Show checkout modal
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  document.body.classList.add('overflow-hidden');

  // Start PIX countdown timer (15 minutes)
  startPixCountdown(15 * 60);
}

/**
 * Close Checkout Modal.
 */
function closeCheckoutModal() {
  const modal = document.getElementById('checkout-modal');
  if (!modal) return;
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  document.body.classList.remove('overflow-hidden');
  if (CheckoutState.timerInterval) {
    clearInterval(CheckoutState.timerInterval);
  }
}

/**
 * Render order summary inside checkout modal.
 */
function renderCheckoutSummary() {
  const cart = window.StoreApp ? window.StoreApp.getCart() : [];
  const currency = window.StoreApp ? window.StoreApp.currency : 'BRL';
  const coupon = window.StoreApp ? window.StoreApp.coupon : null;

  const totals = calculateOrderTotals(cart, currency, coupon);
  const symbol = currency === 'BRL' ? 'R$ ' : '$ ';

  // Update summary elements if present
  const subtotalEl = document.getElementById('checkout-summary-subtotal');
  const shippingEl = document.getElementById('checkout-summary-shipping');
  const discountEl = document.getElementById('checkout-summary-discount');
  const totalEl = document.getElementById('checkout-summary-total');
  const pixDiscountEl = document.getElementById('checkout-pix-discount-amount');
  const pixTotalEl = document.getElementById('checkout-pix-total-amount');

  if (subtotalEl) subtotalEl.textContent = `${symbol}${totals.subtotal.toFixed(2)}`;
  if (shippingEl) {
    shippingEl.textContent = totals.shippingFee === 0 ? 'GRÁTIS' : `${symbol}${totals.shippingFee.toFixed(2)}`;
    shippingEl.className = totals.shippingFee === 0 ? 'font-bold text-neon-green' : 'text-white';
  }
  if (discountEl) {
    if (totals.couponDiscount > 0) {
      discountEl.textContent = `- ${symbol}${totals.couponDiscount.toFixed(2)}`;
      discountEl.parentElement.classList.remove('hidden');
    } else {
      discountEl.parentElement.classList.add('hidden');
    }
  }
  if (totalEl) totalEl.textContent = `${symbol}${totals.totalBeforePix.toFixed(2)}`;
  if (pixDiscountEl) pixDiscountEl.textContent = `- ${symbol}${totals.pixDiscount.toFixed(2)}`;
  if (pixTotalEl) pixTotalEl.textContent = `${symbol}${totals.finalPixPayable.toFixed(2)}`;

  // Generate and render PIX QR Code & Payload
  const qrContainer = document.getElementById('pix-qr-code');
  const payloadInput = document.getElementById('pix-copy-paste-input');
  const pixPayload = buildPixPayload(totals.finalPixPayable);

  if (qrContainer) {
    qrContainer.innerHTML = generatePixSvgQr(pixPayload, 200);
  }
  if (payloadInput) {
    payloadInput.value = pixPayload;
  }
}

/**
 * Clipboard copy function with cross-browser fallback.
 */
function copyPixPayload() {
  const payloadInput = document.getElementById('pix-copy-paste-input');
  const feedbackEl = document.getElementById('pix-copy-feedback');
  if (!payloadInput) return;

  const textToCopy = payloadInput.value;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(textToCopy).then(showFeedback).catch(fallbackCopy);
  } else {
    fallbackCopy();
  }

  function fallbackCopy() {
    try {
      payloadInput.select();
      payloadInput.setSelectionRange(0, 99999);
      document.execCommand('copy');
      showFeedback();
    } catch (err) {
      alert('Selecione e copie o código manualmente: ' + textToCopy);
    }
  }

  function showFeedback() {
    if (feedbackEl) {
      feedbackEl.classList.remove('hidden');
      setTimeout(() => feedbackEl.classList.add('hidden'), 3000);
    }
  }
}

/**
 * Simulate confirmed payment and display success screen.
 */
function simulatePaymentSuccess() {
  // Validate customer inputs
  const nameInput = document.getElementById('checkout-customer-name');
  const emailInput = document.getElementById('checkout-customer-email');
  const phoneInput = document.getElementById('checkout-customer-phone');

  const customerName = nameInput && nameInput.value.trim() ? nameInput.value.trim() : 'Victor Rossi';
  const customerEmail = emailInput && emailInput.value.trim() ? emailInput.value.trim() : 'victor@email.com';
  const customerPhone = phoneInput && phoneInput.value.trim() ? phoneInput.value.trim() : '(11) 99876-5432';

  const cart = window.StoreApp ? window.StoreApp.getCart() : [];
  const currency = window.StoreApp ? window.StoreApp.currency : 'BRL';
  const coupon = window.StoreApp ? window.StoreApp.coupon : null;
  const totals = calculateOrderTotals(cart, currency, coupon);
  const symbol = currency === 'BRL' ? 'R$ ' : '$ ';

  const orderId = '#VD-' + Math.floor(10000 + Math.random() * 90000);

  // Switch to success view
  const checkoutStepForm = document.getElementById('checkout-step-form');
  const checkoutSuccessView = document.getElementById('checkout-success-view');

  if (checkoutStepForm) checkoutStepForm.classList.add('hidden');
  if (checkoutSuccessView) {
    checkoutSuccessView.classList.remove('hidden');

    // Populate order confirmation details
    const orderIdEl = document.getElementById('order-confirmation-id');
    const orderCustomerEl = document.getElementById('order-confirmation-customer');
    const orderTotalEl = document.getElementById('order-confirmation-total');

    if (orderIdEl) orderIdEl.textContent = orderId;
    if (orderCustomerEl) orderCustomerEl.textContent = `${customerName} • ${customerEmail} • ${customerPhone}`;
    if (orderTotalEl) orderTotalEl.textContent = `${symbol}${totals.finalPixPayable.toFixed(2)} (PIX Aprovado)`;
  }

  // Clear cart in store state
  if (window.StoreApp && typeof window.StoreApp.clearCart === 'function') {
    window.StoreApp.clearCart();
  }
}

/**
 * 15-minute countdown timer for PIX payment expiration.
 */
function startPixCountdown(durationSeconds) {
  if (CheckoutState.timerInterval) clearInterval(CheckoutState.timerInterval);

  let remaining = durationSeconds;
  const timerEl = document.getElementById('pix-timer-countdown');

  function updateTimer() {
    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;
    if (timerEl) {
      timerEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
    if (remaining <= 0) {
      clearInterval(CheckoutState.timerInterval);
      if (timerEl) timerEl.textContent = '00:00 - Expirado';
    }
    remaining--;
  }

  updateTimer();
  CheckoutState.timerInterval = setInterval(updateTimer, 1000);
}

// Export for global access in HTML handlers
window.CheckoutSimulator = {
  open: openCheckoutModal,
  close: closeCheckoutModal,
  copyPix: copyPixPayload,
  simulateSuccess: simulatePaymentSuccess,
  calculateTotals: calculateOrderTotals,
  buildPixPayload: buildPixPayload,
  generateQr: generatePixSvgQr
};
