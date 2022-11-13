import functools
import struct


@functools.total_ordering
class Entry():
    def __init__(self, content):
        self.entry = content
        self.name = ''.join(chr(byte) for byte in
                            content[0:8]).strip()
        # print(f'Name = {self.name}')
        self.ext = ''.join(chr(byte) for byte in
                           content[8:11]).strip()
        # print(f'Ext = {self.ext}')
        self.get_attr(content[11])
        self.get_creation_time(content[13:18])
        # print(f'Creation time = {self.date} {self.time}')
        self.get_access_time(content[18:20])
        # print(f'Last access = {self.last_access_date}')
        self.get_edit_time(content[22:26])
        # print(f'Last edit = {self.last_edit_date} {self.last_edit_time}')
        self.cluster = struct.unpack('<H', content[26:28])[0]
        # print(f'Cluster = {self.cluster}')
        self.size = struct.unpack('<I', content[28:32])[0]
        # print(f'Size = {self.size}')

    def get_attr(self, bitmask):
        self.readonly = (bitmask & 0x01) > 0
        # print(f'Readonly = {self.readonly}')
        self.hidden = (bitmask & 0x02) > 0
        # print(f'Hidden = {self.hidden}')
        self.system = (bitmask & 0x04) > 0
        # print(f'System = {self.system}')
        self.volume = (bitmask & 0x08) > 0
        # print(f'Volume = {self.volume}')
        self.dir = (bitmask & 0x10) > 0
        # print(f'Directory = {self.dir}')
        self.archive = (bitmask & 0x20) > 0
        # print(f'Archive = {self.archive}')

    def get_creation_time(self, times_bytes):
        times = struct.unpack('<BHH', times_bytes)
        milliseconds = times[0] * 10
        seconds = times[1] & 0x1F
        minutes = (times[1] & 0x7E0) >> 5
        hours = (times[1] & 0xF800) >> 11
        self.time = str(hours).rjust(
            2, '0') + ':' + str(minutes).rjust(2, '0') + ':' + str(seconds).rjust(2, '0')
        days = times[2] & 0x1F
        monts = (times[2] & 0x1E0) >> 5
        years = ((times[2] & 0xFE00) >> 9) + 1980
        self.date = str(days).rjust(2, '0') + '/' + \
            str(monts).rjust(2, '0') + '/' + str(years).rjust(4, '0')

    def get_access_time(self, times_bytes):
        time = struct.unpack('<H', times_bytes)[0]
        days = time & 0x1F
        monts = (time & 0x1E0) >> 5
        years = ((time & 0xFE00) >> 9) + 1980
        self.last_access_date = str(days).rjust(2, '0') + '/' + \
            str(monts).rjust(2, '0') + '/' + str(years).rjust(4, '0')

    def get_edit_time(self, times_bytes):
        times = struct.unpack('<HH', times_bytes)
        seconds = times[0] & 0x1F
        minutes = (times[0] & 0x7E0) >> 5
        hours = (times[0] & 0xF800) >> 11
        self.last_edit_time = str(hours).rjust(
            2, '0') + ':' + str(minutes).rjust(2, '0')
        days = times[1] & 0x1F
        monts = (times[1] & 0x1E0) >> 5
        years = ((times[1] & 0xFE00) >> 9) + 1980
        self.last_edit_date = str(days).rjust(2, '0') + '/' + \
            str(monts).rjust(2, '0') + '/' + str(years).rjust(4, '0')

    def __eq__(self, __o):
        if type(__o) is Entry:
            return self.entry == __o.entry
        return False

    def __gt__(self, __o):
        if type(__o) is Entry:
            return ((self.name) > (__o.name))
        return False

    def __str__(self):
        # '19/10/2022   14:44   <DIR>   SIZE    NAME.EXT
        return f'{self.date}\t{self.time}\t' + ('<DIR>' if self.dir else '\t') + ('\t' if self.dir else str(self.size)) + '\t' + self.name + (f'.{self.ext}' if self.ext != '' else '')
