from sqlalchemy import Column, Float, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


Base = declarative_base()

# region Configuration


class OrmVersionInfo(Base):
    __tablename__ = 'version_info'

    # Primary Key
    major = Column(Integer, primary_key=True)
    minor = Column(Integer, primary_key=True)

    ''' Time of last upgrade '''
    time = Column(
        DateTime(timezone=True), nullable=False, default=func.now())


class OrmThermostat(Base):
    ''' Basic thermostat for the entire system, designed as a single row '''
    __tablename__ = 'thermostat'

    # Primary Key
    ''' Name for this thermostat '''
    name = Column(String, primary_key=True)

    # Columns
    ''' Total fluxuation around set point allowed before action '''
    delta = Column(Float)
    ''' Seconds to run the fan after heat/cool has ended '''
    fan_runout = Column(Integer)
    ''' Seconds to run the backlight on the LCD after last user input '''
    backlight_timeout = Column(Integer)

    ''' Centerpoint meter uid '''
    meter_id = Column(String)
    ''' Griddy member uid '''
    member_id = Column(String)
    ''' ERCOT settlement point '''
    settlement_point = Column(String)

# endregion

# region Programming


class OrmProgram(Base):
    ''' Describes a specific set of temperature targets and price overrides
    (e.g. 'home', 'away', 'overnight') '''
    __tablename__ = 'program'

    # Primary Key
    name = Column(String, primary_key=True)

    # Columns
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)

    # Relationships
    price_overrides = relationship("OrmPriceOverride")
    times = relationship("OrmScheduleTime")


class OrmPriceOverride(Base):
    ''' For the associated program, describes a set of temperature targets
    as a function of price  '''
    __tablename__ = 'price_override'

    # Primary Key
    ''' Current price '''
    price = Column(Float, primary_key=True)

    # Relationships
    ''' associated program '''
    program_name = Column(String, ForeignKey('program.name'), nullable=False)


class OrmSchedule(Base):
    ''' A user-named schedule describing which program runs when (e.g. 
    'weekdays', 'weekend').  Serves as a place holder to own both the
    ScheduleDays and ScheduleTimes '''
    __tablename__ = 'schedule'

    # Primary Key
    name = Column(String, primary_key=True)

    # Relationships
    days = relationship("OrmScheduleDay")
    times = relationship("OrmScheduleTime")


class OrmScheduleDay(Base):
    ''' Associates a specific day to a specific schedule.  Primary key only
    includes the day field, enforcing that no two schedules should describe
    the same day of the week '''
    __tablename__ = 'schedule_day'

    # Primary Key
    ''' Integer day [0-6] == [Monday...Sunday] '''
    day = Column(Integer, primary_key=True)

    # Relationships
    ''' associated schedule '''
    schedule_name = Column(String, ForeignKey('schedule.name'), nullable=False)


class OrmScheduleTime(Base):
    ''' Associates a specific day to a specific schedule '''
    __tablename__ = 'schedule_time'

    # Primary Key
    ''' associated schedule '''
    schedule_name = Column(
        String, ForeignKey('schedule.name'), primary_key=True, nullable=False)
    ''' Integer hour [0-23] for the program to start in this schedule '''
    hour = Column(Integer, primary_key=True)
    ''' Integer minute [0-59] for the program to start in this schedule '''
    minute = Column(Integer, primary_key=True)

    # Relationships
    ''' associated program '''
    program_name = Column(String, ForeignKey('program.name'), nullable=False)

# endregion

# region State Capture


class OrmGriddyUpdate(Base):
    __tablename__ = 'griddy_update'

    # Primary Key
    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())

    # Columns
    ''' Current price '''
    price = Column(Float)


class OrmSensorReading(Base):
    ''' All sensor readings at a specific date/time '''
    __tablename__ = 'sensor_reading'

    # Primary Key
    ''' Time of the reading '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())

    # Columns
    ''' Temperature in degF '''
    temperature = Column(Float)
    ''' Pressure in hPa(100 Pascals) '''
    pressure = Column(Float)
    ''' Humidity in relative percentage 0-99 '''
    humidity = Column(Float)


class OrmThermostatState(Base):
    __tablename__ = 'thermostat_state'

    # Primary Key
    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())

    # Columns
    fan = Column(Integer)
    cooling = Column(Integer)
    heating = Column(Integer)


class OrmThermostatTargets(Base):
    __tablename__ = 'thermostat_targets'

    # Primary Key
    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())

    # Columns
    mode = Column(Integer)
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)

# endregion
