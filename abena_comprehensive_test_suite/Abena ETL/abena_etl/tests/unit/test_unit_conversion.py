import pytest
from abena_etl import UnitConversionService, UnitType

@pytest.fixture(scope="module")
def unit_service():
    return UnitConversionService()

def test_weight_conversion(unit_service):
    assert unit_service.convert_value(100, 'lb', 'kg', UnitType.WEIGHT) == pytest.approx(45.3592, rel=1e-4)
    assert unit_service.convert_value(45.3592, 'kg', 'lb', UnitType.WEIGHT) == pytest.approx(100, rel=1e-2)

def test_height_conversion(unit_service):
    assert unit_service.convert_value(6, 'ft', 'cm', UnitType.HEIGHT) == pytest.approx(182.88, rel=1e-2)
    assert unit_service.convert_value(182.88, 'cm', 'ft', UnitType.HEIGHT) == pytest.approx(6, rel=1e-2)
    assert unit_service.convert_value(70, 'in', 'cm', UnitType.HEIGHT) == pytest.approx(177.8, rel=1e-2)
    assert unit_service.convert_value(177.8, 'cm', 'in', UnitType.HEIGHT) == pytest.approx(70, rel=1e-2)

def test_temperature_conversion(unit_service):
    assert unit_service.convert_value(98.6, 'F', 'C', UnitType.TEMPERATURE) == pytest.approx(37, rel=1e-2)
    assert unit_service.convert_value(37, 'C', 'F', UnitType.TEMPERATURE) == pytest.approx(98.6, rel=1e-2)
    assert unit_service.convert_value(0, 'C', 'K', UnitType.TEMPERATURE) == pytest.approx(273.15, rel=1e-2)
    assert unit_service.convert_value(273.15, 'K', 'C', UnitType.TEMPERATURE) == pytest.approx(0, rel=1e-2)

def test_glucose_conversion(unit_service):
    assert unit_service.convert_value(100, 'mg/dL', 'mmol/L', UnitType.GLUCOSE) == pytest.approx(5.55, rel=1e-2)
    assert unit_service.convert_value(5.55, 'mmol/L', 'mg/dL', UnitType.GLUCOSE) == pytest.approx(100, rel=1e-1)

def test_same_unit_returns_value(unit_service):
    assert unit_service.convert_value(42, 'kg', 'kg', UnitType.WEIGHT) == 42
    assert unit_service.convert_value(10, 'cm', 'cm', UnitType.HEIGHT) == 10

def test_unknown_unit_returns_none(unit_service, caplog):
    with caplog.at_level('WARNING'):
        result = unit_service.convert_value(10, 'stone', 'kg', UnitType.WEIGHT)
        assert result is None
        assert "No conversion rule found" in caplog.text 