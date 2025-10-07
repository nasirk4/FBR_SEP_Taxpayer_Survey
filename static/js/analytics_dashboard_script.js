// static/js/analytics_dashboard_script.js
class Dashboard {
    constructor() {
        this.validateConfiguration();
        this.initializeProperties();
        this.init();
    }

    validateConfiguration() {
        if (!window.DASHBOARD_CONFIG) {
            console.warn('Dashboard configuration not found. Using fallback values.');
            window.DASHBOARD_CONFIG = {
                apiStatsUrl: '/survey/api/dashboard-stats/',
                csrfToken: document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '',
                updateInterval: 30000,
                timeout: 10000
            };
        }
        const required = ['apiStatsUrl', 'csrfToken'];
        const missing = required.filter(key => !window.DASHBOARD_CONFIG[key]);
        if (missing.length > 0) {
            throw new Error(`Missing required configuration: ${missing.join(', ')}`);
        }
    }

    initializeProperties() {
        this.container = document.querySelector('.dashboard-container');
        this.announcer = document.getElementById('update-announcer');
        this.refreshBtn = document.getElementById('refresh-btn');
        this.offlineMessage = document.querySelector('.offline-message');
        this.searchInput = document.getElementById('qualitative-search');
        this.exportQualitativeBtn = document.getElementById('export-qualitative');
        this.isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        this.updateCount = 0;
        this.lastUpdateTime = null;
        this.config = window.DASHBOARD_CONFIG;
        this.updateInterval = this.config.updateInterval || 30000;
        this.positiveKeywords = ['great', 'excellent', 'good', 'awesome', 'positive', 'satisfied'];
        this.negativeKeywords = ['bad', 'poor', 'issue', 'problem', 'difficult', 'disappointed'];
        this.csrfToken = this.config.csrfToken ||
                         document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    }

    init() {
        try {
            if (this.isTouchDevice) {
                document.body.classList.add('touch-device');
                this.setupTouchScroll();
            }
            this.setupEventListeners();
            this.checkNetworkStatus();
            this.analyzeSentiment();
            this.update();
            this.updateInterval = setInterval(() => this.update(), this.updateInterval);
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.handleFatalError('Failed to initialize dashboard');
        }
    }

    setupEventListeners() {
        window.addEventListener('online', () => this.checkNetworkStatus());
        window.addEventListener('offline', () => this.checkNetworkStatus());

        if (this.container) {
            this.container.addEventListener('click', (e) => {
                if (e.target.classList.contains('dismiss-btn')) {
                    e.target.parentElement.style.display = 'none';
                } else if (e.target.classList.contains('read-more')) {
                    this.toggleReadMore(e.target);
                } else if (e.target.tagName === 'H3' && e.target.closest('.qualitative-section')) {
                    this.toggleQualitativeSection(e.target);
                }
            });
        }

        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase().trim();
                this.filterQualitativeInsights(query);
            });
        }

        if (this.exportQualitativeBtn) {
            this.exportQualitativeBtn.addEventListener('click', () => this.exportQualitativeData());
        }

        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.update());
        }
    }

    toggleReadMore(button) {
        if (!button) return;
        const fullText = button.nextElementSibling;
        if (!fullText) return;
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        fullText.style.display = isExpanded ? 'none' : 'block';
        button.setAttribute('aria-expanded', !isExpanded);
        button.textContent = isExpanded ? 'Read More' : 'Read Less';
    }

    toggleQualitativeSection(header) {
        if (!header) return;
        const section = header.closest('.qualitative-section');
        if (!section) return;
        const box = section.querySelector('.qualitative-box');
        if (!box) return;
        const isExpanded = header.getAttribute('aria-expanded') === 'true';
        box.classList.toggle('visible', !isExpanded);
        header.setAttribute('aria-expanded', !isExpanded);
        section.classList.toggle('collapsed', isExpanded);
    }

    setupTouchScroll() {
        if (!this.container) return;
        this.container.querySelectorAll('.quota-table-container').forEach(container => {
            let startX = 0;
            let scrollLeft = 0;

            const updateScrollIndicators = () => {
                container.classList.toggle('scroll-left', container.scrollLeft > 0);
                container.classList.toggle('scroll-right',
                    container.scrollLeft < container.scrollWidth - container.clientWidth - 1);
            };

            container.addEventListener('touchstart', (e) => {
                startX = e.touches[0].pageX - container.offsetLeft;
                scrollLeft = container.scrollLeft;
            });

            container.addEventListener('touchmove', (e) => {
                if (!startX) return;
                const x = e.touches[0].pageX - container.offsetLeft;
                const walk = (x - startX) * 1.5;
                container.scrollLeft = scrollLeft - walk;
                updateScrollIndicators();
            });

            container.addEventListener('scroll', updateScrollIndicators);
            updateScrollIndicators();
        });
    }

    checkNetworkStatus() {
        const isOnline = navigator.onLine;
        if (this.offlineMessage) {
            this.offlineMessage.style.display = isOnline ? 'none' : 'block';
        }
        if (this.refreshBtn) {
            this.refreshBtn.disabled = !isOnline;
        }
        if (this.container) {
            this.container.querySelectorAll('.export-btn:not(#refresh-btn)').forEach(btn => {
                btn.disabled = !isOnline;
            });
        }
    }

    validateData(data) {
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid data received from server');
        }
        const required = ['summary', 'quota_status'];
        required.forEach(field => {
            if (!data[field]) {
                throw new Error(`Missing required field: ${field}`);
            }
        });
        return true;
    }

    updateUI(data) {
        const totalEl = this.container ? this.container.querySelector('[data-stat="total"]') : null;
        const progressEl = this.container ? this.container.querySelector('[data-stat="progress"]') : null;
        const progressFill = this.container ? this.container.querySelector('.progress-fill') : null;

        if (totalEl && data.summary) {
            totalEl.textContent = data.summary.total_responses || 0;
        }

        if (progressEl && data.quota_status?.total) {
            const newPercentage = data.quota_status.total.percentage || 0;
            progressEl.textContent = `${newPercentage}%`;
            if (progressFill) {
                progressFill.classList.add('animating');
                progressFill.style.width = `${newPercentage}%`;
                setTimeout(() => progressFill.classList.remove('animating'), 800);
            }
        }
    }

    handleUpdateError(error) {
        console.error('Dashboard update failed:', error);
        let errorMessage = 'Unable to refresh data. Please try again.';
        if (error.name === 'TimeoutError') {
            errorMessage = 'Request timed out. Please check your connection.';
        } else if (!navigator.onLine) {
            errorMessage = 'You are offline. Please check your connection.';
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.setAttribute('role', 'alert');
        errorDiv.innerHTML = `
            <h3>⚠️ Update Failed</h3>
            <p>${errorMessage}</p>
            <button class="export-btn" onclick="window.dashboard.update()">Retry</button>
            <button class="dismiss-btn" aria-label="Dismiss error">✖</button>
        `;

        if (this.container) {
            this.container.querySelectorAll('.error-message').forEach(msg => {
                if (msg !== this.offlineMessage) msg.remove();
            });
            this.container.insertBefore(errorDiv, this.container.firstChild);
        }
    }

    handleFatalError(message) {
        console.error('Fatal error:', message);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message fatal-error';
        errorDiv.setAttribute('role', 'alert');
        errorDiv.innerHTML = `
            <h3>🚨 Critical Error</h3>
            <p>${message}</p>
            <button class="export-btn" onclick="window.location.reload()">Reload Page</button>
        `;
        if (this.container) {
            this.container.insertBefore(errorDiv, this.container.firstChild);
        }
    }

    announceUpdate(message) {
        if (this.announcer) {
            this.announcer.textContent = message;
            setTimeout(() => this.announcer.textContent = '', 3000);
        }
    }

    analyzeSentiment() {
        if (this.container) {
            this.container.querySelectorAll('.qualitative-item').forEach(item => {
                const text = item.getAttribute('data-text') || '';
                let sentiment = 'neutral';
                const lowerText = text.toLowerCase();

                if (this.positiveKeywords.some(keyword => lowerText.includes(keyword))) {
                    sentiment = 'positive';
                } else if (this.negativeKeywords.some(keyword => lowerText.includes(keyword))) {
                    sentiment = 'negative';
                }

                const sentimentEl = item.querySelector('.sentiment');
                if (sentimentEl) {
                    sentimentEl.textContent = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
                    sentimentEl.setAttribute('data-sentiment', sentiment);
                    sentimentEl.className = `sentiment sentiment-${sentiment}`;
                }
            });
        }
    }

    filterQualitativeInsights(query) {
        if (this.container) {
            this.container.querySelectorAll('.qualitative-item').forEach(item => {
                const text = item.getAttribute('data-text') || '';
                item.style.display = query === '' || text.includes(query) ? 'block' : 'none';
            });
            this.announceUpdate(query ? `Filtered insights for "${query}"` : 'Cleared search filter');
        }
    }

    exportQualitativeData() {
        if (!navigator.onLine) {
            this.handleUpdateError(new Error('Offline'));
            return;
        }

        const csvRows = ['Section,Insight,Word Count,Sentiment'];
        if (this.container) {
            this.container.querySelectorAll('.qualitative-section').forEach(section => {
                const sectionName = section.getAttribute('data-section') || 'Unknown';
                section.querySelectorAll('.qualitative-item').forEach(item => {
                    const text = item.querySelector('.full-text')?.textContent || item.querySelector('.insight-text').textContent;
                    const wordCount = item.querySelector('.word-count').textContent.replace('Words: ', '');
                    const sentiment = item.querySelector('.sentiment').getAttribute('data-sentiment');
                    const escapedText = `"${text.replace(/"/g, '""')}"`;
                    csvRows.push(`${sectionName},${escapedText},${wordCount},${sentiment}`);
                });
            });
        }

        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `qualitative_insights_${new Date().toISOString().replace(/[:.]/g, '-')}.csv`;
        link.click();
        URL.revokeObjectURL(link.href);
        this.announceUpdate('Qualitative data exported successfully');
    }

    async update() {
        const startTime = performance.now();
        this.updateCount++;

        if (!navigator.onLine) {
            this.handleUpdateError(new Error('Offline'));
            return;
        }

        this.setLoadingState(true);

        try {
            const response = await fetch(this.config.apiStatsUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action: 'update_dashboard' }),
                signal: AbortSignal.timeout(this.config.timeout || 10000)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.validateData(data);
            this.updateUI(data);
            this.announceUpdate('Dashboard updated successfully');
        } catch (error) {
            this.handleUpdateError(error);
        } finally {
            this.setLoadingState(false);
            this.logPerformance(startTime);
        }
    }

    setLoadingState(loading) {
        if (this.refreshBtn) {
            this.refreshBtn.disabled = loading || !navigator.onLine;
            this.refreshBtn.innerHTML = loading ? '⏳ Updating...' : '🔄 Refresh';
            if (loading) {
                this.refreshBtn.classList.add('loading-pulse');
            } else {
                this.refreshBtn.classList.remove('loading-pulse');
            }
        }
    }

    logPerformance(startTime) {
        const endTime = performance.now();
        this.lastUpdateTime = endTime - startTime;
        if (console && console.debug) {
            console.debug(`Dashboard update #${this.updateCount} took ${this.lastUpdateTime.toFixed(2)}ms`);
        }
    }
}

// Initialize dashboard with error handling
document.addEventListener('DOMContentLoaded', () => {
    try {
        const dashboard = new Dashboard();
        window.dashboard = dashboard; // For debugging
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        const container = document.querySelector('.dashboard-container');
        if (container) {
            container.innerHTML = `
                <div class="error-message fatal-error" role="alert">
                    <h3>🚨 Dashboard Initialization Failed</h3>
                    <p>${error.message}</p>
                    <button class="export-btn" onclick="window.location.reload()">Reload Page</button>
                </div>
            `;
        }
    }
});