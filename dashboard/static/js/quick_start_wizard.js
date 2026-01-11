// Quick Start Wizard JavaScript
let currentStep = 1;
const totalSteps = 5;
let wizardData = {
    balance: '',
    riskPerTrade: '',
    strategy: '',
    hotkeysPracticed: false
};

document.addEventListener('DOMContentLoaded', () => {
    initWizard();
});

function initWizard() {
    updateProgress();
    updateStepVisibility();

    // Add event listeners
    document.querySelectorAll('.wizard-btn-next').forEach(btn => {
        btn.addEventListener('click', nextStep);
    });

    document.querySelectorAll('.wizard-btn-back').forEach(btn => {
        btn.addEventListener('click', prevStep);
    });
}

function updateProgress() {
    const progress = (currentStep / totalSteps) * 100;
    document.querySelector('.wizard-progress-bar').style.width = `${progress}%`;

    // Update step dots
    document.querySelectorAll('.step-dot').forEach((dot, index) => {
        const stepNum = index + 1;
        dot.classList.remove('active', 'completed');

        if (stepNum < currentStep) {
            dot.classList.add('completed');
        } else if (stepNum === currentStep) {
            dot.classList.add('active');
        }
    });
}

function updateStepVisibility() {
    document.querySelectorAll('.wizard-step').forEach((step, index) => {
        step.classList.remove('active');
        if (index + 1 === currentStep) {
            step.classList.add('active');
        }
    });
}

function nextStep() {
    if (!validateCurrentStep()) {
        return;
    }

    if (currentStep < totalSteps) {
        currentStep++;
        updateProgress();
        updateStepVisibility();
        saveStepData();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateProgress();
        updateStepVisibility();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function validateCurrentStep() {
    switch (currentStep) {
        case 1: // Balance step
            const balance = document.getElementById('wizard-balance').value;
            if (!balance || parseFloat(balance) <= 0) {
                alert('Please enter a valid balance');
                return false;
            }
            wizardData.balance = balance;
            return true;

        case 2: // Risk step
            const risk = document.querySelector('input[name="risk-per-trade"]:checked');
            if (!risk) {
                alert('Please select a risk percentage');
                return false;
            }
            wizardData.riskPerTrade = risk.value;
            return true;

        case 3: // Strategy step
            if (!wizardData.strategy) {
                alert('Please select a trading strategy');
                return false;
            }
            return true;

        case 4: // Hotkeys step
            return true; // Optional step

        case 5: // Completion
            return true;

        default:
            return true;
    }
}

function saveStepData() {
    // Data is already saved in wizardData object during validation
    console.log('Wizard data:', wizardData);
}

function selectStrategy(strategy) {
    wizardData.strategy = strategy;

    // Update UI
    document.querySelectorAll('.strategy-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.target.closest('.strategy-card').classList.add('selected');
}

function copyHotkey(hotkey) {
    navigator.clipboard.writeText(hotkey).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        btn.style.background = 'var(--accent-green)';

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    });
}

function finishWizard() {
    // Apply settings to backend
    applySettings();

    // Redirect to dashboard
    setTimeout(() => {
        window.location.href = '/';
    }, 2000);
}

async function applySettings() {
    try {
        // Update risk settings
        await fetch('/api/risk/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                account_balance: parseFloat(wizardData.balance),
                risk_per_trade: parseFloat(wizardData.riskPerTrade)
            })
        });

        // Set active strategy
        if (wizardData.strategy) {
            await fetch('/api/strategy/active', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy: wizardData.strategy
                })
            });
        }

        console.log('✅ Settings applied successfully');
    } catch (err) {
        console.error('Failed to apply settings:', err);
    }
}

function skipWizard() {
    window.location.href = '/';
}
