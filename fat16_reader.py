import struct

from entry import Entry


class Reader():
    def __init__(self, filePath):
        with (open(filePath, 'rb') as f):
            self.content = f.read()
            self.parse_img()
            while True:
                print('\\'.join(self.pwd), end='>')
                command = input().strip()
                if (command == 'dir' or command == 'ls'):
                    contents = self.get_contents()
                    print('\n'.join(str(rc)
                          for rc in sorted(contents['directories'] + contents['files'])))
                elif (command == 'pwd'):
                    print('/'.join(self.pwd))
                elif (command.startswith('cd')):
                    args = command.split(' ')
                    if len(args) < 2:
                        print('Missing arguments\nUsage cd [dir]')
                    else:
                        directory = [
                            d for d in self.get_directories() if d.name == args[1]]
                        if (len(directory) >= 1):
                            directory = directory[0]
                            if (directory.cluster >= 2):
                                self.current_index = self.cluster_start + \
                                    (self.cluster_size * (directory.cluster - 2))
                                self.current_cluster = directory.cluster
                            else:
                                self.current_index = self.start_root_directory
                                self.current_cluster = None
                            print(
                                f'Moved to {directory.name} - Cluster {directory.cluster} at {hex(self.current_index)}')
                            if (directory.name == '..'):
                                self.pwd.pop()
                            elif (directory.name != '.'):
                                self.pwd.append(directory.name)
                        else:
                            print(f'Directory {args[1]} not found')
                elif (command.startswith('more')):
                    args = command.split(' ')
                    if len(args) < 2:
                        print('Missing arguments\nUsage more [file]')
                    else:
                        file = [f for f in self.get_files(
                        ) if f'{f.name}.{f.ext}' == args[1]]
                        if (len(file) >= 1):
                            file = file[0]
                            last_index = self.current_index
                            self.current_index = self.cluster_start + \
                                (self.cluster_size * (file.cluster - 2))
                            print(self.read_file(), end='')
                            self.current_index = last_index
                        else:
                            print(f'File {args[1]} not found')
                elif (command == 'exit'):
                    break
                else:
                    print('Command not valid')
            f.close()

    def parse_img(self):
        reserved_sectors = struct.unpack('<H', self.content[14:16])[0]
        print(f'Reserve size = {reserved_sectors}')
        sector_size = struct.unpack('<H', self.content[11:13])[0]
        print(f'Size Sector = {sector_size}')
        self.cluster_size = struct.unpack('<B', self.content[13:14])[
            0] * sector_size
        print(f'Cluster Size = {self.cluster_size}')
        self.start_FAT = reserved_sectors * sector_size
        print(f'Start FAT = {hex(self.start_FAT)}')
        fat_size = struct.unpack('<H', self.content[22:24])[0]
        print(f'FAT Size = {fat_size}')
        fat_number = struct.unpack('<B', self.content[16:17])[0]
        print(f'FAT Number = {fat_number}')
        self.start_root_directory = self.start_FAT + \
            (fat_size * fat_number * sector_size)
        print(f'RD Start = {hex(self.start_root_directory)}')
        root_directory_entries = struct.unpack('<H', self.content[17:19])[0]
        self.cluster_start = self.start_root_directory + \
            (root_directory_entries * 32)
        print(f'Cluster Start = {hex(self.cluster_start)}')
        self.current_index = self.start_root_directory

        index = self.start_root_directory
        while index < self.cluster_start:
            if (self.content[index:index+32] != [0]*32):
                cont = Entry(self.content[index:index+32])
                if (cont.volume):
                    self.device_name = cont.name
                    break
            index += 32
        self.pwd = [self.device_name]

    def get_contents(self):
        contents = {
            'directories': [],
            'files': [],
        }

        start_cluster = self.current_index
        index = self.current_index
        while True:
            if (not all(v == 0 for v in self.content[index:index+32])):
                cont = Entry(self.content[index:index+32])
                if (not cont.volume):
                    if (cont.dir):
                        contents['directories'].append(cont)
                    else:
                        contents['files'].append(cont)
            index += 32
            if self.current_index == self.start_root_directory:
                if index >= self.cluster_start:
                    break
            else:
                if index >= start_cluster + self.cluster_size:
                    start_cluster = self.next_cluster_index()
                    index = start_cluster
                    if start_cluster is None:
                        break

        return contents

    def get_directories(self):
        return self.get_contents()['directories']

    def get_files(self):
        return self.get_contents()['files']

    def read_file(self):
        content = []
        start_cluster = self.current_index
        index = self.current_index
        while True:
            if (self.content[index] == b'\00'):
                break
            content.append(chr(self.content[index]))
            index += 1
            if index >= start_cluster + self.cluster_size:
                start_cluster = self.next_cluster_index()
                index = start_cluster
                if start_cluster is None:
                    break
        return ''.join(content)

    def next_cluster_index(self):
        next_cluster = struct.unpack('<H', self.content[self.start_FAT + (
            self.current_cluster * 2):self.start_FAT + (self.current_cluster * 2) + 2])[0]
        if next_cluster == 0x0000:
            # Empty cluster
            pass
        elif next_cluster <= 0x0002:
            # Not allowed
            raise Exception()
        elif next_cluster == 0xFFF7:
            # Bad sectors in cluster
            raise Exception()
        elif next_cluster >= 0xFFF8:
            return None
        else:
            return next_cluster


if __name__ == '__main__':
    Reader('FAT16Reader/Chiavetta.img')
