# coding=utf-8
import os
from collections import namedtuple
from struct import Struct, unpack

from lib.log import get_logger
from lib.i18n import gettext as _


logger = get_logger('dsp.data')

DATA_FILE_TYPE = '.bin'
DATA_GROUP_TYPE = '.txt'
SOURCE_DATA_TYPES = {
    '*.bin': _('Channel Data Source (*.bin)'),
    '*.txt': _('Channels Source Bundle (*.txt)'),
    }
SOURCE_DATA_TYPES_LINE = '|'.join('%s|%s' % (hint, ext) for ext, hint in SOURCE_DATA_TYPES.items())

HEADER_DATA_FORMAT = (
    '4s'    # сигнатура файла TMB1
    'I'     # Количество каналов: 4 байта, целое (Количество каналов по которым принимался сигнал)
    'I'     # Размер выборки на один канал: 4 байта, целое (число дискретных точек на один временной интервал приема данных (блок даных) N)
    'I'     # Количество спектральных линий: 4 байта, целое (меньше или равно N/2)
    'I'     # Частота среза: 4 байта, целое  (заданная частота среза ФНЧ при приеме данных)
    'f'     # Частотное разрешение: 4 байта, вещественное (шаг по частоте между спектральными линиями при анализе, Гц )
    'f'     # Время приёма блока данных: 4 байта, вещественное (время за которое принимался  блок данных, величина обратная частотному разрешению)
    'I'     # Общее время приёма данных: 4 байта, целое  (время приема всей реализации в секундах)
    'I'     # Количество принятых блоков (задано пользователем): 4 байта, целое (то что было задано пользователем при приеме данных)
    'I'     # размер данных: 4 байта, целое (количество дискретных отсчетов в файле даных)
    'I'     # число принятых блоков(принято системой): 4 байта, целое (реально принятое число блоков)
    'f'     # максимальное значение принятых данных: 4 байта, вещественное (максимальное значение  сигнала)
    'f'     # минимальное значение принятых данных: 4 байта, вещественное (минимальное значение  сигнала)
    # далее идут данные в формате 4 байта, вещественное число для одного дискретного значения сигнала.
    )

SignalHeader = namedtuple('SignalHeader', (
    'signature',
    'channel_count',
    'fetch_size_per_channel',
    'spectral_lines_count',
    'slice_freq',
    'freq_dimension',
    'rcv_time',
    'total_rcv_time',
    'blocks_count',
    'data_size',
    'system_rcved_blocks',
    'max_value',
    'min_value',
))


class SignalData(object):
    def __init__(self, file_name):
        self.file_name = file_name
        with open(self.file_name, 'rb') as f:
            self.data = f.read()

        header = Struct(HEADER_DATA_FORMAT)
        self.header = SignalHeader(*header.unpack(self.data[:header.size]))
        self.raw_signal = self.data[header.size:]

        self.float_data = [unpack('f', self.raw_signal[i:i+4]) for i in xrange(0, len(self.raw_signal)-4, 4)]

        logger.info(_('File is loaded: %s') % file_name)
        logger.info(_('File info: %s') % repr(self.header))

    def __unicode__(self):
        return self.file_name


class SignalsDataSet(list):
    def __init__(self, files, *args, **kwargs):
        super(SignalsDataSet, self).__init__(*args, **kwargs)
        self.extend([SignalData(f) for f in files])

        self.signals = self


def data_factory(file_name):
    files = []
    if file_name.endswith(DATA_FILE_TYPE):
        files.append(file_name)
    elif file_name.endswith(DATA_GROUP_TYPE):
        with open(file_name) as group:
            for line in group:
                line = line.strip()
                if line.endswith(DATA_FILE_TYPE) and not os.path.isabs(line):
                    line = os.path.join(os.path.dirname(file_name), line)
                if not os.path.exists(line):
                    logger.error(_('File does not exist: %s') % line)
                    continue
                files.append(line)

    return SignalsDataSet(files=files)
