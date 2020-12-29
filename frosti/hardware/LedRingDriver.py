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
    """
    Left circle LED 0 is at top-right and increments counter-clockwise.
    Right circle LED 0 is at bottom-left and increments counter-clockwise.
    """

    class ThreadExitException(Exception):
        pass

    def __init__(self, **setupArgs):
        self._bothCircles = LP5024Driver(0x3c, **setupArgs)
        self._leftCircle = LP5024Driver(0x28, **setupArgs)
        self._rightCircle = LP5024Driver(0x29, **setupArgs)

        incrementList = [
            0x000100, -0x010000, 0x000001, -0x000100, 0x010000, -0x000001]

        color = 0xff0000
        self.rgbRainbowList = list()
        for increment in incrementList:
            for i in range(255):
                self.rgbRainbowList.append(color+increment*i)
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
                rgbColorList: int = [0x00ff00],
                brightMin: int = 40,
                brightMax: int = 250,
                brightStep: int = 5,
                cycles: int = 1,
                rate: float = 0.05):
        self._bothCircles.setBankControlled(0b11111111)

        brightnessRange = list(range(brightMin, brightMax, brightStep))
        brightnessRange += list(range(brightMax, brightMin, -brightStep))
        for j in range(cycles):
            for i in brightnessRange:
                self._bothCircles.setBankColor(
                    rgbColorList[j % len(rgbColorList)])
                self._bothCircles.setBankBrightness(i)
                self._sleepOrThrow(rate)

        self._bothCircles.setBankBrightness(brightMin)

    @animation
    def chase(self, *,
              rgbColorList: list = [0x00ff00],
              brightnessList: list = [200],
              cycles: int = 1,
              rate: float = 0.025):
        self._bothCircles.setBankControlled(0x00)
        self._bothCircles.setLedBrightness([0]*8)
        self._bothCircles.setLedColor([0]*8)

        for j in range(16*cycles):
            bothRgbColorList = list(
                rgbColorList[(a+j) % len(rgbColorList)] for a in range(16))
            bothBrightnessList = list(
                brightnessList[(a+j) % len(brightnessList)] for a in range(16))
            self._leftCircle.setLedColor(bothRgbColorList[:8])
            self._leftCircle.setLedBrightness(bothBrightnessList[:8])
            self._rightCircle.setLedColor(bothRgbColorList[-8:])
            self._rightCircle.setLedBrightness(bothBrightnessList[-8:])
            self._sleepOrThrow(rate)
