import sys
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
import shutil
import gzip
import time
import os
import os.path
import contextlib

class TimedCompressedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        TimedRotatingFileHandler.__init__(self, *args, **kwargs)
        class M(object):
            def __init__(self, old):
                self.old = old
                
            def match(self, s):
                return s.endswith('.gz') and self.old.match(s[:-3])
        self.extMatch = M(self.extMatch)
        
    
    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple) + ".gz"
        if os.path.exists(dfn):
            os.remove(dfn)
        # os.rename(self.baseFilename, dfn)
        with open(self.baseFilename) as f:
            with contextlib.closing(gzip.open(dfn, 'wb')) as of:
                shutil.copyfileobj(f, of)
        os.remove(self.baseFilename)
        
        if self.backupCount > 0:
            # find the oldest log file and delete it
            #s = glob.glob(self.baseFilename + ".20*")
            #if len(s) > self.backupCount:
            #    s.sort()
            #    os.remove(s[0])
            for s in self.getFilesToDelete():
                os.remove(s)
        #print "%s -> %s" % (self.baseFilename, dfn)
        self.mode = 'w'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    newRolloverAt = newRolloverAt - 3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt

        
def logsetup(filename, level="INFO", backupCount=30, ):
    levels = {'CRITICAL' : logging.CRITICAL,
              'ERROR' : logging.ERROR,
              'WARN' : logging.WARNING,
              'WARNING' : logging.WARNING,
              'INFO' : logging.INFO,
              'DEBUG' : logging.DEBUG,
              'NOTSET' : logging.NOTSET}
    log_formatter = logging.Formatter("%(asctime)s %(module)s:%(lineno)d - %(levelname)s - %(message)s", '%Y-%m-%d %H:%M:%S')
    root_logger = logging.getLogger()
    root_logger.setLevel(levels[level])
    def logging_handleError(record):
        ei = sys.exc_info()
        try:
            traceback.print_exception(ei[0], ei[1], ei[2],
                                      None, sys.stderr)
            sys.stderr.write('Logged from file %s, line %s\n' % (
                record.filename, record.lineno))
        except IOError:
            pass
        raise ei[1]

    ch1 = logging.StreamHandler()
    ch1.handleError = logging_handleError
    ch1.setFormatter(log_formatter)
    root_logger.addHandler(ch1)

    ch2 = TimedCompressedRotatingFileHandler(filename, when='midnight', backupCount=backupCount)
    ch2.handleError = logging_handleError
    ch2.setFormatter(log_formatter)
    root_logger.addHandler(ch2)


if __name__ == '__main__':
    logsetup("test1.log")
    logging.info("test")
