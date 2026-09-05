import express from 'express';
import cors from 'cors';
import path from 'path';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';
import { generateMockMarketChart, BASE_PRICES } from './src/lib/mock_data';

dotenv.config();

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// In-memory cache for CoinGecko responses
const chartCache = new Map<string, { data: any; cachedAt: number }>();
const spotCache = new Map<string, { data: any; cachedAt: number }>();

// 1. Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    environment: process.env.ENVIRONMENT || 'development',
    telegram_configured: Boolean(process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID),
    coingecko_api_key_set: Boolean(process.env.COINGECKO_API_KEY),
  });
});

// 2. Market chart endpoint
app.get('/api/market-chart', async (req, res) => {
  const coinId = (req.query.coin_id as string) || 'bitcoin';
  const days = parseInt((req.query.days as string) || '30', 10);
  const cacheKey = `${coinId}_${days}`;

  const cached = chartCache.get(cacheKey);
  const now = Date.now();
  // Cache for 5 minutes
  if (cached && now - cached.cachedAt < 5 * 60 * 1000) {
    return res.json({ ...cached.data, source: 'cache' });
  }

  try {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'User-Agent': 'ProyectoAlpha/2.5',
    };
    if (process.env.COINGECKO_API_KEY) {
      headers['x-cg-demo-api-key'] = process.env.COINGECKO_API_KEY;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const cgUrl = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}`;
    const response = await fetch(cgUrl, {
      headers,
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (response.status === 200) {
      const data = await response.json();
      chartCache.set(cacheKey, { data, cachedAt: now });
      return res.json({ ...data, source: 'coingecko' });
    }

    // If rate limited or error, use fallback
    console.warn(`[CoinGecko] HTTP ${response.status} for ${coinId} (${days}d). Using fallback.`);
    const fallback = generateMockMarketChart(coinId, days);
    chartCache.set(cacheKey, { data: fallback, cachedAt: now });
    return res.json({ ...fallback, source: 'fallback', rate_limited: response.status === 429 });
  } catch (err: any) {
    console.warn(`[CoinGecko] Error fetching chart: ${err.message}. Using fallback.`);
    const fallback = generateMockMarketChart(coinId, days);
    return res.json({ ...fallback, source: 'fallback_error', error: err.message });
  }
});

// 3. Spot price endpoint
app.get('/api/spot-price', async (req, res) => {
  const coinId = (req.query.coin_id as string) || 'bitcoin';
  const cacheKey = coinId;
  const now = Date.now();

  const cached = spotCache.get(cacheKey);
  if (cached && now - cached.cachedAt < 60 * 1000) {
    return res.json(cached.data);
  }

  try {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'User-Agent': 'ProyectoAlpha/2.5',
    };
    if (process.env.COINGECKO_API_KEY) {
      headers['x-cg-demo-api-key'] = process.env.COINGECKO_API_KEY;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const cgUrl = `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true`;
    const response = await fetch(cgUrl, { headers, signal: controller.signal });
    clearTimeout(timeout);

    if (response.status === 200) {
      const data = await response.json();
      spotCache.set(cacheKey, { data, cachedAt: now });
      return res.json(data);
    }

    const base = BASE_PRICES[coinId] || { price: 100, vol: 1e9 };
    const fallback = {
      [coinId]: {
        usd: base.price,
        usd_24h_change: 1.85,
        usd_24h_vol: base.vol,
      },
    };
    return res.json(fallback);
  } catch (err) {
    const base = BASE_PRICES[coinId] || { price: 100, vol: 1e9 };
    return res.json({
      [coinId]: {
        usd: base.price,
        usd_24h_change: 0.0,
        usd_24h_vol: base.vol,
      },
    });
  }
});

// 4. Telegram test notification
app.post('/api/telegram/test', async (req, res) => {
  const token = process.env.TELEGRAM_BOT_TOKEN?.trim();
  const chatId = process.env.TELEGRAM_CHAT_ID?.trim();

  if (!token || !chatId) {
    return res.status(400).json({
      success: false,
      message: 'No se encontraron TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el archivo .env.',
    });
  }

  try {
    const message =
      '🔔 <b>¡Prueba desde tu Dashboard!</b>\n' +
      'Tu conexión entre la terminal y tu celular está 100% activa.';

    const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
      }),
    });

    if (response.ok) {
      return res.json({ success: true, message: '¡Mensaje enviado a tu Telegram!' });
    }

    const errData = await response.text();
    return res.status(502).json({
      success: false,
      message: `Error de la API de Telegram (${response.status}): ${errData}`,
    });
  } catch (err: any) {
    return res.status(500).json({
      success: false,
      message: `Error de conexión con Telegram: ${err.message}`,
    });
  }
});

// 5. Telegram trade alert dispatch
app.post('/api/telegram/alert', async (req, res) => {
  const token = process.env.TELEGRAM_BOT_TOKEN?.trim();
  const chatId = process.env.TELEGRAM_CHAT_ID?.trim();

  if (!token || !chatId) {
    return res.status(400).json({
      success: false,
      message: 'Telegram no configurado en .env.',
    });
  }

  const { coinLabel, signalType, price, rsi, strategyName, stopLossPct } = req.body;
  const isBuy = (signalType || '').toUpperCase().includes('COMPRA') || (signalType || '').toUpperCase().includes('BUY');
  const emojiAction = isBuy ? '🟢 COMPRA DETECTADA' : '🔴 VENTA / SALIDA';
  const slPct = stopLossPct || 2.0;
  const slPrice = isBuy ? price * (1.0 - slPct / 100.0) : price * (1.0 + slPct / 100.0);

  const message =
    `🔔 <b>PROYECTO ALPHA – ALERTA CUANTITATIVA</b>\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `🪙 <b>Activo:</b> ${coinLabel}\n` +
    `🎯 <b>Señal:</b> <b>${emojiAction}</b>\n` +
    `💵 <b>Precio Spot:</b> $${Number(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD\n` +
    `📊 <b>RSI (14):</b> ${rsi !== undefined ? Number(rsi).toFixed(1) : 'N/A'}\n` +
    `🤖 <b>Estrategia:</b> ${strategyName || 'Alpha Engine'}\n` +
    `🛡️ <b>Stop-Loss sugerido (-${slPct}%):</b> $${Number(slPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `⚡ <i>Alerta generada en tiempo real por tu terminal local.</i>`;

  try {
    const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
      }),
    });

    if (response.ok) {
      return res.json({ success: true });
    }
    const errData = await response.text();
    return res.status(502).json({ success: false, message: errData });
  } catch (err: any) {
    return res.status(500).json({ success: false, message: err.message });
  }
});

// Vite middleware & static serving
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
