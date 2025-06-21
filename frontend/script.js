const API_BASE = 'http://localhost:8000';

async function makeRequest(url, options = {}) {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}${url}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        showError(`Request failed: ${error.message}`);
        throw error;
    } finally {
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showError(message) {
    alert(`Error: ${message}`);
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

async function loadStats() {
    try {
        const stats = await makeRequest('/stats');
        
        document.getElementById('totalFailures').textContent = formatNumber(stats.nodes || 0);
        document.getElementById('graphNodes').textContent = formatNumber(stats.nodes || 0);
        document.getElementById('repositories').textContent = formatNumber(stats.node_types?.repository || 0);
        document.getElementById('workflows').textContent = stats.node_types?.workflow || 0;
        
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function analyzeFailure() {
    const runId = document.getElementById('runId').value;
    const query = document.getElementById('analysisQuery').value;
    
    if (!runId) {
        showError('Please enter a Run ID');
        return;
    }
    
    try {
        const result = await makeRequest('/analyze', {
            method: 'POST',
            body: JSON.stringify({
                run_id: parseInt(runId),
                query: query || 'analyze failure'
            })
        });
        
        displayAnalysisResult(result);
        
    } catch (error) {
        console.error('Analysis failed:', error);
    }
}

function displayAnalysisResult(result) {
    const container = document.getElementById('analysisResult');
    const content = document.getElementById('analysisContent');
    
    if (!result.analysis) {
        content.innerHTML = '<p>No analysis data available</p>';
        container.style.display = 'block';
        return;
    }
    
    const analysis = result.analysis;
    let html = '';
    
    if (analysis.diagnosis) {
        html += `
            <div class="diagnosis-section">
                <h4><i class="fas fa-stethoscope"></i> Diagnosis</h4>
                <p>${analysis.diagnosis}</p>
            </div>
        `;
    }
    
    if (analysis.context?.graph_similar?.length > 0) {
        html += `
            <div class="diagnosis-section">
                <h4><i class="fas fa-project-diagram"></i> Similar Failures (Graph)</h4>
                <div class="similar-failures">
        `;
        
        analysis.context.graph_similar.forEach(item => {
            html += `
                <div class="similar-failure">
                    <div class="repo">Run: ${item[0]}</div>
                    <div class="workflow">Similarity Score: ${item[1]}</div>
                </div>
            `;
        });
        
        html += `</div></div>`;
    }
    
    if (analysis.context?.vector_similar?.length > 0) {
        html += `
            <div class="diagnosis-section">
                <h4><i class="fas fa-search"></i> Similar Failures (Vector)</h4>
                <div class="similar-failures">
        `;
        
        analysis.context.vector_similar.forEach(item => {
            const metadata = item.metadata;
            html += `
                <div class="similar-failure">
                    <div class="repo">${metadata.repo}</div>
                    <div class="workflow">Workflow: ${metadata.workflow} | Similarity: ${(item.similarity * 100).toFixed(1)}%</div>
                    <div class="error">${metadata.error_patterns?.[0]?.context || 'No error context'}</div>
                </div>
            `;
        });
        
        html += `</div></div>`;
    }
    
    if (analysis.context?.failure_path?.length > 0) {
        html += `
            <div class="diagnosis-section">
                <h4><i class="fas fa-route"></i> Failure Path</h4>
                <div class="similar-failures">
        `;
        
        analysis.context.failure_path.forEach(item => {
            html += `
                <div class="similar-failure">
                    <div class="repo">Type: ${item.type}</div>
                    <div class="workflow">${item.name || item.status || ''} ${item.conclusion || ''}</div>
                    ${item.context ? `<div class="error">${item.context}</div>` : ''}
                </div>
            `;
        });
        
        html += `</div></div>`;
    }
    
    content.innerHTML = html || '<p>No detailed analysis available</p>';
    container.style.display = 'block';
}

async function searchFailures() {
    const query = document.getElementById('searchQuery').value;
    const topK = parseInt(document.getElementById('resultCount').value);
    
    if (!query) {
        showError('Please enter a search query');
        return;
    }
    
    try {
        const result = await makeRequest('/query', {
            method: 'POST',
            body: JSON.stringify({
                query: query,
                top_k: topK
            })
        });
        
        displaySearchResult(result);
        
    } catch (error) {
        console.error('Search failed:', error);
    }
}

function displaySearchResult(result) {
    const container = document.getElementById('searchResult');
    const content = document.getElementById('searchContent');
    
    if (!result.results || result.results.length === 0) {
        content.innerHTML = '<p>No search results found</p>';
        container.style.display = 'block';
        return;
    }
    
    let html = '<div class="similar-failures">';
    
    result.results.forEach(item => {
        html += `
            <div class="failure-item">
                <h4>Run ${item.run_id || 'Unknown'}</h4>
                <div class="metadata">
                    Repository: ${item.repo || 'Unknown'} | 
                    Workflow: ${item.workflow || 'Unknown'} |
                    Status: ${item.conclusion || 'Unknown'}
                </div>
                <div class="similarity">Similarity: ${((item.similarity || 0) * 100).toFixed(1)}%</div>
                <p>${item.error_message || item.error_patterns?.[0]?.context || 'No error description'}</p>
            </div>
        `;
    });
    
    html += '</div>';
    content.innerHTML = html;
    container.style.display = 'block';
}

async function refreshSystemStatus() {
    try {
        // Check API health
        const health = await makeRequest('/health');
        const apiStatus = document.getElementById('apiStatus');
        apiStatus.textContent = health.status === 'healthy' ? 'Online' : 'Offline';
        apiStatus.className = `status-indicator ${health.status === 'healthy' ? 'online' : 'offline'}`;
        
        // Get runtime stats
        try {
            const runtime = await makeRequest('/runtime/system');
            
            if (runtime.cpu_percent !== undefined) {
                const cpuProgress = document.getElementById('cpuProgress');
                const cpuText = document.getElementById('cpuText');
                cpuProgress.style.width = `${runtime.cpu_percent}%`;
                cpuText.textContent = `${runtime.cpu_percent}%`;
            }
            
            if (runtime.memory_percent !== undefined) {
                const memoryProgress = document.getElementById('memoryProgress');
                const memoryText = document.getElementById('memoryText');
                memoryProgress.style.width = `${runtime.memory_percent}%`;
                memoryText.textContent = `${runtime.memory_percent}%`;
            }
            
        } catch (error) {
            console.error('Failed to get runtime stats:', error);
        }
        
    } catch (error) {
        const apiStatus = document.getElementById('apiStatus');
        apiStatus.textContent = 'Offline';
        apiStatus.className = 'status-indicator offline';
        console.error('Failed to refresh system status:', error);
    }
}

async function rebuildGraph() {
    if (!confirm('Rebuilding the knowledge graph may take several minutes. Continue?')) {
        return;
    }
    
    try {
        const result = await makeRequest('/build-graph', {
            method: 'POST'
        });
        
        alert(`Knowledge graph rebuilt successfully!\nNodes: ${result.nodes}\nEdges: ${result.edges}`);
        loadStats(); // Refresh stats
        
    } catch (error) {
        console.error('Failed to rebuild graph:', error);
    }
}

async function exportData() {
    try {
        const stats = await makeRequest('/stats');
        const dataUrl = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(stats, null, 2));
        
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = `devo-analysis-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
    } catch (error) {
        console.error('Failed to export data:', error);
    }
}

function clearCache() {
    if (confirm('Clear all cached data and analysis results?')) {
        localStorage.clear();
        sessionStorage.clear();
        alert('Cache cleared successfully!');
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Devo CI/CD Analysis Frontend Loaded');
    
    // Load initial data
    loadStats();
    refreshSystemStatus();
    
    // Set up auto-refresh for system status
    setInterval(refreshSystemStatus, 30000); // Refresh every 30 seconds
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'Enter':
                    if (document.activeElement.id === 'runId' || document.activeElement.id === 'analysisQuery') {
                        analyzeFailure();
                    } else if (document.activeElement.id === 'searchQuery') {
                        searchFailures();
                    }
                    e.preventDefault();
                    break;
                case 'r':
                    refreshSystemStatus();
                    e.preventDefault();
                    break;
            }
        }
    });
});

// Handle network errors
window.addEventListener('online', function() {
    console.log('Network connection restored');
    refreshSystemStatus();
});

window.addEventListener('offline', function() {
    console.log('Network connection lost');
    const apiStatus = document.getElementById('apiStatus');
    apiStatus.textContent = 'Offline';
    apiStatus.className = 'status-indicator offline';
});
