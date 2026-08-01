const express = require('express');
const XLSX = require('xlsx');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') return res.sendStatus(200);
    next();
});

app.use(express.static('public'));
app.use(express.json());

let historicalData = [];

function loadData() {
  try {
    const wb = XLSX.readFile(path.join(__dirname, 'Lotofácil.xlsx'));
    const ws = wb.Sheets['LOTOFÁCIL'];
    const raw = XLSX.utils.sheet_to_json(ws, { header: 1 });

    historicalData = raw.slice(1).map(row => {
      const balls = row.slice(2, 17).map(Number);
      return {
        concurso: Number(row[0]),
        data: row[1],
        dezenas: balls.sort((a, b) => a - b),
        dezenasOriginal: balls
      };
    }).filter(d => d.dezenas.length === 15 && d.dezenas.every(n => n >= 1 && n <= 25));

    console.log(`Carregados ${historicalData.length} concursos históricos.`);
  } catch (err) {
    console.error('Erro ao carregar dados:', err);
    historicalData = [];
  }
}

loadData();

const MOLDURA = new Set([1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25]);
const MIOLO = new Set([7,8,9,12,13,14,17,18,19]);

function sumArray(arr) {
  return arr.reduce((a, b) => a + b, 0);
}

function countOdds(arr) {
  return arr.filter(n => n % 2 !== 0).length;
}

function countRepeated(newGame, lastGame) {
  if (!lastGame) return 0;
  return newGame.filter(n => lastGame.includes(n)).length;
}

function countConsecutive(arr) {
  let maxSeq = 0, current = 1;
  const sorted = [...arr].sort((a, b) => a - b);
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i] === sorted[i-1] + 1) {
      current++;
      maxSeq = Math.max(maxSeq, current);
    } else {
      current = 1;
    }
  }
  return maxSeq;
}

function scoreGame(game) {
  const sum = sumArray(game);
  const sumScore = 1 - Math.abs(sum - 195.13) / 72.13;

  const odds = countOdds(game);
  const oddScore = odds >= 7 && odds <= 9 ? 1 : 0.5;

  const molduraCount = game.filter(n => MOLDURA.has(n)).length;
  const molduraScore = molduraCount >= 9 && molduraCount <= 11 ? 1 : 0.5;

  const lineDist = getLineDistribution(game);
  const lineScore = isBalancedLines(lineDist) ? 1 : 0.5;

  const consecutive = countConsecutive(game);
  const consecScore = consecutive >= 3 ? 1 : (consecutive >= 2 ? 0.7 : 0.3);

  return (sumScore * 0.3 + oddScore * 0.2 + molduraScore * 0.2 + lineScore * 0.15 + consecScore * 0.15);
}

function getLineDistribution(arr) {
  const lines = [0, 0, 0, 0, 0];
  arr.forEach(n => {
    const line = Math.floor((n - 1) / 5);
    lines[line]++;
  });
  return lines;
}

function isBalancedLines(distribution) {
  const max = Math.max(...distribution);
  const min = Math.min(...distribution);
  return max - min <= 2;
}

function passesFilters(game, lastGame, delayedThreshold = 0) {
  const sum = sumArray(game);
  if (sum < 185 || sum > 205) return false;

  const odds = countOdds(game);
  if (odds < 7 || odds > 9) return false;

  const repeated = countRepeated(game, lastGame ? lastGame.dezenas : []);
  if (repeated < 8 || repeated > 10) return false;

  const molduraCount = game.filter(n => MOLDURA.has(n)).length;
  if (molduraCount < 9 || molduraCount > 11) return false;

  const lineDist = getLineDistribution(game);
  if (!isBalancedLines(lineDist)) return false;

  const consecutive = countConsecutive(game);
  if (consecutive < 2) return false;

  if (delayedThreshold > 0) {
    const delayed = getDelayedNumbers().slice(0, delayedThreshold);
    const delayedNumbers = new Set(delayed.map(d => d.number));
    const hitsInDelayed = game.filter(n => delayedNumbers.has(n)).length;
    if (hitsInDelayed < Math.min(2, delayedThreshold)) return false;
  }

  return true;
}

function generateGame(lastGame, delayedThreshold = 0) {
  const maxAttempts = 10000;
  let attempts = 0;

  while (attempts < maxAttempts) {
    const game = new Set();
    while (game.size < 15) {
      game.add(Math.floor(Math.random() * 25) + 1);
    }
    const arr = Array.from(game).sort((a, b) => a - b);

    if (passesFilters(arr, lastGame, delayedThreshold)) {
      return arr;
    }
    attempts++;
  }
  return null;
}

function generateMultipleGames(count, lastGame, delayedThreshold = 0) {
  const games = [];
  let attempts = 0;
  const maxAttempts = count * 1000;

  while (games.length < count && attempts < maxAttempts) {
    const game = generateGame(lastGame, delayedThreshold);
    if (game) {
      const key = game.join(',');
      if (!games.some(g => g.game.join(',') === key)) {
        games.push({ game, score: scoreGame(game) });
      }
    }
    attempts++;
  }

  return games.sort((a, b) => b.score - a.score);
}

function pearsonCorrelation(a, b) {
  const n = a.length;
  const meanA = a.reduce((s, v) => s + v, 0) / n;
  const meanB = b.reduce((s, v) => s + v, 0) / n;
  let num = 0, denA = 0, denB = 0;
  for (let i = 0; i < n; i++) {
    const da = a[i] - meanA;
    const db = b[i] - meanB;
    num += da * db;
    denA += da * da;
    denB += db * db;
  }
  const den = Math.sqrt(denA) * Math.sqrt(denB);
  return den === 0 ? 0 : num / den;
}

function euclideanDistance(a, b) {
  return Math.sqrt(a.reduce((s, v, i) => s + (v - b[i]) ** 2, 0));
}

function rmse(a, b) {
  return Math.sqrt(a.reduce((s, v, i) => s + (v - b[i]) ** 2, 0) / a.length);
}

function jensenShannonDivergence(a, b) {
  const eps = 1e-12;
  const n = a.length;
  const sumA = a.reduce((s, v) => s + v, 0) || 1;
  const sumB = b.reduce((s, v) => s + v, 0) || 1;
  const p = a.map(v => Math.max(v / sumA, eps));
  const q = b.map(v => Math.max(v / sumB, eps));

  const kl = (p, q) => p.reduce((s, pi, i) => {
    const qi = q[i];
    return s + pi * Math.log(pi / qi);
  }, 0);

  const m = p.map((v, i) => (v + q[i]) / 2);
  return 0.5 * kl(p, m) + 0.5 * kl(q, m);
}

function cosineDistance(a, b) {
  const num = a.reduce((s, v, i) => s + v * b[i], 0);
  const den = Math.sqrt(a.reduce((s, v) => s + v * v, 0)) * Math.sqrt(b.reduce((s, v) => s + v * v, 0));
  return den === 0 ? 1 : 1 - num / den;
}

function getFrequencyVector(balls) {
  const freq = new Array(25).fill(0);
  balls.forEach(b => freq[b - 1]++);
  return freq;
}

function getWindowStats(start, end) {
  const window = historicalData.slice(start, end);
  if (window.length === 0) return null;

  const freq = {};
  for (let i = 1; i <= 25; i++) freq[i] = 0;
  window.forEach(d => d.dezenas.forEach(n => freq[n]++));

  const freqArr = Object.values(freq);

  const sums = window.map(d => d.dezenas.reduce((a, b) => a + b, 0));
  const avgSum = sums.reduce((a, b) => a + b, 0) / sums.length;

  const oddsDist = {};
  window.forEach(d => {
    const odds = d.dezenas.filter(n => n % 2 !== 0).length;
    const key = `${odds}x${15 - odds}`;
    oddsDist[key] = (oddsDist[key] || 0) + 1;
  });

  const molduraMiolo = {};
  window.forEach(d => {
    const m = d.dezenas.filter(n => MOLDURA.has(n)).length;
    const key = `${m}x${15 - m}`;
    molduraMiolo[key] = (molduraMiolo[key] || 0) + 1;
  });

  const repetitionStats = {};
  for (let i = 1; i < window.length; i++) {
    const repeated = window[i].dezenas.filter(n => window[i - 1].dezenas.includes(n)).length;
    repetitionStats[repeated] = (repetitionStats[repeated] || 0) + 1;
  }

  return {
    frequency: freqArr,
    frequencyRelative: freqArr.map(v => v / window.length),
    sum: { min: Math.min(...sums), max: Math.max(...sums), avg: avgSum },
    oddEven: Object.entries(oddsDist).sort((a, b) => b[1] - a[1]),
    molduraMiolo: Object.entries(molduraMiolo).sort((a, b) => b[1] - a[1]),
    repetition: Object.entries(repetitionStats).sort((a, b) => b[1] - a[1]),
    draws: window.length
  };
}

function getGlobalStats() {
  return getWindowStats(0, historicalData.length);
}

function compareWindows(windowStats, globalStats) {
  const freqVec = windowStats.frequencyRelative;
  const globalFreqVec = globalStats.frequencyRelative;

  return {
    pearson: pearsonCorrelation(freqVec, globalFreqVec),
    euclidean: euclideanDistance(freqVec, globalFreqVec),
    rmse: rmse(freqVec, globalFreqVec),
    jensenShannon: jensenShannonDivergence(freqVec, globalFreqVec),
    cosine: cosineDistance(freqVec, globalFreqVec)
  };
}

function getTopPairs(limit = 20) {
  const pairCounts = {};

  historicalData.forEach(d => {
    const balls = d.dezenas;
    for (let i = 0; i < balls.length; i++) {
      for (let j = i + 1; j < balls.length; j++) {
        const pair = `${balls[i]}-${balls[j]}`;
        pairCounts[pair] = (pairCounts[pair] || 0) + 1;
      }
    }
  });

  return Object.entries(pairCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([pair, count]) => ({ pair, count }));
}

function getTopTriplets(limit = 20) {
  const tripletCounts = {};

  historicalData.forEach(d => {
    const balls = d.dezenas;
    for (let i = 0; i < balls.length; i++) {
      for (let j = i + 1; j < balls.length; j++) {
        for (let k = j + 1; k < balls.length; k++) {
          const triplet = `${balls[i]}-${balls[j]}-${balls[k]}`;
          tripletCounts[triplet] = (tripletCounts[triplet] || 0) + 1;
        }
      }
    }
  });

  return Object.entries(tripletCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([triplet, count]) => ({ triplet, count }));
}

function getDelayedNumbers() {
  const lastSeen = {};
  for (let i = 1; i <= 25; i++) lastSeen[i] = -1;

  historicalData.forEach((d, idx) => {
    d.dezenas.forEach(n => {
      lastSeen[n] = idx;
    });
  });

  const totalDraws = historicalData.length;
  const delayed = [];

  for (let n = 1; n <= 25; n++) {
    const delay = lastSeen[n] >= 0 ? totalDraws - 1 - lastSeen[n] : totalDraws;
    delayed.push({
      number: n,
      delay: delay,
      lastConcurso: lastSeen[n] >= 0 ? historicalData[lastSeen[n]].concurso : null
    });
  }

  return delayed.sort((a, b) => b.delay - a.delay);
}

app.get('/api/stats', (req, res) => {
  if (historicalData.length === 0) {
    return res.json({ error: 'Dados não carregados' });
  }

  const freq = {};
  for (let i = 1; i <= 25; i++) freq[i] = 0;
  historicalData.forEach(d => d.dezenas.forEach(n => freq[n]++));

  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);

  const sumStats = historicalData.map(d => sumArray(d.dezenas));
  const avgSum = sumStats.reduce((a, b) => a + b, 0) / sumStats.length;

  const oddEven = {};
  historicalData.forEach(d => {
    const odds = countOdds(d.dezenas);
    const key = `${odds}x${15-odds}`;
    oddEven[key] = (oddEven[key] || 0) + 1;
  });

  const repetitionStats = {};
  for (let i = 1; i < historicalData.length; i++) {
    const repeated = countRepeated(historicalData[i].dezenas, historicalData[i-1].dezenas);
    repetitionStats[repeated] = (repetitionStats[repeated] || 0) + 1;
  }

  const molduraMiolo = {};
  historicalData.forEach(d => {
    const m = d.dezenas.filter(n => MOLDURA.has(n)).length;
    const mi = 15 - m;
    const key = `${m}x${mi}`;
    molduraMiolo[key] = (molduraMiolo[key] || 0) + 1;
  });

  const lineDist = {};
  historicalData.forEach(d => {
    const dist = getLineDistribution(d.dezenas).join('-');
    lineDist[dist] = (lineDist[dist] || 0) + 1;
  });

  res.json({
    totalDraws: historicalData.length,
    frequency: sorted,
    sum: {
      min: Math.min(...sumStats),
      max: Math.max(...sumStats),
      avg: Math.round(avgSum * 100) / 100
    },
    oddEven: Object.entries(oddEven).sort((a, b) => b[1] - a[1]),
    repetition: Object.entries(repetitionStats).sort((a, b) => b[1] - a[1]),
    molduraMiolo: Object.entries(molduraMiolo).sort((a, b) => b[1] - a[1]),
    lineDistribution: Object.entries(lineDist).sort((a, b) => b[1] - a[1]).slice(0, 10),
    lastDraw: historicalData.length > 0 ? {
      concurso: historicalData[historicalData.length - 1].concurso,
      dezenas: historicalData[historicalData.length - 1].dezenas
    } : null
  });
});

app.get('/api/rolling', (req, res) => {
  if (historicalData.length < 2) {
    return res.json({ error: 'Dados insuficientes para análise.' });
  }

  const minWindow = parseInt(req.query.minWindow) || 10;
  const maxWindow = parseInt(req.query.maxWindow) || Math.min(500, historicalData.length);
  const step = parseInt(req.query.step) || 10;

  const globalStats = getGlobalStats();
  const results = [];

  for (let w = minWindow; w <= maxWindow && w <= historicalData.length; w += step) {
    const windows = [];
    for (let start = 0; start <= historicalData.length - w; start++) {
      const stats = getWindowStats(start, start + w);
      if (!stats) continue;
      const comparison = compareWindows(stats, globalStats);
      windows.push({
        start,
        end: start + w - 1,
        concursoStart: historicalData[start].concurso,
        concursoEnd: historicalData[start + w - 1].concurso,
        ...comparison
      });
    }

    if (windows.length === 0) continue;

    const pearsons = windows.map(w => w.pearson);
    const rmseValues = windows.map(w => w.rmse);
    const jsValues = windows.map(w => w.jensenShannon);

    results.push({
      windowSize: w,
      windowsCount: windows.length,
      pearson: {
        mean: pearsons.reduce((a, b) => a + b, 0) / pearsons.length,
        median: pearsons.sort((a, b) => a - b)[Math.floor(pearsons.length / 2)],
        std: Math.sqrt(pearsons.reduce((s, v) => s + (v - pearsons.reduce((a, b) => a + b, 0) / pearsons.length) ** 2, 0) / pearsons.length),
        min: Math.min(...pearsons),
        max: Math.max(...pearsons),
        values: pearsons
      },
      rmse: {
        mean: rmseValues.reduce((a, b) => a + b, 0) / rmseValues.length,
        median: rmseValues.sort((a, b) => a - b)[Math.floor(rmseValues.length / 2)],
        std: Math.sqrt(rmseValues.reduce((s, v) => s + (v - rmseValues.reduce((a, b) => a + b, 0) / rmseValues.length) ** 2, 0) / rmseValues.length),
        min: Math.min(...rmseValues),
        max: Math.max(...rmseValues),
        values: rmseValues
      },
      jensenShannon: {
        mean: jsValues.reduce((a, b) => a + b, 0) / jsValues.length,
        median: jsValues.sort((a, b) => a - b)[Math.floor(jsValues.length / 2)],
        std: Math.sqrt(jsValues.reduce((s, v) => s + (v - jsValues.reduce((a, b) => a + b, 0) / jsValues.length) ** 2, 0) / jsValues.length),
        min: Math.min(...jsValues),
        max: Math.max(...jsValues),
        values: jsValues
      },
      windows: windows.map(w => ({
        start: w.start,
        end: w.end,
        pearson: w.pearson,
        rmse: w.rmse,
        jensenShannon: w.jensenShannon
      }))
    });
  }

  const convergence = results.find(r => r.pearson.mean >= 0.95 && r.rmse.mean <= 0.05) || null;

  res.json({
    totalDraws: historicalData.length,
    minWindow,
    maxWindow,
    step,
    globalStats: {
      frequency: globalStats.frequency,
      sum: globalStats.sum,
      oddEven: globalStats.oddEven,
      molduraMiolo: globalStats.molduraMiolo
    },
    results,
    convergence
  });
});

app.get('/api/history', (req, res) => {
  const limit = parseInt(req.query.limit) || 50;
  res.json(historicalData.slice(-limit).reverse());
});

app.get('/api/check', (req, res) => {
  const { game } = req.query;
  if (!game) return res.json({ error: 'Parâmetro game obrigatório' });

  const numbers = game.split(',').map(Number).sort((a, b) => a - b);
  if (numbers.length !== 15 || numbers.some(n => n < 1 || n > 25)) {
    return res.json({ error: 'Jogo inválido. Informe 15 números de 1 a 25.' });
  }

  const results = historicalData.map(d => {
    const hits = d.dezenas.filter(n => numbers.includes(n)).length;
    return { concurso: d.concurso, data: d.data, acertos: hits };
  });

  const hitsDistribution = {};
  results.forEach(r => {
    hitsDistribution[r.acertos] = (hitsDistribution[r.acertos] || 0) + 1;
  });

  res.json({
    game: numbers,
    hitsDistribution: Object.entries(hitsDistribution).sort((a, b) => b[0] - a[0]),
    bestResults: results.filter(r => r.acertos >= 11).sort((a, b) => b.acertos - a.acertos).slice(0, 10)
  });
});

app.post('/api/generate', (req, res) => {
  const { count = 1, delayedThreshold = 0 } = req.body;
  const lastGame = historicalData.length > 0 ? historicalData[historicalData.length - 1] : null;

  if (count > 20) {
    return res.json({ error: 'Máximo de 20 jogos por requisição.' });
  }

  const threshold = Math.max(0, Math.min(25, parseInt(delayedThreshold) || 0));
  const games = generateMultipleGames(count, lastGame, threshold);
  const delayedNumbers = threshold > 0 ? getDelayedNumbers().slice(0, threshold) : [];

  res.json({
    disclaimer: 'ATENÇÃO: Este sistema é apenas uma ferramenta de análise estatística. Os jogos gerados não constituem método de previsão e não alteram as probabilidades fundamentais do sorteio. Jogue com responsabilidade.',
    lastDraw: lastGame ? { concurso: lastGame.concurso, dezenas: lastGame.dezenas } : null,
    delayedNumbers: delayedNumbers,
    games: games.map(g => ({ dezenas: g.game, score: Math.round(g.score * 100) / 100 }))
  });
});

app.get('/api/frequents', (req, res) => {
  const freq = {};
  for (let i = 1; i <= 25; i++) freq[i] = 0;
  historicalData.forEach(d => d.dezenas.forEach(n => freq[n]++));

  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
  res.json({
    mostFrequent: sorted.slice(0, 10),
    leastFrequent: sorted.slice(-10).reverse()
  });
});

app.get('/api/pairs', (req, res) => {
  const limit = parseInt(req.query.limit) || 20;
  res.json(getTopPairs(limit));
});

app.get('/api/triplets', (req, res) => {
  const limit = parseInt(req.query.limit) || 20;
  res.json(getTopTriplets(limit));
});

app.get('/api/delayed', (req, res) => {
  res.json(getDelayedNumbers());
});

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
