from sqlalchemy import Column, Float, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


Base = declarative_base()


class OrmThermostat(Base):
    ''' Basic thermostat for the entire system, designed as a single row '''
    __tablename__ = 'thermostat'

    # Primary Key
    ''' Unique id for this thermostat '''
    uid = Column(Integer, primary_key=True)

    # Columns
    ''' Name for this thermostat '''
    name = Column(String, unique=True)
    ''' Total fluxuation around set point allowed before action '''
    delta = Column(Float)
    ''' Seconds to run the fan after heat/cool has ended '''
    fan_runout = Column(Integer)
    ''' Seconds to run the backlight on the LCD after last user input '''
    backlight_timeout = Column(Integer)

    # Relationships
    griddy_config = relationship(
        "OrmGriddyConfig", back_populates="thermostat", uselist=False)
    griddy_updates = relationship(
        "OrmGriddyUpdate", back_populates="thermostat", uselist=True,
        order_by="desc(OrmGriddyUpdate.time)")
    programs = relationship(
        "OrmProgram", back_populates="thermostat", uselist=True)
    sensor_readings = relationship(
        "OrmSensorReading", back_populates="thermostat", uselist=True)
    states = relationship(
        "OrmThermostatState", back_populates="thermostat", uselist=True,
        order_by="desc(OrmThermostatState.time)")
    targets = relationship(
        "OrmThermostatTargets", back_populates="thermostat", uselist=True,
        order_by="desc(OrmThermostatTargets.time)")


class OrmGriddyConfig(Base):
    ''' thermostat for GoGriddy integration '''
    __tablename__ = 'griddy_config'

    # Primary Key
    ''' Centerpoint meter uid '''
    meter_id = Column(String, primary_key=True)
    ''' associated thermostat '''
    thermostat_uid = Column(
        Integer, ForeignKey('thermostat.uid'), nullable=False)

    # Columns
    ''' Griddy member uid '''
    member_id = Column(String)
    ''' ERCOT settlement point '''
    settlement_point = Column(String)
    ''' Griddy's API URL end point '''
    api_url = Column(String)

    # Relationships
    thermostat = relationship("OrmThermostat", back_populates="griddy_config")


class OrmGriddyUpdate(Base):
    __tablename__ = 'griddy_update'

    # Primary Key
    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    ''' associated thermostat '''
    thermostat_uid = Column(
        Integer, ForeignKey('thermostat.uid'), nullable=False)

    # Columns
    ''' Current price '''
    price = Column(Float)

    # Relationships
    thermostat = relationship("OrmThermostat", back_populates="griddy_updates")


class OrmProgram(Base):
    ''' A user-named program defining thermostat behavior '''
    __tablename__ = 'program'

    # Primary Key
    name = Column(String, primary_key=True)
    ''' associated thermostat '''
    thermostat_uid = Column(
        Integer, ForeignKey('thermostat.uid'), nullable=False)

    # Columns
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)

    # Relationships
    thermostat = relationship("OrmThermostat", back_populates="programs")


class OrmSensorReading(Base):
    ''' All sensor readings at a specific date/time '''
    __tablename__ = 'sensor_reading'

    # Primary Key
    ''' Time of the reading '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    ''' associated thermostat '''
    thermostat_uid = Column(
        Integer, ForeignKey('thermostat.uid'), nullable=False)

    # Columns
    ''' Temperature in degF '''
    temperature = Column(Float)
    ''' Pressure in hPa (100 Pascals) '''
    pressure = Column(Float)
    ''' Humidity in relative percentage 0-99 '''
    humidity = Column(Float)

    # Relationships
    thermostat = relationship(
        "OrmThermostat", back_populates="sensor_readings")


class OrmThermostatState(Base):
    __tablename__ = 'thermostat_state'

    # Primary Key
    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    ''' associated thermostat '''
    thermostat_uid = Column(
        Integer, ForeignKey('thermostat.uid'), nullable=False)

    # Columns
    fan = Column(Integer)
    cooling = Column(Integer)
    heating = Column(Integer)

    # Relationships
    thermostat = relationship("OrmThermostat", back_populates="states")


class OrmThermostatTargets(Base):
    __tablename__ = 'thermostat_targets'

    # Primary Key
    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    ''' associated thermostat '''
    thermostat_uid = Column(
        Integer, ForeignKey('thermostat.uid'), nullable=False)

    # Columns
    mode = Column(Integer)
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)

    # Relationships
    thermostat = relationship("OrmThermostat", back_populates="targets")
