"""
Configuration management for the Evolutionary Trading System.
Centralizes all configuration to ensure consistency across modules.
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import logging

class TradingMode(Enum):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"

class AssetClass(Enum):
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"

@dataclass
class GeneticConfig:
    """Configuration for genetic algorithm parameters"""
    POPULATION_SIZE: int = 100
    GENERATIONS: int = 50
    MUTATION_RATE: float = 0.1
    CROSSOVER_RATE: float = 0.7
    TOURNAMENT_SIZE: int = 3
    ELITISM_COUNT: int = 2
    GENE_LENGTH: int = 20  # Number of parameters per strategy
    MIN_GENE_VALUE: float = -1.0
    MAX_GENE_VALUE: float = 1.0

@dataclass
class TradingConfig:
    """Configuration for trading parameters"""
    MODE: TradingMode = TradingMode.PAPER
    ASSET_CLASS: AssetClass = AssetClass.CRYPTO
    SYMBOLS: List[str] = None
    TIMEFRAME: str = "1h"
    INITIAL_CAPITAL: float = 10000.0
    MAX_POSITION_SIZE: float = 0.1  # 10% of capital
    STOP_LOSS_PCT: float = 0.02  # 2%
    TAKE_PROFIT_PCT: float = 0.05  # 5%
    COMMISSION_RATE: float = 0.001  # 0.1%
    
    def __post_init__(self):
        if self.SYMBOLS is None:
            if self.ASSET_CLASS == AssetClass.CRYPTO:
                self.SYMBOLS = ["BTC/USDT", "ETH/USDT"]
            elif self.ASSET_CLASS == AssetClass.STOCKS:
                self.SYMBOLS = ["AAPL", "MSFT"]
            else:
                self.SYMBOLS = ["EUR/USD", "GBP/USD"]

@dataclass
class DataConfig:
    """Configuration for data fetching"""
    HISTORICAL_DAYS: int = 365
    UPDATE_INTERVAL_MINUTES: int = 5
    DATA_SOURCE: str = "ccxt"  # "ccxt", "yfinance", or "alpha_vantage"
    FEATURES: List[str] = None
    
    def __post_init__(self):
        if self.FEATURES is None:
            self.FEATURES = [
                "open", "high", "low", "close", "volume",
                "sma_20", "sma_50", "rsi_14", "bb_upper", "bb_lower",
                "macd", "macd_signal", "atr_14", "obv"
            ]

@dataclass
class RiskConfig:
    """Configuration for risk management"""
    MAX_DRAWDOWN_PCT: float = 0.20
    MAX_CORRELATION: float = 0.7
    VAR_CONFIDENCE: float = 0.95
    MAX_LEVERAGE: float = 1.0  # No leverage by default
    DAILY_LOSS_LIMIT_PCT: float = 0.05

class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Core configurations
        self.genetic = GeneticConfig()
        self.trading = TradingConfig()
        self.data = DataConfig()
        self.risk = RiskConfig()
        
        # System paths
        self.PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        self.DATA_DIR = os.path.join(self.PROJECT_ROOT, "data")
        self.LOGS_DIR = os.path.join(self.PROJECT_ROOT, "logs")
        self.STRATEGIES_DIR = os.path.join(self.PROJECT_ROOT, "strategies")
        
        # Firebase configuration (will be loaded from .env)
        self.FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
        self.FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "")
        
        # Exchange credentials (for live trading)
        self.EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY", "")
        self.EXCHANGE_SECRET = os.getenv("EXCHANGE_SECRET", "")
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [self.DATA_DIR, self.LOGS_DIR, self.STRATEGIES_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration for critical errors"""
        errors = []
        
        # Validate trading mode specific requirements
        if self.trading.MODE == TradingMode.LIVE:
            if not self.EXCHANGE_API_KEY or not self.EXCHANGE_SECRET:
                errors.append("Exchange credentials required for LIVE trading mode")
        
        # Validate Firebase configuration
        if not self.FIREBASE_CREDENTIALS_PATH:
            errors.append("Firebase credentials path not set")
        elif not os.path.exists(self.FIREBASE_CREDENTIALS_PATH):
            errors.append(f"Firebase credentials file not found: {self.FIREBASE_CREDENTIALS_PATH