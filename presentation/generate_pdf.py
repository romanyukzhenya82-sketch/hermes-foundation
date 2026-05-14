"""
Hermes Foundation -- Pitch Deck PDF Generator (Multilingual)
Generates 14-slide dark-theme investor presentation in EN, CS, UA.
Usage: python generate_pdf.py
Output: hermes_en.pdf, hermes_cs.pdf, hermes_ua.pdf
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

W, H = 297, 167.0625

BG       = (3,   7,  18)
SURFACE  = (13,  17,  23)
SURFACE2 = (22,  27,  39)
CYAN     = (0,  245, 255)
PURPLE   = (180, 79, 255)
GOLD     = (255, 215,  0)
GREEN    = (0,  255, 136)
RED      = (255, 68,  102)
WHITE    = (255, 255, 255)
TEXT     = (226, 232, 240)
MUTED    = (100, 116, 139)
MUTED2   = (55,  65,  81)
ORANGE   = (255, 107,  53)

# =============================================================================
# LANGUAGE DATA
# =============================================================================

LANG = {

# ─────────────────────────────────────────────────────────────────────────────
'en': {
    's1_tag':   'CONFIDENTIAL INVESTOR BRIEFING -- MAY 2026',
    's1_title': 'HERMES FOUNDATION',
    's1_sub1':  'Institutional-grade crypto signal intelligence.',
    's1_sub2':  'AI-powered multi-agent scanning across 200+ live markets -- every hour, 24/7.',
    's1_badges':       ['6 Specialized Agents','Real-Time Market Scan','Built-in Risk Management','Live as of May 2026'],
    's1_badge_colors': [CYAN, CYAN, PURPLE, GOLD],

    's2_tag': 'The Problem',
    's2_h1':  'The market never sleeps.',
    's2_h2':  'Humans do.',
    's2_problems': [
        '90% of retail crypto traders lose money over 12 months',
        'Emotional decisions destroy edge at critical market moments',
        'Manual scanning of 200+ pairs in real time is humanly impossible',
        'Regime blind spots -- trading into flat markets kills expectancy',
        'No systematic risk sizing -- position sizes driven by gut, not math',
    ],
    's2_stats': [
        ('90%',   'of retail traders underperform',  RED),
        ('200+',  'USDT pairs on Binance Futures',   GOLD),
        ('$2.4T', 'total crypto market cap',         CYAN),
    ],

    's3_tag': 'The Solution',
    's3_h1':  'Meet ',
    's3_h2':  'Hermes',
    's3_points': [
        ('Runs every hour, 24/7',      'Zero human attention required'),
        ('Macro-regime aware',          'Skips flat / chaotic conditions automatically'),
        ('20+ factor scoring engine',  'Ranks every pair before agents see it'),
        ('Built-in position sizer',    'size = risk / |entry - stop|, always'),
        ('Self-logging signals',        'Every signal recorded and graded post-factum'),
        ('Provable edge',              'Backtest -> live validation -> improvement loop'),
    ],
    's3_metrics': [
        ('<10s', 'Full 200-pair scan',   CYAN),
        ('24/7', 'Autonomous operation', GREEN),
        ('6',    'Specialized agents',   GOLD),
        ('3x',   'Exchanges monitored',  PURPLE),
    ],
    's3_callout_h':    'SYSTEM IN ONE SENTENCE',
    's3_callout_body': (
        'Hermes watches 200+ markets simultaneously, detects setups '
        'meeting strict multi-factor criteria, and delivers ready-to-execute '
        'signals with mathematically sized risk - while you sleep.'
    ),

    's4_tag': 'Core Architecture',
    's4_h1':  'Six Specialized ',
    's4_h2':  'Intelligence Agents',
    's4_agents': [
        ('Long Agent',     'FUTURES LONG',
         'Bullish breakout setups. Requires vol spike >= 2x, '
         'strong OI growth, positive trend alignment, score >= 80.'),
        ('Short Agent',    'FUTURES SHORT',
         'Bearish reversal setups. Hunts funding flip, OI divergence, '
         'and momentum exhaustion signals on Binance Futures.'),
        ('Spot Agent',     'SPOT LONG',
         'Accumulation zones with stop anchored to 1H support rather '
         'than fixed percentage, reducing noise exits.'),
        ('Arb Agent',      'CROSS-EXCHANGE ARB',
         'Price gaps across Binance, Bybit, and MEXC Futures. '
         'Surfaces windows with positive slippage-adjusted profit.'),
        ('Options Agent',  'DERIVATIVES ALERTS',
         'BTC / ETH only. Triggers on extreme funding or 4H moves >8%. '
         'Outputs implied-move alerts for Deribit positioning.'),
        ('Moonshot Agent', 'MICRO-CAP SPECULATIVE',
         'Sub-$5 micro-caps with 3x+ volume spikes. '
         'TP1=2x, TP2=4x. High-risk asymmetric bets with 24-48h lookahead.'),
    ],
    's4_agent_colors': [GREEN, RED, CYAN, GOLD, PURPLE, ORANGE],

    's5_tag': 'Signal Generation Pipeline',
    's5_h1':  'From Raw Data to ',
    's5_h2':  'Actionable Signal',
    's5_steps': [
        ('01', 'Universe Scan',
         'Fetch all active USDT pairs\nfrom Binance Futures. Filter:\nregex, OI > $10M, vol > $50M.'),
        ('02', 'Parallel Scoring',
         '8-thread pool builds 20+\nfactor score per pair.\nScan completes in <10 seconds.'),
        ('03', 'Macro Context',
         'BTC + ETH + 20 pairs =>\nregime: Trend / Flat / Chaos.\nAdjusts or blocks agents.'),
        ('04', 'Agent Filters',
         'Each of 6 agents applies\nspecialized criteria. Only\ntop pairs are promoted.'),
        ('05', 'Signal Output',
         'Entry, stop, TP1, TP2,\nR/R ratio, leverage cap,\nposition size -- all pre-calc.'),
    ],
    's5_bstats': [
        ('200+', 'Pairs scanned',  CYAN),
        ('<10s',  'Scan duration', GREEN),
        ('1h',   'Recurrence',     GOLD),
        ('3',    'Exchanges',      PURPLE),
    ],

    's6_tag': 'Proprietary Signal Intelligence',
    's6_h1':  '20+ Factor ',
    's6_h2':  'Scoring Engine',
    's6_factors': [
        ('OI Growth (1h)',   '+30', 1.00),
        ('Volume Spike',     '+25', 0.83),
        ('ATR Momentum',     '+20', 0.67),
        ('Trend Alignment',  '+20', 0.67),
        ('Funding Rate',     '+15', 0.50),
        ('Liq. Proximity',   '+15', 0.50),
        ('Breakout Pattern', '+12', 0.40),
        ('BTC Correlation',  '+10', 0.33),
        ('Support/Resist',   '+10', 0.33),
        ('Macro Regime',     '+10', 0.33),
        ('Category Bonus',   '+8',  0.27),
        ('Spread Penalty',   '-5',  0.17),
    ],
    's6_thresh': [
        ('Min score for Long/Short agent', '>= 80', GREEN),
        ('Top pairs passed to agents',     'Top 80', CYAN),
        ('Avg signals per hourly scan',    '2 - 8',  GOLD),
    ],

    's7_tag':  'Project Status',
    's7_h1':   "What's ",
    's7_h2':   'Already Built',
    's7_h3':   ' -- Right Now',
    's7_done': 'DONE',
    's7_wip':  'WIP',
    's7_items_l': [
        (True,  'All 6 agents -- production-ready',
                'LongAgent, ShortAgent, SpotAgent, ArbAgent, OptionsAgent, MoonshotAgent'),
        (True,  'Parallel market scanner',
                'ThreadPoolExecutor x8 -- full scan in <10 seconds'),
        (True,  'Signal logging system',
                'signals_log.jsonl -- every signal timestamped and stored'),
        (True,  'Backtest framework',
                '30-day historical simulation with WR / expectancy / profit factor'),
        (True,  'Signal evaluation engine',
                'Post-factum HIT_TP1 / HIT_TP2 / HIT_SL outcome grading'),
        (True,  'Position sizer',
                'Fractional Kelly, ATR-based stop, leverage cap enforcement'),
    ],
    's7_items_r': [
        (True,  'Multi-exchange price feeds',
                'Binance fapi + Bybit Linear + MEXC Futures -- all verified'),
        (True,  'Configuration system',
                'config.yaml + dataclass loader -- zero hardcoded parameters'),
        (True,  'Automated hourly execution',
                'Windows Task Scheduler -- runs every hour, logs to /logs/'),
        (True,  '13 automated tests -- all passing',
                'Scanner, config, signals log, position sizing, slippage'),
        (False, 'Live validation -- in progress',
                'Collecting 50+ closed signals for statistical gate check'),
        (False, 'Health monitoring + Telegram alerts',
                'health_check.py -- scheduled for Phase 5'),
    ],

    's8_tag': 'Performance Targets & Gate Criteria',
    's8_h1':  "We Don't Ship Until the ",
    's8_h2':  'Numbers Prove It',
    's8_metrics': [
        ('>52%',  'Target Winrate',   'Long + Short combined, >= 50 signals', GREEN),
        ('>0 R',  'Expectancy',       'Positive expected value per trade',    CYAN),
        ('<20%',  'Max Sim Drawdown', 'Simulated risk over 10-day window',    GOLD),
        ('<10s',  'Scan Latency',     'Full 200-pair universe, parallel',     PURPLE),
    ],
    's8_gate_h': 'RELEASE GATE -- ALL CRITERIA MUST PASS TO SHIP v1.0',
    's8_gates': [
        'Winrate >= 52% across 50+ closed signals',
        'Expectancy > 0 for each agent type',
        'Max sim drawdown <= 20%',
        '15+ automated tests, zero failures',
        'Scan latency < 10 sec, 24/7 uptime proven',
        'health_check + Telegram monitoring live',
        'signals_log running 10+ days without gaps',
        'README + ARCHITECTURE docs current',
    ],
    's8_check':        'CHECK',
    's8_phase_label':  'Live Validation',
    's8_phase_status': '>>> RUNNING NOW <<<',

    's9_tag': 'Execution Roadmap',
    's9_h1':  '30 Days to ',
    's9_h2':  'v1.0 Release',
    's9_phases': [
        ('Days 1-4',   'Phase 1 -- Validation Foundation',
         'Backtest framework, signal logging, evaluate engine',           GREEN,  True),
        ('Days 5-7',   'Phase 2 -- Architecture & Performance',
         'Parallel scan (x8), config system, 13 tests passing',          GREEN,  True),
        ('Days 8-17',  'Phase 3 -- Live Validation',
         '50+ signals, gate check day 10: WR >= 52%, expectancy > 0',   CYAN,   False),
        ('Days 18-22', 'Phase 4 -- Moonshot & Options MVP',
         'Revised TP targets, Deribit integration, ArbAgent live test',  PURPLE, False),
        ('Days 23-28', 'Phase 5 -- Production Hardening',
         'Health monitor, Telegram alerts, log rotation, >= 15 tests',   PURPLE, False),
        ('Days 28-30', 'Phase 6 -- v1.0 Release Gate',
         'All 8 criteria must pass. CHANGELOG v1.0. Go/No-Go decision.', GOLD,   False),
    ],
    's9_complete':    'COMPLETE',
    's9_in_progress': 'IN PROGRESS',
    's9_upcoming':    'UPCOMING',
    's9_summary': [
        ('~4 Weeks', 'To v1.0 from today',    CYAN),
        ('2 / 6',    'Phases complete',        GREEN),
        ('Day 10',   'First go/no-go gate',    GOLD),
        ('Zero',     'External deps to ship',  PURPLE),
    ],

    's10_tag': 'Deployment Checklist',
    's10_h1':  'What Stands Between Us and ',
    's10_h2':  'Production',
    's10_blocks': [
        (CYAN,   '1', 'Live Validation Proof',    '10 days - Currently running',
         ['Collect >= 50 closed signals (TP/SL hit)',
          'Winrate >= 52% Long + Short combined',
          'Expectancy > 0 per direction',
          'Max drawdown <= 20% on simulated risk',
          'Day-3 and day-7 interim reviews']),
        (PURPLE, '2', 'Production Hardening',     '5 days - Phase 5',
         ['health_check.py -- scan latency monitor',
          'Telegram webhook alerts on failures',
          'Log rotation (100MB / weekly)',
          'Expand test coverage to 15+ tests',
          'CryptoPanic news feed integration']),
        (GOLD,   '3', 'Moonshot & Options Tuning','5 days - Phase 4',
         ['MoonshotAgent: TP1=2x, TP2=4x',
          'Lookahead sweep: 24h vs 48h optimal',
          'OptionsAgent: Deribit implied vol feed',
          'ArbAgent: 5-day live profit validation',
          'backtest_moonshot.py sweep results']),
    ],
    's10_callout_h':    'BOTTOM LINE FOR INVESTORS',
    's10_callout_body': (
        'The engine is already running. The remaining work is validation '
        'and hardening -- not building. We are not pre-product. We are pre-release.'
    ),

    's11_tag':     'Competitive Positioning',
    's11_h1':      'Why ',
    's11_h2':      'Hermes',
    's11_h3':      ' Wins',
    's11_headers': ['Capability', 'HERMES', 'Signal Channels', 'TradingView', 'Off-shelf Bots'],
    's11_rows': [
        ('Scans 200+ pairs simultaneously',      True,  False, 'Partial',  'Partial'),
        ('Macro regime awareness',               True,  False, False,      False),
        ('Mathematical position sizing',         True,  False, False,      'Partial'),
        ('Self-grading signal log',              True,  False, False,      False),
        ('Cross-exchange arbitrage',             True,  False, False,      'Rare'),
        ('Provable edge (backtest + live)',       True,  False, False,      False),
        ('Fully configurable & extensible',      True,  False, 'Limited',  'Some'),
    ],
    's11_yes': 'YES',
    's11_no':  'NO',

    's12_tag': 'Risk Management',
    's12_h1':  'Math Protects ',
    's12_h2':  'Every Trade',
    's12_pillars': [
        (GREEN,  'Stop always pre-defined',
                 'ATR-based or support-anchored. You know max loss before entry.'),
        (CYAN,   'R/R >= 2.0 required',
                 'Signals only generated when TP1 yields at least 2:1. Below that = discarded.'),
        (GOLD,   'Regime gate',
                 'MacroContext blocks agents in flat/chaos conditions in real time.'),
        (PURPLE, 'Default: 1% risk per trade',
                 'Conservative default. Max leverage cap: 10x. Configurable per client.'),
    ],

    's13_tag': 'Technology',
    's13_h1':  'Built for Speed, Reliability & Scale',
    's13_techs': [
        ('Python 3.14',        'Latest runtime, typed dataclass config'),
        ('ThreadPoolExecutor', '8-thread parallel scan, 10x speed'),
        ('Binance fapi',       'USDT futures: klines, OI, funding, depth'),
        ('Bybit + MEXC',       'Multi-exchange arbitrage validation'),
        ('pytest x13',         'Unit + integration, all green'),
        ('Task Scheduler',     'Hourly autorun, zero manual ops'),
        ('JSONL Logging',      'Every signal stored, append-only'),
        ('config.yaml',        '40+ parameters externalized'),
        ('Claude AI',          'LLM-assisted briefing + narrative'),
        ('News Feed',          'RSS crypto news correlated with signals'),
    ],
    's13_zeros': [
        ('Zero', 'paid API keys required', CYAN),
        ('Zero', 'external DB needed',     GREEN),
        ('Zero', 'cloud infra for v1.0',   GOLD),
        ('100%', 'open, auditable code',   PURPLE),
    ],

    's14_sub1': 'The engine is live. The signals are flowing.',
    's14_sub2': '4 weeks from battle-tested, provably-edged, production-ready',
    's14_sub3': 'institutional-grade signal intelligence -- with zero black boxes.',
    's14_cta': [
        (CYAN,   'Timeline',      '~4 weeks to v1.0.\nLive validation running\nright now, every hour.'),
        (GREEN,  'Gate Criteria', 'WR >= 52%,\nexpectancy > 0,\n<20% drawdown.'),
        (GOLD,   'Risk First',    'Position sizing is\nnot optional -- it is\nstructural.'),
        (PURPLE, 'Early Access',  'Clients joining pre-v1.0\nparticipate in live\nvalidation.'),
    ],
    's14_live': 'System running live -- next scan fires in under 60 minutes',
},

# ─────────────────────────────────────────────────────────────────────────────
'cs': {
    's1_tag':   'DUVERNY BRIEFING PRO INVESTORY -- KVETEN 2026',
    's1_title': 'HERMES FOUNDATION',
    's1_sub1':  'Kryptosignalni inteligence institucionalni urovne.',
    's1_sub2':  'AI-rizene multi-agentni skenovani 200+ zivych trhu -- kazde hodinu, 24/7.',
    's1_badges':       ['6 specializovanych agentu', 'Trhy v realnem case',
                        'Integrovane rizeni rizik',  'Aktivni od kvetna 2026'],
    's1_badge_colors': [CYAN, CYAN, PURPLE, GOLD],

    's2_tag': 'Problem',
    's2_h1':  'Trh nikdy nespi.',
    's2_h2':  'Lide ano.',
    's2_problems': [
        '90 % retailovych obchodniku s kryptem prodela za 12 mesicu',
        'Emocionalni rozhodnuti nici edge v kriticke trzni momenty',
        'Rucni skenovani 200+ paru v realnem case je nemozne',
        'Slepé misto rezimu -- obchodovani na ploskem trhu nici expectancy',
        'Zadne systematicke rizeni pozic -- velikosti jsou rizenény guts, ne matematikou',
    ],
    's2_stats': [
        ('90%',   'retailovych obchodniku podvykonava', RED),
        ('200+',  'USDT paru na Binance Futures',       GOLD),
        ('$2.4T', 'celkova trzni kapitalizace krypto',  CYAN),
    ],

    's3_tag': 'Reseni',
    's3_h1':  'Seznamte se s ',
    's3_h2':  'Hermes',
    's3_points': [
        ('Bezi kazde hodinu, 24/7',      'Zadna lidska pozornost neni nutna'),
        ('Makro-rezimova inteligence',   'Automaticky preskakuje ploché / chaoticke podminky'),
        ('Skorovaci motor 20+ faktoru',  'Kazdy par ohodnocen pred analyzou agentù'),
        ('Integrovany sizer pozic',      'size = riziko / |entry - stop|, vzdy'),
        ('Samoukládajici signaly',       'Kazdy signal zaznamenan a zpetne hodnocen'),
        ('Prokazatelny edge',            'Backtest -> ziva validace -> iteracni zlepseni'),
    ],
    's3_metrics': [
        ('<10s', 'Plne skenovani 200 paru', CYAN),
        ('24/7', 'Autonomni provoz',        GREEN),
        ('6',    'Specializovanych agentu', GOLD),
        ('3x',   'Monitorovane burzy',      PURPLE),
    ],
    's3_callout_h':    'SYSTEM V JEDNE VETE',
    's3_callout_body': (
        'Hermes sleduje 200+ trhu soucasne, detekuje setupy splnujici prisna '
        'multi-faktorova kriteria a dodava signaly pripravene k obchodovani '
        's matematicky nastavenym rizikem -- zatimco spite.'
    ),

    's4_tag': 'Jadro architektury',
    's4_h1':  'Sest specializovanych ',
    's4_h2':  'inteligentnich agentu',
    's4_agents': [
        ('Long Agent',     'FUTURES LONG',
         'Bullish breakout setupy. Vyzaduje objemovy skok >= 2x, '
         'silny rust OI, pozitivni trendove zarovnani, skore >= 80.'),
        ('Short Agent',    'FUTURES SHORT',
         'Bearish reverzni setupy. Hleda obrat fundingu, divergenci OI '
         'a signaly vycerpani momentu na Binance Futures.'),
        ('Spot Agent',     'SPOT LONG',
         'Akumulacni zony se stopem ukotvenym na supportu 1H, '
         'nikoli na pevnem procentu -- omezuje sumove vystupy.'),
        ('Arb Agent',      'CROSS-EXCHANGE ARB',
         'Cenove mezery na Binance, Bybit a MEXC Futures. '
         'Identifikuje okna s pozitivnim ziskem po odecten slippage.'),
        ('Options Agent',  'DERIVATIVES ALERTS',
         'Pouze BTC / ETH. Spousti se pri extremnim fundingu '
         'nebo pohybu 4H > 8 %. Generuje implied-move alerty pro Deribit.'),
        ('Moonshot Agent', 'MICRO-CAP SPEKULACE',
         'Micro-capy pod $5 s objemovymi skoky 3x+. '
         'TP1=2x, TP2=4x. Asymetricke sazky s vyhledem 24-48h.'),
    ],
    's4_agent_colors': [GREEN, RED, CYAN, GOLD, PURPLE, ORANGE],

    's5_tag': 'Pipeline generovani signalu',
    's5_h1':  'Od surovych dat k ',
    's5_h2':  'realizovatelnemu signalu',
    's5_steps': [
        ('01', 'Skenovani univerza',
         'Nacteni vsech aktivnich USDT\nparu z Binance Futures.\nFiltr: regex, OI>$10M, vol>$50M.'),
        ('02', 'Paralelni skorovani',
         '8-vlaknovy pool sestavuje 20+\nfaktorove skore na par.\nSken dokoncen za < 10 sekund.'),
        ('03', 'Makro kontext',
         'BTC + ETH + 20 paru =>\nrezim: Trend / Flat / Chaos.\nUpravuje nebo blokuje agenty.'),
        ('04', 'Filtry agentu',
         'Kazdy ze 6 agentu aplikuje\nspecializovana kriteria.\nNejlepsi pary jsou povyseny.'),
        ('05', 'Vystup signalu',
         'Entry, stop, TP1, TP2,\nR/R pomer, cap paky,\npozice -- vse predpocitano.'),
    ],
    's5_bstats': [
        ('200+', 'Skenovanych paru',  CYAN),
        ('<10s',  'Doba skenování',   GREEN),
        ('1h',   'Periodicita',       GOLD),
        ('3',    'Burzy',             PURPLE),
    ],

    's6_tag': 'Proprietarni signalni inteligence',
    's6_h1':  '20+ faktorovy ',
    's6_h2':  'skorovaci motor',
    's6_factors': [
        ('Rust OI (1h)',     '+30', 1.00),
        ('Objem. skok',      '+25', 0.83),
        ('Momentum ATR',     '+20', 0.67),
        ('Zarovnani trendu', '+20', 0.67),
        ('Funding Rate',     '+15', 0.50),
        ('Blízkost likvid.', '+15', 0.50),
        ('Breakout vzor',    '+12', 0.40),
        ('Korelace BTC',     '+10', 0.33),
        ('Support/Resist.',  '+10', 0.33),
        ('Makro Rezim',      '+10', 0.33),
        ('Bonus kategorie',  '+8',  0.27),
        ('Penalizace spread','-5',  0.17),
    ],
    's6_thresh': [
        ('Min skore pro Long/Short agenta', '>= 80', GREEN),
        ('Nejlepsi pary predane agentum',   'Top 80', CYAN),
        ('Prum. signalu za hodinovy sken',  '2 - 8',  GOLD),
    ],

    's7_tag':  'Stav projektu',
    's7_h1':   'Co je ',
    's7_h2':   'jiz hotovo',
    's7_h3':   ' -- prave ted',
    's7_done': 'HOTOVO',
    's7_wip':  'PROBIHA',
    's7_items_l': [
        (True,  'Vsech 6 agentu -- pripraveni k produkci',
                'LongAgent, ShortAgent, SpotAgent, ArbAgent, OptionsAgent, MoonshotAgent'),
        (True,  'Paralelni trzni skener',
                'ThreadPoolExecutor x8 -- kompletni skenování za < 10 sekund'),
        (True,  'System logovani signalu',
                'signals_log.jsonl -- kazdy signal casove orazkovan a ulozen'),
        (True,  'Backtestovy ramec',
                '30denni historicka simulace s WR / expectancy / profit factor'),
        (True,  'Motor hodnoceni signalu',
                'Zpetne hodnoceni HIT_TP1 / HIT_TP2 / HIT_SL'),
        (True,  'Sizer pozic',
                'Fractional Kelly, stop na bazi ATR, vynuceni capu paky'),
    ],
    's7_items_r': [
        (True,  'Multi-burzovni cenove toky',
                'Binance fapi + Bybit Linear + MEXC Futures -- overeno'),
        (True,  'Konfiguracni system',
                'config.yaml + dataclass loader -- zadne hardcoded parametry'),
        (True,  'Automaticke hodinove spousteni',
                'Windows Task Scheduler -- kazde hodinu, logy v /logs/'),
        (True,  '13 automatizovanych testu -- vše prochazi',
                'Skener, konfig, signal log, sizer pozic, slippage'),
        (False, 'Ziva validace -- probíhá',
                'Shromazduji 50+ uzavrenych signalu pro statisticke overeni'),
        (False, 'Monitoring zdravi + Telegram alerty',
                'health_check.py -- planovano pro Fazi 5'),
    ],

    's8_tag': 'Vykonnostni cile a pruchodova kriteria',
    's8_h1':  'Nevydame, dokud ',
    's8_h2':  'cisla nedokazi pravdu',
    's8_metrics': [
        ('>52%',  'Cilovy winrate',    'Long + Short dohromady, >= 50 signalu', GREEN),
        ('>0 R',  'Expectancy',        'Pozitivni ocekavana hodnota na obchod', CYAN),
        ('<20%',  'Max sim. drawdown', 'Sim. riziko za 10denni okno',           GOLD),
        ('<10s',  'Latence skenování', 'Plné universum 200 paru, paralelne',    PURPLE),
    ],
    's8_gate_h': 'BRANA UVOLNENI -- VSECHNA KRITERIA MUSI BYT SPLNENA PRO VYDANI v1.0',
    's8_gates': [
        'Winrate >= 52 % z 50+ uzavrenych signalu',
        'Expectancy > 0 pro kazdy typ agenta',
        'Max simulovany drawdown <= 20 %',
        '15+ automatizovanych testu, nula selhani',
        'Latence skenování < 10 s, overeny nepretrzity provoz',
        'health_check + Telegram monitoring aktivni',
        'signals_log funguje 10+ dni bez vypadku',
        'Dokumentace README + ARCHITECTURE aktualni',
    ],
    's8_check':        'OK',
    's8_phase_label':  'Ziva validace',
    's8_phase_status': '>>> PROBIHA NYNI <<<',

    's9_tag': 'Plan realizace',
    's9_h1':  '30 dni do ',
    's9_h2':  'vydani v1.0',
    's9_phases': [
        ('Dny 1-4',   'Faze 1 -- Validacni zaklad',
         'Backtestovy ramec, logovani signalu, hodnoticí motor',    GREEN,  True),
        ('Dny 5-7',   'Faze 2 -- Architektura a vykon',
         'Paralelni sken (x8), konfiguracni system, 13 testu OK',   GREEN,  True),
        ('Dny 8-17',  'Faze 3 -- Ziva validace',
         '50+ signalu, overovaci bod den 10: WR >= 52 %, exp > 0',  CYAN,   False),
        ('Dny 18-22', 'Faze 4 -- Moonshot a Options MVP',
         'Revidovane TP cile, integrace Deribit, test ArbAgenta',   PURPLE, False),
        ('Dny 23-28', 'Faze 5 -- Produkcni hardening',
         'Zdravotni monitor, Telegram, rotace logu, >= 15 testu',   PURPLE, False),
        ('Dny 28-30', 'Faze 6 -- Pruchodova brana v1.0',
         'Musi projit vsech 8 kriterii. CHANGELOG v1.0. Go/No-Go.', GOLD,   False),
    ],
    's9_complete':    'DOKONCENO',
    's9_in_progress': 'PROBÍHA',
    's9_upcoming':    'NADCHAZEJICI',
    's9_summary': [
        ('~4 tydny', 'Do v1.0 od dneska',       CYAN),
        ('2 / 6',    'Dokoncene faze',           GREEN),
        ('Den 10',   'Prvni go/no-go brana',     GOLD),
        ('Nula',     'Externich zavislosti',      PURPLE),
    ],

    's10_tag': 'Kontrolni seznam nasazeni',
    's10_h1':  'Co stoji mezi nami a ',
    's10_h2':  'produkci',
    's10_blocks': [
        (CYAN,   '1', 'Dukaz zive validace',      '10 dni - Prave probiha',
         ['Sbirati >= 50 uzavrenych signalu (TP/SL)',
          'Winrate >= 52 % Long + Short dohromady',
          'Expectancy > 0 pro kazdy smer',
          'Max drawdown <= 20 % na sim. riziku',
          'Prubezne revize ve dnech 3 a 7']),
        (PURPLE, '2', 'Produkcni hardening',       '5 dni - Faze 5',
         ['health_check.py -- monitor latence',
          'Telegram webhook alerty pri selhani',
          'Rotace logu (100 MB / tydenne)',
          'Rozsireni testu na 15+',
          'Integrace CryptoPanic news feedu']),
        (GOLD,   '3', 'Ladeni Moonshot a Options', '5 dni - Faze 4',
         ['MoonshotAgent: TP1=2x, TP2=4x',
          'Sweep lookaheadu: optimum 24h vs 48h',
          'OptionsAgent: Deribit implied vol feed',
          'ArbAgent: 5denni ziva validace zisku',
          'Vysledky sweep backtest_moonshot.py']),
    ],
    's10_callout_h':    'ZAVER PRO INVESTORY',
    's10_callout_body': (
        'Motor jiz funguje. Zbyvajici prace je validace a hardening -- '
        'ne budovani. Nejsme pre-product. Jsme pre-release.'
    ),

    's11_tag':     'Konkurencni pozicovani',
    's11_h1':      'Proc ',
    's11_h2':      'Hermes',
    's11_h3':      ' vitezi',
    's11_headers': ['Schopnost', 'HERMES', 'Signal. kanaly', 'TradingView', 'Hotove boty'],
    's11_rows': [
        ('Skenuje 200+ paru soucasne',           True,  False, 'Castecne',  'Castecne'),
        ('Makro-rezimova inteligence',           True,  False, False,       False),
        ('Matematicky sizing pozic',             True,  False, False,       'Castecne'),
        ('Samohodnoticí log signalu',            True,  False, False,       False),
        ('Cross-burzovni arbitraz',              True,  False, False,       'Vyjim.'),
        ('Prokazatelny edge (backtest + live)',  True,  False, False,       False),
        ('Plne konfigurovatelny a rozsiritelny', True,  False, 'Omezene',   'Nekter.'),
    ],
    's11_yes': 'ANO',
    's11_no':  'NE',

    's12_tag': 'Rizeni rizik',
    's12_h1':  'Matematika chrani ',
    's12_h2':  'kazdy obchod',
    's12_pillars': [
        (GREEN,  'Stop vzdy predem definovany',
                 'Na bazi ATR nebo support. Maximalni ztratu znate pred vstupem.'),
        (CYAN,   'R/R >= 2,0 povinne',
                 'Signaly jsou generovany pouze pokud TP1 prinasi alespon 2:1. Pod tim = zahozen.'),
        (GOLD,   'Brana makro rezimu',
                 'MacroContext blokuje agenty v plosfych/chaotickych podminkach v realnem case.'),
        (PURPLE, 'Vychozi: 1 % rizika na obchod',
                 'Konzervativni hodnota. Max cap paky: 10x. Konfigurovatelne pro klienta.'),
    ],

    's13_tag': 'Technologie',
    's13_h1':  'Postaveno pro rychlost, spolehlivost a skalovatelnost',
    's13_techs': [
        ('Python 3.14',        'Nejnovejsi runtime, typovany dataclass config'),
        ('ThreadPoolExecutor', '8-vlaknove paralelni sken, 10x rychlost'),
        ('Binance fapi',       'USDT futures: klines, OI, funding, depth'),
        ('Bybit + MEXC',       'Multi-burzovni validace arbitraze'),
        ('pytest x13',         'Unit + integracni, vse zelene'),
        ('Task Scheduler',     'Hodinovy autostart, nula rucnich operaci'),
        ('JSONL Logging',      'Kazdy signal ulozen, append-only'),
        ('config.yaml',        '40+ externalizovanych parametru'),
        ('Claude AI',          'LLM-asistovany briefing a analyza'),
        ('News Feed',          'RSS krypto zpravy korelovane se signaly'),
    ],
    's13_zeros': [
        ('Nula', 'placenych API klicu',        CYAN),
        ('Nula', 'externich databazi',         GREEN),
        ('Nula', 'cloudove infrastruktury',    GOLD),
        ('100%', 'otevreny, auditovatelny kod', PURPLE),
    ],

    's14_sub1': 'Motor je zivy. Signaly proudí.',
    's14_sub2': '4 tydny od battle-tested, prokazatelne edged, produkcne pripraveneho',
    's14_sub3': 'signalni inteligence institucionalni tridy -- bez jakychkoliv cernych skrinek.',
    's14_cta': [
        (CYAN,   'Casovy plan',    '~4 tydny do v1.0.\nZiva validace probiha\nprave ted, kazde hodinu.'),
        (GREEN,  'Prud. kriteria', 'WR >= 52 %,\nexpectancy > 0,\n< 20 % drawdown.'),
        (GOLD,   'Riziko na prv.', 'Sizing pozic\nneni volitelny -- je\nstrukturalni.'),
        (PURPLE, 'Brzy pristup',   'Klienti pred v1.0\nse ucastni zive\nvalidace.'),
    ],
    's14_live': 'System bezi live -- dalsi skenování za mene nez 60 minut',
},

# ─────────────────────────────────────────────────────────────────────────────
'ua': {
    's1_tag':   'KONFIDENCIYNIY BRYFING DLYa INVESTORiV -- TRAVEN 2026',
    's1_title': 'HERMES FOUNDATION',
    's1_sub1':  'Kryptosyhnalna rozvidka instytutsiynoho rivnya.',
    's1_sub2':  'SHI-ahentne skanuvannya 200+ zhyvykh rynkiv -- shchohodynyy, 24/7.',
    's1_badges':       ['6 spetsializovanykh ahentiv', 'Skanuvannya rynku v realnomu chasi',
                        'Vbudovane upravlinnya ryzykamy', 'Aktyvno z travnya 2026'],
    's1_badge_colors': [CYAN, CYAN, PURPLE, GOLD],

    's2_tag': 'Problema',
    's2_h1':  'Rynok nikoly ne spyt.',
    's2_h2':  'Lyudy -- tak.',
    's2_problems': [
        '90% rozdribnykh treyderiv vtrachayut hroshi za 12 misyatsiv',
        'Emotsiini rishennya znyschhuyut perevahy v krytychni momenty',
        'Ruchne skanuvannya 200+ par u realnomu chasi nemozhlyve dlya lyudyny',
        'Slippi zony rezhymu -- torhivlya na ploskomu rynku znyschhue expectancy',
        'Vidsutnost systemnoho rozmiru pozytsiy -- rozmiry kerovani intuytsiieyu',
    ],
    's2_stats': [
        ('90%',   'rozdribn. treyderiv pidpratsovuyut', RED),
        ('200+',  'USDT par na Binance Futures',        GOLD),
        ('$2.4T', 'zahalna rynkova kapitalizatsiya',    CYAN),
    ],

    's3_tag': 'Rishennya',
    's3_h1':  'Znayomtesya: ',
    's3_h2':  'Hermes',
    's3_points': [
        ('Pratsyuye shchohodynyy, 24/7',    'Lyudska uvaha ne potribna'),
        ('Makro-rezhymna obiznанist',        'Avtomatychno propuskaie ploski / khaotychni umovy'),
        ('Skorynh z 20+ faktoriv',          'Otsinyuye kozhnu paru do analizu ahentamy'),
        ('Vbudovanyy rozrakhunok pozytsii',  'size = ryzyk / |entry - stop|, zavzhdy'),
        ('Samolohuyuchi syhnaly',            'Kozhen syhnal zapysuyetsya i otsinyuyetsya'),
        ('Dovedena perevaha',               'Bektest -> zhyva validatsiya -> tsykl polipshen'),
    ],
    's3_metrics': [
        ('<10s', 'Povne skanuvannya 200 par', CYAN),
        ('24/7', 'Avtonomna robota',          GREEN),
        ('6',    'Spets. ahentiv',            GOLD),
        ('3x',   'Birzh monitorytsya',        PURPLE),
    ],
    's3_callout_h':    'SYSTEMA V ODNOMU RECHENNi',
    's3_callout_body': (
        'Hermes vidslidkovuye 200+ rynkiv odnochasno, vyyavlyaye setupy, '
        'shcho vidpovidayut suvorym kryteryam, i nadaie syhnaly z matematychno '
        'rozrakhovanym ryzykom -- poky vy spyte.'
    ),

    's4_tag': 'Bazova arkhitektura',
    's4_h1':  'Shist spetsializovanykh ',
    's4_h2':  'intelektualnykh ahentiv',
    's4_agents': [
        ('Long Agent',     'FUTURES LONG',
         'Bychachi breakout setupy. Vymahaie strybok obsyahu >= 2x, '
         'syl. zrostannya OI, pozytyvne trende, skor >= 80.'),
        ('Short Agent',    'FUTURES SHORT',
         'Vedmezhi reversal setupy. Shukaie zminu fundinhu, dyverhensiyu OI '
         'ta syhnaly vysnazhennya momentumu na Binance Futures.'),
        ('Spot Agent',     'SPOT LONG',
         'Zony akumulyatsiyi zi stopom pryvyazanym do pidtrymky 1H, '
         'a ne fiksovanym vidsotkom -- zmenshue khmary vykhody.'),
        ('Arb Agent',      'CROSS-EXCHANGE ARB',
         'Tsinovi rozryvy mizh Binance, Bybit ta MEXC Futures. '
         'Vyyavlyaye vikna z pozytyvnym prybutkom pislya slippage.'),
        ('Options Agent',  'DERIVATIVES ALERTS',
         'Tilky BTC / ETH. Spratsiyo pry ekstr. fundynhu abo rusi 4H > 8 %. '
         'Heneruye implied-move alermy dlya Deribit.'),
        ('Moonshot Agent', 'MICRO-CAP SPEKULYaTsii',
         'Mikro-kepm do $5 iz stryb. obsyahu 3x+. '
         'TP1=2x, TP2=4x. Asymetrychni stavky z horyzontom 24-48h.'),
    ],
    's4_agent_colors': [GREEN, RED, CYAN, GOLD, PURPLE, ORANGE],

    's5_tag': 'Paypalayn heneratsiyi syhnaliv',
    's5_h1':  'Vid syrokh danykh do ',
    's5_h2':  'diyevoho syhnalu',
    's5_steps': [
        ('01', 'Skanuvannya vsesvitu',
         'Zavant. vsikh aktyvnykh USDT\npar z Binance Futures.\nFiltr: regex, OI>$10M, vol>$50M.'),
        ('02', 'Paralelnyy skorynh',
         '8-potok buduye 20+\nfaktornyy skor na paru.\nSkan < 10 sekund.'),
        ('03', 'Makro kontekst',
         'BTC + ETH + 20 par =>\nrezhym: Trend / Flet / Khaos.\nKoryhuye abo blokuye ahentiv.'),
        ('04', 'Filtry ahentiv',
         'Kozhen z 6 ahentiv zastos.\nspetsialt. kryteriyi.\nTilky top pary prosuvayutsya.'),
        ('05', 'Vykhid syhnalu',
         'Vkhid, stop, TP1, TP2,\nkoef. R/R, limit plech,\nrozmir pozytsii -- vse vperyod.'),
    ],
    's5_bstats': [
        ('200+', 'Par proskanovano',  CYAN),
        ('<10s',  'Tryvalost skanu',  GREEN),
        ('1h',   'Povtorennya',       GOLD),
        ('3',    'Birzhi',            PURPLE),
    ],

    's6_tag': 'Firmovaya syhnalna rozvidka',
    's6_h1':  'Skorynh z ',
    's6_h2':  '20+ faktoriv',
    's6_factors': [
        ('Zrostannya OI(1h)', '+30', 1.00),
        ('Strybok obsyahu',   '+25', 0.83),
        ('Momentum ATR',      '+20', 0.67),
        ('Vyriv. trendu',     '+20', 0.67),
        ('Funding Rate',      '+15', 0.50),
        ('Blyzk. likvid.',    '+15', 0.50),
        ('Breakout pater.',   '+12', 0.40),
        ('Korelyatsiya BTC',  '+10', 0.33),
        ('Pidtr./Opir',       '+10', 0.33),
        ('Makro rezhym',      '+10', 0.33),
        ('Bonus katehoriyi',  '+8',  0.27),
        ('Shtraf spredu',     '-5',  0.17),
    ],
    's6_thresh': [
        ('Min skor dlya Long/Short ahenta', '>= 80', GREEN),
        ('Top par peredanykh ahentam',      'Top 80', CYAN),
        ('Sered. syhnaliv za hodunn. skan', '2 - 8',  GOLD),
    ],

    's7_tag':  'Stan proektu',
    's7_h1':   'Shcho vzhe ',
    's7_h2':   'pobudovano',
    's7_h3':   ' -- pryamo zaraz',
    's7_done': 'HOTOVO',
    's7_wip':  'V PROTSESI',
    's7_items_l': [
        (True,  'Usi 6 ahentiv -- hotovi do prodakshn',
                'LongAgent, ShortAgent, SpotAgent, ArbAgent, OptionsAgent, MoonshotAgent'),
        (True,  'Paralelnyi rynkovyi skaner',
                'ThreadPoolExecutor x8 -- povne skanuvannya za < 10 sekund'),
        (True,  'Systema lohuvannya syhnaliv',
                'signals_log.jsonl -- kozhen syhnal z mitkoyу chasu zberezhenyi'),
        (True,  'Bektest-freymvork',
                '30-denni istorychna symulyatsiya z WR / expectancy / profit factor'),
        (True,  'Rushiy otsinky syhnaliv',
                'Postfaktum HIT_TP1 / HIT_TP2 / HIT_SL'),
        (True,  'Rozrakhunok rozmiru pozytsii',
                'Fractional Kelly, ATR-stop, prymusovyi limit plech'),
    ],
    's7_items_r': [
        (True,  'Multybіrzhovi tsinovi potoki',
                'Binance fapi + Bybit Linear + MEXC Futures -- perevireno'),
        (True,  'Systema konfihuratsii',
                'config.yaml + dataclass loader -- zhodnoho hardcode'),
        (True,  'Avtomatychnyy shchohodynnyy zapusk',
                'Windows Task Scheduler -- kozhen hodynu, lohy v /logs/'),
        (True,  '13 avtomato. testiv -- usi prokhodyat',
                'Skaner, konfih, loh syhnaliv, rozmir pozytsii, slippage'),
        (False, 'Zhyva validatsiya -- v protsesi',
                'Zbyraemo 50+ zakrytykh syhnaliv dlya stat. perevirky'),
        (False, 'Monitorynh zdorovya + Telegram alermy',
                'health_check.py -- zaplanovano dlya Fazy 5'),
    ],

    's8_tag': 'Tsili produktyvnosti ta kryteriii shlyuzu',
    's8_h1':  'My ne vypuskaemo, poky ',
    's8_h2':  'tsyfry tse ne dovedut',
    's8_metrics': [
        ('>52%',  'Tsil. winrate',     'Long + Short razom, >= 50 syhnaliv',   GREEN),
        ('>0 R',  'Expectancy',        'Pozytyvne ochikuvane znach. na uhodu',  CYAN),
        ('<20%',  'Maks. sim. prosadka','Sym. ryzyk za 10-denni vikno',         GOLD),
        ('<10s',  'Zatrymka skanu',    'Povnyy vsesvit 200 par, paralel.',      PURPLE),
    ],
    's8_gate_h': 'SHLYuZ RELiZU -- USi KRYTERiYi POVYNNi PROYTY DLYa VYPUSKu v1.0',
    's8_gates': [
        'Winrate >= 52% z 50+ zakrytykh syhnaliv',
        'Expectancy > 0 dlya kozhn. typu ahenta',
        'Maks. sym. prosadka <= 20%',
        '15+ avtom. testiv, nul zboiv',
        'Zatrymka skanu < 10 s, bezpererv. robota',
        'health_check + Telegram monit. aktyvnyy',
        'signals_log pratsyuye 10+ dniv bez pererv',
        'Dokumentatsiya README + ARCHITECTURE aktualna',
    ],
    's8_check':        'OK',
    's8_phase_label':  'Zhyva validatsiya',
    's8_phase_status': '>>> VYKONUYeTSYa ZARAz <<<',

    's9_tag': 'Dorozhnya karta vykonannya',
    's9_h1':  '30 dniv do ',
    's9_h2':  'relyzu v1.0',
    's9_phases': [
        ('Dni 1-4',   'Faza 1 -- Validatsiyna osnova',
         'Bektest, lohuvannya syhnaliv, rushiy otsinky',          GREEN,  True),
        ('Dni 5-7',   'Faza 2 -- Arkhitektura ta produktyvnist',
         'Paraleln. skan (x8), konfih systema, 13 testiv OK',     GREEN,  True),
        ('Dni 8-17',  'Faza 3 -- Zhyva validatsiya',
         '50+ syhnaliv, perevirka den 10: WR >= 52%, exp > 0',   CYAN,   False),
        ('Dni 18-22', 'Faza 4 -- Moonshot ta Options MVP',
         'Perehlyanuti tsili TP, Deribit, test ArbAhenta',        PURPLE, False),
        ('Dni 23-28', 'Faza 5 -- Vyrobn. zmitsnennya',
         'Monitor zdorovya, Telegram, rotatsiya, >= 15 testiv',   PURPLE, False),
        ('Dni 28-30', 'Faza 6 -- Shlyuz relyzu v1.0',
         'Usi 8 kryteriiv. CHANGELOG v1.0. Rishennya Go/No-Go.', GOLD,   False),
    ],
    's9_complete':    'ZAVERShENO',
    's9_in_progress': 'V PROTseSi',
    's9_upcoming':    'NAStuPNE',
    's9_summary': [
        ('~4 tyzhn', 'Do v1.0 vid sohodni',     CYAN),
        ('2 / 6',    'Faz zavershen',            GREEN),
        ('Den 10',   'Pershyi shlyuz go/no-go',  GOLD),
        ('Nul',      'Zovn. zalezhn. dlya rel.', PURPLE),
    ],

    's10_tag': 'Chekl. rozhortatnya',
    's10_h1':  'Shcho stoit mizh namy i ',
    's10_h2':  'prodakshn',
    's10_blocks': [
        (CYAN,   '1', 'Dokaz zhyvoyi valid.',     '10 dniv - Zaraz vykon.',
         ['Zbir >= 50 zakrytykh syhnaliv (TP/SL)',
          'Winrate >= 52% Long + Short razom',
          'Expectancy > 0 za kozhn. napryamom',
          'Maks. prosadka <= 20% sym. ryzyk',
          'Prom. ohlyady na 3-y ta 7-y den']),
        (PURPLE, '2', 'Vyrobnytche zmitsnennya',  '5 dniv - Faza 5',
         ['health_check.py -- monit. zatrymky',
          'Telegram webhook alermy pry zboyakh',
          'Rotatsiya lohiv (100 MB / shchotyp.)',
          'Rozshyrennya testiv do 15+',
          'Intehratsiya CryptoPanic news feed']),
        (GOLD,   '3', 'Nalashtuv. Moonshot/Opt.', '5 dniv - Faza 4',
         ['MoonshotAgent: TP1=2x, TP2=4x',
          'Sweep lookahead: optymum 24h vs 48h',
          'OptionsAgent: Deribit implied vol',
          'ArbAgent: 5-denна zhyva valid.',
          'Rezultaty backtest_moonshot.py']),
    ],
    's10_callout_h':    'PIDSUMOK DLYa INVESTORiV',
    's10_callout_body': (
        'Rushiy vzhe pratsyuye. Zalyshen. robota -- validatsiya ta zmitsnennya, '
        'ne rozrobka. My ne pre-produkt. My pre-reliz.'
    ),

    's11_tag':     'Konkurentne pozytsionuvannya',
    's11_h1':      'Chomu ',
    's11_h2':      'Hermes',
    's11_h3':      ' peremahaie',
    's11_headers': ['Mozhlyvosti', 'HERMES', 'Syhn. kanaly', 'TradingView', 'Hotovi boty'],
    's11_rows': [
        ('Skanuye 200+ par odnochasno',         True,  False, 'Chastk.',   'Chastk.'),
        ('Makro-rezhymna obiznанist',           True,  False, False,       False),
        ('Matematychnyy rozmir pozytsii',        True,  False, False,       'Chastk.'),
        ('Samootsinyuv. loh syhnaliv',           True,  False, False,       False),
        ('Kros-birzhovyi arbitrazh',             True,  False, False,       'Ridko'),
        ('Dovedena pereva. (bektest + live)',    True,  False, False,       False),
        ('Povn. konfihurov. ta rozshyryvane',   True,  False, 'Obm.',      'Deyaki'),
    ],
    's11_yes': 'TAK',
    's11_no':  'Ni',

    's12_tag': 'Upravlinnya ryzykamy',
    's12_h1':  'Matematyka zakhyschaie ',
    's12_h2':  'kozhnu uhodu',
    's12_pillars': [
        (GREEN,  'Stop zavzhdy vyznacheno zazdaleghid',
                 'Na osnovi ATR abo pidtrymky. Maks. zbytoky vidomi do vkhodu.'),
        (CYAN,   'R/R >= 2.0 oboviazkovо',
                 'Syhnaly lysh koly TP1 daie khoch 2:1. Nyzhche -- vidkhyleno.'),
        (GOLD,   'Shlyuz makro-rezhymu',
                 'MacroContext blokuye ahentiv u ploskykh/khaotychnykh umovakh.'),
        (PURPLE, 'Typovo: 1% ryzyku na uhodu',
                 'Konservat. za zamovch. Maks. limit plech: 10x. Konfigur. dlya kl.'),
    ],

    's13_tag': 'Tekhnolohiya',
    's13_h1':  'Pobudovano dlya shvydkosti, nadiynosti ta masshtabovanosti',
    's13_techs': [
        ('Python 3.14',        'Novitniy runtime, typizovanyy dataclass konfih'),
        ('ThreadPoolExecutor', '8-pot. par. skanuvannya, pryskorennya 10x'),
        ('Binance fapi',       'USDT futures: klines, OI, funding, depth'),
        ('Bybit + MEXC',       'Multybіrzhova validatsiya arbitrazhu'),
        ('pytest x13',         'Unit + intehratsiini, usi zeleni'),
        ('Task Scheduler',     'Shchohod. avtozapusk, nul ruchnykh op.'),
        ('JSONL Logging',      'Kozhen syhnal zberezhenyy, append-only'),
        ('config.yaml',        '40+ parametriv vynesenykh nazovni'),
        ('Claude AI',          'LLM-bryfnih ta naratyvnyy analiz'),
        ('News Feed',          'RSS krypto novyny skolov. iz syhnalamy'),
    ],
    's13_zeros': [
        ('Nul', 'platnykh API klyuchiv',       CYAN),
        ('Nul', 'zovnishnikh BD',              GREEN),
        ('Nul', 'khmarnoi infrastruktury',     GOLD),
        ('100%','vidkrytyy, perevirenyy kod',  PURPLE),
    ],

    's14_sub1': 'Rushiy zhyvyy. Syhnaly techut.',
    's14_sub2': '4 tyzhn vid battle-tested, z doveden. perevahoyu, hotovym do prodakshn',
    's14_sub3': 'syhnalnoyi rozvidky instytutsionalnoho klasu -- bez zhodnoyi chornoyi skrynky.',
    's14_cta': [
        (CYAN,   'Chasova shkala', '~4 tyzhn do v1.0.\nZhyva valid. tryvaie\npryamo zaraz, shchoh.'),
        (GREEN,  'Kryteriyi shl.',  'WR >= 52%,\nexpectancy > 0,\n< 20% prosadka.'),
        (GOLD,   'Ryzyk pershyy',  'Rozmir pozyt. --\nne optsiya, a\nstrukturn. element.'),
        (PURPLE, 'Ranniy dostup',  'Klyient do v1.0\nbere uchast u\nzhyviy validatsii.'),
    ],
    's14_live': 'Systema pratsyuye -- nastupne skanuvannya menshe nizh cherez 60 khvylun',
},

} # end LANG


# =============================================================================
# DECK CLASS
# =============================================================================

class Deck(FPDF):
    def __init__(self, font_family='Helvetica', **kwargs):
        super().__init__(**kwargs)
        self._fn = font_family
        if font_family != 'Helvetica':
            fp  = 'C:/Windows/Fonts/arial.ttf'
            fbp = 'C:/Windows/Fonts/arialbd.ttf'
            if not os.path.exists(fbp):
                fbp = fp
            self.add_font(font_family, '',  fp)
            self.add_font(font_family, 'B', fbp)

    # ── low-level helpers ──────────────────────────────────────────────────

    def bg(self, r, g, b):
        self.set_fill_color(r, g, b)
        self.rect(0, 0, W, H, style='F')

    def filled_rect(self, x, y, w, h, color, radius=0):
        self.set_fill_color(*color)
        if radius:
            self.round_corner(x, y, w, h, radius, color)
        else:
            self.rect(x, y, w, h, style='F')

    def round_corner(self, x, y, w, h, r, color):
        self.set_fill_color(*color)
        self.rect(x+r, y, w-2*r, h, style='F')
        self.rect(x, y+r, w, h-2*r, style='F')
        self.ellipse(x, y, r*2, r*2, style='F')
        self.ellipse(x+w-r*2, y, r*2, r*2, style='F')
        self.ellipse(x, y+h-r*2, r*2, r*2, style='F')
        self.ellipse(x+w-r*2, y+h-r*2, r*2, r*2, style='F')

    def glow_line(self, x, y, w=18):
        for i, alpha in enumerate([(0,245,255), (0,180,200), (0,100,140)]):
            self.set_draw_color(*alpha)
            self.set_line_width(1.2 - i * 0.35)
            self.line(x, y + i * 0.3, x + w, y + i * 0.3)

    def tag(self, x, y, text):
        self.set_font(self._fn, 'B', 7)
        self.set_text_color(*CYAN)
        self.set_xy(x, y)
        self.cell(0, 4, text.upper())

    def heading(self, x, y, text, size=22, color=WHITE):
        self.set_font(self._fn, 'B', size)
        self.set_text_color(*color)
        self.set_xy(x, y)
        self.cell(0, size * 0.45, text)

    def subheading(self, x, y, text, w=None, size=10, color=TEXT):
        self.set_font(self._fn, '', size)
        self.set_text_color(*color)
        self.set_xy(x, y)
        if w:
            self.multi_cell(w, size * 0.42, text)
        else:
            self.cell(0, size * 0.42, text)

    def label(self, x, y, text, size=8, color=MUTED):
        self.set_font(self._fn, '', size)
        self.set_text_color(*color)
        self.set_xy(x, y)
        self.cell(0, 4, text)

    def bold(self, x, y, text, size=8, color=WHITE):
        self.set_font(self._fn, 'B', size)
        self.set_text_color(*color)
        self.set_xy(x, y)
        self.cell(0, 4, text)

    def card_bg(self, x, y, w, h, border_color=None):
        self.filled_rect(x, y, w, h, SURFACE, radius=1.5)
        if border_color:
            self.set_draw_color(*border_color)
            self.set_line_width(0.3)
            self.rect(x, y, w, h)

    def metric(self, x, y, w, val, label, note='', color=CYAN):
        self.card_bg(x, y, w, 28)
        self.set_font(self._fn, 'B', 20)
        self.set_text_color(*color)
        self.set_xy(x, y+4)
        self.cell(w, 10, val, align='C')
        self.set_font(self._fn, '', 7)
        self.set_text_color(*TEXT)
        self.set_xy(x, y+15)
        self.cell(w, 4, label, align='C')
        if note:
            self.set_font(self._fn, '', 5.5)
            self.set_text_color(*MUTED)
            self.set_xy(x, y+20)
            self.cell(w, 3, note, align='C')

    def progress_bar(self, x, y, w, h, pct, color=CYAN):
        self.set_fill_color(*SURFACE2)
        self.rect(x, y, w, h, style='F')
        self.set_fill_color(*color)
        self.rect(x, y, w * min(pct, 1.0), h, style='F')

    def page_number_footer(self, n, total):
        self.set_font(self._fn, '', 6)
        self.set_text_color(*MUTED2)
        self.set_xy(W - 20, H - 7)
        self.cell(15, 4, f'{n:02d} / {total:02d}', align='R')
        self.set_draw_color(*MUTED2)
        self.set_line_width(0.2)
        self.line(10, H - 8.5, W - 10, H - 8.5)

    def new_slide(self, n=None, total=14):
        self.add_page()
        self.bg(*BG)
        self.set_draw_color(20, 26, 36)
        self.set_line_width(0.15)
        for yy in range(0, int(H), 12):
            self.line(0, yy, W, yy)
        if n:
            self.page_number_footer(n, total)


# =============================================================================
# BUILD SLIDES
# =============================================================================

def build(pdf: Deck, L: dict):
    fn = pdf._fn

    # ── S1 HERO ───────────────────────────────────────────────────────────
    pdf.new_slide(1)
    for r, alpha in [(38,8),(30,14),(22,22),(14,35)]:
        pdf.set_fill_color(0, int(alpha*2.5), int(alpha*3))
        pdf.ellipse(W/2 - r, 20 - r, r*2, r*2, style='F')
    pdf.set_draw_color(*CYAN)
    pdf.set_line_width(0.6)
    pdf.ellipse(W/2 - 12, 12, 24, 24)
    pdf.set_font(fn, 'B', 16)
    pdf.set_text_color(*CYAN)
    pdf.set_xy(W/2 - 5, 20)
    pdf.cell(10, 6, 'H', align='C')

    pdf.set_font(fn, 'B', 6.5)
    pdf.set_text_color(*CYAN)
    pdf.set_xy(0, 42)
    pdf.cell(W, 4, L['s1_tag'], align='C')

    pdf.set_font(fn, 'B', 34)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(0, 50)
    pdf.cell(W, 14, L['s1_title'], align='C')

    pdf.set_draw_color(*CYAN)
    pdf.set_line_width(1.0)
    pdf.line(W/2 - 30, 65, W/2 + 30, 65)
    pdf.set_line_width(0.3)
    pdf.set_draw_color(*PURPLE)
    pdf.line(W/2 - 45, 66.2, W/2 + 45, 66.2)

    pdf.set_font(fn, '', 10)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(0, 70)
    pdf.cell(W, 5, L['s1_sub1'], align='C')
    pdf.set_xy(0, 76)
    pdf.cell(W, 5, L['s1_sub2'], align='C')

    # badges
    badges       = L['s1_badges']
    badge_colors = L['s1_badge_colors']
    pdf.set_font(fn, 'B', 6.5)
    total_w = sum(pdf.get_string_width(bt) + 14 for bt in badges) + 6 * (len(badges)-1)
    bx = (W - total_w) / 2
    by = 90
    for bt, bc in zip(badges, badge_colors):
        bw = pdf.get_string_width(bt) + 14
        pdf.set_fill_color(*SURFACE2)
        pdf.rect(bx, by, bw, 8, style='F')
        pdf.set_draw_color(*bc)
        pdf.set_line_width(0.3)
        pdf.rect(bx, by, bw, 8)
        pdf.set_font(fn, 'B', 6.5)
        pdf.set_text_color(*bc)
        pdf.set_xy(bx, by+1.8)
        pdf.cell(bw, 4, bt, align='C')
        bx += bw + 6

    # ── S2 PROBLEM ────────────────────────────────────────────────────────
    pdf.new_slide(2)
    pdf.tag(14, 14, L['s2_tag'])
    pdf.set_font(fn, 'B', 18)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22)
    pdf.cell(0, 8, L['s2_h1'])
    pdf.set_font(fn, 'B', 18)
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14, 31)
    pdf.cell(0, 8, L['s2_h2'])
    pdf.glow_line(14, 42)

    y = 50
    for p in L['s2_problems']:
        pdf.set_fill_color(255, 68, 80)
        pdf.ellipse(14, y+1.5, 2.5, 2.5, style='F')
        pdf.set_font(fn, '', 7.5)
        pdf.set_text_color(*TEXT)
        pdf.set_xy(20, y)
        pdf.cell(110, 4.5, p)
        y += 9.5

    cards_x = 148
    cy = 22
    for val, lbl, col in L['s2_stats']:
        pdf.card_bg(cards_x, cy, 120, 30)
        pdf.set_font(fn, 'B', 22)
        pdf.set_text_color(*col)
        pdf.set_xy(cards_x+10, cy+5)
        pdf.cell(100, 10, val, align='C')
        pdf.set_font(fn, '', 7)
        pdf.set_text_color(*MUTED)
        pdf.set_xy(cards_x+10, cy+18)
        pdf.cell(100, 4, lbl, align='C')
        cy += 38

    # ── S3 SOLUTION ───────────────────────────────────────────────────────
    pdf.new_slide(3)
    pdf.tag(14, 14, L['s3_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(0, 8, L['s3_h1'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*CYAN)
    x_after = 14 + pdf.get_string_width(L['s3_h1']) + 1
    pdf.set_xy(x_after, 22); pdf.cell(0, 8, L['s3_h2'])
    pdf.glow_line(14, 32)

    y = 40
    for title, sub in L['s3_points']:
        pdf.set_fill_color(*GREEN)
        pdf.rect(14, y+2, 2.5, 2.5, style='F')
        pdf.set_font(fn, 'B', 7.5); pdf.set_text_color(*WHITE)
        pdf.set_xy(20, y); pdf.cell(0, 4.5, title)
        pdf.set_font(fn, '', 6.5); pdf.set_text_color(*MUTED)
        pdf.set_xy(20, y+4.5); pdf.cell(0, 3.5, sub)
        y += 13.5

    mx = 148
    my = 22
    for val, lbl, col in L['s3_metrics']:
        pdf.metric(mx, my, 58, val, lbl, color=col)
        my += 33

    pdf.set_fill_color(10, 28, 35)
    pdf.set_draw_color(*CYAN); pdf.set_line_width(0.4)
    pdf.rect(mx, my+2, 120, 22)
    pdf.set_draw_color(*CYAN); pdf.set_line_width(1.2)
    pdf.line(mx, my+2, mx, my+24)
    pdf.set_font(fn, 'B', 7); pdf.set_text_color(*CYAN)
    pdf.set_xy(mx+4, my+5); pdf.cell(0, 4, L['s3_callout_h'])
    pdf.set_font(fn, '', 7); pdf.set_text_color(*TEXT)
    pdf.set_xy(mx+4, my+11)
    pdf.multi_cell(112, 4, L['s3_callout_body'])

    # ── S4 AGENTS ─────────────────────────────────────────────────────────
    pdf.new_slide(4)
    pdf.tag(14, 14, L['s4_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(130, 8, L['s4_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s4_h1']), 22)
    pdf.cell(0, 8, L['s4_h2'])
    pdf.glow_line(14, 33)

    cols, card_w, card_h = 3, (W - 28 - 2*6) / 3, 46
    for i, ((name, badge_txt, desc), accent) in enumerate(
            zip(L['s4_agents'], L['s4_agent_colors'])):
        col  = i % cols;  row  = i // cols
        cx   = 14 + col * (card_w + 6)
        cy_c = 42 + row * (card_h + 5)
        pdf.card_bg(cx, cy_c, card_w, card_h)
        pdf.set_fill_color(*accent)
        pdf.rect(cx, cy_c, card_w, 1.8, style='F')
        pdf.set_font(fn, 'B', 9); pdf.set_text_color(*WHITE)
        pdf.set_xy(cx+4, cy_c+5); pdf.cell(card_w-8, 5, name)
        pdf.set_fill_color(*SURFACE2); pdf.set_draw_color(*accent)
        pdf.set_line_width(0.25)
        bw = pdf.get_string_width(badge_txt) + 6
        pdf.rect(cx+4, cy_c+11, bw, 5, style='FD')
        pdf.set_font(fn, 'B', 5); pdf.set_text_color(*accent)
        pdf.set_xy(cx+4, cy_c+12.5); pdf.cell(bw, 3, badge_txt)
        pdf.set_font(fn, '', 6.2); pdf.set_text_color(*MUTED)
        pdf.set_xy(cx+4, cy_c+18); pdf.multi_cell(card_w-8, 3.5, desc)

    # ── S5 HOW IT WORKS ───────────────────────────────────────────────────
    pdf.new_slide(5)
    pdf.tag(14, 14, L['s5_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(130, 8, L['s5_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s5_h1']), 22)
    pdf.cell(0, 8, L['s5_h2'])
    pdf.glow_line(14, 33)

    step_w = (W - 28 - 4*6) / 5
    sx = 14
    for i, (num, title, desc) in enumerate(L['s5_steps']):
        pdf.card_bg(sx, 42, step_w, 60)
        pdf.set_font(fn, 'B', 8); pdf.set_text_color(*CYAN)
        pdf.set_xy(sx+4, 46); pdf.cell(step_w-8, 4, num)
        pdf.set_font(fn, 'B', 8.5); pdf.set_text_color(*WHITE)
        pdf.set_xy(sx+4, 52); pdf.cell(step_w-8, 4.5, title)
        pdf.set_font(fn, '', 6); pdf.set_text_color(*MUTED)
        pdf.set_xy(sx+4, 59); pdf.multi_cell(step_w-8, 3.5, desc)
        if i < len(L['s5_steps']) - 1:
            ax = sx + step_w + 3
            pdf.set_font(fn, 'B', 10); pdf.set_text_color(*CYAN)
            pdf.set_xy(ax-1, 67); pdf.cell(8, 5, '>')
        sx += step_w + 6

    bx = 14
    bw = (W - 28 - 3*6) / 4
    for val, lbl, col in L['s5_bstats']:
        pdf.card_bg(bx, 113, bw, 22)
        pdf.set_font(fn, 'B', 14); pdf.set_text_color(*col)
        pdf.set_xy(bx, 115); pdf.cell(bw, 7, val, align='C')
        pdf.set_font(fn, '', 6.5); pdf.set_text_color(*MUTED)
        pdf.set_xy(bx, 123); pdf.cell(bw, 4, lbl, align='C')
        bx += bw + 6

    # ── S6 SCORING ENGINE ─────────────────────────────────────────────────
    pdf.new_slide(6)
    pdf.tag(14, 14, L['s6_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(130, 8, L['s6_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s6_h1']), 22)
    pdf.cell(0, 8, L['s6_h2'])
    pdf.glow_line(14, 33)

    cols_f, fw, fh = 4, (W - 28 - 3*5) / 4, 17
    for i, (name, weight, pct) in enumerate(L['s6_factors']):
        col_f = i % cols_f; row_f = i // cols_f
        fx = 14 + col_f * (fw + 5); fy = 40 + row_f * (fh + 3)
        pdf.card_bg(fx, fy, fw, fh)
        pdf.set_font(fn, '', 6.5); pdf.set_text_color(*TEXT)
        pdf.set_xy(fx+3, fy+2.5); pdf.cell(fw-6, 3.5, name)
        wcolor = RED if '-' in weight else CYAN
        pdf.set_font(fn, 'B', 11); pdf.set_text_color(*wcolor)
        pdf.set_xy(fx+3, fy+6); pdf.cell(fw-6, 5, weight)
        pdf.set_fill_color(*SURFACE2)
        pdf.rect(fx+3, fy+13, fw-6, 1.8, style='F')
        bar_col = RED if '-' in weight else CYAN
        pdf.set_fill_color(*bar_col)
        pdf.rect(fx+3, fy+13, (fw-6) * pct, 1.8, style='F')

    by_t = H - 30
    for i, (lbl, val, col) in enumerate(L['s6_thresh']):
        bw2 = (W - 28) / 3
        bxi = 14 + i * (bw2 + 5)
        pdf.card_bg(bxi, by_t-3, bw2, 18)
        pdf.set_font(fn, 'B', 13); pdf.set_text_color(*col)
        pdf.set_xy(bxi, by_t); pdf.cell(bw2, 7, val, align='C')
        pdf.set_font(fn, '', 6); pdf.set_text_color(*MUTED)
        pdf.set_xy(bxi, by_t+8); pdf.cell(bw2, 3.5, lbl, align='C')

    # ── S7 BUILD STATUS ───────────────────────────────────────────────────
    pdf.new_slide(7)
    pdf.tag(14, 14, L['s7_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(80, 8, L['s7_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s7_h1']), 22)
    pdf.cell(60, 8, L['s7_h2'])
    pdf.set_text_color(*WHITE)
    pdf.set_xy(14 + pdf.get_string_width(L['s7_h1'] + L['s7_h2']), 22)
    pdf.cell(0, 8, L['s7_h3'])
    pdf.glow_line(14, 33)

    y = 40
    for (done_l, text_l, sub_l), (done_r, text_r, sub_r) in zip(
            L['s7_items_l'], L['s7_items_r']):
        for done, text, sub, x0 in [
                (done_l, text_l, sub_l, 14),
                (done_r, text_r, sub_r, W/2 + 4)]:
            c  = GREEN if done else GOLD
            ic = L['s7_done'] if done else L['s7_wip']
            pdf.set_fill_color(*SURFACE)
            pdf.rect(x0, y, 126, 14, style='F')
            pdf.set_fill_color(*c)
            pdf.rect(x0, y, 1.5, 14, style='F')
            pdf.set_font(fn, 'B', 5.5); pdf.set_text_color(*c)
            pdf.set_xy(x0+4, y+2); pdf.cell(12, 3.5, ic)
            pdf.set_font(fn, 'B', 7); pdf.set_text_color(*WHITE)
            pdf.set_xy(x0+16, y+2); pdf.cell(105, 3.5, text)
            pdf.set_font(fn, '', 5.5); pdf.set_text_color(*MUTED)
            pdf.set_xy(x0+16, y+6.5); pdf.cell(105, 3.5, sub)
        y += 17

    # ── S8 PERFORMANCE ────────────────────────────────────────────────────
    pdf.new_slide(8)
    pdf.tag(14, 14, L['s8_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(140, 8, L['s8_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s8_h1']), 22)
    pdf.cell(0, 8, L['s8_h2'])
    pdf.glow_line(14, 33)

    mw = (W - 28 - 3*6) / 4; mx2 = 14
    for val, lbl, note, col in L['s8_metrics']:
        pdf.metric(mx2, 42, mw, val, lbl, note, color=col)
        mx2 += mw + 6

    pdf.card_bg(14, 80, W-28, 52)
    pdf.set_draw_color(*CYAN); pdf.set_line_width(0.3)
    pdf.rect(14, 80, W-28, 52)
    pdf.set_font(fn, 'B', 7.5); pdf.set_text_color(*CYAN)
    pdf.set_xy(18, 84); pdf.cell(0, 4, L['s8_gate_h'])

    gx, gy = 18, 93
    for i, g in enumerate(L['s8_gates']):
        col_x = gx if i < 4 else gx + (W-28)/2
        row_y = gy + (i % 4) * 9
        pdf.set_fill_color(0, 40, 20); pdf.set_draw_color(0, 180, 80)
        pdf.set_line_width(0.2)
        pdf.rect(col_x, row_y, (W-36)/2, 7, style='FD')
        pdf.set_font(fn, '', 6.5); pdf.set_text_color(*GREEN)
        pdf.set_xy(col_x+2, row_y+1.8); pdf.cell(10, 3.5, L['s8_check'])
        pdf.set_text_color(*TEXT)
        pdf.set_xy(col_x+14, row_y+1.8); pdf.cell((W-36)/2-16, 3.5, g)

    pdf.set_fill_color(*SURFACE2)
    pdf.rect(W-50, 82, 36, 24, style='F')
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*CYAN)
    pdf.set_xy(W-50, 86); pdf.cell(36, 8, 'P3', align='C')
    pdf.set_font(fn, '', 7); pdf.set_text_color(*TEXT)
    pdf.set_xy(W-50, 96); pdf.cell(36, 4, L['s8_phase_label'], align='C')
    pdf.set_font(fn, 'B', 6); pdf.set_text_color(*GREEN)
    pdf.set_xy(W-50, 101); pdf.cell(36, 4, L['s8_phase_status'], align='C')

    # ── S9 ROADMAP ────────────────────────────────────────────────────────
    pdf.new_slide(9)
    pdf.tag(14, 14, L['s9_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(100, 8, L['s9_h1'])
    pdf.set_text_color(*GOLD)
    pdf.set_xy(14 + pdf.get_string_width(L['s9_h1']), 22)
    pdf.cell(0, 8, L['s9_h2'])
    pdf.glow_line(14, 33)

    ph_y, ph_h, label_w = 40, 15, 28
    bar_x = 14 + label_w + 4
    bar_w = W - bar_x - 14

    for (days, title, desc, color, done) in L['s9_phases']:
        pdf.set_font(fn, '', 6.5); pdf.set_text_color(*MUTED)
        pdf.set_xy(14, ph_y+4); pdf.cell(label_w, 4, days, align='R')
        pdf.set_fill_color(*SURFACE)
        pdf.rect(bar_x, ph_y, bar_w, ph_h, style='F')
        pdf.set_fill_color(int(color[0]*0.12), int(color[1]*0.12), int(color[2]*0.12))
        pdf.rect(bar_x, ph_y, bar_w, ph_h, style='F')
        pdf.set_fill_color(*color)
        pdf.rect(bar_x, ph_y, 2, ph_h, style='F')
        pdf.set_font(fn, 'B', 7.5); pdf.set_text_color(*WHITE)
        pdf.set_xy(bar_x+6, ph_y+2.5); pdf.cell(0, 4, title)
        if done:
            status = L['s9_complete']
        elif color == CYAN:
            status = L['s9_in_progress']
        else:
            status = L['s9_upcoming']
        pdf.set_font(fn, 'B', 5.5)
        bw_s = pdf.get_string_width(status) + 6
        pdf.set_fill_color(*SURFACE2); pdf.set_draw_color(*color)
        pdf.set_line_width(0.25)
        sx_b = bar_x + 6 + pdf.get_string_width(title) + 6
        pdf.rect(sx_b, ph_y+2, bw_s, 5, style='FD')
        pdf.set_text_color(*color)
        pdf.set_xy(sx_b+1, ph_y+3.2); pdf.cell(bw_s-2, 3, status)
        pdf.set_font(fn, '', 6.2); pdf.set_text_color(*MUTED)
        pdf.set_xy(bar_x+6, ph_y+8); pdf.cell(bar_w-10, 4, desc)
        ph_y += ph_h + 4

    bsx = 14
    for val, lbl, col in L['s9_summary']:
        bsw = (W-28)/4 - 4
        pdf.card_bg(bsx, ph_y+4, bsw, 14)
        pdf.set_font(fn, 'B', 10); pdf.set_text_color(*col)
        pdf.set_xy(bsx, ph_y+5); pdf.cell(bsw, 6, val, align='C')
        pdf.set_font(fn, '', 5.5); pdf.set_text_color(*MUTED)
        pdf.set_xy(bsx, ph_y+12); pdf.cell(bsw, 3.5, lbl, align='C')
        bsx += bsw + 5.5

    # ── S10 WHAT'S LEFT ───────────────────────────────────────────────────
    pdf.new_slide(10)
    pdf.tag(14, 14, L['s10_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(0, 8, L['s10_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s10_h1']), 22)
    pdf.cell(0, 8, L['s10_h2'])
    pdf.glow_line(14, 33)

    bw3 = (W - 28 - 2*8) / 3; bx3 = 14
    for color, num, title, sub, items in L['s10_blocks']:
        pdf.card_bg(bx3, 42, bw3, 100)
        pdf.set_fill_color(int(color[0]*0.15), int(color[1]*0.15), int(color[2]*0.15))
        pdf.ellipse(bx3+4, 46, 10, 10, style='F')
        pdf.set_draw_color(*color); pdf.set_line_width(0.4)
        pdf.ellipse(bx3+4, 46, 10, 10)
        pdf.set_font(fn, 'B', 8); pdf.set_text_color(*color)
        pdf.set_xy(bx3+4, 47.5); pdf.cell(10, 6, num, align='C')
        pdf.set_font(fn, 'B', 9); pdf.set_text_color(*WHITE)
        pdf.set_xy(bx3+18, 47); pdf.cell(bw3-22, 5, title)
        pdf.set_font(fn, '', 6); pdf.set_text_color(*MUTED)
        pdf.set_xy(bx3+18, 53); pdf.cell(bw3-22, 3.5, sub)
        iy = 62
        for item in items:
            pdf.set_font(fn, '', 6); pdf.set_text_color(*CYAN)
            pdf.set_xy(bx3+6, iy); pdf.cell(5, 3.5, '->')
            pdf.set_text_color(*MUTED)
            pdf.set_xy(bx3+12, iy); pdf.multi_cell(bw3-16, 3.5, item)
            iy += 8
        bx3 += bw3 + 8

    pdf.set_fill_color(5, 25, 15)
    pdf.set_draw_color(*GREEN); pdf.set_line_width(0.4)
    pdf.rect(14, 148, W-28, 14)
    pdf.set_line_width(1.5); pdf.line(14, 148, 14, 162)
    pdf.set_font(fn, 'B', 7.5); pdf.set_text_color(*GREEN)
    pdf.set_xy(20, 151); pdf.cell(0, 4, L['s10_callout_h'])
    pdf.set_font(fn, '', 7); pdf.set_text_color(*TEXT)
    pdf.set_xy(20, 157); pdf.cell(0, 4, L['s10_callout_body'])

    # ── S11 COMPETITIVE MOAT ──────────────────────────────────────────────
    pdf.new_slide(11)
    pdf.tag(14, 14, L['s11_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(50, 8, L['s11_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s11_h1']), 22)
    pdf.cell(50, 8, L['s11_h2'])
    pdf.set_text_color(*WHITE)
    pdf.set_xy(14 + pdf.get_string_width(L['s11_h1'] + L['s11_h2']), 22)
    pdf.cell(0, 8, L['s11_h3'])
    pdf.glow_line(14, 33)

    headers  = L['s11_headers']
    col_w    = [(W-28)*0.38, (W-28)*0.16, (W-28)*0.16, (W-28)*0.15, (W-28)*0.15]
    hx2 = 14
    for i, (hdr, cw) in enumerate(zip(headers, col_w)):
        if i == 1:
            pdf.set_fill_color(0, 40, 50)
            pdf.set_draw_color(*CYAN); pdf.set_line_width(0.3)
            pdf.rect(hx2, 40, cw, 7, style='FD')
            pdf.set_font(fn, 'B', 6.5); pdf.set_text_color(*CYAN)
        else:
            pdf.set_font(fn, 'B', 6.5); pdf.set_text_color(*MUTED)
        pdf.set_xy(hx2, 42)
        pdf.cell(cw, 4, hdr, align='C' if i > 0 else 'L')
        hx2 += cw

    ry = 48
    yes_sym = L['s11_yes']; no_sym = L['s11_no']
    for j, (feat, *vals) in enumerate(L['s11_rows']):
        bg_c = (12,18,28) if j%2==0 else (8,13,20)
        pdf.set_fill_color(*bg_c)
        pdf.rect(14, ry, W-28, 11, style='F')
        hx2 = 14
        for i, (val, cw) in enumerate(zip([feat]+vals, col_w)):
            if i == 0:
                pdf.set_font(fn, '', 7); pdf.set_text_color(*TEXT)
                pdf.set_xy(hx2+2, ry+3.5); pdf.cell(cw-4, 4, str(val), align='L')
            else:
                if val is True:
                    sym, col2 = yes_sym, GREEN
                elif val is False:
                    sym, col2 = no_sym, RED
                else:
                    sym, col2 = str(val), GOLD
                if i == 1:
                    pdf.set_fill_color(0, 30, 40)
                    pdf.rect(hx2, ry, cw, 11, style='F')
                pdf.set_font(fn, 'B', 7); pdf.set_text_color(*col2)
                pdf.set_xy(hx2, ry+3.5); pdf.cell(cw, 4, sym, align='C')
            hx2 += cw
        ry += 11

    # ── S12 RISK MANAGEMENT ───────────────────────────────────────────────
    pdf.new_slide(12)
    pdf.tag(14, 14, L['s12_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(90, 8, L['s12_h1'])
    pdf.set_text_color(*CYAN)
    pdf.set_xy(14 + pdf.get_string_width(L['s12_h1']), 22)
    pdf.cell(0, 8, L['s12_h2'])
    pdf.glow_line(14, 33)

    pdf.set_fill_color(8, 14, 22)
    pdf.set_draw_color(*SURFACE2); pdf.set_line_width(0.3)
    pdf.rect(14, 40, 130, 60, style='FD')
    pdf.set_draw_color(*CYAN); pdf.set_line_width(0.6)
    pdf.line(14, 40, 14, 100)

    code_lines = [
        ('comment', '# Position sizer -- always enforced'),
        ('kw',      'def size(entry, stop, account, risk_pct, leverage):'),
        ('',        '    risk_amount = account * risk_pct   # e.g. 1%'),
        ('',        '    qty = risk_amount / abs(entry - stop)'),
        ('',        '    notional = qty * entry'),
        ('',        '    eff_lev = notional / account'),
        ('kw',      '    if eff_lev > leverage:   # cap enforced'),
        ('',        '        qty = (account * leverage) / entry'),
        ('kw',      '    return'),
        ('str',     '        {"qty": qty, "notional": notional,'),
        ('str',     '         "risk_usd": qty * abs(entry - stop)}'),
    ]
    cy_code = 44
    for kind, line in code_lines:
        col2 = {'comment': MUTED, 'kw': PURPLE, 'str': GOLD, '': TEXT}.get(kind, TEXT)
        pdf.set_font('Courier', '', 6); pdf.set_text_color(*col2)
        pdf.set_xy(18, cy_code); pdf.cell(122, 3.8, line)
        cy_code += 4.5

    rx2 = 154; ry2 = 40
    for color, title, body in L['s12_pillars']:
        pdf.set_fill_color(*SURFACE)
        pdf.rect(rx2, ry2, W-rx2-14, 24, style='F')
        pdf.set_fill_color(*color)
        pdf.rect(rx2, ry2, 1.5, 24, style='F')
        pdf.set_font(fn, 'B', 7.5); pdf.set_text_color(*color)
        pdf.set_xy(rx2+5, ry2+3); pdf.cell(0, 4, title)
        pdf.set_font(fn, '', 6.5); pdf.set_text_color(*MUTED)
        pdf.set_xy(rx2+5, ry2+9)
        pdf.multi_cell(W-rx2-22, 3.5, body)
        ry2 += 28

    # ── S13 TECH STACK ────────────────────────────────────────────────────
    pdf.new_slide(13)
    pdf.tag(14, 14, L['s13_tag'])
    pdf.set_font(fn, 'B', 18); pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 22); pdf.cell(0, 8, L['s13_h1'])
    pdf.glow_line(14, 33)

    tw2 = (W - 28 - 4*5) / 5
    for i, (name, desc) in enumerate(L['s13_techs']):
        col_i = i % 5; row_i = i // 5
        tcx = 14 + col_i * (tw2 + 5); tcy = 40 + row_i * 36
        pdf.card_bg(tcx, tcy, tw2, 30)
        pdf.set_font(fn, 'B', 8); pdf.set_text_color(*WHITE)
        pdf.set_xy(tcx+4, tcy+6); pdf.cell(tw2-8, 5, name)
        pdf.set_font(fn, '', 6.2); pdf.set_text_color(*MUTED)
        pdf.set_xy(tcx+4, tcy+13); pdf.multi_cell(tw2-8, 3.5, desc)

    zx = 14; zw = (W-28)/4 - 4
    for val, lbl, col in L['s13_zeros']:
        pdf.card_bg(zx, 118, zw, 16)
        pdf.set_font(fn, 'B', 13); pdf.set_text_color(*col)
        pdf.set_xy(zx, 120); pdf.cell(zw, 6, val, align='C')
        pdf.set_font(fn, '', 6); pdf.set_text_color(*MUTED)
        pdf.set_xy(zx, 127); pdf.cell(zw, 3.5, lbl, align='C')
        zx += zw + 5.5

    # ── S14 CTA ───────────────────────────────────────────────────────────
    pdf.new_slide(14)
    for r, a in [(55,5),(42,10),(30,18),(20,30)]:
        pdf.set_fill_color(0, int(a*2), int(a*3.5))
        pdf.ellipse(W/2 - r, H/2 - r - 20, r*2, r*2, style='F')
    pdf.set_draw_color(*CYAN); pdf.set_line_width(0.6)
    pdf.ellipse(W/2 - 9, 14, 18, 18)
    pdf.set_font(fn, 'B', 13); pdf.set_text_color(*CYAN)
    pdf.set_xy(W/2 - 4.5, 19); pdf.cell(9, 6, 'H', align='C')

    pdf.set_font(fn, 'B', 30); pdf.set_text_color(*WHITE)
    pdf.set_xy(0, 37); pdf.cell(W, 12, 'HERMES FOUNDATION', align='C')

    pdf.set_draw_color(*CYAN); pdf.set_line_width(0.8)
    pdf.line(W/2 - 28, 51, W/2 + 28, 51)
    pdf.set_draw_color(*PURPLE); pdf.set_line_width(0.3)
    pdf.line(W/2 - 40, 52.2, W/2 + 40, 52.2)

    pdf.set_font(fn, '', 10); pdf.set_text_color(*TEXT)
    pdf.set_xy(0, 57); pdf.cell(W, 5, L['s14_sub1'], align='C')
    pdf.set_xy(0, 64); pdf.cell(W, 5, L['s14_sub2'], align='C')
    pdf.set_font(fn, 'B', 10); pdf.set_text_color(*GOLD)
    pdf.set_xy(0, 71); pdf.cell(W, 5, L['s14_sub3'], align='C')

    cw4 = (W - 28 - 3*6) / 4; cx4 = 14
    for col, title, body in L['s14_cta']:
        pdf.set_fill_color(*SURFACE); pdf.set_draw_color(*col)
        pdf.set_line_width(0.3)
        pdf.rect(cx4, 82, cw4, 40, style='FD')
        pdf.set_fill_color(*col)
        pdf.rect(cx4, 82, cw4, 1.5, style='F')
        pdf.set_font(fn, 'B', 7.5); pdf.set_text_color(*col)
        pdf.set_xy(cx4+4, 87); pdf.cell(cw4-8, 4, title)
        pdf.set_font(fn, '', 6.5); pdf.set_text_color(*TEXT)
        pdf.set_xy(cx4+4, 93); pdf.multi_cell(cw4-8, 4, body)
        cx4 += cw4 + 6

    pdf.set_fill_color(*GREEN)
    pdf.ellipse(W/2 - 2, 128, 4, 4, style='F')
    pdf.set_font(fn, '', 7); pdf.set_text_color(*GREEN)
    pdf.set_xy(W/2 + 4, 128.5); pdf.cell(0, 3.5, L['s14_live'])


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    out_dir = os.path.dirname(os.path.abspath(__file__))

    configs = [
        ('en', 'Helvetica'),
        ('cs', 'Arial'),
        ('ua', 'Arial'),
    ]

    for lang_code, font_family in configs:
        L   = LANG[lang_code]
        pdf = Deck(font_family=font_family, orientation='L', unit='mm', format=(W, H))
        pdf.set_auto_page_break(False)
        pdf.set_margins(0, 0, 0)
        build(pdf, L)
        out_path = os.path.join(out_dir, f'hermes_{lang_code}.pdf')
        pdf.output(out_path)
        kb = os.path.getsize(out_path) // 1024
        print(f'[OK] hermes_{lang_code}.pdf  ({kb} KB, {pdf.page} pages)')

    print('Done. All 3 PDFs generated.')
