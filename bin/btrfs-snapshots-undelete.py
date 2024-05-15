#!/usr/bin/python3

import shlex
from os import unlink
from pathlib import Path
from struct import unpack
from sys import exit, stderr  # pylint: disable=redefined-builtin

from xklb.utils import argparse_utils

printerr = stderr.write


''' btrfs-snapshots-undelete

Displays differences in 2 Btrfs snapshots (from the same subvolume
obviously).
Can read data from diff files created with:
btrfs send -p parent chid --no-data -f /tmp/snaps-diff


Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Copyright (c) 2016-2021 Jean-Denis Girard <jd.girard@sysnux.pf>
© SysNux http://www.sysnux.pf/
'''


class BtrfsStream:
    '''Btrfs send stream representation'''

    # From btrfs/send.h
    send_cmds = 'BTRFS_SEND_C_UNSPEC BTRFS_SEND_C_SUBVOL BTRFS_SEND_C_SNAPSHOT BTRFS_SEND_C_MKFILE BTRFS_SEND_C_MKDIR BTRFS_SEND_C_MKNOD BTRFS_SEND_C_MKFIFO BTRFS_SEND_C_MKSOCK BTRFS_SEND_C_SYMLINK BTRFS_SEND_C_RENAME BTRFS_SEND_C_LINK BTRFS_SEND_C_UNLINK BTRFS_SEND_C_RMDIR BTRFS_SEND_C_SET_XATTR BTRFS_SEND_C_REMOVE_XATTR BTRFS_SEND_C_WRITE BTRFS_SEND_C_CLONE BTRFS_SEND_C_TRUNCATE BTRFS_SEND_C_CHMOD BTRFS_SEND_C_CHOWN BTRFS_SEND_C_UTIMES BTRFS_SEND_C_END BTRFS_SEND_C_UPDATE_EXTENT'.split()

    send_attrs = 'BTRFS_SEND_A_UNSPEC BTRFS_SEND_A_UUID BTRFS_SEND_A_CTRANSID BTRFS_SEND_A_INO BTRFS_SEND_A_SIZE BTRFS_SEND_A_MODE BTRFS_SEND_A_UID BTRFS_SEND_A_GID BTRFS_SEND_A_RDEV BTRFS_SEND_A_CTIME BTRFS_SEND_A_MTIME BTRFS_SEND_A_ATIME BTRFS_SEND_A_OTIME BTRFS_SEND_A_XATTR_NAME BTRFS_SEND_A_XATTR_DATA BTRFS_SEND_A_PATH BTRFS_SEND_A_PATH_TO BTRFS_SEND_A_PATH_LINK BTRFS_SEND_A_FILE_OFFSET BTRFS_SEND_A_DATA BTRFS_SEND_A_CLONE_UUID BTRFS_SEND_A_CLONE_CTRANSID BTRFS_SEND_A_CLONE_PATH BTRFS_SEND_A_CLONE_OFFSET BTRFS_SEND_A_CLONE_LEN'.split()

    # From btrfs/ioctl.h:#define BTRFS_UUID_SIZE 16
    BTRFS_UUID_SIZE = 16

    # Headers length
    l_head = 10
    l_tlv = 4

    def __init__(self, stream_file, delete=False):
        # Read send stream
        try:
            with open(stream_file, 'rb') as f_stream:
                self.stream = f_stream.read()

        except IOError:
            printerr('Error reading stream\n')
            exit(1)

        if delete:
            try:
                unlink(stream_file)
            except OSError:
                printerr('Warning: could not delete stream file "{stream_file}"\n')

        if len(self.stream) < 17:
            printerr('Invalide stream length\n')
            self.version = None

        magic, _, self.version = unpack('<12scI', self.stream[0:17])
        if magic != b'btrfs-stream':
            printerr('Not a Btrfs stream!\n')
            self.version = None

    def _tlv_get(self, attr_type, index):
        attr, l_attr = unpack('<HH', self.stream[index : index + self.l_tlv])
        if self.send_attrs[attr] != attr_type:
            raise ValueError(f'Unexpected attribute {self.send_attrs[attr]}')
        ret = unpack(f'<{l_attr}B', self.stream[index + self.l_tlv : index + self.l_tlv + l_attr])
        return index + self.l_tlv + l_attr, ret

    def _tlv_get_string(self, attr_type, index):
        attr, l_attr = unpack('<HH', self.stream[index : index + self.l_tlv])
        if self.send_attrs[attr] != attr_type:
            raise ValueError(f'Unexpected attribute {self.send_attrs[attr]}')
        (ret,) = unpack(f'<{l_attr}s', self.stream[index + self.l_tlv : index + self.l_tlv + l_attr])
        return index + self.l_tlv + l_attr, ret.decode('utf8')

    def _tlv_get_u64(self, attr_type, index):
        attr, l_attr = unpack('<HH', self.stream[index : index + self.l_tlv])
        if self.send_attrs[attr] != attr_type:
            raise ValueError(f'Unexpected attribute {self.send_attrs[attr]}')
        (ret,) = unpack('<Q', self.stream[index + self.l_tlv : index + self.l_tlv + l_attr])
        return index + self.l_tlv + l_attr, ret

    def _tlv_get_uuid(self, attr_type, index):
        attr, l_attr = unpack('<HH', self.stream[index : index + self.l_tlv])
        if self.send_attrs[attr] != attr_type:
            raise ValueError(f'Unexpected attribute {self.send_attrs[attr]}')
        ret = unpack(
            f'<{self.BTRFS_UUID_SIZE}B',
            self.stream[index + self.l_tlv : index + self.l_tlv + l_attr],
        )
        return index + self.l_tlv + l_attr, ''.join(['%02x' % x for x in ret])

    def _tlv_get_timespec(self, attr_type, index):
        attr, l_attr = unpack('<HH', self.stream[index : index + self.l_tlv])
        if self.send_attrs[attr] != attr_type:
            raise ValueError(f'Unexpected attribute {self.send_attrs[attr]}')
        sec, nanos = unpack('<QL', self.stream[index + self.l_tlv : index + self.l_tlv + l_attr])
        return index + self.l_tlv + l_attr, float(sec) + nanos * 1e-9

    def decode(self, args):
        '''Decodes commands + attributes from send stream'''
        offset = 17
        cmd_ref = 0

        while True:
            # 3rd field is CRC, not used here
            l_cmd, cmd, _ = unpack('<IHI', self.stream[offset : offset + self.l_head])
            try:
                command = self.send_cmds[cmd]
            except IndexError:
                raise ValueError(f'Unkown command {cmd}')

            offset += self.l_head

            if command in 'BTRFS_SEND_C_UNLINK'.split():
                offset2, path = self._tlv_get_string('BTRFS_SEND_A_PATH', offset)
                print('cp', shlex.quote(str(Path(args.snapshot_root, path))), shlex.quote(path))

            elif command == 'BTRFS_SEND_C_TRUNCATE':
                offset2, path = self._tlv_get_string('BTRFS_SEND_A_PATH', offset)
                offset2, size = self._tlv_get_u64('BTRFS_SEND_A_SIZE', offset2)

                print(f'# truncated {size:d} cp', shlex.quote(str(Path(args.snapshot_root, path))), path)

            elif command == 'BTRFS_SEND_C_END':
                break

            offset += l_cmd
            cmd_ref += 1


def main():
    parser = argparse_utils.ArgumentParser(description="print unlinks between 2 btrfs snapshots")
    parser.add_argument('--snapshot-root', default='.snapshots/one/')
    parser.add_argument('diff_file')
    args = parser.parse_args()

    stream = BtrfsStream(args.diff_file)
    if stream.version is None:
        exit(1)

    stream.decode(args)


if __name__ == '__main__':
    main()
