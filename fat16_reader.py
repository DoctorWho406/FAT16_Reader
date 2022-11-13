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
                        print('Missing argumenbts\nUsage cd [dir]')
                    else:
                        directory = [
                            d for d in self.get_directories() if d.name == args[1]]
                        if (len(directory) >= 1):
                            directory = directory[0]
                            self.current_root = self.cluster_start + \
                                (self.cluster_size * directory.size)
                            print(
                                f'Moved to {directory.name}. Start at {hex(self.current_root)}')
                            self.pwd.append(directory.name)
                        else:
                            print(f'Directory {args[1]} not found')
                elif (command.startswith('more')):
                    args = command.split(' ')
                    if len(args) < 2:
                        print('Missing argumenbts\nUsage more [file]')
                    else:
                        if (args[1] not in [f.name for f in self.get_files()]):
                            print(f'File {args[1]} not found')
                        else:
                            # Read file
                            pass
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
        self.current_root = self.start_root_directory

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

        index = self.current_root
        while index < (self.cluster_start if self.current_root == self.start_root_directory else self.current_root+self.cluster_size):
            if (not all(v == 0 for v in self.content[index:index+32])):
                cont = Entry(self.content[index:index+32])
                if (not cont.volume):
                    if (cont.dir):
                        contents['directories'].append(cont)
                    else:
                        contents['files'].append(cont)
            index += 32

        return contents

    def get_directories(self):
        return self.get_contents()['directories']

    def get_files(self):
        return self.get_contents()['files']


if __name__ == '__main__':
    Reader('FAT16Reader/Chiavetta.img')
