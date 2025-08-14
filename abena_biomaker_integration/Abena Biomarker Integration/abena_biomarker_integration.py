"""
Abena IHR - Real-Time Biomarker Integration System
Continuous monitoring and integration of real-time biomarker data
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
import websockets
import requests
import threading
import queue
import time
from collections import deque
import statistics

# Real-time data processing
from scipy import signal
from scipy.stats import zscore
import asyncio
import aiohttp

# Device integration libraries
try:
    import bluetooth  # For Bluetooth devices
    import serial     # For serial connections
    import bleak      # For BLE connections
except ImportError:
    bluetooth = None
    serial = None
    bleak = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DeviceType(Enum):
    CGM = "continuous_glucose_monitor"
    HRV = "heart_rate_variability"
    CORTISOL = "cortisol_sensor"
    BLOOD_PRESSURE = "blood_pressure_monitor"
    PULSE_OX = "pulse_oximeter"
    TEMPERATURE = "temperature_sensor"
    ACTIVITY = "activity_tracker"
    SLEEP = "sleep_monitor"
    STRESS = "stress_sensor"
    PAIN = "pain_assessment_device"

class DataQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class BiometricReading:
    """Single biometric reading from a device"""
    device_id: str
    device_type: DeviceType
    patient_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: DataQuality
    confidence: float  # 0-1
    raw_data: Dict[str, Any] = field(default_factory=dict)
    processed_data: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)

@dataclass
class BiometricStream:
    """Continuous stream of biometric data"""
    stream_id: str
    patient_id: str
    device_type: DeviceType
    readings: deque = field(default_factory=lambda: deque(maxlen=1000))  # Last 1000 readings
    last_reading: Optional[BiometricReading] = None
    stream_started: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    sampling_rate: float = 1.0  # Hz
    quality_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class DeviceConfiguration:
    """Configuration for a monitoring device"""
    device_id: str
    device_type: DeviceType
    patient_id: str
    connection_type: str  # "bluetooth", "wifi", "serial", "api", "ble"
    connection_params: Dict[str, Any]
    sampling_rate: float
    alert_thresholds: Dict[str, Dict[str, float]]
    calibration_params: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True

class DeviceInterface(ABC):
    """Abstract base class for device interfaces"""
    
    def __init__(self, config: DeviceConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"device_{config.device_id}")
        self.is_connected = False
        self.last_reading_time = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the device"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the device"""
        pass
    
    @abstractmethod
    async def read_data(self) -> Optional[BiometricReading]:
        """Read data from the device"""
        pass
    
    @abstractmethod
    async def calibrate(self, calibration_data: Dict) -> bool:
        """Calibrate the device"""
        pass
    
    def validate_reading(self, reading: BiometricReading) -> BiometricReading:
        """Validate and quality-check a reading"""
        # Basic validation
        if reading.value is None or np.isnan(reading.value):
            reading.quality = DataQuality.INVALID
            reading.confidence = 0.0
            return reading
        
        # Device-specific validation
        reading = self._device_specific_validation(reading)
        
        # Calculate confidence based on quality factors
        reading.confidence = self._calculate_confidence(reading)
        
        return reading
    
    def _device_specific_validation(self, reading: BiometricReading) -> BiometricReading:
        """Device-specific validation logic"""
        # Override in specific device implementations
        return reading
    
    def _calculate_confidence(self, reading: BiometricReading) -> float:
        """Calculate confidence score for reading"""
        confidence = 1.0
        
        # Reduce confidence based on quality
        quality_scores = {
            DataQuality.EXCELLENT: 1.0,
            DataQuality.GOOD: 0.9,
            DataQuality.FAIR: 0.7,
            DataQuality.POOR: 0.4,
            DataQuality.INVALID: 0.0
        }
        confidence *= quality_scores.get(reading.quality, 0.5)
        
        # Additional confidence factors can be added here
        
        return confidence

class CGMInterface(DeviceInterface):
    """Continuous Glucose Monitor interface"""
    
    def __init__(self, config: DeviceConfiguration):
        super().__init__(config)
        self.glucose_range = (70, 300)  # mg/dL
        
    async def connect(self) -> bool:
        """Connect to CGM device"""
        try:
            if self.config.connection_type == "api":
                # Connect via API (e.g., Dexcom, Abbott)
                api_url = self.config.connection_params.get("api_url")
                api_key = self.config.connection_params.get("api_key")
                
                headers = {"Authorization": f"Bearer {api_key}"}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{api_url}/status", headers=headers) as response:
                        if response.status == 200:
                            self.is_connected = True
                            self.logger.info(f"Connected to CGM {self.config.device_id}")
                            return True
            
            elif self.config.connection_type == "bluetooth":
                # Bluetooth connection logic
                if bluetooth:
                    device_address = self.config.connection_params.get("mac_address")
                    # Bluetooth connection implementation
                    self.is_connected = True
                    return True
            
            elif self.config.connection_type == "ble":
                # BLE connection logic
                if bleak:
                    device_address = self.config.connection_params.get("mac_address")
                    # BLE connection using bleak would go here
                    self.is_connected = True
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to connect to CGM: {str(e)}")
            
        return False
    
    async def disconnect(self):
        """Disconnect from CGM"""
        self.is_connected = False
        self.logger.info(f"Disconnected from CGM {self.config.device_id}")
    
    async def read_data(self) -> Optional[BiometricReading]:
        """Read glucose data from CGM"""
        if not self.is_connected:
            return None
            
        try:
            if self.config.connection_type == "api":
                glucose_value = await self._read_api_glucose()
            elif self.config.connection_type == "bluetooth":
                glucose_value = await self._read_bluetooth_glucose()
            elif self.config.connection_type == "ble":
                glucose_value = await self._read_ble_glucose()
            else:
                return None
                
            if glucose_value is not None:
                reading = BiometricReading(
                    device_id=self.config.device_id,
                    device_type=DeviceType.CGM,
                    patient_id=self.config.patient_id,
                    timestamp=datetime.now(),
                    value=glucose_value,
                    unit="mg/dL",
                    quality=DataQuality.GOOD,
                    confidence=0.9
                )
                
                # Add glucose-specific alerts
                if glucose_value < 70:
                    reading.alerts.append("HYPOGLYCEMIA_ALERT")
                elif glucose_value > 180:
                    reading.alerts.append("HYPERGLYCEMIA_ALERT")
                
                return self.validate_reading(reading)
                
        except Exception as e:
            self.logger.error(f"Failed to read CGM data: {str(e)}")
            
        return None
    
    async def _read_api_glucose(self) -> Optional[float]:
        """Read glucose via API"""
        api_url = self.config.connection_params.get("api_url")
        api_key = self.config.connection_params.get("api_key")
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{api_url}/glucose/current", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("glucose_value")
        return None
    
    async def _read_bluetooth_glucose(self) -> Optional[float]:
        """Read glucose via Bluetooth"""
        # Placeholder for Bluetooth glucose reading
        # Real implementation would use device-specific protocols
        return 120.0 + np.random.normal(0, 10)  # Simulated data
    
    async def _read_ble_glucose(self) -> Optional[float]:
        """Read glucose via BLE (Bluetooth Low Energy)"""
        # Placeholder for BLE glucose reading implementation
        # In a real implementation, this would use bleak to connect to BLE device
        return 125.0 + np.random.normal(0, 8)  # Simulated data
    
    async def calibrate(self, calibration_data: Dict) -> bool:
        """Calibrate CGM"""
        reference_glucose = calibration_data.get("reference_glucose")
        if reference_glucose:
            # Store calibration parameters
            self.config.calibration_params["reference_glucose"] = reference_glucose
            self.config.calibration_params["calibration_time"] = datetime.now().isoformat()
            return True
        return False
    
    def _device_specific_validation(self, reading: BiometricReading) -> BiometricReading:
        """Validate glucose readings"""
        glucose_value = reading.value
        
        # Check if value is within physiological range
        if glucose_value < 20 or glucose_value > 600:
            reading.quality = DataQuality.INVALID
            reading.alerts.append("GLUCOSE_OUT_OF_RANGE")
        elif glucose_value < self.glucose_range[0] or glucose_value > self.glucose_range[1]:
            reading.quality = DataQuality.FAIR
        else:
            reading.quality = DataQuality.GOOD
            
        return reading

class HRVInterface(DeviceInterface):
    """Heart Rate Variability monitor interface"""
    
    def __init__(self, config: DeviceConfiguration):
        super().__init__(config)
        self.hrv_buffer = deque(maxlen=300)  # 5 minutes at 1Hz
        
    async def connect(self) -> bool:
        """Connect to HRV device"""
        try:
            if self.config.connection_type == "bluetooth":
                # Connect to HRV device (e.g., Polar H10, Garmin)
                device_address = self.config.connection_params.get("mac_address")
                # Bluetooth LE connection for HRV devices
                self.is_connected = True
                self.logger.info(f"Connected to HRV device {self.config.device_id}")
                return True
            
            elif self.config.connection_type == "ble":
                if bleak:
                    device_address = self.config.connection_params.get("mac_address")
                    # BLE connection using bleak would go here
                    self.is_connected = True
                    self.logger.info(f"Connected to HRV device via BLE {self.config.device_id}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to connect to HRV device: {str(e)}")
            
        return False
    
    async def disconnect(self):
        """Disconnect from HRV device"""
        self.is_connected = False
        self.logger.info(f"Disconnected from HRV device {self.config.device_id}")
    
    async def read_data(self) -> Optional[BiometricReading]:
        """Read HRV data"""
        if not self.is_connected:
            return None
            
        try:
            # Read R-R intervals and calculate HRV metrics
            rr_intervals = await self._read_rr_intervals()
            
            if rr_intervals and len(rr_intervals) >= 60:  # Need minimum data for HRV
                hrv_metrics = self._calculate_hrv_metrics(rr_intervals)
                
                reading = BiometricReading(
                    device_id=self.config.device_id,
                    device_type=DeviceType.HRV,
                    patient_id=self.config.patient_id,
                    timestamp=datetime.now(),
                    value=hrv_metrics["rmssd"],  # Primary HRV metric
                    unit="ms",
                    quality=DataQuality.GOOD,
                    confidence=0.9,
                    processed_data=hrv_metrics
                )
                
                # Add HRV-specific alerts
                if hrv_metrics["rmssd"] < 20:
                    reading.alerts.append("LOW_HRV_STRESS_INDICATOR")
                elif hrv_metrics["rmssd"] > 100:
                    reading.alerts.append("UNUSUALLY_HIGH_HRV")
                
                return self.validate_reading(reading)
                
        except Exception as e:
            self.logger.error(f"Failed to read HRV data: {str(e)}")
            
        return None
    
    async def _read_rr_intervals(self) -> Optional[List[float]]:
        """Read R-R intervals from device"""
        # Simulated R-R interval data
        # Real implementation would read from actual device
        base_rr = 800  # ms
        rr_intervals = []
        
        for _ in range(120):  # 2 minutes of data
            rr = base_rr + np.random.normal(0, 50)
            rr_intervals.append(max(400, min(1200, rr)))  # Clamp to reasonable range
            
        return rr_intervals
    
    def _calculate_hrv_metrics(self, rr_intervals: List[float]) -> Dict[str, float]:
        """Calculate HRV metrics from R-R intervals"""
        rr_array = np.array(rr_intervals)
        
        # Time domain metrics
        rmssd = np.sqrt(np.mean(np.diff(rr_array) ** 2))  # Root mean square of successive differences
        sdnn = np.std(rr_array)  # Standard deviation of NN intervals
        pnn50 = np.sum(np.abs(np.diff(rr_array)) > 50) / len(rr_array) * 100
        
        # Frequency domain metrics (simplified)
        # Real implementation would use proper spectral analysis
        mean_hr = 60000 / np.mean(rr_array)  # Convert to BPM
        
        return {
            "rmssd": float(rmssd),
            "sdnn": float(sdnn),
            "pnn50": float(pnn50),
            "mean_hr": float(mean_hr),
            "total_power": float(np.var(rr_array)),
        }
    
    async def calibrate(self, calibration_data: Dict) -> bool:
        """Calibrate HRV device"""
        # HRV devices typically don't require calibration
        return True
    
    def _device_specific_validation(self, reading: BiometricReading) -> BiometricReading:
        """Validate HRV readings"""
        rmssd = reading.value
        
        # Check if value is within physiological range
        if rmssd < 0 or rmssd > 300:
            reading.quality = DataQuality.INVALID
            reading.alerts.append("HRV_OUT_OF_RANGE")
        elif rmssd < 10 or rmssd > 150:
            reading.quality = DataQuality.FAIR
        else:
            reading.quality = DataQuality.GOOD
            
        return reading

class CortisolSensorInterface(DeviceInterface):
    """Cortisol sensor interface (hypothetical future device)"""
    
    def __init__(self, config: DeviceConfiguration):
        super().__init__(config)
        self.cortisol_baseline = 12.0  # μg/dL morning baseline
        
    async def connect(self) -> bool:
        """Connect to cortisol sensor"""
        # This is hypothetical - cortisol sensors are still in development
        try:
            if self.config.connection_type == "api":
                # Connect via research API
                self.is_connected = True
                self.logger.info(f"Connected to cortisol sensor {self.config.device_id}")
                return True
            
            elif self.config.connection_type == "ble":
                # Some advanced wearable might use BLE
                if bleak:
                    device_address = self.config.connection_params.get("mac_address")
                    # BLE connection implementation would go here
                    self.is_connected = True
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to connect to cortisol sensor: {str(e)}")
            
        return False
    
    async def disconnect(self):
        """Disconnect from cortisol sensor"""
        self.is_connected = False
        self.logger.info(f"Disconnected from cortisol sensor {self.config.device_id}")
    
    async def read_data(self) -> Optional[BiometricReading]:
        """Read cortisol data"""
        if not self.is_connected:
            return None
            
        try:
            # Simulated cortisol reading with circadian rhythm
            hour = datetime.now().hour
            circadian_factor = 1.0 + 0.5 * np.cos(2 * np.pi * (hour - 8) / 24)  # Peak at 8 AM
            cortisol_value = self.cortisol_baseline * circadian_factor + np.random.normal(0, 2)
            cortisol_value = max(0, cortisol_value)  # Cortisol can't be negative
            
            reading = BiometricReading(
                device_id=self.config.device_id,
                device_type=DeviceType.CORTISOL,
                patient_id=self.config.patient_id,
                timestamp=datetime.now(),
                value=cortisol_value,
                unit="μg/dL",
                quality=DataQuality.GOOD,
                confidence=0.8  # Lower confidence for hypothetical device
            )
            
            # Cortisol-specific alerts
            if cortisol_value > 25:
                reading.alerts.append("HIGH_CORTISOL_STRESS")
            elif cortisol_value < 3:
                reading.alerts.append("LOW_CORTISOL_ADRENAL_INSUFFICIENCY")
            
            return self.validate_reading(reading)
            
        except Exception as e:
            self.logger.error(f"Failed to read cortisol data: {str(e)}")
            
        return None
    
    async def calibrate(self, calibration_data: Dict) -> bool:
        """Calibrate cortisol sensor"""
        reference_cortisol = calibration_data.get("reference_cortisol")
        if reference_cortisol:
            self.config.calibration_params["reference_cortisol"] = reference_cortisol
            return True
        return False
    
    def _device_specific_validation(self, reading: BiometricReading) -> BiometricReading:
        """Validate cortisol readings"""
        cortisol_value = reading.value
        
        # Check if value is within physiological range
        if cortisol_value < 0 or cortisol_value > 50:
            reading.quality = DataQuality.INVALID
            reading.alerts.append("CORTISOL_OUT_OF_RANGE")
        elif cortisol_value > 30:
            reading.quality = DataQuality.FAIR
            reading.alerts.append("UNUSUALLY_HIGH_CORTISOL")
        else:
            reading.quality = DataQuality.GOOD
            
        return reading 

class RealTimeBiomarkerProcessor:
    """Processes and analyzes real-time biomarker streams"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_functions = {}
        self.alert_callbacks = []
        
    def register_analysis_function(self, device_type: DeviceType, 
                                 analysis_func: Callable[[BiometricStream], Dict]):
        """Register analysis function for device type"""
        self.analysis_functions[device_type] = analysis_func
    
    def register_alert_callback(self, callback: Callable[[List[str], str], None]):
        """Register callback for alerts"""
        self.alert_callbacks.append(callback)
    
    def process_reading(self, reading: BiometricReading, stream: BiometricStream) -> Dict:
        """Process a new reading and update stream analysis"""
        
        # Add reading to stream
        stream.readings.append(reading)
        stream.last_reading = reading
        
        # Update quality metrics
        self._update_quality_metrics(stream)
        
        # Run device-specific analysis
        analysis_result = {}
        if reading.device_type in self.analysis_functions:
            analysis_result = self.analysis_functions[reading.device_type](stream)
        
        # Check for alerts
        alerts = reading.alerts.copy()
        if 'alerts' in analysis_result:
            alerts.extend(analysis_result['alerts'])
        
        # Trigger alert callbacks
        if alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alerts, reading.patient_id)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {str(e)}")
        
        return {
            'reading': reading,
            'analysis': analysis_result,
            'alerts': alerts,
            'stream_quality': stream.quality_metrics
        }
    
    def _update_quality_metrics(self, stream: BiometricStream):
        """Update stream quality metrics"""
        if len(stream.readings) < 10:
            return
            
        recent_readings = list(stream.readings)[-50:]  # Last 50 readings
        
        # Data completeness
        expected_readings = (datetime.now() - stream.stream_started).total_seconds() * stream.sampling_rate
        actual_readings = len(stream.readings)
        completeness = min(1.0, actual_readings / max(1, expected_readings))
        
        # Average confidence
        avg_confidence = np.mean([r.confidence for r in recent_readings])
        
        # Quality distribution
        quality_counts = {}
        for reading in recent_readings:
            quality_counts[reading.quality.value] = quality_counts.get(reading.quality.value, 0) + 1
        
        # Data stability (coefficient of variation)
        values = [r.value for r in recent_readings if r.quality != DataQuality.INVALID]
        stability = 1.0 / (1.0 + np.std(values) / max(np.mean(values), 0.1)) if values else 0.0
        
        stream.quality_metrics.update({
            'completeness': completeness,
            'avg_confidence': avg_confidence,
            'stability': stability,
            'quality_distribution': quality_counts,
            'last_updated': datetime.now().isoformat()
        })

def analyze_glucose_stream(stream: BiometricStream) -> Dict:
    """Analyze glucose stream for patterns and trends"""
    if len(stream.readings) < 12:  # Need at least 12 readings (1 hour at 5min intervals)
        return {}
    
    recent_readings = list(stream.readings)[-72:]  # Last 6 hours
    glucose_values = [r.value for r in recent_readings if r.quality != DataQuality.INVALID]
    
    if len(glucose_values) < 6:
        return {}
    
    # Calculate glucose metrics
    current_glucose = glucose_values[-1]
    avg_glucose = np.mean(glucose_values)
    glucose_variability = np.std(glucose_values)
    
    # Trend analysis
    if len(glucose_values) >= 6:
        recent_trend = np.polyfit(range(6), glucose_values[-6:], 1)[0]  # Slope of last 6 readings
    else:
        recent_trend = 0
    
    # Time in range (70-180 mg/dL)
    time_in_range = sum(1 for g in glucose_values if 70 <= g <= 180) / len(glucose_values) * 100
    
    # Generate alerts
    alerts = []
    if recent_trend > 5:  # Rising > 5 mg/dL per reading
        alerts.append("GLUCOSE_RISING_RAPIDLY")
    elif recent_trend < -5:  # Falling > 5 mg/dL per reading
        alerts.append("GLUCOSE_FALLING_RAPIDLY")
    
    if glucose_variability > 50:
        alerts.append("HIGH_GLUCOSE_VARIABILITY")
    
    if time_in_range < 70:
        alerts.append("POOR_GLUCOSE_CONTROL")
    
    return {
        'current_glucose': current_glucose,
        'avg_glucose': avg_glucose,
        'glucose_variability': glucose_variability,
        'trend_slope': recent_trend,
        'time_in_range_percent': time_in_range,
        'alerts': alerts,
        'analysis_timestamp': datetime.now().isoformat()
    }

def analyze_hrv_stream(stream: BiometricStream) -> Dict:
    """Analyze HRV stream for autonomic nervous system patterns"""
    if len(stream.readings) < 5:  # Need several HRV measurements
        return {}
    
    recent_readings = list(stream.readings)[-20:]  # Last 20 readings
    hrv_values = [r.value for r in recent_readings if r.quality != DataQuality.INVALID]
    
    if len(hrv_values) < 3:
        return {}
    
    # HRV analysis
    current_hrv = hrv_values[-1]
    baseline_hrv = np.mean(hrv_values[:-5]) if len(hrv_values) > 5 else np.mean(hrv_values)
    hrv_trend = (current_hrv - baseline_hrv) / baseline_hrv if baseline_hrv > 0 else 0
    
    # Stress indicators
    alerts = []
    if current_hrv < 20:
        alerts.append("HIGH_STRESS_LOW_HRV")
    elif hrv_trend < -0.3:  # 30% decrease from baseline
        alerts.append("INCREASING_STRESS_PATTERN")
    elif hrv_trend > 0.2:   # 20% increase from baseline
        alerts.append("RECOVERY_DETECTED")
    
    # Autonomic balance assessment
    autonomic_state = "balanced"
    if current_hrv < 20:
        autonomic_state = "sympathetic_dominant"
    elif current_hrv > 60:
        autonomic_state = "parasympathetic_dominant"
    
    return {
        'current_hrv': current_hrv,
        'baseline_hrv': baseline_hrv,
        'hrv_trend_percent': hrv_trend * 100,
        'autonomic_state': autonomic_state,
        'stress_level': max(0, min(10, 10 - current_hrv / 5)),  # 0-10 scale
        'alerts': alerts,
        'analysis_timestamp': datetime.now().isoformat()
    }

def analyze_cortisol_stream(stream: BiometricStream) -> Dict:
    """Analyze cortisol stream for stress and circadian patterns"""
    if len(stream.readings) < 6:  # Need several cortisol measurements
        return {}
    
    recent_readings = list(stream.readings)[-24:]  # Last 24 readings (24 hours if hourly)
    cortisol_values = [(r.timestamp, r.value) for r in recent_readings if r.quality != DataQuality.INVALID]
    
    if len(cortisol_values) < 4:
        return {}
    
    current_cortisol = cortisol_values[-1][1]
    current_hour = datetime.now().hour
    
    # Expected cortisol based on time of day (simplified circadian rhythm)
    expected_cortisol = 12.0 * (1.0 + 0.5 * np.cos(2 * np.pi * (current_hour - 8) / 24))
    cortisol_deviation = (current_cortisol - expected_cortisol) / expected_cortisol
    
    # Trend analysis
    if len(cortisol_values) >= 6:
        times = [(cv[0] - cortisol_values[0][0]).total_seconds() for cv in cortisol_values[-6:]]
        values = [cv[1] for cv in cortisol_values[-6:]]
        trend = np.polyfit(times, values, 1)[0] if len(times) > 1 else 0
    else:
        trend = 0
    
    # Generate alerts
    alerts = []
    if cortisol_deviation > 0.5:  # 50% above expected
        alerts.append("ELEVATED_CORTISOL_STRESS")
    elif cortisol_deviation < -0.3:  # 30% below expected
        alerts.append("LOW_CORTISOL_POSSIBLE_FATIGUE")
    
    if abs(trend) > 2:  # Rapid cortisol changes
        alerts.append("RAPID_CORTISOL_FLUCTUATION")
    
    # Circadian rhythm assessment
    circadian_alignment = 1.0 - abs(cortisol_deviation)
    
    return {
        'current_cortisol': current_cortisol,
        'expected_cortisol': expected_cortisol,
        'cortisol_deviation_percent': cortisol_deviation * 100,
        'cortisol_trend': trend,
        'circadian_alignment': max(0, circadian_alignment),
        'stress_indicator': min(10, max(0, cortisol_deviation * 10 + 5)),
        'alerts': alerts,
        'analysis_timestamp': datetime.now().isoformat()
    } 

class RealTimeBiomarkerManager:
    """Main manager for real-time biomarker integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices: Dict[str, DeviceInterface] = {}
        self.streams: Dict[str, BiometricStream] = {}
        self.processor = RealTimeBiomarkerProcessor()
        self.running = False
        
        # Register analysis functions
        self.processor.register_analysis_function(DeviceType.CGM, analyze_glucose_stream)
        self.processor.register_analysis_function(DeviceType.HRV, analyze_hrv_stream)
        self.processor.register_analysis_function(DeviceType.CORTISOL, analyze_cortisol_stream)
        
        # Data storage
        self.data_queue = queue.Queue()
        self.alert_history = []
        
    def add_device(self, config: DeviceConfiguration) -> bool:
        """Add a new monitoring device"""
        try:
            # Create appropriate device interface
            if config.device_type == DeviceType.CGM:
                device = CGMInterface(config)
            elif config.device_type == DeviceType.HRV:
                device = HRVInterface(config)
            elif config.device_type == DeviceType.CORTISOL:
                device = CortisolSensorInterface(config)
            else:
                self.logger.error(f"Unsupported device type: {config.device_type}")
                return False
            
            self.devices[config.device_id] = device
            
            # Create stream for this device
            stream = BiometricStream(
                stream_id=f"{config.patient_id}_{config.device_type.value}",
                patient_id=config.patient_id,
                device_type=config.device_type,
                sampling_rate=config.sampling_rate
            )
            self.streams[config.device_id] = stream
            
            self.logger.info(f"Added device: {config.device_id} for patient {config.patient_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add device {config.device_id}: {str(e)}")
            return False
    
    async def start_monitoring(self):
        """Start monitoring all configured devices"""
        self.running = True
        self.logger.info("Starting real-time biomarker monitoring")
        
        # Connect to all devices
        connection_tasks = []
        for device_id, device in self.devices.items():
            if device.config.enabled:
                connection_tasks.append(self._connect_device(device_id, device))
        
        # Wait for all connections
        connection_results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        
        connected_count = sum(1 for result in connection_results if result is True)
        self.logger.info(f"Connected to {connected_count}/{len(connection_tasks)} devices")
        
        # Start monitoring tasks
        monitoring_tasks = []
        for device_id, device in self.devices.items():
            if device.is_connected:
                task = asyncio.create_task(self._monitor_device(device_id))
                monitoring_tasks.append(task)
        
        # Start data processing task
        processing_task = asyncio.create_task(self._process_data_queue())
        monitoring_tasks.append(processing_task)
        
        # Run all monitoring tasks
        try:
            await asyncio.gather(*monitoring_tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
        finally:
            await self.stop_monitoring()
    
    async def _connect_device(self, device_id: str, device: DeviceInterface) -> bool:
        """Connect to a specific device"""
        try:
            success = await device.connect()
            if success:
                self.logger.info(f"Connected to device {device_id}")
            else:
                self.logger.warning(f"Failed to connect to device {device_id}")
            return success
        except Exception as e:
            self.logger.error(f"Connection error for device {device_id}: {str(e)}")
            return False
    
    async def _monitor_device(self, device_id: str):
        """Monitor a specific device continuously"""
        device = self.devices[device_id]
        stream = self.streams[device_id]
        
        self.logger.info(f"Starting monitoring for device {device_id}")
        
        while self.running and device.is_connected:
            try:
                # Read data from device
                reading = await device.read_data()
                
                if reading:
                    # Process the reading
                    result = self.processor.process_reading(reading, stream)
                    
                    # Queue for storage/further processing
                    self.data_queue.put({
                        'type': 'reading',
                        'device_id': device_id,
                        'data': result,
                        'timestamp': datetime.now()
                    })
                    
                    # Log high-priority alerts
                    if result['alerts']:
                        self.logger.warning(f"Alerts for {device_id}: {result['alerts']}")
                        self.alert_history.append({
                            'device_id': device_id,
                            'patient_id': reading.patient_id,
                            'alerts': result['alerts'],
                            'timestamp': datetime.now(),
                            'reading_value': reading.value
                        })
                
                # Wait according to sampling rate
                await asyncio.sleep(1.0 / device.config.sampling_rate)
                
            except Exception as e:
                self.logger.error(f"Monitoring error for device {device_id}: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_data_queue(self):
        """Process queued data for storage and analysis"""
        while self.running:
            try:
                if not self.data_queue.empty():
                    data_items = []
                    
                    # Batch process queue items
                    while not self.data_queue.empty() and len(data_items) < 100:
                        data_items.append(self.data_queue.get())
                    
                    # Process batch
                    await self._process_data_batch(data_items)
                
                await asyncio.sleep(1)  # Process queue every second
                
            except Exception as e:
                self.logger.error(f"Data processing error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _process_data_batch(self, data_items: List[Dict]):
        """Process a batch of data items"""
        # Store to Abena SDK, trigger integrations, etc.
        for item in data_items:
            if item['type'] == 'reading':
                # Store reading through Abena SDK
                await self._store_reading(item['data']['reading'])
                
                # Trigger real-time analysis updates
                await self._trigger_real_time_analysis(item)
    
    async def _store_reading(self, reading: BiometricReading):
        """Store reading through Abena SDK with automatic encryption and audit logging"""
        try:
            # Convert reading to dictionary format for Abena SDK
            biomarker_data = {
                'device_id': reading.device_id,
                'device_type': reading.device_type.value,
                'patient_id': reading.patient_id,
                'timestamp': reading.timestamp.isoformat(),
                'value': reading.value,
                'unit': reading.unit,
                'quality': reading.quality.value,
                'confidence': reading.confidence,
                'raw_data': reading.raw_data,
                'processed_data': reading.processed_data,
                'alerts': reading.alerts
            }
            
            # Use Abena SDK to store the data
            # This automatically handles encryption, audit logging, and blockchain integration
            from api_integration import AbenaAPIIntegration
            api_integration = AbenaAPIIntegration()
            success = await api_integration.store_biomarker_data(reading.patient_id, biomarker_data)
            
            if success:
                self.logger.debug(f"Successfully stored reading: {reading.device_id} = {reading.value} {reading.unit}")
            else:
                self.logger.error(f"Failed to store reading: {reading.device_id}")
                
        except Exception as e:
            self.logger.error(f"Error storing reading: {str(e)}")
    
    async def _trigger_real_time_analysis(self, data_item: Dict):
        """Trigger real-time analysis updates based on new data"""
        reading_data = data_item['data']
        
        # Check if this triggers any treatment adjustments
        if reading_data['alerts']:
            await self._handle_critical_alerts(
                reading_data['reading'].patient_id,
                reading_data['alerts'],
                reading_data['reading']
            )
    
    async def _handle_critical_alerts(self, patient_id: str, alerts: List[str], 
                                    reading: BiometricReading):
        """Handle critical alerts that may require immediate action"""
        critical_alerts = [
            "HYPOGLYCEMIA_ALERT",
            "HIGH_STRESS_LOW_HRV", 
            "ELEVATED_CORTISOL_STRESS"
        ]
        
        for alert in alerts:
            if alert in critical_alerts:
                # Trigger immediate clinical notification
                await self._send_clinical_alert(patient_id, alert, reading)
                
                # Trigger predictive model update
                await self._update_predictive_models(patient_id, reading)
    
    async def _send_clinical_alert(self, patient_id: str, alert: str, 
                                 reading: BiometricReading):
        """Send alert to clinical team"""
        alert_message = {
            'patient_id': patient_id,
            'alert_type': alert,
            'device_type': reading.device_type.value,
            'current_value': reading.value,
            'unit': reading.unit,
            'timestamp': reading.timestamp.isoformat(),
            'urgency': 'high'
        }
        
        # This would integrate with your alert system
        self.logger.critical(f"CLINICAL ALERT: {alert_message}")
    
    async def _update_predictive_models(self, patient_id: str, reading: BiometricReading):
        """Update predictive models with real-time data"""
        # This would integrate with your predictive analytics engine
        # to update patient risk profiles based on real-time biomarkers
        pass
    
    async def stop_monitoring(self):
        """Stop monitoring all devices"""
        self.running = False
        self.logger.info("Stopping real-time biomarker monitoring")
        
        # Disconnect all devices
        disconnect_tasks = []
        for device in self.devices.values():
            if device.is_connected:
                disconnect_tasks.append(device.disconnect())
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        self.logger.info("All devices disconnected")
    
    def get_patient_current_status(self, patient_id: str) -> Dict:
        """Get current real-time status for a patient"""
        patient_streams = {
            device_id: stream for device_id, stream in self.streams.items()
            if stream.patient_id == patient_id and stream.is_active
        }
        
        current_status = {
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat(),
            'active_monitors': len(patient_streams),
            'biomarkers': {},
            'alerts': [],
            'overall_status': 'stable'
        }
        
        for device_id, stream in patient_streams.items():
            if stream.last_reading:
                reading = stream.last_reading
                current_status['biomarkers'][reading.device_type.value] = {
                    'value': reading.value,
                    'unit': reading.unit,
                    'quality': reading.quality.value,
                    'timestamp': reading.timestamp.isoformat(),
                    'confidence': reading.confidence
                }
                
                # Collect active alerts
                if reading.alerts:
                    current_status['alerts'].extend(reading.alerts)
        
        # Determine overall status
        if any('CRITICAL' in alert or 'HIGH' in alert for alert in current_status['alerts']):
            current_status['overall_status'] = 'critical'
        elif current_status['alerts']:
            current_status['overall_status'] = 'warning'
        
        return current_status
    
    def get_patient_trends(self, patient_id: str, hours: int = 24) -> Dict:
        """Get biomarker trends for a patient over specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        patient_streams = {
            device_id: stream for device_id, stream in self.streams.items()
            if stream.patient_id == patient_id
        }
        
        trends = {
            'patient_id': patient_id,
            'time_period_hours': hours,
            'biomarker_trends': {},
            'pattern_analysis': {},
            'recommendations': []
        }
        
        for device_id, stream in patient_streams.items():
            device_type = stream.device_type.value
            
            # Get readings from time period
            period_readings = [
                r for r in stream.readings 
                if r.timestamp >= cutoff_time and r.quality != DataQuality.INVALID
            ]
            
            if len(period_readings) < 3:
                continue
            
            values = [r.value for r in period_readings]
            timestamps = [r.timestamp for r in period_readings]
            
            # Calculate trend metrics
            time_deltas = [(t - timestamps[0]).total_seconds() / 3600 for t in timestamps]  # Hours
            trend_slope = np.polyfit(time_deltas, values, 1)[0] if len(values) > 1 else 0
            
            trends['biomarker_trends'][device_type] = {
                'current_value': values[-1],
                'min_value': min(values),
                'max_value': max(values),
                'mean_value': np.mean(values),
                'std_value': np.std(values),
                'trend_slope': trend_slope,
                'data_points': len(values),
                'trend_direction': 'increasing' if trend_slope > 0.1 else 'decreasing' if trend_slope < -0.1 else 'stable'
            }
        
        # Generate pattern analysis and recommendations
        trends['pattern_analysis'] = self._analyze_biomarker_patterns(trends['biomarker_trends'])
        trends['recommendations'] = self._generate_real_time_recommendations(trends)
        
        return trends
    
    def _analyze_biomarker_patterns(self, biomarker_trends: Dict) -> Dict:
        """Analyze patterns across multiple biomarkers"""
        patterns = {
            'correlations': {},
            'synchrony': {},
            'risk_indicators': []
        }
        
        # Check for concerning patterns
        glucose_trend = biomarker_trends.get('continuous_glucose_monitor', {})
        hrv_trend = biomarker_trends.get('heart_rate_variability', {})
        cortisol_trend = biomarker_trends.get('cortisol_sensor', {})
        
        # Stress pattern detection
        if (hrv_trend.get('trend_direction') == 'decreasing' and 
            cortisol_trend.get('trend_direction') == 'increasing'):
            patterns['risk_indicators'].append('increasing_stress_pattern')
        
        # Glucose instability pattern
        if glucose_trend.get('std_value', 0) > 50:  # High glucose variability
            patterns['risk_indicators'].append('glucose_instability')
        
        # Recovery pattern detection
        if (hrv_trend.get('trend_direction') == 'increasing' and 
            cortisol_trend.get('trend_direction') == 'decreasing'):
            patterns['risk_indicators'].append('recovery_pattern')
        
        return patterns
    
    def _generate_real_time_recommendations(self, trends: Dict) -> List[str]:
        """Generate recommendations based on real-time trends"""
        recommendations = []
        
        biomarker_trends = trends['biomarker_trends']
        patterns = trends['pattern_analysis']
        
        # Glucose-based recommendations
        glucose_trend = biomarker_trends.get('continuous_glucose_monitor', {})
        if glucose_trend:
            if glucose_trend.get('std_value', 0) > 50:
                recommendations.append("High glucose variability detected. Consider reviewing meal timing and medication adherence.")
            
            if glucose_trend.get('trend_direction') == 'increasing':
                recommendations.append("Rising glucose trend detected. Monitor carbohydrate intake and activity levels.")
        
        # HRV-based recommendations
        hrv_trend = biomarker_trends.get('heart_rate_variability', {})
        if hrv_trend:
            if hrv_trend.get('trend_direction') == 'decreasing':
                recommendations.append("Declining HRV indicates increasing stress. Consider stress management techniques.")
            elif hrv_trend.get('current_value', 0) < 20:
                recommendations.append("Low HRV detected. Recommend rest and recovery activities.")
        
        # Pattern-based recommendations
        if 'increasing_stress_pattern' in patterns.get('risk_indicators', []):
            recommendations.append("Multi-biomarker stress pattern detected. Consider comprehensive stress evaluation.")
        
        if 'recovery_pattern' in patterns.get('risk_indicators', []):
            recommendations.append("Recovery pattern detected. Current interventions appear effective.")
        
        return recommendations 

class RealTimeBiomarkerIntegration:
    """Main integration class for real-time biomarker system"""
    
    def __init__(self):
        self.manager = RealTimeBiomarkerManager()
        self.logger = logging.getLogger(__name__)
        
        # Integration callbacks
        self.clinical_alert_callback = None
        self.predictive_update_callback = None
        self.data_storage_callback = None
    
    def set_clinical_alert_callback(self, callback: Callable):
        """Set callback for clinical alerts"""
        self.clinical_alert_callback = callback
        self.manager.processor.register_alert_callback(self._handle_clinical_alert)
    
    def set_predictive_update_callback(self, callback: Callable):
        """Set callback for predictive model updates"""
        self.predictive_update_callback = callback
    
    def set_data_storage_callback(self, callback: Callable):
        """Set callback for data storage"""
        self.data_storage_callback = callback
    
    def _handle_clinical_alert(self, alerts: List[str], patient_id: str):
        """Handle clinical alerts"""
        if self.clinical_alert_callback:
            self.clinical_alert_callback(alerts, patient_id)
    
    async def configure_patient_monitoring(self, patient_id: str, 
                                         device_configs: List[Dict]) -> bool:
        """Configure monitoring for a patient"""
        try:
            for config_dict in device_configs:
                config = DeviceConfiguration(
                    device_id=config_dict['device_id'],
                    device_type=DeviceType(config_dict['device_type']),
                    patient_id=patient_id,
                    connection_type=config_dict['connection_type'],
                    connection_params=config_dict['connection_params'],
                    sampling_rate=config_dict.get('sampling_rate', 1.0),
                    alert_thresholds=config_dict.get('alert_thresholds', {}),
                    enabled=config_dict.get('enabled', True)
                )
                
                success = self.manager.add_device(config)
                if not success:
                    self.logger.error(f"Failed to add device {config.device_id}")
                    return False
            
            self.logger.info(f"Configured {len(device_configs)} devices for patient {patient_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure patient monitoring: {str(e)}")
            return False
    
    async def start_patient_monitoring(self, patient_id: str):
        """Start monitoring for a specific patient"""
        patient_devices = [
            device_id for device_id, stream in self.manager.streams.items()
            if stream.patient_id == patient_id
        ]
        
        if not patient_devices:
            self.logger.warning(f"No devices configured for patient {patient_id}")
            return False
        
        # Start monitoring (this would be enhanced to support per-patient monitoring)
        await self.manager.start_monitoring()
        return True
    
    def get_real_time_patient_data(self, patient_id: str) -> Dict:
        """Get real-time data for a patient"""
        current_status = self.manager.get_patient_current_status(patient_id)
        trends_24h = self.manager.get_patient_trends(patient_id, hours=24)
        
        return {
            'patient_id': patient_id,
            'current_status': current_status,
            'trends_24h': trends_24h,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_biomarker_alerts(self, patient_id: str, hours: int = 24) -> List[Dict]:
        """Get recent alerts for a patient"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        patient_alerts = [
            alert for alert in self.manager.alert_history
            if alert['patient_id'] == patient_id and alert['timestamp'] >= cutoff_time
        ]
        
        return sorted(patient_alerts, key=lambda x: x['timestamp'], reverse=True)


# Example usage and testing
async def main():
    """Example usage of real-time biomarker integration"""
    
    print("Abena IHR - Real-Time Biomarker Integration System")
    print("=" * 60)
    
    # Initialize the system
    biomarker_integration = RealTimeBiomarkerIntegration()
    
    # Configure monitoring for a patient
    patient_id = "PATIENT_001"
    device_configs = [
        {
            'device_id': 'CGM_001',
            'device_type': 'continuous_glucose_monitor',
            'connection_type': 'api',
            'connection_params': {
                'api_url': 'https://api.dexcom.com',
                'api_key': 'demo_key'
            },
            'sampling_rate': 0.2,  # Every 5 minutes
            'alert_thresholds': {
                'low_glucose': {'value': 70, 'severity': 'high'},
                'high_glucose': {'value': 180, 'severity': 'moderate'}
            }
        },
        {
            'device_id': 'HRV_001', 
            'device_type': 'heart_rate_variability',
            'connection_type': 'bluetooth',
            'connection_params': {
                'mac_address': '00:11:22:33:44:55'
            },
            'sampling_rate': 0.016,  # Every minute
            'alert_thresholds': {
                'low_hrv': {'value': 20, 'severity': 'moderate'}
            }
        }
    ]
    
    # Configure patient monitoring
    success = await biomarker_integration.configure_patient_monitoring(patient_id, device_configs)
    
    if success:
        print(f"✓ Configured monitoring for patient {patient_id}")
        
        # Set up callbacks
        def handle_clinical_alert(alerts, patient_id):
            print(f"🚨 CLINICAL ALERT for {patient_id}: {alerts}")
        
        biomarker_integration.set_clinical_alert_callback(handle_clinical_alert)
        
        # Start the monitoring (this would typically run indefinitely)
        # We'll run it briefly for demonstration
        print("Starting monitoring for 10 seconds...")
        monitoring_task = asyncio.create_task(biomarker_integration.manager.start_monitoring())
        
        # Wait for a short period
        await asyncio.sleep(10)
        
        # Stop monitoring
        biomarker_integration.manager.running = False
        await asyncio.sleep(1)  # Give time for tasks to clean up
        
        # Get real-time data
        real_time_data = biomarker_integration.get_real_time_patient_data(patient_id)
        print(f"\n📊 Real-time data: {json.dumps(real_time_data, indent=2, default=str)}")
        
        print("\n🔄 Real-time biomarker integration system ready!")
    else:
        print("❌ Failed to configure patient monitoring")

if __name__ == "__main__":
    asyncio.run(main()) 