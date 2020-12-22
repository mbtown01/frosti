from sqlalchemy import Column, Float, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid


Base = declarative_base()


class OrmVersionInfo(Base):
    __tablename__ = 'version_info'

    # Primary Key
    major = Column(Integer, primary_key=True)
    minor = Column(Integer, primary_key=True)

    ''' Time of last upgrade '''
    time = Column(
        DateTime(timezone=True), nullable=False, default=func.now())


class OrmConfig(Base):
    ''' Key value configuration data storage '''
    __tablename__ = 'config'

    # Primary Key
    ''' Name of the configuration value '''
    name = Column(String, primary_key=True)

    # Columns
    value = Column(String, nullable=False)

# endregion

# region Programming


class OrmProgram(Base):
    ''' Describes a specific set of temperature targets and price overrides
    (e.g. 'home', 'away', 'overnight') '''
    __tablename__ = 'program'

    # Primary Key
    ''' GUID as primary key '''
    guid = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Columns
    ''' Name of this program '''
    name = Column(String, unique=True, nullable=False)
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)

    # Relationships
    ''' All price overrides for this program '''
    overrides = relationship(
        "OrmPriceOverride", back_populates="program", cascade="all, delete")
    ''' All times this program runs '''
    times = relationship(
        "OrmScheduleTime", back_populates="program", cascade="all, delete")


class OrmPriceOverride(Base):
    ''' For the associated program, describes a set of temperature targets
    as a function of price  '''
    __tablename__ = 'price_override'

    # Primary Key
    ''' Current price '''
    price = Column(Float, primary_key=True)
    ''' associated program '''
    program_guid = Column(
        UUID(as_uuid=True), ForeignKey('program.guid', ondelete="CASCADE"),
        nullable=False, primary_key=True)

    # Columns
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)

    # Relationships
    ''' associated program record '''
    program = relationship(
        "OrmProgram", back_populates="overrides", cascade="all, delete")


class OrmSchedule(Base):
    ''' A user-named schedule describing which program runs when (e.g.
    'weekdays', 'weekend').  Serves as a place holder to own both the
    ScheduleDays and ScheduleTimes '''
    __tablename__ = 'schedule'

    # Primary Key
    ''' GUID as primary key '''
    guid = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Columns
    ''' Name of this schedule '''
    name = Column(String, unique=True, nullable=False)

    # Relationships
    ''' All days this schedule runs in '''
    days = relationship(
        "OrmScheduleDay", back_populates="schedule", cascade="all, delete")
    ''' All times this schedule runs each day '''
    times = relationship(
        "OrmScheduleTime", back_populates="schedule", cascade="all, delete")


class OrmScheduleDay(Base):
    ''' Associates a specific day to a specific schedule.  Primary key only
    includes the day field, enforcing that no two schedules should describe
    the same day of the week '''
    __tablename__ = 'schedule_day'

    # Primary Key
    ''' Integer day [0-6] == [Monday...Sunday] '''
    day = Column(Integer, primary_key=True)

    # Columns
    ''' associated schedule '''
    schedule_guid = Column(
        UUID(as_uuid=True), ForeignKey('schedule.guid', ondelete="CASCADE"),
        nullable=False)

    # Relationships
    ''' associated schedule record '''
    schedule = relationship(
        "OrmSchedule", back_populates="days", cascade="all, delete")


class OrmScheduleTime(Base):
    ''' Associates a specific day to a specific schedule '''
    __tablename__ = 'schedule_time'

    # Primary Key
    ''' associated schedule '''
    schedule_guid = Column(
        UUID(as_uuid=True), ForeignKey('schedule.guid', ondelete="CASCADE"),
        primary_key=True, nullable=False)
    ''' Integer hour [0-23] for the program to start in this schedule '''
    hour = Column(Integer, primary_key=True)
    ''' Integer minute [0-59] for the program to start in this schedule '''
    minute = Column(Integer, primary_key=True)

    # Columns
    ''' associated program guid '''
    program_guid = Column(
        UUID(as_uuid=True), ForeignKey('program.guid', ondelete="CASCADE"),
        nullable=False)

    # Relationships
    ''' associated program record '''
    program = relationship(
        "OrmProgram", back_populates="times", cascade="all, delete")
    ''' associated schedule record '''
    schedule = relationship(
        "OrmSchedule", back_populates="times", cascade="all, delete")


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
