from frosti.logging import handleException, log
from frosti.hardware.LP5024LedDriver import LP5024Driver
from threading import Thread, Lock, currentThread
from queue import Queue
from functools import wraps
from time import sleep


def animation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        driver = args[0]
        animation = func.__name__
        if currentThread() != driver._animationThread:
            count = driver._animationQueue.qsize()
            log.debug(f"QUEUEING animation '{animation} size={count}'...")
            # driver.stopAnimation()
            driver._animationQueue.put_nowait((animation, kwargs))
        else:
            log.debug(f"STARTING animation '{animation}'...")
            func(*args, **kwargs)
            log.debug(f"COMPLETED animation '{animation}'...")
    return wrapper


class LedRingDriver:

    class ThreadExitException(Exception):
        pass

    def __init__(self, **setupArgs):
        self._bothCircles = LP5024Driver(0x3c, **setupArgs)
        self._leftCircle = LP5024Driver(0x28, **setupArgs)
        self._rightCircle = LP5024Driver(0x29, **setupArgs)

        incrementList = [
            0x000100, -0x010000, 0x000001, -0x000100, 0x010000, -0x000001]

        color = 0xff0000
        self._rainbowColorList = list()
        for increment in incrementList:
            for i in range(255):
                self._rainbowColorList.append(color+increment*i)
            color += increment*(255)

        self._animationQueue = Queue(32)
        self._animationStop = Lock()

        self._animationThread = Thread(
            target=self._threadStart, daemon=True, name='LED Ring Driver')
        self._animationThread.start()

    def setup(self, **setupArgs):
        self._bothCircles.setup(**setupArgs)

    def stopAnimation(self, stopAll: bool = True):
        log.debug("Stopping the animation")
        with self._animationStop:
            if stopAll:
                log.debug("Removing all other animations")
                while not self._animationQueue.empty():
                    self._animationQueue.get()
            log.debug("Releasing the animation thread")

    def _sleepOrThrow(self, secs: float):
        if self._animationStop.locked():
            raise LedRingDriver.ThreadExitException()
        sleep(secs)

    def _threadStart(self):
        while True:
            try:
                animation, kwargs = self._animationQueue.get()
                self._bothCircles.setup(enable=True)
                method = getattr(self, animation)
                if method is None:
                    raise RuntimeError(f"Animation {animation} unknown?!")
                method(**kwargs)
            except LedRingDriver.ThreadExitException:
                log.debug("DROPPING out of an animation")
                with self._animationStop:
                    log.debug("DROPPED out of an animation")
            except:
                handleException("Animation thread")
            finally:
                self._animationQueue.task_done()
                if self._animationQueue.empty():
                    self._bothCircles.setup(enable=False)

    @animation
    def breathe(self, *,
                rgbColor: int = 0x00ff00,
                brightMin: int = 40,
                brightMax: int = 250,
                brightStep: int = 5,
                cycles: int = 1,
                rate: float = 0.05):
        self._bothCircles.setBankColor(rgbColor)
        self._bothCircles.setBankControlled(0b11111111)

        for j in range(cycles):
            for i in range(brightMin, brightMax, brightStep):
                self._bothCircles.setBankBrightness(i)
                self._sleepOrThrow(rate)
            for i in range(brightMax, brightMin, -brightStep):
                self._bothCircles.setBankBrightness(i)
                self._sleepOrThrow(rate)

        self._bothCircles.setBankBrightness(brightMin)

    @animation
    def rainbow(self, *,
                colorStep: int = 16,
                brightness: int = 230,
                cycles: int = 1,
                rate: float = 0.025):
        self._bothCircles.setBankControlled(0b11111111)
        self._bothCircles.setBankBrightness(brightness)

        colorList = self._rainbowColorList
        for j in range(cycles):
            for c in range(0, len(colorList), colorStep):
                self._bothCircles.setBankColor(colorList[c % len(colorList)])
                self._sleepOrThrow(rate)

    @animation
    def dance(self, *,
              rgbColorList: list = [0xff0000, 0xff0000],
              brightness: int = 230,
              cycles: int = 1,
              rate: float = 0.05):
        self._bothCircles.setBankControlled(0b00000000)
        self._bothCircles.setLedBrightness([brightness]*8)

        for j in range(cycles):
            localColorList = list(
                rgbColorList[(j+i) % len(rgbColorList)] for i in range(8))
            self._bothCircles.setLedColor(localColorList)
            self._sleepOrThrow(rate)

    @animation
    def chase(self, *,
              rgbColorList: list = [0x00ff00]*16,
              brightnessList: list = [200]*16,
              cycles: int = 1,
              rate: float = 0.025):
        self._bothCircles.setBankControlled(0x00)
        self._bothCircles.setLedBrightness([0]*8)
        self._bothCircles.setLedColor([0]*8)

        if len(rgbColorList) != 16:
            raise RuntimeError("Expected 16 RGB color values")
        if len(brightnessList) != 16:
            raise RuntimeError("Expected 16 brightness values")

        for j in range(16*cycles):
            leftCircleRgbColorList = list(
                rgbColorList[(a+j) % 16] for a in range(8))
            leftCircleBrightness = list(
                brightnessList[(a+j) % 16] for a in range(8))
            rightCircleRgbColorList = list(
                rgbColorList[(a+j+8) % 16] for a in range(8))
            rightCircleBrightness = list(
                brightnessList[(a+j+8) % 16] for a in range(8))
            self._leftCircle.setLedColor(leftCircleRgbColorList)
            self._leftCircle.setLedBrightness(leftCircleBrightness)
            self._rightCircle.setLedColor(rightCircleRgbColorList)
            self._rightCircle.setLedBrightness(rightCircleBrightness)
            self._sleepOrThrow(rate)
