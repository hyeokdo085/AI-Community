const API = {
    login: "/login",
    register: "/register",
    history: "/api/chat/history",
    send: "/api/chat/send",
};

const state = {
    user: window.__AI_COMMUNITY_USER__ || null,
    theme: localStorage.getItem('theme') || 'dark',
};

// Theme Management
function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = state.theme === 'dark' ? '☀️' : '🌙';
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = state.theme === 'dark' ? '☀️' : '🌙';
    }
    
    // Add transition effect
    document.body.style.transition = 'all 0.5s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 500);
}

// Particle Effect
function createParticles() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles';
    document.body.appendChild(particlesContainer);
    
    setInterval(() => {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 10 + 5) + 's';
        particle.style.animationDelay = Math.random() * 2 + 's';
        particlesContainer.appendChild(particle);
        
        setTimeout(() => {
            particle.remove();
        }, 15000);
    }, 3000);
}

async function postJSON(url, payload) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "요청 실패");
    return data;
}

function renderFeedback(message, isError = false) {
    const el = document.getElementById("auth-feedback");
    if (!el) return;
    el.textContent = message;
    el.style.color = isError ? "var(--error)" : "var(--success)";
    el.style.border = `2px solid ${isError ? "var(--error)" : "var(--success)"}`;
    el.style.background = isError ? "rgba(255, 0, 85, 0.1)" : "rgba(0, 255, 0, 0.1)";
    el.style.boxShadow = isError ? "0 0 30px rgba(255, 0, 85, 0.3)" : "0 0 30px rgba(0, 255, 0, 0.3)";
    
    if (isError) {
        el.classList.add('error-message');
        setTimeout(() => el.classList.remove('error-message'), 1000);
    }
}

function uuid() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return Math.random().toString(36).slice(2);
}

function buildPacket(body) {
    return {
        header: {
            version: "1.0",
            message_type: "CHAT",
            message_id: uuid(),
            sender: state.user?.email || "anonymous",
            channel: "lobby",
            timestamp: new Date().toISOString(),
        },
        payload: {
            body,
            metadata: {},
        },
    };
}

function showTypingIndicator() {
    const log = document.getElementById("chat-log");
    if (!log) return;
    
    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    indicator.id = "typing-indicator";
    indicator.innerHTML = '<span></span><span></span><span></span>';
    log.appendChild(indicator);
    log.scrollTop = log.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) {
        indicator.remove();
    }
}

function renderHistory(history) {
    const log = document.getElementById("chat-log");
    if (!log) return;
    
    hideTypingIndicator();
    log.innerHTML = "";
    
    history.forEach((packet, index) => {
        setTimeout(() => {
            const wrapper = document.createElement("article");
            wrapper.className = "chat-entry";
            if (packet.header.message_type === "AI") {
                wrapper.classList.add("chat-entry--ai");
            }
            const meta = document.createElement("div");
            meta.className = "chat-entry__meta";
            const timestamp = new Date(packet.header.timestamp);
            meta.textContent = `${packet.header.sender} • ${timestamp.toLocaleTimeString()}`;
            const body = document.createElement("div");
            body.className = "chat-entry__body";
            
            // Typing effect for messages
            const text = packet.payload.body;
            if (packet.header.message_type === "AI") {
                let charIndex = 0;
                body.textContent = '';
                const typingInterval = setInterval(() => {
                    if (charIndex < text.length) {
                        body.textContent += text[charIndex];
                        charIndex++;
                        log.scrollTop = log.scrollHeight;
                    } else {
                        clearInterval(typingInterval);
                    }
                }, 20);
            } else {
                body.textContent = text;
            }
            
            wrapper.append(meta, body);
            log.appendChild(wrapper);
            log.scrollTop = log.scrollHeight;
        }, index * 100); // Stagger animation
    });
}

async function refreshHistory() {
    try {
        const res = await fetch(API.history);
        if (!res.ok) throw new Error("기록을 가져오지 못했습니다.");
        const data = await res.json();
        renderHistory(data.history || []);
    } catch (error) {
        console.error("History refresh error:", error);
    }
}

function wireAuthForms() {
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const form = new FormData(loginForm);
                const payload = Object.fromEntries(form.entries());
                const result = await postJSON(API.login, payload);
                state.user = { email: payload.email, id: result.user_id };
                renderFeedback("🎉 로그인 성공! 잠시 후 채팅방으로 이동합니다.");
                
                // Add success effect
                loginForm.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    loginForm.style.transform = '';
                    window.location.href = "/chat";
                }, 1000);
            } catch (err) {
                renderFeedback("❌ " + err.message, true);
            }
        });
    }

    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
                const form = new FormData(registerForm);
                const payload = Object.fromEntries(form.entries());
                await postJSON(API.register, payload);
                renderFeedback("✨ 회원가입 완료! 이제 로그인해 주세요.");
                registerForm.reset();
                
                // Add success effect
                registerForm.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    registerForm.style.transform = '';
                }, 500);
            } catch (err) {
                renderFeedback("❌ " + err.message, true);
            }
        });
    }
}

function wireChatElements() {
    const chatForm = document.getElementById("chat-form");
    if (!chatForm) return;

    const textarea = chatForm.querySelector("textarea[name='message']");
    const askAiInput = chatForm.querySelector("input[name='ask_ai']");
    
    // Add shift+enter for new line, enter for submit
    textarea?.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const body = textarea.value.trim();
        if (!body) return;
        
        const askAi = askAiInput?.checked ?? true;
        
        try {
            const packet = buildPacket(body);
            textarea.value = "";
            textarea.style.height = 'auto';
            
            // Show sending animation
            const submitBtn = chatForm.querySelector("button[type='submit']");
            const originalText = submitBtn.textContent;
            submitBtn.textContent = "전송 중... 🚀";
            submitBtn.disabled = true;
            
            if (askAi) {
                showTypingIndicator();
            }
            
            const result = await postJSON(API.send, { packet, ask_ai: askAi });
            
            await refreshHistory();
            
            if (result.ai_packet) {
                // Wait a bit for AI response animation
                await new Promise(resolve => setTimeout(resolve, 500));
                await refreshHistory();
            }
            
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            
            // Add success flash
            submitBtn.style.boxShadow = '0 0 50px var(--primary-glow)';
            setTimeout(() => {
                submitBtn.style.boxShadow = '';
            }, 300);
            
        } catch (err) {
            hideTypingIndicator();
            alert("❌ " + err.message);
            
            // Reset button on error
            const submitBtn = chatForm.querySelector("button[type='submit']");
            submitBtn.textContent = "전송 ✈️";
            submitBtn.disabled = false;
        }
    });
    
    // Auto-resize textarea
    textarea?.addEventListener("input", function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    const refreshButton = document.getElementById("refresh-history");
    refreshButton?.addEventListener("click", async () => {
        refreshButton.textContent = "🔄 새로고침 중...";
        refreshButton.disabled = true;
        await refreshHistory();
        refreshButton.textContent = "🔄 기록 새로고침";
        refreshButton.disabled = false;
        
        // Add success animation
        refreshButton.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            refreshButton.style.transform = '';
        }, 500);
    });

    // Initial load
    refreshHistory().catch(() => {});
    
    // Auto-refresh every 5 seconds
    setInterval(() => {
        refreshHistory().catch(() => {});
    }, 5000);
}

// Smooth scroll animations
function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .auth form').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

// Enhanced input focus effects
function addInputEffects() {
    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = '';
        });
    });
}

// Initialize everything
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    createParticles();
    wireAuthForms();
    wireChatElements();
    addScrollAnimations();
    addInputEffects();
    
    // Add welcome animation
    setTimeout(() => {
        const main = document.querySelector('main');
        if (main) {
            main.style.animation = 'fadeIn 0.8s ease-out';
        }
    }, 100);
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Alt + T to toggle theme
    if (e.altKey && e.key === 't') {
        e.preventDefault();
        toggleTheme();
    }
    
    // Alt + R to refresh chat history
    if (e.altKey && e.key === 'r') {
        e.preventDefault();
        const refreshBtn = document.getElementById('refresh-history');
        if (refreshBtn) {
            refreshBtn.click();
        }
    }
});

// Add visibility change handler for auto-refresh
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        refreshHistory().catch(() => {});
    }
});
