const API_BASE = '';

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// Utility functions
function createBall(number) {
    const ball = document.createElement('div');
    ball.className = 'number-ball';
    ball.textContent = number.toString().padStart(2, '0');
    return ball;
}

function showMessage(elementId, message, type = 'info') {
    const el = document.getElementById(elementId);
    el.innerHTML = `<div class="message ${type}">${message}</div>`;
}

// Dashboard
async function loadStats() {
    try {
        const [statsRes, pairsRes, tripletsRes, delayedRes] = await Promise.all([
            fetch(`${API_BASE}/api/stats`),
            fetch(`${API_BASE}/api/pairs?limit=15`),
            fetch(`${API_BASE}/api/triplets?limit=10`),
            fetch(`${API_BASE}/api/delayed`)
        ]);

        const data = await statsRes.json();
        const pairs = await pairsRes.json();
        const triplets = await tripletsRes.json();
        const delayed = await delayedRes.json();

        document.getElementById('totalDraws').textContent = data.totalDraws.toLocaleString('pt-BR');
        document.getElementById('avgSum').textContent = data.sum.avg.toLocaleString('pt-BR');
        document.getElementById('sumRange').textContent = `${data.sum.min} - ${data.sum.max}`;

        if (data.lastDraw) {
            document.getElementById('lastDraw').textContent = `#${data.lastDraw.concurso}`;
        }

        renderFrequencyChart(data.frequency);
        renderOddEvenChart(data.oddEven);
        renderMolduraChart(data.molduraMiolo);
        renderRepetitionChart(data.repetition);
        renderPairsChart(pairs);
        renderTripletsChart(triplets);
    } catch (err) {
        console.error('Erro ao carregar estatísticas:', err);
    }
}

function renderFrequencyChart(frequency) {
    const ctx = document.getElementById('frequencyChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: frequency.map(f => f[0]),
            datasets: [{
                label: 'Ocorrências',
                data: frequency.map(f => f[1]),
                backgroundColor: '#2563eb',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderOddEvenChart(data) {
    const container = document.getElementById('oddEvenChart');
    container.innerHTML = '';
    const max = Math.max(...data.map(d => d[1]));

    data.forEach(([label, value]) => {
        const bar = document.createElement('div');
        bar.style.cssText = 'display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;';
        bar.innerHTML = `
            <span style="width: 40px; font-weight: 600;">${label}</span>
            <div style="flex: 1; height: 24px; background: var(--bg); border-radius: 12px; overflow: hidden;">
                <div style="width: ${(value / max) * 100}%; height: 100%; background: linear-gradient(90deg, #2563eb, #3b82f6); border-radius: 12px; transition: width 0.5s;"></div>
            </div>
            <span style="width: 60px; text-align: right; color: var(--text-light);">${value.toLocaleString('pt-BR')}</span>
        `;
        container.appendChild(bar);
    });
}

function renderMolduraChart(data) {
    const container = document.getElementById('molduraChart');
    container.innerHTML = '';
    const max = Math.max(...data.map(d => d[1]));

    data.forEach(([label, value]) => {
        const bar = document.createElement('div');
        bar.style.cssText = 'display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;';
        bar.innerHTML = `
            <span style="width: 60px; font-weight: 600;">${label}</span>
            <div style="flex: 1; height: 24px; background: var(--bg); border-radius: 12px; overflow: hidden;">
                <div style="width: ${(value / max) * 100}%; height: 100%; background: linear-gradient(90deg, #16a34a, #22c55e); border-radius: 12px; transition: width 0.5s;"></div>
            </div>
            <span style="width: 60px; text-align: right; color: var(--text-light);">${value.toLocaleString('pt-BR')}</span>
        `;
        container.appendChild(bar);
    });
}

function renderRepetitionChart(data) {
    const container = document.getElementById('repetitionChart');
    container.innerHTML = '';
    const max = Math.max(...data.map(d => d[1]));

    data.forEach(([label, value]) => {
        const bar = document.createElement('div');
        bar.style.cssText = 'display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;';
        bar.innerHTML = `
            <span style="width: 60px; font-weight: 600;">${label} repetidas</span>
            <div style="flex: 1; height: 24px; background: var(--bg); border-radius: 12px; overflow: hidden;">
                <div style="width: ${(value / max) * 100}%; height: 100%; background: linear-gradient(90deg, #d97706, #f59e0b); border-radius: 12px; transition: width 0.5s;"></div>
            </div>
            <span style="width: 60px; text-align: right; color: var(--text-light);">${value.toLocaleString('pt-BR')}</span>
        `;
        container.appendChild(bar);
    });
}

function renderPairsChart(data) {
    const container = document.getElementById('pairsChart');
    container.innerHTML = '';
    const max = Math.max(...data.map(d => d.count));

    data.forEach(item => {
        const bar = document.createElement('div');
        bar.style.cssText = 'display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;';
        bar.innerHTML = `
            <span style="width: 60px; font-weight: 600; font-size: 0.9rem;">${item.pair}</span>
            <div style="flex: 1; height: 24px; background: var(--bg); border-radius: 12px; overflow: hidden;">
                <div style="width: ${(item.count / max) * 100}%; height: 100%; background: linear-gradient(90deg, #7c3aed, #a78bfa); border-radius: 12px; transition: width 0.5s;"></div>
            </div>
            <span style="width: 60px; text-align: right; color: var(--text-light);">${item.count.toLocaleString('pt-BR')}</span>
        `;
        container.appendChild(bar);
    });
}

function renderTripletsChart(data) {
    const container = document.getElementById('tripletsChart');
    container.innerHTML = '';
    const max = Math.max(...data.map(d => d.count));

    data.forEach(item => {
        const bar = document.createElement('div');
        bar.style.cssText = 'display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;';
        bar.innerHTML = `
            <span style="width: 90px; font-weight: 600; font-size: 0.85rem;">${item.triplet}</span>
            <div style="flex: 1; height: 24px; background: var(--bg); border-radius: 12px; overflow: hidden;">
                <div style="width: ${(item.count / max) * 100}%; height: 100%; background: linear-gradient(90deg, #db2777, #f472b6); border-radius: 12px; transition: width 0.5s;"></div>
            </div>
            <span style="width: 60px; text-align: right; color: var(--text-light);">${item.count.toLocaleString('pt-BR')}</span>
        `;
        container.appendChild(bar);
    });
}

// Generator
document.getElementById('generateBtn').addEventListener('click', async () => {
    const count = parseInt(document.getElementById('gameCount').value) || 5;
    const delayedThreshold = parseInt(document.getElementById('delayedThreshold').value) || 0;
    const container = document.getElementById('generatedGames');
    container.innerHTML = '<p>Gerando jogos...</p>';

    try {
        const res = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count, delayedThreshold })
        });
        const data = await res.json();

        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const disclaimer = document.createElement('div');
        disclaimer.className = 'disclaimer-note';

        let info = `<strong>Último sorteio analisado:</strong> Concurso #${data.lastDraw?.concurso} - ${data.lastDraw?.dezenas?.join(', ')}`;
        if (data.delayedNumbers && data.delayedNumbers.length > 0) {
            info += `<br><strong>Números mais atrasados considerados:</strong> ${data.delayedNumbers.map(d => `${d.number} (${d.delay} concursos)`).join(', ')}`;
        }
        disclaimer.innerHTML = info;
        container.innerHTML = '';
        container.appendChild(disclaimer);

        data.games.forEach((game, idx) => {
            const card = document.createElement('div');
            card.className = 'game-card';

            const dezenas = game.dezenas;
            const sum = dezenas.reduce((a, b) => a + b, 0);
            const odds = dezenas.filter(n => n % 2 !== 0).length;
            const moldura = dezenas.filter(n => [1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25].includes(n)).length;

            card.innerHTML = `<h4>Jogo ${idx + 1} <span style="font-size:0.8rem; color: var(--primary);">(Score: ${game.score.toFixed(2)})</span></h4>`;
            const numbersDiv = document.createElement('div');
            numbersDiv.className = 'game-numbers';
            dezenas.forEach(n => numbersDiv.appendChild(createBall(n)));
            card.appendChild(numbersDiv);

            const meta = document.createElement('div');
            meta.className = 'game-meta';
            meta.innerHTML = `
                <span>Soma: <strong>${sum}</strong></span>
                <span>Ímpares: <strong>${odds}</strong></span>
                <span>Moldura: <strong>${moldura}</strong></span>
            `;
            card.appendChild(meta);

            container.appendChild(card);
        });
    } catch (err) {
        container.innerHTML = `<p class="error">Erro ao gerar jogos: ${err.message}</p>`;
    }
});

// Checker
document.getElementById('checkBtn').addEventListener('click', async () => {
    const input = document.getElementById('checkGame').value.trim();
    const container = document.getElementById('checkResults');

    if (!input) {
        container.innerHTML = '<p class="error">Por favor, insira 15 números.</p>';
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/check?game=${encodeURIComponent(input)}`);
        const data = await res.json();

        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        const numbers = data.game;
        container.innerHTML = `
            <div class="game-numbers" style="margin-bottom: 2rem;">
                ${numbers.map(n => createBall(n).outerHTML).join('')}
            </div>
            <h3>Distribuição de Acertos</h3>
            <div class="result-summary">
                ${Object.entries(data.hitsDistribution).map(([hits, count]) => `
                    <div class="result-item">
                        <div class="hits">${hits}</div>
                        <div class="label">acertos: ${count.toLocaleString('pt-BR')} vezes</div>
                    </div>
                `).join('')}
            </div>
            ${data.bestResults.length > 0 ? `
                <h3>Melhores Resultados (11+ acertos)</h3>
                <div class="history-table">
                    <table>
                        <thead>
                            <tr><th>Concurso</th><th>Data</th><th>Acertos</th></tr>
                        </thead>
                        <tbody>
                            ${data.bestResults.map(r => `
                                <tr>
                                    <td>#${r.concurso}</td>
                                    <td>${r.data}</td>
                                    <td><strong>${r.acertos}</strong></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            ` : '<p>Nenhum resultado com 11+ acertos encontrado no histórico.</p>'}
        `;
    } catch (err) {
        container.innerHTML = `<p class="error">Erro ao verificar: ${err.message}</p>`;
    }
});

// History
document.getElementById('historyLimit').addEventListener('change', loadHistory);

async function loadHistory() {
    const limit = document.getElementById('historyLimit').value;
    const container = document.getElementById('historyTable');

    try {
        const res = await fetch(`${API_BASE}/api/history?limit=${limit}`);
        const data = await res.json();

        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Concurso</th>
                        <th>Data</th>
                        <th>Dezenas</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(d => `
                        <tr>
                            <td>#${d.concurso}</td>
                            <td>${d.data}</td>
                            <td class="numbers">${d.dezenas.map(n => `<span>${n.toString().padStart(2, '0')}</span>`).join('')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (err) {
        container.innerHTML = `<p class="error">Erro ao carregar histórico: ${err.message}</p>`;
    }
}

// Rolling Window Analysis
document.getElementById('runRollingBtn').addEventListener('click', async () => {
    const minWindow = parseInt(document.getElementById('minWindow').value) || 10;
    const maxWindow = parseInt(document.getElementById('maxWindow').value) || 200;
    const step = parseInt(document.getElementById('stepWindow').value) || 10;
    const container = document.getElementById('rollingResults');
    container.innerHTML = '<p>Executando análise...</p>';

    try {
        const res = await fetch(`${API_BASE}/api/rolling?minWindow=${minWindow}&maxWindow=${maxWindow}&step=${step}`);
        const data = await res.json();

        if (data.error) {
            container.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        container.innerHTML = '';

        const summary = document.createElement('div');
        summary.className = 'rolling-summary';
        summary.innerHTML = `
            <h3>Resumo da Análise</h3>
            <p><strong>Total de concursos:</strong> ${data.totalDraws.toLocaleString('pt-BR')}</p>
            <p><strong>Janelas analisadas:</strong> ${minWindow} a ${maxWindow} (passo ${step})</p>
            ${data.convergence ? `
                <p class="success"><strong>Janela de convergência encontrada:</strong> ${data.convergence.windowSize} concursos
                (Pearson: ${data.convergence.pearson.mean.toFixed(4)}, RMSE: ${data.convergence.rmse.mean.toFixed(4)})</p>
            ` : '<p class="warning">Nenhuma janela atingiu o critério de convergência (Pearson ≥ 0,95 e RMSE ≤ 0,05)</p>'}
        `;
        container.appendChild(summary);

        renderRollingCharts(data);
    } catch (err) {
        container.innerHTML = `<p class="error">Erro na análise: ${err.message}</p>`;
    }
});

function renderRollingCharts(data) {
    const labels = data.results.map(r => r.windowSize);
    const pearsonMean = data.results.map(r => r.pearson.mean);
    const rmseMean = data.results.map(r => r.rmse.mean);
    const jsMean = data.results.map(r => r.jensenShannon.mean);

    renderLineChart('pearsonChart', 'Correlação de Pearson', labels, pearsonMean, 'Pearson', '#2563eb');
    renderLineChart('rmseChart', 'RMSE', labels, rmseMean, 'RMSE', '#dc2626');
    renderLineChart('jsChart', 'Divergência Jensen-Shannon', labels, jsMean, 'JS', '#16a34a');

    renderBoxplot('boxplotContainer', data.results);
    renderHeatmap('heatmapContainer', data.results);
}

function renderLineChart(canvasId, label, labels, values, datasetLabel, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: datasetLabel,
                data: values,
                borderColor: color,
                backgroundColor: color + '20',
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Tamanho da Janela' }
                },
                y: {
                    title: { display: true, text: label }
                }
            }
        }
    });
}

function renderBoxplot(containerId, results) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const maxPearson = Math.max(...results.map(r => r.pearson.max));
    const minPearson = Math.min(...results.map(r => r.pearson.min));

    const width = container.clientWidth || 800;
    const height = 300;
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    const xScale = (i) => padding + (i / (results.length - 1)) * chartWidth;
    const yScale = (v) => padding + chartHeight - ((v - minPearson) / (maxPearson - minPearson || 1)) * chartHeight;

    const axisColor = '#94a3b8';

    const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    xAxis.setAttribute('x1', padding);
    xAxis.setAttribute('y1', height - padding);
    xAxis.setAttribute('x2', width - padding);
    xAxis.setAttribute('y2', height - padding);
    xAxis.setAttribute('stroke', axisColor);
    svg.appendChild(xAxis);

    const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    yAxis.setAttribute('x1', padding);
    yAxis.setAttribute('y1', padding);
    yAxis.setAttribute('x2', padding);
    yAxis.setAttribute('y2', height - padding);
    yAxis.setAttribute('stroke', axisColor);
    svg.appendChild(yAxis);

    results.forEach((r, i) => {
        const x = xScale(i);
        const yMin = yScale(r.pearson.min);
        const yMax = yScale(r.pearson.max);
        const yMedian = yScale(r.pearson.median);
        const yQ1 = yScale(r.pearson.min + (r.pearson.max - r.pearson.min) * 0.25);
        const yQ3 = yScale(r.pearson.min + (r.pearson.max - r.pearson.min) * 0.75);

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x);
        line.setAttribute('y1', yMin);
        line.setAttribute('x2', x);
        line.setAttribute('y2', yMax);
        line.setAttribute('stroke', '#2563eb');
        line.setAttribute('stroke-width', '2');
        svg.appendChild(line);

        const median = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        median.setAttribute('x1', x - 5);
        median.setAttribute('y1', yMedian);
        median.setAttribute('x2', x + 5);
        median.setAttribute('y2', yMedian);
        median.setAttribute('stroke', '#dc2626');
        median.setAttribute('stroke-width', '2');
        svg.appendChild(median);

        const box = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        box.setAttribute('x', x - 6);
        box.setAttribute('y', yQ3);
        box.setAttribute('width', 12);
        box.setAttribute('height', yQ1 - yQ3);
        box.setAttribute('fill', '#2563eb');
        box.setAttribute('opacity', '0.3');
        svg.appendChild(box);
    });

    container.appendChild(svg);
}

function renderHeatmap(containerId, results) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const width = container.clientWidth || 800;
    const height = 300;
    const padding = 50;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    const maxWindows = Math.max(...results.map(r => r.windowsCount));
    const minPearson = 0;
    const maxPearson = 1;

    const cellWidth = chartWidth / results.length;
    const cellHeight = chartHeight / maxWindows;

    results.forEach((r, wi) => {
        r.windows.forEach((w, pi) => {
            const x = padding + wi * cellWidth;
            const y = padding + pi * cellHeight;
            const color = getHeatmapColor(w.pearson, minPearson, maxPearson);

            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', x);
            rect.setAttribute('y', y);
            rect.setAttribute('width', cellWidth);
            rect.setAttribute('height', cellHeight);
            rect.setAttribute('fill', color);
            rect.setAttribute('stroke', '#fff');
            rect.setAttribute('stroke-width', '0.5');
            svg.appendChild(rect);
        });
    });

    const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    xAxis.setAttribute('x1', padding);
    xAxis.setAttribute('y1', height - padding);
    xAxis.setAttribute('x2', width - padding);
    xAxis.setAttribute('y2', height - padding);
    xAxis.setAttribute('stroke', '#94a3b8');
    svg.appendChild(xAxis);

    const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    yAxis.setAttribute('x1', padding);
    yAxis.setAttribute('y1', padding);
    yAxis.setAttribute('x2', padding);
    yAxis.setAttribute('y2', height - padding);
    yAxis.setAttribute('stroke', '#94a3b8');
    svg.appendChild(yAxis);

    const xLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    xLabel.setAttribute('x', width / 2);
    xLabel.setAttribute('y', height - 10);
    xLabel.setAttribute('text-anchor', 'middle');
    xLabel.setAttribute('fill', '#64748b');
    xLabel.setAttribute('font-size', '12');
    xLabel.textContent = 'Tamanho da Janela';
    svg.appendChild(xLabel);

    const yLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    yLabel.setAttribute('x', 15);
    yLabel.setAttribute('y', height / 2);
    yLabel.setAttribute('text-anchor', 'middle');
    yLabel.setAttribute('fill', '#64748b');
    yLabel.setAttribute('font-size', '12');
    yLabel.setAttribute('transform', `rotate(-90, 15, ${height / 2})`);
    yLabel.textContent = 'Posição da Janela';
    svg.appendChild(yLabel);

    container.appendChild(svg);
}

function getHeatmapColor(value, min, max) {
    const ratio = (value - min) / (max - min || 1);
    const r = Math.round(255 * (1 - ratio));
    const g = Math.round(255 * ratio);
    const b = 100;
    return `rgb(${r}, ${g}, ${b})`;
}

// Initialize
loadStats();
loadHistory();
