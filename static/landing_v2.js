/**
 * landing_v2.js
 * JavaScript engine for Desk & Ledger home page:
 *  - Hero Interactive Trading Dashboard Canvas Widget
 *  - Area / Candlestick rendering modes + Crosshair Tooltip
 *  - Main Live Market Pulse Chart (6 markets)
 *  - Risk Donut Chart animation
 *  - Watchlist filtering & Live quote polling
 */

(function () {
  'use strict';

  function qs(sel) { return document.querySelector(sel); }
  function qsa(sel) { return document.querySelectorAll(sel); }

  /* =============================================================
     HERO TRADING DASHBOARD WIDGET ENGINE (PRO FINTECH GRAPH)
     ============================================================= */
  var widgetData = {
    nifty: {
      name: 'NIFTY 50',
      currency: '₹',
      tf: {
        '1D': {
          price: '24,380.15', change: '+142.30 (+0.59%)', isUp: true,
          highLbl: 'Day High', high: '24,412.50',
          lowLbl: 'Day Low', low: '24,198.30',
          rsi: '64.2 (Bullish)', signal: 'Strong Outperform',
          pts: [24238, 24220, 24212, 24245, 24268, 24285, 24275, 24290, 24310, 24335, 24365, 24385, 24412, 24395, 24380.15],
          times: ['09:15', '09:30', '09:45', '10:15', '10:45', '11:15', '11:45', '12:15', '12:45', '13:15', '13:45', '14:15', '14:45', '15:15', '15:30'],
          xLabels: ['09:15', '10:30', '12:00', '13:30', '15:00', '15:30'],
          candles: [
            { o: 24238, h: 24260, l: 24198, c: 24245, t: '09:30' },
            { o: 24245, h: 24285, l: 24240, c: 24285, t: '10:30' },
            { o: 24285, h: 24320, l: 24270, c: 24310, t: '11:30' },
            { o: 24310, h: 24345, l: 24300, c: 24335, t: '12:30' },
            { o: 24335, h: 24375, l: 24330, c: 24365, t: '13:30' },
            { o: 24365, h: 24400, l: 24350, c: 24385, t: '14:30' },
            { o: 24385, h: 24412, l: 24365, c: 24412, t: '15:00' },
            { o: 24412, h: 24410, l: 24370, c: 24380.15, t: '15:30' }
          ]
        },
        '1W': {
          price: '24,380.15', change: '+389.40 (+1.62%)', isUp: true,
          highLbl: 'Week High', high: '24,450.00',
          lowLbl: 'Week Low', low: '23,890.20',
          rsi: '61.8 (Bullish)', signal: 'Buy on Dips',
          pts: [23890, 23950, 24020, 24080, 24150, 24120, 24210, 24290, 24350, 24450, 24410, 24380.15],
          times: ['Mon AM', 'Mon PM', 'Tue AM', 'Tue PM', 'Wed AM', 'Wed PM', 'Thu AM', 'Thu PM', 'Fri AM', 'Fri Mid', 'Fri PM', 'Today'],
          xLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
          candles: [
            { o: 23890, h: 23980, l: 23870, c: 23950, t: 'Mon' },
            { o: 23950, h: 24110, l: 23960, c: 24080, t: 'Tue' },
            { o: 24080, h: 24210, l: 24060, c: 24150, t: 'Wed' },
            { o: 24150, h: 24320, l: 24150, c: 24290, t: 'Thu' },
            { o: 24290, h: 24450, l: 24260, c: 24380.15, t: 'Fri' }
          ]
        },
        '1M': {
          price: '24,380.15', change: '+1,120.80 (+4.82%)', isUp: true,
          highLbl: 'Month High', high: '24,510.80',
          lowLbl: 'Month Low', low: '23,150.00',
          rsi: '66.5 (Bullish)', signal: 'Strong Outperform',
          pts: [23150, 23260, 23380, 23450, 23580, 23690, 23820, 23980, 24150, 24320, 24510, 24420, 24380.15],
          times: ['01 Aug', '03 Aug', '06 Aug', '09 Aug', '12 Aug', '15 Aug', '18 Aug', '21 Aug', '24 Aug', '27 Aug', '30 Aug', '02 Sep', 'Today'],
          xLabels: ['01 Aug', '08 Aug', '15 Aug', '22 Aug', 'Today'],
          candles: [
            { o: 23150, h: 23380, l: 23120, c: 23380, t: 'Wk 1' },
            { o: 23380, h: 23690, l: 23320, c: 23690, t: 'Wk 2' },
            { o: 23690, h: 24020, l: 23580, c: 23980, t: 'Wk 3' },
            { o: 23980, h: 24510, l: 23920, c: 24380.15, t: 'Wk 4' }
          ]
        },
        '1Y': {
          price: '24,380.15', change: '+4,210.50 (+20.87%)', isUp: true,
          highLbl: '52W High', high: '24,850.00',
          lowLbl: '52W Low', low: '19,250.00',
          rsi: '70.4 (Overbought)', signal: 'Long-term Accumulate',
          pts: [20170, 19650, 19250, 19850, 20450, 21200, 21850, 22400, 22900, 23600, 24200, 24850, 24550, 24380.15],
          times: ['Aug 25', 'Sep 25', 'Oct 25', 'Nov 25', 'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26', 'Aug 26', 'Today'],
          xLabels: ['Aug \'25', 'Nov \'25', 'Feb \'26', 'May \'26', 'Today'],
          candles: [
            { o: 20170, h: 20500, l: 19250, c: 19850, t: 'Q3 25' },
            { o: 19850, h: 21650, l: 19700, c: 21850, t: 'Q4 25' },
            { o: 21850, h: 22600, l: 21100, c: 22900, t: 'Q1 26' },
            { o: 22900, h: 24850, l: 22400, c: 24380.15, t: 'Q2 26' }
          ]
        }
      }
    },
    reliance: {
      name: 'RELIANCE',
      currency: '₹',
      tf: {
        '1D': {
          price: '2,948.10', change: '+36.20 (+1.24%)', isUp: true,
          highLbl: 'Day High', high: '2,962.00',
          lowLbl: 'Day Low', low: '2,910.50',
          rsi: '58.7 (Moderate Buy)', signal: 'Outperform',
          pts: [2912, 2910.5, 2916, 2924, 2928, 2935, 2938, 2944, 2952, 2962, 2955, 2948.10],
          times: ['09:15', '09:30', '10:00', '10:30', '11:15', '12:00', '12:45', '13:30', '14:15', '15:00', '15:20', '15:30'],
          xLabels: ['09:15', '10:30', '12:00', '13:30', '15:00', '15:30'],
          candles: [
            { o: 2912, h: 2925, l: 2908, c: 2916, t: '09:30' },
            { o: 2916, h: 2932, l: 2914, c: 2928, t: '10:30' },
            { o: 2928, h: 2945, l: 2925, c: 2938, t: '11:30' },
            { o: 2938, h: 2952, l: 2938, c: 2944, t: '12:30' },
            { o: 2944, h: 2960, l: 2940, c: 2952, t: '13:30' },
            { o: 2952, h: 2962, l: 2946, c: 2948.10, t: '15:30' }
          ]
        },
        '1W': {
          price: '2,948.10', change: '+78.50 (+2.74%)', isUp: true,
          highLbl: 'Week High', high: '2,975.00',
          lowLbl: 'Week Low', low: '2,840.00',
          rsi: '63.1 (Bullish)', signal: 'Momentum Buy',
          pts: [2840, 2865, 2880, 2905, 2918, 2935, 2950, 2975, 2960, 2948.10],
          times: ['Mon AM', 'Mon PM', 'Tue AM', 'Tue PM', 'Wed AM', 'Wed PM', 'Thu AM', 'Thu PM', 'Fri AM', 'Today'],
          xLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
          candles: [
            { o: 2840, h: 2875, l: 2835, c: 2865, t: 'Mon' },
            { o: 2865, h: 2915, l: 2855, c: 2905, t: 'Tue' },
            { o: 2905, h: 2940, l: 2890, c: 2935, t: 'Wed' },
            { o: 2935, h: 2965, l: 2920, c: 2950, t: 'Thu' },
            { o: 2950, h: 2975, l: 2940, c: 2948.10, t: 'Fri' }
          ]
        },
        '1M': {
          price: '2,948.10', change: '+145.30 (+5.18%)', isUp: true,
          highLbl: 'Month High', high: '3,010.00',
          lowLbl: 'Month Low', low: '2,780.00',
          rsi: '65.4 (Bullish)', signal: 'Strong Outperform',
          pts: [2780, 2815, 2840, 2865, 2890, 2915, 2945, 2970, 3010, 2975, 2948.10],
          times: ['01 Aug', '04 Aug', '08 Aug', '12 Aug', '16 Aug', '20 Aug', '24 Aug', '27 Aug', '30 Aug', '02 Sep', 'Today'],
          xLabels: ['01 Aug', '08 Aug', '15 Aug', '22 Aug', 'Today'],
          candles: [
            { o: 2780, h: 2840, l: 2770, c: 2840, t: 'Wk 1' },
            { o: 2840, h: 2895, l: 2810, c: 2890, t: 'Wk 2' },
            { o: 2890, h: 2950, l: 2865, c: 2945, t: 'Wk 3' },
            { o: 2945, h: 3010, l: 2925, c: 2948.10, t: 'Wk 4' }
          ]
        },
        '1Y': {
          price: '2,948.10', change: '+512.00 (+21.02%)', isUp: true,
          highLbl: '52W High', high: '3,120.00',
          lowLbl: '52W Low', low: '2,220.00',
          rsi: '68.0 (Bullish)', signal: 'Long-term Core Holding',
          pts: [2430, 2310, 2220, 2380, 2490, 2610, 2720, 2840, 2950, 3120, 3020, 2948.10],
          times: ['Aug 25', 'Oct 25', 'Nov 25', 'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26', 'Today'],
          xLabels: ['Aug \'25', 'Nov \'25', 'Feb \'26', 'May \'26', 'Today'],
          candles: [
            { o: 2430, h: 2490, l: 2220, c: 2380, t: 'Q3 25' },
            { o: 2380, h: 2600, l: 2340, c: 2610, t: 'Q4 25' },
            { o: 2610, h: 2880, l: 2550, c: 2840, t: 'Q1 26' },
            { o: 2840, h: 3120, l: 2820, c: 2948.10, t: 'Q2 26' }
          ]
        }
      }
    },
    sp500: {
      name: 'S&P 500',
      currency: '$',
      tf: {
        '1D': {
          price: '5,540.20', change: '+28.40 (+0.51%)', isUp: true,
          highLbl: 'Day High', high: '5,548.30',
          lowLbl: 'Day Low', low: '5,498.20',
          rsi: '61.4 (Bullish)', signal: 'Outperform',
          pts: [5502, 5498.2, 5506, 5514, 5520, 5526, 5532, 5538, 5545, 5548.3, 5544, 5540.20],
          times: ['09:30', '10:00', '10:45', '11:30', '12:15', '13:00', '13:45', '14:30', '15:15', '15:45', '15:55', '16:00'],
          xLabels: ['09:30', '11:00', '12:30', '14:00', '15:30', '16:00'],
          candles: [
            { o: 5502, h: 5512, l: 5498, c: 5506, t: '10:00' },
            { o: 5506, h: 5522, l: 5504, c: 5520, t: '11:30' },
            { o: 5520, h: 5532, l: 5514, c: 5526, t: '13:00' },
            { o: 5526, h: 5544, l: 5522, c: 5538, t: '14:30' },
            { o: 5538, h: 5548, l: 5535, c: 5540.20, t: '16:00' }
          ]
        },
        '1W': {
          price: '5,540.20', change: '+92.60 (+1.70%)', isUp: true,
          highLbl: 'Week High', high: '5,560.00',
          lowLbl: 'Week Low', low: '5,420.00',
          pts: [5420, 5445, 5468, 5490, 5505, 5525, 5540, 5560, 5548, 5540.20],
          times: ['Mon AM', 'Mon PM', 'Tue AM', 'Tue PM', 'Wed AM', 'Wed PM', 'Thu AM', 'Thu PM', 'Fri AM', 'Today'],
          xLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
          rsi: '63.8 (Bullish)', signal: 'Macro Momentum',
          candles: [
            { o: 5420, h: 5460, l: 5415, c: 5445, t: 'Mon' },
            { o: 5445, h: 5495, l: 5435, c: 5490, t: 'Tue' },
            { o: 5490, h: 5520, l: 5475, c: 5505, t: 'Wed' },
            { o: 5505, h: 5545, l: 5500, c: 5540, t: 'Thu' },
            { o: 5540, h: 5560, l: 5525, c: 5540.20, t: 'Fri' }
          ]
        },
        '1M': {
          price: '5,540.20', change: '+215.10 (+4.04%)', isUp: true,
          highLbl: 'Month High', high: '5,585.00',
          lowLbl: 'Month Low', low: '5,310.00',
          rsi: '65.2 (Bullish)', signal: 'Broad Index Buy',
          pts: [5310, 5345, 5380, 5415, 5455, 5490, 5525, 5560, 5585, 5555, 5540.20],
          times: ['01 Aug', '04 Aug', '08 Aug', '12 Aug', '16 Aug', '20 Aug', '24 Aug', '27 Aug', '30 Aug', '02 Sep', 'Today'],
          xLabels: ['01 Aug', '08 Aug', '15 Aug', '22 Aug', 'Today'],
          candles: [
            { o: 5310, h: 5390, l: 5300, c: 5380, t: 'Wk 1' },
            { o: 5380, h: 5465, l: 5350, c: 5455, t: 'Wk 2' },
            { o: 5455, h: 5530, l: 5420, c: 5525, t: 'Wk 3' },
            { o: 5525, h: 5585, l: 5510, c: 5540.20, t: 'Wk 4' }
          ]
        },
        '1Y': {
          price: '5,540.20', change: '+890.50 (+19.15%)', isUp: true,
          highLbl: '52W High', high: '5,660.00',
          lowLbl: '52W Low', low: '4,350.00',
          rsi: '69.5 (Strong Bullish)', signal: 'Structural Uptrend',
          pts: [4650, 4480, 4350, 4580, 4790, 4980, 5160, 5320, 5460, 5660, 5580, 5540.20],
          times: ['Aug 25', 'Oct 25', 'Nov 25', 'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26', 'Today'],
          xLabels: ['Aug \'25', 'Nov \'25', 'Feb \'26', 'May \'26', 'Today'],
          candles: [
            { o: 4650, h: 4720, l: 4350, c: 4580, t: 'Q3 25' },
            { o: 4580, h: 4980, l: 4520, c: 4980, t: 'Q4 25' },
            { o: 4980, h: 5320, l: 4900, c: 5320, t: 'Q1 26' },
            { o: 5320, h: 5660, l: 5200, c: 5540.20, t: 'Q2 26' }
          ]
        }
      }
    },
    nvda: {
      name: 'NVIDIA',
      currency: '$',
      tf: {
        '1D': {
          price: '142.66', change: '+4.72 (+3.42%)', isUp: true,
          highLbl: 'Day High', high: '144.20',
          lowLbl: 'Day Low', low: '137.50',
          rsi: '72.1 (Overbought/Strong)', signal: 'High Volatility Buy',
          pts: [137.5, 138.2, 138.8, 139.6, 140.5, 141.2, 142.0, 143.2, 144.2, 143.5, 142.66],
          times: ['09:30', '10:00', '10:45', '11:30', '12:15', '13:00', '13:45', '14:30', '15:15', '15:45', '16:00'],
          xLabels: ['09:30', '11:00', '12:30', '14:00', '15:30', '16:00'],
          candles: [
            { o: 137.5, h: 139.5, l: 137.0, c: 138.8, t: '10:00' },
            { o: 138.8, h: 141.0, l: 138.2, c: 140.5, t: '11:30' },
            { o: 140.5, h: 142.5, l: 139.8, c: 142.0, t: '13:00' },
            { o: 142.0, h: 144.2, l: 141.2, c: 144.2, t: '14:30' },
            { o: 144.2, h: 144.2, l: 142.2, c: 142.66, t: '16:00' }
          ]
        },
        '1W': {
          price: '142.66', change: '+12.10 (+9.27%)', isUp: true,
          highLbl: 'Week High', high: '146.50',
          lowLbl: 'Week Low', low: '128.00',
          rsi: '74.5 (High Momentum)', signal: 'Breakout Confirmed',
          pts: [128.0, 131.5, 134.0, 136.5, 139.0, 142.0, 145.0, 146.5, 144.0, 142.66],
          times: ['Mon AM', 'Mon PM', 'Tue AM', 'Tue PM', 'Wed AM', 'Wed PM', 'Thu AM', 'Thu PM', 'Fri AM', 'Today'],
          xLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
          candles: [
            { o: 128.0, h: 133.0, l: 127.5, c: 131.5, t: 'Mon' },
            { o: 131.5, h: 138.0, l: 130.0, c: 136.5, t: 'Tue' },
            { o: 136.5, h: 141.5, l: 135.0, c: 139.0, t: 'Wed' },
            { o: 139.0, h: 145.0, l: 139.0, c: 145.0, t: 'Thu' },
            { o: 145.0, h: 146.5, l: 142.0, c: 142.66, t: 'Fri' }
          ]
        },
        '1M': {
          price: '142.66', change: '+24.80 (+21.04%)', isUp: true,
          highLbl: 'Month High', high: '148.00',
          lowLbl: 'Month Low', low: '115.00',
          rsi: '76.8 (Super Bullish)', signal: 'High Volatility Buy',
          pts: [115.0, 120.0, 125.0, 129.0, 134.0, 138.5, 143.0, 148.0, 145.0, 142.66],
          times: ['01 Aug', '04 Aug', '08 Aug', '12 Aug', '16 Aug', '20 Aug', '24 Aug', '28 Aug', '01 Sep', 'Today'],
          xLabels: ['01 Aug', '08 Aug', '15 Aug', '22 Aug', 'Today'],
          candles: [
            { o: 115.0, h: 125.5, l: 114.0, c: 125.0, t: 'Wk 1' },
            { o: 125.0, h: 136.0, l: 121.5, c: 134.0, t: 'Wk 2' },
            { o: 134.0, h: 144.5, l: 131.0, c: 143.0, t: 'Wk 3' },
            { o: 143.0, h: 148.0, l: 141.0, c: 142.66, t: 'Wk 4' }
          ]
        },
        '1Y': {
          price: '142.66', change: '+86.40 (+153.57%)', isUp: true,
          highLbl: '52W High', high: '152.00',
          lowLbl: '52W Low', low: '42.00',
          rsi: '81.2 (Extreme Bullish)', signal: 'AI Cycle Leader',
          pts: [56.2, 48.0, 42.0, 58.5, 74.0, 92.0, 110.0, 128.0, 142.0, 152.0, 146.0, 142.66],
          times: ['Aug 25', 'Oct 25', 'Nov 25', 'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26', 'Today'],
          xLabels: ['Aug \'25', 'Nov \'25', 'Feb \'26', 'May \'26', 'Today'],
          candles: [
            { o: 56.2, h: 62.0, l: 42.0, c: 58.5, t: 'Q3 25' },
            { o: 58.5, h: 76.0, l: 56.0, c: 74.0, t: 'Q4 25' },
            { o: 74.0, h: 104.0, l: 70.0, c: 110.0, t: 'Q1 26' },
            { o: 110.0, h: 152.0, l: 95.0, c: 142.66, t: 'Q2 26' }
          ]
        }
      }
    },
    btc: {
      name: 'BITCOIN',
      currency: '$',
      tf: {
        '1D': {
          price: '64,250.00', change: '-410.00 (-0.63%)', isUp: false,
          highLbl: 'Day High', high: '65,100.00',
          lowLbl: 'Day Low', low: '64,100.00',
          rsi: '46.8 (Neutral)', signal: 'Consolidation',
          pts: [64650, 64800, 65050, 65100, 64920, 64750, 64550, 64380, 64280, 64100, 64220, 64250],
          times: ['00:00', '02:30', '05:00', '07:30', '10:00', '12:30', '15:00', '17:30', '20:00', '22:00', '23:15', 'Now'],
          xLabels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', 'Now'],
          candles: [
            { o: 64650, h: 64950, l: 64580, c: 64800, t: '04:00' },
            { o: 64800, h: 65100, l: 64680, c: 65050, t: '08:00' },
            { o: 65050, h: 65080, l: 64600, c: 64750, t: '12:00' },
            { o: 64750, h: 64800, l: 64250, c: 64380, t: '16:00' },
            { o: 64380, h: 64600, l: 64100, c: 64280, t: '20:00' },
            { o: 64280, h: 64400, l: 64150, c: 64250, t: '23:59' }
          ]
        },
        '1W': {
          price: '64,250.00', change: '+2,150.00 (+3.46%)', isUp: true,
          highLbl: 'Week High', high: '66,200.00',
          lowLbl: 'Week Low', low: '61,800.00',
          rsi: '55.2 (Moderate Buy)', signal: 'Rebound Phase',
          pts: [61800, 62450, 62900, 63600, 64200, 64900, 65600, 66200, 65400, 64700, 64250],
          times: ['Mon AM', 'Mon PM', 'Tue AM', 'Tue PM', 'Wed AM', 'Wed PM', 'Thu AM', 'Thu PM', 'Fri AM', 'Weekend', 'Today'],
          xLabels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          candles: [
            { o: 61800, h: 62800, l: 61600, c: 62450, t: 'Mon' },
            { o: 62450, h: 64200, l: 62000, c: 63600, t: 'Tue' },
            { o: 63600, h: 65600, l: 63300, c: 64900, t: 'Wed' },
            { o: 64900, h: 66200, l: 64700, c: 65600, t: 'Thu' },
            { o: 65600, h: 66100, l: 64100, c: 64250, t: 'Weekend' }
          ]
        },
        '1M': {
          price: '64,250.00', change: '+5,400.00 (+9.18%)', isUp: true,
          highLbl: 'Month High', high: '68,500.00',
          lowLbl: 'Month Low', low: '57,200.00',
          rsi: '59.6 (Bullish)', signal: 'Accumulation Zone',
          pts: [57200, 59100, 60800, 62400, 64200, 65800, 67200, 68500, 66800, 65200, 64250],
          times: ['01 Aug', '04 Aug', '08 Aug', '12 Aug', '16 Aug', '20 Aug', '24 Aug', '28 Aug', '01 Sep', '03 Sep', 'Today'],
          xLabels: ['01 Aug', '08 Aug', '15 Aug', '22 Aug', 'Today'],
          candles: [
            { o: 57200, h: 61200, l: 56800, c: 60800, t: 'Wk 1' },
            { o: 60800, h: 64800, l: 59200, c: 64200, t: 'Wk 2' },
            { o: 64200, h: 68500, l: 62100, c: 67200, t: 'Wk 3' },
            { o: 67200, h: 68200, l: 63800, c: 64250, t: 'Wk 4' }
          ]
        },
        '1Y': {
          price: '64,250.00', change: '+35,100.00 (+120.41%)', isUp: true,
          highLbl: '52W High', high: '73,750.00',
          lowLbl: '52W Low', low: '26,000.00',
          rsi: '67.3 (Bullish)', signal: 'Macro Halving Cycle',
          pts: [29150, 26000, 34500, 42100, 48900, 56000, 64500, 73750, 67200, 58400, 66800, 64250],
          times: ['Sep 25', 'Oct 25', 'Nov 25', 'Dec 25', 'Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26', 'Today'],
          xLabels: ['Sep \'25', 'Nov \'25', 'Jan \'26', 'Mar \'26', 'May \'26', 'Jul \'26', 'Now'],
          candles: [
            { o: 29150, h: 35000, l: 26000, c: 34500, t: 'Q3 25' },
            { o: 34500, h: 45000, l: 33800, c: 42100, t: 'Q4 25' },
            { o: 42100, h: 73750, l: 42000, c: 64500, t: 'Q1 26' },
            { o: 64500, h: 71500, l: 56500, c: 64250, t: 'Q2 26' }
          ]
        }
      }
    }
  };

  var activeSymbol = 'nifty';
  var activeTimeframe = '1D';
  var chartMode = 'line'; // 'line' or 'candles'
  var widgetAnimOff = 0;
  var mouseX = -1;
  var mouseY = -1;

  var widgetCanvas = qs('#heroWidgetCanvas');
  var widgetWrap = qs('#heroWidgetCanvasWrap');
  var tooltip = qs('#heroChartTooltip');

  function getActiveWidgetData() {
    var sym = widgetData[activeSymbol] || widgetData.nifty;
    var tfData = (sym.tf && sym.tf[activeTimeframe]) || (sym.tf && sym.tf['1D']) || sym;
    return {
      name: sym.name,
      currency: sym.currency,
      price: tfData.price,
      change: tfData.change,
      isUp: tfData.isUp,
      highLbl: tfData.highLbl || 'Period High',
      high: tfData.high,
      lowLbl: tfData.lowLbl || 'Period Low',
      low: tfData.low,
      rsi: tfData.rsi,
      signal: tfData.signal,
      pts: tfData.pts || [],
      times: tfData.times || [],
      xLabels: tfData.xLabels || [],
      candles: tfData.candles || []
    };
  }

  function updateWidgetUI() {
    var d = getActiveWidgetData();
    var nameEl = qs('#heroWName');
    var priceEl = qs('#heroWPrice');
    var changeEl = qs('#heroWChange');
    var highLbl = qs('#wmHighLbl');
    var highEl = qs('#wmHigh');
    var lowLbl = qs('#wmLowLbl');
    var lowEl = qs('#wmLow');
    var rsiEl = qs('#wmRsi');
    var signalEl = qs('#wmSignal');

    if (nameEl) nameEl.textContent = d.name;
    if (priceEl) priceEl.textContent = d.price;
    if (changeEl) {
      changeEl.textContent = d.change;
      changeEl.className = 'wpr-change ' + (d.isUp ? 'up' : 'down');
    }
    if (highLbl) highLbl.textContent = d.highLbl;
    if (highEl) highEl.textContent = d.high;
    if (lowLbl) lowLbl.textContent = d.lowLbl;
    if (lowEl) lowEl.textContent = d.low;
    if (rsiEl) rsiEl.textContent = d.rsi;
    if (signalEl) signalEl.textContent = d.signal;
  }

  // Smooth Catmull-Rom spline helper for continuous, organic financial curves
  function buildSplinePath(ctx, points) {
    if (!points || points.length < 2) return;
    ctx.moveTo(points[0].x, points[0].y);
    for (var i = 0; i < points.length - 1; i++) {
      var p0 = i > 0 ? points[i - 1] : points[i];
      var p1 = points[i];
      var p2 = points[i + 1];
      var p3 = (i + 2 < points.length) ? points[i + 2] : p2;

      var cp1x = p1.x + (p2.x - p0.x) / 5.5;
      var cp1y = p1.y + (p2.y - p0.y) / 5.5;
      var cp2x = p2.x - (p3.x - p1.x) / 5.5;
      var cp2y = p2.y - (p3.y - p1.y) / 5.5;

      ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
    }
  }

  if (widgetCanvas && widgetWrap) {
    var wCtx = widgetCanvas.getContext('2d');

    function resizeWidgetCanvas() {
      var dpr = window.devicePixelRatio || 1;
      var rect = widgetWrap.getBoundingClientRect();
      widgetCanvas.width = rect.width * dpr;
      widgetCanvas.height = rect.height * dpr;
      wCtx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resizeWidgetCanvas);
    resizeWidgetCanvas();

    widgetWrap.addEventListener('mousemove', function (e) {
      var rect = widgetWrap.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
    });

    widgetWrap.addEventListener('mouseleave', function () {
      mouseX = -1;
      mouseY = -1;
      if (tooltip) tooltip.style.display = 'none';
    });

    function drawHeroWidget() {
      var w = widgetWrap.clientWidth;
      var h = widgetWrap.clientHeight;
      wCtx.clearRect(0, 0, w, h);

      var d = getActiveWidgetData();
      widgetAnimOff += 0.035;

      // Margins
      var padL = 12;
      var padR = 64; // right margin for Y-axis price labels
      var padT = 16;
      var padB = 26; // bottom margin for X-axis time labels
      var plotW = Math.max(w - padL - padR, 100);
      var plotH = Math.max(h - padT - padB, 100);
      var chartBaseline = padT + plotH;

      var pts = d.pts;
      if (!pts || pts.length === 0) {
        requestAnimationFrame(drawHeroWidget);
        return;
      }

      var minP = Math.min.apply(null, pts);
      var maxP = Math.max.apply(null, pts);
      var paddingP = (maxP - minP) * 0.10 || 1;
      minP -= paddingP;
      maxP += paddingP;
      var rngP = maxP - minP || 1;
      var isLight = document.documentElement.getAttribute('data-theme') === 'light';
      var gridColor = isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.045)';
      var textAxisColor = isLight ? 'rgba(100, 116, 139, 0.85)' : 'rgba(148, 163, 184, 0.75)';

      // 1. Horizontal Dashed Grid Lines & Right Y-Axis Price Labels
      var gridSteps = 4;
      wCtx.font = '10px "Plus Jakarta Sans", "Manrope", sans-serif';
      wCtx.fillStyle = textAxisColor;
      wCtx.textAlign = 'right';
      wCtx.textBaseline = 'middle';

      for (var gi = 0; gi <= gridSteps; gi++) {
        var gy = padT + (gi / gridSteps) * plotH;
        var gPrice = maxP - (gi / gridSteps) * (maxP - minP);

        wCtx.beginPath();
        wCtx.strokeStyle = gridColor;
        wCtx.lineWidth = 1;
        wCtx.setLineDash([3, 4]);
        wCtx.moveTo(padL, gy);
        wCtx.lineTo(padL + plotW, gy);
        wCtx.stroke();
        wCtx.setLineDash([]);

        var priceStr = gPrice >= 1000 ? gPrice.toLocaleString('en-US', { maximumFractionDigits: 0 }) : gPrice.toFixed(2);
        wCtx.fillText((d.currency || '') + priceStr, w - 8, gy);
      }

      // 2. Bottom Timeline Labels (X-Axis)
      var xLabels = d.xLabels || [];
      if (xLabels.length > 0) {
        wCtx.fillStyle = textAxisColor;
        wCtx.font = '10px "Plus Jakarta Sans", "Manrope", sans-serif';
        wCtx.textBaseline = 'top';
        for (var xi = 0; xi < xLabels.length; xi++) {
          var xlX = padL + (xi / (xLabels.length - 1)) * plotW;
          wCtx.textAlign = (xi === 0) ? 'left' : (xi === xLabels.length - 1) ? 'right' : 'center';
          wCtx.fillText(xLabels[xi], xlX, chartBaseline + 8);
        }
      }

      var lineColor = d.isUp ? (isLight ? '#00A86B' : '#10D890') : (isLight ? '#E11D48' : '#FF4D6D');
      var areaColor1 = d.isUp ? (isLight ? 'rgba(0, 168, 107, 0.22)' : 'rgba(16, 216, 144, 0.25)') : (isLight ? 'rgba(225, 29, 72, 0.22)' : 'rgba(255, 77, 109, 0.25)');
      var areaColor2 = d.isUp ? (isLight ? 'rgba(0, 168, 107, 0.02)' : 'rgba(16, 216, 144, 0.01)') : (isLight ? 'rgba(225, 29, 72, 0.02)' : 'rgba(255, 77, 109, 0.01)');

      if (chartMode === 'line') {
        var ptsCopy = pts.slice();
        // Subtle micro-pulse on live end tick
        var liveSwing = (maxP - minP) * 0.005 || 0.4;
        ptsCopy[ptsCopy.length - 1] += Math.sin(widgetAnimOff * 2) * liveSwing;

        var coords = ptsCopy.map(function (p, i) {
          return {
            x: padL + (i / (ptsCopy.length - 1)) * plotW,
            y: padT + plotH - ((p - minP) / rngP) * plotH,
            val: p,
            idx: i
          };
        });

        // 1. Glowing Area Fill Gradient
        wCtx.beginPath();
        wCtx.moveTo(coords[0].x, chartBaseline);
        wCtx.lineTo(coords[0].x, coords[0].y);
        buildSplinePath(wCtx, coords);
        wCtx.lineTo(coords[coords.length - 1].x, chartBaseline);
        wCtx.closePath();

        var areaGrad = wCtx.createLinearGradient(0, padT, 0, chartBaseline);
        areaGrad.addColorStop(0, areaColor1);
        areaGrad.addColorStop(0.75, areaColor2);
        areaGrad.addColorStop(1, isLight ? 'rgba(255, 255, 255, 0)' : 'rgba(8, 11, 16, 0)');
        wCtx.fillStyle = areaGrad;
        wCtx.fill();

        // 2. Stroke Line with Bloom Glow
        wCtx.save();
        wCtx.beginPath();
        buildSplinePath(wCtx, coords);
        wCtx.shadowColor = lineColor;
        wCtx.shadowBlur = isLight ? 4 : 8;
        wCtx.strokeStyle = lineColor;
        wCtx.lineWidth = 2.2;
        wCtx.stroke();
        wCtx.restore();

        // 3. Pulsing End Beacon Dot
        var endPt = coords[coords.length - 1];
        wCtx.beginPath();
        wCtx.arc(endPt.x, endPt.y, 4, 0, Math.PI * 2);
        wCtx.fillStyle = lineColor;
        wCtx.fill();

        // Concentric animated ripple ring
        var rippleR = 7 + Math.sin(widgetAnimOff * 3) * 3.5;
        wCtx.beginPath();
        wCtx.arc(endPt.x, endPt.y, rippleR, 0, Math.PI * 2);
        wCtx.strokeStyle = lineColor;
        wCtx.lineWidth = 1.2;
        wCtx.stroke();

        // 4. Interactive Crosshair & HUD
        if (mouseX >= padL && mouseX <= padL + plotW) {
          var closest = coords[0];
          var minDist = Math.abs(coords[0].x - mouseX);
          for (var k = 1; k < coords.length; k++) {
            var dist = Math.abs(coords[k].x - mouseX);
            if (dist < minDist) { minDist = dist; closest = coords[k]; }
          }

          // Vertical crosshair
          wCtx.save();
          wCtx.strokeStyle = isLight ? 'rgba(0, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.22)';
          wCtx.lineWidth = 1;
          wCtx.setLineDash([4, 4]);
          wCtx.beginPath();
          wCtx.moveTo(closest.x, padT);
          wCtx.lineTo(closest.x, chartBaseline);
          wCtx.stroke();

          // Horizontal crosshair
          wCtx.beginPath();
          wCtx.moveTo(padL, closest.y);
          wCtx.lineTo(padL + plotW, closest.y);
          wCtx.stroke();
          wCtx.restore();

          // Glowing hover dot
          wCtx.beginPath();
          wCtx.arc(closest.x, closest.y, 5, 0, Math.PI * 2);
          wCtx.fillStyle = isLight ? '#0F172A' : '#FFFFFF';
          wCtx.shadowColor = lineColor;
          wCtx.shadowBlur = 8;
          wCtx.fill();
          wCtx.shadowBlur = 0;

          // Floating Y-axis Badge
          var badgePriceStr = d.currency + closest.val.toLocaleString('en-US', { minimumFractionDigits: 2 });
          wCtx.fillStyle = isLight ? 'rgba(255, 255, 255, 0.98)' : 'rgba(11, 15, 23, 0.95)';
          wCtx.fillRect(padL + plotW + 2, closest.y - 9, padR - 6, 18);
          wCtx.strokeStyle = lineColor;
          wCtx.lineWidth = 1;
          wCtx.strokeRect(padL + plotW + 2, closest.y - 9, padR - 6, 18);
          wCtx.fillStyle = isLight ? '#0F172A' : '#FFFFFF';
          wCtx.font = '600 10px "Plus Jakarta Sans", "Manrope", sans-serif';
          wCtx.textAlign = 'center';
          wCtx.textBaseline = 'middle';
          wCtx.fillText(badgePriceStr, padL + plotW + (padR - 4) / 2, closest.y);

          // Update Tooltip
          if (tooltip) {
            tooltip.style.display = 'flex';
            var ttPrice = qs('#ttPrice');
            var ttChange = qs('#ttChange');
            var ttTime = qs('#ttTime');
            var startVal = pts[0];
            var diffPct = ((closest.val - startVal) / startVal) * 100;
            var diffStr = (diffPct >= 0 ? '+' : '') + diffPct.toFixed(2) + '%';

            if (ttPrice) ttPrice.textContent = badgePriceStr;
            if (ttChange) {
              ttChange.textContent = diffStr + ' in ' + activeTimeframe;
              ttChange.className = 'tt-change ' + (diffPct >= 0 ? 'up' : 'down');
            }
            if (ttTime) {
              var tStr = (d.times && d.times[closest.idx]) ? d.times[closest.idx] : 'Point ' + (closest.idx + 1);
              ttTime.textContent = tStr;
            }
          }
        }
      } else {
        // Candlestick rendering mode
        var cndls = d.candles;
        if (cndls.length > 0) {
          var cW = Math.max((plotW / cndls.length) * 0.58, 5);
          var mnC = Math.min.apply(null, cndls.map(function (c) { return c.l; })) - paddingP;
          var mxC = Math.max.apply(null, cndls.map(function (c) { return c.h; })) + paddingP;
          var rngC = mxC - mnC || 1;

          var hoveredCandle = null;
          var minCDist = 999999;

          cndls.forEach(function (c, idx) {
            var cx = padL + (idx / (cndls.length - 1)) * plotW;
            var isBull = c.c >= c.o;
            var yOpen = padT + plotH - ((c.o - mnC) / rngC) * plotH;
            var yClose = padT + plotH - ((c.c - mnC) / rngC) * plotH;
            var yHigh = padT + plotH - ((c.h - mnC) / rngC) * plotH;
            var yLow = padT + plotH - ((c.l - mnC) / rngC) * plotH;

            var color = isBull ? (isLight ? '#00A86B' : '#10D890') : (isLight ? '#E11D48' : '#FF4D6D');

            // Wick line
            wCtx.strokeStyle = color;
            wCtx.lineWidth = 1.4;
            wCtx.beginPath();
            wCtx.moveTo(cx, yHigh);
            wCtx.lineTo(cx, yLow);
            wCtx.stroke();

            // Candle body
            var topY = Math.min(yOpen, yClose);
            var bH = Math.max(Math.abs(yOpen - yClose), 3);
            wCtx.fillStyle = color;
            wCtx.fillRect(cx - cW / 2, topY, cW, bH);

            if (mouseX >= padL && mouseX <= padL + plotW) {
              var distC = Math.abs(cx - mouseX);
              if (distC < minCDist) {
                minCDist = distC;
                hoveredCandle = { c: c, cx: cx, cy: (topY + bH / 2) };
              }
            }
          });

          // Crosshair tooltip for candles
          if (hoveredCandle && mouseX >= padL && minCDist < 35 && tooltip) {
            tooltip.style.display = 'flex';
            var ttP = qs('#ttPrice');
            var ttC = qs('#ttChange');
            var ttT = qs('#ttTime');
            var cDiff = ((hoveredCandle.c.c - hoveredCandle.c.o) / hoveredCandle.c.o) * 100;

            if (ttP) ttP.textContent = d.currency + hoveredCandle.c.c.toLocaleString('en-US', { minimumFractionDigits: 2 });
            if (ttC) {
              ttC.textContent = (cDiff >= 0 ? '+' : '') + cDiff.toFixed(2) + '% (O:' + hoveredCandle.c.o + ' H:' + hoveredCandle.c.h + ' L:' + hoveredCandle.c.l + ')';
              ttC.className = 'tt-change ' + (cDiff >= 0 ? 'up' : 'down');
            }
            if (ttT) ttT.textContent = hoveredCandle.c.t || 'Candle';
          }
        }
      }

      requestAnimationFrame(drawHeroWidget);
    }
    requestAnimationFrame(drawHeroWidget);

    // Asset Tab buttons logic
    qsa('.w-tab').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.w-tab').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        activeSymbol = btn.getAttribute('data-symbol');
        updateWidgetUI();
      });
    });

    // Timeframe buttons logic (1D, 1W, 1M, 1Y)
    qsa('.tf-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.tf-btn').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var tf = btn.getAttribute('data-tf') || btn.textContent.trim();
        if (tf) {
          activeTimeframe = tf;
          updateWidgetUI();
        }
      });
    });

    // Mode buttons (Line vs Candle)
    qsa('.cm-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.cm-btn').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        chartMode = btn.getAttribute('data-mode');
      });
    });
  }

  /* =============================================================
     MAIN LIVE MARKET PULSE CHART (TRADINGVIEW CANDLESTICK ENGINE - 6 MARKETS)
     ============================================================= */
  
  // Helper to generate realistic dense intraday session candles (~46 candles)
  function createMarketCandles(baseOpen, trendPoints, startTime, stepMins, volBase, curSym) {
    var candles = [];
    var cur = baseOpen;
    var timeMin = 9 * 60 + 15; // 09:15 default
    if (startTime === '09:30') timeMin = 9 * 60 + 30;
    if (startTime === '00:00') timeMin = 0;

    for (var i = 0; i < trendPoints.length; i++) {
      var target = trendPoints[i];
      var openP = cur;
      var closeP = target;
      var delta = closeP - openP;
      var wickU = Math.abs(delta) * (0.2 + (i % 5) * 0.15) + (baseOpen * 0.0008);
      var wickL = Math.abs(delta) * (0.2 + ((i + 2) % 5) * 0.15) + (baseOpen * 0.0008);
      var highP = Math.max(openP, closeP) + wickU;
      var lowP = Math.min(openP, closeP) - wickL;

      var hh = Math.floor(timeMin / 60) % 24;
      var mm = timeMin % 60;
      var tStr = (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
      timeMin += stepMins;

      var v = Math.round(volBase * (0.6 + Math.sin(i * 0.45) * 0.35 + ((i === 18 || i === 31 || i === 42) ? 0.9 : 0)));
      candles.push({
        t: tStr,
        o: parseFloat(openP.toFixed(2)),
        h: parseFloat(highP.toFixed(2)),
        l: parseFloat(lowP.toFixed(2)),
        c: parseFloat(closeP.toFixed(2)),
        v: v
      });
      cur = closeP;
    }
    return candles;
  }

  var niftyTrends = [
    24238, 24245, 24228, 24215, 24222, 24210, 24205, 24198, 24218, 24235,
    24228, 24242, 24255, 24248, 24262, 24275, 24288, 24310, 24325, 24318,
    24305, 24315, 24330, 24345, 24360, 24375, 24368, 24382, 24395, 24412,
    24405, 24390, 24382, 24370, 24362, 24378, 24392, 24408, 24398, 24385,
    24372, 24365, 24370, 24382, 24378, 24380.15
  ];

  var sensexTrends = [
    79728, 79745, 79710, 79680, 79695, 79660, 79650, 79685, 79720, 79765,
    79740, 79780, 79820, 79850, 79890, 79930, 79980, 80030, 80075, 80050,
    80020, 80060, 80110, 80160, 80210, 80260, 80240, 80290, 80330, 80350,
    80320, 80290, 80265, 80240, 80220, 80250, 80280, 80310, 80285, 80250,
    80230, 80215, 80225, 80240, 80220, 80210.35
  ];

  var sp500Trends = [
    5511.8, 5514.2, 5508.5, 5502.1, 5498.2, 5504.0, 5509.5, 5515.2, 5512.0, 5518.4,
    5522.0, 5526.5, 5524.0, 5528.2, 5532.0, 5536.5, 5540.0, 5538.2, 5542.5, 5546.0,
    5548.3, 5545.0, 5542.2, 5540.0, 5543.5, 5546.2, 5544.0, 5541.5, 5538.0, 5536.2,
    5539.0, 5541.5, 5543.8, 5545.2, 5543.0, 5541.2, 5539.5, 5538.0, 5540.5, 5542.2,
    5541.0, 5539.8, 5540.5, 5541.8, 5539.5, 5540.2
  ];

  var nasdaqTrends = [
    19710, 19725, 19702, 19690, 19705, 19720, 19735, 19725, 19745, 19760,
    19750, 19775, 19790, 19810, 19800, 19825, 19845, 19860, 19850, 19835,
    19820, 19840, 19855, 19850, 19835, 19820, 19810, 19825, 19840, 19855,
    19845, 19830, 19815, 19805, 19820, 19835, 19848, 19840, 19830, 19818,
    19812, 19822, 19830, 19825, 19818, 19820.5
  ];

  var btcTrends = [
    64660, 64720, 64790, 64850, 64920, 65040, 65100, 65050, 64980, 64920,
    64860, 64800, 64750, 64680, 64620, 64550, 64500, 64440, 64380, 64320,
    64280, 64230, 64180, 64140, 64100, 64130, 64170, 64210, 64250, 64280,
    64240, 64200, 64160, 64120, 64150, 64180, 64220, 64260, 64240, 64210,
    64180, 64200, 64230, 64260, 64235, 64250
  ];

  var goldTrends = [
    2362.8, 2364.5, 2362.0, 2359.8, 2358.0, 2356.2, 2359.0, 2362.5, 2365.0, 2368.2,
    2370.5, 2372.8, 2375.0, 2374.2, 2376.5, 2379.0, 2381.2, 2383.5, 2385.0, 2384.2,
    2382.5, 2380.0, 2378.5, 2380.2, 2382.0, 2383.5, 2384.8, 2383.2, 2381.5, 2380.0,
    2379.2, 2380.8, 2382.5, 2384.0, 2383.0, 2381.8, 2380.5, 2381.5, 2382.8, 2383.5,
    2382.2, 2381.0, 2380.5, 2381.8, 2382.0, 2381.4
  ];

  var marketData = {
    nifty: {
      name: 'NIFTY 50', currency: '₹', price: '24,380.15', change: '+142.30 (+0.59%)', isUp: true,
      open: '24,238.00', high: '24,412.50', low: '24,198.30', prev: '24,237.85',
      h52: '26,277.35', l52: '21,964.60',
      signal: { idx: 17, type: 'BUY', label: 'AI BUY', price: '₹24,310.00' },
      candles: createMarketCandles(24238.00, niftyTrends, '09:15', 8, 48, '₹'),
      xLabels: ['09:15', '10:15', '11:15', '12:15', '13:15', '14:15', '15:30']
    },
    sensex: {
      name: 'SENSEX', currency: '₹', price: '80,210.35', change: '+482.10 (+0.60%)', isUp: true,
      open: '79,728.00', high: '80,350.20', low: '79,650.40', prev: '79,728.25',
      h52: '82,129.49', l52: '65,248.80',
      signal: { idx: 16, type: 'BUY', label: 'AI BUY', price: '₹79,980.00' },
      candles: createMarketCandles(79728.00, sensexTrends, '09:15', 8, 38, '₹'),
      xLabels: ['09:15', '10:15', '11:15', '12:15', '13:15', '14:15', '15:30']
    },
    sp500: {
      name: 'S&P 500', currency: '$', price: '5,540.20', change: '+28.40 (+0.51%)', isUp: true,
      open: '5,511.80', high: '5,548.30', low: '5,498.20', prev: '5,511.80',
      h52: '$5,669.67', l52: '$4,103.78',
      signal: { idx: 15, type: 'BUY', label: 'AI BUY', price: '$5,536.50' },
      candles: createMarketCandles(5511.80, sp500Trends, '09:30', 8, 65, '$'),
      xLabels: ['09:30', '10:30', '11:45', '13:00', '14:15', '15:15', '16:00']
    },
    nasdaq: {
      name: 'NASDAQ 100', currency: '$', price: '19,820.50', change: '+110.30 (+0.56%)', isUp: true,
      open: '19,710.00', high: '19,860.20', low: '19,690.10', prev: '19,710.20',
      h52: '$20,690.97', l52: '$14,058.30',
      signal: { idx: 16, type: 'BUY', label: 'AI BUY', price: '$19,845.00' },
      candles: createMarketCandles(19710.00, nasdaqTrends, '09:30', 8, 72, '$'),
      xLabels: ['09:30', '10:30', '11:45', '13:00', '14:15', '15:15', '16:00']
    },
    btc: {
      name: 'Bitcoin / USD', currency: '$', price: '$64,250.00', change: '-410.00 (-0.63%)', isUp: false,
      open: '$64,660.00', high: '$65,100.00', low: '$64,100.00', prev: '$64,660.00',
      h52: '$73,750.00', l52: '$38,500.00',
      signal: { idx: 20, type: 'SELL', label: 'AI EXIT', price: '$64,320.00' },
      candles: createMarketCandles(64660.00, btcTrends, '00:00', 30, 55, '$'),
      xLabels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:30']
    },
    gold: {
      name: 'Gold (USD/oz)', currency: '$', price: '$2,381.40', change: '+18.60 (+0.79%)', isUp: true,
      open: '$2,362.80', high: '$2,385.00', low: '$2,356.20', prev: '$2,362.80',
      h52: '$2,483.70', l52: '$1,810.20',
      signal: { idx: 14, type: 'BUY', label: 'AI BUY', price: '$2,376.50' },
      candles: createMarketCandles(2362.80, goldTrends, '00:00', 30, 42, '$'),
      xLabels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:30']
    }
  };

  var currentMarket = 'nifty';
  var homeAnimOffset = 0;
  var homeMouseX = -1;

  var homeCanvas = qs('#homeMainChart');
  var homeTooltip = qs('#homeChartTooltip');

  if (homeCanvas) {
    var hCtx = homeCanvas.getContext('2d');
    var homeWrap = homeCanvas.parentElement;

    function resizeHomeChart() {
      var dpr = window.devicePixelRatio || 1;
      homeCanvas.width = homeWrap.clientWidth * dpr;
      homeCanvas.height = homeWrap.clientHeight * dpr;
      hCtx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resizeHomeChart);
    resizeHomeChart();

    if (homeWrap) {
      homeWrap.addEventListener('mousemove', function (e) {
        var rect = homeWrap.getBoundingClientRect();
        homeMouseX = e.clientX - rect.left;
      });
      homeWrap.addEventListener('mouseleave', function () {
        homeMouseX = -1;
        if (homeTooltip) homeTooltip.style.display = 'none';
      });
    }

    // Helper to calculate EMA arrays
    function computeEMA(candles, period, liveClose) {
      var k = 2 / (period + 1);
      var emaArr = [];
      var val = candles[0].c;
      for (var i = 0; i < candles.length; i++) {
        var closeVal = (i === candles.length - 1 && liveClose !== undefined) ? liveClose : candles[i].c;
        val = closeVal * k + val * (1 - k);
        emaArr.push(val);
      }
      return emaArr;
    }

    function drawHomeChart() {
      var w = homeWrap.clientWidth;
      var h = homeWrap.clientHeight;
      hCtx.clearRect(0, 0, w, h);

      var d = marketData[currentMarket] || marketData.nifty;
      var cndls = d.candles || [];
      if (cndls.length === 0) {
        requestAnimationFrame(drawHomeChart);
        return;
      }

      homeAnimOffset += 0.035;

      // Margins
      var padL = 16;
      var padR = 80; // right margin for Y-axis money price levels
      var padT = 24;
      var padB = 32; // bottom margin for X-axis time labels
      var plotW = Math.max(w - padL - padR, 100);
      var plotH = Math.max(h - padT - padB, 100);
      var chartBaseline = padT + plotH;

      var isLight = document.documentElement.getAttribute('data-theme') === 'light';
      var gridColor = isLight ? 'rgba(0, 0, 0, 0.05)' : 'rgba(255, 255, 255, 0.05)';
      var textAxisColor = isLight ? 'rgba(100, 116, 139, 0.85)' : 'rgba(148, 163, 184, 0.75)';

      var allL = cndls.map(function (c) { return c.l; });
      var allH = cndls.map(function (c) { return c.h; });
      var minP = Math.min.apply(null, allL);
      var maxP = Math.max.apply(null, allH);

      // Micro live tick animation on last point
      var liveSwing = (maxP - minP) * 0.003 || 0.4;
      var liveOffset = Math.sin(homeAnimOffset * 2.5) * liveSwing;
      var lastLiveClose = cndls[cndls.length - 1].c + liveOffset;

      var paddingP = (maxP - minP) * 0.12 || 1;
      minP -= paddingP;
      maxP += paddingP;
      var rngP = maxP - minP || 1;

      // 1. Horizontal Dashed Grid Lines & Right Y-Axis Price Levels
      var gridSteps = 5;
      hCtx.font = '11px "Plus Jakarta Sans", "Manrope", sans-serif';
      hCtx.fillStyle = textAxisColor;
      hCtx.textAlign = 'right';
      hCtx.textBaseline = 'middle';

      for (var gi = 0; gi <= gridSteps; gi++) {
        var gy = padT + (gi / gridSteps) * plotH;
        var gPrice = maxP - (gi / gridSteps) * (maxP - minP);

        hCtx.beginPath();
        hCtx.strokeStyle = gridColor;
        hCtx.lineWidth = 1;
        hCtx.setLineDash([3, 4]);
        hCtx.moveTo(padL, gy);
        hCtx.lineTo(padL + plotW, gy);
        hCtx.stroke();
        hCtx.setLineDash([]);

        var priceStr = gPrice >= 1000 ? gPrice.toLocaleString('en-US', { maximumFractionDigits: 0 }) : gPrice.toFixed(2);
        hCtx.fillText((d.currency || '') + priceStr, w - 8, gy);
      }

      // 2. Bottom Timeline Milestone Labels
      var xLabels = d.xLabels || [];
      if (xLabels.length > 0) {
        hCtx.fillStyle = textAxisColor;
        hCtx.font = '11px "Plus Jakarta Sans", "Manrope", sans-serif';
        hCtx.textBaseline = 'top';
        for (var xi = 0; xi < xLabels.length; xi++) {
          var xlX = padL + (xi / (xLabels.length - 1)) * plotW;
          hCtx.textAlign = (xi === 0) ? 'left' : (xi === xLabels.length - 1) ? 'right' : 'center';
          hCtx.fillText(xLabels[xi], xlX, chartBaseline + 8);
        }
      }

      // 3. Volume Histogram at Bottom (16% height)
      var maxVol = Math.max.apply(null, cndls.map(function (c) { return c.v || 30; })) || 100;
      var volMaxH = plotH * 0.16;
      var nCandles = cndls.length;
      var candleSlotW = plotW / (nCandles - 1);
      var cW = Math.max(candleSlotW * 0.68, 5);

      cndls.forEach(function (c, idx) {
        var cx = padL + idx * candleSlotW;
        var isBull = c.c >= c.o;
        var vH = ((c.v || 30) / maxVol) * volMaxH;
        var volColor = isBull
          ? (isLight ? 'rgba(0, 168, 107, 0.28)' : 'rgba(16, 216, 144, 0.32)')
          : (isLight ? 'rgba(225, 29, 72, 0.28)' : 'rgba(255, 77, 109, 0.32)');
        hCtx.fillStyle = volColor;
        hCtx.fillRect(cx - cW / 2, chartBaseline - vH, cW, vH);
      });

      // 4. Triple Multi-EMA Technical Ribbon (EMA-9, EMA-21, EMA-50)
      var ema9 = computeEMA(cndls, 9, lastLiveClose);
      var ema21 = computeEMA(cndls, 21, lastLiveClose);
      var ema50 = computeEMA(cndls, 50, lastLiveClose);

      function drawEmaLine(emaValues, strokeStyle, lineWidth) {
        hCtx.save();
        hCtx.beginPath();
        hCtx.strokeStyle = strokeStyle;
        hCtx.lineWidth = lineWidth;
        for (var i = 0; i < emaValues.length; i++) {
          var ex = padL + i * candleSlotW;
          var ey = padT + plotH - ((emaValues[i] - minP) / rngP) * plotH;
          if (i === 0) hCtx.moveTo(ex, ey);
          else hCtx.lineTo(ex, ey);
        }
        hCtx.stroke();
        hCtx.restore();
      }

      // Draw EMAs: Slow (Cyan), Medium (Amber), Fast (Gold)
      drawEmaLine(ema50, isLight ? 'rgba(2, 132, 199, 0.65)' : 'rgba(0, 210, 255, 0.6)', 1.4);
      drawEmaLine(ema21, isLight ? 'rgba(234, 88, 12, 0.75)' : 'rgba(251, 146, 60, 0.75)', 1.5);
      drawEmaLine(ema9, isLight ? 'rgba(217, 119, 6, 0.9)' : 'rgba(245, 158, 11, 0.9)', 1.6);

      // 5. Candlesticks Rendering (Authentic TradingView / Dense Style)
      var hoveredCandle = null;
      var minCDist = 999999;

      cndls.forEach(function (c, idx) {
        var isLast = (idx === cndls.length - 1);
        var curOpen = c.o;
        var curClose = isLast ? lastLiveClose : c.c;
        var curHigh = isLast ? Math.max(c.h, curClose) : c.h;
        var curLow = isLast ? Math.min(c.l, curClose) : c.l;

        var cx = padL + idx * candleSlotW;
        var isBull = curClose >= curOpen;

        var yOpen = padT + plotH - ((curOpen - minP) / rngP) * plotH;
        var yClose = padT + plotH - ((curClose - minP) / rngP) * plotH;
        var yHigh = padT + plotH - ((curHigh - minP) / rngP) * plotH;
        var yLow = padT + plotH - ((curLow - minP) / rngP) * plotH;

        var bullColor = isLight ? '#00A86B' : '#10D890';
        var bearColor = isLight ? '#E11D48' : '#FF4D6D';
        var candleColor = isBull ? bullColor : bearColor;

        // Wick line
        hCtx.save();
        hCtx.strokeStyle = candleColor;
        hCtx.lineWidth = 1.3;
        hCtx.beginPath();
        hCtx.moveTo(cx, yHigh);
        hCtx.lineTo(cx, yLow);
        hCtx.stroke();
        hCtx.restore();

        // Candle body
        var topY = Math.min(yOpen, yClose);
        var bH = Math.max(Math.abs(yOpen - yClose), 2.5);

        hCtx.save();
        hCtx.fillStyle = candleColor;
        hCtx.fillRect(cx - cW / 2, topY, cW, bH);
        hCtx.strokeStyle = isBull ? (isLight ? '#008453' : '#0DB878') : (isLight ? '#BE123C' : '#E03657');
        hCtx.lineWidth = 0.8;
        hCtx.strokeRect(cx - cW / 2, topY, cW, bH);
        hCtx.restore();

        // Check hover distance
        if (homeMouseX >= padL && homeMouseX <= padL + plotW) {
          var dist = Math.abs(cx - homeMouseX);
          if (dist < minCDist) {
            minCDist = dist;
            hoveredCandle = {
              c: c,
              idx: idx,
              isLast: isLast,
              liveClose: curClose,
              cx: cx,
              cy: (topY + bH / 2),
              yHigh: yHigh,
              yLow: yLow,
              isBull: isBull
            };
          }
        }
      });

      // 6. AI Signal Callout Marker (from Photo 3)
      if (d.signal && d.signal.idx < cndls.length) {
        var sigIdx = d.signal.idx;
        var sigCandle = cndls[sigIdx];
        var sigX = padL + sigIdx * candleSlotW;
        var sigCandleLowY = padT + plotH - ((sigCandle.l - minP) / rngP) * plotH;
        var isBuy = d.signal.type === 'BUY';
        var sigColor = isBuy ? '#F59E0B' : '#FF4D6D';

        var pinY = sigCandleLowY + 36;
        var pillW = 68;
        var pillH = 34;
        var pillX = sigX - pillW / 2;
        var pillY = pinY + 8;

        hCtx.save();
        // Stem line
        hCtx.strokeStyle = sigColor;
        hCtx.lineWidth = 1.2;
        hCtx.setLineDash([2, 2]);
        hCtx.beginPath();
        hCtx.moveTo(sigX, sigCandleLowY + 4);
        hCtx.lineTo(sigX, pillY);
        hCtx.stroke();
        hCtx.setLineDash([]);

        // Glowing Signal Beacon Pin
        hCtx.fillStyle = sigColor;
        hCtx.beginPath();
        hCtx.arc(sigX, pinY, 4, 0, Math.PI * 2);
        hCtx.fill();

        // Beacon Pulsing Ring
        var pR = 6 + Math.sin(homeAnimOffset * 3) * 2.5;
        hCtx.beginPath();
        hCtx.arc(sigX, pinY, pR, 0, Math.PI * 2);
        hCtx.strokeStyle = sigColor;
        hCtx.lineWidth = 1;
        hCtx.stroke();

        // Signal Card / Callout Bubble
        hCtx.fillStyle = isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(15, 23, 42, 0.92)';
        hCtx.beginPath();
        hCtx.roundRect ? hCtx.roundRect(pillX, pillY, pillW, pillH, 6) : hCtx.fillRect(pillX, pillY, pillW, pillH);
        hCtx.fill();
        hCtx.strokeStyle = sigColor;
        hCtx.lineWidth = 1;
        hCtx.stroke();

        // Signal Text
        hCtx.fillStyle = sigColor;
        hCtx.font = '700 9px "Plus Jakarta Sans", "Manrope", sans-serif';
        hCtx.textAlign = 'center';
        hCtx.textBaseline = 'top';
        hCtx.fillText(d.signal.label, sigX, pillY + 5);

        hCtx.fillStyle = isLight ? '#0F172A' : '#FFFFFF';
        hCtx.font = '600 9px "Plus Jakarta Sans", "Manrope", sans-serif';
        hCtx.fillText(d.signal.price, sigX, pillY + 18);
        hCtx.restore();
      }

      // 7. Live Horizontal Price Indicator Line & Glowing Pill Tag
      var yLive = padT + plotH - ((lastLiveClose - minP) / rngP) * plotH;
      var liveColor = d.isUp ? (isLight ? '#00A86B' : '#10D890') : (isLight ? '#E11D48' : '#FF4D6D');

      hCtx.save();
      hCtx.strokeStyle = liveColor;
      hCtx.lineWidth = 1;
      hCtx.setLineDash([4, 4]);
      hCtx.beginPath();
      hCtx.moveTo(padL, yLive);
      hCtx.lineTo(padL + plotW, yLive);
      hCtx.stroke();
      hCtx.setLineDash([]);
      hCtx.restore();

      // Right Live Price Pill Badge
      var livePriceStr = (d.currency || '') + (lastLiveClose >= 1000 ? lastLiveClose.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : lastLiveClose.toFixed(2));
      var badgeW = padR - 8;
      var badgeH = 20;
      var badgeX = padL + plotW + 4;
      var badgeY = yLive - badgeH / 2;

      hCtx.save();
      hCtx.fillStyle = liveColor;
      hCtx.beginPath();
      hCtx.roundRect ? hCtx.roundRect(badgeX, badgeY, badgeW, badgeH, 4) : hCtx.fillRect(badgeX, badgeY, badgeW, badgeH);
      hCtx.fill();

      hCtx.fillStyle = '#FFFFFF';
      hCtx.font = '700 10px "Plus Jakarta Sans", "Manrope", sans-serif';
      hCtx.textAlign = 'center';
      hCtx.textBaseline = 'middle';
      hCtx.fillText(livePriceStr, badgeX + badgeW / 2, badgeY + badgeH / 2);
      hCtx.restore();

      // 8. Interactive Hover Crosshairs & Floating Tooltip
      if (hoveredCandle && homeMouseX >= padL && homeMouseX <= padL + plotW && minCDist < 30) {
        // Vertical crosshair
        hCtx.save();
        hCtx.strokeStyle = isLight ? 'rgba(0, 0, 0, 0.25)' : 'rgba(255, 255, 255, 0.3)';
        hCtx.lineWidth = 1;
        hCtx.setLineDash([4, 4]);
        hCtx.beginPath();
        hCtx.moveTo(hoveredCandle.cx, padT);
        hCtx.lineTo(hoveredCandle.cx, chartBaseline);
        hCtx.stroke();

        // Horizontal crosshair
        hCtx.beginPath();
        hCtx.moveTo(padL, hoveredCandle.cy);
        hCtx.lineTo(padL + plotW, hoveredCandle.cy);
        hCtx.stroke();
        hCtx.restore();

        // Update Tooltip with full Candlestick details
        if (homeTooltip) {
          homeTooltip.style.display = 'flex';
          var homeTtPrice = qs('#homeTtPrice');
          var homeTtChange = qs('#homeTtChange');
          var homeTtTime = qs('#homeTtTime');

          var candleObj = hoveredCandle.c;
          var effectiveClose = hoveredCandle.isLast ? hoveredCandle.liveClose : candleObj.c;
          var cDiff = ((effectiveClose - candleObj.o) / candleObj.o) * 100;
          var diffStr = (cDiff >= 0 ? '+' : '') + cDiff.toFixed(2) + '%';
          var fmt = function (num) {
            return (d.currency || '') + (num >= 1000 ? num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : num.toFixed(2));
          };

          if (homeTtPrice) {
            homeTtPrice.textContent = fmt(effectiveClose);
          }
          if (homeTtChange) {
            homeTtChange.textContent = diffStr + ' (O: ' + fmt(candleObj.o) + '  H: ' + fmt(candleObj.h) + '  L: ' + fmt(candleObj.l) + ')';
            homeTtChange.className = 'tt-change ' + (cDiff >= 0 ? 'up' : 'down');
          }
          if (homeTtTime) {
            homeTtTime.textContent = (candleObj.t ? (candleObj.t + ' · ') : '') + (candleObj.v ? (candleObj.v + 'K Vol') : 'Session');
          }
        }
      }

      requestAnimationFrame(drawHomeChart);
    }
    requestAnimationFrame(drawHomeChart);

    // Tab buttons
    qsa('.hct-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.hct-btn').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        currentMarket = btn.getAttribute('data-market');
        var d = marketData[currentMarket];
        var name = qs('#homeChartName');
        var price = qs('#homeChartPrice');
        var change = qs('#homeChartChange');
        var csOpen = qs('#csOpen');
        var csHigh = qs('#csHigh');
        var csLow = qs('#csLow');
        var csPrev = qs('#csPrev');
        var cs52High = qs('#cs52High');
        var cs52Low = qs('#cs52Low');
        if (name) name.textContent = d.name;
        if (price) price.textContent = d.price;
        if (change) {
          change.textContent = d.change;
          change.className = 'hci-change ' + (d.isUp ? 'up' : 'down');
        }
        if (csOpen) csOpen.textContent = d.open;
        if (csHigh) csHigh.textContent = d.high;
        if (csLow) csLow.textContent = d.low;
        if (csPrev) csPrev.textContent = d.prev;
        if (cs52High && d.h52) cs52High.textContent = d.h52;
        if (cs52Low && d.l52) cs52Low.textContent = d.l52;
      });
    });
  }

  /* =============================================================
     RISK DONUT CHART
     ============================================================= */
  var donutCanvas = qs('#riskDonutChart');
  if (donutCanvas) {
    var dCtx = donutCanvas.getContext('2d');
    var donutW = donutCanvas.width;
    var donutH = donutCanvas.height;
    var donutCx = donutW / 2, donutCy = donutH / 2;
    var donutR = Math.min(donutW, donutH) * 0.44;
    var donutInner = donutR * 0.58;
    var donutAngle = 0;

    var segments = [
      { pct: 0.35, color: '#10D890', label: 'Low' },
      { pct: 0.40, color: '#F59E0B', label: 'Medium' },
      { pct: 0.25, color: '#FF4D6D', label: 'High' }
    ];

    function drawDonut() {
      dCtx.clearRect(0, 0, donutW, donutH);
      donutAngle += 0.008;

      var isLight = document.documentElement.getAttribute('data-theme') === 'light';
      var segColors = [
        isLight ? '#00A86B' : '#10D890',
        isLight ? '#EA580C' : '#F59E0B',
        isLight ? '#E11D48' : '#FF4D6D'
      ];

      var start = -Math.PI / 2 + Math.sin(donutAngle * 0.3) * 0.06;
      segments.forEach(function (seg, sIdx) {
        var end = start + seg.pct * Math.PI * 2;

        dCtx.beginPath();
        dCtx.arc(donutCx, donutCy, donutR, start, end);
        dCtx.arc(donutCx, donutCy, donutInner, end, start, true);
        dCtx.closePath();
        dCtx.fillStyle = segColors[sIdx] || seg.color;
        dCtx.fill();

        start = end;
      });

      // Center text - theme responsive
      dCtx.fillStyle = isLight ? '#0A0F1D' : '#F8FAFC';
      dCtx.font = 'bold 20px "Plus Jakarta Sans", sans-serif';
      dCtx.textAlign = 'center';
      dCtx.textBaseline = 'middle';
      dCtx.fillText('Risk', donutCx, donutCy - 10);
      dCtx.font = '12px "Plus Jakarta Sans", "Manrope", sans-serif';
      dCtx.fillStyle = isLight ? '#64748B' : '#94A3B8';
      dCtx.fillText('Profile', donutCx, donutCy + 12);

      requestAnimationFrame(drawDonut);
    }
    requestAnimationFrame(drawDonut);
  }

  /* =============================================================
     ASSET CARD FILTER (watchlist)
     ============================================================= */
  qsa('.vw-filter-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      qsa('.vw-filter-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var cat = btn.getAttribute('data-category');
      qsa('.vw-asset-card').forEach(function (card) {
        if (cat === 'all' || card.getAttribute('data-category') === cat) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  /* =============================================================
     NEWSLETTER FORM
     ============================================================= */
  var newsletterForm = qs('#vwNewsletterForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = qs('#vwNewsletterNote');
      if (note) note.classList.add('visible');
    });
  }

  /* =============================================================
     LIVE QUOTE POLLING
     ============================================================= */
  var assetCards = qsa('.vw-asset-card[data-symbol]');
  if (assetCards.length > 0) {
    var symbols = Array.from(assetCards).map(function (c) { return c.getAttribute('data-symbol'); }).filter(Boolean);

    function refreshQuotes() {
      if (!symbols.length) return;
      fetch('/api/live-quotes?tickers=' + symbols.join(','))
        .then(function (r) { return r.json(); })
        .then(function (data) {
          assetCards.forEach(function (card) {
            var sym = card.getAttribute('data-symbol');
            if (!data[sym]) return;
            var q = data[sym];
            var priceEl = card.querySelector('.live-price-value');
            var changeEl = card.querySelector('.live-change-value');
            var arrowEl = card.querySelector('.live-arrow');
            var changeWrap = card.querySelector('.vw-asset-change');
            if (priceEl) priceEl.textContent = q.price.toLocaleString();
            if (changeEl) changeEl.textContent = q.change.toFixed(2);
            if (arrowEl) arrowEl.textContent = q.change >= 0 ? '▲' : '▼';
            if (changeWrap) {
              changeWrap.className = 'vw-asset-change ' + (q.change >= 0 ? 'up' : 'down');
            }
            card.setAttribute('data-price', q.price);
            card.setAttribute('data-change', q.change);
            card.classList.add('live-flash');
            setTimeout(function () { card.classList.remove('live-flash'); }, 700);
          });
        })
        .catch(function () {});
    }

    refreshQuotes();
    setInterval(refreshQuotes, 30000);
  }

  /* =============================================================
     BIG FORMAT ASSET CHART MODAL CONTROLLER
     ============================================================= */
  var modalEl = qs('#assetChartModal');
  var modalBackdrop = qs('#assetModalBackdrop');
  var modalCloseBtn = qs('#modalAssetClose');
  var modalCanvasWrap = qs('#modalCanvasWrap');
  var modalCanvas = qs('#modalBigCanvas');
  var modalTooltip = qs('#modalChartTooltip');
  var modalLoading = qs('#modalChartLoading');

  var currentModalAsset = null;
  var currentModalTf = '1D';
  var modalChartData = null;
  var modalMouseX = -1;
  var modalMouseY = -1;

  if (modalEl && modalCanvas && modalCanvasWrap) {
    var mCtx = modalCanvas.getContext('2d');

    function resizeModalCanvas() {
      if (!modalEl.classList.contains('active')) return;
      var dpr = window.devicePixelRatio || 1;
      var rect = modalCanvasWrap.getBoundingClientRect();
      modalCanvas.width = rect.width * dpr;
      modalCanvas.height = rect.height * dpr;
      mCtx.setTransform(1, 0, 0, 1, 0, 0);
      mCtx.scale(dpr, dpr);
      renderModalChart();
    }
    window.addEventListener('resize', resizeModalCanvas);

    modalCanvasWrap.addEventListener('mousemove', function (e) {
      var rect = modalCanvasWrap.getBoundingClientRect();
      modalMouseX = e.clientX - rect.left;
      modalMouseY = e.clientY - rect.top;
      renderModalChart();
    });

    modalCanvasWrap.addEventListener('mouseleave', function () {
      modalMouseX = -1;
      modalMouseY = -1;
      if (modalTooltip) modalTooltip.style.display = 'none';
      renderModalChart();
    });

    function formatNumber(num) {
      if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
      if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
      if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
      return num.toLocaleString();
    }

    function openAssetModal(card) {
      var sym = card.getAttribute('data-symbol') || '';
      var ticker = card.getAttribute('data-ticker') || sym;
      var name = card.getAttribute('data-name') || ticker;
      var exchange = card.getAttribute('data-exchange') || 'US';
      var category = card.getAttribute('data-category') || 'stocks';
      var currency = card.getAttribute('data-currency') || '₹';
      var price = parseFloat(card.getAttribute('data-price')) || 0;
      var change = parseFloat(card.getAttribute('data-change')) || 0;
      var spark = card.getAttribute('data-spark') || '';

      currentModalAsset = {
        symbol: sym,
        ticker: ticker,
        name: name,
        exchange: exchange,
        category: category,
        currency: currency,
        price: price,
        change: change,
        spark: spark
      };

      currentModalTf = '1D';

      // Update header elements
      var elSym = qs('#modalAssetSymbol');
      var elEx = qs('#modalAssetExchange');
      var elCat = qs('#modalAssetCategory');
      var elName = qs('#modalAssetName');
      var elPrice = qs('#modalAssetPrice');
      var elChange = qs('#modalAssetChange');
      var reportBtn = qs('#modalViewReportBtn');

      if (elSym) elSym.textContent = ticker;
      if (elEx) elEx.textContent = exchange;
      if (elCat) elCat.textContent = category;
      if (elName) elName.textContent = name;
      if (elPrice) elPrice.textContent = currency + (price >= 1000 ? price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : price.toFixed(2));
      if (elChange) {
        var isUp = change >= 0;
        elChange.className = 'amh-change ' + (isUp ? 'up' : 'down');
        var changeNumEl = elChange.querySelector('.amh-change-num');
        var arrowEl = elChange.querySelector('.amh-arrow');
        if (arrowEl) arrowEl.textContent = isUp ? '▲' : '▼';
        if (changeNumEl) changeNumEl.textContent = (isUp ? '+' : '') + change.toFixed(2) + '%';
      }
      if (reportBtn) {
        reportBtn.href = '/reports?ticker=' + encodeURIComponent(sym);
      }

      // Reset timeframes active state
      qsa('#modalTimeframes .amc-tf-btn').forEach(function (btn) {
        if (btn.getAttribute('data-tf') === '1D') {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });

      // Quick baseline chart from sparkline or base price for instant feel
      generateInitialChartData(currentModalAsset);

      // Show modal
      modalEl.classList.add('active');
      modalEl.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';

      // Resize & render
      setTimeout(function () {
        resizeModalCanvas();
        fetchModalData(sym, currentModalTf);
      }, 50);
    }

    function closeAssetModal() {
      modalEl.classList.remove('active');
      modalEl.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      currentModalAsset = null;
      modalChartData = null;
    }

    if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeAssetModal);
    if (modalBackdrop) modalBackdrop.addEventListener('click', closeAssetModal);

    window.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modalEl.classList.contains('active')) {
        closeAssetModal();
      }
    });

    // Timeframe selector buttons
    qsa('#modalTimeframes .amc-tf-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('#modalTimeframes .amc-tf-btn').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        currentModalTf = btn.getAttribute('data-tf');
        if (currentModalAsset) {
          fetchModalData(currentModalAsset.symbol, currentModalTf);
        }
      });
    });

    // Click on cards opens modal (except clicking report links)
    document.addEventListener('click', function (e) {
      var link = e.target.closest('a');
      if (link) return;

      var chartBtn = e.target.closest('.btn-open-chart');
      var card = e.target.closest('.vw-asset-card');

      if (chartBtn) {
        e.preventDefault();
        e.stopPropagation();
        var parentCard = chartBtn.closest('.vw-asset-card');
        if (parentCard) openAssetModal(parentCard);
        return;
      }

      if (card) {
        e.preventDefault();
        openAssetModal(card);
      }
    });

    function generateInitialChartData(asset) {
      var pts = [];
      var base = asset.price || 100;
      var pointsCount = 40;
      var cur = base * (1 - (asset.change / 100) * 0.8);
      var drift = ((base - cur) / pointsCount);

      for (var i = 0; i < pointsCount; i++) {
        cur += drift + (Math.sin(i * 0.6) * base * 0.003) + ((Math.random() - 0.48) * base * 0.004);
        var hr = 9 + Math.floor((i * 6.5) / 60);
        var mn = Math.floor((i * 6.5) % 60);
        pts.push({
          time: String(hr).padStart(2, '0') + ':' + String(mn).padStart(2, '0'),
          price: Math.max(cur, 0.01),
          open: cur * 0.998,
          high: cur * 1.002,
          low: cur * 0.997,
          volume: Math.floor(12000 + Math.random() * 45000)
        });
      }
      pts[pts.length - 1].price = base;

      modalChartData = {
        points: pts,
        currency: asset.currency,
        isUp: asset.change >= 0,
        open: pts[0].price,
        high: Math.max.apply(null, pts.map(function (p) { return p.price; })),
        low: Math.min.apply(null, pts.map(function (p) { return p.price; })),
        volume: pts.reduce(function (a, b) { return a + b.volume; }, 0)
      };
      updateModalStats(modalChartData);
    }

    function updateModalStats(data) {
      var elOpen = qs('#modalStatOpen');
      var elHigh = qs('#modalStatHigh');
      var elLow = qs('#modalStatLow');
      var elVol = qs('#modalStatVolume');
      var c = currentModalAsset ? currentModalAsset.currency : '';

      if (elOpen) elOpen.textContent = c + (data.open ? (data.open >= 1000 ? data.open.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : data.open.toFixed(2)) : '—');
      if (elHigh) elHigh.textContent = c + (data.high ? (data.high >= 1000 ? data.high.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : data.high.toFixed(2)) : '—');
      if (elLow) elLow.textContent = c + (data.low ? (data.low >= 1000 ? data.low.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : data.low.toFixed(2)) : '—');
      if (elVol) elVol.textContent = data.volume ? formatNumber(data.volume) : '—';
    }

    function fetchModalData(symbol, tf) {
      if (!symbol) return;
      if (modalLoading) modalLoading.style.display = 'flex';

      fetch('/api/asset-chart?ticker=' + encodeURIComponent(symbol) + '&tf=' + encodeURIComponent(tf))
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (modalLoading) modalLoading.style.display = 'none';
          if (res && res.points && res.points.length > 1) {
            var firstP = res.points[0].price;
            var lastP = res.points[res.points.length - 1].price;
            var isUp = lastP >= firstP;

            modalChartData = {
              points: res.points,
              currency: currentModalAsset.currency,
              isUp: isUp,
              open: res.open || firstP,
              high: res.high || Math.max.apply(null, res.points.map(function (p) { return p.price; })),
              low: res.low || Math.min.apply(null, res.points.map(function (p) { return p.price; })),
              volume: res.volume || 0,
              changePct: res.change_pct
            };

            // Update header price & change
            var elPrice = qs('#modalAssetPrice');
            var elChange = qs('#modalAssetChange');
            if (elPrice && res.current_price) {
              elPrice.textContent = currentModalAsset.currency + (res.current_price >= 1000 ? res.current_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : res.current_price.toFixed(2));
            }
            if (elChange && res.change_pct !== undefined) {
              elChange.className = 'amh-change ' + (isUp ? 'up' : 'down');
              var changeNumEl = elChange.querySelector('.amh-change-num');
              var arrowEl = elChange.querySelector('.amh-arrow');
              if (arrowEl) arrowEl.textContent = isUp ? '▲' : '▼';
              if (changeNumEl) changeNumEl.textContent = (isUp ? '+' : '') + res.change_pct.toFixed(2) + '%';
            }

            updateModalStats(modalChartData);
            renderModalChart();
          }
        })
        .catch(function () {
          if (modalLoading) modalLoading.style.display = 'none';
        });
    }

    function renderModalChart() {
      if (!modalEl.classList.contains('active') || !modalChartData) return;

      var w = modalCanvasWrap.clientWidth;
      var h = modalCanvasWrap.clientHeight;
      mCtx.clearRect(0, 0, w, h);

      var pts = modalChartData.points;
      if (!pts || pts.length < 2) return;

      var isLight = document.documentElement.getAttribute('data-theme') === 'light';
      var gridColor = isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.05)';
      var textAxisColor = isLight ? '#64748B' : '#94A3B8';

      var padL = 16;
      var padR = 74; // Room for price tags on right
      var padT = 20;
      var padB = 30; // Room for time tags on bottom
      var plotW = Math.max(w - padL - padR, 100);
      var plotH = Math.max(h - padT - padB, 80);
      var baseline = padT + plotH;

      var prices = pts.map(function (p) { return p.price; });
      var minP = Math.min.apply(null, prices);
      var maxP = Math.max.apply(null, prices);
      var padRange = (maxP - minP) * 0.12 || 1;
      minP -= padRange;
      maxP += padRange;
      var rngP = maxP - minP || 1;

      // 1. Horizontal Dashed Grid Lines & Right Y-Axis Price Labels
      var gridSteps = 4;
      mCtx.font = '11px "Plus Jakarta Sans", "Manrope", sans-serif';
      mCtx.fillStyle = textAxisColor;
      mCtx.textAlign = 'right';
      mCtx.textBaseline = 'middle';

      for (var gi = 0; gi <= gridSteps; gi++) {
        var gy = padT + (gi / gridSteps) * plotH;
        var gPrice = maxP - (gi / gridSteps) * (maxP - minP);

        mCtx.beginPath();
        mCtx.strokeStyle = gridColor;
        mCtx.lineWidth = 1;
        mCtx.setLineDash([3, 4]);
        mCtx.moveTo(padL, gy);
        mCtx.lineTo(padL + plotW, gy);
        mCtx.stroke();
        mCtx.setLineDash([]);

        var pStr = gPrice >= 1000 ? gPrice.toLocaleString('en-US', { maximumFractionDigits: 2 }) : gPrice.toFixed(2);
        mCtx.fillText((modalChartData.currency || '') + pStr, w - 8, gy);
      }

      // 2. Bottom Timeline Labels (X-Axis)
      var stepX = Math.max(Math.floor((pts.length - 1) / 4), 1);
      mCtx.fillStyle = textAxisColor;
      mCtx.font = '10px "Plus Jakarta Sans", "Manrope", sans-serif';
      mCtx.textBaseline = 'top';

      for (var xi = 0; xi < pts.length; xi += stepX) {
        var xlX = padL + (xi / (pts.length - 1)) * plotW;
        mCtx.textAlign = (xi === 0) ? 'left' : (xi >= pts.length - stepX) ? 'right' : 'center';
        mCtx.fillText(pts[xi].time || '', xlX, baseline + 8);
      }

      // Coordinates mapping
      var coords = pts.map(function (p, i) {
        return {
          x: padL + (i / (pts.length - 1)) * plotW,
          y: padT + plotH - ((p.price - minP) / rngP) * plotH,
          val: p.price,
          time: p.time,
          idx: i
        };
      });

      var isUp = modalChartData.isUp;
      var lineColor = isUp ? (isLight ? '#00A86B' : '#10D890') : (isLight ? '#E11D48' : '#FF4D6D');
      var areaColor1 = isUp ? (isLight ? 'rgba(0, 168, 107, 0.25)' : 'rgba(16, 216, 144, 0.28)') : (isLight ? 'rgba(225, 29, 72, 0.25)' : 'rgba(255, 77, 109, 0.28)');
      var areaColor2 = isUp ? (isLight ? 'rgba(0, 168, 107, 0.02)' : 'rgba(16, 216, 144, 0.01)') : (isLight ? 'rgba(225, 29, 72, 0.02)' : 'rgba(255, 77, 109, 0.01)');

      // Area Fill
      mCtx.beginPath();
      mCtx.moveTo(coords[0].x, baseline);
      mCtx.lineTo(coords[0].x, coords[0].y);
      buildSplinePath(mCtx, coords);
      mCtx.lineTo(coords[coords.length - 1].x, baseline);
      mCtx.closePath();

      var areaGrad = mCtx.createLinearGradient(0, padT, 0, baseline);
      areaGrad.addColorStop(0, areaColor1);
      areaGrad.addColorStop(0.75, areaColor2);
      areaGrad.addColorStop(1, isLight ? 'rgba(255, 255, 255, 0)' : 'rgba(8, 11, 16, 0)');
      mCtx.fillStyle = areaGrad;
      mCtx.fill();

      // Stroke Line
      mCtx.save();
      mCtx.beginPath();
      buildSplinePath(mCtx, coords);
      mCtx.shadowColor = lineColor;
      mCtx.shadowBlur = isLight ? 4 : 8;
      mCtx.strokeStyle = lineColor;
      mCtx.lineWidth = 2.4;
      mCtx.stroke();
      mCtx.restore();

      // Pulsing End Beacon Dot
      var lastPt = coords[coords.length - 1];
      mCtx.beginPath();
      mCtx.arc(lastPt.x, lastPt.y, 4.5, 0, Math.PI * 2);
      mCtx.fillStyle = lineColor;
      mCtx.fill();

      mCtx.beginPath();
      mCtx.arc(lastPt.x, lastPt.y, 8, 0, Math.PI * 2);
      mCtx.strokeStyle = lineColor;
      mCtx.lineWidth = 1.2;
      mCtx.stroke();

      // Interactive Crosshairs & Tooltip
      if (modalMouseX >= padL && modalMouseX <= padL + plotW) {
        var closest = coords[0];
        var minDist = Math.abs(coords[0].x - modalMouseX);
        for (var k = 1; k < coords.length; k++) {
          var dist = Math.abs(coords[k].x - modalMouseX);
          if (dist < minDist) { minDist = dist; closest = coords[k]; }
        }

        // Vertical crosshair
        mCtx.save();
        mCtx.strokeStyle = isLight ? 'rgba(0, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.24)';
        mCtx.lineWidth = 1;
        mCtx.setLineDash([4, 4]);
        mCtx.beginPath();
        mCtx.moveTo(closest.x, padT);
        mCtx.lineTo(closest.x, baseline);
        mCtx.stroke();

        // Horizontal crosshair
        mCtx.beginPath();
        mCtx.moveTo(padL, closest.y);
        mCtx.lineTo(padL + plotW, closest.y);
        mCtx.stroke();
        mCtx.restore();

        // Hover dot on curve
        mCtx.beginPath();
        mCtx.arc(closest.x, closest.y, 6, 0, Math.PI * 2);
        mCtx.fillStyle = isLight ? '#0F172A' : '#FFFFFF';
        mCtx.shadowColor = lineColor;
        mCtx.shadowBlur = 10;
        mCtx.fill();
        mCtx.shadowBlur = 0;

        // Floating Y-axis Badge
        var badgePriceStr = (modalChartData.currency || '') + (closest.val >= 1000 ? closest.val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : closest.val.toFixed(2));
        mCtx.fillStyle = isLight ? '#FFFFFF' : '#0B0F17';
        mCtx.fillRect(padL + plotW + 2, closest.y - 10, padR - 6, 20);
        mCtx.strokeStyle = lineColor;
        mCtx.lineWidth = 1.2;
        mCtx.strokeRect(padL + plotW + 2, closest.y - 10, padR - 6, 20);
        mCtx.fillStyle = isLight ? '#0F172A' : '#FFFFFF';
        mCtx.font = '700 11px "Plus Jakarta Sans", "Manrope", sans-serif';
        mCtx.textAlign = 'center';
        mCtx.textBaseline = 'middle';
        mCtx.fillText(badgePriceStr, padL + plotW + (padR - 4) / 2, closest.y);

        // Update Tooltip HUD
        if (modalTooltip) {
          modalTooltip.style.display = 'flex';
          var ttPrice = qs('#modalTooltipPrice');
          var ttChange = qs('#modalTooltipChange');
          var ttTime = qs('#modalTooltipTime');
          var startP = coords[0].val;
          var diffPct = ((closest.val - startP) / startP) * 100;

          if (ttPrice) ttPrice.textContent = badgePriceStr;
          if (ttChange) {
            ttChange.textContent = (diffPct >= 0 ? '+' : '') + diffPct.toFixed(2) + '%';
            ttChange.className = 'amt-change ' + (diffPct >= 0 ? 'up' : 'down');
          }
          if (ttTime) {
            ttTime.textContent = closest.time || ('Point ' + (closest.idx + 1));
          }
        }
      }
    }
  }

})();
