# Abena IHR - Intelligence Layer
# Integration Monitoring, Alerting & Data Quality Analytics

import asyncio
import json
import uuid
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import redis
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from jinja2 import Template

# =============================================================================
# 1. DATABASE MODELS FOR MONITORING DATA
# =============================================================================

Base = declarative_base()

class IntegrationMetrics(Base):
    __tablename__ = 'integration_metrics'
    
    id = Column(Integer, primary_key=True)
    source_system = Column(String(100), nullable=False)
    endpoint = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float)
    status_code = Column(Integer)
    success = Column(Boolean)
    error_message = Column(Text)
    request_size = Column(Integer)
    response_size = Column(Integer)
    records_processed = Column(Integer)

class DataQualityMetrics(Base):
    __tablename__ = 'data_quality_metrics'
    
    id = Column(Integer, primary_key=True)
    source_system = Column(String(100), nullable=False)
    data_type = Column(String(50), nullable=False)  # patient, observation, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer)
    valid_records = Column(Integer)
    completeness_score = Column(Float)  # 0-1
    accuracy_score = Column(Float)      # 0-1
    consistency_score = Column(Float)   # 0-1
    timeliness_score = Column(Float)    # 0-1
    quality_issues = Column(JSON)       # Detailed issues found

class SystemHealth(Base):
    __tablename__ = 'system_health'
    
    id = Column(Integer, primary_key=True)
    component = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    network_io = Column(Float)
    is_healthy = Column(Boolean, default=True)
    health_score = Column(Float)  # 0-100

class AlertLog(Base):
    __tablename__ = 'alert_log'
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    source = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text) 